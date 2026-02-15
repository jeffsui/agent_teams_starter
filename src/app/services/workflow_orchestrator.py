"""Workflow orchestrator for chaining agents."""
import asyncio
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from src.app.core.agents import (
    ArchitectAgent,
    ImplementAgent,
    ReviewerAgent,
    TesterAgent,
)
from src.app.core.llm_providers import ProviderFactory, ProviderConfig
from src.app.models.orchestration import (
    WorkflowState,
    WorkflowStatus,
    AgentStepStatus,
    AgentStepResult,
)


class WorkflowOrchestrator:
    """Orchestrates the workflow of multiple agents."""

    def __init__(self):
        """Initialize the workflow orchestrator."""
        self._workflows: dict[str, WorkflowState] = {}
        self._lock = asyncio.Lock()

    async def start_workflow(
        self,
        requirements: str,
        context: str | None = None,
        provider: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Start a new workflow execution.

        Args:
            requirements: User requirements.
            context: Additional context.
            provider: LLM provider to use.
            temperature: Temperature for generation.
            max_tokens: Maximum tokens to generate.

        Returns:
            The workflow ID.
        """
        workflow_id = str(uuid.uuid4())
        now = datetime.utcnow()

        workflow = WorkflowState(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            created_at=now,
            requirements=requirements,
            context=context,
            provider=provider,
        )

        async with self._lock:
            self._workflows[workflow_id] = workflow

        # Start the workflow in the background
        asyncio.create_task(
            self._execute_workflow(
                workflow_id, requirements, context, provider, temperature, max_tokens
            )
        )

        return workflow_id

    async def _execute_workflow(
        self,
        workflow_id: str,
        requirements: str,
        context: str | None,
        provider: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> None:
        """Execute the workflow steps in sequence.

        Args:
            workflow_id: The workflow ID.
            requirements: User requirements.
            context: Additional context.
            provider: LLM provider to use.
            temperature: Temperature for generation.
            max_tokens: Maximum tokens to generate.
        """
        async with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow:
                return
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.utcnow()

        # Create provider
        config = ProviderConfig()
        if provider:
            config.default_provider = provider

        llm_provider = ProviderFactory.create(provider, config)

        # Initialize agents
        architect = ArchitectAgent(llm_provider)
        implement = ImplementAgent(llm_provider)
        reviewer = ReviewerAgent(llm_provider)
        tester = TesterAgent(llm_provider)

        architect_output: BaseModel | None = None
        implement_output: BaseModel | None = None
        reviewer_output: BaseModel | None = None

        # Execute Architect
        try:
            await self._update_step_status(
                workflow_id, "architect", AgentStepStatus.IN_PROGRESS
            )
            architect_output = await architect.execute(
                requirements=requirements, context=context or "", temperature=temperature or 0.7, max_tokens=max_tokens or 4096
            )
            await self._complete_step(
                workflow_id,
                "architect",
                architect_output.model_dump(),
            )
        except Exception as e:
            await self._fail_step(workflow_id, "architect", str(e))
            await self._fail_workflow(workflow_id, str(e))
            return

        # Execute Implement
        try:
            await self._update_step_status(
                workflow_id, "implement", AgentStepStatus.IN_PROGRESS
            )
            implement_output = await implement.execute(
                architecture=architect_output.model_dump(),
                requirements=requirements,
                context=context or "",
                temperature=temperature or 0.7,
                max_tokens=max_tokens or 4096,
            )
            await self._complete_step(
                workflow_id,
                "implement",
                implement_output.model_dump(),
            )
        except Exception as e:
            await self._fail_step(workflow_id, "implement", str(e))
            await self._fail_workflow(workflow_id, str(e))
            return

        # Execute Reviewer
        try:
            await self._update_step_status(
                workflow_id, "reviewer", AgentStepStatus.IN_PROGRESS
            )
            reviewer_output = await reviewer.execute(
                implementation=implement_output.model_dump(),
                architecture=architect_output.model_dump(),
                requirements=requirements,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or 4096,
            )
            await self._complete_step(
                workflow_id,
                "reviewer",
                reviewer_output.model_dump(),
            )
        except Exception as e:
            await self._fail_step(workflow_id, "reviewer", str(e))
            # Don't fail the entire workflow for review errors, continue to testing

        # Execute Tester
        try:
            await self._update_step_status(
                workflow_id, "tester", AgentStepStatus.IN_PROGRESS
            )
            await tester.execute(
                implementation=implement_output.model_dump(),
                architecture=architect_output.model_dump(),
                requirements=requirements,
                review=reviewer_output.model_dump() if reviewer_output else None,
                temperature=temperature or 0.7,
                max_tokens=max_tokens or 4096,
            )
            await self._complete_step(
                workflow_id,
                "tester",
                {},
            )
        except Exception as e:
            await self._fail_step(workflow_id, "tester", str(e))
            # Don't fail the entire workflow for tester errors

        # Mark workflow as completed
        async with self._lock:
            workflow = self._workflows.get(workflow_id)
            if workflow and workflow.status != WorkflowStatus.FAILED:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.utcnow()

    async def _update_step_status(
        self, workflow_id: str, agent_name: str, status: AgentStepStatus
    ) -> None:
        """Update the status of an agent step."""
        async with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow:
                return

            step_result = AgentStepResult(
                agent_name=agent_name,
                status=status,
                started_at=datetime.utcnow() if status == AgentStepStatus.IN_PROGRESS else None,
            )

            if agent_name == "architect":
                workflow.architect_result = step_result
            elif agent_name == "implement":
                workflow.implement_result = step_result
            elif agent_name == "reviewer":
                workflow.reviewer_result = step_result
            elif agent_name == "tester":
                workflow.tester_result = step_result

    async def _complete_step(
        self, workflow_id: str, agent_name: str, result: dict[str, Any]
    ) -> None:
        """Mark an agent step as completed with results."""
        async with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow:
                return

            step_result = AgentStepResult(
                agent_name=agent_name,
                status=AgentStepStatus.COMPLETED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                result=result,
            )

            if agent_name == "architect":
                workflow.architect_result = step_result
            elif agent_name == "implement":
                workflow.implement_result = step_result
            elif agent_name == "reviewer":
                workflow.reviewer_result = step_result
            elif agent_name == "tester":
                workflow.tester_result = step_result

    async def _fail_step(
        self, workflow_id: str, agent_name: str, error: str
    ) -> None:
        """Mark an agent step as failed."""
        async with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow:
                return

            step_result = AgentStepResult(
                agent_name=agent_name,
                status=AgentStepStatus.FAILED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                error=error,
            )

            if agent_name == "architect":
                workflow.architect_result = step_result
            elif agent_name == "implement":
                workflow.implement_result = step_result
            elif agent_name == "reviewer":
                workflow.reviewer_result = step_result
            elif agent_name == "tester":
                workflow.tester_result = step_result

    async def _fail_workflow(self, workflow_id: str, error: str) -> None:
        """Mark the workflow as failed."""
        async with self._lock:
            workflow = self._workflows.get(workflow_id)
            if workflow:
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = datetime.utcnow()
                workflow.error = error

    async def get_workflow_status(self, workflow_id: str) -> WorkflowState | None:
        """Get the status of a workflow.

        Args:
            workflow_id: The workflow ID.

        Returns:
            The workflow state, or None if not found.
        """
        async with self._lock:
            return self._workflows.get(workflow_id)

    async def get_workflow_results(
        self, workflow_id: str
    ) -> dict[str, Any] | None:
        """Get the results of a completed workflow.

        Args:
            workflow_id: The workflow ID.

        Returns:
            The workflow results, or None if not found or incomplete.
        """
        async with self._lock:
            workflow = self._workflows.get(workflow_id)
            if not workflow or workflow.status != WorkflowStatus.COMPLETED:
                return None

            return {
                "architect_result": workflow.architect_result.result if workflow.architect_result else None,
                "implement_result": workflow.implement_result.result if workflow.implement_result else None,
                "reviewer_result": workflow.reviewer_result.result if workflow.reviewer_result else None,
                "tester_result": workflow.tester_result.result if workflow.tester_result else None,
            }


# Global orchestrator instance
_orchestrator: WorkflowOrchestrator | None = None


def get_orchestrator() -> WorkflowOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator
