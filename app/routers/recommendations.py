from fastapi import APIRouter
from app.models.recommendations import Recommendations
from app.utils.openAIconfig import openai

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()

@router.get("/recommendations/")
async def info_recommendations():
    return {
        "message": "This route only support POST requests",
        "body": {
            "user": "string",
            "assistant": "string"
        }
    }

@router.post("/recommendations/")
async def get_recommendations(recommendations: Recommendations):
    recommendations_data = recommendations.model_dump()

    user = recommendations_data.get('user')
    assistant = recommendations_data.get('assistant')

    response = openai.Completion.create(
        model='text-davinci-003',
        prompt="Genera una lista de recomendaciones cortas de consultas que se pueden hacer a un asistente de odoo, esta debe de ser una lista de 3 recomendaciones, las recomendaciones solo deben de ser consultas de datos, tomando en cuenta el siguiente contexto:{'user':" + user + ",'assistant':" + assistant + "}\nResp:",
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["END"]
    )

    recommendations_response = recommendations.format_recommendations(response.choices[0].text)
    return {
        "message": "Recommendations generated", 
        "recommendations": recommendations_response
    }