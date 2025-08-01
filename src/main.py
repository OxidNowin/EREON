import uvicorn

from core.config import settings


def main():
    uvicorn.run(
        app="server.server:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.reload,
        workers=settings.workers,
    )


if __name__ == "__main__":
    main()
