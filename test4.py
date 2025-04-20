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
DB_NAME = "music_player_db1"

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

        # Create table to store MP3 file data (BLOB) and file name
        cursor.execute('''CREATE TABLE IF NOT EXISTS songs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            song_data LONGBLOB NOT NULL,
                            song_name VARCHAR(255) NOT NULL
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

        # Extract the song name from the file path
        song_name = os.path.basename(file_path)

        # Connect to the database and insert the song data
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO songs (song_data, song_name) VALUES (%s, %s)", (song_data, song_name))
        conn.commit()
        conn.close()
        print(f"Inserted song {song_name} into the database.")
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
            messagebox.showinfo("Success", f"Song '{os.path.basename(file_path)}' added to the database!")
            load_song_list()  # Reload the list of songs

        except Exception as e:
            messagebox.showerror("Error", f"Error adding the file: {e}")

# Function to load songs from the database into the listbox
def load_song_list():
    try:
        # Connect to the database and fetch all song names
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT song_name FROM songs")
        songs = cursor.fetchall()

        # Clear the listbox and add all songs
        song_listbox.delete(0, END)
        for song in songs:
            song_listbox.insert(END, song[0])

        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# Function to play a selected song from the list
def play_selected_song(event):
    try:
        # Get the selected song name from the listbox
        selected_song = song_listbox.get(song_listbox.curselection())

        # Connect to the database and fetch the selected song data
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT song_data FROM songs WHERE song_name = %s", (selected_song,))
        song_data = cursor.fetchone()

        if song_data:
            # Save the binary data to a temporary file and play it
            temp_file = "temp_song.mp3"
            with open(temp_file, 'wb') as f:
                f.write(song_data[0])

            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            print(f"Playing from database: {temp_file}")
        else:
            messagebox.showinfo("Info", "No song data found!")

        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    except Exception as e:
        messagebox.showerror("Error", f"Error playing the song: {e}")

# Create main window
root = Tk()
root.title("MP3 Player with MySQL Database")
root.geometry("400x300")

# Initialize database and create tables
create_database()

# Create and place open file button
open_button = Button(root, text="Open MP3 File", command=open_file)
open_button.pack(pady=10)

# Create a listbox to display song names
song_listbox = Listbox(root, height=10, width=50)
song_listbox.pack(pady=20)

# Bind the listbox selection to the play function
song_listbox.bind("<ButtonRelease-1>", play_selected_song)

# Load and display the list of songs from the database
load_song_list()

# Start the Tkinter event loop
root.mainloop()
