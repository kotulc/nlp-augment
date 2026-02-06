import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from app.core.operations import get_result
from app.crud.database import init_database, update_database
from app.schemas import MetricsRequest, MetricsResponse, SummaryRequest, SummaryResponse, TagsRequest, TagsResponse
from app.settings import get_settings


# Load application settings (model configs, prompts, etc.)
USER_SETTINGS = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database before starting the app"""
    init_database()
    yield

# Return user settings for now, over ride this as needed
def get_route_configs() -> dict:
    """Return the retrieved user settings"""
    return USER_SETTINGS

# TODO: Update return values to reflect response types
# Define a general request handling method 
def handle_response(operation: str, request: dict, configs: dict) -> dict:
    """Supply user request and app configs to the requested operation"""
    # Define BaseResponse return values
    record = {}
    try:
        # Get all requested operations results and store them in the database
        result = get_result(operation, configs, request.model_dump())
        record = update_database(operation, result)
    except Exception as e:
        # Handle all exceptions
        logger.exception(f"Operation {operation} failed: {type(e).__name__} - {str(e)}")

    return record


# Initialize the FastAPI app instance
app = FastAPI(
    lifespan=lifespan, 
    title=USER_SETTINGS.name, 
    version=USER_SETTINGS.version, 
)

@app.post(f"/metrics/", response_model=MetricsResponse)
async def post_metrics(request: MetricsRequest, configs: dict=Depends(get_route_configs)):
    """Return a response including the metrics of the specified request types"""
    return handle_response('metrics', request, configs)

@app.post(f"/summary/", response_model=SummaryResponse)
async def post_summary(request: SummaryRequest, configs: dict=Depends(get_route_configs)):
    """Return a response including the metrics of the specified request types"""
    return handle_response('summary', request, configs)

@app.post(f"/tags/", response_model=TagsResponse)
async def post_tags(request: TagsRequest, configs: dict=Depends(get_route_configs)):
    """Return a response including the metrics of the specified request types"""
    return handle_response('tags', request, configs)
