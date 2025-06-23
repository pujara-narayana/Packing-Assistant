"""Agent that calculates the estimated budget based on user input and compares it with the user's budget."""

from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.agent_toolkits.load_tools import load_tools

from langgraph.prebuilt import create_react_agent

from backend.api_key_load import GEMINI_API_KEY
from backend.api_clients.flight_api import get_flight_data
from backend.api_clients.hotel_rental_api import get_hotel_data
from backend.api_clients.accommodation_api import get_accommodation_data_of_city
from backend.api_clients.car_rental_api import get_car_rental_data_of_city
from backend.agents.prompts import BUDGET_AGENT_SYSTEM_PROMPT

class BudgetAgent:
    """Create a budget agent."""
    def __init__(self, budget: int, origin_city: str, destination: str, start_date: str, end_date: str, adults: int = 1):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_API_KEY, temperature=0.5)
        self.budget = budget
        self.origin_city = origin_city
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.adults = adults
        self.tavily_search = TavilySearchResults()
        self.memory = MemorySaver()
        self.extra_tools = load_tools(["wikipedia","llm-math"], llm=self.llm)
        self.system_prompt = BUDGET_AGENT_SYSTEM_PROMPT
        self.tools = [get_flight_data, get_hotel_data, get_accommodation_data_of_city, get_car_rental_data_of_city, self.tavily_search, *self.extra_tools]
        self.config = {"configurable": {"thread_id": "abc123"}}
        self.budget_agent = create_react_agent(self.llm, self.tools, checkpointer=self.memory)


    def get_budget(self) -> RunnableConfig | None:
        """Initialize the budget agent to get its response."""

        budget_prompt = (f"The number of people travelling is {self.adults}. I/We have a budget of {self.budget} USD. "
                         f"I/We are travelling from {self.origin_city} to {self.destination} from {self.start_date} to {self.end_date}. "
                         f"Can you calculate the estimated budget for flights, hotels, accommodation, car rentals and taxi/uber? "
                         f"Compare it with my budget and provide suggestions on how to manage the budget effectively. "
                         f"Also, provide any additional information that might be useful for planning the trip.")
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=budget_prompt)
        ]

        response = ""

        for step in self.budget_agent.stream(
                {"messages": messages},
                self.config,
                stream_mode="values"):

            response = step["messages"][-1].pretty_print()

        return response

if __name__ == "__main__":
    # Example usage
    budget_agent = BudgetAgent(budget=1500, origin_city="New York", destination="Boston", start_date="2025-06-24", end_date="2025-06-28")
    result = budget_agent.get_budget()
    print(result)