from pydantic import BaseModel

class Profile(BaseModel):
    id: int
    nickname: str