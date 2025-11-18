"""
Schermata Modalità Disperso.
Permette di registrare il percorso GPS del disperso e esportarlo.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from datetime import datetime
import time

from app.models.track import Track
from app.models.database import get_database
from app.services.gps_service import get_gps_service


class DispersoScreen(Screen):
    """Schermata per la modalità disperso."""

    # Properties
    is_recording = BooleanProperty(False)
    points_count = NumericProperty(0)
    gps_quality = NumericProperty(0)
    recording_time = StringProperty("00:00:00")
    current_lat = StringProperty("--")
    current_lon = StringProperty("--")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'disperso'

        # Dati
        self.track = None
        self.start_time = None
        self.gps_service = None
        self.sampling_interval = 5  # Secondi tra campionamenti
        self.last_sample_time = 0
        self.clock_event = None

        # Costruisci UI
        self.build_ui()

    def build_ui(self):
        """Costruisce l'interfaccia utente."""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint=(1, 0.1), spacing=10)
        back_btn = Button(
            text='← Indietro',
            size_hint=(0.3, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)

        title = Label(
            text='MODALITÀ DISPERSO',
            font_size='20sp',
            bold=True,
            size_hint=(0.7, 1)
        )

        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Info GPS
        info_box = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=5)

        # Coordinate
        coords_label = Label(
            text='Posizione GPS',
            font_size='14sp',
            size_hint=(1, 0.2)
        )
        info_box.add_widget(coords_label)

        coords_box = BoxLayout(size_hint=(1, 0.3))
        self.lat_label = Label(
            text=f'Lat: {self.current_lat}',
            font_size='12sp'
        )
        self.lon_label = Label(
            text=f'Lon: {self.current_lon}',
            font_size='12sp'
        )
        coords_box.add_widget(self.lat_label)
        coords_box.add_widget(self.lon_label)
        info_box.add_widget(coords_box)

        # Qualità GPS
        quality_box = BoxLayout(size_hint=(1, 0.25))
        quality_box.add_widget(Label(text='Qualità GPS:', font_size='14sp'))
        self.quality_label = Label(
            text=f'{self.gps_quality}/100',
            font_size='18sp',
            bold=True
        )
        quality_box.add_widget(self.quality_label)
        info_box.add_widget(quality_box)

        # Punti registrati
        points_box = BoxLayout(size_hint=(1, 0.25))
        points_box.add_widget(Label(text='Punti registrati:', font_size='14sp'))
        self.points_label = Label(
            text=str(self.points_count),
            font_size='18sp',
            bold=True
        )
        points_box.add_widget(self.points_label)
        info_box.add_widget(points_box)

        layout.add_widget(info_box)

        # Timer
        timer_box = BoxLayout(size_hint=(1, 0.1))
        timer_box.add_widget(Label(text='Tempo:', font_size='14sp'))
        self.timer_label = Label(
            text=self.recording_time,
            font_size='20sp',
            bold=True,
            color=(0.2, 0.6, 0.9, 1)
        )
        timer_box.add_widget(self.timer_label)
        layout.add_widget(timer_box)

        # Pulsante START/STOP
        self.record_btn = Button(
            text='AVVIA REGISTRAZIONE',
            size_hint=(1, 0.15),
            background_color=(0.2, 0.7, 0.2, 1),
            font_size='18sp'
        )
        self.record_btn.bind(on_press=self.toggle_recording)
        layout.add_widget(self.record_btn)

        # Pulsante Export
        self.export_btn = Button(
            text='ESPORTA PERCORSO',
            size_hint=(1, 0.12),
            background_color=(0.2, 0.5, 0.8, 1),
            disabled=True
        )
        self.export_btn.bind(on_press=self.export_track)
        layout.add_widget(self.export_btn)

        # Settings
        settings_box = BoxLayout(size_hint=(1, 0.13), spacing=10)
        settings_box.add_widget(Label(
            text='Frequenza campionamento (sec):',
            size_hint=(0.6, 1),
            font_size='12sp'
        ))

        self.interval_input = TextInput(
            text=str(self.sampling_interval),
            multiline=False,
            input_filter='int',
            size_hint=(0.2, 1)
        )
        self.interval_input.bind(text=self.on_interval_change)
        settings_box.add_widget(self.interval_input)

        layout.add_widget(settings_box)

        self.add_widget(layout)

    def on_enter(self):
        """Chiamato quando si entra nella schermata."""
        # Inizializza GPS service
        self.gps_service = get_gps_service(use_mock=not self.is_mobile())

        # Configura GPS
        self.gps_service.configure(min_time=1000, min_distance=0)

        # Avvia GPS per mostrare posizione corrente
        self.gps_service.start(
            on_location=self.on_gps_location,
            on_status=self.on_gps_status
        )

    def on_leave(self):
        """Chiamato quando si esce dalla schermata."""
        # Ferma registrazione se attiva
        if self.is_recording:
            self.stop_recording()

        # Ferma GPS
        if self.gps_service:
            self.gps_service.stop()

    def toggle_recording(self, instance):
        """Avvia o ferma la registrazione."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Avvia la registrazione del percorso."""
        # Crea nuovo track
        self.track = Track(
            name=f"Percorso {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description="Percorso disperso"
        )

        self.is_recording = True
        self.start_time = time.time()
        self.last_sample_time = 0
        self.points_count = 0

        # Aggiorna UI
        self.record_btn.text = 'FERMA REGISTRAZIONE'
        self.record_btn.background_color = (0.9, 0.2, 0.2, 1)
        self.export_btn.disabled = True
        self.interval_input.disabled = True

        # Avvia timer
        self.clock_event = Clock.schedule_interval(self.update_timer, 0.5)

        print("Registrazione avviata")

    def stop_recording(self):
        """Ferma la registrazione del percorso."""
        self.is_recording = False

        # Ferma timer
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

        # Aggiorna UI
        self.record_btn.text = 'AVVIA REGISTRAZIONE'
        self.record_btn.background_color = (0.2, 0.7, 0.2, 1)
        self.export_btn.disabled = False
        self.interval_input.disabled = False

        # Salva nel database
        if self.track and not self.track.is_empty():
            db = get_database()
            duration = int(time.time() - self.start_time) if self.start_time else 0
            track_id = db.save_track(
                name=self.track.name,
                track_data=self.track.to_string(),
                description=self.track.description,
                duration_seconds=duration
            )
            print(f"Percorso salvato nel database con ID: {track_id}")

        print("Registrazione fermata")

    def on_gps_location(self, lat, lon, altitude, accuracy, speed):
        """Callback per nuove posizioni GPS."""
        # Aggiorna coordinate visualizzate
        self.current_lat = f"{lat:.6f}"
        self.current_lon = f"{lon:.6f}"
        self.lat_label.text = f'Lat: {self.current_lat}'
        self.lon_label.text = f'Lon: {self.current_lon}'

        # Calcola qualità
        self.gps_quality = self.gps_service.get_gps_quality(accuracy)
        self.quality_label.text = f'{self.gps_quality}/100'

        # Colora in base alla qualità
        if self.gps_quality >= 90:
            color = (0, 0, 1, 1)  # Blu
        elif self.gps_quality >= 70:
            color = (0, 1, 0, 1)  # Verde
        elif self.gps_quality >= 50:
            color = (1, 1, 0, 1)  # Giallo
        elif self.gps_quality >= 30:
            color = (1, 0.5, 0, 1)  # Arancione
        else:
            color = (1, 0, 0, 1)  # Rosso

        self.quality_label.color = color

        # Se registrazione attiva, campiona in base all'intervallo
        if self.is_recording:
            current_time = time.time()
            if current_time - self.last_sample_time >= self.sampling_interval:
                self.track.add_point(lat, lon, self.gps_quality)
                self.points_count = self.track.get_point_count()
                self.points_label.text = str(self.points_count)
                self.last_sample_time = current_time
                print(f"Punto registrato: {lat:.6f}, {lon:.6f} (q={self.gps_quality})")

    def on_gps_status(self, status_type, message):
        """Callback per stato GPS."""
        print(f"GPS Status: {status_type} - {message}")

    def update_timer(self, dt):
        """Aggiorna il timer della registrazione."""
        if self.is_recording and self.start_time:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.recording_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.text = self.recording_time

    def on_interval_change(self, instance, value):
        """Callback per cambio intervallo campionamento."""
        try:
            interval = int(value) if value else 5
            if interval < 1:
                interval = 1
            elif interval > 60:
                interval = 60
            self.sampling_interval = interval
        except ValueError:
            pass

    def export_track(self, instance):
        """Esporta il percorso in formato CSV."""
        if not self.track or self.track.is_empty():
            self.show_message("Errore", "Nessun percorso da esportare!")
            return

        # Genera stringa CSV
        track_str = self.track.to_string()

        # Mostra popup con il percorso
        self.show_export_popup(track_str)

    def show_export_popup(self, track_str):
        """Mostra popup per esportare/copiare il percorso."""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Info
        info = Label(
            text=f'Percorso con {self.points_count} punti\nCopia il testo e invialo via WhatsApp/Telegram',
            size_hint=(1, 0.2),
            font_size='12sp'
        )
        content.add_widget(info)

        # Text area con il percorso
        text_area = TextInput(
            text=track_str,
            multiline=True,
            readonly=True,
            size_hint=(1, 0.6)
        )
        content.add_widget(text_area)

        # Pulsanti
        buttons = BoxLayout(size_hint=(1, 0.2), spacing=10)

        copy_btn = Button(
            text='COPIA',
            background_color=(0.2, 0.6, 0.9, 1)
        )
        copy_btn.bind(on_press=lambda x: self.copy_to_clipboard(track_str))

        close_btn = Button(
            text='CHIUDI',
            background_color=(0.5, 0.5, 0.5, 1)
        )

        buttons.add_widget(copy_btn)
        buttons.add_widget(close_btn)
        content.add_widget(buttons)

        # Crea popup
        popup = Popup(
            title='Esporta Percorso',
            content=content,
            size_hint=(0.9, 0.8)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def copy_to_clipboard(self, text):
        """Copia il testo negli appunti."""
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            self.show_message("Successo", "Percorso copiato negli appunti!")
        except Exception as e:
            print(f"Errore copia clipboard: {e}")
            self.show_message("Errore", "Impossibile copiare negli appunti")

    def show_message(self, title, message):
        """Mostra un messaggio popup."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))

        btn = Button(text='OK', size_hint=(1, 0.3))
        content.add_widget(btn)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        """Torna alla schermata di selezione modalità."""
        self.manager.current = 'mode_selection'

    @staticmethod
    def is_mobile():
        """Verifica se siamo su mobile."""
        from kivy.utils import platform
        return platform in ('android', 'ios')
