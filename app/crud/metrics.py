from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.core.operations import get_metrics
from app.crud.tables import Metric
from app.crud.database import engine


def get_metrics_from_core(content: str, metrics: List[str] | None = None) -> Dict[str, float]:
    """Call core.get_metrics and return the raw mapping of name->value."""
    return get_metrics(content, metrics)


def get_metric_by_name(session: Session, section_id: UUID, name: str) -> Optional[Metric]:
    """Return a single Metric by section and name, or None if not found."""
    statement = select(Metric).where(Metric.section_id == section_id, Metric.name == name)
    return session.exec(statement).first()


def list_metrics_for_section(session: Session, section_id: UUID) -> List[Metric]:
    """Return all Metric records for a given section."""
    statement = select(Metric).where(Metric.section_id == section_id)
    return session.exec(statement).all()


def create_or_update_metric(session: Session, section_id: UUID, name: str, value: float) -> Metric:
    """Create a new Metric or overwrite an existing one (section_id + name key).

    This satisfies the requirement "A new metric generated for a Section should overwrite
    an existing metric with the name." The function commits and refreshes the instance.
    """
    existing = get_metric_by_name(session, section_id, name)
    now = datetime.now()
    if existing:
        existing.value = float(value)
        existing.recorded_at = now
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    metric = Metric(section_id=section_id, name=name, value=float(value), recorded_at=now)
    session.add(metric)
    session.commit()
    session.refresh(metric)
    return metric


def delete_metric(session: Session, section_id: UUID, name: str) -> bool:
    """Delete a metric by section and name. Returns True if deleted."""
    existing = get_metric_by_name(session, section_id, name)
    if not existing:
        return False
    session.delete(existing)
    session.commit()
    return True


def create_metrics_for_section(
        session: Session | None,
        section_id: UUID,
        content: str,
        metrics: List[str] | None = None,
    ) -> List[Metric]:
    """Compute metrics using core.get_metrics and upsert them for the given section.

    If no session is provided, this helper will open its own `Session(engine)`.
    Returns the list of persisted Metric objects.
    """
    close_session = False
    if session is None:
        session = Session(engine)
        close_session = True

    try:
        results = get_metrics_from_core(content, metrics)
        persisted: List[Metric] = []
        for name, value in results.items():
            metric = create_or_update_metric(session, section_id, name, value)
            persisted.append(metric)
        return persisted
    finally:
        if close_session:
            session.close()


def create_metrics_for_section_and_return_one(
        section_id: UUID, content: str, metric_name: str, metrics: List[str] | None = None
    ) -> Optional[Metric]:
    """Convenience wrapper: compute metrics and return the named metric result."""
    with Session(engine) as session:
        create_metrics_for_section(session, section_id, content, metrics)
        return get_metric_by_name(session, section_id, metric_name)
