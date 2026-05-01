"""Development entry point for the payment service.

Starts the Uvicorn server with hot-reload enabled on port 8007.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.app.runner.asgi:app", host="0.0.0.0", port=8007, reload=True)
