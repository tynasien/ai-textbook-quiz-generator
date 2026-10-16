# точка входа (enrty point)
# инициализация FastAPI приложения, настройка CORS и подключение маршрутов
from fastapi import FastAPI # для создания веб-приложения FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router

app = FastAPI( # главный объект приложения FastAPI
    title="AI Textbook Quiz Generator",
    description="Генерация интерактивных тестов по учебникам",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ # список разрешённых источников для CORS (Cross-Origin Resource Sharing)
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "AI Textbook Quiz Generator API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
