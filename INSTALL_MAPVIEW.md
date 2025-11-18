# Come Installare MapView su Windows

## 📦 Installazione Rapida

### Metodo 1: Pip (Consigliato)

```bash
pip install kivy-garden.mapview
```

### Metodo 2: Kivy Garden

Se il Metodo 1 non funziona:

```bash
# 1. Installa kivy-garden
pip install kivy-garden

# 2. Installa mapview tramite garden
garden install mapview
```

## ⚠️ Problemi Comuni su Windows

### Problema: "No module named 'kivy_garden.mapview'"

**Soluzione 1 - Reinstalla:**
```bash
pip uninstall kivy-garden.mapview
pip install kivy-garden.mapview --no-cache-dir
```

**Soluzione 2 - Installa versione specifica:**
```bash
pip install kivy-garden.mapview==1.0.6
```

**Soluzione 3 - Da GitHub:**
```bash
pip install https://github.com/kivy-garden/mapview/archive/master.zip
```

### Problema: MapView non si visualizza o va in crash

**Cause possibili:**
1. **Nessuna connessione internet** - MapView scarica tile da OpenStreetMap online
2. **Firewall blocca connessione** - Controlla impostazioni firewall
3. **Problemi con SDL2** - MapView usa SDL2 che può avere problemi su Windows

**Soluzioni:**
- Verifica connessione internet
- Prova su altra rete WiFi
- Disabilita temporaneamente firewall per test
- Aggiorna Kivy: `pip install --upgrade kivy`

## ✅ Verifica Installazione

Dopo l'installazione, testa con questo script:

```python
# test_mapview.py
try:
    from kivy_garden.mapview import MapView, MapMarker
    print("✓ MapView installato correttamente!")
    print(f"  - MapView: {MapView}")
    print(f"  - MapMarker: {MapMarker}")
except ImportError as e:
    print("✗ MapView NON installato")
    print(f"  Errore: {e}")
```

Esegui:
```bash
python test_mapview.py
```

## 🖥️ Limitazioni su Windows Desktop

**Nota importante:** MapView è ottimizzato per **mobile** (Android/iOS), non per desktop.

### Cosa funziona:
- ✅ Visualizzazione mappa base
- ✅ Marker e layer
- ✅ Zoom e pan (con mouse)

### Cosa potrebbe non funzionare:
- ⚠️ Gesture multitouch (pinch to zoom)
- ⚠️ Rotazione mappa
- ⚠️ Performance su schermi grandi
- ⚠️ Alcune animazioni

### Alternative per Testing Desktop:

Se MapView non funziona bene su Windows, puoi:

1. **Usare placeholder** (comportamento di default nell'app)
   - Tutte le altre funzionalità funzionano
   - Solo la visualizzazione mappa è disabilitata

2. **Testare su Android reale**
   - Build APK con `buildozer android debug` (su Linux/WSL)
   - MapView funziona perfettamente su Android

3. **Usare emulatore Android**
   - Android Studio Emulator
   - MapView funziona nell'emulatore

## 📱 Su Android (Produzione)

Quando fai il build per Android, **non serve installare niente manualmente!**

Buildozer include automaticamente MapView quando:
1. È nei `requirements` in `buildozer.spec`
2. È nelle `garden_requirements`

Nel nostro `buildozer.spec`:
```ini
requirements = python3,kivy==2.2.1,kivymd==1.1.1,plyer,android,pyjnius
garden_requirements = mapview
```

Buildozer scaricherà e includerà tutto automaticamente durante il build.

## 🔍 Debug MapView

### Abilita logging dettagliato:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from kivy_garden.mapview import MapView
# ... resto del codice
```

### Controlla versioni:

```bash
pip show kivy-garden.mapview
pip show kivy
```

**Versioni consigliate:**
- Kivy: 2.2.1
- MapView: 1.0.6

## 💡 Consigli

1. **Per sviluppo su Windows:**
   - Accetta che MapView potrebbe non funzionare perfettamente
   - Usa placeholder per testare altre funzionalità
   - Testa mappa solo su Android reale

2. **Per testing completo:**
   - Testa Modalità Disperso e Cinofila su Windows (non servono mappe)
   - Testa Modalità Addestratore su Android (con mappa reale)

3. **Connessione internet:**
   - MapView **richiede** internet per scaricare tile mappa
   - Nessun internet = mappa bianca/grigia

## 🎯 Quick Fix

Se hai fretta e vuoi testare subito:

```bash
# Tentativo rapido
pip install --upgrade pip setuptools wheel
pip install kivy-garden.mapview --force-reinstall

# Poi riavvia l'app
python main.py
```

Se funziona vedrai:
- Mappa OpenStreetMap nella Modalità Addestratore
- Percorso colorato sulla mappa
- Marker posizione

Se non funziona:
- Vedrai placeholder "[MAPPA] MapView non disponibile"
- **Tutto il resto funziona comunque!**

## ℹ️ Info Aggiuntive

- **Repository GitHub**: https://github.com/kivy-garden/mapview
- **Documentazione**: https://kivy-garden.github.io/mapview/
- **Issue tracker**: https://github.com/kivy-garden/mapview/issues

---

**TL;DR**: Esegui `pip install kivy-garden.mapview` e riavvia l'app. Se non funziona, è normale su Windows - tutto funzionerà perfettamente su Android!
