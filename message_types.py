from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    TEXT = "text"
    BUTTONS = "buttons"
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    POLL = "poll"
    QUIZ = "quiz"

@dataclass
class Button:
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None

@dataclass
class MediaMessage:
    type: MessageType
    caption: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    buttons: List[List[Button]] = None

@dataclass
class PollMessage:
    question: str
    options: List[str]
    is_anonymous: bool = True
    allows_multiple_answers: bool = False

class MessageBuilder:
    @staticmethod
    def create_text_message(text: str, buttons: List[List[Button]] = None):
        return {
            'type': MessageType.TEXT.value,
            'text': text,
            'buttons': [[button.__dict__ for button in row] for row in buttons] if buttons else []
        }
    
    @staticmethod
    def create_media_message(msg_type: MessageType, caption: str, 
                           file_path: str = None, buttons: List[List[Button]] = None):
        return {
            'type': msg_type.value,
            'caption': caption,
            'file_path': file_path,
            'buttons': [[button.__dict__ for button in row] for row in buttons] if buttons else []
        }
    
    @staticmethod
    def create_poll_message(question: str, options: List[str], **kwargs):
        return {
            'type': MessageType.POLL.value,
            'question': question,
            'options': options,
            **kwargs
        }