"""
Widget personalizzato per visualizzare il percorso su griglia cartesiana.
Alternativa offline a MapView, più semplice e performante.
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.properties import ObjectProperty
from kivy.metrics import dp

from app.models.track import Track


class TrackGridView(Widget):
    """
    Visualizza un percorso GPS su una griglia cartesiana.
    Sfondo nero, griglia verde, percorso colorato per qualità GPS.
    """

    track = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.grid_size_meters = 100  # Dimensione quadrato griglia in metri

        self.bind(size=self.redraw, pos=self.redraw)

    def set_track(self, track: Track):
        """Imposta il percorso da visualizzare."""
        self.track = track
        self.calculate_scale()
        self.redraw()

    def calculate_scale(self):
        """Calcola scala e offset per centrare il percorso."""
        if not self.track or self.track.is_empty():
            return

        # Converti coordinate GPS in metri relativi
        points_meters = self._gps_to_meters(self.track.points)

        if not points_meters:
            return

        # Trova bounds in metri
        xs = [p[0] for p in points_meters]
        ys = [p[1] for p in points_meters]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Dimensioni percorso in metri
        width_meters = max_x - min_x
        height_meters = max_y - min_y

        # Aggiungi margine (20% del percorso)
        margin = max(width_meters, height_meters) * 0.2
        width_meters += margin * 2
        height_meters += margin * 2

        # Calcola scala per adattare a schermo (mantieni aspect ratio)
        if width_meters > 0 and height_meters > 0:
            scale_x = self.width / width_meters if width_meters > 0 else 1
            scale_y = self.height / height_meters if height_meters > 0 else 1
            self.scale = min(scale_x, scale_y)
        else:
            self.scale = 1.0

        # Calcola offset per centrare
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        self.offset_x = self.width / 2 - center_x * self.scale
        self.offset_y = self.height / 2 - center_y * self.scale

    def _gps_to_meters(self, gps_points):
        """
        Converte coordinate GPS in metri relativi al primo punto.

        Args:
            gps_points: Lista di GPSPoint

        Returns:
            Lista di tuple (x_metri, y_metri)
        """
        if not gps_points:
            return []

        # Usa primo punto come origine
        origin = gps_points[0]

        result = []
        for point in gps_points:
            # Approssimazione: 1 grado lat = ~111km, 1 grado lon = ~111km * cos(lat)
            import math

            delta_lat = point.latitude - origin.latitude
            delta_lon = point.longitude - origin.longitude

            # Converti in metri
            meters_per_degree_lat = 111000
            meters_per_degree_lon = 111000 * math.cos(math.radians(origin.latitude))

            x_meters = delta_lon * meters_per_degree_lon
            y_meters = delta_lat * meters_per_degree_lat

            result.append((x_meters, y_meters))

        return result

    def _meters_to_screen(self, x_meters, y_meters):
        """Converte coordinate metri in coordinate schermo."""
        screen_x = x_meters * self.scale + self.offset_x
        screen_y = y_meters * self.scale + self.offset_y
        return screen_x, screen_y

    def redraw(self, *args):
        """Ridisegna la griglia e il percorso."""
        self.canvas.clear()

        with self.canvas:
            # Sfondo nero
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Disegna griglia
            self._draw_grid()

            # Disegna percorso
            if self.track and not self.track.is_empty():
                self._draw_track()

            # Disegna posizione live (se presente)
            self._draw_live_position()

    def _draw_grid(self):
        """Disegna la griglia con linee verdi."""
        if self.scale <= 0:
            return

        # Dimensione griglia in pixel
        grid_pixel_size = self.grid_size_meters * self.scale

        if grid_pixel_size < 10:  # Troppo piccola, non disegnare
            return

        # Linee verticali
        Color(0, 0.3, 0, 1)  # Verde scuro
        x = self.offset_x % grid_pixel_size
        while x < self.width:
            Line(points=[self.x + x, self.y, self.x + x, self.y + self.height], width=0.5)
            x += grid_pixel_size

        # Linee orizzontali
        y = self.offset_y % grid_pixel_size
        while y < self.height:
            Line(points=[self.x, self.y + y, self.x + self.width, self.y + y], width=0.5)
            y += grid_pixel_size

        # Assi centrali più evidenti
        Color(0, 0.5, 0, 1)  # Verde medio

        # Asse X (orizzontale al centro)
        center_y = self.y + self.offset_y
        if 0 <= center_y - self.y <= self.height:
            Line(points=[self.x, center_y, self.x + self.width, center_y], width=1.5)

        # Asse Y (verticale al centro)
        center_x = self.x + self.offset_x
        if 0 <= center_x - self.x <= self.width:
            Line(points=[center_x, self.y, center_x, self.y + self.height], width=1.5)

        # Label scala (opzionale - mostra dimensione griglia)
        self._draw_scale_label()

    def _draw_scale_label(self):
        """Disegna label con la scala della griglia."""
        # Testo in angolo in alto a destra
        Color(0, 1, 0, 0.7)
        # Nota: Per semplicità non disegniamo testo qui,
        # ma potrebbe essere aggiunto con Label widget sovrapposto

    def _draw_track(self):
        """Disegna il percorso con colori qualità GPS."""
        points_meters = self._gps_to_meters(self.track.points)

        if len(points_meters) < 2:
            return

        # Disegna linee tra i punti
        for i in range(len(points_meters) - 1):
            p1 = points_meters[i]
            p2 = points_meters[i + 1]

            # Converti in coordinate schermo
            x1, y1 = self._meters_to_screen(p1[0], p1[1])
            x2, y2 = self._meters_to_screen(p2[0], p2[1])

            # Colore in base alla qualità GPS media
            quality1 = self.track.points[i].quality
            quality2 = self.track.points[i + 1].quality
            avg_quality = (quality1 + quality2) / 2

            color = self._get_quality_color(avg_quality)
            Color(*color)
            Line(points=[x1, y1, x2, y2], width=2)

        # Disegna punti campionati
        Color(1, 1, 1, 0.8)  # Bianco semi-trasparente
        for i, pm in enumerate(points_meters):
            x, y = self._meters_to_screen(pm[0], pm[1])
            Ellipse(pos=(x - 3, y - 3), size=(6, 6))

        # Evidenzia inizio (verde) e fine (rosso)
        if points_meters:
            # Inizio
            x, y = self._meters_to_screen(points_meters[0][0], points_meters[0][1])
            Color(0, 1, 0, 1)  # Verde
            Ellipse(pos=(x - 6, y - 6), size=(12, 12))

            # Fine
            x, y = self._meters_to_screen(points_meters[-1][0], points_meters[-1][1])
            Color(1, 0, 0, 1)  # Rosso
            Ellipse(pos=(x - 6, y - 6), size=(12, 12))

    def _get_quality_color(self, quality):
        """
        Restituisce colore RGBA in base alla qualità GPS.

        Args:
            quality: Qualità GPS (0-100)

        Returns:
            Tupla RGBA
        """
        if quality >= 90:
            return (0, 0.5, 1, 1)  # Azzurro
        elif quality >= 70:
            return (0, 1, 0, 1)  # Verde
        elif quality >= 50:
            return (1, 1, 0, 1)  # Giallo
        elif quality >= 30:
            return (1, 0.5, 0, 1)  # Arancione
        else:
            return (1, 0, 0, 1)  # Rosso

    def update_live_position(self, lat, lon):
        """
        Aggiorna la posizione live dell'addestratore.

        Args:
            lat: Latitudine corrente
            lon: Longitudine corrente
        """
        if not self.track or self.track.is_empty():
            return

        # Salva posizione corrente
        self.current_lat = lat
        self.current_lon = lon

        # Ridisegna tutto (include la nuova posizione)
        self.redraw()

    def _draw_live_position(self):
        """Disegna la posizione live dell'addestratore."""
        if not hasattr(self, 'current_lat') or not self.track or self.track.is_empty():
            return

        # Converti posizione corrente in metri relativi
        origin = self.track.points[0]
        import math

        delta_lat = self.current_lat - origin.latitude
        delta_lon = self.current_lon - origin.longitude

        meters_per_degree_lat = 111000
        meters_per_degree_lon = 111000 * math.cos(math.radians(origin.latitude))

        x_meters = delta_lon * meters_per_degree_lon
        y_meters = delta_lat * meters_per_degree_lat

        # Converti in coordinate schermo
        x, y = self._meters_to_screen(x_meters, y_meters)

        # Disegna marker posizione corrente (azzurro pulsante)
        Color(0, 0.5, 1, 0.8)  # Azzurro
        Ellipse(pos=(x - 10, y - 10), size=(20, 20))
        Color(1, 1, 1, 1)  # Bianco centro
        Ellipse(pos=(x - 5, y - 5), size=(10, 10))
