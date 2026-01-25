from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from app.database import init_database

from app.core.operations import get_result
from app.schema import OperationRequest, OperationResponse


from app.settings import get_settings


# Load application settings (model configs, prompts, etc.)
USER_SETTINGS = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database before starting the app"""
    init_database()
    yield

# Return user settings for now, over ride this as needed
def get_route_configs() -> dict:
    """Return the retrieved user settings"""
    return USER_SETTINGS

# Define a general request handling method 
def handle_response(operation: str, request: dict, configs: dict) -> dict:
    """Supply user request and app configs to the requested operation"""
    # Define BaseResponse return values
    success, result, meta = True, {}, {}
    try:
        # Get all requested enum operations results
        result = get_result(operation, configs, request.model_dump())
        # TODO: Add logging and database call here
    except Exception as e:
        # Handle all exceptions
        meta[type(e).__name__] = str(e)
        success = False

    return dict(id=request.id, success=success, result=result, metadata=meta)


# Initialize the FastAPI app instance
app = FastAPI(
    lifespan=lifespan, 
    title=USER_SETTINGS.name, 
    version=USER_SETTINGS.version, 
    debug=USER_SETTINGS.debug
)

@app.post("/", response_model=OperationResponse)
async def post_metrics(request: OperationRequest):
    """Return a response including the metrics of the specified request types"""
    return OperationResponse(success=True, result={"message": "Welcome to the NLP Service API!"})

# Define all available core routes below:
for route_prefix in ['metrics', 'summary', 'tags']:
    @app.post(f"/{route_prefix}/", response_model=OperationResponse)
    async def post_metrics(request: OperationRequest, configs: dict=Depends(get_route_configs)):
        """Return a response including the metrics of the specified request types"""
        return handle_response(route_prefix, request, configs.get(route_prefix, {}))
