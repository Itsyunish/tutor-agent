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


        
        
# @app.post("/query/")
# async def query(query:str =  Query(...,description="ask the question for user query"),
#                 user_id:int = Query(...,description="enter the same user id as while uploading file")):
    
    
#     if not query.strip():
#         raise HTTPException("Query cannot be empty")
    
#     conversation_history = get_conversation(user_id)
    
#     conversation_history.append({"role": "user", "content": query})
    
#     conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history])
    
    
#     pc = Pinecone(api_key=settings.pinecone_api_key.get_secret_value())
    
#     user_match = metadata_collection.find_one({"user_id": user_id})
    
#     if user_match:
#         namespace_id = user_match.get("namespace_id")
#         print(f"Namespace id found:{namespace_id}")
#     else:
#         print("User not found")
        
#     async with pc.IndexAsyncio(host=settings.index_host.get_secret_value()) as index:

#         results = await index.search(
#                 namespace=namespace_id,
#                 query={
#                     "inputs": {"text": query},
#                     "top_k": 3,
#                 }
#             )

#         print("looping through results")
#         for hit in results['result']['hits']:
#             print(
#                 f"id: {hit['_id']:<5} | score: {round(hit['_score'], 2):<5} | text: {hit.get('fields', {}).get('text', '')[:50]}"
#             )

#         context_text = "\n".join(
#             hit.get("fields", {}).get("text", "") for hit in results['result']['hits']
#         )

#         print("context text")
#         print(context_text)

#         # 6. Query LLM
#         llm = get_llm()
#         prompt_template = """
#         You are a helpful assistant. Use the following context to answer the user's query.
#         Don't give wrong answers. If you don't know say it in a polite way.

#         Context:
#         {context}

#         Query:
#         {query}

#         Answer:
#         """
#         prompt = ChatPromptTemplate.from_template(prompt_template)
        
#         chain: Runnable = RunnableMap({
#         "query": lambda x: x['query'],
#         "context": lambda x: x['context'],  # use input context
#        }) | prompt | llm | StrOutputParser()
        
#         full_context = f"Conversation History:/n {conversation_text} + \n\n + Context:\n {context_text}"

#     answer = await chain.ainvoke({'query': query, "context": full_context})

#     conversation_history.append({"role": "assistant", "content": answer})
#     save_conversation(user_id, conversation_history)

#     return {"query": query, "answer": answer}

    
   
   
    
   
   
   
   
   
   
   
   
   
   
   
   
    