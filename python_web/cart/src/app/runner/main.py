"""Development entry point for the cart service.

Starts the Uvicorn server with hot-reload enabled when executed directly.
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app.runner.asgi:app", host="0.0.0.0", port=8006, reload=True)
