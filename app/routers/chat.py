from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from app.models.chat import Chat
from app.db.factory import DatabaseFactory
from app.utils.openAiFunction import ChatFunction

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

router = APIRouter()

def get_db_factory(request: Request) -> DatabaseFactory:
    return request.app.state.db

@router.get("/chat")
async def info_chat():
    response = {
        "message": "This route only support POST requests",
        "body": {
            "prompt": "string",
            "chat_id": "int"
        }
    }
    return response

# add route options, this route redirect to post route
@router.options("/chat")
async def options_chat():
    return {
        "message": "This route only support POST requests",
        "body": {
            "prompt": "string",
            "chat_id": "int"
        }
    }

@router.post("/chat")
async def chat(chat: Chat, db_factory: DatabaseFactory = Depends(get_db_factory)):
    chat_data = chat.dict()
    chat.set_db_factory(db_factory)

    # db_factory.create(chat_data, "chats")

    response = await chat.ChatResponse(
        model='gpt-3.5-turbo-0613',
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=chat_data['stream']
    )

    if chat_data['stream']:
        return StreamingResponse(response, 
                                #  media_type="application/json"
                                # media_type="text/event-stream"
                                media_type="text/plain"
                                 )
    else:
        return response