"""Agent that gets the weather data"""

from datetime import date, datetime
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from backend.api_clients.weather_data import get_weather_data_of_city
from backend.agents.prompts import WEATHER_AGENT_SYSTEM_PROMPT
from backend.api_key_load import GEMINI_API_KEY

class WeatherAgent:
    """Create a weather agent."""
    def __init__(self, city_to_visit: str, begin_date: date, end_date: date):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_API_KEY, temperature=0.5)
        self.city_to_visit = city_to_visit
        self.begin_date = begin_date
        self.end_date = end_date
        self.system_prompt = WEATHER_AGENT_SYSTEM_PROMPT
        self.tavily_search = TavilySearchResults()
        self.memory = MemorySaver()
        self.tools = [get_weather_data_of_city, self.tavily_search]
        self.weather_agent = create_react_agent(self.llm, self.tools, checkpointer=self.memory)
        self.config = {"configurable": {"thread_id": "abc123"}}

    def get_weather_data(self) -> RunnableConfig | None:
        """Initialize the weather agent to get its response."""
        current_date = datetime.now().date()
        weather_request = (f"Today is {current_date}. "
            f"Get weather forecast for {self.city_to_visit} from {self.begin_date} to {self.end_date}. "
            f"Analyze the conditions and provide travel and packing recommendations.")

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=weather_request)
        ]

        for step in self.weather_agent.stream(
                {"messages": messages},
            self.config,
            stream_mode="values"):

            step["messages"][-1].pretty_print()