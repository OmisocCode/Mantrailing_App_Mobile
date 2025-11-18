"""
Schermata Modalità Addestratore.
Visualizza il percorso su mappa con qualità GPS e traccia la posizione live.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Line, Ellipse
from kivy.properties import BooleanProperty

try:
    from kivy_garden.mapview import MapView, MapMarker, MapLayer
    MAPVIEW_AVAILABLE = True
except ImportError:
    MAPVIEW_AVAILABLE = False
    print("Warning: MapView not available. Map functionality will be limited.")
    # Crea classi placeholder quando MapView non è disponibile
    MapView = None
    MapMarker = None
    MapLayer = object  # Classe base fittizia

from app.models.track import Track
from app.services.gps_service import get_gps_service


# Definisci TrackMapLayer solo se MapView è disponibile
if MAPVIEW_AVAILABLE:
    class TrackMapLayer(MapLayer):
        """Layer personalizzato per disegnare il percorso sulla mappa."""

        def __init__(self, track=None, **kwargs):
            super().__init__(**kwargs)
            self.track = track
            self.reposition()

        def reposition(self):
            """Ridisegna il percorso sulla mappa."""
            if not self.track or self.track.is_empty():
                return

            mapview = self.parent
            if not mapview:
                return

            self.canvas.clear()

            # Disegna linee tra i punti con colori basati sulla qualità GPS
            with self.canvas:
                for i in range(len(self.track.points) - 1):
                    p1 = self.track.points[i]
                    p2 = self.track.points[i + 1]

                    # Converti coordinate GPS in coordinate schermo
                    x1, y1 = mapview.get_window_xy_from(p1.latitude, p1.longitude, mapview.zoom)
                    x2, y2 = mapview.get_window_xy_from(p2.latitude, p2.longitude, mapview.zoom)

                    # Colore in base alla qualità GPS media del segmento
                    avg_quality = (p1.quality + p2.quality) / 2
                    color = self.get_quality_color(avg_quality)

                    Color(*color)
                    Line(points=[x1, y1, x2, y2], width=3)

                # Disegna cerchi neri sui punti campionati
                Color(0, 0, 0, 0.7)
                for point in self.track.points:
                    x, y = mapview.get_window_xy_from(point.latitude, point.longitude, mapview.zoom)
                    Ellipse(pos=(x - 3, y - 3), size=(6, 6))

        @staticmethod
        def get_quality_color(quality):
            """
            Restituisce il colore RGBA in base alla qualità GPS.

            Args:
                quality: Qualità GPS (0-100)

            Returns:
                Tupla RGBA (r, g, b, a)
            """
            if quality >= 90:
                return (0, 0, 1, 1)  # Blu
            elif quality >= 70:
                return (0, 1, 0, 1)  # Verde
            elif quality >= 50:
                return (1, 1, 0, 1)  # Giallo
            elif quality >= 30:
                return (1, 0.5, 0, 1)  # Arancione
            else:
                return (1, 0, 0, 1)  # Rosso
else:
    # Classe placeholder quando MapView non è disponibile
    TrackMapLayer = None


class AddestratoreScreen(Screen):
    """Schermata per la modalità addestratore."""

    is_tracking = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'addestratore'

        # Dati
        self.track = None
        self.gps_service = None
        self.my_marker = None
        self.track_layer = None
        self.mapview = None
        self.clock_event = None

        # Costruisci UI
        self.build_ui()

    def build_ui(self):
        """Costruisce l'interfaccia utente."""
        main_layout = BoxLayout(orientation='vertical', spacing=0)

        # Header con controlli
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.35), padding=10, spacing=10)

        # Back button e titolo
        top_bar = BoxLayout(size_hint=(1, 0.2), spacing=10)
        back_btn = Button(
            text='← Indietro',
            size_hint=(0.3, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)

        title = Label(
            text='MODALITÀ ADDESTRATORE',
            font_size='16sp',
            bold=True,
            size_hint=(0.7, 1)
        )

        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        header.add_widget(top_bar)

        # Import percorso
        import_box = BoxLayout(orientation='vertical', size_hint=(1, 0.5), spacing=5)
        import_box.add_widget(Label(
            text='Incolla il percorso da monitorare:',
            size_hint=(1, 0.2),
            font_size='11sp'
        ))

        self.track_input = TextInput(
            multiline=True,
            size_hint=(1, 0.5),
            hint_text='45.4642,9.19,95;45.465,9.191,90;...'
        )
        import_box.add_widget(self.track_input)

        import_btn = Button(
            text='CARICA PERCORSO',
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 0.9, 1)
        )
        import_btn.bind(on_press=self.import_track)
        import_box.add_widget(import_btn)

        header.add_widget(import_box)

        # Info e controlli
        controls = BoxLayout(size_hint=(1, 0.3), spacing=5)

        self.track_info = Label(
            text='Nessun percorso caricato',
            font_size='10sp',
            size_hint=(0.5, 1),
            color=(0.8, 0.8, 0.8, 1)
        )
        controls.add_widget(self.track_info)

        self.tracking_btn = Button(
            text='INIZIA TRACKING',
            size_hint=(0.5, 1),
            background_color=(0.3, 0.7, 0.3, 1),
            disabled=True
        )
        self.tracking_btn.bind(on_press=self.toggle_tracking)
        controls.add_widget(self.tracking_btn)

        header.add_widget(controls)

        main_layout.add_widget(header)

        # Mappa o placeholder
        if MAPVIEW_AVAILABLE:
            self.mapview = MapView(
                zoom=15,
                lat=45.4642,  # Milano default
                lon=9.1900,
                size_hint=(1, 0.65)
            )
            main_layout.add_widget(self.mapview)
        else:
            # Placeholder se MapView non disponibile
            self.mapview = None  # Importante: imposta a None se non disponibile
            placeholder = BoxLayout(orientation='vertical', size_hint=(1, 0.65))
            placeholder.add_widget(Label(
                text='[MAPPA]\n\nMapView non disponibile.\nInstalla kivy-garden.mapview\nper visualizzare la mappa.',
                font_size='14sp',
                color=(0.7, 0.7, 0.7, 1)
            ))
            main_layout.add_widget(placeholder)

        self.add_widget(main_layout)

    def on_enter(self):
        """Chiamato quando si entra nella schermata."""
        # Inizializza GPS service
        self.gps_service = get_gps_service(use_mock=not self.is_mobile())

    def on_leave(self):
        """Chiamato quando si esce dalla schermata."""
        # Ferma tracking se attivo
        if self.is_tracking:
            self.stop_tracking()

        # Ferma GPS
        if self.gps_service:
            self.gps_service.stop()

    def import_track(self, instance):
        """Importa e visualizza il percorso sulla mappa."""
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
            self.track_info.text = f'✓ {self.track.get_point_count()} punti'
            self.track_info.color = (0.2, 0.8, 0.2, 1)
            self.tracking_btn.disabled = False

            # Visualizza su mappa
            if MAPVIEW_AVAILABLE and self.mapview:
                self.display_track_on_map()

            # Info
            from app.utils.geo_utils import calculate_track_length
            length = calculate_track_length(self.track)

            self.show_message(
                "Successo",
                f"Percorso caricato!\n\n"
                f"Punti: {self.track.get_point_count()}\n"
                f"Lunghezza: {int(length)} metri"
            )

        except Exception as e:
            self.show_message("Errore", f"Errore importazione: {str(e)}")
            self.track = None

    def display_track_on_map(self):
        """Visualizza il percorso sulla mappa."""
        if not self.track or not MAPVIEW_AVAILABLE or not self.mapview or TrackMapLayer is None:
            return

        # Rimuovi layer precedente se esiste
        if self.track_layer:
            self.mapview.remove_layer(self.track_layer)

        # Crea nuovo layer per il percorso
        self.track_layer = TrackMapLayer(track=self.track)
        self.mapview.add_layer(self.track_layer)

        # Centra la mappa sul percorso
        center = self.track.get_center()
        if center:
            self.mapview.center_on(center[0], center[1])

        # Aggiungi marker per inizio e fine
        first_point = self.track.get_first_point()
        last_point = self.track.get_last_point()

        if first_point:
            start_marker = MapMarker(
                lat=first_point.latitude,
                lon=first_point.longitude,
                source='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='  # Trasparente
            )
            # TODO: Usare icona verde per inizio
            self.mapview.add_marker(start_marker)

        if last_point and last_point != first_point:
            end_marker = MapMarker(
                lat=last_point.latitude,
                lon=last_point.longitude
            )
            # TODO: Usare icona rossa per fine
            self.mapview.add_marker(end_marker)

        # Ridisegna quando la mappa viene spostata/zoomata
        self.mapview.bind(on_touch_up=self.on_map_touch)

    def on_map_touch(self, instance, touch):
        """Ridisegna il percorso quando la mappa viene toccata."""
        if self.track_layer:
            Clock.schedule_once(lambda dt: self.track_layer.reposition(), 0.1)

    def toggle_tracking(self, instance):
        """Avvia o ferma il tracking della posizione."""
        if self.is_tracking:
            self.stop_tracking()
        else:
            self.start_tracking()

    def start_tracking(self):
        """Avvia il tracking della posizione live."""
        if not self.track:
            self.show_message("Errore", "Carica prima un percorso!")
            return

        self.is_tracking = True

        # Avvia GPS
        self.gps_service.start(
            on_location=self.on_gps_location,
            on_status=self.on_gps_status
        )

        # Aggiorna UI
        self.tracking_btn.text = 'FERMA TRACKING'
        self.tracking_btn.background_color = (0.9, 0.2, 0.2, 1)
        self.track_input.disabled = True

        print("Tracking avviato")

    def stop_tracking(self):
        """Ferma il tracking della posizione."""
        self.is_tracking = False

        # Ferma GPS
        if self.gps_service:
            self.gps_service.stop()

        # Rimuovi marker posizione
        if self.my_marker and MAPVIEW_AVAILABLE and self.mapview:
            self.mapview.remove_marker(self.my_marker)
            self.my_marker = None

        # Aggiorna UI
        self.tracking_btn.text = 'INIZIA TRACKING'
        self.tracking_btn.background_color = (0.3, 0.7, 0.3, 1)
        self.track_input.disabled = False

        print("Tracking fermato")

    def on_gps_location(self, lat, lon, altitude, accuracy, speed):
        """Callback per nuove posizioni GPS."""
        if not MAPVIEW_AVAILABLE or not self.mapview:
            print(f"Posizione: {lat:.6f}, {lon:.6f}")
            return

        # Aggiorna o crea marker posizione
        if self.my_marker:
            self.my_marker.lat = lat
            self.my_marker.lon = lon
        else:
            self.my_marker = MapMarker(lat=lat, lon=lon)
            # TODO: Usare icona blu per posizione addestratore
            self.mapview.add_marker(self.my_marker)

        # Opzionalmente centra la mappa sulla posizione
        # self.mapview.center_on(lat, lon)

    def on_gps_status(self, status_type, message):
        """Callback per stato GPS."""
        print(f"GPS Status: {status_type} - {message}")

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
