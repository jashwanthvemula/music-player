import math
import struct
import pygame
import tkinter as tk
from tkinter import messagebox


def create_tone_audio_10sec(filename="beep_10sec.wav", frequency=440, duration=10, sample_rate=44100, volume=0.5):
    """Generate a 10-second tone and save as WAV file."""
    num_samples = int(sample_rate * duration)
    data = bytearray()

    for n in range(num_samples):
        sample = volume * math.sin(2 * math.pi * frequency * n / sample_rate)
        data += struct.pack('<h', int(sample * 32767))  # 16-bit PCM

    byte_rate = sample_rate * 2  # 2 bytes per sample
    block_align = 2
    data_size = len(data)
    chunk_size = 36 + data_size

    header = bytearray()
    header += b'RIFF'
    header += struct.pack('<I', chunk_size)
    header += b'WAVE'

    header += b'fmt '
    header += struct.pack('<I', 16)
    header += struct.pack('<H', 1)  # PCM
    header += struct.pack('<H', 1)  # Mono
    header += struct.pack('<I', sample_rate)
    header += struct.pack('<I', byte_rate)
    header += struct.pack('<H', block_align)
    header += struct.pack('<H', 16)  # Bits per sample

    header += b'data'
    header += struct.pack('<I', data_size)

    with open(filename, "wb") as f:
        f.write(header + data)


def play_song():
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("beep_10sec.wav")
        pygame.mixer.music.play()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to play song: {e}")


def main():
    # Step 1: Create the audio file
    create_tone_audio_10sec()

    # Step 2: Launch the GUI
    window = tk.Tk()
    window.title("Simple Audio Player")
    window.geometry("300x150")
    window.resizable(False, False)

    label = tk.Label(window, text="10 Second Beep Tone", font=("Arial", 14))
    label.pack(pady=20)

    play_button = tk.Button(window, text="▶️ Play Song", font=("Arial", 12), command=play_song)
    play_button.pack()

    window.mainloop()


if __name__ == "__main__":
    main()
