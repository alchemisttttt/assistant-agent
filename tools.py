import os
import requests
from dotenv import load_dotenv
import resend

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY
MY_EMAIL = os.getenv("MY_EMAIL")
def get_weather(location):
    url="https://api.openweathermap.org/data/2.5/weather"
    params={
        "q": location,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return f"Error getting weather data in'{location}'"

    data = response.json()
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    desc = data["weather"][0]["description"]

    return f"Weather in {location}: {desc}, {temp}°C (feels like {feels_like}°C)"
def web_search(query):
    url="https://api.tavily.com/search"
    payload={
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results":3
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return f"Error in search of'{query}'"

    data = response.json()
    results = data.get("results",[])
    if not results:
        return f"No results found for '{query}'"

    formatted_results = []
    for r in results:
        formatted_results.append(f"- {r['title']}: {r['content'][:150]}... ({r['url']})")

    return  f"Search results for '{query}':\n" + "\n".join(formatted_results)

def send_email( subject, body):
    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": MY_EMAIL,
            "subject": subject,
            "text": body
        })
        return f"e-mail sent with {subject}"
    except Exception as e:
        return f"E-mail failed to send  {e}"
