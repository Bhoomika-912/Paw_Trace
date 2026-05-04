import hashlib
import os

def calculate_hash(file_path):
    hash_obj = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except FileNotFoundError:
        return None

# Get file from user
file_path = input("Enter file path: ")

# First hash (original)
original_hash = calculate_hash(file_path)

if original_hash is None:
    print("File not found!")
else:
    print("\nOriginal Hash:", original_hash)

    input("\nPress Enter after modifying the file...")

    # New hash
    new_hash = calculate_hash(file_path)

    print("\nNew Hash:", new_hash)

    # Compare
    if original_hash == new_hash:
        print("✅ File is SAFE (No changes detected)")
    else:
        print("🚨 ALERT: File has been MODIFIED!")