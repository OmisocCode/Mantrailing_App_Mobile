"""
Servizio GPS per l'app Mantrailing Training.
Gestisce l'accesso al GPS tramite plyer e fornisce wrapper per le operazioni GPS.
"""

from typing import Optional, Callable, Tuple
import time

try:
    from plyer import gps
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Warning: plyer not available. GPS functionality will be limited.")


class GPSService:
    """Wrapper per l'accesso al GPS cross-platform tramite plyer."""

    def __init__(self):
        """Inizializza il servizio GPS."""
        self.is_running = False
        self.current_location = None
        self.last_error = None
        self.on_location_callback = None
        self.on_status_callback = None

        # Parametri GPS
        self.min_time = 1000  # Tempo minimo tra aggiornamenti in millisecondi
        self.min_distance = 0  # Distanza minima tra aggiornamenti in metri

        # Statistiche
        self.location_updates_count = 0
        self.last_update_time = None

    def configure(self, min_time: int = 1000, min_distance: int = 0):
        """
        Configura i parametri GPS.

        Args:
            min_time: Tempo minimo tra aggiornamenti in millisecondi
            min_distance: Distanza minima tra aggiornamenti in metri
        """
        self.min_time = min_time
        self.min_distance = min_distance

    def start(self, on_location: Callable = None, on_status: Callable = None):
        """
        Avvia il tracciamento GPS.

        Args:
            on_location: Callback chiamata quando si riceve una nuova posizione.
                         Firma: on_location(lat, lon, altitude, accuracy, speed)
            on_status: Callback chiamata quando cambia lo stato GPS.
                       Firma: on_status(status, message)
        """
        if not PLYER_AVAILABLE:
            if on_status:
                on_status('error', 'Plyer not available')
            return False

        try:
            self.on_location_callback = on_location
            self.on_status_callback = on_status

            # Configura i callback per plyer
            gps.configure(
                on_location=self._on_location,
                on_status=self._on_status
            )

            # Avvia il GPS
            gps.start(minTime=self.min_time, minDistance=self.min_distance)
            self.is_running = True

            if on_status:
                on_status('started', 'GPS tracking started')

            return True

        except Exception as e:
            self.last_error = str(e)
            if on_status:
                on_status('error', str(e))
            return False

    def stop(self):
        """Ferma il tracciamento GPS."""
        if not PLYER_AVAILABLE:
            return

        try:
            if self.is_running:
                gps.stop()
                self.is_running = False

                if self.on_status_callback:
                    self.on_status_callback('stopped', 'GPS tracking stopped')

        except Exception as e:
            self.last_error = str(e)
            print(f"Error stopping GPS: {e}")

    def _on_location(self, **kwargs):
        """
        Callback interno chiamato quando si riceve una nuova posizione.

        Args:
            **kwargs: Dizionario con i dati della posizione:
                - lat: latitudine
                - lon: longitudine
                - altitude: altitudine (opzionale)
                - accuracy: accuratezza in metri (opzionale)
                - speed: velocità in m/s (opzionale)
                - bearing: direzione in gradi (opzionale)
        """
        self.current_location = kwargs
        self.location_updates_count += 1
        self.last_update_time = time.time()

        # Chiama il callback esterno se definito
        if self.on_location_callback:
            lat = kwargs.get('lat', 0.0)
            lon = kwargs.get('lon', 0.0)
            altitude = kwargs.get('altitude', 0.0)
            accuracy = kwargs.get('accuracy', 0.0)
            speed = kwargs.get('speed', 0.0)

            self.on_location_callback(lat, lon, altitude, accuracy, speed)

    def _on_status(self, stype, status):
        """
        Callback interno chiamato quando cambia lo stato del GPS.

        Args:
            stype: Tipo di stato ('provider-enabled', 'provider-disabled', etc.)
            status: Messaggio di stato
        """
        if self.on_status_callback:
            self.on_status_callback(stype, status)

    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Ottiene la posizione corrente (ultima conosciuta).

        Returns:
            Tupla (latitudine, longitudine) o None se non disponibile
        """
        if self.current_location:
            lat = self.current_location.get('lat')
            lon = self.current_location.get('lon')
            if lat is not None and lon is not None:
                return (lat, lon)
        return None

    def get_current_accuracy(self) -> Optional[float]:
        """
        Ottiene l'accuratezza GPS corrente.

        Returns:
            Accuratezza in metri o None se non disponibile
        """
        if self.current_location:
            return self.current_location.get('accuracy')
        return None

    def get_gps_quality(self, accuracy: float = None) -> int:
        """
        Calcola la qualità del segnale GPS basata sull'accuratezza.

        Args:
            accuracy: Accuratezza in metri. Se None, usa l'ultima disponibile.

        Returns:
            Qualità GPS da 0 a 100:
            - 100: accuratezza <= 5m (eccellente)
            - 90: accuratezza <= 10m (ottimo)
            - 70: accuratezza <= 20m (buono)
            - 50: accuratezza <= 50m (discreto)
            - 30: accuratezza <= 100m (scarso)
            - 0: accuratezza > 100m o non disponibile (molto scarso)
        """
        if accuracy is None:
            accuracy = self.get_current_accuracy()

        if accuracy is None:
            return 0

        # Converti l'accuratezza in qualità (0-100)
        if accuracy <= 5:
            return 100
        elif accuracy <= 10:
            return 90
        elif accuracy <= 20:
            return 70
        elif accuracy <= 50:
            return 50
        elif accuracy <= 100:
            return 30
        else:
            return max(0, int(30 - (accuracy - 100) / 10))

    def is_gps_available(self) -> bool:
        """
        Verifica se il GPS è disponibile sul dispositivo.

        Returns:
            True se il GPS è disponibile
        """
        return PLYER_AVAILABLE

    def request_permissions(self):
        """
        Richiede i permessi GPS (Android).
        Su Android, i permessi devono essere dichiarati nel manifest e
        richiesti a runtime per Android 6.0+.
        """
        if not PLYER_AVAILABLE:
            return False

        try:
            # Su Android, i permessi vengono gestiti tramite buildozer.spec
            # e richiesti automaticamente da plyer quando necessario
            # Questo metodo è un placeholder per future implementazioni
            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def get_stats(self) -> dict:
        """
        Ottiene statistiche sul servizio GPS.

        Returns:
            Dizionario con le statistiche
        """
        return {
            'is_running': self.is_running,
            'location_updates_count': self.location_updates_count,
            'last_update_time': self.last_update_time,
            'current_location': self.current_location,
            'last_error': self.last_error,
            'plyer_available': PLYER_AVAILABLE
        }

    def __del__(self):
        """Distruttore: ferma il GPS se ancora in esecuzione."""
        if self.is_running:
            self.stop()


# ============================================================================
# MOCK GPS SERVICE (per testing senza GPS reale)
# ============================================================================

class MockGPSService(GPSService):
    """
    Servizio GPS mock per testing.
    Simula dati GPS senza bisogno di un dispositivo reale.
    """

    def __init__(self, start_lat: float = 45.4642, start_lon: float = 9.1900):
        """
        Inizializza il servizio GPS mock.

        Args:
            start_lat: Latitudine iniziale
            start_lon: Longitudine iniziale
        """
        super().__init__()
        self.mock_lat = start_lat
        self.mock_lon = start_lon
        self.mock_quality = 95
        self._mock_running = False

    def start(self, on_location: Callable = None, on_status: Callable = None):
        """Avvia il GPS mock."""
        self.on_location_callback = on_location
        self.on_status_callback = on_status
        self.is_running = True
        self._mock_running = True

        if on_status:
            on_status('started', 'Mock GPS started')

        # Simula prima posizione
        self._simulate_location()

        return True

    def stop(self):
        """Ferma il GPS mock."""
        self.is_running = False
        self._mock_running = False

        if self.on_status_callback:
            self.on_status_callback('stopped', 'Mock GPS stopped')

    def _simulate_location(self):
        """Simula una nuova posizione GPS."""
        if self.on_location_callback:
            # Simula un leggero movimento casuale
            import random
            delta = 0.0001  # Circa 10 metri
            self.mock_lat += random.uniform(-delta, delta)
            self.mock_lon += random.uniform(-delta, delta)
            self.mock_quality = random.randint(80, 100)

            accuracy = random.uniform(5, 15)

            self.on_location_callback(
                self.mock_lat,
                self.mock_lon,
                altitude=100.0,
                accuracy=accuracy,
                speed=1.0
            )

            self.current_location = {
                'lat': self.mock_lat,
                'lon': self.mock_lon,
                'altitude': 100.0,
                'accuracy': accuracy,
                'speed': 1.0
            }

    def update_position(self, lat: float, lon: float, quality: int = 95):
        """
        Aggiorna manualmente la posizione mock.

        Args:
            lat: Nuova latitudine
            lon: Nuova longitudine
            quality: Qualità GPS (0-100)
        """
        self.mock_lat = lat
        self.mock_lon = lon
        self.mock_quality = quality

        if self.is_running:
            self._simulate_location()


# Singleton instance
_gps_instance = None

def get_gps_service(use_mock: bool = False) -> GPSService:
    """
    Ottiene l'istanza singleton del servizio GPS.

    Args:
        use_mock: Se True, usa MockGPSService invece del GPS reale

    Returns:
        Istanza del servizio GPS
    """
    global _gps_instance
    if _gps_instance is None:
        if use_mock or not PLYER_AVAILABLE:
            _gps_instance = MockGPSService()
        else:
            _gps_instance = GPSService()
    return _gps_instance
