from app.db.models import LogsJson
from app.db.database import add_to_table


async def logs_bot(TypeLog: str, Text: str) -> None:
    """
    Логирует сообщения в базу данных.

    Аргументы:
        TypeLog: str - Уровень логирования (например, "error", "warning", "info", "debug").
        Text: str - Сообщение для логирования.
    """
    valid_log_types = ["error", "warning", "info", "debug"]
    if TypeLog.lower() not in valid_log_types:
        TypeLog = "warning"  

    log_entry = LogsJson(data={"level": TypeLog, "message": Text})
    await add_to_table(LogsJson, {"data": log_entry.data})  # Оборачиваем log_entry.data в словарь
