import re
from langchain_core.tools import Tool
from pydantic import BaseModel
import math


class CalcInput(BaseModel):
    expression: str


ALLOWED_GLOBALS = {"__builtins__": None}


def __get_allowed_locals__():
    math_locals = {
        name: getattr(math, name) for name in dir(math) if not name.startswith("__")
    }
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


def calculator(expression: str) -> str:
    """
    Safely evaluates a mathematical expression using math functions and selected Python built-ins.
    """
    try:
        allowed_locals = __get_allowed_locals__()
        expression = re.sub(r"[^0-9+\-*/().]", "", expression)
        result = eval(expression, ALLOWED_GLOBALS, allowed_locals)
        return str(result)
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError):
        return "Error: Invalid expression"
    except Exception as error:
        return f"Error evaluating expression: {str(error)}"


calculator_tool = Tool(
    name="calculator",
    func=calculator,
    description=(
        "Evaluates a mathematical expression using Python math and safe functions.\n"
        "Input: { expression: string } — e.g., { expression: 'log10(1000) + sqrt(25)' }\n"
        "Allowed functions: abs, round, pow, max, min, sum, and most functions from the Python `math` module.\n"
        "Output: String with the result or an error message.\n"
    ),
    args_schema=CalcInput,
)
