from typing import Optional
from pydantic import BaseModel

class KakaoRequest(BaseModel):
    intent: Optional[dict] = None
    userRequest: Optional[dict] = None
    bot: Optional[dict] = None
    action: Optional[dict] = None