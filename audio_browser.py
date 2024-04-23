import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# Function to scan directory for audio files
def scan_directory(directory):
  audio_files = []
  for root, _, files in os.walk(directory):
    for file in files:
      if file.endswith(('.mp3', '.wav')):
        audio_files.append(os.path.join(root, file))
  return audio_files

# Function to handle directory selection for source directory
def select_source_directory():
  global audio_files_list
  directory = filedialog.askdirectory()
  if directory:
    audio_files_list = scan_directory(directory)
    update_checkbuttons()

# Function to handle directory selection for target directory
def select_target_directory():
  directory = filedialog.askdirectory()
  if directory:
    target_entry.set(directory)

# Function to handle file transfer
def transfer_files():
  selected_files = []
  for i, var in enumerate(checkvars):
    if var.get():
      selected_files.append(audio_files_list[i])
   
  if not selected_files:
    tk.messagebox.showerror("Error", "No files selected for transfer.")
    return

  target_dir = target_entry.get()
  if not target_dir:
    tk.messagebox.showerror("Error", "No target directory selected.")
    return

  for file in selected_files:
    shutil.copy(file, target_dir)
   
  tk.messagebox.showinfo("Success", "Files transferred successfully.")

# Function to update checkbuttons with audio files
def update_checkbuttons():
    # Clear existing checkbuttons (if any)
    for widget in checkbutton_frame.winfo_children():
        widget.destroy()

    checkvars.clear()  # Clear associated checkvar list

    # Create and pack checkbuttons within the scrollable frame
    for i, file in enumerate(audio_files_list):
        var = tk.IntVar()
        checkbutton = ttk.Checkbutton(checkbutton_frame, text=os.path.basename(file), variable=var)
        checkbutton.pack(fill=tk.X, anchor=tk.W)
        checkvars.append(var)

    # Update scroll region to ensure all content is visible
    canvas.update_idletasks()  # Update the canvas
    canvas.configure(scrollregion=canvas.bbox('all'))  # Update scroll region

# Make the canvas scrollable
# GUI setup
root = tk.Tk()
root.title("Audio Browser")

# Source directory selection button
source_frame = tk.Frame(root)
source_frame.pack(padx=10, pady=10)
select_source_button = tk.Button(source_frame, text="Select Source Directory", command=select_source_directory)
select_source_button.pack(side=tk.LEFT)

# Target directory selection button
target_frame = tk.Frame(root)
target_frame.pack(padx=10, pady=5)
select_target_button = tk.Button(target_frame, text="Select Target Directory", command=select_target_directory)
select_target_button.pack(side=tk.LEFT)

# Label for target directory
target_label = tk.Label(root, text="Target Directory:")
target_label.pack(pady=(5,0))

# Entry for displaying selected target directory
target_entry = tk.StringVar()
target_entry.set("")
target_entry_label = tk.Label(root, textvariable=target_entry)
target_entry_label.pack(pady=(0,10), padx=10, fill=tk.X)

# Frame to hold checkbuttons
frame = tk.Frame(root)
frame.pack(padx=10, pady=(0,5))

# Add a scrollbar
scrollbar = tk.Scrollbar(frame, orient="vertical")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the canvas
canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add the scrollbar to the canvas
scrollbar.config(command=canvas.yview)

# Make the canvas scrollable
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

# Create another frame inside the canvas (already done in previous part)
checkbutton_frame = tk.Frame(canvas)

# Add that new frame to a window in the canvas (already done in previous part)
canvas.create_window((0,0), window=checkbutton_frame, anchor='nw')

# List of check variables (already initialized in previous part)
checkvars = []

# Transfer button
transfer_button = tk.Button(root, text="Transfer Files", command=transfer_files)
transfer_button.pack(pady=(0,10))

# Global variables
audio_files_list = []
update_checkbuttons()

# Start the GUI main loop
root.mainloop()