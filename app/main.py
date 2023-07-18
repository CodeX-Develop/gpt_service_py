from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import recommendations
from .routers import chat
from fastapi.responses import HTMLResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite las solicitudes desde este origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

# API
app.include_router(chat.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")

# add router main with hello world
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    nombre = "Usuario"
    with open("./templates/index.html", "r") as f:
        return f.read()
