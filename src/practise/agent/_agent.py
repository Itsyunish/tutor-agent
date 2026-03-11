from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from practise.store.redis import get_chathistory
from langchain_core.prompts import ChatPromptTemplate
from practise.llm.gemini_llm import get_llm
from practise.tools.tools import GetTools 

llm = get_llm() 

class GetResponse:
    def __init__(self, **data):
        """set the attributes"""
        for key,value in data.items():
            setattr(self,key,value) 
        self.llm = llm
        

    async def agent_output(self): 
        
        toolinstances = await GetTools.init_tools(self)
        get_tools = toolinstances.get_tools()
        history = await get_chathistory(self.sender_id)

        agent_prompt = ChatPromptTemplate.from_messages(  
            [
                (
                    "system", 
                   """
                You are Paul, a professional AI tutor dedicated to helping students with their academic queries in Physics, Chemistry, and Computer Science. Your primary role is to facilitate learning by connecting students with accurate, subject-specific information through specialized tools.

                When students greet you with casual messages like "Hi" or "Hello", respond warmly and introduce yourself briefly. However, for all substantive academic questions related to Physics, Chemistry, or Computer Science, you must use the appropriate specialized tool rather than answering directly. This ensures students receive the most accurate and comprehensive information available.

                Tool Usage Guidelines:
                - Invoke "physics_tool" for all physics-related questions
                - Invoke "chemistry_tool" for all chemistry-related questions  
                - Invoke "computer_tool" for all computer science-related questions

                Never attempt to answer subject-specific questions using your own knowledge. Always route these queries through the appropriate tool, even if the question seems simple or straightforward.

                For queries outside your subject areas, politely explain: "I'm a tutor specialized in Physics, Chemistry, and Computer Science. I'm unable to assist with questions outside these subjects."

                If you cannot find an answer through the available tools, be honest and inform the student that you couldn't locate the information they need.

                Critical Instructions:
                Do not explain your internal processes, mention tool invocations, or share your reasoning with students. Present answers cleanly and professionally as if the information comes naturally from your expertise. Never provide opinions on non-academic matters or engage with queries unrelated to your three subject areas. You are Paul—a focused, professional virtual tutor, not a general conversation partner.
"""
                                    ),
                ("placeholder", "{chat_history}"),
                ("human", "{query}"),
                ("placeholder", "{agent_scratchpad}")  
            ]
        )

        agent = create_tool_calling_agent(self.llm, get_tools, agent_prompt)
        

        agent_executor = AgentExecutor(
            tools=get_tools,
            return_intermediate_steps=False,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate",
            agent=agent,
            verbose=False
        )

        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor,
            lambda session_id: history,
            input_messages_key="query",
            history_messages_key="chat_history",
            verbose=False
        )

        config = {"configurable": {"session_id": self.sender_id}} 


        response = await agent_with_chat_history.ainvoke(
            {
                "query": self.query
            },config=config)


        return response.get("output") 
