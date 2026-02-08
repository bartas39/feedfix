# backend/main.py

from fastapi import FastAPI, Form, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

import requests
import xml.etree.ElementTree as ET
import tempfile
import os
import uuid

from validator.google import validate_google_feed
from report import generate_pdf_report


# =====================
# APP
# =====================

app = FastAPI(title="FeedFix API", version="1.0")


# =====================
# CORS (GLOBAL)
# =====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# ROOT
# =====================

@app.get("/")
def root():
    return {"status": "FeedFix online"}


# =====================
# JSON
# =====================

@app.post("/validate/url")
def validate_feed(url: str = Form(...)):

    try:

        r = requests.get(url, timeout=20)

        if r.status_code != 200:
            raise HTTPException(400, "Nie można pobrać XML")

        root = ET.fromstring(r.content)

        return validate_google_feed(root)

    except Exception as e:

        raise HTTPException(500, str(e))


# =====================
# PDF
# =====================

@app.post("/validate/url/pdf")
def validate_pdf(response: Response, url: str = Form(...)):

    try:

        r = requests.get(url, timeout=20)

        if r.status_code != 200:
            raise HTTPException(400, "Nie można pobrać XML")

        root = ET.fromstring(r.content)

        data = validate_google_feed(root)

        file_id = uuid.uuid4().hex
        name = f"report_{file_id}.pdf"

        path = os.path.join(tempfile.gettempdir(), name)

        generate_pdf_report(data, path)

        with open(path, "rb") as f:
            pdf = f.read()

        if os.path.exists(path):
            os.remove(path)

        # Wymuś headers
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=raport.pdf"

        return Response(content=pdf, media_type="application/pdf")

    except Exception as e:

        raise HTTPException(500, str(e))
