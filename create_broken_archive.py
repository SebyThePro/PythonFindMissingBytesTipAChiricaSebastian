import sys
import os
import hashlib
import zipfile

def calculate_file_hash(zip_path):
    """
    Opens the valid ZIP, extracts the first file in memory, 
    and calculates its SHA256 hash.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            first_file_name = zf.namelist()[0]
            
            with zf.open(first_file_name) as f:
                data = f.read()
                # Calculate SHA256
                sha256 = hashlib.sha256(data).hexdigest()
                return sha256, first_file_name
    except Exception as e:
        print(f"Error reading valid zip: {e}")
        sys.exit(1)

def truncate_file(input_path, output_path, bytes_to_remove):
    """
    Reads the raw binary data of the zip and removes the last N bytes.
    """
    file_size = os.path.getsize(input_path)
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    #Remove last bytes
    truncated_data = data[:-bytes_to_remove]
    
    with open(output_path, 'wb') as f:
        f.write(truncated_data)
        
    print(f"Original Size: {file_size} bytes")
    print(f"New Size:      {len(truncated_data)} bytes")
    print(f"Removed:       {bytes_to_remove} bytes")

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_broken_archive.py <valid_zip_file> [bytes_to_remove]")
        sys.exit(1)

    input_zip = sys.argv[1]
    # removing 4 bytes if not specified
    bytes_to_remove = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    output_zip = "broken.zip"

    if not os.path.exists(input_zip):
        print(f"File not found: {input_zip}")
        sys.exit(1)

    print("Analyzing valid archive...")
    expected_hash, inner_filename = calculate_file_hash(input_zip)
    print(f"Target File Inside: {inner_filename}")
    print(f"Expected Hash:      {expected_hash}")

    print("\nCreating broken archive...")
    truncate_file(input_zip, output_zip, bytes_to_remove)
    print(f"Saved to: {output_zip}")

    print("\n TEST COMMAND...")
    print(f"comand:")
    print(f"python main.py {output_zip} {expected_hash}")

if __name__ == "__main__":
    main()