import os
import librosa.display
import matplotlib.pyplot as plt
import tkinter as tk

class AudioViewer:
    @staticmethod
    def generate_waveform_async(audio_file, waveform_callback):
        # Load audio file
        y, sr = librosa.load(audio_file, sr=None)

        # Generate waveform
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(y, sr=sr)
        plt.title('Waveform: ' + os.path.basename(audio_file))
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.tight_layout()

        # Save waveform image to a temporary file
        waveform_file = "waveform.png"
        plt.savefig(waveform_file)

        # Call the callback function with the waveform image file
        waveform_callback(waveform_file)
