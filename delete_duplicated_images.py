import os
from pathlib import Path
from PIL import Image, ImageTk
import imagehash
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# -------- Settings --------
IMAGE_EXTS = (".jpg", ".jpeg", ".jfif", ".png", ".bmp", ".gif", ".webp")

# -------- Helper functions --------
def get_image_hashes(image_path):
    """Generate different hashes for the image (including flipped and mirrored versions)"""
    try:
        img = Image.open(image_path).convert("RGB")
        base_hash = imagehash.phash(img)
        flipped_hash = imagehash.phash(img.transpose(Image.FLIP_LEFT_RIGHT))
        rotated_hash = imagehash.phash(img.transpose(Image.ROTATE_180))
        return {base_hash, flipped_hash, rotated_hash}
    except Exception:
        return set()

def find_duplicate_images(root_dir):
    """
    Find duplicate images in a directory.
    Uses multiple hashes to detect flipped/mirrored duplicates.
    Returns a list of tuples (original_file, duplicate_file)
    """
    all_files = [p for p in Path(root_dir).rglob("*") if p.suffix.lower() in IMAGE_EXTS]
    hash_map = {}
    duplicates = []

    for file_path in all_files:
        hashes = get_image_hashes(file_path)
        found = False
        for h in hashes:
            if h in hash_map:
                # Only pair with the first file already stored
                duplicates.append((hash_map[h][0], file_path))
                hash_map[h].append(file_path)
                found = True
                break
        if not found:
            for h in hashes:
                hash_map[h] = [file_path]

    return duplicates

# -------- GUI --------
class DuplicateViewer(tk.Tk):
    def __init__(self, duplicates):
        super().__init__()
        self.title("Duplicate Images")
        self.geometry("900x600")

        self.scrollable_frame = None  # store reference for checking emptiness

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.duplicates = duplicates.copy()  # keep a list for checking emptiness

        for i, (f1, f2) in enumerate(duplicates, start=1):
            frame_pair = ttk.Frame(self.scrollable_frame, padding=5)
            frame_pair.pack(fill=tk.X, padx=10, pady=5)

            ttk.Label(frame_pair, text=f"Pair {i}:").grid(row=0, column=0, rowspan=2)

            for j, f in enumerate([f1, f2]):
                try:
                    img = Image.open(f)
                    img.thumbnail((100, 100))
                    tk_img = ImageTk.PhotoImage(img)
                    lbl = ttk.Label(frame_pair, image=tk_img)
                    lbl.image = tk_img
                    lbl.grid(row=0, column=j + 1)
                    ttk.Label(frame_pair, text=f.name).grid(row=1, column=j + 1)
                    
                    # Delete button removes the frame and checks if all duplicates are gone
                    btn = ttk.Button(
                        frame_pair, text="🗑 Delete",
                        command=lambda file=f, fr=frame_pair: self.delete_and_remove(file, fr)
                    )
                    btn.grid(row=2, column=j + 1)
                except Exception:
                    ttk.Label(frame_pair, text=f.name).grid(row=1, column=j + 1)

    def delete_and_remove(self, path, frame):
        try:
            os.remove(path)
            frame.destroy()  # remove the pair from the GUI
            # Remove the pair from duplicates list
            self.duplicates = [pair for pair in self.duplicates if path not in pair]
            messagebox.showinfo("Deleted", f"File {path.name} was deleted.")

            # If all pairs are gone, show a final message and close the window
            if not self.duplicates:
                messagebox.showinfo("Done", "All duplicate images have been deleted.")
                self.destroy()  # Close the window automatically

        except Exception as e:
            messagebox.showerror("Error", str(e))

# -------- Main --------
if __name__ == "__main__":
    folder = filedialog.askdirectory(title="Select a folder to scan")
    if folder:
        print("⏳ Scanning folder... This may take some time.")
        duplicates = find_duplicate_images(folder)
        if duplicates:
            print(f"Found {len(duplicates)} pairs of duplicate images.")
            app = DuplicateViewer(duplicates)
            app.mainloop()
        else:
            print("✅ No duplicate images found.")
            messagebox.showinfo("Done", "No duplicate images found.")
