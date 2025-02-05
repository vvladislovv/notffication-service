import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from app.services.chat import router

# Создаем экземпляр FastAPI и подключаем маршрутизатор
app = FastAPI()
app.include_router(router)

@pytest.mark.asyncio
async def test_send_text_message():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/message_answer", json={
            "chat_id": "1",
            "type": "text",
            "content": "Hello, this is a text message!"
        })
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Контент успешно отправлен"}

@pytest.mark.asyncio
async def test_send_photo_message():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/message_answer", json={
            "chat_id": "1",
            "type": "photo",
            "content": "http://example.com/photo.jpg",
            "caption": "This is a photo"
        })
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Контент успешно отправлен"}

@pytest.mark.asyncio
async def test_send_video_message():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/message_answer", json={
            "chat_id": "1",
            "type": "video",
            "content": "http://example.com/video.mp4",
            "caption": "This is a video"
        })
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Контент успешно отправлен"}

@pytest.mark.asyncio
async def test_send_animation_message():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/message_answer", json={
            "chat_id": "1",
            "type": "animation",
            "content": "http://example.com/animation.gif",
            "caption": "This is an animation"
        })
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Контент успешно отправлен"}

@pytest.mark.asyncio
async def test_send_document_message():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/message_answer", json={
            "chat_id": "1",
            "type": "document",
            "content": "http://example.com/document.pdf",
            "caption": "This is a document"
        })
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Контент успешно отправлен"}

@pytest.mark.asyncio
async def test_ping():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "PONG!"} 