from aiogram import Bot, Dispatcher
from app.core.config import settings
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.core.logging import logs_bot
from app.services import notification_service as services
from app.db.database import init_db
import asyncio

async def main():
    try:
        # Инициализация бота
        bot = Bot(token=settings.config.bot_token, 
                default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        
        
        # Инициализация диспетчера
        dp = Dispatcher()
        
        await bot.delete_webhook(drop_pending_updates=True)
        await logs_bot("info", "Сервис успешно запущен")    
        asyncio.create_task(services.run_fastapi())
        await init_db()
        
        # Запуск поллинга
        await dp.start_polling(bot)

    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as Error:
        asyncio.run(logs_bot("error", f"Bot work off.. {Error}"))
