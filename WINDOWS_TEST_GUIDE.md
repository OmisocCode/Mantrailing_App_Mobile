# GUIDA TEST SU WINDOWS

Questa guida spiega come testare l'app Mantrailing Training su PC Windows.

## 📋 Prerequisiti

### Python
- **Python 3.8 o superiore** installato
- Verifica versione: `python --version`
- Download: https://www.python.org/downloads/

### Virtual Environment (Consigliato)
Per evitare conflitti con altre installazioni Python:

```bash
# Crea virtual environment
python -m venv venv

# Attiva virtual environment
# Su Windows CMD:
venv\Scripts\activate.bat

# Su Windows PowerShell:
venv\Scripts\Activate.ps1

# Su Git Bash o simili:
source venv/Scripts/activate
```

## 🔧 Installazione Dipendenze

```bash
# Installa le dipendenze
pip install -r requirements.txt

# Se hai problemi con kivy-garden.mapview, puoi installarlo separatamente:
pip install kivy-garden.mapview
```

### Note su Windows:
- **Kivy** potrebbe richiedere Microsoft Visual C++ Redistributable
- Se `pip install` fallisce, prova:
  ```bash
  pip install --upgrade pip setuptools wheel
  pip install kivy kivymd plyer
  ```

## 🧪 Test Disponibili

### 1. Test Componenti Core

Testa database, modelli, GPS service, utilità geospaziali:

```bash
python test_core.py
```

**Output atteso:**
```
============================================================
TEST COMPONENTI CORE - MANTRAILING TRAINING APP
============================================================

=== Test GPSPoint ===
✓ GPSPoint OK

=== Test Track ===
✓ Track OK

=== Test Database ===
✓ Database OK

=== Test Geo Utils ===
✓ Geo Utils OK

=== Test GPS Service ===
✓ GPS Service OK

=== Test Integrazione ===
✓ Integrazione OK

============================================================
✓ TUTTI I TEST COMPLETATI CON SUCCESSO!
============================================================
```

### 2. Test App Completa

Avvia l'app in modalità desktop (finestra 360x640px):

```bash
python main.py
```

**Cosa succede:**
- Si apre una finestra che simula uno smartphone
- GPS usa **MockGPSService** (dati simulati)
- Database SQLite creato in `app/data/mantrailing.db`
- Puoi navigare tra tutte le schermate

## 📱 Test delle Modalità

### Modalità Disperso

**Cosa testare:**
1. Clicca "MODALITÀ DISPERSO"
2. Osserva coordinate GPS simulate
3. Imposta frequenza campionamento (es. 2 secondi)
4. Clicca "AVVIA REGISTRAZIONE"
5. Osserva il contatore punti che aumenta
6. Osserva il timer che scorre
7. Clicca "FERMA REGISTRAZIONE"
8. Clicca "ESPORTA PERCORSO"
9. Copia il testo generato

**Output atteso:**
```
Registrazione avviata
Punto registrato: 45.464200, 9.190000 (q=95)
Punto registrato: 45.464300, 9.190100 (q=92)
...
Percorso salvato nel database con ID: 1
Registrazione fermata
```

**Test clipboard:**
- Il percorso viene copiato negli appunti (CTRL+V per incollare)
- Formato: `45.4642,9.19,95;45.465,9.191,90;...`

### Modalità Unità Cinofila

**Cosa testare:**
1. Copia un percorso dalla modalità Disperso
2. Clicca "MODALITÀ UNITÀ CINOFILA"
3. Incolla il percorso nel campo di testo
4. Clicca "IMPORTA PERCORSO"
5. Regola il raggio alert (slider)
6. Clicca "INIZIA RICERCA"
7. Osserva la distanza dal percorso
8. **Alert acustici** vengono simulati con print sulla console

**Output atteso:**
```
✓ Percorso caricato: 10 punti
Ricerca avviata
🔊 BEEP! Distanza: 250m (limite: 200m)
🔊 BEEP! Distanza: 220m (limite: 200m)
...
```

**Comportamento distanza:**
- Verde: Dentro il raggio
- Arancione: Vicino al limite
- Rosso: Fuori dal raggio
- Alert sonoro (print) quando fuori dal raggio

### Modalità Addestratore

**Cosa testare:**
1. Copia un percorso
2. Clicca "MODALITÀ ADDESTRATORE"
3. Incolla il percorso
4. Clicca "CARICA PERCORSO"
5. Osserva la mappa (se MapView disponibile)
6. Clicca "INIZIA TRACKING"
7. Osserva il marker della posizione che si muove

**Note su MapView:**
- MapView richiede connessione internet per scaricare tile
- Su Windows potrebbe non funzionare perfettamente
- Se MapView non è disponibile, vedrai un placeholder
- Il percorso viene comunque caricato e validato

**Output atteso:**
```
✓ 10 punti
Tracking avviato
Posizione: 45.464200, 9.190000
Posizione: 45.464300, 9.190100
...
```

## 🎯 Scenari di Test Completi

### Scenario 1: Flusso Completo

```bash
# 1. Avvia app
python main.py

# 2. Modalità Disperso
- Seleziona "MODALITÀ DISPERSO"
- Imposta frequenza: 2 sec
- Avvia registrazione
- Aspetta 20 secondi (10 punti)
- Ferma registrazione
- Esporta e copia percorso

# 3. Modalità Cinofila
- Torna indietro
- Seleziona "MODALITÀ UNITÀ CINOFILA"
- Incolla il percorso
- Importa percorso
- Imposta raggio: 100 metri
- Inizia ricerca
- Osserva alert nella console

# 4. Modalità Addestratore
- Torna indietro
- Seleziona "MODALITÀ ADDESTRATORE"
- Incolla il percorso
- Carica percorso
- Inizia tracking
- Osserva mappa (se disponibile)
```

### Scenario 2: Test Persistenza Database

```bash
# 1. Esegui prima volta
python main.py
# Registra un percorso in modalità Disperso
# Chiudi app

# 2. Esegui seconda volta
python main.py
# Il percorso è salvato nel database!

# 3. Verifica database
# Il file si trova in: app/data/mantrailing.db
# Puoi aprirlo con DB Browser for SQLite
```

### Scenario 3: Test Percorsi Lunghi

Crea un percorso più lungo per testare performance:

```python
# In test_long_track.py
from app.models.track import Track

track = Track(name="Test Lungo")
for i in range(100):
    track.add_point(45.4642 + i*0.0001, 9.19 + i*0.0001, 95)

print(track.to_string())
```

Copia l'output e usalo nelle modalità Cinofila/Addestratore.

## 🐛 Problemi Comuni

### 1. Import Error: No module named 'kivy'

**Soluzione:**
```bash
pip install --upgrade pip
pip install kivy==2.2.1
```

### 2. MapView non funziona

**Soluzione:**
```bash
pip install kivy-garden.mapview
```

Se persiste:
- MapView non è critico per i test
- L'app mostra un placeholder
- Funziona comunque su Android

### 3. GPS Service Error

**Soluzione:**
- Su Windows viene automaticamente usato MockGPSService
- Non è un errore, è comportamento atteso
- plyer.gps non funziona su desktop

### 4. Window troppo piccola/grande

**Modifica in main.py:**
```python
# Cambia dimensione finestra
Window.size = (400, 700)  # Più grande
# oppure
Window.size = (320, 568)  # Più piccola
```

### 5. Database locked

**Soluzione:**
- Chiudi tutte le istanze dell'app
- Elimina `app/data/mantrailing.db`
- Riavvia app

## 📊 Verifica Funzionamento

### Checklist Test:

- [ ] Test core passano tutti (test_core.py)
- [ ] App si avvia senza errori
- [ ] Schermata selezione modalità funziona
- [ ] Modalità Disperso:
  - [ ] GPS mock funziona
  - [ ] Registrazione punti
  - [ ] Timer funziona
  - [ ] Export percorso
  - [ ] Clipboard copia
- [ ] Modalità Cinofila:
  - [ ] Import percorso
  - [ ] Calcolo distanza
  - [ ] Alert quando fuori raggio
  - [ ] Slider raggio funziona
- [ ] Modalità Addestratore:
  - [ ] Import percorso
  - [ ] Mappa visibile (o placeholder)
  - [ ] Tracking posizione
- [ ] Database:
  - [ ] Percorsi salvati
  - [ ] Persistenza tra sessioni
- [ ] Navigazione:
  - [ ] Pulsante indietro funziona
  - [ ] Cambio schermata fluido

## 🔍 Debug

### Abilita logging dettagliato:

Aggiungi in `main.py` all'inizio:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verifica database:

```python
# In Python console
from app.models.database import get_database

db = get_database()
stats = db.get_stats()
print(stats)

tracks = db.get_all_tracks()
for track in tracks:
    print(track)
```

### Verifica GPS mock:

```python
# In Python console
from app.services.gps_service import MockGPSService

gps = MockGPSService(start_lat=45.4642, start_lon=9.1900)

def on_location(lat, lon, alt, acc, speed):
    print(f"Position: {lat}, {lon}")

gps.start(on_location=on_location)
gps.update_position(45.465, 9.191, 95)
gps.stop()
```

## 📝 Report Bug

Se trovi problemi, prendi nota di:
1. Versione Python: `python --version`
2. Sistema operativo e versione Windows
3. Messaggi errore completi
4. Passi per riprodurre il problema
5. Output console

## ✅ Prossimi Step

Dopo aver testato su Windows:
1. ✓ Tutti i test core passano
2. ✓ Tutte le modalità funzionano
3. ✓ Nessun crash o errore critico
4. → Pronto per build Android!

## 🚀 Build Android (Preview)

Quando sei pronto per testare su Android reale:

```bash
# Installa buildozer (solo Linux/WSL/Mac)
pip install buildozer

# Build APK
buildozer android debug

# L'APK sarà in: bin/mantrailing-0.1.0-debug.apk
```

**Nota:** Buildozer non funziona nativamente su Windows.
Usa WSL (Windows Subsystem for Linux) o una VM Linux.

---

**Buon testing!** 🎉

Per domande o problemi, consulta:
- DEV_README.md
- README.md
- Codice sorgente in `app/`
