from fastapi import APIRouter
from model.profile import Profile
from data.profile import ProfileData

router = APIRouter(prefix="/profile")

@router.post("/nickname")
def update_nickname(req: Profile):
    profile_data = ProfileData()
    data = profile_data.update_nickname(req.id, req.nickname)
    return {"success": True, "data": data}
