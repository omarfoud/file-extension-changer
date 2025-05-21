import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os
import shutil # For copying the file

class FileExtensionChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Extension Changer (Rename Only)")
        self.root.geometry("550x280") # Adjusted size

        self.selected_file_path = tk.StringVar()
        self.original_extension = tk.StringVar() # Store original extension for comparison
        self.new_extension = tk.StringVar()
        self.status_message = tk.StringVar()
        self.status_message.set("Please select a file.")

        # --- Define Common Extensions ---
        # You can customize this list extensively
        self.common_extensions = sorted([
            # Images
            "jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "svg",
            # Documents
            "txt", "rtf", "doc", "docx", "odt", "pdf", "xls", "xlsx", "ods",
            "ppt", "pptx", "odp", "csv",
            # Audio
            "mp3", "wav", "ogg", "flac", "aac", "m4a",
            # Video
            "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm",
            # Archives
            "zip", "rar", "7z", "tar", "gz",
            # Code/Text
            "py", "js", "html", "css", "json", "xml", "md", "java", "c", "cpp",
            # Other
            "exe", "dll", "iso", "bin"
        ])

        # --- GUI Elements ---
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File Selection Row
        ttk.Label(main_frame, text="Selected File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_label = ttk.Label(main_frame, textvariable=self.selected_file_path, relief="sunken", padding=5, width=45)
        self.file_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.selected_file_path.set("No file selected")

        self.upload_button = ttk.Button(main_frame, text="Upload File", command=self.select_file)
        self.upload_button.grid(row=0, column=2, padx=5, pady=5)

        # Original Extension (Read-only display)
        ttk.Label(main_frame, text="Original Ext:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.orig_ext_label = ttk.Label(main_frame, textvariable=self.original_extension, relief="flat", padding=(5,0))
        self.orig_ext_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.original_extension.set("N/A")

        # New Extension Row (Combobox)
        ttk.Label(main_frame, text="Choose New Ext:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ext_combobox = ttk.Combobox(
            main_frame,
            textvariable=self.new_extension,
            values=self.common_extensions,
            state="readonly", # Prevent typing custom extensions
            width=15
        )
        self.ext_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        # Optional: Set a default selection if desired
        # self.new_extension.set(self.common_extensions[0]) # Set default to first in list
        self.ext_combobox.bind("<<ComboboxSelected>>", self.check_enable_save) # Enable save on selection

        # Download/Save Button
        self.download_button = ttk.Button(main_frame, text="Change Extension & Save As...", command=self.change_and_save, state=tk.DISABLED)
        self.download_button.grid(row=3, column=0, columnspan=3, padx=5, pady=15)

        # Status Bar
        status_bar = ttk.Label(root, textvariable=self.status_message, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure grid weights for resizing
        main_frame.columnconfigure(1, weight=1)

    def get_file_extension(self, file_path):
        """Safely extracts the file extension in lowercase, without the dot."""
        if not file_path or file_path == "No file selected":
            return ""
        try:
            _, ext = os.path.splitext(file_path)
            return ext.lower().lstrip('.') # Remove leading dot and make lowercase
        except Exception:
            return "" # Return empty string on error

    def select_file(self):
        """Opens a file dialog to select a file."""
        file_path = filedialog.askopenfilename(title="Select a File")
        if file_path:
            self.selected_file_path.set(file_path)
            orig_ext = self.get_file_extension(file_path)
            self.original_extension.set(f".{orig_ext}" if orig_ext else "None")
            self.status_message.set(f"Selected: {os.path.basename(file_path)}")
            # Don't enable save button yet, user needs to choose an extension
            self.check_enable_save()
        else:
            # Reset if dialog is cancelled and no file was previously selected
            if not self.selected_file_path.get() or self.selected_file_path.get() == "No file selected":
                 self.selected_file_path.set("No file selected")
                 self.original_extension.set("N/A")
                 self.status_message.set("File selection cancelled.")
                 self.download_button.config(state=tk.DISABLED)

    def check_enable_save(self, event=None):
         """Enable save button only if a file is selected AND an extension is chosen."""
         file_selected = self.selected_file_path.get() and self.selected_file_path.get() != "No file selected"
         ext_selected = bool(self.new_extension.get()) # Checks if the stringvar is not empty

         if file_selected and ext_selected:
             self.download_button.config(state=tk.NORMAL)
         else:
             self.download_button.config(state=tk.DISABLED)


    def change_and_save(self):
        """Shows warning, prompts user for save location, copies file with new extension."""
        original_path = self.selected_file_path.get()
        if not original_path or original_path == "No file selected":
            messagebox.showerror("Error", "Please select a file first.")
            return

        new_ext = self.new_extension.get() # Already validated by combobox selection
        if not new_ext:
            messagebox.showerror("Error", "Please choose a new extension from the list.")
            return

        original_ext_str = self.original_extension.get().lstrip('.') # Get original without dot

        # --- WARNING LOGIC ---
        if original_ext_str != new_ext:
            warning_title = "Potential Compatibility Issue"
            warning_message = (
                f"You are changing the file extension from '.{original_ext_str}' to '.{new_ext}'.\n\n"
                "IMPORTANT: This action only RENAMES the file. It does NOT convert the actual file content or format.\n\n"
                f"Opening the renamed file with software expecting a '.{new_ext}' format may fail, show errors, or display corrupted data.\n\n"
                "Do you want to proceed with renaming?"
            )
            # Ask the user to confirm
            proceed = messagebox.askyesno(warning_title, warning_message, icon='warning')
            if not proceed:
                self.status_message.set("Save operation cancelled by user due to warning.")
                return # Stop the function if user selects "No"
        # --- End Warning Logic ---

        try:
            # Prepare suggested filename for the save dialog
            directory = os.path.dirname(original_path)
            base_name_no_ext = os.path.splitext(os.path.basename(original_path))[0]
            suggested_filename = f"{base_name_no_ext}.{new_ext}"

            # Ask user where to save the new file
            save_path = filedialog.asksaveasfilename(
                initialdir=directory,
                initialfile=suggested_filename,
                defaultextension=f".{new_ext}",
                title="Save File As (Rename Only)",
                filetypes=[(f"{new_ext.upper()} files", f"*.{new_ext}"), ("All files", "*.*")]
            )

            if save_path:
                # Ensure the final save path has the correct selected extension
                # asksaveasfilename might not add it if the user manually types a name without one
                # or selects "All files" and doesn't type an extension.
                final_save_path_base, final_save_path_ext = os.path.splitext(save_path)
                if final_save_path_ext.lower().lstrip('.') != new_ext.lower():
                   save_path = f"{final_save_path_base}.{new_ext}"

                # Copy the original file to the new path
                shutil.copy2(original_path, save_path) # copy2 preserves metadata
                self.status_message.set(f"File renamed and saved as: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", f"File successfully renamed and saved as:\n{save_path}")
            else:
                self.status_message.set("Save operation cancelled.")

        except Exception as e:
            self.status_message.set(f"Error during save: {e}")
            messagebox.showerror("Error", f"An error occurred during saving:\n{e}")

# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FileExtensionChangerApp(root)
    root.mainloop()