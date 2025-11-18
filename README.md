# MANTRAILING TRAINING APP
==================================================

App mobile per l'addestramento di cani da ricerca persone scomparse (mantrailing).
Sviluppata con Kivy/Python per Android e iOS.

==================================================
DESCRIZIONE
==================================================

L'applicazione permette di simulare scenari di addestramento mantrailing attraverso 
tre modalità operative:

1. MODALITÀ DISPERSO
   Registra il percorso effettuato dalla persona "dispersa"
   
2. MODALITÀ UNITÀ CINOFILA
   Segue il percorso registrato con assistenza acustica
   
3. MODALITÀ ADDESTRATORE
   Monitora l'esercitazione su mappa con visualizzazione completa

==================================================
FUNZIONALITÀ PER MODALITÀ
==================================================

--- MODALITÀ DISPERSO ---

La persona che simula il disperso utilizza questa modalità per registrare 
il proprio percorso di nascondimento.

Funzionalità:
- Tracciamento GPS continuo della posizione
- Registrazione punti con coordinate (latitudine, longitudine, qualità segnale)
- Esportazione percorso in formato testuale copiabile
- Nessuna visualizzazione mappa (per evitare consumo batteria)

Formato esportazione:
lat1,lon1,quality1;lat2,lon2,quality2;...;latN,lonN,qualityN

Settings:
- Frequenza campionamento (in secondi) - regolabile per adattarsi alla durata
  e complessità del percorso

Utilizzo:
1. Avviare registrazione
2. Effettuare il percorso di nascondimento
3. Terminare registrazione
4. Copiare il testo generato
5. Inviare via WhatsApp/Telegram/SMS all'addestratore


--- MODALITÀ UNITÀ CINOFILA ---

Il conduttore cinofilo utilizza questa modalità durante l'esercitazione di ricerca.
Il percorso rimane nascosto per simulare una ricerca reale.

Funzionalità:
- Importazione percorso tramite copia-incolla
- Tracciamento GPS continuo della posizione
- Alert acustico quando ci si allontana dal percorso
- Nessuna visualizzazione mappa (per concentrarsi sul cane)

Algoritmo alert:
- Calcola continuamente la distanza minima dal percorso registrato
- Emette segnale acustico se distanza > raggio impostato
- Frequenza/intensità del segnale può aumentare con la distanza

Settings:
- Raggio alert (default: 200 metri) - regolabile in base al livello 
  di addestramento del cane e alla difficoltà desiderata

Utilizzo:
1. Ricevere il percorso dall'addestratore
2. Incollare il percorso nell'app
3. Iniziare la ricerca con il cane
4. Seguire le indicazioni acustiche per rimanere sul percorso


--- MODALITÀ ADDESTRATORE ---

L'addestratore utilizza questa modalità per monitorare l'esercitazione 
e verificare l'accuratezza del lavoro del cane.

Funzionalità:
- Importazione percorso tramite copia-incolla
- Visualizzazione mappa completa
- Tracciamento GPS continuo della posizione dell'addestratore
- Visualizzazione grafica del percorso del disperso

Visualizzazione percorso:
- Linea colorata con gradiente basato sulla qualità GPS:
  - BLU: segnale GPS ottimo (alta qualità)
  - VERDE: segnale GPS buono
  - GIALLO: segnale GPS discreto
  - ARANCIONE: segnale GPS scarso
  - ROSSO: segnale GPS assente/molto scarso
  
- Cerchi neri sui punti campionati per visualizzare la densità
  del tracciamento

- Indicatore posizione live dell'addestratore

Utilizzo:
1. Ricevere il percorso dal disperso
2. Incollare il percorso nell'app
3. Seguire l'unità cinofila a distanza
4. Monitorare su mappa l'aderenza al percorso originale
5. Valutare la performance del cane

==================================================
FORMATO DATI
==================================================

I percorsi vengono salvati e scambiati in formato testuale:

lat,lon,quality;lat,lon,quality;...;lat,lon,quality

Dove:
- lat = latitudine (gradi decimali, es: 45.4642)
- lon = longitudine (gradi decimali, es: 9.1900)
- quality = qualità segnale GPS (valore da 0 a 100, o altro standard)

Esempio:
45.4642,9.1900,95;45.4643,9.1902,87;45.4645,9.1905,92

Vantaggi formato:
- Leggero e compatto
- Facile da copiare/incollare
- Compatibile con qualsiasi app di messaggistica
- Nessun server necessario
- Privacy garantita (dati solo in locale)

==================================================
REQUISITI TECNICI
==================================================

Hardware:
- GPS integrato
- Almeno 50 MB spazio libero
- Connessione internet per mappe (modalità addestratore)

Permessi richiesti:
- Accesso GPS/posizione (sempre, anche in background)
- Accesso memoria (per salvare percorsi localmente)
- Accesso clipboard (per copia-incolla percorsi)

Sistema operativo:
- Android 6.0 o superiore
- iOS 12.0 o superiore

==================================================
PRIVACY E SICUREZZA
==================================================

- Tutti i dati sono salvati SOLO in locale sul dispositivo
- Nessun server remoto coinvolto
- Nessuna registrazione utente richiesta
- I percorsi sono condivisi manualmente dall'utente via messaggistica
- Possibilità di eliminare percorsi salvati in qualsiasi momento

==================================================
STACK TECNOLOGICO
==================================================

Framework:
- Kivy - Framework Python cross-platform
- KivyMD - Material Design components

Librerie:
- plyer - Accesso GPS cross-platform
- kivy-garden.mapview - Visualizzazione mappe OpenStreetMap
- sqlite3 - Database locale

Build:
- Buildozer - Compilazione APK Android
- python-for-android - Backend Android

==================================================
INSTALLAZIONE
==================================================

[Da completare con istruzioni specifiche per la pubblicazione]

Android:
- Download APK dal sito ufficiale
- Abilitare "Installa da origini sconosciute"
- Installare e concedere permessi necessari

iOS:
- Download da App Store
- Concedere permessi necessari

==================================================
USO CONSIGLIATO
==================================================

Scenario tipico di addestramento:

1. PREPARAZIONE
   • Il disperso apre l'app in modalità "Disperso"
   • Configura frequenza campionamento (es: ogni 5 secondi per percorsi brevi,
     ogni 10-15 secondi per percorsi lunghi)
   • Avvia registrazione

2. PERCORSO
   • Il disperso effettua il percorso di nascondimento
   • L'app registra automaticamente la posizione
   • Al termine, il disperso termina la registrazione

3. CONDIVISIONE
   • L'app genera il testo con il percorso
   • Il disperso copia il testo
   • Invia il testo via WhatsApp/Telegram all'addestratore

4. CONFIGURAZIONE UNITÀ CINOFILA
   • Il conduttore riceve il percorso
   • Apre l'app in modalità "Unità Cinofila"
   • Incolla il percorso
   • Configura raggio alert (es: 200m per cani esperti, 300m per principianti)

5. CONFIGURAZIONE ADDESTRATORE
   • L'addestratore riceve il percorso
   • Apre l'app in modalità "Addestratore"
   • Incolla il percorso
   • Visualizza il percorso su mappa

6. ESERCITAZIONE
   • L'unità cinofila inizia la ricerca
   • Il cane segue la traccia olfattiva
   • L'app emette alert acustici se ci si allontana dal percorso
   • L'addestratore monitora su mappa

7. DEBRIEFING
   • Analisi del percorso effettuato vs percorso originale
   • Valutazione della performance del cane
   • Identificazione aree di miglioramento

==================================================
TIPS & BEST PRACTICES
==================================================

Per il Disperso:
- Verificare che il GPS sia attivo prima di iniziare
- In aree boschive, aumentare la frequenza di campionamento
- Tenere il telefono in posizione stabile (tasca/zaino)
- Verificare la batteria prima di iniziare

Per l'Unità Cinofila:
- Non guardare l'app durante la ricerca, solo ascoltare
- Impostare un raggio alert adeguato al livello del cane
- Volume alert a livello udibile ma non disturbante per il cane
- Tenere il telefono in tasca o fascia braccio

Per l'Addestratore:
- Mantenere distanza dall'unità cinofila per non interferire
- Osservare pattern di deviazione dal percorso
- Annotare punti critici per il debriefing
- Considerare qualità GPS nei punti di deviazione

Generali:
- Salvare percorsi interessanti per riutilizzo futuro
- Testare l'app in condizioni normali prima dell'esercitazione
- Portare batterie esterne per sessioni lunghe
- Calibrare i settings in base all'ambiente (bosco, urbano, misto)

==================================================
SUPPORTO
==================================================

[Da completare con informazioni di contatto]

Per bug, suggerimenti o richieste:
- Email: [email]
- GitHub: [repository]
- Telegram: [gruppo]

==================================================
LICENZA
==================================================

[Da definire]

==================================================
CREDITI
==================================================

Sviluppato per la comunità cinofila di ricerca persone scomparse.

Grazie a tutti i conduttori e addestratori che hanno contribuito
con feedback e test sul campo.

==================================================
