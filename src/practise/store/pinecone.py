from pinecone import Pinecone
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from fastapi import HTTPException
import aiofiles
import uuid
import asyncio
from practise.config import settings
from langchain_community.document_loaders import (
    UnstructuredPDFLoader,
    PyMuPDFLoader 
)
import os


BATCH_SIZE = 96

class PineconeService:
    def __init__(self, api_key: str, host: str, files: List):
        self.files = [file for file in files] if files and not isinstance (files, List) else files
        self.batch_size = 96
        self.docs = []
        
        
    BATCH_SIZE = 20  # Small batch size 
    DELAY = 3  # 3 seconds between batches 

    async def upload(self): 
        if not self.files: 
            return 
        
        all_docs = []
        for uploaded_file in self.files:
            namespace = os.path.splitext(uploaded_file.filename)[0].lower()
            print(f"**********************{namespace}***********************************")
            ext_file = uploaded_file.filename.split(".")[-1].lower()
            if ext_file != "pdf":
                raise HTTPException(status_code=400, detail="Uploaded file is not a PDF")

            unique_filename = f"{uuid.uuid4()}_{uploaded_file.filename}"
            temp_file_name = f"{unique_filename}"

            # Save uploaded file 
            contents = await uploaded_file.read()
            async with aiofiles.open(temp_file_name, "wb") as f:
                await f.write(contents) 

            try:
                # Load PDF
                loader = PyMuPDFLoader(temp_file_name)
                documents = loader.load()

                # Split documents 
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,  # Smaller chunks
                    chunk_overlap=150
                )
                chunks = text_splitter.split_documents(documents)

                # Convert to LangChain Document objects
                for idx, item in enumerate(chunks):  
                    all_docs.append(Document(
                        page_content=item.page_content,
                        metadata={"source": uploaded_file.filename}
                    ))

            finally:
                # Clean up temp file
                if os.path.exists(temp_file_name):
                    os.remove(temp_file_name)
        
        # Upsert to Pinecone
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index_name = "aitutor"
        
        # Create index if not exists
        if not pc.has_index(index_name):
            pc.create_index_for_model(
                name=index_name,
                cloud="aws", 
                region="us-east-1",
                embed={"model": "multilingual-e5-large", "field_map": {"text": "text"}}
            )
            await asyncio.sleep(5)  # Wait for index to be ready
        
        async with pc.IndexAsyncio(host=settings.PINECONE_HOST) as index:
            
            await index.delete(delete_all=True, namespace=namespace)
            print(f"Dropped Pinecone namespace '{namespace}'")
            
            for start_idx in range(0, len(all_docs), BATCH_SIZE):
                batch = all_docs[start_idx:start_idx + BATCH_SIZE]
                
                chunks_to_upsert = [
                    {"id": f"doc_{start_idx + idx}", "text": doc.page_content}  
                    for idx, doc in enumerate(batch)  
                ]
                
                print("namespace", namespace)
                print(f"Upserting batch {start_idx//BATCH_SIZE + 1} ({len(chunks_to_upsert)} docs)") 
                
                try:
                    await index.upsert_records(namespace=namespace, records=chunks_to_upsert) 
                    print(f"✓ Success")
                except Exception as e:
                    print(f"Error: {e}")
                    # If rate limited, wait longer and retry once
                    if "429" in str(e):
                        print("Waiting 10 seconds...")
                        await asyncio.sleep(10)
                        await index.upsert_records(namespace=namespace, records=chunks_to_upsert)
                
                # IMPORTANT: Wait between batches
                await asyncio.sleep(delay=3)
            
            return f"✓ Done! Uploaded {len(all_docs)} documents"
                    
        
        
    async def _upsert_batch(self, vector_id: str, values: list, metadata: dict = None):
        chunks = self._file_chunking()
        pass
        
        
        return self.index.upsert(
            vectors=[{
                "id": vector_id,
                "values": values,
                "metadata": metadata or {}
            }]
        )

    def query(self, vector: list, top_k: int = 5):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )

    def delete(self, vector_id: str):
        return self.index.delete(ids=[vector_id])  
