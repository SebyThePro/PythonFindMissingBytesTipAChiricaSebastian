import argparse
import os
import sys
import logging
import itertools
import zipfile
import io
import hashlib
from multiprocessing import Pool, cpu_count, freeze_support
from tqdm import tqdm 

#Config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("FindMissingBytes")

def solve_chunk(args):
    """
    Worker function executed by each CPU core.
    """
    broken_data, prefix_tuple, missing_len, expected_hash = args
    
    remaining_len = missing_len - len(prefix_tuple)
    
    for suffix in itertools.product(range(256), repeat=remaining_len):
        
        full_tail_tuple = prefix_tuple + suffix
        tail_bytes = bytes(full_tail_tuple)
        
        candidate_data = broken_data + tail_bytes
        
        virtual_file = io.BytesIO(candidate_data)
        
        try:
            with zipfile.ZipFile(virtual_file, 'r') as zf:
                
                if zf.testzip() is not None:
                    continue
                
                target_name = zf.namelist()[0]
                with zf.open(target_name) as f:
                    content = f.read()
                    current_hash = hashlib.sha256(content).hexdigest()
                    
                    if current_hash == expected_hash:
                        return tail_bytes
                        
        except (zipfile.BadZipFile, RuntimeError):
            continue
            
    return None

def main():
    freeze_support()
    
    parser = argparse.ArgumentParser(description="FindMissingBytes: Parallel ZIP Repair Tool")
    parser.add_argument("filename", help="Path to broken ZIP")
    parser.add_argument("expected_hash", help="SHA256 of the valid extracted file")
    parser.add_argument("--bytes", type=int, default=4, help="Number of missing bytes to guess (Default: 4)")
    
    args = parser.parse_args()
    
    #Validation
    if not os.path.exists(args.filename):
        logger.error("File not found.")
        sys.exit(1)

    logger.info(f"Loading {args.filename} into RAM...")
    with open(args.filename, 'rb') as f:
        broken_data = f.read()
    
    MISSING_LEN = args.bytes
    logger.info(f"Attempting to brute-force {MISSING_LEN} bytes.")
    logger.info(f"CPU Cores available: {cpu_count()}")
    
    # Format: (data, (start_byte,), total_len, target_hash)
    tasks = [
        (broken_data, (start_byte,), MISSING_LEN, args.expected_hash) 
        for start_byte in range(256)
    ]
    
    logger.info("Starting Parallel Engine... (Press Ctrl+C to abort)")
    
    found_tail = None
    
    with Pool(processes=cpu_count()) as pool:
        for result in tqdm(pool.imap_unordered(solve_chunk, tasks), total=len(tasks), unit="chunk"):
            if result:
                found_tail = result
                pool.terminate() 
                break
    
    if found_tail:
        print("\n" + "="*40)
        logger.info(f"SUCCES! MATCH FOUND.")
        logger.info(f"Recovered Bytes (Hex): {found_tail.hex()}")
        
        recovered_filename = "recovered_" + os.path.basename(args.filename)
        with open(recovered_filename, 'wb') as f:
            f.write(broken_data + found_tail)
        logger.info(f"Saved recovered archive to: {recovered_filename}")
        print("="*40)
    else:
        logger.error("Failed to find the missing bytes.")

if __name__ == "__main__":
    main()