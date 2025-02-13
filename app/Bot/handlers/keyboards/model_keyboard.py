from aiogram.types import Message, InlineKeyboardMarkup
from app.core.logging import logs_bot

async def new_message(message: Message, text: str, keyword: InlineKeyboardMarkup) -> Message:
    """
    Отправляет новое сообщение с клавиатурой
    
    Параметры:
    - message: Объект сообщения для ответа
    - text: Текст сообщения
    - keyword: Клавиатура (InlineKeyboardMarkup или список кнопок)
    
    Возвращает:
    - Объект отправленного сообщения
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
    Обновляет существующее сообщение с клавиатурой
    
    Параметры:
    - message: Объект сообщения для обновления
    - text: Новый текст сообщения
    - keyword: Обновленная клавиатура (InlineKeyboardMarkup или список)
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