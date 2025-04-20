import os
import mysql.connector
import pygame
from tkinter import *
from tkinter import filedialog, messagebox

# Initialize Pygame mixer
pygame.mixer.init()

# MySQL Database connection details
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "new_password"
DB_NAME = "music_player_db"

# Function to create the database and table if they do not exist
def create_database():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.database = DB_NAME

        # Create table to store MP3 file data (BLOB)
        cursor.execute('''CREATE TABLE IF NOT EXISTS songs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            song_data LONGBLOB NOT NULL
                        )''')

        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# Function to insert a song's binary data into the database
def insert_song(file_path):
    try:
        # Read the MP3 file as binary data
        with open(file_path, 'rb') as file:
            song_data = file.read()
        
        # Connect to the database and insert the song data
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO songs (song_data) VALUES (%s)", (song_data,))
        conn.commit()
        conn.close()
        print(f"Inserted song {file_path} into the database.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# Function to open and insert an audio file into the database
def open_file():
    # Ask user to select an audio file
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")])
    
    if file_path:
        try:
            # Insert file data into the database
            insert_song(file_path)
            
            # Play the selected file
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"Playing {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error playing the file: {e}")

# Function to play a song from the database
def play_from_database():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT song_data FROM songs ORDER BY id DESC LIMIT 1")  # Get the last inserted song
        row = cursor.fetchone()
        
        if row:
            song_data = row[0]
            # Save the binary data to a temporary file and play it
            temp_file = "temp_song.mp3"
            with open(temp_file, 'wb') as f:
                f.write(song_data)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            print(f"Playing from database: {temp_file}")
        else:
            messagebox.showinfo("Info", "No songs found in the database!")
        
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# Create main window
root = Tk()
root.title("MP3 Player with MySQL Database")
root.geometry("400x200")

# Initialize database and create tables
create_database()

# Create and place open file button
open_button = Button(root, text="Open MP3 File", command=open_file)
open_button.pack(pady=20)

# Create and place play from database button
play_button = Button(root, text="Play From Database", command=play_from_database)
play_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
