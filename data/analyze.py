import os
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def save_analysis(user_id: int, analysis_data: dict):
    data_to_save = analysis_data.copy()
    data_to_save['user_id'] = user_id
    
    try:
        resp = supabase.table("analyze").insert(data_to_save).execute()
        if len(resp.data) == 0:
            raise Exception("Failed to insert analysis into Supabase")
        return resp.data[0]
    except Exception as e:
        print(f"Error saving analysis: {e}")
        raise e