from pydantic import BaseModel

class TodoUpdateRequest(BaseModel):
    done: bool