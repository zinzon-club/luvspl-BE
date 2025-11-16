from data import ProfileData

def post_profile(req: Profile):
    return data.post_profile(req.nickname)