from pydantic import BaseModel, Field

class CodeExecutionRequest(BaseModel):
    code: str = Field(description="Execute code in Python environment and return the result.")
    
def execute_code(request: CodeExecutionRequest) -> str:
    local_context = {}
    try:
        exec(request.code, {}, local_context)
        execution_result = local_context.get("result")
        return str(execution_result) if execution_result is not None else "No result produced."
    except Exception as exception:
        return f"Error: {exception}"
