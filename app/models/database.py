"""
Database manager per l'app Mantrailing Training.
Gestisce la creazione dello schema SQLite e le operazioni CRUD sui percorsi.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """Gestisce tutte le operazioni del database SQLite."""

    def __init__(self, db_path: str = None):
        """
        Inizializza il database manager.

        Args:
            db_path: Percorso del file database. Se None, usa percorso di default.
        """
        if db_path is None:
            # Usa directory dati dell'app
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(app_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, 'mantrailing.db')

        self.db_path = db_path
        self.connection = None
        self._init_database()

    def _init_database(self):
        """Crea le tabelle del database se non esistono."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabella per i percorsi salvati
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER,
                total_points INTEGER,
                track_data TEXT NOT NULL
            )
        ''')

        # Tabella per i punti GPS individuali (opzionale, per analisi dettagliate)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS track_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                gps_quality INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                point_order INTEGER NOT NULL,
                FOREIGN KEY (track_id) REFERENCES tracks (id) ON DELETE CASCADE
            )
        ''')

        # Tabella per le impostazioni dell'app
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Indici per ottimizzare le query
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tracks_created_at
            ON tracks(created_at DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_track_points_track_id
            ON track_points(track_id, point_order)
        ''')

        conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Ottiene una connessione al database."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Per ottenere risultati come dizionari
        return self.connection

    def close(self):
        """Chiude la connessione al database."""
        if self.connection:
            self.connection.close()
            self.connection = None

    # ============================================================================
    # OPERAZIONI CRUD PER I PERCORSI
    # ============================================================================

    def save_track(self, name: str, track_data: str, description: str = "",
                   duration_seconds: int = 0) -> int:
        """
        Salva un nuovo percorso nel database.

        Args:
            name: Nome del percorso
            track_data: Dati del percorso in formato CSV (lat,lon,quality;...)
            description: Descrizione opzionale
            duration_seconds: Durata della registrazione in secondi

        Returns:
            ID del percorso salvato
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Conta i punti nel percorso
        total_points = len(track_data.split(';')) if track_data else 0

        cursor.execute('''
            INSERT INTO tracks (name, description, track_data, duration_seconds, total_points)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, track_data, duration_seconds, total_points))

        track_id = cursor.lastrowid
        conn.commit()

        return track_id

    def get_track(self, track_id: int) -> Optional[Dict]:
        """
        Recupera un percorso dal database.

        Args:
            track_id: ID del percorso

        Returns:
            Dizionario con i dati del percorso o None se non trovato
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tracks WHERE id = ?', (track_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_all_tracks(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Recupera tutti i percorsi salvati.

        Args:
            limit: Numero massimo di percorsi da recuperare
            offset: Offset per la paginazione

        Returns:
            Lista di dizionari con i dati dei percorsi
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM tracks
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        return [dict(row) for row in cursor.fetchall()]

    def update_track(self, track_id: int, name: str = None,
                     description: str = None) -> bool:
        """
        Aggiorna i metadati di un percorso.

        Args:
            track_id: ID del percorso
            name: Nuovo nome (opzionale)
            description: Nuova descrizione (opzionale)

        Returns:
            True se l'aggiornamento è andato a buon fine
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if name is not None:
            updates.append('name = ?')
            params.append(name)

        if description is not None:
            updates.append('description = ?')
            params.append(description)

        if not updates:
            return False

        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(track_id)

        query = f"UPDATE tracks SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

        return cursor.rowcount > 0

    def delete_track(self, track_id: int) -> bool:
        """
        Elimina un percorso dal database.

        Args:
            track_id: ID del percorso da eliminare

        Returns:
            True se l'eliminazione è andata a buon fine
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM tracks WHERE id = ?', (track_id,))
        conn.commit()

        return cursor.rowcount > 0

    def search_tracks(self, search_term: str) -> List[Dict]:
        """
        Cerca percorsi per nome o descrizione.

        Args:
            search_term: Termine di ricerca

        Returns:
            Lista di percorsi che corrispondono alla ricerca
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT * FROM tracks
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY created_at DESC
        ''', (search_pattern, search_pattern))

        return [dict(row) for row in cursor.fetchall()]

    # ============================================================================
    # OPERAZIONI PER LE IMPOSTAZIONI
    # ============================================================================

    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """
        Recupera un'impostazione dal database.

        Args:
            key: Chiave dell'impostazione
            default: Valore di default se l'impostazione non esiste

        Returns:
            Valore dell'impostazione o default
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()

        return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        """
        Salva un'impostazione nel database.

        Args:
            key: Chiave dell'impostazione
            value: Valore da salvare
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))

        conn.commit()

    def delete_setting(self, key: str) -> bool:
        """
        Elimina un'impostazione dal database.

        Args:
            key: Chiave dell'impostazione da eliminare

        Returns:
            True se l'eliminazione è andata a buon fine
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
        conn.commit()

        return cursor.rowcount > 0

    # ============================================================================
    # UTILITY
    # ============================================================================

    def get_stats(self) -> Dict:
        """
        Recupera statistiche sul database.

        Returns:
            Dizionario con le statistiche
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Conta totale percorsi
        cursor.execute('SELECT COUNT(*) as count FROM tracks')
        total_tracks = cursor.fetchone()['count']

        # Conta totale punti
        cursor.execute('SELECT SUM(total_points) as total FROM tracks')
        total_points = cursor.fetchone()['total'] or 0

        return {
            'total_tracks': total_tracks,
            'total_points': total_points,
            'db_path': self.db_path
        }


# Singleton instance
_db_instance = None

def get_database() -> DatabaseManager:
    """Ottiene l'istanza singleton del database manager."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
