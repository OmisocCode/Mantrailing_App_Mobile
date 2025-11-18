# MANTRAILING TRAINING APP - Documentazione Sviluppo

## 📁 Struttura Progetto

```
Mantrailing_App_Mobile/
├── app/
│   ├── models/          # Modelli dati
│   │   ├── track.py     # Modello Track e GPSPoint
│   │   └── database.py  # Database manager SQLite
│   ├── services/        # Servizi
│   │   └── gps_service.py  # Wrapper GPS con plyer
│   ├── utils/           # Utilità
│   │   └── geo_utils.py    # Calcoli geospaziali
│   ├── views/           # Schermate UI (TODO)
│   ├── controllers/     # Logica business (TODO)
│   └── assets/          # Risorse (icone, suoni)
├── main.py              # Punto di ingresso applicazione
├── test_core.py         # Test componenti core
├── requirements.txt     # Dipendenze Python
├── buildozer.spec       # Configurazione build Android
└── README.md            # Documentazione utente

```

## ✅ Fase 1 e 2 Completate

### Fase 1: Setup e Infrastruttura ✓
- [x] Struttura directory progetto
- [x] File requirements.txt con dipendenze
- [x] File buildozer.spec per Android build
- [x] Schema database SQLite

### Fase 2: Componenti Core ✓
- [x] Servizio GPS wrapper (con mock per testing)
- [x] Modello Track per gestione dati percorso
- [x] Utilità geospaziali (distanze, calcoli)
- [x] App Kivy base con schermata selezione modalità

## 🔧 Setup Ambiente di Sviluppo

### Prerequisiti
- Python 3.8 o superiore
- pip (package manager Python)

### Installazione Dipendenze

```bash
# Installa le dipendenze
pip install -r requirements.txt
```

### Test Componenti Core

```bash
# Esegui i test
python test_core.py
```

Questo script testa:
- Modello GPSPoint
- Modello Track (serializzazione/deserializzazione)
- Database SQLite (CRUD operations)
- Utilità geospaziali (distanze, calcoli)
- GPS Service (mock)
- Integrazione completa

### Esecuzione App (Desktop Testing)

```bash
# Avvia l'app in modalità desktop
python main.py
```

L'app si avvierà in una finestra 360x640px simulando uno smartphone.

## 📦 Componenti Implementati

### 1. Modello Track (`app/models/track.py`)

**Classi:**
- `GPSPoint`: Singolo punto GPS (lat, lon, quality)
- `Track`: Percorso completo con lista di punti

**Funzionalità:**
- Serializzazione/deserializzazione formato CSV
- Calcolo bounds e centro geografico
- Validazione dati
- Qualità media GPS
- Colori qualità (blu/verde/giallo/arancione/rosso)

**Formato esportazione:**
```
lat1,lon1,quality1;lat2,lon2,quality2;...;latN,lonN,qualityN
```

### 2. Database Manager (`app/models/database.py`)

**Schema tabelle:**
- `tracks`: Percorsi salvati
- `track_points`: Punti GPS individuali (opzionale)
- `settings`: Impostazioni app

**Operazioni CRUD:**
- `save_track()`: Salva nuovo percorso
- `get_track()`: Recupera percorso per ID
- `get_all_tracks()`: Lista tutti i percorsi
- `update_track()`: Aggiorna metadati
- `delete_track()`: Elimina percorso
- `search_tracks()`: Ricerca per nome/descrizione

**Settings:**
- `get_setting()`: Leggi impostazione
- `set_setting()`: Salva impostazione
- `delete_setting()`: Elimina impostazione

### 3. GPS Service (`app/services/gps_service.py`)

**Classi:**
- `GPSService`: Wrapper per plyer GPS
- `MockGPSService`: GPS simulato per testing

**Funzionalità:**
- Tracciamento GPS continuo
- Callback per nuove posizioni
- Calcolo qualità GPS da accuracy
- Gestione permessi
- Statistiche utilizzo

**Qualità GPS (0-100):**
- 100: accuracy ≤ 5m (eccellente)
- 90: accuracy ≤ 10m (ottimo)
- 70: accuracy ≤ 20m (buono)
- 50: accuracy ≤ 50m (discreto)
- 30: accuracy ≤ 100m (scarso)
- 0: accuracy > 100m (molto scarso)

### 4. Utilità Geospaziali (`app/utils/geo_utils.py`)

**Funzioni principali:**
- `haversine_distance()`: Distanza tra due coordinate GPS
- `distance_point_to_track()`: Distanza punto-percorso
- `find_closest_point_on_track()`: Punto più vicino su percorso
- `calculate_track_length()`: Lunghezza totale percorso
- `calculate_bearing()`: Direzione tra due punti
- `interpolate_points()`: Interpolazione punti
- `smooth_track()`: Smoothing percorso (media mobile)
- `simplify_track()`: Semplificazione (Douglas-Peucker)

### 5. Main App (`main.py`)

**Schermate:**
- `ModeSelectionScreen`: Selezione modalità operativa
  - Disperso
  - Unità Cinofila
  - Addestratore
  - Impostazioni

**Gestione lifecycle:**
- `on_start()`: Inizializzazione app
- `on_pause()`: Pausa (ferma GPS)
- `on_resume()`: Ripresa
- `on_stop()`: Chiusura (cleanup)

## 🔄 Prossime Fasi

### Fase 3: Modalità Disperso (TODO)
- [ ] UI schermata Disperso
- [ ] Registrazione percorso GPS
- [ ] Export formato CSV
- [ ] Condivisione via messaggistica

### Fase 4: Modalità Unità Cinofila (TODO)
- [ ] UI schermata Unità Cinofila
- [ ] Import percorso da clipboard
- [ ] Sistema alert acustici
- [ ] Calcolo distanza real-time

### Fase 5: Modalità Addestratore (TODO)
- [ ] UI schermata Addestratore
- [ ] Integrazione MapView
- [ ] Visualizzazione percorso su mappa
- [ ] Tracciamento live posizione

### Fase 6: Navigazione e UX (TODO)
- [ ] Gestione percorsi salvati
- [ ] Settings globali
- [ ] Tutorial primo utilizzo

### Fase 7: Build e Deployment (TODO)
- [ ] Build APK Android
- [ ] Test su dispositivi reali
- [ ] Ottimizzazioni

## 🧪 Testing

### Test Automatici
Il file `test_core.py` verifica tutti i componenti core:

```bash
python test_core.py
```

### Test Manuali Desktop
1. Avvia l'app: `python main.py`
2. Verifica schermata selezione modalità
3. Testa navigazione tra schermate

### Test Android (quando disponibile)
```bash
# Build APK debug
buildozer -v android debug

# Deploy su dispositivo
buildozer android deploy run
```

## 📝 Convenzioni Codice

- **Docstrings**: Tutti i metodi pubblici hanno docstring
- **Type hints**: Usati dove possibile per chiarezza
- **Naming**: snake_case per funzioni/variabili, PascalCase per classi
- **Commenti**: Sezioni marcate con `# ===...===`

## 🐛 Debug

### Logging
```python
# In main.py, abilita logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### GPS Mock
Per testare senza GPS reale:
```python
from app.services.gps_service import MockGPSService
gps = MockGPSService(start_lat=45.4642, start_lon=9.1900)
```

### Database in Memoria
Per testare senza file database:
```python
from app.models.database import DatabaseManager
db = DatabaseManager(":memory:")
```

## 📚 Risorse

- [Kivy Documentation](https://kivy.org/doc/stable/)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Plyer Documentation](https://plyer.readthedocs.io/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone <repository_url>
cd Mantrailing_App_Mobile

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Esegui test
python test_core.py

# 4. Avvia app
python main.py
```

## 📊 Stato Sviluppo

| Componente | Stato | Note |
|------------|-------|------|
| Setup Progetto | ✅ | Completato |
| Database | ✅ | Completato |
| Modello Track | ✅ | Completato |
| GPS Service | ✅ | Completato (con mock) |
| Geo Utils | ✅ | Completato |
| App Base | ✅ | Schermata selezione |
| Modalità Disperso | 🔲 | TODO Fase 3 |
| Modalità Cinofila | 🔲 | TODO Fase 4 |
| Modalità Addestratore | 🔲 | TODO Fase 5 |
| Build Android | 🔲 | TODO Fase 7 |

---

**Ultimo aggiornamento:** 2025-11-18
**Versione:** 0.1.0-dev
**Fasi completate:** 1-2 / 10
