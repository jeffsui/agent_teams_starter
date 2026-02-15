"""Tests for workflow orchestration API endpoints."""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


def test_start_workflow(client: TestClient):
    """Test starting a new workflow."""
    with patch("src.app.api.orchestration.get_orchestrator") as mock_get_orchestrator:
        mock_orchestrator = AsyncMock()
        mock_orchestrator.start_workflow = AsyncMock(return_value="test-workflow-id")
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.post(
            "/api/workflow",
            json={
                "requirements": "Build a REST API for user management",
                "context": "Use Python and FastAPI",
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert data["workflow_id"] == "test-workflow-id"
        assert data["status"] == "pending"
        assert "message" in data


def test_start_workflow_with_provider(client: TestClient):
    """Test starting a workflow with provider selection."""
    with patch("src.app.api.orchestration.get_orchestrator") as mock_get_orchestrator:
        mock_orchestrator = AsyncMock()
        mock_orchestrator.start_workflow = AsyncMock(return_value="test-workflow-id")
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.post(
            "/api/workflow",
            json={
                "requirements": "Build a REST API",
                "provider": "anthropic",
                "temperature": 0.5,
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert data["workflow_id"] == "test-workflow-id"


def test_get_workflow_status(client: TestClient):
    """Test getting workflow status."""
    from datetime import datetime
    from src.app.models.orchestration import WorkflowState, WorkflowStatus, AgentStepResult, AgentStepStatus

    with patch("src.app.api.orchestration.get_orchestrator") as mock_get_orchestrator:
        mock_orchestrator = AsyncMock()
        mock_state = WorkflowState(
            workflow_id="test-workflow-id",
            status=WorkflowStatus.RUNNING,
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            requirements="Build a REST API",
            architect_result=AgentStepResult(
                agent_name="architect",
                status=AgentStepStatus.IN_PROGRESS,
                started_at=datetime.utcnow(),
            ),
        )
        mock_orchestrator.get_workflow_status = AsyncMock(return_value=mock_state)
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/workflow/test-workflow-id")

        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "test-workflow-id"
        assert data["status"] == "running"
        assert data["current_step"] == "architect"


def test_get_workflow_status_not_found(client: TestClient):
    """Test getting status for non-existent workflow."""
    with patch("src.app.api.orchestration.get_orchestrator") as mock_get_orchestrator:
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_workflow_status = AsyncMock(return_value=None)
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/workflow/non-existent-id")

        assert response.status_code == 404


def test_get_workflow_results(client: TestClient):
    """Test getting workflow results."""
    from datetime import datetime
    from src.app.models.orchestration import WorkflowState, WorkflowStatus, AgentStepResult, AgentStepStatus

    with patch("src.app.api.orchestration.get_orchestrator") as mock_get_orchestrator:
        mock_orchestrator = AsyncMock()

        mock_state = WorkflowState(
            workflow_id="test-workflow-id",
            status=WorkflowStatus.COMPLETED,
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            requirements="Build a REST API",
            architect_result=AgentStepResult(
                agent_name="architect",
                status=AgentStepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                result={"tech_stack": {"python": "3.11"}},
            ),
            implement_result=AgentStepResult(
                agent_name="implement",
                status=AgentStepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                result={"files": []},
            ),
            reviewer_result=AgentStepResult(
                agent_name="reviewer",
                status=AgentStepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                result={"overall_assessment": "Good"},
            ),
            tester_result=AgentStepResult(
                agent_name="tester",
                status=AgentStepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                result={"test_cases": []},
            ),
        )
        mock_orchestrator.get_workflow_status = AsyncMock(return_value=mock_state)
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/workflow/test-workflow-id/results")

        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "test-workflow-id"
        assert data["status"] == "completed"
        assert data["architect_result"] is not None
        assert data["implement_result"] is not None


def test_get_workflow_results_not_completed(client: TestClient):
    """Test getting results for incomplete workflow."""
    from datetime import datetime
    from src.app.models.orchestration import WorkflowState, WorkflowStatus

    with patch("src.app.api.orchestration.get_orchestrator") as mock_get_orchestrator:
        mock_orchestrator = AsyncMock()
        mock_state = WorkflowState(
            workflow_id="test-workflow-id",
            status=WorkflowStatus.RUNNING,
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            requirements="Build a REST API",
        )
        mock_orchestrator.get_workflow_status = AsyncMock(return_value=mock_state)
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/workflow/test-workflow-id/results")

        assert response.status_code == 400
