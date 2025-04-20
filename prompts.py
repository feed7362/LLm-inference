import importlib
import inspect
import pkgutil
import json
import openai
import agency
import os
from pydantic import BaseModel

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

DEFAULT_METADATA_FILE = "data/metadata/tools.json"

def validate_metadata(metadata_file: str = DEFAULT_METADATA_FILE) -> None:
    _ensure_directory_exists(metadata_file)
    if not os.path.exists(metadata_file):
        logger.warning(f"{metadata_file} not found. Creating a new metadata file.")
        save_metadata_to_file(metadata_file)
        return
    try:
        with open(metadata_file, "r") as f:
            existing_metadata = json.load(f)
        registered_functions = {entry["function"]["name"] for entry in load_tools_metadata()}
        file_functions = {entry["function"]["name"] for entry in existing_metadata}
        missing_functions = file_functions - registered_functions
        if missing_functions:
            logger.warning(f"Detected tools not registered via decorators: {missing_functions}")
            save_metadata_to_file(metadata_file)
    except Exception as error:
        logger.error(f"Failed to validate metadata: {error}")
        save_metadata_to_file(metadata_file)

def _ensure_directory_exists(file_path: str) -> None:
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def save_metadata_to_file(filepath: str = DEFAULT_METADATA_FILE) -> None:
    try:
        schemas = load_tools_metadata()
        logger.debug(f"{len(schemas)} schemas loaded from {filepath}")
        with open(filepath, "w") as f:
            json.dump(schemas, f, indent=2)
    except Exception as error:
        logger.error(f"Failed to save metadata: {error}")

def load_tools_metadata() -> list:
    tool_schemas = []
    for _, module_name, is_pkg in pkgutil.iter_modules(agency.__path__, agency.__name__ + "."):
        if is_pkg:
            continue

        module = importlib.import_module(module_name)

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, BaseModel) and cls is not BaseModel:
                tool_schema = openai.pydantic_function_tool(cls)
                tool_schemas.append(tool_schema)
    logger.debug("Loaded tools metadata: %s", tool_schemas)
    return tool_schemas


def format_input(user_input: list[dict]) -> list[dict]:
    system_message = (
        "You are an AI assistant. You must always respond text using the function `ResponseRequest`. "
        "Do not answer with plain text. Every response must be returned as a function call with the full answer inside the argument. "
    )
    latex_instructions = (  
        "Format all mathematical expressions using LaTeX syntax. \n"
        "- Use `\\( ... \\)` for inline math.\n"
        "- Use `$$ ... $$` for display math blocks.\n"
        "- Do not explain LaTeX, just use it to present math."
    )
    return [
        {
            "role": "system",
            "content": f"{system_message}\n{latex_instructions}"
        },
        {
            "role": "user",
            "content": user_input
        }
    ]