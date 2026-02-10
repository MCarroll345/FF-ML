from fastapi import FastAPI, APIRouter, Body, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from .recomRoute import recomRouter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(recomRouter)