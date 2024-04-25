import os
import shutil
from audio_viewer import AudioViewer
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# Function to select the source directory
def select_source_directory():  # Select the source directory for scanning
    directory = filedialog.askdirectory()  # Get the selected directory
    if directory:  # Check if a directory was selected
        source_entry.set(directory)  # Set the entry field with the selected directory
        threading.Thread(target=scan_and_update, args=(directory,)).start()  # Start scanning in a new thread

# Function to scan the directory and update the checkbuttons
def scan_directory(directory):  # Scan the directory for audio files
    audio_files = []  # Initialize list of audio files
    for root, _, files in os.walk(directory):  # Walk through the directory tree
        for file in files:
            if file.endswith(('.mp3', '.wav')):  # Check if the file is an audio file
                audio_files.append(os.path.join(root, file))  # Add the file to the list
    return audio_files

# Function to scan and update the checkbuttons
def scan_and_update(directory):  # Scan the directory for audio files and update the checkbuttons
    global audio_files_list  # Use a global variable for the list of audio files
    audio_files_list = scan_directory(directory)  # Get the list of audio files
    update_checkbuttons()  # Update the checkbuttons

# Function to select the target directory
def select_target_directory():  # Select the target directory for transferring files
    directory = filedialog.askdirectory()  # Get the selected directory
    if directory:  # Check if a directory was selected
        target_entry.set(directory)  # Set the entry field with the selected directory

# Function to update the checkbuttons
def update_checkbuttons():  # Update the checkbuttons with the filtered list of audio files
    for widget in checkbutton_frame.winfo_children():  # Destroy all existing widgets
        widget.destroy()  # Clear the frame

    global file_vars  # Use a global variable for the dictionary of variables
    file_vars = {}  # Initialize the dictionary

    global filtered_files  # Use a global variable for the list of filtered files
    filter_text = filter_entry.get().lower()  # Get the text from the filter entry field
    filtered_files = [file for file in audio_files_list if filter_text in os.path.basename(file).lower()]  # Filter the list of audio files

    for file in filtered_files:  # Create a checkbutton for each filtered file
        var = tk.IntVar()  # Initialize an integer variable
        checkbutton = ttk.Checkbutton(checkbutton_frame, text=os.path.basename(file), variable=var)  # Create the checkbutton
        checkbutton.pack(fill=tk.X, anchor=tk.W, padx=6, pady=1)  # Pack the checkbutton
        file_vars[file] = var  # Add the variable to the dictionary
        checkbutton.bind("<Button-1>", lambda event, file=file, cb=checkbutton: show_waveform(file, cb))  # Bind a function to the checkbutton

    canvas.update_idletasks()  # Update the canvas
    canvas.configure(scrollregion=canvas.bbox('all'))  # Configure the scroll region

    if len(filtered_files) > 0:  # Check if there are any filtered files
        files_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=(4, 8))  # Pack the frame
    else:
        files_frame.pack_forget()  # Forget the frame

# Function to transfer files
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

# Function to handle mouse wheel events
def on_mousewheel(event):  # Handle mouse wheel events
    if event.delta < 0:
        canvas.yview_scroll(1, "units")  # Scroll up
    elif event.delta > 0:
        canvas.yview_scroll(-1, "units")  # Scroll down

# Function to handle filter text changes
def on_filter_text_changed(event):  # Handle filter text changes
    update_checkbuttons()  # Update the checkbuttons

# Function to show a waveform for an audio file
def show_waveform(file, checkbutton):  # Show a waveform for an audio file
    for widget in root.winfo_children():  # Destroy all existing widgets
        if isinstance(widget, tk.Label) and widget.winfo_class() == "Label":  # Check if the widget is a Label
            widget.destroy()  # Clear the frame

    if file:  # Check if an audio file was selected
         # Show loading message while waveform is being generated
        loading_label = tk.Label(root, text="Generating waveform, please wait...")  # Create a loading label
        loading_label.pack(side=tk.TOP, padx=10, pady=10)  # Pack the label

        def display_waveform(waveform_image):  # Define a function to display the waveform image
            loading_label.destroy()  # Destroy the loading label
            waveform_photo = tk.PhotoImage(file=waveform_image)  # Create a PhotoImage for the waveform
            waveform_label = tk.Label(root, image=waveform_photo)  # Create a Label for the waveform
            waveform_label.image = waveform_photo  # Store the image in the Label
            waveform_label.pack(side=tk.TOP, padx=16, pady=10)  # Pack the label
            checkbutton.state(['!alternate'])  # Set the state of the checkbutton

        AudioViewer.generate_waveform_async(file, display_waveform)  # Generate and display the waveform asynchronously

checkvars = []  # Initialize a list for check variables
audio_files_list = []  # Initialize a global variable for the list of audio files
filtered_files = []  # Initialize a global variable for the list of filtered files

root = tk.Tk()  # Create the main window
root.title("Audio Browser")  # Set the title of the window

source_frame = tk.Frame(root)  # Create a frame for the source directory
source_frame.pack(fill=tk.X, padx=10, pady=(8, 4))  # Pack the frame

select_source_button = tk.Button(source_frame, text="Select Source Directory", command=select_source_directory)  # Create a button to select the source directory
select_source_button.pack(side=tk.LEFT, padx=(0, 6), pady=(0, 8))  # Pack the button

source_label = tk.Label(source_frame, text="Source Directory:")  # Create a label for the source directory
source_label.pack(side=tk.LEFT, pady=(0, 8))  # Pack the label

source_entry = tk.StringVar()  # Initialize an entry field for the source directory
source_entry.set("")  # Set the default value of the entry field
source_entry_label = tk.Label(source_frame, textvariable=source_entry, anchor='w', width=40)  # Create a label for the entry field
source_entry_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 8))  # Pack the label

target_frame = tk.Frame(root)  # Create a frame for the target directory
target_frame.pack(fill=tk.X, padx=10, pady=(4, 8))  # Pack the frame

select_target_button = tk.Button(target_frame, text="Select Target Directory", command=select_target_directory)  # Create a button to select the target directory
select_target_button.pack(side=tk.LEFT, padx=(0, 6), pady=(0, 8))  # Pack the button

target_label = tk.Label(target_frame, text="Target Directory:")  # Create a label for the target directory
target_label.pack(side=tk.LEFT, pady=(0, 8))  # Pack the label

target_entry = tk.StringVar()  # Initialize an entry field for the target directory
target_entry.set("")  # Set the default value of the entry field
target_entry_label = tk.Label(target_frame, textvariable=target_entry, anchor='w', width=40)  # Create a label for the entry field
target_entry_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 8))  # Pack the label

filter_entry = tk.Entry(root, highlightthickness=1, bd=1)  # Create an entry field for filtering files
filter_entry.pack(fill=tk.X, padx=16, pady=(4, 0))  # Pack the entry field
filter_entry.bind("<KeyRelease>", on_filter_text_changed)  # Bind a function to the key release event

files_frame = tk.Frame(root)  # Create a frame for the list of files
files_frame.pack(padx=10, fill=tk.BOTH, expand=True)  # Pack the frame

scrollbar = tk.Scrollbar(files_frame, orient="vertical", width=12, bg="light gray")  # Create a scrollbar
scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=6)  # Pack the scrollbar

canvas = tk.Canvas(files_frame, yscrollcommand=scrollbar.set, highlightthickness=0)  # Create a canvas
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=8)  # Pack the canvas
scrollbar.config(command=canvas.yview)  # Configure the scrollbar

canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))  # Bind a function to the configure event
canvas.bind_all("<MouseWheel>", on_mousewheel)  # Bind a function to mouse wheel events

checkbutton_frame = tk.Frame(canvas)  # Create a frame for the checkbuttons
canvas.create_window((0, 0), window=checkbutton_frame, anchor='nw')  # Pack the frame

transfer_button_frame = tk.Frame(root)  # Create a frame for the transfer button
transfer_button_frame.pack(side=tk.BOTTOM, pady=8)  # Pack the frame

transfer_button = tk.Button(transfer_button_frame, text="Transfer Files", command=transfer_files)  # Create a button to transfer files
transfer_button.pack(pady=6)  # Pack the button

update_checkbuttons()  # Update the checkbuttons initially
root.mainloop()  # Start the main event loop