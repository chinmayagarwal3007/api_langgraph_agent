from fastapi import FastAPI
from chat.router import router as chat_router
from auth.router import router as auth_router

app = FastAPI()


app.include_router(chat_router)
app.include_router(auth_router)