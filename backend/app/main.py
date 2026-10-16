
from fastapi import FastAPI

app = FastAPI(
    title="AI Textbook Quiz Generator",
    description="API для генерации интерактивных тестов по учебникам",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "AI Textbook Quiz Generator API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
