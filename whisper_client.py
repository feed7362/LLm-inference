import subprocess

from utils.logger import CustomLogger

logger = CustomLogger(__name__)


def run_whisper(audio: str) -> str:
    """
    Run the Whisper
    """
    logger.info("Running Whisper on audio file: %s", audio)

    result = subprocess.run([
        "whisper-cli", "-m", "./models/stt/ggml-large-v3-turbo-q5_0.bin",
        "-f", f"./data/audio/{audio}",
        "--print-colors",  # Confidence color-coding
        "-ml", "16",  # length of the generated text segments
        "-vm", "./models/stt/ggml-silero-v5.1.2.bin", "--vad",  # Voice Activity Detection
        "--no-timestamps",

    ], capture_output=True, text=True)
    logger.debug("Whisper internal logs: %s", result.stderr)

    return result.stdout
