"""
Schermata Modalità Unità Cinofila.
Importa un percorso e fornisce alert acustici quando ci si allontana.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.core.audio import SoundLoader

from app.models.track import Track
from app.services.gps_service import get_gps_service
from app.utils.geo_utils import distance_point_to_track


class CinofilaScreen(Screen):
    """Schermata per la modalità unità cinofila."""

    # Properties
    is_active = BooleanProperty(False)
    distance_from_track = NumericProperty(0)
    current_lat = StringProperty("--")
    current_lon = StringProperty("--")
    alert_radius = NumericProperty(200)  # metri
    alert_active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'cinofila'

        # Dati
        self.track = None
        self.gps_service = None
        self.beep_sound = None
        self.clock_event = None

        # Costruisci UI
        self.build_ui()

    def build_ui(self):
        """Costruisce l'interfaccia utente."""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint=(1, 0.08), spacing=10)
        back_btn = Button(
            text='← Indietro',
            size_hint=(0.3, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)

        title = Label(
            text='MODALITÀ UNITÀ CINOFILA',
            font_size='18sp',
            bold=True,
            size_hint=(0.7, 1)
        )

        header.add_widget(back_btn)
        header.add_widget(title)
        layout.add_widget(header)

        # Istruzioni
        instructions = Label(
            text='Incolla il percorso ricevuto dal disperso:',
            size_hint=(1, 0.05),
            font_size='12sp'
        )
        layout.add_widget(instructions)

        # Text area per incollare percorso
        self.track_input = TextInput(
            multiline=True,
            size_hint=(1, 0.15),
            hint_text='45.4642,9.19,95;45.465,9.191,90;...'
        )
        layout.add_widget(self.track_input)

        # Pulsante Import
        import_btn = Button(
            text='IMPORTA PERCORSO',
            size_hint=(1, 0.08),
            background_color=(0.2, 0.6, 0.9, 1)
        )
        import_btn.bind(on_press=self.import_track)
        layout.add_widget(import_btn)

        # Info percorso importato
        self.track_info = Label(
            text='Nessun percorso caricato',
            size_hint=(1, 0.05),
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        layout.add_widget(self.track_info)

        # Distanza dal percorso
        distance_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)
        distance_box.add_widget(Label(
            text='Distanza dal percorso:',
            font_size='14sp',
            size_hint=(1, 0.3)
        ))

        self.distance_label = Label(
            text='-- m',
            font_size='32sp',
            bold=True,
            size_hint=(1, 0.7)
        )
        distance_box.add_widget(self.distance_label)
        layout.add_widget(distance_box)

        # Stato alert
        self.alert_status = Label(
            text='',
            size_hint=(1, 0.06),
            font_size='14sp',
            bold=True
        )
        layout.add_widget(self.alert_status)

        # Settings raggio alert
        settings_box = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)
        settings_box.add_widget(Label(
            text=f'Raggio alert: {int(self.alert_radius)} metri',
            font_size='12sp'
        ))

        self.radius_slider = Slider(
            min=50,
            max=500,
            value=self.alert_radius,
            step=50
        )
        self.radius_slider.bind(value=self.on_radius_change)
        settings_box.add_widget(self.radius_slider)

        layout.add_widget(settings_box)

        # Pulsante START/STOP
        self.start_btn = Button(
            text='INIZIA RICERCA',
            size_hint=(1, 0.12),
            background_color=(0.3, 0.7, 0.3, 1),
            font_size='18sp',
            disabled=True
        )
        self.start_btn.bind(on_press=self.toggle_search)
        layout.add_widget(self.start_btn)

        # Info GPS
        gps_box = BoxLayout(size_hint=(1, 0.06))
        self.gps_label = Label(
            text='GPS: --',
            font_size='11sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        gps_box.add_widget(self.gps_label)
        layout.add_widget(gps_box)

        self.add_widget(layout)

    def on_enter(self):
        """Chiamato quando si entra nella schermata."""
        # Inizializza GPS service
        self.gps_service = get_gps_service(use_mock=not self.is_mobile())

        # Configura GPS
        self.gps_service.configure(min_time=1000, min_distance=0)

        # Inizializza suono beep (simulato con print su desktop)
        self.init_beep_sound()

    def on_leave(self):
        """Chiamato quando si esce dalla schermata."""
        # Ferma ricerca se attiva
        if self.is_active:
            self.stop_search()

        # Ferma GPS
        if self.gps_service:
            self.gps_service.stop()

    def init_beep_sound(self):
        """Inizializza il suono di alert."""
        # Su desktop, usa print. Su mobile, carica un suono reale
        if self.is_mobile():
            # TODO: Caricare un file audio reale
            # self.beep_sound = SoundLoader.load('app/assets/sounds/beep.wav')
            pass
        else:
            print("Alert sonoro simulato (desktop mode)")

    def import_track(self, instance):
        """Importa il percorso dal text input."""
        track_str = self.track_input.text.strip()

        if not track_str:
            self.show_message("Errore", "Inserisci un percorso da importare!")
            return

        try:
            # Parse il percorso
            self.track = Track.from_string(track_str)

            # Valida
            is_valid, error = self.track.validate()
            if not is_valid:
                self.show_message("Errore", f"Percorso non valido: {error}")
                self.track = None
                return

            # Aggiorna UI
            self.track_info.text = f'✓ Percorso caricato: {self.track.get_point_count()} punti'
            self.track_info.color = (0.2, 0.8, 0.2, 1)
            self.start_btn.disabled = False

            # Calcola info percorso
            from app.utils.geo_utils import calculate_track_length
            length = calculate_track_length(self.track)

            self.show_message(
                "Successo",
                f"Percorso importato!\n\n"
                f"Punti: {self.track.get_point_count()}\n"
                f"Lunghezza: {int(length)} metri\n"
                f"Raggio alert: {int(self.alert_radius)} metri"
            )

        except Exception as e:
            self.show_message("Errore", f"Errore importazione: {str(e)}")
            self.track = None

    def toggle_search(self, instance):
        """Avvia o ferma la ricerca."""
        if self.is_active:
            self.stop_search()
        else:
            self.start_search()

    def start_search(self):
        """Avvia la modalità ricerca con alert."""
        if not self.track:
            self.show_message("Errore", "Importa prima un percorso!")
            return

        self.is_active = True

        # Avvia GPS
        self.gps_service.start(
            on_location=self.on_gps_location,
            on_status=self.on_gps_status
        )

        # Aggiorna UI
        self.start_btn.text = 'FERMA RICERCA'
        self.start_btn.background_color = (0.9, 0.2, 0.2, 1)
        self.track_input.disabled = True
        self.radius_slider.disabled = True

        # Avvia check periodico alert
        self.clock_event = Clock.schedule_interval(self.check_alert, 1.0)

        print("Ricerca avviata")

    def stop_search(self):
        """Ferma la modalità ricerca."""
        self.is_active = False

        # Ferma GPS
        if self.gps_service:
            self.gps_service.stop()

        # Ferma check alert
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

        # Ferma alert se attivo
        self.alert_active = False

        # Aggiorna UI
        self.start_btn.text = 'INIZIA RICERCA'
        self.start_btn.background_color = (0.3, 0.7, 0.3, 1)
        self.track_input.disabled = False
        self.radius_slider.disabled = False
        self.alert_status.text = ''

        print("Ricerca fermata")

    def on_gps_location(self, lat, lon, altitude, accuracy, speed):
        """Callback per nuove posizioni GPS."""
        self.current_lat = f"{lat:.6f}"
        self.current_lon = f"{lon:.6f}"

        # Aggiorna label GPS
        quality = self.gps_service.get_gps_quality(accuracy)
        self.gps_label.text = f'GPS: {self.current_lat}, {self.current_lon} (Q:{quality})'

        # Calcola distanza dal percorso
        if self.track and self.is_active:
            distance = distance_point_to_track(lat, lon, self.track)
            if distance is not None:
                self.distance_from_track = distance
                self.distance_label.text = f'{int(distance)} m'

                # Colora in base alla distanza
                if distance > self.alert_radius:
                    self.distance_label.color = (1, 0, 0, 1)  # Rosso
                elif distance > self.alert_radius * 0.7:
                    self.distance_label.color = (1, 0.5, 0, 1)  # Arancione
                else:
                    self.distance_label.color = (0, 1, 0, 1)  # Verde

    def on_gps_status(self, status_type, message):
        """Callback per stato GPS."""
        print(f"GPS Status: {status_type} - {message}")

    def check_alert(self, dt):
        """Controlla se emettere alert acustico."""
        if not self.is_active or not self.track:
            return

        # Se fuori dal raggio, attiva alert
        if self.distance_from_track > self.alert_radius:
            if not self.alert_active:
                self.alert_active = True
                self.alert_status.text = '⚠ FUORI PERCORSO! ⚠'
                self.alert_status.color = (1, 0, 0, 1)

            # Emetti beep
            self.play_beep()

        else:
            if self.alert_active:
                self.alert_active = False
                self.alert_status.text = '✓ Sul percorso'
                self.alert_status.color = (0, 1, 0, 1)

    def play_beep(self):
        """Emette il suono di alert."""
        if self.is_mobile() and self.beep_sound:
            # Riproduci suono su mobile
            self.beep_sound.play()
        else:
            # Simula con print su desktop
            print(f"🔊 BEEP! Distanza: {int(self.distance_from_track)}m (limite: {int(self.alert_radius)}m)")

        # TODO: Su Android, usare anche vibrazione
        # from plyer import vibrator
        # vibrator.vibrate(0.5)

    def on_radius_change(self, instance, value):
        """Callback per cambio raggio alert."""
        self.alert_radius = value
        # Aggiorna label
        for child in self.children[0].children:
            if isinstance(child, BoxLayout):
                for subchild in child.children:
                    if isinstance(subchild, Label) and 'Raggio alert' in subchild.text:
                        subchild.text = f'Raggio alert: {int(value)} metri'

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
