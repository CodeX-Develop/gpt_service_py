from pydantic import BaseModel
from app.utils.openAIconfig import openai

class Completion(BaseModel):
    prompt : str
    stream: bool = False


    async def CompletionResponse(self, **kwargs):
        response = openai.Completion.create(
            prompt=self.prompt,
            **kwargs
        )

        if kwargs.get('stream', False):
            return self.__stream_data(response, **kwargs)
            
        else:
            text_completion = response.choices[0].text
            return {
                "message": "Completion generated", 
                "completion": text_completion
            } 
        
    async def __stream_data(self, response, **kwargs):
        for res in response:
             yield res.choices[0].delta.get('text', '')

           

        