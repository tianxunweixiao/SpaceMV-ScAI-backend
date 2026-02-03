import uvicorn
from app_factory import create_app

# create app
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001
    )
