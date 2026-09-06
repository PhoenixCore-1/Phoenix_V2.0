"""Local development launcher for the Phoenix landing application."""

import uvicorn


if __name__ == "__main__":
    uvicorn.run("phoenix_system.web.app:app", host="127.0.0.1", port=8000, reload=True)
