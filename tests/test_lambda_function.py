import json
import pytest
from unittest.mock import patch, MagicMock

from lambda_function import lambda_handler


@pytest.fixture
def mock_transcribe_client():
    """Creates a mock for the boto3 Transcribe client."""
    mock_client = MagicMock()

    mock_client.start_transcription_job.return_value = {}

    mock_client.get_transcription_job.side_effect = [
        {"TranscriptionJob": {"TranscriptionJobStatus": "IN_PROGRESS"}},
        {
            "TranscriptionJob": {
                "TranscriptionJobStatus": "COMPLETED",
                "Transcript": {
                    "TranscriptFileUri": "http://example.com/transcript.json"
                },
            }
        },
    ]

    return mock_client


@pytest.fixture
def mock_urlopen():
    """Mock urllib.request.urlopen to return a fake transcript JSON."""
    mock_response = MagicMock()
    fake_transcript = {
        "results": {"transcripts": [{"transcript": "Hello world, this is a test."}]}
    }

    mock_response.read.return_value = json.dumps(fake_transcript).encode("utf-8")
    return mock_response


@patch("boto3.client")
@patch("urllib.request.urlopen")
def test_lambda_handler(
    mock_urllib, mock_boto3_client, mock_transcribe_client, mock_urlopen
):
    """
    Test the lambda_handler by mocking out AWS Transcribe calls and the final transcript fetch.
    """

    mock_boto3_client.return_value = mock_transcribe_client
    mock_urllib.return_value = mock_urlopen

    event = {"file_uri": "s3://my-audio-bucket/my-file.mp3"}

    result = lambda_handler(event, context={})

    mock_transcribe_client.start_transcription_job.assert_called_once()
    assert (
        mock_transcribe_client.start_transcription_job.call_args[1]["Media"][
            "MediaFileUri"
        ]
        == "s3://my-audio-bucket/my-file.mp3"
    )

    assert mock_transcribe_client.get_transcription_job.call_count == 2

    mock_urllib.assert_called_once_with("http://example.com/transcript.json")

    assert result["job_status"] == "COMPLETED"
    assert "transcription" in result
    assert result["transcription"] == "Hello world, this is a test."
