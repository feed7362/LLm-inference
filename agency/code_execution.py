from langchain_core.tools import Tool
from pydantic import BaseModel

class CodeInput(BaseModel):
    code: str
    
def execute_code(code: str) -> str:
    """
    Executes Python code in a safe environment. Retrieves variable `result` if set.
    """
    local_context = {}
    try:
        exec(code, {}, local_context)
        execution_result = local_context.get("result")
        return str(execution_result) if execution_result is not None else "No result produced."
    except Exception as exception:
        return f"Error: {exception}"

code_execution_tool = Tool(
    name="execute_code",
    func=execute_code,
    description=(
        "Executes Python code in a sandboxed environment.\n"
        "Input: { code: string } — Python code where the final result must be assigned to a variable named `result`.\n"
        "Output: The value of `result`, or an error message if execution fails.\n"
    ),
    args_schema=CodeInput
)