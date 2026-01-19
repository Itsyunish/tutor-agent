from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request

from src.practise.llm.gemini_llm import get_llm
from pathlib import Path
from src.practise.store.pinecone import PineconeService
import uuid
from practise.agent._agent import GetResponse
from langchain_core.runnables import Runnable, RunnableMap
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser   
from pinecone import Pinecone
from practise.config import settings 
from fastapi import FastAPI
from typing import  List


app = FastAPI()

load_dotenv()


@app.post("/query", tags=["query"])
async def query_route(query: str, sender_id: str):
    
    data = {
        "query": query,
        "sender_id":sender_id 
    }

    res = GetResponse(**data)
    result = await res.agent_output() 
    return result 



@app.post("/upload_file", tags=["File Uploads"])
async def query(
    file: List[UploadFile] = File(...),
):
    services = PineconeService(
        api_key=settings.PINECONE_API_KEY,
        host=settings.PINECONE_HOST,
        files=file
    )
    return await services.upload()


   