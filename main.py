
import time
from contextlib import asynccontextmanager
from sys import prefix

from app.utils.database import init_db

#import calls
import random
from datetime import datetime
from typing import Dict

import requests
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, RedirectResponse, FileResponse
from starlette.templating import Jinja2Templates
from app.models.models import User
from app.routers.user_routes import router as user_router
from app.routers.authenticate import router as auth_router
from app.routers.astrologer import  router as astro_router
from app.routers.astro_online import router as astro_online_router
# from app.routers.chat import router as chat_router
from app.utils.database import init_db, get_db
from app.routers.availability import router as availability_router
from app.routers.category import router as category_router
from app.routers.followers import router as follower_router
from app.routers.customerdetails import router as customer_router
from app.routers.language import router as language_router
from app.routers.skill import router as skill_router
from app.routers.userdevicedetails import router as user_device_router
from app.routers.userreviews import router as user_review_router
from app.routers.userwallets import router as wallet_router
from app.routers.wallettransaction import router as wallet_transaction_router
from app.routers.chat import router as chat_router
from app.routers.block import router as  block_router
from  app.routers.calls import router as calls_router
from app.routers.notification import router as notification_router
from app.routers.notification_ws import router as ws_notification_router
from app.routers.rating import router as rating_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Run on startup
    init_db()
    yield
    # ✅ Run on shutdown (if needed)


# ✅ Initialize FastAPI with Lifespan



app = FastAPI(
    title="AstroOnline API",
    description="API for Umeed WebApp.",
    version="1.0.0",
    lifespan=lifespan,
)

# ✅ Include User Routes
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="static/dist/assets"), name="assets")

templates = Jinja2Templates(directory="templates")
import os
SECRET_KEY = os.urandom(24).hex()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins={"*"},
    #allow_origins=["http://localhost:8080", "https://dash.gurutvapay.com", "https://www.templamart.com"],  # Allow requests from React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


app.include_router(auth_router, prefix="/api/v1/auth", tags=["Login"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(astro_router, prefix="/api/v1/astro", tags=["Astro"])


app.include_router(availability_router, prefix="/api/v1/availability", tags=["Availability"])
app.include_router(category_router, prefix="/api/v1/categories", tags=["Astrologer Categories"])
app.include_router(follower_router, prefix="/api/v1", tags=["Followers"])
app.include_router(customer_router, prefix="/api/v1", tags=["CustomerDetails"])
app.include_router(language_router, prefix="/api/v1", tags=["Languages"])
app.include_router(skill_router, prefix="/api/v1", tags=["Skills"])
app.include_router(user_device_router, prefix="/api/v1", tags=["User Device Details"])
app.include_router(user_review_router, prefix="/api/v1", tags=["User Reviews"])
app.include_router(wallet_router, prefix="/api/v1", tags=["User Wallets"])
app.include_router(wallet_transaction_router, prefix="/api/v1", tags=["Wallet Transactions"])
app.include_router(chat_router,prefix="/chat", tags=["Chat Router"])
app.include_router(block_router, prefix="/api/v1/block", tags=["Astrologer block/report"])
app.include_router(calls_router, prefix="/api/v1", tags=["Calls Request"])
app.include_router(notification_router,prefix="/api/v1",tags=["Notification request"])
app.include_router(ws_notification_router,prefix="/ws", tags=["WebSocket"])
app.include_router(rating_router,prefix="/ratings", tags=["Ratings"])
#app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(astro_online_router,prefix="/astro_online",tags=["Astro Online"])


from app.routers import customer_notification_router,astrologer_notification_router

app.include_router(customer_notification_router.router,prefix="/Customer_notification",tags=["Customer Notification"])
app.include_router(astrologer_notification_router.router,prefix="/Astrologer_notification",tags=["Astrologer Notification"])
from app.routers import admin
app.include_router(admin.router)


@app.middleware("http")
async def log_time(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    return response


# ✅ Basic Root Check
@app.get("/")
def index():
    return {"message": "🚀 Jyotishi FastAPI backend is running successfully!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="debug")




