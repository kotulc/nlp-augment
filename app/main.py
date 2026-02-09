import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session

from app.crud.database import init_database, get_session
from app.schemas.metrics import MetricsRequest, MetricsResponse
from app.schemas.summary import SummaryRequest, SummaryResponse
from app.schemas.tags import TagsRequest, TagsResponse
from app.services.operations import handle_request
from app.settings import get_settings


# Load application settings (model configs, prompts, etc.)
USER_SETTINGS = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database before starting the app"""
    init_database()
    yield

# Return user settings for now, override this as needed
def get_route_configs() -> dict:
    """Return the retrieved user settings"""
    return USER_SETTINGS


# Initialize the FastAPI app instance
app = FastAPI(
    lifespan=lifespan, 
    title=USER_SETTINGS.name, 
    version=USER_SETTINGS.version, 
)

@app.post(f"/metrics/", response_model=MetricsResponse)
async def post_metrics(
        request: MetricsRequest,
        configs: dict = Depends(get_route_configs),
        session: Session = Depends(get_session),
    ):
    """Return a response including the metrics of the specified request types"""
    return handle_request('metrics', request, configs, session)

@app.post(f"/summary/", response_model=SummaryResponse)
async def post_summary(
        request: SummaryRequest,
        configs: dict = Depends(get_route_configs),
        session: Session = Depends(get_session),
    ):
    """Return a response including the summary of the specified content"""
    return handle_request('summary', request, configs, session)

@app.post(f"/tags/", response_model=TagsResponse)
async def post_tags(
        request: TagsRequest,
        configs: dict = Depends(get_route_configs),
        session: Session = Depends(get_session),
    ):
    """Return a response including the tags extracted from the specified content"""
    return handle_request('tags', request, configs, session)
