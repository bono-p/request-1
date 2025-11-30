# database.py - Version MySQL AlwaysData avec PyMySQL
""" import os
import pymysql
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Valeurs récupérées depuis Render ENV VARS
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        """Établit la connexion MySQL (thread-safe)."""
        if self.conn and self.conn.open:
            return self.conn

        def _connect():
            return pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                port=MYSQL_PORT,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )

        self.conn = await asyncio.to_thread(_connect)
        return self.conn

    async def init_db(self):
        """Créer les tables si elles n’existent pas (idempotent)."""
        conn = await self.connect()

        async def _init():
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INT AUTO_INCREMENT PRIMARY KEY,
                        matricule VARCHAR(15) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        phone VARCHAR(9) NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS requests (
                        request_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        all_name VARCHAR(255) NOT NULL,
                        matricule VARCHAR(15) NOT NULL,
                        cycle VARCHAR(50) NOT NULL,
                        level INT NOT NULL,
                        nom_code_ue VARCHAR(2048) NOT NULL,
                        note_exam BOOLEAN DEFAULT FALSE,
                        note_cc BOOLEAN DEFAULT FALSE,
                        note_tp BOOLEAN DEFAULT FALSE,
                        note_tpe BOOLEAN DEFAULT FALSE,
                        autre BOOLEAN DEFAULT FALSE,
                        comment TEXT,
                        just_p BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                """)

            conn.commit()

        await asyncio.to_thread(_init)
        print("✅ Base de données MySQL initialisée !")

    async def execute_query(self, query, params=None):
        """Exécuter INSERT, UPDATE, DELETE."""
        conn = await self.connect()

        def _execute():
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.lastrowid  # fonctionne pour INSERT

        return await asyncio.to_thread(_execute)

    async def fetch_one(self, query, params=None):
        """Récupère une seule ligne."""
        conn = await self.connect()

        def _fetch():
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()

        return await asyncio.to_thread(_fetch)

    async def fetch_all(self, query, params=None):
        """Récupère plusieurs lignes."""
        conn = await self.connect()

        def _fetchall():
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

        return await asyncio.to_thread(_fetchall)

    async def test_connection(self):
        """Tester la connexion."""
        try:
            result = await self.fetch_one("SELECT VERSION()")
            return {"status": "success", "version": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Instance globale
db = Database()"""






# database.py - Version MySQL AlwaysData avec PyMySQL
import os
import pymysql
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Valeurs récupérées depuis Render ENV VARS
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

# Debugging - À ajouter temporairement pour vérification
print("=== CONFIGURATION DATABASE ===")
print(f"MYSQL_HOST: {MYSQL_HOST}")
print(f"MYSQL_USER: {MYSQL_USER}")
print(f"MYSQL_DB: {MYSQL_DB}")
print(f"MYSQL_PORT: {MYSQL_PORT}")
print("==============================")

class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        """Établit la connexion MySQL (thread-safe)."""
        if self.conn and self.conn.open:
            return self.conn

        def _connect():
            return pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                port=MYSQL_PORT,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )

        self.conn = await asyncio.to_thread(_connect)
        print("✅ Connexion MySQL établie !")
        return self.conn

    async def close(self):
        """Ferme la connexion (nécessaire pour le lifespan)."""
        if self.conn and self.conn.open:
            def _close():
                self.conn.close()
            await asyncio.to_thread(_close)
            self.conn = None
            print("✅ Connexion MySQL fermée !")
        else:
            print("ℹ️ Aucune connexion à fermer")

    async def init_db(self):
        """Créer les tables si elles n'existent pas (idempotent)."""
        try:
            conn = await self.connect()

            def _init():
                with conn.cursor() as cur:
                    # Table users
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            user_id INT AUTO_INCREMENT PRIMARY KEY,
                            matricule VARCHAR(15) UNIQUE NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            last_name VARCHAR(255) NOT NULL,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            phone VARCHAR(9) NOT NULL,
                            password TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # Table requests
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS requests (
                            request_id INT AUTO_INCREMENT PRIMARY KEY,
                            user_id INT NOT NULL,
                            all_name VARCHAR(255) NOT NULL,
                            matricule VARCHAR(15) NOT NULL,
                            cycle VARCHAR(50) NOT NULL,
                            level INT NOT NULL,
                            nom_code_ue VARCHAR(2048) NOT NULL,
                            note_exam BOOLEAN DEFAULT FALSE,
                            note_cc BOOLEAN DEFAULT FALSE,
                            note_tp BOOLEAN DEFAULT FALSE,
                            note_tpe BOOLEAN DEFAULT FALSE,
                            autre BOOLEAN DEFAULT FALSE,
                            comment TEXT,
                            just_p BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                        )
                    """)

                conn.commit()

            await asyncio.to_thread(_init)
            print("✅ Base de données MySQL initialisée avec succès !")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
            raise

    async def execute_query(self, query, params=None):
        """Exécuter INSERT, UPDATE, DELETE."""
        conn = await self.connect()

        def _execute():
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.lastrowid  # fonctionne pour INSERT

        return await asyncio.to_thread(_execute)

    async def fetch_one(self, query, params=None):
        """Récupère une seule ligne."""
        conn = await self.connect()

        def _fetch():
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()

        return await asyncio.to_thread(_fetch)

    async def fetch_all(self, query, params=None):
        """Récupère plusieurs lignes."""
        conn = await self.connect()

        def _fetchall():
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

        return await asyncio.to_thread(_fetchall)

    async def test_connection(self):
        """Tester la connexion."""
        try:
            result = await self.fetch_one("SELECT VERSION() as version")
            return {"status": "success", "version": result["version"]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def is_connected(self):
        """Vérifie si la connexion est active."""
        try:
            await self.fetch_one("SELECT 1")
            return True
        except Exception:
            return False


# Instance globale
db = Database()