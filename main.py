import uvicorn  # Thêm uvicorn vào import

from fastapi import FastAPI, Form, HTTPException
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
from typing import Optional
from login_auth import timedelta, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from fastapi.responses import JSONResponse
from scores import load_scores, score_to_numeric

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Danh sách các origins được phép
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức
    allow_headers=["*"],  # Cho phép tất cả các header
)
# Chat message model
class ChatMessage(BaseModel):
    message: str

@app.post("/chat/")
async def chat_endpoint(chat_message: ChatMessage):
    chat_store = load_chat_store()
    # Initialize the chatbot with the user's info
    agent = initialize_chatbot(chat_store)
    try:
        # text = chat_response(agent, chat_store, chat_message.message)
        text = chat_interface(agent, chat_store, chat_message.message)
        print(text)
        return {"status": "ok", "text": text}
    except Exception as e:
        return {"status": "false", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)