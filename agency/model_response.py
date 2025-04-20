from pydantic import BaseModel, Field

class ResponseRequest(BaseModel):
    response: str = Field(description="Always return the assistant's response via this function.")
    
def return_response(request: ResponseRequest):
    return request.response