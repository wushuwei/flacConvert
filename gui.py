import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from flacHelper import scan_and_convert, convert_audio_to_mp3

class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter to MP3")

        self.source_folder = tk.StringVar()
        self.target_folder = tk.StringVar()

        # Configure style for a more modern look
        style = ttk.Style()
        style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # --- Source Folder Selection ---
        ttk.Label(root, text="Source Folder:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.source_entry = ttk.Entry(root, textvariable=self.source_folder, width=50, state='readonly')
        self.source_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(root, text="Browse...", command=self.browse_source).grid(row=0, column=2, padx=5, pady=5)

        # --- Target Folder Selection ---
        ttk.Label(root, text="Target Folder:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = ttk.Entry(root, textvariable=self.target_folder, width=50, state='readonly')
        self.target_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(root, text="Browse...", command=self.browse_target).grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(root, text="If no target is selected, '[source_folder_name]_mp3' will be created next to the source.",
                  font=('TkDefaultFont', 8)).grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)

        # --- Start Conversion Button ---
        self.start_button = ttk.Button(root, text="Start Conversion", command=self.start_conversion)
        self.start_button.grid(row=3, column=1, padx=5, pady=10)
        
        # --- Progress Bar (Optional but good for UX) ---
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        # --- Status Message Area ---
        self.status_label = ttk.Label(root, text="Select source and target folders to start.")
        self.status_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # Configure column weights for responsive resizing
        root.columnconfigure(1, weight=1)

    def browse_source(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.source_folder.set(folder_selected)
            self.status_label.config(text="Source folder selected. Select target folder or start.")
            # Clear target if source changes, to re-trigger default logic if needed
            self.target_folder.set("") 
            self.status_label.config(text="Source folder selected. Target will be auto-generated or select one.")


    def browse_target(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.target_folder.set(folder_selected)
            self.status_label.config(text="Target folder selected. Ready to start.")

    def start_conversion(self):
        source = self.source_folder.get()
        target = self.target_folder.get()
        
        if not source:
            messagebox.showerror("Error", "Source folder must be selected.")
            self.status_label.config(text="Source folder selection is required.")
            return

        if not target:
            source_name = os.path.basename(os.path.normpath(source)) # Get 'folder_name' from 'path/to/folder_name/'
            default_target_name = f"{source_name}_mp3"
            target = os.path.join(os.path.dirname(source), default_target_name)
            self.target_folder.set(target) # Update the GUI
            self.status_label.config(text=f"Target folder set to: {target}")

        try:
            os.makedirs(target, exist_ok=True)
            self.status_label.config(text=f"Starting conversion... Output: {target}")
            self.start_button.config(state=tk.DISABLED)
            self.progress_var.set(0) # Reset progress
            self.root.update_idletasks() # Ensure UI updates

            # This is a simplified progress update.
            # For real progress, scan_and_convert would need to yield progress.
            # Here, we'll just simulate it or update after it's done.
            
            scan_and_convert(source, target) # This is a blocking call

            # Simulate progress for now
            self.progress_var.set(100) 
            messagebox.showinfo("Success", f"Conversion complete!\nFiles saved to: {target}")
            self.status_label.config(text="Conversion complete! Select folders to start again.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during conversion: {e}")
            self.status_label.config(text=f"Error: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.progress_var.set(0) # Reset progress bar


if __name__ == '__main__':
    root = tk.Tk()
    app = AudioConverterApp(root)
    root.mainloop()
