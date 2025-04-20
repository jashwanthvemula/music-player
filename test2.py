import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector
import pygame
import tempfile
import os


# --- CONFIGURE THESE ---
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "new_password"
DB_NAME = "musicdb"
TABLE_NAME = "songs"
# ------------------------
def connect_db():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.errors.ProgrammingError as e:
        if "Unknown database" in str(e):
            temp_conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE {DB_NAME}")
            temp_conn.commit()
            temp_cursor.close()
            temp_conn.close()
            return connect_db()
        else:
            raise e





def create_table_if_not_exists():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            data LONGBLOB
        )
    """)
    db.commit()
    cursor.close()
    db.close()


def upload_song():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
    if not file_path:
        return

    try:
        with open(file_path, 'rb') as f:
            audio_data = f.read()
            filename = os.path.basename(file_path)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO {TABLE_NAME} (name, data) VALUES (%s, %s)", (filename, audio_data))
        db.commit()
        cursor.close()
        db.close()

        messagebox.showinfo("Success", f"'{filename}' uploaded to database!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to upload: {e}")


def play_song_from_db():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT name, data FROM {TABLE_NAME} ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        db.close()

        if result:
            name, blob = result
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(blob)
                tmp_path = tmp_file.name

            pygame.mixer.init()
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
        else:
            messagebox.showinfo("Info", "No songs found in database.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to play: {e}")


def main():
    connect_db()
    create_table_if_not_exists()


    window = tk.Tk()
    window.title("🎶 Song Uploader & Player")
    window.geometry("350x200")
    window.resizable(False, False)

    tk.Label(window, text="Song Manager (MySQL)", font=("Arial", 14)).pack(pady=15)

    tk.Button(window, text="📤 Upload Song to DB", font=("Arial", 12), command=upload_song).pack(pady=10)
    tk.Button(window, text="▶️ Play Last Uploaded", font=("Arial", 12), command=play_song_from_db).pack(pady=10)

    window.mainloop()


if __name__ == "__main__":
    main()
