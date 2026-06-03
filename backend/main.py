# Entry point — delegates to app/main.py
from app.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host='localhost',
        port=8000,
        reload=True
    )
