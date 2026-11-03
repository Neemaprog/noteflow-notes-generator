from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.password_reset import router as password_reset_router
from app.routers.conversations import router as conversations_router
from app.routers.documents import router as documents_router
from app.routers.history import router as history_router
from app.routers.notes import router as notes_router
from app.routers.processing_jobs import router as processing_jobs_router
from app.routers.settings import router as settings_router
from app.routers.visuals import router as visuals_router

app = FastAPI(title="AI Notes Generator API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(password_reset_router)
app.include_router(documents_router)
app.include_router(conversations_router)
app.include_router(notes_router)
app.include_router(visuals_router)
app.include_router(processing_jobs_router)
app.include_router(history_router)
app.include_router(settings_router)

@app.get("/")
def read_root():
    return {"message": "AI Notes Generator backend is running"}