from aiogram.types import Message, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardMarkup
from app.core.logging import logs_bot
from aiogram import Bot
from app.core.config import settings
import aiohttp

bot_message = Bot(token=settings.config.bot_token) 

async def new_message(message: Message, text: str, keyword: InlineKeyboardMarkup) -> Message:
    """
    Отправляет новое сообщение пользователю.
    
    Параметры:
    - message: объект Message, представляющий сообщение, на которое отвечает бот.
    - text: текст сообщения, которое будет отправлено.
    - keyword: объект InlineKeyboardMarkup или список, представляющий клавиатуру, которая будет прикреплена к сообщению.
    
    Возвращает:
    - объект Message, представляющий отправленное сообщение.
    """
    try:
        markup = None
        if keyword:
            if isinstance(keyword, (InlineKeyboardMarkup, list)):
                markup = keyword if isinstance(keyword, InlineKeyboardMarkup) else InlineKeyboardMarkup(inline_keyboard=keyword)
            else:
                markup = keyword.as_markup()
                
        return await message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        await logs_bot("error", f"Error in new_message: {e}")


async def update_message(message: Message, text: str, keyword: InlineKeyboardMarkup) -> Message:
    """
    Обновляет текст существующего сообщения.
    
    Параметры:
    - message: объект Message, представляющий сообщение, которое нужно обновить.
    - text: новый текст сообщения.
    - keyword: объект InlineKeyboardMarkup или список, представляющий клавиатуру, которая будет прикреплена к обновленному сообщению.
    """
    try:
        markup = None
        if keyword:
            if isinstance(keyword, InlineKeyboardMarkup):
                markup = keyword
            elif isinstance(keyword, list):
                markup = InlineKeyboardMarkup(inline_keyboard=keyword)
            else:
                markup = keyword.as_markup()
                
        await message.edit_text(
            text,
            parse_mode="HTML", 
            reply_markup=markup
        )
    except Exception as error:
        await logs_bot("error", f"Error in update_message: {error}")


async def send_message(chat_id: int, text: str, parse_mode: str = None):
    """
    Отправляет текстовое сообщение в указанный чат.
    """
    await bot_message.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode
    )

async def download_and_send_file(chat_id: int, file_url: str, send_func, caption: str = None, parse_mode: str = None):
    """
    Скачивает файл и отправляет его в чат используя указанную функцию отправки.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                print(response.status)
                if response.status != 200:
                    raise ValueError(f"Не удалось скачать файл: {response.status}")

                file_data = await response.read()  # Await the coroutine to get the file data

                # Создаем объект InputFile из скачанных данных
                file = BufferedInputFile(file_data, filename=file_url.split('/')[-1])
                print(file)
                # Отправляем файл
                result = await send_func(
                    chat_id=chat_id,
                    file=file,
                    caption=caption,
                    parse_mode=parse_mode
                )
                print(result)
                if not result:
                    raise ValueError("Ошибка при отправке файла.")
    except Exception as e:
        await logs_bot("error", f"Error downloading/sending file: {str(e)}")
        raise

async def send_photo(chat_id: int, photo: str, caption: str = None, parse_mode: str = None):
    """Отправляет фото в указанный чат."""
    await download_and_send_file(
        chat_id=chat_id,
        file_url=photo,
        send_func=bot_message.send_photo,
        caption=caption,
        parse_mode=parse_mode
    )

async def send_video(chat_id: int, video: str, caption: str = None, parse_mode: str = None):
    """Отправляет видео в указанный чат."""
    await download_and_send_file(
        chat_id=chat_id,
        file_url=video,
        send_func=bot_message.send_video,
        caption=caption,
        parse_mode=parse_mode
    )

async def send_animation(chat_id: int, animation: str, caption: str = None, parse_mode: str = None):
    """Отправляет анимацию в указанный чат."""
    await download_and_send_file(
        chat_id=chat_id,
        file_url=animation,
        send_func=bot_message.send_animation,
        caption=caption,
        parse_mode=parse_mode
    )

async def send_document(chat_id: int, document: str, caption: str = None, parse_mode: str = None):
    """Отправляет документ в указанный чат."""
    await download_and_send_file(
        chat_id=chat_id,
        file_url=document,
        send_func=bot_message.send_document,
        caption=caption,
        parse_mode=parse_mode
    )