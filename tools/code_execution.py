from langchain_core.tools import Tool
from pydantic import BaseModel

class CodeInput(BaseModel):
    code: str
    
def execute_code(code: str) -> str:
    """
    Executes Python code in a safe environment.
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
        "Use only when the user explicitly asks to execute Python code. "
        "NEVER use this tool to answer general questions, weather, search, or chat. "
        "Input: { code: string } — Python code where the final result must be assigned to a variable named `result`."
    ),
    args_schema=CodeInput
)