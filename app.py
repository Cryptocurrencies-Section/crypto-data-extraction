import os
import re
import json
import pandas as pd
import pdfplumber
import openpyxl
import mammoth
import tkinter as tk
from tkinter import ttk, filedialog, Label, Button, Text, Scrollbar, END, BooleanVar
import pyperclip
import csv
from datetime import datetime
import sys

# Definizione dei pattern di ricerca
PATTERNS = {
    'Bitcoin Address': r'(?:^|[^a-km-zA-HJ-NP-Z0-9])(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59})(?:$|[^a-km-zA-HJ-NP-Z0-9])',
    'Transaction Hash': r'[a-fA-F0-9]{64}',
    'Ethereum Address': r'0x[a-fA-F0-9]{40}',
    'Ethereum Transaction': r'0x[a-fA-F0-9]{64}',
    'Monero Address': r'4[0-9AB][123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{93}',
    'Tron Address': r'T[A-Za-z1-9]{33}',
    'IP Address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'URL': r'\bhttps?:\/\/[^\s/$.?#].[^\s]*\b',
    'Email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
}


def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.xlsx', '.xls']:
        return extract_text_from_excel(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_word(file_path)
    elif ext == '.csv':
        return extract_text_from_csv(file_path)
    elif ext in ['.txt', '.json']:
        return extract_text_from_text(file_path)
    else:
        return "Formato non supportato"


def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name=None)
    return '\n'.join(['\n'.join(map(str, df[sheet].values.flatten())) for sheet in df])


def extract_text_from_word(file_path):
    with open(file_path, 'rb') as docx_file:
        result = mammoth.extract_raw_text(docx_file)
    return result.value


def extract_text_from_csv(file_path):
    df = pd.read_csv(file_path, error_bad_lines=False)
    return '\n'.join(df.astype(str).values.flatten())


def extract_text_from_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_text(text, patterns=None):
    if patterns is None:
        patterns = PATTERNS
    results = []
    summary = {}
    for label, pattern in patterns.items():
        matches = re.findall(pattern, text)
        unique_matches = list(set(matches))
        if unique_matches:
            summary[label] = len(unique_matches)
            for match in unique_matches:
                results.append({'type': label, 'value': match})
    return results, summary


def resource_path(relative_path):
    """ Ottiene il percorso assoluto per le risorse, funziona sia in development che in produzione """
    try:
        # PyInstaller crea una cartella temp e memorizza il percorso in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class FileAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Badger 1.0 - Crypto Data Extraction")
        self.root.geometry("400x390")
        self.root.resizable(False, False)
        
        # Usa resource_path per l'icona
        try:
            icon_path = resource_path("favicon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Errore nel caricamento dell'icona: {e}")
        
        self.pattern_vars = {}
        self.results = []
        self.file_path = None
        self.status_label = None
        self.status_after_id = None  # Per tenere traccia del timer
        self.setup_initial_gui()

    def setup_initial_gui(self):
        # Frame principale
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill='both', expand=True)

        # Frame per il logo e il titolo
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 20))

        # Carica e mostra il logo
        try:
            from PIL import Image, ImageTk
            logo_path = resource_path("logo.png")
            logo_image = Image.open(logo_path)
            # Ridimensiona l'immagine mantenendo le proporzioni
            logo_size = (80, 80)  # Dimensione desiderata
            logo_image.thumbnail(logo_size, Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            
            logo_label = ttk.Label(header_frame, image=logo_photo)
            logo_label.image = logo_photo  # Mantiene un riferimento
            logo_label.pack(pady=(0, 10))

        except Exception as e:
            print(f"Errore nel caricamento del logo: {e}")

        # Titolo principale
        ttk.Label(header_frame, 
                 text="Badger 1.0 - Crypto Data Extraction", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))

        # Sottotitolo con i formati supportati
        supported_formats = "Estrai dati relativi alle criptovalute ed altri elementi forensi da file: PDF (.pdf), Excel (.xlsx, .xls), Word (.docx, .doc), CSV (.csv), Text (.txt, .json)"
        ttk.Label(header_frame, 
                 text=supported_formats,
                 justify='center',
                 wraplength=300).pack(pady=(0, 10))

        # Pulsante per scegliere il file
        ttk.Button(self.main_frame, 
                  text="Scegli File",
                  command=self.choose_file,
                  style='Accent.TButton',
                  width=20).pack(pady=10)

        # Info sezione
        ttk.Label(self.main_frame,
                 text="Sezione Criptovalute - V.B. Luigi Rosato",
                 font=("Arial", 8),
                 foreground='gray').pack(side='bottom', pady=(20, 0))

        # Configura stile per il pulsante
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 11))

    def setup_analysis_gui(self):
        # Pulisci il frame principale
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Ripristina la dimensione della finestra
        self.root.geometry("400x390")

        # Mostra il nome del file selezionato
        file_name = os.path.basename(self.file_path)
        ttk.Label(self.main_frame, 
                 text=f"File selezionato:\n{file_name}", 
                 font=("Arial", 11),
                 wraplength=350,
                 justify='center').pack(pady=(0, 20))

        # Frame per checkbox
        checkbox_frame = ttk.LabelFrame(self.main_frame, text="Elementi da cercare", padding=10)
        checkbox_frame.pack(fill='x', padx=10, pady=(0, 20))

        # Organizza i checkbox in una griglia
        row = 0
        col = 0
        for pattern_name in PATTERNS.keys():
            self.pattern_vars[pattern_name] = BooleanVar(value=True)
            ttk.Checkbutton(checkbox_frame, 
                          text=pattern_name, 
                          variable=self.pattern_vars[pattern_name]).grid(row=row, 
                                                                       column=col, 
                                                                       padx=5, 
                                                                       pady=5,
                                                                       sticky='w')
            col += 1
            if col > 1:  # 2 checkbox per riga
                col = 0
                row += 1

        # Pulsante Analizza (centrato)
        ttk.Button(self.main_frame, 
                  text="Analizza",
                  command=self.analyze_file,
                  style='Accent.TButton',
                  width=15).pack(pady=10)

    def setup_results_gui(self):
        # Imposta dimensione fissa per la finestra dei risultati
        self.root.geometry("900x500")
        self.root.resizable(False, False)
        
        # Pulisci il frame principale
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Frame per il percorso del file
        file_frame = ttk.Frame(self.main_frame)
        file_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(file_frame,
                 text=f"File: {os.path.basename(self.file_path)}",
                 font=("Arial", 9),
                 wraplength=680).pack(anchor='w')

        # Separatore con più spazio sotto
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', padx=10, pady=(5, 10))

        # Notebook per le tab
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Frame per il messaggio di stato
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill='x', padx=10)
        self.status_label = ttk.Label(status_frame, text="", font=("Arial", 8))
        self.status_label.pack(side='left')

        # Frame inferiore per i pulsanti
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(bottom_frame, 
                  text="Chiudi",
                  command=self.root.destroy,
                  width=15).pack(side='right', padx=5)
        
        ttk.Button(bottom_frame, 
                  text="💾 Esporta Tutto",
                  command=self.export_all_to_csv,
                  width=15).pack(side='right', padx=5)

        # Dizionario per tenere traccia delle tab e delle loro treeview
        self.tabs = {}
        self.treeviews = {}

    def create_tab(self, pattern_name, total_items):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=f"{pattern_name} ({total_items})")
        self.tabs[pattern_name] = tab

        # Header frame per i pulsanti della tab
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill='x', padx=5, pady=5)  # Ripristinato il pady originale
        
        ttk.Label(header_frame,
                 text=f"{pattern_name} - {total_items} risultati",
                 font=("Arial", 10, "bold")).pack(side='left', padx=5)
        
        ttk.Button(header_frame, 
                  text="📋 Copia Tutti",
                  command=lambda p=pattern_name: self.copy_all(p),
                  style='Small.TButton',
                  width=12).pack(side='right', padx=(0,5))
        
        ttk.Button(header_frame, 
                  text="💾 Esporta CSV",
                  command=lambda p=pattern_name: self.export_to_csv(p),
                  style='Small.TButton',
                  width=12).pack(side='right', padx=5)

        # Separatore
        ttk.Separator(tab, orient='horizontal').pack(fill='x', padx=5)  # Ripristinato il pady originale

        # Creazione Treeview con stile alternato per le righe
        style = ttk.Style()
        style.configure("Striped.Treeview", 
                       background="white",
                       fieldbackground="white",
                       rowheight=25)  # Ripristinata l'altezza originale delle righe
        style.configure("Small.TButton", 
                       font=('Arial', 9))
        style.map("Striped.Treeview",
                 background=[("selected", "#0078D7")])
        
        tree = ttk.Treeview(tab, 
                           columns=("value",), 
                           show="tree",  # Cambiato da "headings" a "tree" per rimuovere l'header
                           style="Striped.Treeview")
        tree.column("#0", width=0, stretch=False)  # Nasconde la colonna dell'albero
        tree.column("value", width=500)
        
        # Scrollbar per Treeview
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.treeviews[pattern_name] = tree
        tree.bind('<Double-1>', lambda e, p=pattern_name: self.copy_item(e, p))
        tree.tag_configure('oddrow', background='#F5F5F5')

    def choose_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*"),
                      ("PDF", "*.pdf"),
                      ("Excel", "*.xlsx;*.xls"),
                      ("Word", "*.docx;*.doc"),
                      ("CSV", "*.csv"),
                      ("Text", "*.txt;*.json")]
        )
        if self.file_path:
            self.setup_analysis_gui()

    def analyze_file(self):
        if not self.file_path:
            return

        text = extract_text_from_file(self.file_path)
        selected_patterns = {k: v for k, v in PATTERNS.items() if self.pattern_vars[k].get()}
        results, summary = analyze_text(text, patterns=selected_patterns)

        # Se non ci sono risultati, mostra un messaggio e non aprire la finestra dei risultati
        if not results:
            from tkinter import messagebox
            messagebox.showinfo(
                "Nessun risultato",
                "Non è stato trovato alcun elemento nel file selezionato."
            )
            return

        self.setup_results_gui()

        # Crea le tab per i risultati
        for pattern_name, count in summary.items():
            if count > 0:
                self.create_tab(pattern_name, count)
                tree = self.treeviews[pattern_name]
                pattern_results = [r['value'] for r in results if r['type'] == pattern_name]
                for i, value in enumerate(pattern_results):
                    tag = 'oddrow' if i % 2 else ''
                    tree.insert('', 'end', values=(value,), tags=(tag,))

    def reset_to_initial(self):
        # Resetta le variabili
        self.file_path = None
        self.pattern_vars.clear()
        self.status_label = None
        self.status_after_id = None
        
        # Ripristina la dimensione originale
        self.root.geometry("400x390")
        
        # Pulisci il frame principale
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Ricrea la GUI iniziale
        self.setup_initial_gui()

    def show_copy_message(self, message="Elemento copiato negli appunti"):
        if self.status_label:
            self.status_label.configure(text=message)
            # Cancella il timer precedente se esiste
            if self.status_after_id:
                self.root.after_cancel(self.status_after_id)
            # Imposta un nuovo timer per cancellare il messaggio dopo 2 secondi
            self.status_after_id = self.root.after(2000, lambda: self.status_label.configure(text=""))

    def copy_item(self, event, pattern_name):
        tree = self.treeviews[pattern_name]
        selected_item = tree.selection()
        if selected_item:
            value = tree.item(selected_item[0])['values'][0]
            pyperclip.copy(value)
            self.show_copy_message()

    def copy_all(self, pattern_name):
        tree = self.treeviews[pattern_name]
        values = [tree.item(item)['values'][0] for item in tree.get_children()]
        pyperclip.copy('\n'.join(values))
        self.show_copy_message("Tutti gli elementi copiati negli appunti")

    def export_to_csv(self, pattern_name):
        tree = self.treeviews[pattern_name]
        values = [tree.item(item)['values'][0] for item in tree.get_children()]
        
        filename = f"export_{pattern_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[("CSV files", "*.csv")],
            title="Salva CSV"
        )
        
        if file_path:  # Se l'utente non ha annullato la selezione
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['value'])
                writer.writerows([[v] for v in values])

    def export_all_to_csv(self):
        all_data = []
        for pattern_name, tree in self.treeviews.items():
            values = [tree.item(item)['values'][0] for item in tree.get_children()]
            for value in values:
                all_data.append({'type': pattern_name, 'value': value})
        
        filename = f"export_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[("CSV files", "*.csv")],
            title="Salva CSV"
        )
        
        if file_path:  # Se l'utente non ha annullato la selezione
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['type', 'value'])
                writer.writeheader()
                writer.writerows(all_data)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileAnalyzer(root)
    root.mainloop()
