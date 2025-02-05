from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from typing import Any, List, Optional
import os


engine = create_async_engine(settings.config.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def init_db():
    """
    Инициализирует базу данных, создавая необходимые директории и таблицы.
    
    Проверяет наличие директории для базы данных и создает её, если она отсутствует.
    Затем выполняет создание всех таблиц, определенных в модели базы данных.
    
    Возвращает:
        None: Функция не возвращает значения.
    """
    db_dir = os.path.dirname(settings.config.DATABASE_URL.replace('sqlite:///', ''))
    if db_dir and not os.path.exists(db_dir) and 'sandbox/db' not in db_dir:
        os.makedirs(db_dir)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_to_table(table_class: Base, data: dict) -> Any:
    """
    Общая функция для добавления данных в любую таблицу с проверкой  
    
    Аргументы:
        table_class: Base - Класс модели SQLAlchemy
        data: dict - Данные для вставки
        
    Возвращает:
        Созданную или существующую запись или False, если не удалось вставить данные
    """
    
    async with async_session() as session:
        if 'user_id' in data:
            # Проверяем, существует ли запись с этим chat_id
            existing = await session.execute(
                select(table_class).where(
                    table_class.user_id == data['user_id']
                )
            )

            existing_record: Optional[Base] = existing.scalar_one_or_none()
            
            if existing_record:
                # Обновляем существующую запись
                for key, value in data.items():
                    setattr(existing_record, key, value)
                await session.commit()
                return existing_record
        
        # Проверяем, можно ли создать новую запись
        try:
            new_record: Base = table_class(**data)
            session.add(new_record)
            await session.commit()
            await session.refresh(new_record)
            return new_record
        except Exception as e:
            # Если не удалось вставить данные, возвращаем False
            #await logs_bot("error", f"Database insertion error: {str(e)}")
            print(f"Database insertion error: {str(e)}")
            return False

async def get_table_data(table_class: Base) -> List[dict]:
    """
    Функция для получения данных из указанной таблицы в формате JSON.
    
    Аргументы:
        table_class: Base - Класс модели SQLAlchemy
        
    Возвращает:
        Список словарей с данными из таблицы
    """
    async with async_session() as session:
        result = await session.execute(select(table_class))
        records: List[Base] = result.scalars().all()
        return [record.__dict__ for record in records]

async def delete_table(table_class: Base, user_id: str) -> bool:
    """
    Удаляет чат из базы данных по его идентификатору.
    
    Аргументы:
        chat_id: str - Уникальный идентификатор чата для удаления
        table_class: Base - Класс модели SQLAlchemy для удаления
        
    Возвращает:
        bool: True если чат был успешно удален, False если чат не найден
    """
    async with async_session() as session:
        try:
            # Находим чат по ID
            chat = await session.scalar(
                select(table_class).where(table_class.user_id == user_id)
            )
            if chat is None:
                return False  # Чат не найден
            
            # Удаляем чат
            await session.delete(chat)
            await session.commit()
            return True  # Успешно удалено

        except Exception as e:
            print(f"Error occurred while deleting chat: {e}")
            return False  # Возвращаем False в случае ошибки
            