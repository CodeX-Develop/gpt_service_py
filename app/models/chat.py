from typing import Callable, ClassVar, Dict, List, Any
from pydantic import BaseModel
from app.utils.openAIconfig import system_prompt, openai

import json
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Chat(BaseModel):
    prompt: str
    chat_id: int = 0
    stream: bool = False

    functions: ClassVar[List[dict]] = []
    active_functions: ClassVar[Dict[str, Callable]] = {}
    messages: list = []
    text_response: str = ''

    db_factory: Any = None

    @classmethod
    def active_function(cls, **decorator_kwargs ):
        def decorator(func):  
            description = decorator_kwargs.get('description', None)
            arguments = decorator_kwargs.get('arguments', None)
            required = decorator_kwargs.get('required', [])

            if not description: raise ValueError("Description is required for active functions")
            if not arguments: raise ValueError("Arguments is required for active functions")

            cls.functions.append({
                'name': func.__name__,
                'description': description,
                'parameters': {
                    'type': 'object',
                    'properties': arguments,
                    'required': required
                },
            })
            cls.active_functions[func.__name__] = func
            return func
        return decorator
    
    def set_db_factory(self, db_factory):
        self.db_factory = db_factory

    async def load_messages(self):
        messages_chat = [system_prompt]

        if self.chat_id == 0:
            messages_chat.append({'role': 'user','content': self.prompt})
            self.messages = messages_chat
        else: 
            messages_chat = self.format_message( await self.db_factory.read_all({"chat_id": self.chat_id}, "messages") )
            messages_chat.append({'role': 'user','content': self.prompt})
            log.info(messages_chat)
            self.messages = messages_chat

    def format_message(self, messages):
        messages_history = []
        for message in messages:
            messages_history.append({ "role": message['role'], "content": message['content'] })
        return messages_history
    
    async def save_message(self):
        if self.chat_id != 0:
            await self.db_factory.create({
                "chat_id": self.chat_id,
                "role": "user",
                "content": self.prompt,
                "created_at": datetime.now()
            }, "messages")

            await self.db_factory.create({
                "chat_id": self.chat_id,
                "role": "assistant",
                "content": self.text_response,
                "created_at": datetime.now()
            }, "messages")
    
    async def ChatResponse(self, **kwargs):
        await self.load_messages()
        if self.functions:
            response = openai.ChatCompletion.create(
                messages=self.messages,
                functions=self.functions,
                function_call="auto",
                **kwargs
            )
        else:
            response = openai.ChatCompletion.create(
                messages=self.messages,
                **kwargs
            )

        if kwargs.get('stream', False):
            return self.__stream_data(response, self.messages, **kwargs)
        else:
            response_message = response["choices"][0]["message"]
            if response_message.get("function_call"):
                function_name = response_message["function_call"]["name"]
                function_args = response_message["function_call"]["arguments"]
                second_response = self.__execution_functions(function_name, function_args, self.messages, **kwargs)
                self.text_response = second_response.choices[0].message.get('content', '')
            else:
                self.text_response = response.choices[0].message.get('content', '')
            
            await self.save_message()
            return {
                "message": "Chat generated", 
                "chat": self.text_response
            }
        
    async def __stream_data(self, response, messages, **kwargs):
        generator = self.__get_json_data(response, messages, **kwargs)
        async for data in generator:
            yield data
        await self.save_message()
        

    async def __get_json_data(self, response, messages, **kwargs):
        function_args_res = ''
        function_name = None

        for res in response:
            function_call = res.choices[0].delta.get("function_call")
            if function_call:
                # log.info('Function call: %s', function_call)
                if function_call.get("name"): function_name = function_call.get("name")
                function_args_res += function_call.get("arguments", "")
            else:
                response = self.__format_data_response(res)
                yield response
        
        if function_name:
            response = self.__execution_functions(function_name, function_args_res, messages, **kwargs)
            for res in response:
                response = self.__format_data_response(res)
                yield response

    def __execution_functions(self, func_name, func_args, messages, **kwargs):
        function_to_call = self.active_functions[func_name]
        function_args = json.loads(func_args)
        function_response = function_to_call(self, **function_args)

        messages.append({
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": func_name,
                "arguments": func_args
            }
        })

        messages.append({
            "role": "function",
            "name": func_name,
            "content": function_response
        })

        second_response = openai.ChatCompletion.create(
            messages=messages,
            **kwargs
        )
        return second_response

    def __format_data_response(self, response):
        self.text_response += response.choices[0].delta.get('content', '')
        return response.choices[0].delta.get('content', '')
    
    
        
        