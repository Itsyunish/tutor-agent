from langchain_community.chat_message_histories import RedisChatMessageHistory
from practise.config import settings

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os

import redis

redis_server = os.getenv("REDIS_SERVER")
url=f"redis://{redis_server}"  

async def get_chathistory(sender):
    history = RedisChatMessageHistory(sender, url,ttl=60*60*8)
    messages = history.messages 
    if len(messages) > 10:
      redis_client = redis.StrictRedis.from_url(f"redis://{redis_server}")
      redis_client.ltrim(history.key, 0, 9)
      history =RedisChatMessageHistory(sender, url, ttl=60*60*8)
      
    return history   