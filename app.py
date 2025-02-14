import os
import re
import json
import pandas as pd
import pdfplumber
import openpyxl
import mammoth
from tkinter import Tk, filedialog, Label, Button, Text, Scrollbar, END

# Definizione dei pattern di ricerca
PATTERNS = {
    'Bitcoin Address': r'(?![a-km-zA-HJ-NP-Z1-9])[13][a-km-zA-HJ-NP-Z1-9]{26,33}(?![a-km-zA-HJ-NP-Z1-9])|bc1[a-zA-HJ-NP-Za-z0-9]{39,59}',
    'Ethereum Address': r'0x[a-fA-F0-9]{40}',
    'IP Address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    'URL': r'\bhttps?:\/\/[^\s/$.?#].[^\s]*\b',
    'Email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'Transaction Hash': r'[a-fA-F0-9]{64}'
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


def analyze_text(text):
    results = []
    summary = {}
    for label, pattern in PATTERNS.items():
        matches = re.findall(pattern, text)
        unique_matches = list(set(matches))
        if unique_matches:
            summary[label] = len(unique_matches)
            for match in unique_matches:
                results.append({'type': label, 'value': match})
    return results, summary


def open_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("All Files", "*.*"),
                   ("PDF", "*.pdf"),
                   ("Excel", "*.xlsx;*.xls"),
                   ("Word", "*.docx;*.doc"),
                   ("CSV", "*.csv"),
                   ("Text", "*.txt;*.json")]
    )
    if not file_path:
        return
    
    text = extract_text_from_file(file_path)
    results, summary = analyze_text(text)
    
    output_text.delete(1.0, END)
    output_text.insert(END, f"Analisi di {os.path.basename(file_path)}\n\n")
    for key, value in summary.items():
        output_text.insert(END, f"{key}: {value} risultati\n")
    output_text.insert(END, "\nDettagli:\n")
    for result in results:
        output_text.insert(END, f"{result['type']}: {result['value']}\n")
    
    output_text.insert(END, "\nAnalisi completata!\n")


# Creazione GUI
root = Tk()
root.title("File Analyzer")
root.geometry("600x500")

Label(root, text="Seleziona un file per l'analisi", font=("Arial", 14)).pack(pady=10)
Button(root, text="Apri File", command=open_file, font=("Arial", 12)).pack(pady=5)

output_text = Text(root, wrap='word', height=20, width=70)
output_text.pack(padx=10, pady=10, fill='both', expand=True)
scrollbar = Scrollbar(root, command=output_text.yview)
scrollbar.pack(side='right', fill='y')
output_text.config(yscrollcommand=scrollbar.set)

root.mainloop()
