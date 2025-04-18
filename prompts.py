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

def validate_metadata(metadata_path="data/metadata/tools.json"):
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    if not os.path.exists(metadata_path):
        logger.warning(f"{metadata_path} not found. Creating a new metadata file.")
        save_metadata_to_file(metadata_path)
        return
    try:
        with open(metadata_path, "r") as f:
            existing_metadata = json.load(f)

        registered_names = {m["function"]["name"] for m in load_tools_metadata()}
        file_names = {m["function"]["name"] for m in existing_metadata}

        missing = file_names - registered_names
        if missing:
            logger.warning(f"Detected tools not registered via decorators: {missing}")
            save_metadata_to_file(metadata_path)
    except Exception as e:
        logger.error(f"Failed to validate metadata: {e}")
        save_metadata_to_file(metadata_path)

def save_metadata_to_file(filepath="data/metadata/tools.json"):
    try:
        schemas = load_tools_metadata()
        logger.debug(f"{len(schemas)} schemas loaded from {filepath}")
        json.dump(schemas, open(filepath, "w"), indent=2)
    except Exception as e:
        logger.error(f"Failed to save metadata: {e}")
        
def load_tools_metadata():
    tool_schemas = []
    for _, module_name, is_pkg in pkgutil.iter_modules(agency.__path__, agency.__name__ + "."):
        if is_pkg:
            continue

        module = importlib.import_module(module_name)

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, BaseModel) and cls is not BaseModel:
                tool = openai.pydantic_function_tool(cls)
                tool_schemas.append(tool)
                
    logger.debug("Loaded tools metadata: %s", tool_schemas)
    return tool_schemas

def format_input(user_input: list[dict]):
    """
    User_input format
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg" } }

        ]
    }
    """
    system = ("A chat between a curious user and an artificial intelligence assistant. "
              "The assistant gives helpful, detailed, and polite answers to the user's questions. "
              "The assistant calls functions with appropriate input when necessary")
    latex = """ 
            Format all mathematical expressions using LaTeX syntax. 
            - Use `\\( ... \\)` for inline math.
            - Use `$$ ... $$` for display math blocks.
            - Do not explain LaTeX, just use it to present math.
            """
    return [
        {
          "role": "system",
          "content": [f"{system}\n{latex}"]

        },
        {
          "role": "user",
          "content": user_input
        }
      ]