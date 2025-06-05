# backend/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv
import httpx

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI()

# Allow frontend requests from Vite dev server
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Chat endpoint for GPT assistant
@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    prompt = data.get("message", "")
    if not prompt:
        return {"reply": "Please provide a question."}
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"reply": response.choices[0].message.content.strip()}

# Irradiance estimation from PVGIS API
@app.get("/api/irradiance")
async def irradiance(lat: float, lon: float, peakpower: float = 5.0, loss: float = 14.0):
    url = (
        "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?"
        f"lat={lat}&lon={lon}&peakpower={peakpower}&loss={loss}&outputformat=json"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
