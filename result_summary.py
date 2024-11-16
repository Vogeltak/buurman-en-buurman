import json
import argparse
import re
import csv
from collections import defaultdict
from pathlib import Path

def extract_episode_number(filename):
    match = re.match(r'(\d+)_', filename)
    if match:
        return match.group(1)
    return 'unknown'

def export_to_csv(episode_responses, episode_totals, output_file):
    # Get all unique combinations of (pat, mat) across all episodes
    all_combinations = set()
    for ep_responses in episode_responses.values():
        all_combinations.update(ep_responses.keys())
    
    # Prepare CSV headers
    headers = ['episode', 'total_frames']
    for pat, mat in sorted(all_combinations):
        headers.append(f'pat_{pat}_mat_{mat}_count')
        headers.append(f'pat_{pat}_mat_{mat}_percentage')
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        # Write data for each episode
        for episode in sorted(episode_responses.keys()):
            row = {
                'episode': episode,
                'total_frames': episode_totals[episode]
            }
            
            # Fill in counts and percentages for each combination
            for pat, mat in sorted(all_combinations):
                count = episode_responses[episode].get((pat, mat), 0)
                percentage = (count / episode_totals[episode] * 100) if episode_totals[episode] > 0 else 0
                
                row[f'pat_{pat}_mat_{mat}_count'] = count
                row[f'pat_{pat}_mat_{mat}_percentage'] = f'{percentage:.2f}'
            
            writer.writerow(row)

def process_jsonl(filepath, csv_output=None):
    episode_responses = defaultdict(lambda: defaultdict(int))
    episode_totals = defaultdict(int)
    
    with open(filepath, 'r') as file:
        for line in file:
            try:
                entry = json.loads(line)
                frame_filename = entry['request']['labels']['frame']
                episode = extract_episode_number(frame_filename)
                
                response_text = entry['response']['candidates'][0]['content']['parts'][0]['text']
                response_data = json.loads(response_text)
                
                result_key = (response_data['pat'], response_data['mat'])
                episode_responses[episode][result_key] += 1
                episode_totals[episode] += 1
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing line: {e}")
                continue
    
    # Print results
    grand_total = sum(episode_totals.values())
    print(f"\nTotal entries processed: {grand_total}")
    
    for episode in sorted(episode_responses.keys()):
        total_ep = episode_totals[episode]
        print(f"\nEpisode {episode}:")
        print(f"Total frames: {total_ep}")
        
        for (pat, mat), count in sorted(episode_responses[episode].items()):
            percentage = (count / total_ep) * 100 if total_ep > 0 else 0
            print(f"  Pat: {pat}, Mat: {mat} - Count: {count} ({percentage:.2f}%)")
    
    print("\nOverall Distribution:")
    overall_counts = defaultdict(int)
    for ep_responses in episode_responses.values():
        for result_key, count in ep_responses.items():
            overall_counts[result_key] += count
            
    for (pat, mat), count in sorted(overall_counts.items()):
        percentage = (count / grand_total) * 100 if grand_total > 0 else 0
        print(f"Pat: {pat}, Mat: {mat} - Count: {count} ({percentage:.2f}%)")
    
    # Export to CSV if requested
    if csv_output:
        export_to_csv(episode_responses, episode_totals, csv_output)
        print(f"\nResults exported to: {csv_output}")
    
    return episode_responses

def main():
    parser = argparse.ArgumentParser(description='Process JSONL file containing Pat & Mat detection results')
    parser.add_argument('filepath', help='Path to the JSONL file to process')
    parser.add_argument('--csv', help='Export results to specified CSV file')
    args = parser.parse_args()
    
    try:
        results = process_jsonl(args.filepath, args.csv)
    except FileNotFoundError:
        print(f"Error: File '{args.filepath}' not found")
        exit(1)
    except PermissionError:
        print(f"Error: Permission denied accessing file '{args.filepath}'")
        exit(1)

if __name__ == "__main__":
    main()
