import os
import csv
from pathlib import Path
import logging

def setup_logging():
    """Configure logging to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('file_renaming.log'),
            logging.StreamHandler()
        ]
    )

def load_csv(csv_path):
    """
    Load the CSV file containing the title mappings.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        list: List of tuples containing (nr, title)
    """
    try:
        mappings = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip rows where nr or title is missing
                if not row['nr'] or not row['title']:
                    continue
                    
                # Pad the number with leading zeros
                nr = str(row['nr']).strip().zfill(2)
                title = row['title'].strip()
                mappings.append((nr, title))
        return mappings
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise

def rename_files(directory_path, csv_path):
    """
    Rename files in the specified directory based on the CSV mapping.
    
    Args:
        directory_path (str): Path to the directory containing files to rename
        csv_path (str): Path to the CSV file containing the mapping
    """
    setup_logging()
    logging.info(f"Starting file renaming process in {directory_path}")
    
    try:
        # Load the CSV data
        mappings = load_csv(csv_path)
        directory = Path(directory_path)
        
        # Keep track of processed files to avoid double renaming
        processed_files = set()
        
        # Iterate through each file in the directory
        for file_path in directory.glob('*'):
            if file_path.is_file():
                original_name = file_path.name.lower()
                
                # Check each title from the CSV
                for nr, title in mappings:
                    title_lower = title.lower()
                    
                    # If the title is found in the filename
                    if title_lower in original_name and file_path.name not in processed_files:
                        # Get the file extension
                        ext = file_path.suffix
                        
                        # Create the new filename
                        new_name = f"{nr}_{title}{ext}"
                        new_path = file_path.parent / new_name
                        
                        try:
                            # Rename the file
                            file_path.rename(new_path)
                            processed_files.add(new_name)
                            logging.info(f"Renamed '{file_path.name}' to '{new_name}'")
                        except Exception as e:
                            logging.error(f"Error renaming {file_path.name}: {e}")
        
        logging.info("File renaming process completed")
        
    except Exception as e:
        logging.error(f"An error occurred during the renaming process: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Rename files based on CSV mapping.')
    parser.add_argument('directory', help='Directory containing files to rename')
    parser.add_argument('csv_file', help='Path to the CSV file with title mappings')
    
    args = parser.parse_args()
    
    rename_files(args.directory, args.csv_file)
