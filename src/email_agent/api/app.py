from typing import Annotated, Literal

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from email_agent.config import Settings, load_settings


class HealthResponse(BaseModel):
    status: Literal["ok"]


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or load_settings()

    app = FastAPI(title="Email Agent API", version="0.1.0")

    def get_settings() -> Settings:
        return resolved_settings

    @app.get("/health", response_model=HealthResponse)
    def health(
        _settings: Annotated[Settings, Depends(get_settings)],
    ) -> HealthResponse:
        return HealthResponse(status="ok")

    return app
