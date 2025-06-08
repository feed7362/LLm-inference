from langchain_core.tools import Tool
from pydantic import BaseModel

class ExampleInput(BaseModel):
    example_input: str
    
def example(example_input: str) -> str:
    """
    This is an example tool that takes a string input and returns a modified version of it.
    """
    return "This is an example tool" + example_input

calculator_tool = Tool(
    name="example",
    func=example,
    description=(
        "This is an example tool that takes a string input and returns a modified version of it."
    ),
    args_schema=ExampleInput
)