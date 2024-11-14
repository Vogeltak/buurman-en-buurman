import vertexai
from vertexai.batch_prediction import BatchPredictionJob


BUCKET = "buurman-en-buurman-data"


vertexai.init()


def create_batch_job(input_uri=f"gs://{BUCKET}/prompts.jsonl", output_uri=f"gs://{BUCKET}/predictions"):
    job = BatchPredictionJob.submit(
        source_model="gemini-1.5-pro-002",
        input_dataset=input_uri,
        output_uri_prefix=output_uri
    )

    # Check job status
    print(f"Job resource name: {job.resource_name}")
    print(f"Model resource name with the job: {job.model_name}")
    print(f"Job state: {job.state.name}")


def check_batch_jobs():
    jobs = BatchPredictionJob.list()
    for j in jobs:
        print(f"{j.state.name} {j.resource_name} ({j.model_name})")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create and check batch prediction jobs.')
    parser.add_argument('--create', help='Input dataset URI (e.g., gs://bucket/prompts.jsonl)')
    parser.add_argument('--check', action='store_true', help='Check status of all batch prediction jobs')
    
    args = parser.parse_args()

    if args.create:
        create_batch_job(args.create)
    elif args.check:
        check_batch_jobs()
