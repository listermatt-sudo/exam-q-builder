from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def run_script():

    # ✅ run your existing script automatically
    os.system("python markscheme_images.py")

    return """
    <html>
        <head>
            <title>Mark Scheme Processor</title>
        </head>
        <body>
            <h1>✅ Processing Complete</h1>
            <p>Your mark scheme has been processed.</p>
            <p>Check the output images folder.</p>
        </body>
    </html>
    """
