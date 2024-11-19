import sqlite3
import threading

# Crear un Lock global para manejar la concurrencia
db_lock = threading.Lock()

# Conexión a la base de datos con timeout y acceso concurrente permitido
def connect_db():
    # El timeout de 5 segundos permite esperar antes de renunciar si la base de datos está bloqueada
    return sqlite3.connect('movies.db', timeout=5, check_same_thread=False)

# Función para crear un registro en la tabla 'movies'
def create_movie(id, nombre, details):
    with db_lock:
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO movies (id, nombre, details) VALUES (?, ?, ?)", (id, nombre, details))
            conn.commit()
            print(f"Película '{nombre}' creada con éxito.")
        except sqlite3.IntegrityError:
            print(f"Película '{nombre}' ya existe en la base de datos.")
        finally:
            conn.close()

# Función para leer registros de la tabla 'movies'
def read_movies():
    with db_lock:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies")
        movies = cursor.fetchall()
        conn.close()
        return movies

# Función para crear un país en la tabla 'country'
def create_country(nombre, url=None):
    with db_lock:
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO country (nombre, url) VALUES (?, ?)", (nombre, url))
            conn.commit()
            print(f"País '{nombre}' creado con éxito.")
        except sqlite3.IntegrityError:
            print(f"País '{nombre}' ya existe en la base de datos.")
        finally:
            conn.close()

# Función para verificar si un país ya existe en la tabla 'country'
def country_exists(nombre):
    with db_lock:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM country WHERE nombre = ?", (nombre,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

# Función para crear una relación entre película y países en 'movie_country'
def create_movie_country(id_movie, paises):
    with db_lock:
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO movie_country (id_movie, paises) VALUES (?, ?)", (id_movie, paises))
            conn.commit()
            print(f"Relación película-paises creada para la película ID '{id_movie}'.")
        except sqlite3.IntegrityError:
            print(f"La relación para la película ID '{id_movie}' ya existe.")
        finally:
            conn.close()
