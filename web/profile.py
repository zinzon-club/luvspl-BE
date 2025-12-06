from fastapi import APIRouter, Depends
from model.profile import UpdateNicknameRequest
from data.profile import ProfileData
from utils.JWT import get_current_user

router = APIRouter(prefix="/profile")

@router.post("/nickname")
def update_nickname(req: UpdateNicknameRequest, user_id: int = Depends(get_current_user)):
    profile_data = ProfileData()
    data = profile_data.update_nickname(user_id, req.nickname)
    return {"success": True, "data": data}
