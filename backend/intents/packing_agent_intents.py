"""Packing Agent Intents Module"""

from datetime import date

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from backend.agents.budget_agent import BudgetAgent
from backend.agents.suggestion_agent import SuggestionAgent
from backend.agents.weather_agent import WeatherAgent


@tool
def weather_tool(destination: str, start_date: str, end_date: str) -> RunnableConfig | str:
    """Gets the weather forecast for a given location and date range.

    Args:
        destination: The destination city name
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        The weather agent's response with weather data and recommendations
    """
    try:
        weather_agent = WeatherAgent(
            city_to_visit=destination,
            begin_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date)
        )
        return weather_agent.get_weather_data()
    except Exception as e:
        return f"Error getting weather data: {str(e)}"


@tool
def suggestion_tool(destination: str, foodie: bool, entertainment: bool, business: bool, weather_report: str) -> RunnableConfig | str:
    """Gets activity suggestions based on interests and weather.

    Args:
        destination: The destination city name
        foodie: Whether the user is interested in food experiences
        entertainment: Whether the user wants entertainment activities
        business: Whether this is a business trip
        weather_report: Current weather information

    Returns:
        The suggestion agent's response with activity suggestions according to the user's interests and weather conditions
    """
    try:
        suggestion_agent = SuggestionAgent(
            city_to_visit=destination,
            foodie=foodie,
            entertainment=entertainment,
            business=business
        )
        return suggestion_agent.get_activities_agently(weather_report)
    except Exception as e:
        return f"Error getting activity suggestions: {str(e)}"


@tool
def budget_tool(origin: str, destination: str, start_date: str, end_date: str, adults: int, budget: int, suggestions: str) -> RunnableConfig | str :
    """Gets a budget analysis for the trip.

    Args:
        origin: Origin city name
        destination: Destination city name
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        adults: Number of adults traveling
        budget: Available budget in USD
        suggestions: Activity suggestions to include in budget

    Returns:
        The budget agent's response with budget analysis and recommendations according to the user's budget and trip details
    """
    try:
        budget_agent = BudgetAgent(
            budget=budget,
            origin_city=origin,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            adults=adults
        )
        return budget_agent.get_budget(suggestions)
    except Exception as e:
        return f"Error getting budget analysis: {str(e)}"