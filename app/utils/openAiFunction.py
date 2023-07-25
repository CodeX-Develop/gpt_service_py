from app.models.chat import Chat
import json
from googlesearch import search
import requests

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
        description = "Make actual good google search results by query",
        arguments = {
            'busqueda': {
                'type': 'string',
                'description': 'The query to search in google by user input'
            }
        },
        required = ['busqueda']
    )
    def google_search(self, busqueda):
        result = search(busqueda, advanced=True, lang='es', num_results= 3)
        array_result = []
        for i in result:
            log.info(i)
            titulo = i.title
            descripcion = i.description
            array_result.append({
                'titulo' : titulo,
                'descripcion' : descripcion
            })

        result_openia = {
            'message' : f'Estos son los resultados de la busqueda: {result}',
            'result' : array_result
        }

        return json.dumps(result_openia)
    
    @Chat.active_function(
    description="Realiza una consulta exacta sobre el clima de una ciudad dada",
    arguments={
        "ciudad": {
            "type": "string",
            "description": "La ciudad a consultar"
        }
    },
    required=['ciudad']
)
    def get_weather(self, ciudad):
        response_lat_log = requests.get(f'https://nominatim.openstreetmap.org/search?format=json&q={ciudad}')
        response_lat_log_data = response_lat_log.json()
        latitud = response_lat_log_data[0]['lat']
        longitud = response_lat_log_data[0]['lon']
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={latitud}&lon={longitud}&appid=055676e58560ae66cbf3b1c1b9af2729')
        response_data = response.json()  # Convert the response to a Python dictionary

        response_weather = {
            'message': f"El clima del país: {response_data['sys']['country']} es: {response_data['weather'][0]['description']} con una temperatura de: {(response_data['main']['temp'] - 32) * 5/9} grados Celcius"
        }
        return json.dumps(response_weather)

    
    def printFunctions(self):
        log.info("Active functions: %s", self.active_functions)
        log.info("Functions: %s", self.functions)
    
