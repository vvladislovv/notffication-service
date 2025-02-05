from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from app.core.config import settings

security = HTTPBearer()

async def verify_token(request: Request):
    """
    Проверяет токен авторизации в заголовке запроса.
    Токен должен быть передан в заголовке Authorization: Bearer <token>
    """
    # Получаем токен из переменных окружения
    api_token = settings.config.api_token
    if not api_token:
        raise HTTPException(
            status_code=500,
            detail="Ошибка конфигурации сервера: API_TOKEN не настроен"
        )

    try:
        # Получаем токен из заголовка
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Неверный токен авторизации")

        # Убираем проверку на Bearer и берем токен как есть
        token = auth_header

        # Проверяем токен
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Токен авторизации не может быть пустым"
            )

        if token != api_token:
            raise HTTPException(
                status_code=401,
                detail="Неверный токен авторизации"
            )

        # Если всё хорошо, продолжаем обработку запроса
        return True

    except HTTPException:
        # Пробрасываем ошибки HTTPException как есть
        raise

    except Exception as e:
        # Логируем неожиданные ошибки
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при проверке авторизации"
        )