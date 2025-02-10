import ssl
import certifi
from urllib.parse import urlparse
from aiohttp import TCPConnector

def create_ssl_context(url: str = None):
    """
    Создает SSL контекст с учетом домена
    
    Args:
        url (str): URL для проверки домена
    """
    # Для Google Drive отключаем проверку SSL
    if url and "drive.google.com" in urlparse(url).netloc:
        ssl_context = ssl._create_unverified_context()
    else:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ssl_context 

def get_ssl_context():
    """
    Создает и возвращает настроенный SSL контекст с корректными сертификатами
    """
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ssl_context

def get_connector():
    """
    Возвращает TCP коннектор с настроенным SSL контекстом
    """
    return TCPConnector(ssl=get_ssl_context()) 