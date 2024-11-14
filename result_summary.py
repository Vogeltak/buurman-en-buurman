import json
import argparse
from collections import defaultdict

def process_jsonl(filepath):
    response_counts = defaultdict(int)
    total_entries = 0
    
    with open(filepath, 'r') as file:
        for line in file:
            try:
                entry = json.loads(line)
                response_text = entry['response']['candidates'][0]['content']['parts'][0]['text']
                response_data = json.loads(response_text)
                
                result_key = (response_data['pat'], response_data['mat'])
                response_counts[result_key] += 1
                total_entries += 1
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing line: {e}")
                continue
    
    print(f"\nTotal entries processed: {total_entries}")
    print("\nResponse distribution:")
    for (pat, mat), count in sorted(response_counts.items()):
        percentage = (count / total_entries) * 100 if total_entries > 0 else 0
        print(f"Pat: {pat}, Mat: {mat} - Count: {count} ({percentage:.2f}%)")
    
    return response_counts

def main():
    parser = argparse.ArgumentParser(description='Process JSONL file containing Pat & Mat detection results')
    parser.add_argument('filepath', help='Path to the JSONL file to process')
    args = parser.parse_args()
    
    try:
        results = process_jsonl(args.filepath)
    except FileNotFoundError:
        print(f"Error: File '{args.filepath}' not found")
        exit(1)
    except PermissionError:
        print(f"Error: Permission denied accessing file '{args.filepath}'")
        exit(1)

if __name__ == "__main__":
    main()
