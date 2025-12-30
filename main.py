import argparse
import os
import sys
import logging

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("FindMissingBytes")

def configure_cli():
    """
    Configures and parses command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="FindMissingBytes: Tool for repairing truncated ZIP archives."
    )
    
    # Path to the file
    parser.add_argument(
        "filename", 
        type=str, 
        help="Path to the truncated/broken ZIP archive."
    )
    
    # Expected Hash (SHA256)
    parser.add_argument(
        "expected_hash", 
        type=str, 
        help="The expected SHA256 hash of the extracted file."
    )

    return parser.parse_args()

def validate_environment(args):
    """
    Validates the input arguments.
    Returns True or False.
    """
    
    # Check : Does the file exist?
    if not os.path.exists(args.filename):
        logger.error(f"File not found: {args.filename}")
        return False
        
    # Check : Is the file empty?
    if os.path.getsize(args.filename) == 0:
        logger.error(f"File {args.filename} is empty (0 bytes).")
        return False

    # Check : Is the hash length correct? 
    if len(args.expected_hash) != 64:
        logger.warning(f"Warning: The provided hash has {len(args.expected_hash)} characters.")

    logger.info("Validatin successful. Inputs are ready.")
    return True

def main():
    logger.info("=== FindMissingBytes Start ===")
    
    args = configure_cli()
    
    if not validate_environment(args):
        logger.error("Forced exit due to validation errors.")
        sys.exit(1)

    logger.info(f"Target File: {args.filename}")
    logger.info(f"Expected Hash: {args.expected_hash}")
    logger.info("System ready for Phase 2 (Truncation Simulation).")

if __name__ == "__main__":
    main()