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
        bucket = "question-images"  # ✅ FIX THIS

        url = f"{SUPABASE_URL}/storage/v1/object/list/{bucket}"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        res = requests.get(url, headers=headers)

        data = res.json()

        # ✅ If error returned, show it clearly
        if isinstance(data, dict) and "error" in data:
            return data

        result = []

        for f in data:
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{f['name']}"

            result.append({
                "name": f["name"],
                "url": file_url
            })

        return result

    except Exception as e:
        return {"error": str(e)}
