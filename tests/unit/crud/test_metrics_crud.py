"""Unit tests for app.crud.metrics CRUD operations."""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import patch

from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.crud.metrics import (
    get_metric,
    add_metric,
    delete_metric,
    list_section_metrics,
    handle_metrics_request,
)
from app.crud.tables import Metric
from app.schemas.metrics import MetricsRequest


@pytest.fixture
def test_db_session():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_section_id() -> UUID:
    """Provide a consistent section UUID for tests"""
    return uuid4()


@pytest.fixture
def sample_metric_kwargs(sample_section_id: UUID) -> dict:
    """Return default kwargs for creating a sample metric"""
    return dict(section_id=sample_section_id, name="sentiment", value=0.85)


@pytest.fixture
def sample_metric(sample_metric_kwargs: dict) -> dict:
    """Return default kwargs for creating a sample metric"""
    return Metric(**sample_metric_kwargs)


class TestAddMetric:
    """Tests for add_metric function"""

    def test_add_metric(self, test_db_session: Session, sample_metric_kwargs: dict):
        """Test creating a new metric record"""
        # Add a new metric
        result = add_metric(test_db_session, **sample_metric_kwargs)

        # Check returned record
        assert result.section_id == sample_metric_kwargs["section_id"]
        assert result.name == sample_metric_kwargs["name"]
        assert result.value == sample_metric_kwargs["value"]
        assert isinstance(result.recorded_at, datetime)

    @pytest.mark.parametrize("missing_field", ["section_id", "name", "value"])
    def test_add_metric_exceptions(self, test_db_session: Session, sample_metric_kwargs: dict, missing_field: str):
        """Verify exceptions are raised for missing required fields"""
        # Remove a required field
        del sample_metric_kwargs[missing_field]

        # Attempt to add a partial metric
        with pytest.raises(Exception):
            add_metric(test_db_session, **sample_metric_kwargs)

    def test_add_metric_float(self, test_db_session: Session, sample_metric_kwargs: dict):
        """Test that metric values are converted to float"""
        # Add a metric with a string value, string should be converted to float
        sample_metric_kwargs["value"] = "0.95"
        result = add_metric(test_db_session, **sample_metric_kwargs)

        assert isinstance(result.value, float)
        assert result.value == 0.95

    def test_add_metric_update(self, test_db_session: Session, sample_metric_kwargs: dict):
        """Test updating an existing metric (upsert behavior)"""
        section_id = sample_metric_kwargs["section_id"]

        # First add then update a given metric
        original = add_metric(test_db_session, **sample_metric_kwargs)
        assert original.section_id == section_id
        assert original.value == sample_metric_kwargs["value"]

        sample_metric_kwargs["value"] = 0.3
        updated = add_metric(test_db_session, **sample_metric_kwargs)
 
        # Verify the same record was updated
        assert updated.section_id == section_id
        assert updated.value == 0.3

        # Verify only one record exists
        section_metrics = list_section_metrics(test_db_session, section_id)
        assert len(section_metrics) == 1


class TestDeleteMetric:
    """Tests for delete_metric crud function"""

    def test_delete_metric(self, test_db_session: Session, sample_metric_kwargs: dict):
        """Test deleting an existing metric"""
        # Add a sample metric and delete it
        result = add_metric(test_db_session, **sample_metric_kwargs)

        section_id = sample_metric_kwargs["section_id"]
        metric_name = sample_metric_kwargs["name"]
        result = delete_metric(test_db_session, section_id, metric_name)

        assert result is True
        assert get_metric(test_db_session, section_id, metric_name) is None

    def test_delete_metric_nonexistent(self, test_db_session: Session, sample_section_id: UUID):
        """Test deleting a non-existent metric returns False"""
        result = delete_metric(test_db_session, sample_section_id, "nonexistent")

        assert result is False

    def test_delete_metric_specified(self, test_db_session: Session, sample_section_id: UUID):
        """Test that delete only removes the specified metric"""
        # Add two metrics and delete one
        add_metric(test_db_session, sample_section_id, "mode", 0.4)
        add_metric(test_db_session, sample_section_id, "tone", 0.7)
        delete_metric(test_db_session, sample_section_id, "mode")

        assert get_metric(test_db_session, sample_section_id, "mode") is None
        assert get_metric(test_db_session, sample_section_id, "tone") is not None


class TestGetMetricRecord:
    """Tests for get_metric_record function"""

    def test_get_metric_existing(self, test_db_session: Session, sample_metric: Metric):
        """Test retrieving an existing metric by section and name"""
        # Add a new metric to the database
        test_db_session.add(sample_metric)
        test_db_session.commit()

        # Attempt to retreive the metric
        result = get_metric(test_db_session, sample_metric.section_id, sample_metric.name)

        # Verify a matching record is returned
        assert result is not None
        assert result.section_id == sample_metric.section_id
        assert result.name == sample_metric.name
        assert result.value == sample_metric.value

    def test_get_metric_nonexistent(self, test_db_session: Session, sample_section_id: UUID):
        """Test retrieving a non-existent metric returns None"""
        # Attempt to get a non-existent metric
        result = get_metric(test_db_session, sample_section_id, "nonexistent")

        assert result is None

    def test_get_metric_section(self, test_db_session: Session, sample_section_id: UUID):
        """Test that metrics from different sections are isolated"""
        # Generate a metric for a different section
        new_seection_id = uuid4()
        add_metric(test_db_session, sample_section_id, "sentiment", 0.4)
        add_metric(test_db_session, new_seection_id, "sentiment", 0.7)
        test_db_session.commit()

        # Attempt to retrive a metric for the original section
        first_record = get_metric(test_db_session, sample_section_id, "sentiment")
        second_record = get_metric(test_db_session, new_seection_id, "sentiment")

        assert first_record.value == 0.4
        assert second_record.value == 0.7


class TestListSectionMetrics:
    """Tests for list_section_metrics function"""

    def test_list_section_metrics_empty(self, test_db_session: Session, sample_section_id: UUID):
        """Test listing metrics when section has none"""
        result = list_section_metrics(test_db_session, sample_section_id)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_section_metrics_multiple(self, test_db_session: Session, sample_section_id: UUID):
        """Test listing all metrics for a section"""
        # Add multiple metrics for a given section
        metric_names = ["diction", "sentiment", "toxicity"]
        for name in metric_names:
            add_metric(test_db_session, sample_section_id, name, 0.1)
        result = list_section_metrics(test_db_session, sample_section_id)

        assert len(result) == 3
        assert {m.name for m in result} == set(metric_names)

    def test_list_section_metrics_isolated(self, test_db_session: Session, sample_section_id: UUID):
        """Test that metrics are isolated by section"""
        # Add metrics to two different sections and verify isolation
        new_section_id = uuid4()
        add_metric(test_db_session, sample_section_id, "sentiment", 0.5)
        add_metric(test_db_session, new_section_id, "sentiment", 0.8)
        sample_result = list_section_metrics(test_db_session, sample_section_id)
        new_result = list_section_metrics(test_db_session, new_section_id)

        assert len(sample_result) == 1
        assert len(new_result) == 1
        assert sample_result[0].value == 0.5
        assert new_result[0].value == 0.8


class TestHandleMetricsRequest:
    """Tests for handle_metrics_request orchestration function."""

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test complete flow: mock core, persist all metrics"""
        # Set values to be returned by the mocked get_metrics function
        metric_dict = {"diction": 0.72, "sentiment": 0.85, "toxicity": 0.1}
        request = MetricsRequest(section_id=sample_section_id, content="Test content", metrics=None)
        mock_get_metrics.return_value = metric_dict
        result = handle_metrics_request(test_db_session, request, {})
        
        # Check returned records
        assert all(isinstance(m, Metric) for m in result)
        assert len(result) == len(metric_dict)
        assert {m.name for m in result} == set(metric_dict.keys())
        assert {m.value for m in result} == set(metric_dict.values())

        # Verify persisted
        result = list_section_metrics(test_db_session, sample_section_id)
        assert len(result) == len(metric_dict)
        assert {m.name for m in result} == set(metric_dict.keys())
        assert {m.value for m in result} == set(metric_dict.values())

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request_upsert(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test that re-running updates existing metrics (upsert)"""
        # Define a sample request and mock get_metrics
        mock_get_metrics.return_value = {"sentiment": 0.5}
        request = MetricsRequest(section_id=sample_section_id, content="Content v1", metrics=None)
        handle_metrics_request(test_db_session, request, {})

        # Update the metric value and re-run the request, simulating an update scenario
        mock_get_metrics.return_value = {"sentiment": 0.8}
        request = MetricsRequest(section_id=sample_section_id, content="Content v2", metrics=None)
        result = handle_metrics_request(test_db_session, request, {})

        # Assert: same record ID, updated value
        assert len(result) == 1
        assert result[0].value == 0.8
        assert len(list_section_metrics(test_db_session, sample_section_id)) == 1

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request_empty(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test handling when get_metrics returns empty dict."""
        # Mock an empty result from get_metrics
        mock_get_metrics.return_value = {}
        request = MetricsRequest(section_id=sample_section_id, content="Content", metrics=None)
        result = handle_metrics_request(test_db_session, request, {})

        assert result == []

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request_metrics(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test that request parameters are passed to core get_metrics."""
        # Mock get_metrics and verify only requested metrics are passed
        mock_get_metrics.return_value = {"sentiment": 0.5}
        metrics_list = ["sentiment", "toxicity"]
        request = MetricsRequest(content="Content", metrics=metrics_list, section_id=sample_section_id)
        handle_metrics_request(test_db_session, request, {})

        # Assert: verify get_metrics was called with correct args
        mock_get_metrics.assert_called_once_with("Content", metrics_list)
