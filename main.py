from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests

app = FastAPI()

SUPABASE_URL = "https://gdcwjpkgffqmatsmuqra.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdkY3dqcGtnZmZxbWF0c211cXJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA4ODMxMzksImV4cCI6MjA5NjQ1OTEzOX0.bpjgWe1ydbiIK2e9yOwESvMRLoK5c_lHljCpOM8q-3o"


@app.get("/")
def serve_home():
    return FileResponse("index.html")


@app.get("/structure")
def get_structure():

    try:
        url = f"{SUPABASE_URL}/storage/v1/object/list/your-bucket-name"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }

        res = requests.get(url, headers=headers)

        return res.json()

    except Exception as e:
        return {"error": str(e)}
