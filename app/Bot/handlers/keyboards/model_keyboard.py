from aiogram.types import Message, BufferedInputFile, FSInputFile, InputFile
from aiogram.utils.keyboard import InlineKeyboardMarkup
from app.core.logging import logs_bot
from aiogram import Bot
from app.core.config import settings
import aiohttp
from app.core.ssl_config import create_ssl_context, get_connector
import tempfile
import os
import re
from io import BytesIO
from typing import Optional, Union

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

async def get_google_drive_direct_url(file_url: str) -> str:
    """
    Получает прямую ссылку на скачивание файла с Google Drive
    """
    if "drive.google.com" not in file_url:
        return file_url
        
    file_id = None
    
    # Извлекаем ID файла из разных форматов URL Google Drive
    if "/file/d/" in file_url:
        file_id = file_url.split("/file/d/")[1].split("/")[0]
    elif "id=" in file_url:
        file_id = file_url.split("id=")[1].split("&")[0]
        
    if not file_id:
        raise ValueError("Не удалось получить ID файла из URL Google Drive")
        
    return f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

async def download_file(url: str) -> tuple[bytes, str, str]:
    """
    Скачивает файл по URL и возвращает его содержимое и тип
    
    Args:
        url: URL файла для скачивания
        
    Returns:
        tuple: (файл в байтах, content_type, расширение файла)
    """
    ssl_context = create_ssl_context(url)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.get(url) as response:
            if response.status != 200:
                error_text = await response.text()
                await logs_bot("error", f"Download failed. Status: {response.status}, Response: {error_text}")
                raise ValueError(f"Не удалось скачать файл: {url}")
                
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            ext = get_file_extension(content_type)
            return await response.read(), content_type, ext

def get_file_extension(content_type: str) -> str:
    """Определяет расширение файла на основе content-type"""
    if 'video' in content_type: return '.mp4'
    if 'image/gif' in content_type: return '.gif'
    if 'image' in content_type: return '.jpg'
    return '.dat'

async def send_media(
    chat_id: int,
    file_url: str,
    media_type: str,
    caption: Optional[str] = None,
    parse_mode: str = "HTML"
) -> dict:
    """
    Универсальная функция для отправки медиа-файлов
    
    Args:
        chat_id: ID чата
        file_url: URL медиа-файла
        media_type: Тип медиа (photo/video/animation/document)
        caption: Подпись к медиа
        parse_mode: Режим форматирования текста
    """
    try:
        file_data, content_type, ext = await download_file(file_url)
        file_name = f"file{ext}"
        
        input_file = BufferedInputFile(file_data, filename=file_name)
        
        methods = {
            'photo': bot_message.send_photo,
            'video': bot_message.send_video,
            'animation': bot_message.send_animation,
            'document': bot_message.send_document
        }
        
        send_method = methods.get(media_type)
        if not send_method:
            raise ValueError(f"Неподдерживаемый тип медиа: {media_type}")
            
        params = {
            'chat_id': chat_id,
            media_type: input_file,
            'caption': caption,
            'parse_mode': parse_mode
        }
        
        # Добавляем специальные параметры для видео
        if media_type == 'video':
            params.update({'supports_streaming': True, 'width': 1280, 'height': 720})
            
        response = await send_method(**params)
        if not response:
            raise ValueError(f"Telegram API не вернул ответ при отправке {media_type}")
            
        return response
        
    except Exception as e:
        error_msg = f"Ошибка при отправке {media_type}: {str(e)}"
        await logs_bot("error", error_msg)
        raise ValueError(error_msg)

# Создаем специализированные функции на основе универсальной
async def send_photo(chat_id: int, photo: str, caption: str = "", parse_mode: str = "HTML"):
    """Отправляет фото в чат"""
    return await send_media(chat_id, photo, 'photo', caption, parse_mode)

async def send_video(chat_id: int, video: str, caption: str = None, parse_mode: str = "HTML"):
    """Отправляет видео в чат"""
    return await send_media(chat_id, video, 'video', caption, parse_mode)

async def send_animation(chat_id: int, animation: str, caption: str = "", parse_mode: str = "HTML"):
    """Отправляет GIF-анимацию в чат"""
    return await send_media(chat_id, animation, 'animation', caption, parse_mode)

async def send_document(chat_id: int, document: str, caption: str = None, parse_mode: str = "HTML"):
    """Отправляет документ в чат"""
    return await send_media(chat_id, document, 'document', caption, parse_mode)