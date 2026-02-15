"""Orchestration API endpoints for workflow management."""
from fastapi import APIRouter, HTTPException, status

from src.app.models import (
    WorkflowRequest,
    WorkflowStartResponse,
    WorkflowStatusResponse,
    WorkflowResultsResponse,
    WorkflowStatus,
)
from src.app.services import get_orchestrator

router = APIRouter()


@router.post("/workflow", response_model=WorkflowStartResponse, status_code=202)
async def start_workflow(request: WorkflowRequest) -> WorkflowStartResponse:
    """Start a new workflow that chains all agents.

    The workflow executes: Architect → Implement → Reviewer → Tester

    Args:
        request: Workflow request with requirements and context.

    Returns:
        Workflow start response with workflow ID.

    Raises:
        HTTPException: If workflow cannot be started.
    """
    try:
        orchestrator = get_orchestrator()

        workflow_id = await orchestrator.start_workflow(
            requirements=request.requirements,
            context=request.context,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return WorkflowStartResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            message="Workflow started successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}",
        )


@router.get("/workflow/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str) -> WorkflowStatusResponse:
    """Get the status of a workflow.

    Args:
        workflow_id: The workflow ID.

    Returns:
        Workflow status response.

    Raises:
        HTTPException: If workflow not found.
    """
    orchestrator = get_orchestrator()
    workflow = await orchestrator.get_workflow_status(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Determine current step
    current_step = None
    if workflow.architect_result and workflow.architect_result.status.value == "in_progress":
        current_step = "architect"
    elif workflow.implement_result and workflow.implement_result.status.value == "in_progress":
        current_step = "implement"
    elif workflow.reviewer_result and workflow.reviewer_result.status.value == "in_progress":
        current_step = "reviewer"
    elif workflow.tester_result and workflow.tester_result.status.value == "in_progress":
        current_step = "tester"

    return WorkflowStatusResponse(
        workflow_id=workflow.workflow_id,
        status=workflow.status,
        created_at=workflow.created_at,
        started_at=workflow.started_at,
        completed_at=workflow.completed_at,
        current_step=current_step,
        error=workflow.error,
    )


@router.get("/workflow/{workflow_id}/results", response_model=WorkflowResultsResponse)
async def get_workflow_results(workflow_id: str) -> WorkflowResultsResponse:
    """Get the results of a completed workflow.

    Args:
        workflow_id: The workflow ID.

    Returns:
        Workflow results response.

    Raises:
        HTTPException: If workflow not found or not completed.
    """
    orchestrator = get_orchestrator()
    workflow = await orchestrator.get_workflow_status(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    if workflow.status != WorkflowStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow {workflow_id} is not completed. Current status: {workflow.status.value}",
        )

    results = {
        "architect_result": workflow.architect_result.result if workflow.architect_result else None,
        "implement_result": workflow.implement_result.result if workflow.implement_result else None,
        "reviewer_result": workflow.reviewer_result.result if workflow.reviewer_result else None,
        "tester_result": workflow.tester_result.result if workflow.tester_result else None,
    }

    return WorkflowResultsResponse(
        workflow_id=workflow.workflow_id,
        status=workflow.status,
        results=results,
        architect_result=workflow.architect_result.result if workflow.architect_result else None,
        implement_result=workflow.implement_result.result if workflow.implement_result else None,
        reviewer_result=workflow.reviewer_result.result if workflow.reviewer_result else None,
        tester_result=workflow.tester_result.result if workflow.tester_result else None,
        completed_at=workflow.completed_at,
    )
