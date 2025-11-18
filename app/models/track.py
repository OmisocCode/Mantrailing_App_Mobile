"""
Modello Track per la gestione dei percorsi GPS.
Rappresenta un percorso registrato con coordinate GPS e metadati.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime


@dataclass
class GPSPoint:
    """Rappresenta un singolo punto GPS."""
    latitude: float
    longitude: float
    quality: int  # Valore da 0 a 100
    timestamp: Optional[datetime] = None

    def to_tuple(self) -> Tuple[float, float, int]:
        """Converte il punto in tupla (lat, lon, quality)."""
        return (self.latitude, self.longitude, self.quality)

    @staticmethod
    def from_tuple(data: Tuple[float, float, int]) -> 'GPSPoint':
        """Crea un GPSPoint da una tupla (lat, lon, quality)."""
        return GPSPoint(latitude=data[0], longitude=data[1], quality=data[2])

    @staticmethod
    def from_string(point_str: str) -> 'GPSPoint':
        """
        Crea un GPSPoint da una stringa formato: "lat,lon,quality"

        Args:
            point_str: Stringa con formato "45.4642,9.1900,95"

        Returns:
            GPSPoint creato dalla stringa

        Raises:
            ValueError: Se il formato della stringa non è valido
        """
        try:
            parts = point_str.split(',')
            if len(parts) != 3:
                raise ValueError(f"Invalid point format: {point_str}")

            lat = float(parts[0])
            lon = float(parts[1])
            quality = int(parts[2])

            # Validazione coordinate
            if not (-90 <= lat <= 90):
                raise ValueError(f"Invalid latitude: {lat}")
            if not (-180 <= lon <= 180):
                raise ValueError(f"Invalid longitude: {lon}")
            if not (0 <= quality <= 100):
                raise ValueError(f"Invalid quality: {quality}")

            return GPSPoint(latitude=lat, longitude=lon, quality=quality)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid GPS point string '{point_str}': {e}")

    def to_string(self) -> str:
        """Converte il punto in stringa formato: "lat,lon,quality"."""
        return f"{self.latitude},{self.longitude},{self.quality}"

    def __str__(self) -> str:
        return f"GPSPoint(lat={self.latitude:.6f}, lon={self.longitude:.6f}, q={self.quality})"


@dataclass
class Track:
    """Rappresenta un percorso GPS completo."""
    points: List[GPSPoint] = field(default_factory=list)
    name: str = ""
    description: str = ""
    created_at: Optional[datetime] = None
    duration_seconds: int = 0
    track_id: Optional[int] = None

    def __post_init__(self):
        """Inizializza i valori di default dopo la creazione."""
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_point(self, latitude: float, longitude: float, quality: int):
        """
        Aggiunge un punto al percorso.

        Args:
            latitude: Latitudine del punto
            longitude: Longitudine del punto
            quality: Qualità del segnale GPS (0-100)
        """
        point = GPSPoint(latitude=latitude, longitude=longitude, quality=quality)
        self.points.append(point)

    def add_gps_point(self, point: GPSPoint):
        """
        Aggiunge un GPSPoint al percorso.

        Args:
            point: Oggetto GPSPoint da aggiungere
        """
        self.points.append(point)

    def get_point_count(self) -> int:
        """Restituisce il numero di punti nel percorso."""
        return len(self.points)

    def is_empty(self) -> bool:
        """Verifica se il percorso è vuoto."""
        return len(self.points) == 0

    def clear(self):
        """Rimuove tutti i punti dal percorso."""
        self.points.clear()

    def get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """
        Calcola i limiti geografici del percorso.

        Returns:
            Tupla (min_lat, min_lon, max_lat, max_lon) o None se vuoto
        """
        if self.is_empty():
            return None

        lats = [p.latitude for p in self.points]
        lons = [p.longitude for p in self.points]

        return (min(lats), min(lons), max(lats), max(lons))

    def get_center(self) -> Optional[Tuple[float, float]]:
        """
        Calcola il centro geografico del percorso.

        Returns:
            Tupla (lat, lon) del centro o None se vuoto
        """
        if self.is_empty():
            return None

        lats = [p.latitude for p in self.points]
        lons = [p.longitude for p in self.points]

        center_lat = (min(lats) + max(lats)) / 2
        center_lon = (min(lons) + max(lons)) / 2

        return (center_lat, center_lon)

    def get_average_quality(self) -> float:
        """
        Calcola la qualità media del segnale GPS.

        Returns:
            Qualità media (0-100) o 0 se vuoto
        """
        if self.is_empty():
            return 0.0

        total_quality = sum(p.quality for p in self.points)
        return total_quality / len(self.points)

    # ============================================================================
    # SERIALIZZAZIONE / DESERIALIZZAZIONE
    # ============================================================================

    def to_string(self) -> str:
        """
        Converte il percorso in stringa formato CSV.
        Formato: "lat1,lon1,quality1;lat2,lon2,quality2;...;latN,lonN,qualityN"

        Returns:
            Stringa con tutti i punti del percorso
        """
        if self.is_empty():
            return ""

        point_strings = [p.to_string() for p in self.points]
        return ";".join(point_strings)

    @staticmethod
    def from_string(track_str: str) -> 'Track':
        """
        Crea un Track da una stringa CSV.

        Args:
            track_str: Stringa formato "lat,lon,quality;lat,lon,quality;..."

        Returns:
            Track creato dalla stringa

        Raises:
            ValueError: Se il formato della stringa non è valido
        """
        track = Track()

        if not track_str or track_str.strip() == "":
            return track

        # Split per i punti separati da ";"
        point_strings = track_str.strip().split(';')

        for point_str in point_strings:
            point_str = point_str.strip()
            if point_str:  # Ignora stringhe vuote
                try:
                    point = GPSPoint.from_string(point_str)
                    track.add_gps_point(point)
                except ValueError as e:
                    # Log l'errore ma continua con gli altri punti
                    print(f"Warning: Skipping invalid point: {e}")

        return track

    def validate(self) -> Tuple[bool, str]:
        """
        Valida il percorso.

        Returns:
            Tupla (is_valid, error_message)
        """
        if self.is_empty():
            return (False, "Track is empty")

        if len(self.points) < 2:
            return (False, "Track must have at least 2 points")

        # Verifica che tutti i punti abbiano coordinate valide
        for i, point in enumerate(self.points):
            if not (-90 <= point.latitude <= 90):
                return (False, f"Invalid latitude at point {i}: {point.latitude}")
            if not (-180 <= point.longitude <= 180):
                return (False, f"Invalid longitude at point {i}: {point.longitude}")
            if not (0 <= point.quality <= 100):
                return (False, f"Invalid quality at point {i}: {point.quality}")

        return (True, "")

    # ============================================================================
    # METODI DI CONVENIENZA
    # ============================================================================

    def get_first_point(self) -> Optional[GPSPoint]:
        """Restituisce il primo punto del percorso."""
        return self.points[0] if self.points else None

    def get_last_point(self) -> Optional[GPSPoint]:
        """Restituisce l'ultimo punto del percorso."""
        return self.points[-1] if self.points else None

    def get_point_at(self, index: int) -> Optional[GPSPoint]:
        """
        Restituisce il punto all'indice specificato.

        Args:
            index: Indice del punto (0-based)

        Returns:
            GPSPoint o None se l'indice non è valido
        """
        if 0 <= index < len(self.points):
            return self.points[index]
        return None

    def get_quality_color(self, quality: int) -> str:
        """
        Restituisce il colore associato alla qualità GPS.

        Args:
            quality: Valore della qualità (0-100)

        Returns:
            Nome del colore: "blue", "green", "yellow", "orange", "red"
        """
        if quality >= 90:
            return "blue"  # Ottimo
        elif quality >= 70:
            return "green"  # Buono
        elif quality >= 50:
            return "yellow"  # Discreto
        elif quality >= 30:
            return "orange"  # Scarso
        else:
            return "red"  # Molto scarso

    def __str__(self) -> str:
        """Rappresentazione stringa del percorso."""
        if self.name:
            return f"Track '{self.name}' ({len(self.points)} points)"
        return f"Track ({len(self.points)} points)"

    def __repr__(self) -> str:
        return f"Track(name='{self.name}', points={len(self.points)}, id={self.track_id})"
