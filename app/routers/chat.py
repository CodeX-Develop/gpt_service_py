from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.chat import Chat
from app.utils.openAIconfig import openai

import asyncio

import json
import io

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()

@router.get("/chat/")
async def info_chat():
    return {
        "message": "This route only support POST requests",
        "body": {
            "prompt": "string",
            "chat_id": "int"
        }
    }

def get_current_weather(location):
    log.info("Getting weather for %s", location)
    weather_info = {
        "result": f"The current weather in {location} is 30 degrees celsius"
    }
    return json.dumps(weather_info)

async def get_json_data(response, messages):
    function_args_res = ''
    function_name = None

    available_functions = {
        "get_current_weather": get_current_weather,
    }

    for res in response:
        function_call = res.choices[0].delta.get("function_call")
        if function_call:
            log.info('Function call: %s', function_call)
            if function_call.get("name"): function_name = function_call.get("name")
            function_args_res += function_call.get("arguments", "")
        else: 
            data = {
                "role": res.choices[0].delta.get('role', ''),
                "content": res.choices[0].delta.get('content', '')
            }
            yield res.choices[0].delta.get('content', '')
    
    if function_name:
        function_to_call = available_functions[function_name]
        function_args = json.loads(function_args_res)
        log.info("Function arguments: %s", function_args)
        function_response = function_to_call(**function_args)

        messages.append({
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_name,
                "arguments": function_args_res
            }
        })

        messages.append({
            "role": "function",
            "name": function_name,
            "content": function_response
        })

        second_response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0613',
            messages=messages,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stream=True
        )

        for res in second_response:
            data = {
                "role": res.choices[0].delta.get('role', ''),
                "content": res.choices[0].delta.get('content', '')
            }
            yield res.choices[0].delta.get('content', '')
    

async def stream_data(response, messages):
    generator = get_json_data(response, messages)
    async for data in generator:
        # yield json.dumps(data)
        yield data

@router.post("/chat/")
async def chat(chat: Chat):
    chat_data = chat.model_dump()

    messages = await chat.messages()

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo-0613',
        messages=messages,
        functions = [
            {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            }
        ],
        function_call="auto",
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=chat_data['stream']
    )

    text_response = ''

    if chat_data['stream']:
        return StreamingResponse(stream_data(response, messages), 
                                #  media_type="application/json"
                                # media_type="text/event-stream"
                                media_type="text/plain"
                                 )
    else:
        text_response = response.choices[0].message.get('content', '')
        return {
            "message": "Chat generated", 
            "chat": text_response
        }