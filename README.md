🖼️ Find Duplicate Images

A Python tool that scans a folder for duplicate or mirrored images and allows you to view and delete duplicates easily via a simple Tkinter GUI.

🚀 Features
Detects identical, flipped, or rotated image duplicates
Supports popular formats: .jpg, .jpeg, .png, .gif, .bmp, .webp, .jfif
Provides a graphical interface for viewing duplicates side by side and deleting 

🧩 Requirements
Make sure you have Python 3.8+ installed, then install dependencies:
pip install pillow imagehash

🗂️ Usage
Run the script:
python delete_duplicated_images.py

🧠 How It Works
Each image is hashed using perceptual hashing (phash) from the imagehash library.
It also computes hashes for flipped and rotated versions to catch mirrored duplicates.
If two images share the same hash (or any of their flipped versions do), they are marked as duplicates.

👨‍💻 Author
Developed by Narkis Shallev

A simple yet effective tool for keeping your photo collections clean and duplicate-free.
