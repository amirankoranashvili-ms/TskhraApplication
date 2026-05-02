"""Development entry point that starts the admin service via uvicorn."""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app.runner.asgi:app", host="0.0.0.0", port=8003, reload=True)
