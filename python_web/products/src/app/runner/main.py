"""Development server entry point.

Runs the products service using Uvicorn with auto-reload enabled
when executed directly as a script.
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app.runner.asgi:app", host="0.0.0.0", port=8004, reload=True)
