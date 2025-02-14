# File Analyzer

## Descrizione
Questo progetto è un'applicazione Python che consente di analizzare file nei formati PDF, CSV, Excel, Word, JSON e TXT per identificare informazioni come indirizzi crypto, hash, IP, URL ed email.

## Requisiti
- Python 3.8 o superiore

## Installazione

1. **Clonare il repository**
   ```sh
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Creare un ambiente virtuale**
   ```sh
   python -m venv venv
   ```

3. **Attivare l'ambiente virtuale**
   - Su **Windows**:
     ```sh
     venv\Scripts\activate
     ```
   - Su **macOS/Linux**:
     ```sh
     source venv/bin/activate
     ```

4. **Installare le dipendenze**
   ```sh
   pip install -r requirements.txt
   ```

## Utilizzo

1. **Avviare l'applicazione**
   ```sh
   python file_analysis_app.py
   ```

2. **Selezionare un file** dalla GUI per avviare l'analisi.

## Note
- Assicurarsi di avere Python installato e configurato correttamente.
- Se si verificano problemi con le dipendenze, provare ad aggiornare `pip` con:
  ```sh
  pip install --upgrade pip
  
