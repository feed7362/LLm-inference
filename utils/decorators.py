    
def tool(name: str = None, description: str = ""):
    def decorator(func):
        func._tool_metadata = {
            "name": name or func.__name__,
            "description": description,
            "parameters": list(func.__annotations__.items())
        }
        return func
    return decorator