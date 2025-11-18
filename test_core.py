"""
Test script per verificare il funzionamento dei componenti core dell'app.
Esegui questo file per testare database, modelli, GPS service e utilità geospaziali.
"""

import sys
import os

# Aggiungi la directory corrente al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.track import Track, GPSPoint
from app.models.database import DatabaseManager
from app.services.gps_service import MockGPSService
from app.utils.geo_utils import (
    haversine_distance,
    distance_point_to_track,
    calculate_track_length,
    find_closest_point_on_track
)


def test_gps_point():
    """Test GPSPoint model."""
    print("\n=== Test GPSPoint ===")

    # Crea un punto GPS
    point = GPSPoint(latitude=45.4642, longitude=9.1900, quality=95)
    print(f"Punto creato: {point}")

    # Test conversione a stringa
    point_str = point.to_string()
    print(f"Stringa: {point_str}")

    # Test creazione da stringa
    point2 = GPSPoint.from_string(point_str)
    print(f"Punto da stringa: {point2}")

    assert point.latitude == point2.latitude
    assert point.longitude == point2.longitude
    assert point.quality == point2.quality

    print("✓ GPSPoint OK")


def test_track():
    """Test Track model."""
    print("\n=== Test Track ===")

    # Crea un percorso
    track = Track(name="Test Track", description="Percorso di test")

    # Aggiungi alcuni punti (simulazione percorso da Milano verso nord)
    track.add_point(45.4642, 9.1900, 95)  # Milano centro
    track.add_point(45.4650, 9.1910, 90)
    track.add_point(45.4660, 9.1920, 85)
    track.add_point(45.4670, 9.1930, 88)

    print(f"Percorso: {track}")
    print(f"Numero punti: {track.get_point_count()}")
    print(f"Centro: {track.get_center()}")
    print(f"Bounds: {track.get_bounds()}")
    print(f"Qualità media: {track.get_average_quality():.2f}")

    # Test serializzazione
    track_str = track.to_string()
    print(f"Serializzato (primi 100 char): {track_str[:100]}...")

    # Test deserializzazione
    track2 = Track.from_string(track_str)
    print(f"Deserializzato: {track2}")

    assert track.get_point_count() == track2.get_point_count()

    # Test validazione
    is_valid, error = track.validate()
    print(f"Validazione: {is_valid} - {error}")

    assert is_valid

    print("✓ Track OK")


def test_database():
    """Test Database operations."""
    print("\n=== Test Database ===")

    # Crea database in memoria per test
    db = DatabaseManager(":memory:")

    # Crea un percorso di test
    track_data = "45.4642,9.1900,95;45.4650,9.1910,90;45.4660,9.1920,85"

    # Salva il percorso
    track_id = db.save_track(
        name="Percorso Test",
        track_data=track_data,
        description="Test database",
        duration_seconds=300
    )
    print(f"Percorso salvato con ID: {track_id}")

    # Recupera il percorso
    track = db.get_track(track_id)
    print(f"Percorso recuperato: {track['name']}")
    print(f"Punti: {track['total_points']}")

    # Lista tutti i percorsi
    all_tracks = db.get_all_tracks()
    print(f"Totale percorsi nel DB: {len(all_tracks)}")

    # Test settings
    db.set_setting("sampling_rate", "5")
    sampling_rate = db.get_setting("sampling_rate")
    print(f"Setting recuperato: sampling_rate = {sampling_rate}")

    assert sampling_rate == "5"

    # Statistiche
    stats = db.get_stats()
    print(f"Statistiche DB: {stats}")

    db.close()

    print("✓ Database OK")


def test_geo_utils():
    """Test utilità geospaziali."""
    print("\n=== Test Geo Utils ===")

    # Test distanza Haversine
    # Milano centro -> Milano Nord (circa 1 km)
    lat1, lon1 = 45.4642, 9.1900
    lat2, lon2 = 45.4732, 9.1900

    distance = haversine_distance(lat1, lon1, lat2, lon2)
    print(f"Distanza Milano centro -> Milano Nord: {distance:.2f} metri")

    # Dovrebbe essere circa 1 km
    assert 900 < distance < 1100

    # Test distanza punto-percorso
    track = Track()
    track.add_point(45.4642, 9.1900, 95)
    track.add_point(45.4650, 9.1900, 90)
    track.add_point(45.4660, 9.1900, 85)

    # Punto vicino al percorso
    dist_to_track = distance_point_to_track(45.4650, 9.1905, track)
    print(f"Distanza punto-percorso: {dist_to_track:.2f} metri")

    # Test lunghezza percorso
    track_length = calculate_track_length(track)
    print(f"Lunghezza percorso: {track_length:.2f} metri")

    # Test trova punto più vicino
    closest = find_closest_point_on_track(45.4650, 9.1905, track)
    if closest:
        point, index = closest
        print(f"Punto più vicino: indice {index}, {point}")

    print("✓ Geo Utils OK")


def test_gps_service():
    """Test GPS service (mock)."""
    print("\n=== Test GPS Service ===")

    # Crea mock GPS service
    gps = MockGPSService(start_lat=45.4642, start_lon=9.1900)

    # Callback per le posizioni
    positions = []

    def on_location(lat, lon, altitude, accuracy, speed):
        positions.append((lat, lon, accuracy))
        print(f"Posizione ricevuta: lat={lat:.6f}, lon={lon:.6f}, accuracy={accuracy:.2f}m")

    def on_status(status_type, message):
        print(f"Stato GPS: {status_type} - {message}")

    # Avvia il GPS
    gps.start(on_location=on_location, on_status=on_status)

    # Simula alcune posizioni
    for i in range(3):
        gps.update_position(45.4642 + i * 0.0001, 9.1900 + i * 0.0001, quality=95)

    # Verifica qualità GPS
    quality = gps.get_gps_quality(accuracy=8.0)
    print(f"Qualità GPS per accuracy=8m: {quality}/100")

    # Ferma il GPS
    gps.stop()

    print(f"Posizioni raccolte: {len(positions)}")
    assert len(positions) > 0

    print("✓ GPS Service OK")


def test_integration():
    """Test integrazione componenti."""
    print("\n=== Test Integrazione ===")

    # Crea un percorso completo
    track = Track(name="Percorso Integrazione", description="Test completo")

    # Simula registrazione con GPS mock
    gps = MockGPSService(start_lat=45.4642, start_lon=9.1900)

    def on_location(lat, lon, altitude, accuracy, speed):
        quality = gps.get_gps_quality(accuracy)
        track.add_point(lat, lon, quality)

    gps.start(on_location=on_location)

    # Simula 5 punti GPS
    for i in range(5):
        gps.update_position(
            lat=45.4642 + i * 0.0001,
            lon=9.1900 + i * 0.0001,
            quality=95
        )

    gps.stop()

    print(f"Percorso creato con {track.get_point_count()} punti")

    # Salva nel database
    db = DatabaseManager(":memory:")
    track_data = track.to_string()
    track_id = db.save_track(
        name=track.name,
        track_data=track_data,
        description=track.description,
        duration_seconds=60
    )

    print(f"Percorso salvato nel database con ID: {track_id}")

    # Recupera e verifica
    saved_track_data = db.get_track(track_id)
    recovered_track = Track.from_string(saved_track_data['track_data'])

    print(f"Percorso recuperato: {recovered_track.get_point_count()} punti")

    assert recovered_track.get_point_count() == track.get_point_count()

    # Calcola lunghezza
    length = calculate_track_length(recovered_track)
    print(f"Lunghezza totale percorso: {length:.2f} metri")

    db.close()

    print("✓ Integrazione OK")


def main():
    """Esegue tutti i test."""
    print("="*60)
    print("TEST COMPONENTI CORE - MANTRAILING TRAINING APP")
    print("="*60)

    try:
        test_gps_point()
        test_track()
        test_database()
        test_geo_utils()
        test_gps_service()
        test_integration()

        print("\n" + "="*60)
        print("✓ TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("="*60)

        return 0

    except AssertionError as e:
        print(f"\n✗ Test fallito: {e}")
        import traceback
        traceback.print_exc()
        return 1

    except Exception as e:
        print(f"\n✗ Errore durante i test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
