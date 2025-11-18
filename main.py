"""
Mantrailing Training App
App mobile per l'addestramento di cani da ricerca persone scomparse (mantrailing).

Punto di ingresso principale dell'applicazione.
"""

import os
import sys

# Aggiungi la directory corrente al path per importare i moduli app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty

# Importa i moduli dell'app
from app.models.database import get_database
from app.services.gps_service import get_gps_service


class ModeSelectionScreen(Screen):
    """Schermata di selezione modalità."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'mode_selection'

        # Layout principale
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Titolo
        title = Label(
            text='MANTRAILING TRAINING',
            font_size='24sp',
            size_hint=(1, 0.2),
            bold=True
        )
        layout.add_widget(title)

        # Sottotitolo
        subtitle = Label(
            text='Seleziona la modalità operativa',
            font_size='16sp',
            size_hint=(1, 0.1)
        )
        layout.add_widget(subtitle)

        # Contenitore per i pulsanti
        buttons_layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 0.7))

        # Pulsante Modalità Disperso
        disperso_btn = Button(
            text='MODALITÀ DISPERSO\n\nRegistra il percorso del disperso',
            font_size='16sp',
            background_color=(0.2, 0.6, 0.9, 1)
        )
        disperso_btn.bind(on_press=self.goto_disperso_mode)
        buttons_layout.add_widget(disperso_btn)

        # Pulsante Modalità Unità Cinofila
        cinofila_btn = Button(
            text='MODALITÀ UNITÀ CINOFILA\n\nSegui il percorso con alert acustici',
            font_size='16sp',
            background_color=(0.3, 0.7, 0.3, 1)
        )
        cinofila_btn.bind(on_press=self.goto_cinofila_mode)
        buttons_layout.add_widget(cinofila_btn)

        # Pulsante Modalità Addestratore
        addestratore_btn = Button(
            text='MODALITÀ ADDESTRATORE\n\nMonitora su mappa l\'esercitazione',
            font_size='16sp',
            background_color=(0.8, 0.4, 0.2, 1)
        )
        addestratore_btn.bind(on_press=self.goto_addestratore_mode)
        buttons_layout.add_widget(addestratore_btn)

        layout.add_widget(buttons_layout)

        # Pulsante impostazioni in basso
        settings_btn = Button(
            text='Impostazioni',
            size_hint=(1, 0.1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        settings_btn.bind(on_press=self.goto_settings)
        layout.add_widget(settings_btn)

        self.add_widget(layout)

    def goto_disperso_mode(self, instance):
        """Passa alla modalità disperso."""
        # TODO: Implementare la schermata modalità disperso
        print("Modalità Disperso selezionata")

    def goto_cinofila_mode(self, instance):
        """Passa alla modalità unità cinofila."""
        # TODO: Implementare la schermata modalità cinofila
        print("Modalità Unità Cinofila selezionata")

    def goto_addestratore_mode(self, instance):
        """Passa alla modalità addestratore."""
        # TODO: Implementare la schermata modalità addestratore
        print("Modalità Addestratore selezionata")

    def goto_settings(self, instance):
        """Passa alle impostazioni."""
        # TODO: Implementare la schermata impostazioni
        print("Impostazioni selezionate")


class MantrailingApp(App):
    """Classe principale dell'applicazione."""

    # Proprietà per il titolo
    title = StringProperty('Mantrailing Training')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.gps = None
        self.screen_manager = None

    def build(self):
        """
        Costruisce l'interfaccia principale dell'app.

        Returns:
            Widget root dell'applicazione
        """
        # Imposta le dimensioni della finestra per il testing desktop
        if not self.is_mobile():
            Window.size = (360, 640)

        # Inizializza il database
        self.db = get_database()
        print(f"Database inizializzato: {self.db.get_stats()}")

        # Inizializza il GPS (usa mock per testing desktop)
        use_mock = not self.is_mobile()
        self.gps = get_gps_service(use_mock=use_mock)
        print(f"GPS service inizializzato (mock={use_mock})")

        # Crea il screen manager
        self.screen_manager = ScreenManager()

        # Aggiungi la schermata di selezione modalità
        mode_selection_screen = ModeSelectionScreen()
        self.screen_manager.add_widget(mode_selection_screen)

        # TODO: Aggiungere altre schermate
        # - DispersoModeScreen
        # - CinofilaModeScreen
        # - AddestratoreModeSscreen
        # - SettingsScreen
        # - TrackListScreen

        return self.screen_manager

    def on_start(self):
        """Chiamato quando l'app viene avviata."""
        print("Mantrailing Training App avviata")

    def on_pause(self):
        """
        Chiamato quando l'app va in pausa (Android).

        Returns:
            True per permettere il pause
        """
        # Ferma il GPS quando l'app va in pausa
        if self.gps and self.gps.is_running:
            self.gps.stop()
        return True

    def on_resume(self):
        """Chiamato quando l'app riprende dall'essere in pausa (Android)."""
        # Opzionalmente riavvia il GPS se era attivo
        pass

    def on_stop(self):
        """Chiamato quando l'app viene chiusa."""
        # Chiudi le connessioni
        if self.gps and self.gps.is_running:
            self.gps.stop()

        if self.db:
            self.db.close()

        print("Mantrailing Training App chiusa")

    @staticmethod
    def is_mobile():
        """
        Verifica se l'app è in esecuzione su dispositivo mobile.

        Returns:
            True se su mobile, False su desktop
        """
        from kivy.utils import platform
        return platform in ('android', 'ios')


def main():
    """Funzione principale per avviare l'app."""
    try:
        app = MantrailingApp()
        app.run()
    except Exception as e:
        print(f"Errore nell'avvio dell'app: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
