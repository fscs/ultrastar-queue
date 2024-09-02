import uvicorn
from fastapi_backend.src.app import app

if __name__ == "__main__":
    uvicorn.run(app)
