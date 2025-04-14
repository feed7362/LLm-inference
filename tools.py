import math
import datetime
import json

def load_tools_metadata(path="tools_metadata.json") -> list:
    try:
        with open(path, "r") as file:
            return json.load(file)
    except Exception as e:
        return f"Error loading metadata: {str(e)}"

def calculator(expression: str) -> str:
    try:
        allowed_globals = {"__builtins__": None}
        allowed_locals = {k: getattr(math, k) for k in dir(math) if not k.startswith("__")}
        allowed_locals.update({
            "abs": abs,
            "round": round,
            "pow": pow,
            "max": max,
            "min": min,
            "sum": sum,
        })

        result = eval(expression, allowed_globals, allowed_locals)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

def datetime_now() -> str:
    try:
        now = datetime.datetime.now()
        return now.strftime("%d-%m-%Y- %H:%M:%S")
    except Exception as e:
        return f"Error getting current date/time: {str(e)}"