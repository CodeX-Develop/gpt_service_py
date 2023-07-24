from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.completion import Completion

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()

@router.get("/completion")
async def info_completion():
    return {
        "message": "This route only support POST requests",
        "body": {
            "prompt": "string",
            "stream": "bool"
        }
    }

@router.post("/completion")
async def completion(completion: Completion):
    completion_data = completion.dict()

    response = await completion.CompletionResponse(
        model='text-davinci-003',
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=completion_data['stream']
    )

    if completion_data['stream']:
        return StreamingResponse(response, media_type="text/plain")
    else:
        return response