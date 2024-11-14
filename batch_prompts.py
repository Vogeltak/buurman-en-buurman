import json
from pathlib import Path
from google.cloud.storage import Client, transfer_manager


BUCKET_NAME = "buurman-en-buurman-data"
REQUEST_TEMPLATE = {
    "request": {
        # TEMPLATE: add a field data object of the "fileData" type, pointing to
        # the frame URI in Google Cloud Storage (i.e., gs://bucket-name/frame-file.jpg)
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": "Determine who is in this frame from the animated series Pat & Mat. Pat wears yellow and Mat wears grey or red. Respond only with a valid JSON object following this schema:\n\n```{\"pat\": boolean,\"mat\": boolean}```"
                    }
                ]
            }
        ],
        # "systemInstruction": {
        #     "role": "user",
        #     "parts": [
        #         {
        #             "text": "Determine who is in this frame from the animated series Pat & Mat. Pat wears yellow and Mat wears grey or red. Respond only with a valid JSON object following this schema:\n\n```{\"pat\": boolean,\"mat\": boolean}```"
        #         }
        #     ]
        # },
        "generationConfig": {
          "temperature": 1,
          "top_p": 0.95,
          "top_k": 40,
          "max_output_tokens": 8192,
          "response_mime_type": "application/json",
        },
        # TEMPLATE: fill with key-value pair for identification; "frame": {id}
        "labels": {}
    }
}


def generate_prompts(frames_dir, target_jsonl="batch_prompts.jsonl"):
    frames = [str(path.relative_to(frames_dir)) for path in Path(frames_dir).rglob("*")]

    lines = []

    for frame in frames:
        req = REQUEST_TEMPLATE
        # req["request"]["contents"] = [
        #     {
        #         "role": "user",
        #         "parts": [
        #             {
        #                 "fileData": {
        #                     "mimeType": "image/jpeg",
        #                     "fileUri": f"gs://{BUCKET_NAME}/{frame}"
        #                 }
        #             }
        #         ]
        #     }
        # ]

        # Truncate the previous frame fileData part
        req["request"]["contents"][0]["parts"] = req["request"]["contents"][0]["parts"][:1]
        req["request"]["contents"][0]["parts"].append({
            "fileData": {
                "mimeType": "image/jpeg",
                "fileUri": f"gs://{BUCKET_NAME}/{frame}"
            }
        })
        req["request"]["labels"]["frame"] = frame

        lines.append(json.dumps(req))

    with open(target_jsonl, 'w') as f:
        for line in lines:
            f.write(f"{line}\n")

    print(f"Wrote {len(lines)} JSON lines to {target_jsonl}")


def upload_jsonl(jsonl_file):
    storage_client = Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(jsonl_file)
    blob.upload_from_filename(jsonl_file)

    print(f"Uploaded {jsonl_file} to the {BUCKET_NAME} bucket")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare (or upload) JSON Lines inputs for all frame prompts.')
    parser.add_argument('--frames-dir', help='Directory with frames that we want to prompt')
    parser.add_argument('--upload', help='JSON Lines file with prepared prompts')
    
    args = parser.parse_args()

    match (args.frames_dir, args.upload):
        case(frames_dir, upload) if frames_dir != None and upload != None:
            generate_prompts(frames_dir, upload)
            upload_jsonl(upload)
        case (frames_dir, _) if frames_dir != None:
            generate_prompts(frames_dir)
        case (_, upload) if upload != None:
            upload_jsonl(upload)
        case _:
            parser.print_help()
