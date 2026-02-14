"""Orchestrator for handling API requests: call core operations, dispatch to CRUD handlers, manage transactions."""

import logging

from typing import Any
from sqlmodel import Session

from app.crud.metrics import handle_metrics_request


LOGGER = logging.getLogger(__name__)

# Registry mapping operation name to (core handler, crud handler)
REGISTRY: dict[str, callable] = {
    "metrics": handle_metrics_request,
    "summary": None,
    "tags": None,
}


def handle_request(operation: str, request: Any, configs: dict, session: Session) -> dict:
    """Orchestrate a request: call handler and manage the transaction.
    
    Args:
        operation: operation name ("metrics", "summary", "tags")
        request: Pydantic request model instance
        configs: app configs from settings
        session: active SQLModel Session for DB transaction
    
    Returns:
        response dict with operation results
    
    Raises:
        Exception: propagates from core operations or CRUD handlers
    """
    result = {}

    try:
        # Dispatch to registered handler and optionally persist to DB
        request_handler = REGISTRY.get(operation)
        result = request_handler(session, request, configs)
        LOGGER.info(f"Operation {operation} completed successfully.")

    except Exception as e:
        LOGGER.exception(f"Operation {operation} failed: {type(e).__name__} - {str(e)}")
        session.rollback()

    session.close()
    return result
