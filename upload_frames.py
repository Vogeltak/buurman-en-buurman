from pathlib import Path
from google.cloud.storage import Client, transfer_manager


def upload_frames(bucket_name, frames_dir, frames=None, max_workers=8):
    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)

    if not frames:
        frame_paths = [path for path in Path(frames_dir).rglob("*")]
        relative_paths = [path.relative_to(frames_dir) for path in frame_paths]
        frames = [str(path) for path in relative_paths]

    print(f"Found {len(frames)} frames to upload")

    # TESTING: just upload a few to see if it works
    # frames = frames[:10]

    print(f"Uploading {len(frames)} frames...")

    results = transfer_manager.upload_many_from_filenames(
        bucket, frames, frames_dir, max_workers=max_workers
    )

    for name, result in zip(frames, results):
        if isinstance(result, Exception):
            print("Failed to upload {} due to exception: {}".format(name, result))


if __name__ == "__main__":
    import argparse

    BUCKET_NAME = "buurman-en-buurman-data"
    
    parser = argparse.ArgumentParser(description='Upload frames to Google Cloud Storage')
    parser.add_argument('directory', help='Directory containing i-frames to upload')
    parser.add_argument('--frames', help='Filenames of the frames to upload (comma-separated)')
    
    args = parser.parse_args()

    if args.frames:
        frames = args.frames.split(',')
    
    upload_frames(BUCKET_NAME, args.directory, frames)
