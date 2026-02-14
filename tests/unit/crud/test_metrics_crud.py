"""Unit tests for app.crud.metrics CRUD operations."""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import MagicMock, patch

from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.crud.metrics import (
    get_metric_record,
    add_metric,
    delete_metric,
    list_section_metrics,
    handle_metrics_request,
)
from app.crud.tables import Metric
from app.schemas.metrics import MetricsRequest


@pytest.fixture
def test_db_session():
    """Create an in-memory SQLite database for testing."""
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
    """Provide a consistent section UUID for tests."""
    return uuid4()


@pytest.fixture
def sample_metric(sample_section_id: UUID) -> Metric:
    """Create a sample metric for testing."""
    return Metric(
        section_id=sample_section_id,
        name="diction",
        value=0.75,
        content="Sample content",
    )


class TestGetMetricRecord:
    """Tests for get_metric_record function."""

    def test_get_metric_record_existing(self, test_db_session: Session, sample_section_id: UUID):
        """Test retrieving an existing metric by section and name."""
        # Add a new metric to the database
        metric = Metric(
            section_id=sample_section_id,
            name="sentiment",
            value=0.85,
            content="Test content",
        )
        test_db_session.add(metric)
        test_db_session.commit()

        # Attempt to retreive the metric
        result = get_metric_record(test_db_session, "sentiment", sample_section_id)

        assert result is not None
        assert result.name == "sentiment"
        assert result.value == 0.85
        assert result.section_id == sample_section_id

    def test_get_metric_record_not_found(self, test_db_session: Session, sample_section_id: UUID):
        """Test retrieving a non-existent metric returns None."""
        # Attempt to get a non-existent metric
        result = get_metric_record(test_db_session, "nonexistent", sample_section_id)

        assert result is None

    def test_get_metric_record_different_section(self, test_db_session: Session, sample_section_id: UUID):
        """Test that metrics from different sections are isolated."""
        # Generate a metric for a different section
        other_section_id = uuid4()
        metric = Metric(
            section_id=other_section_id,
            name="sentiment",
            value=0.85,
            content="Test content",
        )
        test_db_session.add(metric)
        test_db_session.commit()

        # Attempt to retrive a metric for the original section
        result = get_metric_record(test_db_session, "sentiment", sample_section_id)

        assert result is None


class TestAddMetric:
    """Tests for add_metric function."""

    def test_add_metric_new(self, test_db_session: Session, sample_section_id: UUID):
        """Test creating a new metric record."""
        # Add a new metric
        result = add_metric(
            test_db_session,
            name="polarity",
            value=0.5,
            section_id=sample_section_id,
        )

        # Check returned record
        assert result.id is not None
        assert result.name == "polarity"
        assert result.value == 0.5
        assert result.section_id == sample_section_id
        assert isinstance(result.recorded_at, datetime)

        # Verify persisted
        persisted = get_metric_record(test_db_session, "polarity", sample_section_id)
        assert persisted.id == result.id

    def test_add_metric_update_existing(self, test_db_session: Session, sample_section_id: UUID):
        """Test updating an existing metric (upsert behavior)."""
        # First add then update a given metric
        original = add_metric(
            test_db_session,
            name="toxicity",
            value=0.1,
            section_id=sample_section_id,
        )
        updated = add_metric(
            test_db_session,
            name="toxicity",
            value=0.3,
            section_id=sample_section_id,
        )

        # Verify the same record was updated
        assert updated.id ==  original.id
        assert updated.value == 0.3
        assert updated.recorded_at > original.recorded_at

        # Verify only one record exists
        all_metrics = list_section_metrics(test_db_session, sample_section_id)
        toxicity_metrics = [m for m in all_metrics if m.name == "toxicity"]
        assert len(toxicity_metrics) == 1

    def test_add_metric_float_conversion(self, test_db_session: Session, sample_section_id: UUID):
        """Test that metric values are converted to float."""
        # Add a metric with a string value, string should be converted to float
        result = add_metric(
            test_db_session,
            name="spam",
            value="0.95", 
            section_id=sample_section_id,
        )

        assert isinstance(result.value, float)
        assert result.value == 0.95


class TestDeleteMetric:
    """Tests for delete_metric function."""

    def test_delete_metric_existing(self, test_db_session: Session, sample_section_id: UUID):
        """Test deleting an existing metric."""
        # Add a sample metric and delete it
        add_metric(
            test_db_session,
            name="genre",
            value=0.6,
            section_id=sample_section_id,
        )
        result = delete_metric(test_db_session, "genre", sample_section_id)

        assert result is True
        assert get_metric_record(test_db_session, "genre", sample_section_id) is None

    def test_delete_metric_nonexistent(self, test_db_session: Session, sample_section_id: UUID):
        """Test deleting a non-existent metric returns False."""
        result = delete_metric(test_db_session, "nonexistent", sample_section_id)

        assert result is False

    def test_delete_metric_only_specified(self, test_db_session: Session, sample_section_id: UUID):
        """Test that delete only removes the specified metric."""
        # Add two metrics and delete one
        add_metric(test_db_session, "mode", 0.4, sample_section_id)
        add_metric(test_db_session, "tone", 0.7, sample_section_id)
        delete_metric(test_db_session, "mode", sample_section_id)

        assert get_metric_record(test_db_session, "mode", sample_section_id) is None
        assert get_metric_record(test_db_session, "tone", sample_section_id) is not None


class TestListSectionMetrics:
    """Tests for list_section_metrics function."""

    def test_list_section_metrics_empty(self, test_db_session: Session, sample_section_id: UUID):
        """Test listing metrics when section has none."""
        result = list_section_metrics(test_db_session, sample_section_id)

        assert result == []

    def test_list_section_metrics_multiple(self, test_db_session: Session, sample_section_id: UUID):
        """Test listing all metrics for a section."""
        # Add multiple metrics for a given section
        names = ["diction", "sentiment", "toxicity"]
        for i, name in enumerate(names):
            add_metric(test_db_session, name, float(i) * 0.1, sample_section_id)
        result = list_section_metrics(test_db_session, sample_section_id)

        assert len(result) == 3
        result_names = {m.name for m in result}
        assert result_names == set(names)

    def test_list_section_metrics_isolated_by_section(self, test_db_session: Session):
        """Test that metrics are isolated by section."""
        # Add metrics to two different sections and verify isolation
        section1 = uuid4()
        section2 = uuid4()
        add_metric(test_db_session, "sentiment", 0.5, section1)
        add_metric(test_db_session, "sentiment", 0.8, section2)
        result1 = list_section_metrics(test_db_session, section1)
        result2 = list_section_metrics(test_db_session, section2)

        assert len(result1) == 1
        assert len(result2) == 1
        assert result1[0].value == 0.5
        assert result2[0].value == 0.8


class TestHandleMetricsRequest:
    """Tests for handle_metrics_request orchestration function."""

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request_full_flow(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test complete flow: mock core, persist all metrics."""
        # Set values to be returned by the mocked get_metrics function
        mock_get_metrics.return_value = {
            "diction": 0.72,
            "sentiment": 0.85,
            "toxicity": 0.1,
        }
        request = MetricsRequest(
            content="Test content",
            metrics=None,
            section_id=sample_section_id,
        )
        result = handle_metrics_request(test_db_session, request, {})

        # Check returned records
        assert len(result) == 3
        assert all(isinstance(m, Metric) for m in result)
        names = {m.name for m in result}
        assert names == {"diction", "sentiment", "toxicity"}

        # Verify persisted
        all_metrics = list_section_metrics(test_db_session, sample_section_id)
        assert len(all_metrics) == 3

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request_upsert_on_rerun(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test that re-running updates existing metrics (upsert)."""
        # Define a sample request and mock get_metrics
        mock_get_metrics.return_value = {"sentiment": 0.5}
        request = MetricsRequest(
            content="Content v1",
            metrics=None,
            section_id=sample_section_id,
        )
        result1 = handle_metrics_request(test_db_session, request, {})
        id1 = result1[0].id

        # Update the metric value and re-run the request, simulating an update scenario
        mock_get_metrics.return_value = {"sentiment": 0.8}
        request2 = MetricsRequest(
            content="Content v2",
            metrics=None,
            section_id=sample_section_id,
        )
        result2 = handle_metrics_request(test_db_session, request2, {})

        # Assert: same record ID, updated value
        assert result2[0].id == id1
        assert result2[0].value == 0.8
        assert len(list_section_metrics(test_db_session, sample_section_id)) == 1

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request_empty_result(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test handling when get_metrics returns empty dict."""
        # Mock an empty result from get_metrics
        mock_get_metrics.return_value = {}
        request = MetricsRequest(
            content="Content",
            metrics=None,
            section_id=sample_section_id,
        )
        result = handle_metrics_request(test_db_session, request, {})

        assert result == []

    @patch("app.crud.metrics.get_metrics")
    def test_handle_metrics_request_passes_params(self, mock_get_metrics, test_db_session: Session, sample_section_id: UUID):
        """Test that request parameters are passed to core get_metrics."""
        # Mock get_metrics and verify only requested metrics are passed
        mock_get_metrics.return_value = {"sentiment": 0.5}
        metrics_list = ["sentiment", "toxicity"]
        request = MetricsRequest(
            content="Content",
            metrics=metrics_list,
            section_id=sample_section_id,
        )
        handle_metrics_request(test_db_session, request, {})

        # Assert: verify get_metrics was called with correct args
        mock_get_metrics.assert_called_once_with("Content", metrics_list)
