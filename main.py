
import os
import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field


from typing import Any

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Email Automation Gateway",
    description="API Gateway connecting GitHub Pages to n8n",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pin-ai-coder.github.io",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)

# n8n webhook configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


# Request data validation
class EmailRequest(BaseModel):
    email: EmailStr
    message: str = Field(min_length=1, max_length=10000)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FastAPI Email Gateway"
    }


# Check Github Pages to FAST API requests
@app.post("/test/receive")
async def receive_test(data: dict[str, Any]):
    print("\n========== GITHUB PAGES REQUEST ==========")
    print(data)
    print("==========================================\n")

    return {
        "success": True,
        "message": "FastAPI received your request!",
        "received_data": data
    }

# Email automation endpoint
@app.post("/n8n/email")
async def send_email(data: EmailRequest):

    if not N8N_WEBHOOK_URL:
        raise HTTPException(
            status_code=500,
            detail="n8n webhook URL is not configured"
        )

    payload = {
        "email": str(data.email),
        "message": data.message
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:

            response = await client.post(
                N8N_WEBHOOK_URL,
                json=payload
            )

            response.raise_for_status()

        return {
            "success": True,
            "message": "Request successfully forwarded to n8n"
        }

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=f"n8n returned HTTP {error.response.status_code}"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to n8n"
        )

