import os
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

class AudioViewer:
    @staticmethod
    def generate_visuals_async(audio_file, visuals_callback):
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


        # Save waveform and spectrogram images to temporary files
        waveform_file = "waveform.png"
        spectrogram_file = "spectrogram.png"
        waveform_figure.savefig(waveform_file)
        spectrogram_figure.savefig(spectrogram_file)

        # Call the callback functions with the waveform and spectrogram image files
        visuals_callback(waveform_file, spectrogram_file)

