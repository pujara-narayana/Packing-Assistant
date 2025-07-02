# Packing-Assistant

## Basic Idea - 

An AI app/website which lets you know the weather, prices of the plane/train tickets, which places to visit in the country/city you are planning to visit, and will give you a full guide on how, when, where at what time to visit each place.

1. Place to go
2. How many days?
3. Reason for visiting, like different places, will be suggested to different users based on their reasons.
4. Starting & Ending date.
5. User’s budget

The above is what the user should provide, or the LLM will ask the user directly  

The LLM will respond with - 

* Weather for each day they are visiting (same as the above point)
* Suggest places to visit for each day
* What type of clothes to wear and how much to pack 
* Famous restaurants and hotels, and Airbnb [budget accordingly]
* Different activities to do there based on the user’s input
* Give an opinion, is it a good time to visit or not? #
* Give an estimated budget based on the user’s input
* Suggest Uber or car rentals
* Use Google Maps to increase interactiveness with the user.

![packing_assistant](https://github.com/user-attachments/assets/4cda27cf-364b-4243-a154-5506d4873c1e)


## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/pujara-narayana/Packing-Assistant.git
   cd packing-assistant
   ```

2. **Install uv (if not already installed)**
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Create and activate virtual environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. **Install dependencies**
   ```bash
   uv sync
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and configuration
   ```

6. **Install development dependencies (optional)**
   ```bash
   uv sync --extra dev
   ```
NOTE: If you are using Pycharm, you can set the interpreter to the virtual environment created by uv.

Another Note: I have commented out the main function in packing_agent.py if you want to run the program in your IDE's console please uncomment it and run the file.

### Environment Variables

Create a `.env` file in the root directory with the following variables:

* OPENWEATHER_API_KEY:
* TAVILY_API_KEY:
* GEMINI_API_KEY:
* AMADEUS_API_KEY:
* AMADEUS_API_SECRET: 
* GEOAPIFY_API_KEY:
* GEMINI_PRO_API_KEY:

All the above API keys can be obtained from their respective websites and are free of cost. Only for GEMINI_PRO_API_KEY, you need to make an account on Google Cloud Platform and get the API key.
