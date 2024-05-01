import os
import shutil, time
from audio_viewer import AudioViewer
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import pygame # type: ignore

pygame.mixer.init()

def select_source_directory():  # Select the source directory for scanning
    directory = filedialog.askdirectory()  # Get the selected directory
    if directory:  # Check if a directory was selected
        source_entry.set(directory)  # Set the entry field with the selected directory
        threading.Thread(target=scan_and_update, args=(directory,)).start()  # Start scanning in a new thread
def scan_directory(directory):  # Scan the directory for audio files
    audio_files = []  # Initialize list of audio files
    for root, _, files in os.walk(directory):  # Walk through the directory tree
        for file in files:
            if file.endswith(('.mp3', '.wav')):  # Check if the file is an audio file
                audio_files.append(os.path.join(root, file))  # Add the file to the list
    return audio_files
def scan_and_update(directory):  # Scan the directory for audio files and update the checkbuttons
    global audio_files_list  # Use a global variable for the list of audio files
    audio_files_list = scan_directory(directory)  # Get the list of audio files
    update_checkbuttons()  # Update the checkbuttons
def select_target_directory():  # Select the target directory for transferring files
    directory = filedialog.askdirectory()  # Get the selected directory
    if directory:  # Check if a directory was selected
        target_entry.set(directory)  # Set the entry field with the selected directory
def on_filter_text_changed(event):  # Handle filter text changes
    update_checkbuttons()  # Update the checkbuttons
def on_entry_click(event):
    if filter_entry.get() == 'Type here to filter files':
        filter_entry.delete(0, tk.END)
        filter_entry.config(fg='white')  # Change text color to black when user starts typing
def on_entry_leave(event):
    if not filter_entry.get():
        filter_entry.insert(0, 'Type here to filter files')
        filter_entry.config(fg='white')  # Change text color back to grey when entry is empty
def on_mousewheel(event):  # Handle mouse wheel events
    if event.delta < 0:
        canvas.yview_scroll(1, "units")  # Scroll up
    elif event.delta > 0:
        canvas.yview_scroll(-1, "units")  # Scroll down

def update_checkbuttons():  # Update the checkbuttons with the filtered list of audio files
    for widget in checkbutton_frame.winfo_children():  # Destroy all existing widgets
        widget.destroy()  # Clear the frame

    global file_vars  # Use a global variable for the dictionary of variables
    file_vars = {}  # Initialize the dictionary

    global filtered_files  # Use a global variable for the list of filtered files
    
    filter_text = filter_entry.get().lower() if filter_entry.get().lower() != 'type here to filter files' else ''
    filtered_files = [file for file in audio_files_list if filter_text in os.path.basename(file).lower()]  # Filter the list of audio files

    for file in filtered_files:  # Create a checkbutton for each filtered file
        var = tk.IntVar()  # Initialize an integer variable
        checkbutton = ttk.Checkbutton(checkbutton_frame, text=os.path.basename(file), variable=var)  # Create the checkbutton
        checkbutton.pack(fill=tk.X, anchor=tk.W, padx=12, pady=1)  # Pack the checkbutton
        file_vars[file] = var  # Add the variable to the dictionary
        checkbutton.bind("<Button-1>", lambda event, file=file, cb=checkbutton: show_visuals(file, cb))   # Bind a function to the checkbutton

    canvas.update_idletasks()  # Update the canvas
    canvas.configure(scrollregion=canvas.bbox('all'))  # Configure the scroll region

    if len(filtered_files) > 0:  # Check if there are any filtered files
        files_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=(4, 8))  # Pack the frame
    else:
        files_frame.pack_forget()  # Forget the frame

def show_visuals(file, checkbutton):
    
    global last_selected_file
    if file == last_selected_file: last_selected_file; play_audio(); return
    last_selected_file = file
    
    original_width, original_height = root.winfo_width(), root.winfo_height() # Store the original window size
    [widget.destroy() for widget in waveform_frame.winfo_children() + spectrogram_frame.winfo_children()] # Clear plot frames

    if file:
        loading_label = tk.Label(waveform_frame, text="Generating plots, please wait...")
        loading_label.pack(side=tk.TOP, padx=10, pady=10)

        def display_waveform_and_spectrogram():
            loading_label.destroy()
            AudioViewer.generate_visuals_async(file, waveform_frame, spectrogram_frame, checkbutton)

            # Prevent the window from shrinking below the original size
            root.update_idletasks()
            current_width = root.winfo_width()
            current_height = root.winfo_height()
            root.minsize(max(current_width, original_width), max(current_height, original_height))

            play_button.pack(side=tk.BOTTOM)# Pack the play button at the bottom of the player frame
            play_audio()  # Start audio playback after visuals are generated
        
        visuals_frame.after(0, display_waveform_and_spectrogram) # Call the function asynchronously
        play_button.pack_forget() # Hide the play button during plot generation

def play_audio():
    global sound, audio_playing, last_played_file
    
    if last_selected_file:
        if audio_playing and last_played_file == last_selected_file:
            sound.stop()
            audio_playing = False
            play_button.config(text="Play")  # Change button text to "Play"
        else:
            if audio_playing and last_played_file != last_selected_file:
                sound.stop()
                
            sound = pygame.mixer.Sound(last_selected_file)
            sound.play()  # Start playback asynchronously
            
            # Update audio_playing flag and button text asynchronously
            audio_playing = True
            play_button.config(text="Stop")  # Change button text to "Stop"
            
    
            # Update the last played file
            last_played_file = last_selected_file
            
            # Schedule checking for playback completion
            root.after(100, check_playback_completion)
    else:
        messagebox.showerror("Error", "No audio file selected.")



def check_playback_completion():
    global sound, audio_playing
    
    if not pygame.mixer.get_busy():  # If no channel is actively playing
        audio_playing = False
        play_button.config(text="Play")  # Change button text to "Play"
    else:
        root.after(100, check_playback_completion) # Schedule the next check after 100 milliseconds
def transfer_files():  # Transfer selected files to the target directory
    selected_files = [file for file, var in file_vars.items() if var.get()]  # Get the list of selected files

    if not selected_files:  # Check if any files were selected
        messagebox.showerror("Error", "No files selected for transfer.")  # Show an error message
        return

    target_dir = target_entry.get()  # Get the target directory
    if not target_dir:  # Check if a target directory was selected
        messagebox.showerror("Error", "No target directory selected.")  # Show an error message
        return

    for file in selected_files:  # Transfer each selected file
        shutil.copy(file, target_dir)  # Copy the file to the target directory

    messagebox.showinfo("Success", "Files transferred successfully.")  # Show a success message

audio_files_list, filtered_files, checkvars = [], [], []  # Initialize a list for audio files, filtered files and check variables
# Initialize global variables
last_played_file, last_selected_file, sound = None, None, None
audio_playing = False

root = tk.Tk()  # Create the main window
root.title("Audio Browser")  # Set the title of the window

directory_frame = tk.Frame(root)

source_frame = tk.Frame(directory_frame)  # Create a frame for the source directory
select_source_button = tk.Button(source_frame, text="Select Source Directory", command=select_source_directory)  # Create a button to select the source directory
select_source_button.pack(side=tk.LEFT, padx=(0, 6))
source_label = tk.Label(source_frame, text="Source Directory:")  # Create a label for the source directory
source_label.pack(side=tk.LEFT)
source_entry = tk.StringVar()  # Initialize an entry field for the source directory
source_entry.set("")  # Set the default value of the entry field
source_entry_label = tk.Label(source_frame, textvariable=source_entry, anchor='w', width=40)  # Create a label for the entry field
source_entry_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
source_frame.pack(fill=tk.X, padx=10, pady=(6, 2))

target_frame = tk.Frame(directory_frame)  # Create a frame for the target directory
select_target_button = tk.Button(target_frame, text="Select Target Directory", command=select_target_directory)  # Create a button to select the target directory
select_target_button.pack(side=tk.LEFT, padx=(0, 6))
target_label = tk.Label(target_frame, text="Target Directory:")  # Create a label for the target directory
target_label.pack(side=tk.LEFT) 
target_entry = tk.StringVar()  # Initialize an entry field for the target directory
target_entry.set("")  # Set the default value of the entry field
target_entry_label = tk.Label(target_frame, textvariable=target_entry, anchor='w', width=36)  # Create a label for the entry field
target_entry_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(2, 2)) 
target_frame.pack(fill=tk.X, padx=10, pady=(2, 6))

filter_entry = tk.Entry(directory_frame, highlightthickness=1, bd=1, fg='white', bg='black')  # Create an entry field for filtering files
filter_entry.insert(0, 'Type here to filter files')  # Insert faded text as placeholder
filter_entry.bind("<KeyRelease>", on_filter_text_changed)  # Bind a function to the key release event
filter_entry.bind('<FocusIn>', on_entry_click)  # Bind click event
filter_entry.bind('<FocusOut>', on_entry_leave)  # Bind leave event
filter_entry.pack(fill=tk.X, padx=16, pady=(3, 3))

directory_frame.pack(fill=tk.X, padx=6, pady=6)

browser_frame = tk.Frame(root)

files_frame = tk.Frame(browser_frame)  # Create a frame for the list of files

scrollbar = tk.Scrollbar(files_frame, orient="vertical", width=10, troughcolor="black", bg="dark gray")  # Create a scrollbar
canvas = tk.Canvas(files_frame, yscrollcommand=scrollbar.set, highlightthickness=0)  # Create a canvas
scrollbar.config(command=canvas.yview)  # Configure the scrollbar
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))  # Bind a function to the configure event
canvas.bind_all("<MouseWheel>", on_mousewheel)  # Bind a function to mouse wheel events
checkbutton_frame = tk.Frame(canvas)  # Create a frame for the checkbuttons
canvas.create_window((0, 0), window=checkbutton_frame, anchor='nw')  # Pack the frame

scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=6, pady=2)  # Pack the scrollbar
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=2)  # Pack the canvas

files_frame.pack(side=tk.LEFT, padx=(6,2), fill=tk.BOTH, expand=True)  # Pack the frame

visuals_frame = tk.Frame(browser_frame)

player_frame = tk.Frame(visuals_frame)
play_button = tk.Button(player_frame, text="Play", command=play_audio)
player_frame.pack(side=tk.BOTTOM) 

waveform_frame = tk.Frame(visuals_frame)  # Create a frame for the waveform
waveform_frame.pack(side=tk.TOP, pady=2)  # Pack the frame

spectrogram_frame = tk.Frame(visuals_frame)  # Create a frame for the waveform
spectrogram_frame.pack(pady=2)  # Pack the frame

visuals_frame.pack(side=tk.RIGHT, padx=(2,6), fill=tk.BOTH, expand=True) 

browser_frame.pack(fill=tk.X, padx=6, pady=4)

transfer_button_frame = tk.Frame(root)  # Create a frame for the transfer button
transfer_button_frame.pack(side=tk.BOTTOM, pady=8)  # Pack the frame

transfer_button = tk.Button(transfer_button_frame, text="Transfer Files", command=transfer_files)  # Create a button to transfer files
transfer_button.pack(pady=6)  # Pack the button

update_checkbuttons()  # Update the checkbuttons initially
root.mainloop()  # Start the main event loop