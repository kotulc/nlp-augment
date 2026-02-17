from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.core.operations import get_metrics
from app.crud.tables import Metric
from app.schemas.metrics import MetricsRequest


def get_metric(session: Session, section_id: UUID, name: str) -> Metric:
    """Return a single Metric by section and name, or None if not found."""
    statement = select(Metric).where(Metric.section_id == section_id, Metric.name == name)
    return session.exec(statement).first()


def add_metric(session: Session, section_id: UUID, name: str, value: float) -> Metric:
    """Create a new Metric or overwrite an existing one (section_id + name key).

    This satisfies the requirement "A new metric generated for a Section should overwrite
    an existing metric with the name." The function commits and refreshes the instance.
    """
    existing = get_metric(session, section_id, name)
    if existing:
        existing.value = float(value)
        existing.recorded_at = datetime.now()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    metric = Metric(section_id=section_id, name=name, value=float(value))
    session.add(metric)
    session.commit()
    session.refresh(metric)
    return metric


def delete_metric(session: Session, section_id: UUID, name: str) -> bool:
    """Delete a metric by section and name. Returns True if deleted."""
    existing = get_metric(session, section_id, name)
    if not existing:
        return False
    
    session.delete(existing)
    session.commit()
    return True


def list_section_metrics(session: Session, section_id: UUID) -> List[Metric]:
    """Return all Metric records for a given section."""
    statement = select(Metric).where(Metric.section_id == section_id)
    return session.exec(statement).all()


def handle_metrics_request(session: Session, request: MetricsRequest, configs: dict) -> List[Metric]:
    """Compute metrics using core.get_metrics and upsert them for the given section.

    If no session is provided, this helper will open its own `Session(engine)`.
    Returns the list of Metric records objects.
    """
    results = get_metrics(request.content, request.metrics)
    records: List[Metric] = []
    
    for name, value in results.items():
        metric = add_metric(session, request.section_id, name, value)
        records.append(metric)
    
    return records
