from app.models.chat import Chat
import json

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class ChatFunction(Chat):

    # @Chat.active_function(
    #     description="Get the current weather in a location",
    #     arguments={
    #         "location": {
    #             "type": "string",
    #             "description": "The location to get the weather for"
    #         }
    #     },
    #     required=["location"]
    # )
    # def get_current_weather(self, location):
    #     log.info("Getting weather for %s", location)
    #     weather_info = {
    #         "result": f"The current weather in {location} is 30 degrees celsius"
    #     }
    #     return json.dumps(weather_info)
    
    @Chat.active_function(
        description="Search google with a given query, look for current information, information you don't know, only when needed.",
        arguments={
            "query": {
                "type": "string",
                "description": "The query to search"
            }
        },
        required=["query"]
    )
    def search_in_google(self, query):
        log.info("Searching in google for %s", query)
        google_info = {
            "result": f"Google search for {query}"
        }
        return json.dumps(google_info)
    
    def printFunctions(self):
        log.info("Active functions: %s", self.active_functions)
        log.info("Functions: %s", self.functions)
    
