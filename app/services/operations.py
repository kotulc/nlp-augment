"""Orchestrator for handling API requests: call core operations, dispatch to CRUD handlers, manage transactions."""

import logging
from typing import Any, Dict

from sqlmodel import Session

from app.core.operations import get_result
from app.crud.registry import REGISTRY
from app.crud.database import store_result
from app.settings import get_settings


logger = logging.getLogger(__name__)
USER_SETTINGS = get_settings()


def handle_request(operation: str, request: Any, configs: Dict[str, Any], session: Session) -> Dict[str, Any]:
    """Orchestrate a request: call get_result, dispatch handler, manage transaction.
    
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
        # 1. Call core operation to compute results
        result = get_result(operation, configs, request.model_dump())
        
        # 2. Dispatch to registered handler (if exists) to persist to DB
        handler = REGISTRY.get(operation)
        if handler:
            persisted = handler(session, request, result)
            session.commit()
            return persisted
        
        # 3. Fallback: use generic store_result for audit
        logger.warning(f"No handler registered for operation: {operation}, using fallback store_result")
        store_result(operation, result)
        session.commit()
        return {"operation": operation, "result": result}
        
    except Exception as e:
        logger.exception(f"Operation {operation} failed: {type(e).__name__} - {str(e)}")
        session.rollback()
        raise
