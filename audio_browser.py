import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def select_source_directory():
    directory = filedialog.askdirectory()
    if directory:
        source_entry.set(directory)
        threading.Thread(target=scan_and_update, args=(directory,)).start()

def scan_directory(directory):
    audio_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.wav')):
                audio_files.append(os.path.join(root, file))
    return audio_files

def scan_and_update(directory):
    global audio_files_list
    audio_files_list = scan_directory(directory)
    update_checkbuttons()

def select_target_directory():
    directory = filedialog.askdirectory()
    if directory:
        target_entry.set(directory)

def transfer_files():
    selected_files = [audio_files_list[i] for i, var in enumerate(checkvars) if var.get()]

    if not selected_files:
        messagebox.showerror("Error", "No files selected for transfer.")
        return

    target_dir = target_entry.get()
    if not target_dir:
        messagebox.showerror("Error", "No target directory selected.")
        return

    for file in selected_files:
        shutil.copy(file, target_dir)

    messagebox.showinfo("Success", "Files transferred successfully.")

def update_checkbuttons():
    for widget in checkbutton_frame.winfo_children():
        widget.destroy()

    checkvars.clear()

    filter_text = filter_entry.get().lower()

    filtered_files = [file for file in audio_files_list if filter_text in os.path.basename(file).lower()]

    for i, file in enumerate(filtered_files):
        var = tk.IntVar()
        checkbutton = ttk.Checkbutton(checkbutton_frame, text=os.path.basename(file), variable=var)
        checkbutton.pack(fill=tk.X, anchor=tk.W, padx=6, pady=1)
        checkvars.append(var)

    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox('all'))

    if len(filtered_files) > 0:
        frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=(4, 8))
    else:
        frame.pack_forget()

def on_mousewheel(event):
    if event.delta < 0:
        canvas.yview_scroll(1, "units")
    elif event.delta > 0:
        canvas.yview_scroll(-1, "units")

def on_filter_text_changed(event):
    update_checkbuttons()

root = tk.Tk()
root.title("Audio Browser")

source_frame = tk.Frame(root)
source_frame.pack(fill=tk.X, padx=10, pady=(8, 4))
select_source_button = tk.Button(source_frame, text="Select Source Directory", command=select_source_directory)
select_source_button.pack(side=tk.LEFT, padx=(0, 6), pady=(0, 8))
source_label = tk.Label(source_frame, text="Source Directory:")
source_label.pack(side=tk.LEFT, pady=(0, 8))
source_entry = tk.StringVar()
source_entry.set("")
source_entry_label = tk.Label(source_frame, textvariable=source_entry, anchor='w', width=40)
source_entry_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 8))

target_frame = tk.Frame(root)
target_frame.pack(fill=tk.X, padx=10, pady=(4, 8))
select_target_button = tk.Button(target_frame, text="Select Target Directory", command=select_target_directory)
select_target_button.pack(side=tk.LEFT, padx=(0, 6), pady=(0, 8))
target_label = tk.Label(target_frame, text="Target Directory:")
target_label.pack(side=tk.LEFT, pady=(0, 8))
target_entry = tk.StringVar()
target_entry.set("")
target_entry_label = tk.Label(target_frame, textvariable=target_entry, anchor='w', width=40)
target_entry_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 8))

filter_entry = tk.Entry(root, highlightthickness=1, bd=1)
filter_entry.pack(fill=tk.X, padx=16, pady=(4, 0))
filter_entry.bind("<KeyRelease>", on_filter_text_changed)

frame = tk.Frame(root)
frame.pack(padx=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame, orient="vertical", width=12, bg="light gray")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=6)

canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set, highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=8)

scrollbar.config(command=canvas.yview)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
canvas.bind_all("<MouseWheel>", on_mousewheel)

checkbutton_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=checkbutton_frame, anchor='nw')

checkvars = []

audio_files_list = []
update_checkbuttons()

transfer_button_frame = tk.Frame(root)
transfer_button_frame.pack(side=tk.BOTTOM, pady=8)
transfer_button = tk.Button(transfer_button_frame, text="Transfer Files", command=transfer_files)
transfer_button.pack(pady=6)

root.mainloop()
