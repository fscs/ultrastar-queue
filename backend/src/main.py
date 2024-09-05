import uvicorn
from .app.main import app
from .app.config import settings

if __name__ == "__main__":
    uvicorn.run(app, host=settings.BACKEND_HOST, port=settings.BACKEND_PORT)
