import math
from pydantic import BaseModel, Field

ALLOWED_GLOBALS = {"__builtins__": None}

def __get_allowed_locals__():
    math_locals = {name: getattr(math, name) for name in dir(math) if not name.startswith("__")}
    safe_functions = {
        "abs": abs,
        "round": round,
        "pow": pow,
        "max": max,
        "min": min,
        "sum": sum,
    }
    math_locals.update(safe_functions)
    return math_locals

class CalculatorRequest(BaseModel):
    expression: str = Field(description="Evaluates a mathematical expression")

def calculator(request: CalculatorRequest) -> str:
    try:
        allowed_locals = __get_allowed_locals__()
        result = eval(request.expression, ALLOWED_GLOBALS, allowed_locals)
        return str(result)
    except (SyntaxError, NameError) as error:
        return f"Syntax or Name error: {str(error)}"
    except Exception as error:
        return f"Error evaluating expression: {str(error)}"
