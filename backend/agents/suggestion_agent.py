"""Agent that will suggest activities to do in the city the user is visiting."""

from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from backend.api_clients.travel_search_api import get_activities_data_of_city_sync
from backend.agents.prompts import SUGGESTION_AGENT_SYSTEM_PROMPT
from backend.api_key_load import GEMINI_API_KEY

class SuggestionAgent:
    """Create a suggestion agent."""
    def __init__(self, city_to_visit: str, foodie: bool, business: bool, entertainment: bool ):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_API_KEY, temperature=0.5)
        self.city_to_visit = city_to_visit
        self.foodie = foodie
        self.entertainment = entertainment
        self.business = business
        self.system_prompt = SUGGESTION_AGENT_SYSTEM_PROMPT
        self.tavily_search = TavilySearchResults()
        self.memory = MemorySaver()
        self.config = {"configurable": {"thread_id": "abc123"}}
        self.tools = [get_activities_data_of_city_sync, self.tavily_search]
        self.suggestion_agent = create_react_agent(self.llm, self.tools, checkpointer=self.memory)

    def get_activities_agently(self) -> RunnableConfig | None:
        """Initialize the suggestion agent to get its response."""
        activities_request = ""
        if self.foodie:
            activities_request = (f"I am visiting {self.city_to_visit} and I am a foodie type of person. I love to"
                                  f" visit different restaurants and cafes. Can you suggest some good restaurants to visit in {self.city_to_visit}?")
        if self.business:
            activities_request = (f"I am visiting {self.city_to_visit} for business purposes. "
                                  f"Can you suggest some good places to visit in {self.city_to_visit} while I am free from work and conferences?")

        if self.entertainment:
            activities_request = (f"I am visiting {self.city_to_visit} and my purpose is to have fun and enjoy. "
                                  f"Can you suggest some good entertainment places to visit in {self.city_to_visit}?")


        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=activities_request)
        ]

        response = ""
        for step in self.suggestion_agent.stream(
                {"messages": messages},
                self.config,
                stream_mode="values"):

            response = step["messages"][-1].pretty_print()

        return response