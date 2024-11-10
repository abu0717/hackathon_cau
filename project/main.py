import uvicorn
from fastapi import FastAPI, Path, HTTPException, status
from fastapi.responses import FileResponse
from routers import router
from settings import settings
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists('media/images'):
        os.makedirs('media/images')
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get('/media/images/{file_path}', response_class=FileResponse)
async def media(file_path: str = Path()):
    file_path = f"media/images/{file_path}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(file_path)


@app.get("/")
async def home():
    return "hello"




def main():
    uvicorn.run(app=app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
