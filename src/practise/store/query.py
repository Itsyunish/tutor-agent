from practise.config import settings
from pinecone import Pinecone


async def query_store(namespace: str, query: str):
    print("entering indexing")
    
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    
    async with pc.IndexAsyncio(host=settings.PINECONE_HOST) as index:

        results = await index.search(
                namespace=namespace,
                query={
                    "inputs": {"text": query},
                    "top_k": 10,
                }   
            )
        print(results) 

        context_text = "\n".join(
            hit.get("fields", {}).get("text", "") for hit in results['result']['hits']
        )
        print("context",context_text)
        print("********************context received***************************")
        
        return context_text 