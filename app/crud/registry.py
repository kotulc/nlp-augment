"""Registry mapping operation names to CRUD handler callables.

Each handler receives:
  - session: Session (active DB session for the transaction)
  - request: request object with content, parameters, etc.
  - result: dict output from core.operations.get_result()

Handlers should persist the result to the DB and return the persisted record(s).
"""

from typing import Callable, Any
from sqlmodel import Session

from app.crud.metrics import create_metrics_for_section
from app.schemas.metrics import MetricsRequest
from app.schemas.summary import SummaryRequest
from app.schemas.tags import TagsRequest


def metrics_handler(session: Session, request: MetricsRequest, result: dict) -> Any:
    """Persist metrics results for a section."""
    # For now, return the result dict; in future: create/update Section + Metric records
    # Example: if request has section_id, call create_metrics_for_section
    return {"operation": "metrics", "result": result}


def summary_handler(session: Session, request: SummaryRequest, result: dict) -> Any:
    """Persist summary results for a section."""
    # TODO: implement Section + Summary record creation
    return {"operation": "summary", "result": result}


def tags_handler(session: Session, request: TagsRequest, result: dict) -> Any:
    """Persist tag results for a section."""
    # TODO: implement Section + Tag record creation
    return {"operation": "tags", "result": result}


# Registry mapping operation name -> handler callable
REGISTRY: dict[str, Callable[[Session, Any, dict], Any]] = {
    "metrics": metrics_handler,
    "summary": summary_handler,
    "tags": tags_handler,
}
