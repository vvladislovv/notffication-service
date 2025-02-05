from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
import aiohttp
from app.services.chat import router as chat_router


session = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    session = aiohttp.ClientSession()
    yield
    await session.close()

app = FastAPI(lifespan=lifespan)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def verify_api_key(api_key: str = Depends(api_key_header), request: Request = None):
    """
    Проверяет наличие API ключа в заголовках запроса.
    
    Если API ключ отсутствует, выбрасывает исключение HTTPException с кодом 401.
    
    Параметры:
    - api_key: строка, полученная из заголовка Authorization.
    - request: объект запроса FastAPI (необязательный).
    
    Возвращает:
    - api_key: строка, если ключ присутствует.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    return api_key

# router
app.include_router(chat_router, prefix="/chat", tags=["chat"], dependencies=[Depends(verify_api_key)])


@app.post("/sending_service") # без тестов 
async def send_notification(message: dict,target_service_url: str,api_key: str = Depends(api_key_header)):
    """
    Эндпоинт для отправки уведомлений на другой сервис
    {
        "message": "Hello from service A",
        "data": {
            "type": "alert",
            "priority": "high"
        },
        "target_service_url": "http://target-service:8001/notifications"
    }

    message - сообщение для отправки
    target_service_url - URL целевого сервиса
    api_key - API ключ для проверки
    data - данные для отправки
    data/type - тип сообщения
    data/priority - приоритет сообщения
    """

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    
    try:
        async with session.post(
            target_service_url,
            json=message
        ) as response:
            if response.status == 200:
                return {"status": "success", "message": "Notification sent successfully"}
            else:
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to send notification: {await response.text()}"
                )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {str(e)}"
        )

@app.get("/ping")
async def ping(api_key: str = Depends(api_key_header)):
    """Эндпоинт для проверки работоспособности сервиса"""
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    
    try:
        return {"status": "success", "message": "PONG!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def run_fastapi():
    import uvicorn
    uvicorn.run(
        "app.services.notification_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,           # Включаем автоматическую перезагрузку
        log_level="info"       # Уровень логирования
    )

