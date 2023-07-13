from pydantic import BaseModel
from app.utils.openAIconfig import system_prompt

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class Chat(BaseModel):
    prompt: str
    chat_id: int = 0
    stream: bool = False

    async def messages(self):
        messages_chat = [
            system_prompt
        ]
        log.info(messages_chat)
        if self.chat_id == 0:
            messages_chat.append(
                {
                    'role': 'user',
                    'content': self.prompt
                }
            )
            return messages_chat
        else: 
            # Add connection to database
            return messages_chat
    
    async def save_message(self, message):
        # Add connection to database
        return True
        