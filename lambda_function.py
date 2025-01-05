import uuid
import boto3
import time
import urllib.request
import json


def lambda_handler(event, context):
    """
    Expects an event with S3 bucket info of the audio file, for example:
    {
      "file_uri": "my-audio-bucket",
    }
    """

    file_uri = event.get("file_uri")
    if not file_uri:
        raise ValueError("Event must specify the audio file path in S3 bucket.")

    job_name = f"transcription-job-{str(uuid.uuid4())}"

    transcribe_client = boto3.client("transcribe")

    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": file_uri},
        MediaFormat=file_uri.split(".")[-1],
        LanguageCode="en-US",
    )

    while True:
        status_response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        status = status_response["TranscriptionJob"]["TranscriptionJobStatus"]
        print(f"Current TranscriptionJobStatus: {status}")

        if status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(5)  # wait 5 seconds before polling again

    if status == "FAILED":
        raise RuntimeError(f"Transcription job failed for {job_name}")

    transcript_file_uri = status_response["TranscriptionJob"]["Transcript"][
        "TranscriptFileUri"
    ]
    print(f"Transcript File URI: {transcript_file_uri}")

    with urllib.request.urlopen(transcript_file_uri) as response:
        transcript_json = json.loads(response.read())

    transcript_text = transcript_json["results"]["transcripts"][0]["transcript"]
    print(f"Transcript: {transcript_text}")

    return {
        "transcription": transcript_text,
        "job_name": job_name,
        "job_status": status,
    }
