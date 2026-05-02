"""Development entry point for the provider service.

Runs the ASGI application using Uvicorn with hot-reload enabled.
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app.runner.asgi:app", host="0.0.0.0", port=8005, reload=True)
