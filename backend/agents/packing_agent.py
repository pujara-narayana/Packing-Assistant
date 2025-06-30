"""Agent that will communicate with other agents and will make the itinerary for the user."""

import uuid
from typing import TypedDict, Annotated, List, Dict, Any
from operator import add

from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.graph.state import CompiledStateGraph

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

from datetime import date
from backend.api_key_load import GEMINI_PRO_API_KEY
from backend.agents.weather_agent import WeatherAgent
from backend.agents.suggestion_agent import SuggestionAgent
from backend.agents.budget_agent import BudgetAgent
from backend.agents.prompts import PACKING_AGENT_SYSTEM_PROMPT
from backend.intents.packing_agent_intents import weather_tool, suggestion_tool, budget_tool

class TravelPlanningState(TypedDict):
    origin_city: str
    destination: str
    start_date: str
    end_date: str
    adults: int
    budget: int
    foodie: bool
    entertainment: bool
    business: bool

    weather_response: str
    suggestion_response: str
    budget_response: str
    final_itinerary: str

    initial_plan_complete: bool
    messages: Annotated[List[BaseMessage], add]


class PackingAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            api_key=GEMINI_PRO_API_KEY,
            temperature=0.5
        )
        self.memory = MemorySaver()
        self.tavily_search = TavilySearchResults()
        self.system_prompt = PACKING_AGENT_SYSTEM_PROMPT
        self.tools = [weather_tool, suggestion_tool, budget_tool, self.tavily_search]

        self.llm_with_tools = self.llm.bind_tools(self.tools)

        self.graph = self.build_graph()

    def build_graph(self) -> CompiledStateGraph:
        workflow = StateGraph(TravelPlanningState)

        workflow.add_node("weather_agent", self.call_weather_agent)
        workflow.add_node("suggestion_agent", self.call_suggestion_agent)
        workflow.add_node("budget_agent", self.call_budget_agent)
        workflow.add_node("synthesizer", self.call_synthesizer)

        workflow.add_node("supervisor", self.call_supervisor)
        tool_node = ToolNode(self.tools)
        workflow.add_node("tools", tool_node)

        workflow.add_node("gatekeeper", self.gatekeeper)
        workflow.set_entry_point("gatekeeper")

        workflow.add_conditional_edges(
            "gatekeeper",
            lambda state: "supervisor" if state.get("initial_plan_complete") else "weather_agent",
            {"weather_agent": "weather_agent", "supervisor": "supervisor"}
        )

        workflow.add_edge("weather_agent", "suggestion_agent")
        workflow.add_edge("suggestion_agent", "budget_agent")
        workflow.add_edge("budget_agent", "synthesizer")
        workflow.add_edge("synthesizer", END)

        workflow.add_conditional_edges(
            "supervisor",
            self.should_continue,
            {"tools": "tools", "__end__": END}
        )
        workflow.add_edge('tools', 'supervisor')

        return workflow.compile(checkpointer=self.memory)

    def should_continue(self, state: TravelPlanningState) -> str:
        """Determine if we should continue to tools or end."""
        messages = state.get("messages", [])
        if not messages:
            return "__end__"

        last_message = messages[-1]
        # Check if the last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "__end__"

    def gatekeeper(self, state: TravelPlanningState) -> Dict[str, Any]:
        """The entry point that routes to the correct phase."""
        print("---GATEKEEPER CHECKING---")
        return {}

    def call_weather_agent(self, state: TravelPlanningState) -> Dict[str, Any]:
        print("---(Phase 1) CALLING WEATHER AGENT---")
        try:
            weather_agent = WeatherAgent(
                state["destination"],
                date.fromisoformat(state["start_date"]),
                date.fromisoformat(state["end_date"])
            )
            response = weather_agent.get_weather_data()
            return {"weather_response": response}
        except Exception as e:
            print(f"Error in weather agent: {e}")
            return {"weather_response": f"Error getting weather data: {str(e)}"}

    def call_suggestion_agent(self, state: TravelPlanningState) -> Dict[str, Any]:
        print("---(Phase 1) CALLING SUGGESTION AGENT---")
        try:
            suggestion_agent = SuggestionAgent(
                state["destination"],
                state["foodie"],
                state["entertainment"],
                state["business"]
            )
            response = suggestion_agent.get_activities_agently(state.get("weather_response", ""))
            return {"suggestion_response": response}
        except Exception as e:
            print(f"Error in suggestion agent: {e}")
            return {"suggestion_response": f"Error getting suggestions: {str(e)}"}

    def call_budget_agent(self, state: TravelPlanningState) -> Dict[str, Any]:
        print("---(Phase 1) CALLING BUDGET AGENT---")
        try:
            budget_agent = BudgetAgent(
                state["budget"],
                state["origin_city"],
                state["destination"],
                state["start_date"],
                state["end_date"],
                state["adults"]
            )
            response = budget_agent.get_budget(state.get("suggestion_response", ""))
            return {"budget_response": response}
        except Exception as e:
            print(f"Error in budget agent: {e}")
            return {"budget_response": f"Error getting budget analysis: {str(e)}"}

    def call_synthesizer(self, state: TravelPlanningState) -> Dict[str, Any]:
        print("---(Phase 1) SYNTHESIZING ITINERARY---")
        try:
            synthesis_prompt = f"""Create a comprehensive final itinerary using the following data:

TRIP DETAILS:
- Route: {state['origin_city']} → {state['destination']}
- Dates: {state['start_date']} to {state['end_date']}
- Travelers: {state['adults']} adult(s)
- Budget: ${state['budget']}

Please create a detailed day-by-day itinerary with packing recommendations."""

            self.system_prompt += f"""\n\n Weather Agent Response: {state.get('weather_response', 'Not available')} \n
        Suggestion Agent Response: {state.get('suggestion_response', 'Not available')} \n
        Budget Agent Response: {state.get('budget_response', 'Not available')} \n"""

            response = self.llm.invoke([SystemMessage(content=self.system_prompt), HumanMessage(content=synthesis_prompt)])

            return {
                "initial_plan_complete": True,
                "final_itinerary": response.content,
                "messages": [AIMessage(content=response.content)]
            }
        except Exception as e:
            print(f"Error in synthesizer: {e}")
            error_message = f"Error creating itinerary: {str(e)}"
            return {
                "initial_plan_complete": True,
                "final_itinerary": error_message,
                "messages": [AIMessage(content=error_message)]
            }

    def call_supervisor(self, state: TravelPlanningState) -> Dict[str, Any]:
        print("---(Phase 2) SUPERVISOR CHECKING---")
        try:
            messages = state.get('messages', [])
            if not messages:
                return {"messages": [AIMessage(content="How can I help you with your travel plans?")]}

            conversation = [SystemMessage(content=self.system_prompt)] + messages

            response = self.llm_with_tools.invoke(conversation)

            return {"messages": [response]}

        except Exception as e:
            print(f"Error in supervisor: {e}")
            error_response = AIMessage(content=f"I encountered an error: {str(e)}. Please try again.")
            return {"messages": [error_response]}

# The below function is just for running the agent in a console-like environment.

    def run(self):
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        print("--- Welcome to the Two-Phase AI Travel Planner ---")
        print("--- Phase 1: Initial Plan Creation (Required) ---")

        try:
            initial_data = {
                "origin_city": input("Enter your origin city: "),
                "destination": input("Enter your destination city: "),
                "start_date": input("Enter trip start date (YYYY-MM-DD): "),
                "end_date": input("Enter trip end date (YYYY-MM-DD): "),
                "adults": int(input("Enter number of adults: ")),
                "budget": int(input("Enter your budget in USD: ")),
                "foodie": "y" in input("Are you a foodie? (y/n): ").lower(),
                "entertainment": "y" in input("Interested in entertainment? (y/n): ").lower(),
                "business": "y" in input("Is this a business trip? (y/n): ").lower(),
                "initial_plan_complete": False,
                "messages": [],
            }
        except ValueError:
            print("Invalid input. Please enter numbers for adults and budget. Exiting.")
            return

        print("\n--- Generating your initial itinerary... ---")
        try:
            result_phase1 = self.graph.invoke(initial_data, config=config)

            print("\n\n--- YOUR PERSONALIZED TRAVEL ITINERARY ---")
            print(result_phase1.get('final_itinerary', 'Error: Could not generate itinerary'))
            print("-" * 50)

            print("\n--- Phase 2: Follow-up Chat ---")
            print("You can now ask follow-up questions. Type 'quit' to exit.")

            while True:
                user_input = input("You: ")
                if user_input.lower() == 'quit':
                    break

                try:
                    follow_up_result = self.graph.invoke(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=config
                    )

                    messages = follow_up_result.get("messages", [])
                    if messages:
                        ai_message = messages[-1].content
                        print(f"\nAI Planner: {ai_message}\n")
                    else:
                        print("\nAI Planner: I didn't understand that. Could you please rephrase?\n")

                except Exception as e:
                    print(f"\nError during chat: {str(e)}")
                    print("Please try again.\n")

        except Exception as e:
            print(f"Error during phase 1: {str(e)}")
            print("Please check your inputs and try again.")


if __name__ == '__main__':
    agent = PackingAgent()
    agent.run()