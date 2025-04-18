import math
from pydantic import BaseModel, Field

class CalculatorRequest(BaseModel):
    expression: str = Field(description="Calculate a mathematical expression with math module support")

def calculator(request: CalculatorRequest):
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

        result = eval(request.expression, allowed_globals, allowed_locals)
        return str(result)
    except (SyntaxError, NameError) as e:
        return f"Syntax or Name error: {str(e)}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"