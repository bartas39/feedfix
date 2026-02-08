# backend/main.py

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import requests
import xml.etree.ElementTree as ET
import tempfile
import os
import uuid

from validator.google import validate_google_feed
from report import generate_pdf_report


# =========================
# APP
# =========================

app = FastAPI(
    title="FeedFix API",
    version="1.0"
)


# =========================
# CORS (WAŻNE)
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "https://feedfix-production.up.railway.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROOT
# =========================

@app.get("/")
def home():
    return {"status": "FeedFix API działa"}


# =========================
# JSON
# =========================

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


# =========================
# PDF
# =========================

@app.post("/validate/url/pdf")
def validate_feed_pdf(url: str = Form(...)):

    try:

        r = requests.get(url, timeout=20)

        if r.status_code != 200:
            raise HTTPException(400, "Nie można pobrać XML")

        root = ET.fromstring(r.content)

        result = validate_google_feed(root)

        file_id = uuid.uuid4().hex
        name = f"report_{file_id}.pdf"

        path = os.path.join(
            tempfile.gettempdir(),
            name
        )

        generate_pdf_report(result, path)

        with open(path, "rb") as f:
            pdf = f.read()

        if os.path.exists(path):
            os.remove(path)

        return pdf

    except Exception as e:

        raise HTTPException(500, str(e))
