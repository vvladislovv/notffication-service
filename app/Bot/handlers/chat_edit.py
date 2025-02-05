from aiogram import Router, types
from aiogram.filters import CommandStart
from app.Bot.handlers.keyboards import model_keyboard
from app.db.models import User
from app.db.database import add_to_table

router = Router(name=__name__)

@router.message(CommandStart())
async def command_start(message: types.Message):
    """
    Обрабатывает команду /start от пользователя.
    
    Эта функция отправляет приветственное сообщение пользователю и сохраняет информацию о пользователе в базе данных.
    """
    await model_keyboard.new_message(message, 'Привет, я бот для управления вашим ботом. Я могу помочь вам управлять вашим ботом.', None)

    user_data = {
        'user_id': message.from_user.id,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }

    await add_to_table(User, user_data)
