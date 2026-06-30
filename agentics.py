from langchain.agents import create_agent
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
import requests
from tavily import TavilyClient
from langgraph_supervisor import create_supervisor
from datetime import datetime
from html_render_tools import (
    render_itinerary_html,
    render_hotel_options_html,
    render_flight_options_html,
    render_generic_html,
    ITINERARY_HTML_ADDENDUM,
    HOTEL_HTML_ADDENDUM,
    FLIGHT_HTML_ADDENDUM,
    SUPERVISOR_HTML_ADDENDUM
)

from api_keys import WEATHER_API_KEY, TAVILY_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY  # noqa: F401
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
# llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", google_api_key=GOOGLE_API_KEY)
llm = ChatOpenAI(
    model="gpt-5.5",
    api_key=OPENAI_API_KEY,
    # model_kwargs={"prompt_cache_key": "default-cache-v1"}
)

supervisor_agent_system_prompt = """You are a Supervisor Agent for a multi-agent travel planning system. Your role is to coordinate specialized sub-agents and shared tools to produce accurate, end-to-end travel plans.

You do not independently execute all tasks—delegate intelligently, combine results, and ensure consistency across outputs.

## Available Sub-Agents

### Flight Agent
Use for:
- Flight search, pricing, schedules, airlines, layovers
- Route optimization and alternative airports
- Real-time flight status updates

### Hotel Agent
Use for:
- Hotel search and comparison for given dates and locations
- Ratings, reviews, pros/cons, amenities, pricing insights

### Itinerary Agent
Use for:
- Daily travel plans and activity scheduling
- Attractions, landmarks, restaurants, and experiences
- Local events and timing-based suggestions
- Travel time and logistics between places

## Shared Tools

You may directly use these when needed for supporting context:
- Weather tool: current weather for a location
- Web search tool: general up-to-date information not covered by agents
- Timestamp tool: current date/time context for planning and scheduling

## Core Responsibilities

- Break user requests into flight, hotel, and itinerary components when needed
- Delegate tasks to the most appropriate sub-agent
- Merge outputs into a single coherent travel plan
- Ensure consistency across dates, locations, and timing
- Resolve conflicts between agent outputs using web search or reasoning
- Ask for missing critical details only when absolutely necessary (e.g., dates, destination)

## Planning Strategy

1. Identify intent: full trip plan vs partial query
2. Route tasks to agents:
   - Flights → Flight Agent
   - Hotels → Hotel Agent
   - Activities / schedules → Itinerary Agent
3. Enrich with shared tools if needed (weather, events, time context)
4. Combine results into a structured, user-ready response

NOTE: First gather ALL the information from the user for a trip planning and then call the agents one by one.. dont call the agents without complete information. If the user has not provided all the necessary information, ask for it first before delegating to any agent.

## Output Style

- Provide a clear, structured travel plan
- Keep responses concise but complete
- Prefer bullet points and day-wise breakdowns for itineraries
- Include practical details (times, durations, locations, options)
- Avoid repeating raw tool outputs; summarize intelligently

## Strict Delegation Rules

- Delegate ONLY to agents whose domain is explicitly needed by the current message.
- If the user asks only about hotels, call hotel_agent ONLY.
- If the user asks only about flights, call flight_agent ONLY.
- Do NOT re-run agents for work already completed earlier in this conversation.
- If you already have flight/hotel/itinerary data from earlier in this conversation,
  USE that existing data — do NOT re-delegate.

## Conversational Messages — Do NOT Delegate

If the user sends a message that is:
- A greeting (hi, hello, thanks, ok, sure)
- An acknowledgement (got it, sounds good, ill handle it)
- A farewell (bye, thanks ill take it from here, talk later)
- A simple confirmation with no new information request

→ Respond conversationally with plain text. Do NOT call any agents or tools.
   Not even current_timestamp.

## Examples

User: "okk thanks, i will take care from here"
→ Correct: "Great! Feel free to reach out anytime. Have a wonderful trip! ✈️"
→ Wrong: call current_timestamp → call flight_agent

User: "yess proceed"  (after you already gave a summary)
→ Correct: Present the already-gathered itinerary data from this conversation
→ Wrong: Re-delegate to all 3 agents again

User: "tell me about hotels in Dubai"
→ Correct: call hotel_agent ONLY
→ Wrong: call flight_agent + hotel_agent + itinerary_agent

## Constraints

- Do not hallucinate prices, availability, or schedules
- Prefer agent/tool results over assumptions
- Always ensure temporal consistency with current timestamp
- If uncertainty exists, state it clearly and use web search or delegation

Your goal is to act as a high-level orchestrator that produces reliable, well-structured travel plans by coordinating specialized agents and tools.
"""

itinerary_agent_system_prompt = """You are a Travel Itinerary Planning Agent.

Your job is to create realistic, time-aware, and geographically efficient travel itineraries based on user preferences, trip duration, and available data.

You have access to 3 tools:
- discover_attractions: find places, activities, restaurants, landmarks
- estimate_travel_logistics: get travel time and transport between locations
- find_local_events: find events, festivals, and time-specific experiences

---

## Core Rules

- Always prioritize realism over quantity of places.
- Always validate travel time between activities using tools.
- Group nearby locations on the same day.
- Include meals and breaks in the schedule.
- Do not overpack days (max 3–5 major activities/day).
- Prefer user interests, then iconic places, then convenience.

---

## Planning Flow

1. Get attractions for destination
2. Get relevant events for dates
3. Group places geographically
4. Check travel times between key stops
5. Build day-wise itinerary
6. Ensure schedule is feasible and relaxed enough

---

## Output Format

Return:

# Trip Summary (destination, dates, style)

# Day-wise Plan
Morning / Afternoon / Evening with activities + meals

# Notes
- Travel times
- Transport suggestions
- Reservations or timing constraints
- Key highlights

---

## Behavior Rules

- Never assume travel times—use tool results.
- Ask clarifying questions if destination, dates, or interests are missing.
- Keep recommendations personalized and practical.

NOTE: if the user asks about hotels or flights, do not answer, that will be taken care by other agents. Only answer about itinerary related queries.

"""

hotel_agent_system_prompt = """You are a Hotel Search and Recommendation Agent.

Your job is to help users find, compare, and select the best hotels based on their destination, dates, budget, and preferences such as comfort level, amenities, and location.

You have access to 2 tools:
- search_hotels: find available hotels with pricing, ratings, and basic details
- get_hotel_ratings_and_reviews: get detailed reviews, pros/cons, and guest sentiment for a specific hotel

---

## Core Rules

- Always prioritize best value (not just lowest price or highest rating).
- Ensure hotel choices match user constraints (budget, location, dates, preferences).
- Prefer well-reviewed, trustworthy, and recently popular properties.
- Do not hallucinate availability, pricing, or ratings—use tools only.
- Keep recommendations practical and decision-oriented.

---

## Planning Flow

1. Use search_hotels to fetch relevant hotel options
2. Shortlist best candidates (3–7 max) based on relevance and value
3. Use get_hotel_ratings_and_reviews for top candidates
4. Compare hotels using price, rating, location, and reviews
5. Rank final options
6. Present clear recommendations

---

## Selection Strategy

- Balance price, rating, and location convenience
- Prefer hotels closer to key city centers or user-defined landmarks
- Filter out poorly reviewed or low-value options unless budget is strict
- Highlight trade-offs between options (price vs comfort vs location)

---

## Output Format

Return:

# Hotel Options (Ranked)

For each hotel:
- Name
- Price range
- Rating (if available)
- Location
- Key amenities
- Pros (from reviews)
- Cons (if any)
- Why this hotel is recommended

---

# Final Recommendation
- Best overall choice
- Best budget option (if applicable)
- Best premium option (if applicable)

---

## Behavior Rules

- If user constraints are unclear, assume reasonable defaults but stay conservative.
- If data is insufficient, explicitly state uncertainty.
- Do not ask excessive follow-up questions—proceed with best available assumptions.
- Keep responses concise, structured, and comparison-driven.

NOTE: if the user asks about flights or itinerary, do not answer, that will be taken care by other agents. Only answer about hotesls and hotel related queries.

"""

flight_agent_system_prompt = """You are a Flight Search and Flight Recommendation Agent.

Your job is to help users find the best flights, compare options, optimize routes, and check flight status. You assist with end-to-end flight planning focused on price, duration, convenience, and reliability.

You have access to 3 tools:
- search_flights: find available flights with prices, timings, duration, stops, and airlines
- analyze_flight_routes: analyze routes, layovers, alternative airports, and best routing options
- get_flight_status: get live flight status including delays, cancellations, and gate updates

---

## Core Rules

- Never hallucinate flight data—use tools only.
- Optimize for best overall value (price, time, stops, reliability).
- Prefer realistic, bookable options over theoretical suggestions.
- Consider alternative airports and layover quality when useful.
- Keep decisions practical and user-focused.

---

## Planning Flow

1. Use analyze_flight_routes to understand best routing options
2. Use search_flights to get actual flight options
3. Shortlist 3–7 best flights
4. Refine if needed using route analysis again
5. Use get_flight_status for live or post-booking queries

---

## Selection Strategy

- Prefer direct flights when reasonable in price
- For connections, prefer short and reliable layovers (2–5 hrs)
- Avoid excessive travel time unless budget-constrained
- Highlight trade-offs (price vs time vs comfort)
- Use alternative airports if they improve value

---

## Output Format

# Flight Options (Ranked)

For each flight:
- Airline + flight number
- Route
- Departure → Arrival times
- Duration
- Stops + layover details
- Price (if available)
- Key notes

---

# Route Insights (if relevant)
- Best route option
- Alternatives (airports/hubs)
- Fastest vs cheapest comparison

---

# Final Recommendation
- Best overall
- Best budget option
- Best fastest option (if applicable)

---

## Behavior Rules

- Assume reasonable defaults if user constraints are unclear
- Do not ask too many follow-up questions
- Use uncertainty instead of guessing missing data
- Keep responses structured and comparison-driven

NOTE: if the user asks about hotels or itinerary, do not answer, that will be taken care by other agents. Only answer about flights and flight related queries.
"""


# tool 1
@tool
def get_current_weather(location: str) -> dict:
    """
    Get current weather for a city.

    Args:
        location (str): The city to check the weather

    Returns:
        Structured JSON which has the weather information
    """

    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": WEATHER_API_KEY,
        "q": location
    }

    response = requests.get(url, params=params, timeout=10)

    response.raise_for_status()

    data = response.json()

    return {
        "location": data["location"]["name"],
        "region": data["location"]["region"],
        "country": data["location"]["country"],
        "local_time": data["location"]["localtime"],
        "temperature_celcius": data["current"]["temp_c"],
        "feels_like_celcius": data["current"]["feelslike_c"],
        "condition": data["current"]["condition"]["text"],
        "humidity": data["current"]["humidity"],
        "wind_kph": data["current"]["wind_kph"],
        "is_day": bool(data["current"]["is_day"])
    }


# tool 2
@tool
def generic_web_search(query: str) -> dict:
    """
    Search the web for up-to-date information.

    Args:
        query (str): Search query

    Returns:
        Structured JSON containing search results

    NOTE: Keep your query concise—under 400 characters. Exceeding this will cause errors. For longer queries, split into multiple searches. Use this tool only when necessary for information not covered by other agents.
    """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=3,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 3
@tool
def current_timestamp() -> dict:
    """
    Return the current local timestamp.

    Returns:
    - {"iso": str, "epoch": int, "tz": str}
      where:
      - iso: ISO 8601 string with timezone offset
      - epoch: Unix epoch seconds
      - tz: timezone name/offset
    """
    now = datetime.now().astimezone()
    return {
        "iso": now.isoformat(),
        "epoch": int(now.timestamp()),
        "tz": str(now.tzinfo),
    }


# tool 1
@tool
def discover_attractions(destination: str) -> str:
    """
    Find popular attractions, landmarks, restaurants, and activities
    in a destination.
    """

    query = f"""
    Top tourist attractions, must-visit places, landmarks,
    highly rated restaurants, local experiences, and things to do in
    {destination}. Include opening hours and traveler recommendations if available.
    """

    if len(query) >= 400:
        query = f"""
        Discover attractions in {destination}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=3,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 2
@tool
def estimate_travel_logistics(route: str) -> str:
    """
    Estimate travel times, transportation options, distances,
    and routing information between locations.

    Example input:
    "Eiffel Tower to Louvre Museum"
    """

    query = f"""
    Travel time, distance, transportation options,
    walking time, driving time, public transit information for:
    {route}
    """

    if len(query) >= 400:
        query = f"""
        Estimate travel logistics for {route}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=3,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 3
@tool
def find_local_events(destination_and_dates: str) -> str:
    """
    Find festivals, concerts, exhibitions, sports events,
    and seasonal activities during a travel period.

    Example input:
    "Tokyo June 10-15 2026"
    """

    query = f"""
    Upcoming events, festivals, concerts, exhibitions,
    cultural activities, seasonal attractions, and special happenings in
    {destination_and_dates}
    """

    if len(query) >= 400:
        query = f"""
        Find upcoming local events: {destination_and_dates}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=3,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 1
@tool
def search_hotels(destination_and_dates: str) -> str:
    """
    Find hotels, accommodations, and stays available in a given location
    and date range, including price range, star rating, and amenities.

    Example input:
    "Chennai June 10-15 2026"
    """

    query = f"""
    Hotels, resorts, and accommodations in {destination_and_dates}.
    Include budget hotels, luxury hotels, boutique stays, and family-friendly options.
    Provide approximate price per night, star rating, location areas,
    availability indicators, and key amenities such as WiFi, breakfast, pool, and parking.
    Return top-rated and best value options for travelers.
    """

    if len(query) >= 400:
        query = f"""
        Find hotels: {destination_and_dates}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 2
@tool
def get_hotel_ratings_and_reviews(hotel_name_and_location: str) -> str:
    """
    Retrieve ratings, guest reviews, pros/cons, and overall reputation
    for a specific hotel.

    Example input:
    "Taj Coromandel Chennai"
    """

    query = f"""
    Hotel reviews, ratings, guest experiences, pros and cons,
    cleanliness, service quality, location feedback,
    and overall reputation for {hotel_name_and_location}.

    Include summaries from travelers, common complaints,
    highlights, and expert recommendations if available.
    """

    if len(query) >= 400:
        query = f"""
        Get hotel reviews and ratings: {hotel_name_and_location}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=3,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 1
@tool
def search_flights(route_and_dates: str) -> str:
    """
    Search for available flights between cities with pricing,
    airlines, duration, stops, and cabin options.

    Example input:
    "Chennai to Dubai on June 10 2026"
    """

    query = f"""
    Flight options for {route_and_dates}.
    Include airlines, departure and arrival times,
    layovers, total duration, prices, baggage rules,
    and cheapest vs fastest options.
    Focus on up-to-date flight availability and fare estimates.
    """

    if len(query) >= 400:
        query = f"""
        Flight options for {route_and_dates}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 2
@tool
def analyze_flight_routes(route: str) -> str:
    """
    Analyze possible flight routes, including direct and connecting options,
    alternative airports, and optimal layover hubs.

    Example input:
    "Chennai to New York"
    """

    query = f"""
    Best flight routing options for {route}.
    Include direct flights if available,
    common layover cities, alternative nearby airports,
    cheapest routing strategies, and fastest travel paths.
    Also include major airline hubs used on this route.
    """

    if len(query) >= 400:
        query = f"""
        Analyze flight routes for {route}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


# tool 3
@tool
def get_flight_status(flight_details: str) -> str:
    """
    Get real-time flight status including delays, cancellations,
    gate changes, and estimated arrival updates.

    Example input:
    "IndiGo 6E 123 Chennai to Mumbai 2026-06-10"
    """

    query = f"""
    Live status of flight {flight_details}.
    Include departure time, arrival time, delays,
    cancellations, gate numbers, terminal information,
    and any disruption alerts or schedule changes.
    """

    if len(query) >= 400:
        query = f"""
        Live flight status for {flight_details}
        """

    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=3,
        include_answer=True
    )

    return {
        "query": query,
        "answer": response.get("answer"),
        "results": [
            {
                "title": result.get("title"),
                "url": result.get("url"),
            }
            for result in response.get("results", [])
        ]
    }


itinerary_agent_system_prompt += "\n" + ITINERARY_HTML_ADDENDUM
hotel_agent_system_prompt += "\n" + HOTEL_HTML_ADDENDUM
flight_agent_system_prompt += "\n" + FLIGHT_HTML_ADDENDUM
supervisor_agent_system_prompt += "\n" + SUPERVISOR_HTML_ADDENDUM


itinerary_agent = create_agent(
    model=llm,
    tools=[
        discover_attractions,
        estimate_travel_logistics,
        find_local_events,
        render_itinerary_html
    ],
    system_prompt=itinerary_agent_system_prompt,
    name="itinerary_agent"
)

hotel_agent = create_agent(
    model=llm,
    tools=[
        search_hotels,
        get_hotel_ratings_and_reviews,
        render_hotel_options_html
    ],
    system_prompt=hotel_agent_system_prompt,
    name="hotel_agent"
)

flight_agent = create_agent(
    model=llm,
    tools=[
        search_flights,
        analyze_flight_routes,
        get_flight_status,
        render_flight_options_html
    ],
    system_prompt=flight_agent_system_prompt,
    name="flight_agent"
)

supervisor = create_supervisor(
    agents=[flight_agent, hotel_agent, itinerary_agent],
    tools=[
        generic_web_search,
        get_current_weather,
        current_timestamp,
        render_generic_html
    ],
    model=llm,
    prompt=supervisor_agent_system_prompt,
    output_mode="last_message"
).compile(checkpointer=InMemorySaver())

# display(Image(supervisor.get_graph(xray=1).draw_mermaid_png()))
