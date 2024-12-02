import uvicorn
from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import yaml
import hashlib
import os
from src.global_settings import USERS_FILE, SCORES_FILE
import streamlit as st
from pydantic import BaseModel
from llama_index.llms.openai import OpenAI
import openai
from src.index_builder import build_indexes
from src.ingest_pipeline import ingest_documents
from src.conversation_engine import initialize_chatbot, load_chat_store, chat_response, chat_interface
from llama_index.core import Settings
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from login_auth import timedelta, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
from scores import load_scores, score_to_numeric
import base64
from openai import OpenAI

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()
openai.api_key = st.secrets.openai.OPENAI_API_KEY
client = OpenAI(api_key=st.secrets.openai.OPENAI_API_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Read the image file
        contents = await file.read()
        # Convert to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "What object is in this image? Answering a specific category: Electronics, Mobile, Book, Laptop, Art, Toy, Clothes."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        return {"analysis": completion.choices[0].message.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/")
async def chat_endpoint(chat_message: ChatMessage):
    chat_store = load_chat_store()
    agent = initialize_chatbot(chat_store)
    try:
        text = chat_interface(agent, chat_store, chat_message.message)
        print(text)
        return {"status": "ok", "text": text}
    except Exception as e:
        return {"status": "false", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)