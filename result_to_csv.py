import json
import csv
from typing import Dict, List
import argparse
from pathlib import Path

def parse_jsonl_line(line: str) -> Dict:
    """
    Parse a single JSONL line and extract relevant information.
    
    Args:
        line (str): A single line from the JSONL file
        
    Returns:
        Dict: Dictionary containing frame label and parsed pat/mat values
    """
    try:
        data = json.loads(line)
        
        # Extract frame label
        frame = data['request']['labels']['frame']
        
        # Extract and parse the JSON response
        response_text = data['response']['candidates'][0]['content']['parts'][0]['text']
        response_data = json.loads(response_text)
        
        return {
            'frame': frame,
            'pat': response_data['pat'],
            'mat': response_data['mat']
        }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing line: {e}")
        return None

def process_jsonl_file(input_file: str, output_file: str):
    """
    Process the entire JSONL file and create a CSV output.
    
    Args:
        input_file (str): Path to input JSONL file
        output_file (str): Path to output CSV file
    """
    results: List[Dict] = []
    
    # Read and process JSONL file
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            try:
                result = parse_jsonl_line(line.strip())
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing line {line_number}: {e}")
    
    # Write results to CSV
    if results:
        fieldnames = ['frame', 'pat', 'mat']
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} entries to {output_file}")
    else:
        print("No valid entries found to write to CSV")

def main():
    parser = argparse.ArgumentParser(description='Process JSONL file to CSV')
    parser.add_argument('input_file', help='Path to input JSONL file')
    parser.add_argument('output_file', help='Path to output CSV file')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input_file).is_file():
        print(f"Error: Input file '{args.input_file}' does not exist")
        return
    
    process_jsonl_file(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
