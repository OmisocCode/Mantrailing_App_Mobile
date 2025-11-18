"""
Utilità geospaziali per l'app Mantrailing Training.
Fornisce funzioni per calcolare distanze, punti più vicini, ecc.
"""

import math
from typing import List, Tuple, Optional
from app.models.track import GPSPoint, Track


# Raggio medio della Terra in metri
EARTH_RADIUS_METERS = 6371000


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcola la distanza tra due punti GPS usando la formula di Haversine.

    Args:
        lat1: Latitudine del primo punto in gradi decimali
        lon1: Longitudine del primo punto in gradi decimali
        lat2: Latitudine del secondo punto in gradi decimali
        lon2: Longitudine del secondo punto in gradi decimali

    Returns:
        Distanza in metri tra i due punti
    """
    # Converti gradi in radianti
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differenze
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Formula di Haversine
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    # Distanza in metri
    distance = EARTH_RADIUS_METERS * c

    return distance


def distance_point_to_point(point1: GPSPoint, point2: GPSPoint) -> float:
    """
    Calcola la distanza tra due GPSPoint.

    Args:
        point1: Primo punto GPS
        point2: Secondo punto GPS

    Returns:
        Distanza in metri tra i due punti
    """
    return haversine_distance(
        point1.latitude, point1.longitude,
        point2.latitude, point2.longitude
    )


def distance_point_to_segment(point: Tuple[float, float],
                               segment_start: Tuple[float, float],
                               segment_end: Tuple[float, float]) -> float:
    """
    Calcola la distanza minima tra un punto e un segmento di linea.

    Questo metodo proietta il punto sul segmento e calcola la distanza
    più breve possibile.

    Args:
        point: Tupla (lat, lon) del punto
        segment_start: Tupla (lat, lon) dell'inizio del segmento
        segment_end: Tupla (lat, lon) della fine del segmento

    Returns:
        Distanza minima in metri
    """
    px, py = point[0], point[1]
    x1, y1 = segment_start[0], segment_start[1]
    x2, y2 = segment_end[0], segment_end[1]

    # Lunghezza al quadrato del segmento
    segment_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

    # Se il segmento è un punto, calcola la distanza diretta
    if segment_length_sq == 0:
        return haversine_distance(px, py, x1, y1)

    # Parametro t per la proiezione del punto sul segmento
    # t = 0 -> inizio del segmento
    # t = 1 -> fine del segmento
    # 0 < t < 1 -> punto sul segmento
    t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / segment_length_sq))

    # Coordinate del punto proiettato sul segmento
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)

    # Distanza tra il punto e la sua proiezione sul segmento
    return haversine_distance(px, py, proj_x, proj_y)


def distance_point_to_track(lat: float, lon: float, track: Track) -> Optional[float]:
    """
    Calcola la distanza minima tra un punto e un percorso.

    Questo metodo trova il segmento del percorso più vicino al punto
    e calcola la distanza minima.

    Args:
        lat: Latitudine del punto
        lon: Longitudine del punto
        track: Percorso GPS

    Returns:
        Distanza minima in metri o None se il percorso è vuoto
    """
    if track.is_empty() or track.get_point_count() < 2:
        return None

    point = (lat, lon)
    min_distance = float('inf')

    # Itera su tutti i segmenti del percorso
    for i in range(len(track.points) - 1):
        p1 = track.points[i]
        p2 = track.points[i + 1]

        segment_start = (p1.latitude, p1.longitude)
        segment_end = (p2.latitude, p2.longitude)

        distance = distance_point_to_segment(point, segment_start, segment_end)
        min_distance = min(min_distance, distance)

    return min_distance if min_distance != float('inf') else None


def find_closest_point_on_track(lat: float, lon: float, track: Track) -> Optional[Tuple[GPSPoint, int]]:
    """
    Trova il punto del percorso più vicino a una posizione data.

    Args:
        lat: Latitudine della posizione
        lon: Longitudine della posizione
        track: Percorso GPS

    Returns:
        Tupla (GPSPoint più vicino, indice nel percorso) o None se il percorso è vuoto
    """
    if track.is_empty():
        return None

    min_distance = float('inf')
    closest_point = None
    closest_index = -1

    for i, point in enumerate(track.points):
        distance = haversine_distance(lat, lon, point.latitude, point.longitude)
        if distance < min_distance:
            min_distance = distance
            closest_point = point
            closest_index = i

    return (closest_point, closest_index) if closest_point else None


def calculate_track_length(track: Track) -> float:
    """
    Calcola la lunghezza totale del percorso.

    Args:
        track: Percorso GPS

    Returns:
        Lunghezza totale in metri
    """
    if track.get_point_count() < 2:
        return 0.0

    total_length = 0.0

    for i in range(len(track.points) - 1):
        p1 = track.points[i]
        p2 = track.points[i + 1]
        total_length += distance_point_to_point(p1, p2)

    return total_length


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcola la direzione (bearing) da un punto all'altro.

    Args:
        lat1: Latitudine del punto di partenza
        lon1: Longitudine del punto di partenza
        lat2: Latitudine del punto di arrivo
        lon2: Longitudine del punto di arrivo

    Returns:
        Direzione in gradi (0-360) dove 0 = Nord, 90 = Est, 180 = Sud, 270 = Ovest
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon_rad = math.radians(lon2 - lon1)

    x = math.sin(dlon_rad) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)

    # Normalizza a 0-360
    return (bearing_deg + 360) % 360


def interpolate_points(point1: GPSPoint, point2: GPSPoint, num_points: int) -> List[GPSPoint]:
    """
    Interpola punti tra due GPSPoint.

    Args:
        point1: Primo punto
        point2: Secondo punto
        num_points: Numero di punti da interpolare (esclusi gli estremi)

    Returns:
        Lista di GPSPoint interpolati
    """
    if num_points <= 0:
        return []

    interpolated = []

    for i in range(1, num_points + 1):
        t = i / (num_points + 1)  # Parametro di interpolazione (0 < t < 1)

        # Interpolazione lineare delle coordinate
        lat = point1.latitude + t * (point2.latitude - point1.latitude)
        lon = point1.longitude + t * (point2.longitude - point1.longitude)
        quality = int(point1.quality + t * (point2.quality - point1.quality))

        interpolated.append(GPSPoint(latitude=lat, longitude=lon, quality=quality))

    return interpolated


def smooth_track(track: Track, window_size: int = 3) -> Track:
    """
    Applica uno smoothing al percorso usando una media mobile.

    Args:
        track: Percorso GPS da smoothare
        window_size: Dimensione della finestra per la media mobile

    Returns:
        Nuovo percorso smoothato
    """
    if track.get_point_count() < window_size:
        return track

    smoothed_track = Track(
        name=track.name + " (smoothed)",
        description=track.description
    )

    half_window = window_size // 2

    for i in range(len(track.points)):
        start_idx = max(0, i - half_window)
        end_idx = min(len(track.points), i + half_window + 1)

        # Calcola la media delle coordinate
        avg_lat = sum(p.latitude for p in track.points[start_idx:end_idx]) / (end_idx - start_idx)
        avg_lon = sum(p.longitude for p in track.points[start_idx:end_idx]) / (end_idx - start_idx)
        avg_quality = int(sum(p.quality for p in track.points[start_idx:end_idx]) / (end_idx - start_idx))

        smoothed_track.add_point(avg_lat, avg_lon, avg_quality)

    return smoothed_track


def simplify_track(track: Track, tolerance_meters: float = 10.0) -> Track:
    """
    Semplifica un percorso rimuovendo punti ridondanti.
    Usa l'algoritmo Douglas-Peucker.

    Args:
        track: Percorso GPS da semplificare
        tolerance_meters: Tolleranza massima in metri

    Returns:
        Nuovo percorso semplificato
    """
    if track.get_point_count() < 3:
        return track

    def douglas_peucker(points: List[GPSPoint], tolerance: float) -> List[GPSPoint]:
        """Algoritmo Douglas-Peucker ricorsivo."""
        if len(points) < 3:
            return points

        # Trova il punto più lontano dalla linea tra primo e ultimo punto
        start = (points[0].latitude, points[0].longitude)
        end = (points[-1].latitude, points[-1].longitude)

        max_distance = 0
        max_index = 0

        for i in range(1, len(points) - 1):
            point = (points[i].latitude, points[i].longitude)
            distance = distance_point_to_segment(point, start, end)

            if distance > max_distance:
                max_distance = distance
                max_index = i

        # Se il punto più lontano è oltre la tolleranza, dividi e ricorri
        if max_distance > tolerance:
            left = douglas_peucker(points[:max_index + 1], tolerance)
            right = douglas_peucker(points[max_index:], tolerance)
            return left[:-1] + right
        else:
            return [points[0], points[-1]]

    simplified_points = douglas_peucker(track.points, tolerance_meters)

    simplified_track = Track(
        name=track.name + " (simplified)",
        description=track.description
    )

    for point in simplified_points:
        simplified_track.add_gps_point(point)

    return simplified_track


def is_point_in_bounds(lat: float, lon: float, bounds: Tuple[float, float, float, float]) -> bool:
    """
    Verifica se un punto è all'interno di un rettangolo geografico.

    Args:
        lat: Latitudine del punto
        lon: Longitudine del punto
        bounds: Tupla (min_lat, min_lon, max_lat, max_lon)

    Returns:
        True se il punto è all'interno dei bounds
    """
    min_lat, min_lon, max_lat, max_lon = bounds
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def expand_bounds(bounds: Tuple[float, float, float, float],
                  margin_percent: float = 10.0) -> Tuple[float, float, float, float]:
    """
    Espande i bounds di una percentuale.

    Args:
        bounds: Tupla (min_lat, min_lon, max_lat, max_lon)
        margin_percent: Percentuale di espansione (default 10%)

    Returns:
        Nuova tupla di bounds espansa
    """
    min_lat, min_lon, max_lat, max_lon = bounds

    lat_margin = (max_lat - min_lat) * margin_percent / 100
    lon_margin = (max_lon - min_lon) * margin_percent / 100

    return (
        min_lat - lat_margin,
        min_lon - lon_margin,
        max_lat + lat_margin,
        max_lon + lon_margin
    )
