from fastapi import APIRouter
from app.db.database import get_table_data, add_to_table
from app.core.logging import logs_bot
from app.Bot.handlers.keyboards.telegram_sender import (
    send_message,
    send_photo,
    send_video,
    send_animation,
    send_document
)
from app.db.models import User, Notification


router = APIRouter()

async def validate_and_log_request(http_message: dict):
    """
    Валидация и логирование входящего запроса.
    
    Проверяет наличие обязательных полей и существование пользователя в базе данных.
    Логирует информацию о полученном запросе.
    """
    await logs_bot("info", f"Received request with data: {http_message}")
    
    # Проверяем наличие обязательных полей
    required_fields = ["chat_id", "type", "content"]
    for field in required_fields:
        if field not in http_message:
            raise ValueError(f"Missing required field: {field}")
            
    users = await get_table_data(User)
    user_exists = any(user["user_id"] == int(http_message["chat_id"]) for user in users)
    
    if not user_exists:
        await logs_bot("warning", f"User not found: {http_message['chat_id']}")

def get_message_params(http_message: dict) -> dict:
    """
    Подготовка параметров сообщения.
    
    Проверяет корректность типа сообщения и формирует словарь с параметрами,
    включая chat_id, content и caption.
    """
    valid_types = ["text", "photo", "video", "animation", "document"]
    message_type = http_message.get("type")
    if message_type not in valid_types:
        raise ValueError(f"Invalid message type: {message_type}. Must be one of {valid_types}")
        
    return {
        "message_type": message_type,
        "chat_id": int(http_message["chat_id"]),
        "content": http_message.get("content"),
        "caption": http_message.get("caption", "")
    }

# Общий обработчик для всех типов сообщений
async def send_content(chat_id: int, params: dict):
    """
    Отправляет контент пользователю в зависимости от типа сообщения.
    
    Определяет функцию-обработчик для каждого типа сообщения (text, photo, video, animation, document)
    и вызывает соответствующую функцию отправки с необходимыми аргументами.
    """
    handlers = {
        "text": {
            "func": send_message,
            "args": {"chat_id": chat_id, "text": params["content"]}
        },
        "photo": {
            "func": send_photo,
            "args": {
                "photo": params["content"],
                "caption": params.get("caption"),
                "chat_id": chat_id
            }
        },
        "video": {
            "func": send_video,
            "args": {
                "video": params["content"],
                "caption": params.get("caption"),
                "chat_id": chat_id
            }
        },
        "animation": {
            "func": send_animation,
            "args": {
                "animation": params["content"],
                "caption": params.get("caption", ""),
                "chat_id": chat_id
            }
        },
        "document": {
            "func": send_document,
            "args": {
                "document": params["content"],
                "caption": params.get("caption"),
                "chat_id": chat_id
            }
        }
    }

    message_type = params["message_type"]
    if message_type not in handlers:
        await logs_bot("warning", f"Unsupported message type: {message_type}")
        raise ValueError(f"Unsupported message type: {message_type}")

    try:
        handler = handlers[message_type]
        await handler["func"](
            **handler["args"]
        )
    except Exception as e:
        await logs_bot("error", f"Error sending {message_type}: {str(e)}")
        raise

async def log_notification(params: dict):
    """
    Сохраняет информацию об отправленном уведомлении в базу данных.
    
    Формирует запись уведомления с user_id и типом контента и добавляет её в таблицу Notification.
    """
    notification_entry = {
        "user_id": params["chat_id"],
        "type_content": params["message_type"],
    }
    await add_to_table(Notification, notification_entry)

@router.get("/users")
async def get_users():
    """
    Получает список всех пользователей из базы данных.
    
    Возвращает список пользователей с их user_id, first_name, last_name и created_at.
    """
    users = await get_table_data(User)
    return {
        "users": [
            {
                "user_id": user["user_id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "created_at": user["created_at"].isoformat()
            }
            for user in users
        ]
    }

@router.post("/message_answer")
async def send_message_endpoint(http_message: dict):
    """
    Эндпоинт для отправки различных типов сообщений пользователям.
    
    Этапы обработки:
    1. Валидация входящего запроса.
    2. Подготовка параметров сообщения.
    3. Отправка контента пользователю.
    4. Логирование уведомления.

    Формат запроса для /message_answer:
    {
        "chat_id": "ID пользователя",
        "type": "(text/photo/video/animation/document)", 
        "content": "содержимое сообщения",
        "caption": "подпись (опционально)"
    }
    """
    try:
        await validate_and_log_request(http_message)
        
        message_params = get_message_params(http_message)
        
        await send_content(message_params["chat_id"], message_params)
        await log_notification(message_params)
    
        await logs_bot("info", "Message sent successfully")
        return {"status": "success", "message": "Контент успешно отправлен"} # problems
        
    except Exception as e:
        error_msg = f"Error in message_answer endpoint: {str(e)}"
        await logs_bot("error", error_msg)
        return {"status": "error", "message": error_msg}


@router.get("/ping")
async def ping():
    """
    Эндпоинт для проверки работоспособности сервиса.
    
    Возвращает статус сервиса с сообщением "PONG!".
    """
    try:
        return {"status": "success", "message": "PONG!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}