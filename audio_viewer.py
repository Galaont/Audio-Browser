import numpy as np
import os
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import librosa
import librosa.display

class AudioViewer:
    @staticmethod
    def generate_visuals_async(audio_file, waveform_frame, spectrogram_frame):
        # Load audio file
        y, sr = librosa.load(audio_file, sr=None)

        # Generate waveform
        waveform_figure = plt.figure(figsize=(9, 3.9))  # Adjusted figure size
        waveform_ax = waveform_figure.add_subplot(111)
        waveform_ax.set_title('Waveform: ' + os.path.basename(audio_file))
        waveform_ax.set_xlabel('Time (s)')
        waveform_ax.set_ylabel('Amplitude')
        librosa.display.waveshow(y, sr=sr, ax=waveform_ax)
        waveform_ax.margins(0, 0.1)  # Adjust padding to ensure waveform starts from y-axis
        plt.subplots_adjust(left=0.09, right=0.98, top=0.92)

        # Generate spectrogram
        spectrogram_figure = plt.figure(figsize=(9, 3.9))  # Adjusted figure size
        spectrogram_ax = spectrogram_figure.add_subplot(111)
        spectrogram_ax.set_title('Spectrogram: ' + os.path.basename(audio_file))
        spectrogram_ax.set_xlabel('Time (s)')
        spectrogram_ax.set_ylabel('Frequency (Hz)')
        S = librosa.feature.melspectrogram(y=y, sr=sr)
        S_dB = librosa.power_to_db(S, ref=np.max)

        librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', ax=spectrogram_ax)
        plt.subplots_adjust(left=0.09, right=0.98, top=0.92)

        # Embed waveform and spectrogram into Tkinter frames
        waveform_canvas = FigureCanvasTkAgg(waveform_figure, master=waveform_frame)
        waveform_canvas.draw()
        waveform_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        spectrogram_canvas = FigureCanvasTkAgg(spectrogram_figure, master=spectrogram_frame)
        spectrogram_canvas.draw()
        spectrogram_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Destroy Matplotlib figures
        plt.close(waveform_figure)
        plt.close(spectrogram_figure)