# Guida Build APK Android

Questa guida spiega come creare l'APK Android dell'app Mantrailing Training.

## 📋 Prerequisiti

**IMPORTANTE:** Buildozer funziona solo su **Linux**. Su Windows hai 3 opzioni:
1. **WSL** (Windows Subsystem for Linux) - **CONSIGLIATO**
2. **VM Linux** (VirtualBox, VMware)
3. **GitHub Actions** (build automatico su cloud)

---

## 🟦 Opzione 1: WSL su Windows (CONSIGLIATO)

### Passo 1: Installa WSL

```powershell
# In PowerShell come Amministratore
wsl --install
```

Oppure:
```powershell
wsl --install -d Ubuntu-22.04
```

**Riavvia il PC** dopo l'installazione.

### Passo 2: Avvia WSL

```powershell
# Apri WSL Ubuntu
wsl
```

Crea username e password quando richiesto.

### Passo 3: Installa Dipendenze

```bash
# Aggiorna sistema
sudo apt update
sudo apt upgrade -y

# Installa Python e dipendenze build
sudo apt install -y python3 python3-pip python3-venv git zip unzip

# Installa Java (necessario per Android SDK)
sudo apt install -y openjdk-17-jdk

# Installa dipendenze Buildozer
sudo apt install -y build-essential libssl-dev libffi-dev \
    python3-dev autoconf automake libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev \
    ccache autoconf automake libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev

# Installa Cython
pip3 install --upgrade cython
```

### Passo 4: Accedi al Progetto

WSL può accedere ai file Windows in `/mnt/c/`:

```bash
# Esempio: Se il progetto è in C:\Users\tuonome\Desktop\Mantrailing_App_Mobile
cd /mnt/c/Users/tuonome/Desktop/Pitone/ProgettoMantrailing/Mantrailing_App_Mobile

# Verifica di essere nella directory giusta
ls -la
# Dovresti vedere: main.py, buildozer.spec, app/, etc.
```

### Passo 5: Installa Buildozer

```bash
# Installa Buildozer
pip3 install buildozer

# Verifica installazione
buildozer --version
```

### Passo 6: Build APK

```bash
# Prima build (può richiedere 30-60 minuti, scarica Android SDK/NDK)
buildozer android debug

# Build successive (molto più veloci)
buildozer android debug
```

**IMPORTANTE:** La prima build scarica:
- Android SDK (~500 MB)
- Android NDK (~1 GB)
- Dipendenze Python per Android

### Passo 7: Trova l'APK

```bash
# L'APK sarà in:
ls -lh bin/

# Dovresti vedere: mantrailing-0.1.0-armeabi-v7a_arm64-v8a-debug.apk
```

### Passo 8: Trasferisci APK su Windows

```bash
# Copia APK nella cartella Windows
cp bin/*.apk /mnt/c/Users/tuonome/Desktop/
```

Ora l'APK è sul tuo Desktop Windows!

---

## 🟩 Opzione 2: VM Linux (VirtualBox)

### Passo 1: Installa VirtualBox

1. Download: https://www.virtualbox.org/wiki/Downloads
2. Installa VirtualBox
3. Download Ubuntu ISO: https://ubuntu.com/download/desktop

### Passo 2: Crea VM

1. Nuova VM in VirtualBox
2. Nome: "BuildozerVM"
3. RAM: Almeno 4 GB
4. Disco: Almeno 30 GB
5. Monta ISO Ubuntu e installa

### Passo 3: Trasferisci Progetto

Opzioni:
- **Git**: `git clone` del repository
- **Shared Folder**: Configura cartella condivisa VirtualBox
- **USB**: Copia su chiavetta USB

### Passo 4: Segui Istruzioni WSL

Dalla VM Ubuntu, segui gli stessi comandi dell'Opzione 1 (Passo 3-7).

---

## ☁️ Opzione 3: GitHub Actions (Build Cloud)

### Vantaggi
- ✅ Nessuna configurazione locale
- ✅ Build automatico ad ogni push
- ✅ Gratis per repository pubblici

### Setup

Crea file `.github/workflows/build-android.yml`:

```yaml
name: Build Android APK

on:
  push:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y openjdk-17-jdk autoconf automake libtool pkg-config
        pip install buildozer cython

    - name: Build with Buildozer
      run: buildozer android debug

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: mantrailing-apk
        path: bin/*.apk
```

**Come usare:**
1. Fai commit di questo file
2. Push su GitHub
3. Vai su GitHub → Actions
4. Scarica l'APK dagli artifacts

---

## 🔧 Troubleshooting Build

### Errore: "Command failed: ..."

**Soluzione:**
```bash
# Pulisci build precedente
buildozer android clean

# Riprova
buildozer android debug
```

### Errore: "SDK License not accepted"

**Soluzione:**
```bash
# Accetta licenze SDK
buildozer android debug
# Quando chiede di accettare licenze, digita: y
```

### Errore: "NDK not found"

**Soluzione:**
```bash
# Forza re-download NDK
rm -rf ~/.buildozer/android/platform/android-ndk-*
buildozer android debug
```

### Errore: Spazio disco insufficiente

**Soluzione:**
```bash
# Libera spazio
sudo apt clean
sudo apt autoremove

# Buildozer cache può essere grande
du -sh ~/.buildozer
```

### Build troppo lenta

**Soluzione:**
```bash
# Usa ccache per velocizzare build successive
sudo apt install ccache
export USE_CCACHE=1
```

---

## 📱 Installa APK su Android

### Via USB

1. **Abilita Debug USB** su telefono:
   - Impostazioni → Info telefono
   - Tap 7 volte su "Numero build"
   - Torna indietro → Opzioni sviluppatore
   - Abilita "Debug USB"

2. **Collega telefono a PC**

3. **Trasferisci APK:**
```bash
# Su WSL/Linux
adb install bin/mantrailing-*.apk

# Oppure copia manualmente
adb push bin/mantrailing-*.apk /sdcard/Download/
```

4. **Installa da File Manager** sul telefono

### Via Cloud

1. Carica APK su Google Drive / Dropbox
2. Apri link dal telefono
3. Scarica e installa

### Via Email

1. Invia APK via email a te stesso
2. Apri email sul telefono
3. Scarica allegato e installa

**IMPORTANTE:** Devi abilitare "Installa app da origini sconosciute" nelle impostazioni Android!

---

## 🚀 Build Release (per Pubblicazione)

Quando sei pronto per pubblicare su Google Play:

```bash
# Build release (richiede keystore)
buildozer android release

# Firma APK
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore mykeystore.keystore \
  bin/mantrailing-*.apk myalias
```

**Keystore:** Crea con `keytool`:
```bash
keytool -genkey -v -keystore mykeystore.keystore \
  -alias myalias -keyalg RSA -keysize 2048 -validity 10000
```

---

## ⚙️ Personalizzazione Build

### Cambia Nome App

In `buildozer.spec`:
```ini
title = Mantrailing Training
```

### Cambia Icona

1. Crea icona 512x512 PNG: `icon.png`
2. In `buildozer.spec`:
```ini
icon.filename = %(source.dir)s/icon.png
```

### Cambia Versione

In `buildozer.spec`:
```ini
version = 0.2.0
```

### Cambia Permessi

In `buildozer.spec`:
```ini
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,...
```

### Cambia Architetture

In `buildozer.spec`:
```ini
# Solo ARM 64-bit (file più piccolo)
android.archs = arm64-v8a

# ARM 32+64 bit (compatibilità massima)
android.archs = arm64-v8a, armeabi-v7a
```

---

## 📊 Checklist Build

Prima di fare il build:

- [ ] `buildozer.spec` configurato correttamente
- [ ] Versione aggiornata
- [ ] Icona pronta (opzionale)
- [ ] Permessi corretti
- [ ] Testato su desktop (tutte le modalità)
- [ ] Database funziona
- [ ] GPS mock funziona
- [ ] Spazio disco sufficiente (almeno 10 GB liberi)
- [ ] Connessione internet stabile (prima build)

---

## 🎯 Quick Start WSL

**TL;DR - Setup rapido:**

```bash
# 1. Installa WSL (PowerShell Amministratore)
wsl --install

# 2. Riavvia PC

# 3. Apri WSL
wsl

# 4. Setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git openjdk-17-jdk build-essential
pip3 install buildozer cython

# 5. Vai al progetto
cd /mnt/c/Users/TUONOME/Desktop/Pitone/ProgettoMantrailing/Mantrailing_App_Mobile

# 6. Build!
buildozer android debug

# 7. Aspetta 30-60 min (prima volta)

# 8. APK pronto in bin/
ls -lh bin/
```

---

## 📚 Risorse

- **Buildozer Docs**: https://buildozer.readthedocs.io/
- **Python for Android**: https://python-for-android.readthedocs.io/
- **Kivy Android**: https://kivy.org/doc/stable/guide/android.html
- **WSL Docs**: https://learn.microsoft.com/en-us/windows/wsl/

---

## 🆘 Supporto

**Problemi comuni:**
1. Build fallisce → Controlla log: `.buildozer/logs/`
2. APK non si installa → Abilita "origini sconosciute"
3. App crasha → Controlla log: `adb logcat | grep python`
4. Permessi negati → Controlla permessi in buildozer.spec

**Log dettagliato:**
```bash
buildozer -v android debug
```

---

**Buona build!** 🚀
