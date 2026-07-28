import os
import json
from dotenv import load_dotenv
from tools import send_email,web_search,get_weather
from groq import Groq

load_dotenv()
client=Groq(api_key=os.getenv('GROQ_API_KEY'))

tools=[

    {
        "type":"function",
        "function":{
            "name":"get_weather",
            "description":"Get the current weather for a specific city",
            "parameters":{
                    "type":"object",
                    "properties":{
                        "location":{"type":"string","description":"City name, e.g. 'Paris'"}
                    },
                "required":["location"]
                      }
        }

    },

    {
        "type":"function",
        "function":{
            "name":"web_search",
            "description":"Search the web for current information on a topic",
            "parameters":{
                "type":"object",
                "properties":{
                   "query":{"type":"string","description":"What to search for"}
                },
                "required":["query"]
            }

        }

    },


    {
        "type":"function",
        "function":{
            "name":"send_email",
            "description":"Send an email to the user with a subject and body. Only use this when the user explicitly asks you to send/email them something.",
            "parameters":{
                "type":"object",
                "properties":{
                "subject":{"type":"string","description":"The email subject line"},
                "body":{"type":"string","description":"The email content"}
                },
            "required":["subject","body"]
            }

        }
    }
]


av_functions={
    "get_weather":get_weather,
    "send_email":send_email,
    "web_search":web_search
}


SYSTEM_PROMPT = (
    "You are a helpful personal assistant with access to real-time tools: "
    "checking the weather, searching the web, and sending emails. "
    "Use a tool ONLY when it's clearly needed to answer the request. "
    "For send_email specifically, only use it when the user explicitly asks you "
    "to send or email them something — never send an email on your own initiative. "
    "After a tool runs, summarize the result naturally and concisely in one or two sentences."
)



def run_agent(usr_msg,history:list):
    history.append({"role":"user","content":usr_msg})
    try:
        response= client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=history,
            tools=tools,
        )
    except Exception as e:
        history.append({"role":"assistant","content":"Sorry, I had trouble processing that — could you try rephrasing?"})
        return "Sorry, I had trouble processing that — could you try rephrasing?"

    msg = response.choices[0].message

    if msg.tool_calls:
        history.append(msg)

        for call in msg.tool_calls:
            func_name= call.function.name
            func_args = json.loads(call.function.arguments) or {}
            print(f"[Agent is calling: {func_name}({func_args})]")
            result = av_functions[func_name](**func_args)

            history.append({"role":"tool","tool_call_id":call.id,"content":result})

        response_2= client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=history,
        )
        reply= response_2.choices[0].message.content
        history.append({"role":"assistant","content":reply})
        return reply


    reply = msg.content
    history.append({"role":"assistant","content":reply})
    return reply


if __name__ == "__main__":
    history=[{"role":"system","content":SYSTEM_PROMPT}]
    print("Assistant ready. Type 'exit' to quit.")

    while True:
        usr_input=input("You:")

        if usr_input.lower()=="exit":
            break
        print("Agent:",run_agent(usr_input,history))