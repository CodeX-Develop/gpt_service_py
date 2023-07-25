from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers import chat, completion
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from .db.factory import DBType, get_database_factory

import json


class APIBuilder:
    def __init__(self):
        self.app = FastAPI()
        self.templates = Jinja2Templates("app/templates")

    def add_static_files(self):
        self.app.mount("/static", StaticFiles(directory="app/static"), name="static")
        return self

    def add_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://127.0.0.1"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return self

    def add_routers(self):
        self.app.include_router(chat.router, prefix="/api")
        self.app.include_router(completion.router, prefix="/api")
        return self

    def add_main_route(self):
        @self.app.get("/", response_class=HTMLResponse)
        async def root(request: Request):
            nombre = "Usuario"
            return self.templates.TemplateResponse("index.html", {"request": request, "nombre": nombre})
        return self

    def build(self):
        return self.app
    
def main():
    with open('config.json') as f:
        config = json.load(f)

    db_type = DBType(config['db_type'])
    connection = config['connection']
    db_factory = get_database_factory(db_type, connection)

    app = (
        APIBuilder()
        .add_static_files()
        .add_cors()
        .add_routers()
        .add_main_route()
        .build()
    )
    app.state.db = db_factory  # Aquí asignas la factory de la base de datos a tu aplicación

    return app

app = main()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)