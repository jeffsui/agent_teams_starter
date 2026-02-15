"""Dashboard API endpoints for workflow management."""
from fastapi import APIRouter, HTTPException, Query, status

from src.app.models import (
    WorkflowListItem,
    WorkflowDetail,
    ConversationMessage,
    DashboardStats,
)
from src.app.repositories import get_workflow_repository


router = APIRouter()


@router.get("/workflows", response_model=list[WorkflowListItem])
async def list_workflows(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of workflows to return"),
    offset: int = Query(0, ge=0, description="Number of workflows to skip"),
    status_filter: str | None = Query(None, description="Filter by workflow status"),
) -> list[WorkflowListItem]:
    """Get a list of all workflows.

    Args:
        limit: Maximum number of workflows to return.
        offset: Number of workflows to skip.
        status_filter: Optional filter by status.

    Returns:
        List of workflow items.
    """
    try:
        repo = get_workflow_repository()
        return await repo.list_workflows(
            limit=limit,
            offset=offset,
            status=status_filter,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}",
        )


@router.get("/workflows/stats", response_model=DashboardStats)
async def get_dashboard_stats() -> DashboardStats:
    """Get dashboard statistics.

    Returns:
        Dashboard statistics.
    """
    try:
        repo = get_workflow_repository()
        return await repo.get_dashboard_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}",
        )


@router.get("/workflows/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow_detail(workflow_id: str) -> WorkflowDetail:
    """Get detailed information about a workflow.

    Args:
        workflow_id: The workflow ID.

    Returns:
        Detailed workflow information.

    Raises:
        HTTPException: If workflow not found.
    """
    repo = get_workflow_repository()
    workflow = await repo.get_workflow(workflow_id)

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    return workflow


@router.get("/workflows/{workflow_id}/history", response_model=list[ConversationMessage])
async def get_conversation_history(workflow_id: str) -> list[ConversationMessage]:
    """Get conversation history for a workflow.

    Args:
        workflow_id: The workflow ID.

    Returns:
        List of conversation messages.
    """
    try:
        repo = get_workflow_repository()
        return await repo.get_conversation_history(workflow_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}",
        )


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(workflow_id: str) -> None:
    """Delete a workflow.

    Args:
        workflow_id: The workflow ID.

    Raises:
        HTTPException: If workflow not found.
    """
    repo = get_workflow_repository()
    deleted = await repo.delete_workflow(workflow_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
