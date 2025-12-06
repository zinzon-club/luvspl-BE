from pydantic import BaseModel

class Profile(BaseModel):
    id: int
    nickname: str

class UpdateNicknameRequest(BaseModel):
    nickname: str
