from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from practise.store.query import query_store
from practise.llm.gemini_llm import get_llm

llm = get_llm()

class QueryInput(BaseModel):
    query: str = Field(description="User query")


async def physics(self):
    async def phy_tool(query: str):

        template = """
        You are a physics tutor for students, from the given context try to answer the question. Don't try to answer by yourself, Use the given context. If the answer is not in the context, say itsn not avaialble.
        
        query: `{query}`
        
        Context: `{context}`
        
         """
        prompt_temp=ChatPromptTemplate.from_template(template=template)
        
        context = await query_store(namespace="physics",query=query)

        chain= RunnableMap({       
        "query":lambda x: x['query'],
        "context":lambda _: context

        })| prompt_temp | llm | StrOutputParser() 


        response= await chain.ainvoke({"query":query})
        
        return response
    return phy_tool



async def chemistry(self):
    async def chem_tool(query: str):

        template = """
        You are a chemistry tutor for students, from the given context try to answer the question. Don't try to answer by yourself, Use the given context. If the answer is not in the context, say itsn not avaialble.
        
        query: `{query}`
        
        Context: `{context}`
        
                    """
        prompt_temp=ChatPromptTemplate.from_template(template=template)
        
        context = await query_store(namespace="chemistry",query=query)


        chain= RunnableMap({       
        "query":lambda x: x['query'],
        "context":lambda _: context

        })| prompt_temp | llm | StrOutputParser()


        response= await chain.ainvoke({"query":query})
        
        return response
    return chem_tool
    
    

async def computer(self):
    async def comp_tool(query: str):

        template = """
        You are a computer tutor for students, from the given context try to answer the question. Don't try to answer by yourself, Use the given context. If the answer is not in the context, say itsn not avaialble.
        
        query: `{query}`
        
        Context: `{context}`
        
 """
                    
        context = await query_store(namespace="computer",query=query)

        prompt_temp=ChatPromptTemplate.from_template(template=template)

        chain= RunnableMap({       
        "query":lambda x: x['query'],
        "context":lambda _: context


        })| prompt_temp | llm | StrOutputParser()

        response= await chain.ainvoke({"query":query})
        
        return response
    return comp_tool



class GetTools:
    
    def __init__(self, params=None):
        self.tools = []
        self.params = params  
    
    @classmethod
    async def init_tools(cls, params=None):
        self = cls(params)
        await self._get_tools()
        return self 


    async def _get_tools(self):
            physics_tool = StructuredTool.from_function(
                name="physics_tool",
                coroutine=await physics(self),
                args_schema=QueryInput,
                description="Use this tool when the query is related to physics subject "
            )

            chemistry_tool = StructuredTool.from_function(
                name="chemistry_tool",
                coroutine=await chemistry(self),
                args_schema=QueryInput,
                description="Use this tool when the query is related to chemistry question"
            )

            computer_tool = StructuredTool.from_function( 
                name="computer_tool",
                coroutine=await computer(self),
                args_schema=QueryInput,
                description="Use this tool when the query is related to computer question"
            )
        
            self.tools = [physics_tool, chemistry_tool, computer_tool]  
        
    def get_tools(self):
        return self.tools