from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/")
def serve_home():
    return FileResponse("index.html")
from fastapi import FastAPI
import requests

app = FastAPI()

SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-key"


@app.get("/")
def serve_home():
    from fastapi.responses import FileResponse
    return FileResponse("index.html")


@app.get("/structure")
def get_structure():

    url = f"{SUPABASE_URL}/rest/v1/structure"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    res = requests.get(url, headers=headers)

    return res.json()
