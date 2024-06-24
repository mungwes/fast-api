from fastapi import FastAPI
from app import models
from app.database import engine
from .routers import user, post, auth,vote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"] # if you want the API to be open
#origins = ["https://www.google.com", "https://www.youtube.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

 

