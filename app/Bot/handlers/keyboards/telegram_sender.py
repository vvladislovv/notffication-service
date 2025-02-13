from aiogram import Bot

import aiohttp
from app.core.logging import logs_bot
from typing import Optional
from aiogram.types import BufferedInputFile
from app.core.config import settings

bot = Bot(token=settings.config.bot_token)


async def send_message(chat_id: int, text: str, parse_mode: Optional[str] = None):
    """
    Отправляет текстовое сообщение в указанный чат.
    
    Параметры:
    - bot: экземпляр бота Aiogram.
    - chat_id: ID чата, куда будет отправлено сообщение.
    - text: текст сообщения, который нужно отправить.
    - parse_mode: режим парсинга текста (например, HTML или Markdown).
    """
    if text is None:
        raise ValueError("The 'text' argument is required and cannot be None.")
    
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML"
    )


async def download_file(url: str) -> tuple[bytes, str, str]:
    """
    Скачивает файл по URL с отключенной SSL-проверкой.
    
    Параметры:
    - url: URL файла, который нужно скачать.
    
    Возвращает:
    - кортеж из байтовых данных файла, его content-type и расширения.
    """
    connector = aiohttp.TCPConnector(ssl=False)  # Отключаем SSL проверку
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            if response.status != 200:
                error_text = await response.text()
                await logs_bot("error", f"Ошибка скачивания: {response.status}, Ответ: {error_text}")
                raise ValueError(f"Ошибка загрузки: {response.status}")
                
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            ext = get_file_extension(content_type)
            return await response.read(), content_type, ext

def get_file_extension(content_type: str) -> str:
    """
    Определяет расширение файла на основе content-type.
    
    Параметры:
    - content_type: тип содержимого файла (например, 'image/jpeg').
    
    Возвращает:
    - строку с расширением файла.
    """
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
    Универсальная функция для отправки медиа-файлов.
    
    Параметры:
    - chat_id: ID чата, куда будет отправлено медиа.
    - file_url: URL медиа-файла, который нужно отправить.
    - media_type: тип медиа (например, 'photo', 'video').
    - caption: подпись к медиа (опционально).
    - parse_mode: режим парсинга текста (по умолчанию HTML).
    
    Возвращает:
    - ответ от Telegram API после отправки медиа.
    """
    try:
        file_data, content_type, ext = await download_file(file_url)
        file_name = f"file{ext}"
        
        input_file = BufferedInputFile(file_data, filename=file_name)
        
        methods = {
            'photo': bot.send_photo,
            'video': bot.send_video,
            'animation': bot.send_animation,
            'document': bot.send_document
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
        
        if media_type == 'video':
            params.update({'supports_streaming': True, 'width': 1920, 'height': 1080})
            
        response = await send_method(**params)
        if not response:
            raise ValueError(f"Telegram API не вернул ответ при отправке {media_type}")
            
        return response
        
    except Exception as e:
        error_msg = f"Ошибка при отправке {media_type}: {str(e)}"
        await logs_bot("error", error_msg)
        raise ValueError(error_msg)

# Специализированные функции отправки медиа
async def send_photo(chat_id: int, photo: str, caption: str = "", parse_mode: str = "HTML"):
    """
    Отправляет фотографию в указанный чат.
    
    Параметры:
    - chat_id: ID чата, куда будет отправлена фотография.
    - photo: URL или путь к фотографии.
    - caption: подпись к фотографии (опционально).
    - parse_mode: режим парсинга текста (по умолчанию HTML).
    """
    return await send_media(chat_id, photo, 'photo', caption, parse_mode)

async def send_video(chat_id: int, video: str, caption: str = None, parse_mode: str = "HTML"):
    """
    Отправляет видео в указанный чат.
    
    Параметры:
    - chat_id: ID чата, куда будет отправлено видео.
    - video: URL или путь к видео.
    - caption: подпись к видео (опционально).
    - parse_mode: режим парсинга текста (по умолчанию HTML).
    """
    return await send_media(chat_id, video, 'video', caption, parse_mode)

async def send_animation(chat_id: int, animation: str, caption: str = "", parse_mode: str = "HTML"):
    """
    Отправляет анимацию в указанный чат.
    
    Параметры:
    - chat_id: ID чата, куда будет отправлена анимация.
    - animation: URL или путь к анимации.
    - caption: подпись к анимации (опционально).
    - parse_mode: режим парсинга текста (по умолчанию HTML).
    """
    return await send_media(chat_id, animation, 'animation', caption, parse_mode)

async def send_document(chat_id: int, document: str, caption: str = None, parse_mode: str = "HTML"):
    """
    Отправляет документ в указанный чат.
    
    Параметры:
    - chat_id: ID чата, куда будет отправлен документ.
    - document: URL или путь к документу.
    - caption: подпись к документу (опционально).
    - parse_mode: режим парсинга текста (по умолчанию HTML).
    """
    return await send_media(chat_id, document, 'document', caption, parse_mode)