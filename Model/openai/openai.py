import requests
import search_func
import json
import pickle
import summary
import os
from const_config import proxy,openapikey
from loguru import logger


usage=0
messages = []
functions = [
        {
            "name": "search_from_Internet",
            "description": "search for information from internet when it's needed(Such as when you are not sure about something)",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "The question or keywords you want to search(describe in detail lead to better reply) ",
                    },
                },
                "required": ["q"],
            },
        },

#        {
#            "name": "schedule",
#            "description": "Set to-do items, set schedules and reminders, set alarm clock, set countdown, remind when time is up",
#            "parameters": {
#                "type": "object",
#                "properties": {
#                    "time": {
#                        "type": "string",
#                        "description": "The time to be set, in strict accordance with the following format: %Y-%m-%d %H:%M:%S",
#                    },
#                    "content":{
#                        "type": "string",
#                        "description": "The specific content to be reminded, if not specified by the user, it can be empty",
#                    }
#                },
#                "required": ["time","content"],
#            },
#        },

    ]

url='https://api.openai.com/v1/chat/completions'
proxy= proxy

asession=requests.session()
def chatRequest(model,messages,functions,function_call):
    key = openapikey
    headers={
        "Authorization": f"Bearer {key}"
    }
    prama={
        "model": model,
        "messages": messages,
        "functions":functions,
        "function_call":function_call
    }
    result=asession.post(url,headers=headers,json=prama,proxies=proxy,timeout=20)
    result=result.json()
    return result

def send(message):
    global usage
    # try:
    completion = chatRequest(
        model="gpt-4-turbo-preview",
        # model="gpt-3.5-turbo",
        messages=message,
        functions=functions,
        function_call="auto",
    )
    message.pop(-1)
    # print(completion)
    messages.append(completion['choices'][0]["message"])
    #print(messages)
    # print(completion.choices[0]["message"]["content"])
    usage=completion['usage']['total_tokens']
    return completion['choices'][0]["message"]

def ask(words):
    from prompt_and_deal import get_system_prompt
    askmsg = messages.append({"role": "user", "content": words})
    text = get_system_prompt()
    askmsg = messages.append(text)
    return askmsg

def funask(function_name,function_response):
    askmsg= messages.append({"role": "function",
                "name": function_name,
                "content": function_response,})
    return askmsg

def initsystem():
    global messages
    messages = []

def systemask(response):
    from prompt_and_deal import get_system_prompt
    text = get_system_prompt()
    askmsg= messages.append({"role": "system",
                "content": response})
    askmsg= messages.append(text)
    return askmsg


def deal():
    global response
    response=send(messages)

    if response.get("function_call"):
        logger.debug(response["function_call"])
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "search_from_Internet": search_func.search,
        }  # only one function in this example, but you can have multiple
        function_name = response["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response["function_call"]["arguments"])
        if function_name =="search_from_Internet":
            function_response = fuction_to_call(
                q=function_args.get("q"),
            )
            funask(function_name,function_response)
            response=deal()
            return response
    elif usage > 2200:
        summareply = summary.summarize(messages)
        initsystem()
        systemask(summareply)
        return response
    else : return response

def save():
    if(os.path.exists('message.data')):
        os.remove('message.data')
    with open("message.data", 'wb+') as f:
        pickle.dump(messages, f)

def read():
    global messages
    if(os.path.exists('message.data')):
        with open("message.data", 'rb+') as f:
            messages=pickle.load(f)

def chat(words):
    ask(words)
    reply = deal()
    if reply:
        return reply['content']

if __name__=="__main__":
    while (1):
        reply=chat(input("请输入: "))
        print("\rAI:",reply,'\n')


