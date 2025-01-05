import uuid


def lambda_function(event, context):
    """
    Expects an event with S3 bucket/key info of the audio file, for example:
    {
      "bucket": "my-audio-bucket",
      "key": "recordings/audio-file.mp3",
      "language_code": "en-US"  # optional, defaults to 'en-US'
    }
    """

    # Extracting parameters from the event
    bucket_name = event.get("bucket")
    object_key = event.get("key")
    language_code = event.get("language_code", "en-US")

    if not bucket_name or not object_key:
        raise ValueError("Event must specify 'bucket' and 'key' for the audio file.")

    return
