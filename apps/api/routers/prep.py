from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.config import settings
from core.dependencies import get_driver
from models.common import ApiResponse
from models.prep import (
    PrepBriefResponse,
    ReadingAssignmentCreate,
    ReadingAssignmentResponse,
    ReadingAssignmentUpdate,
    WorkshopAssignmentCreate,
    WorkshopAssignmentResponse,
    WorkshopAssignmentUpdate,
)
from models.thread_prep import ThreadPrepBriefResponse
from repositories.cycle_repository import CycleRepository
from repositories.prep_repository import PrepRepository
from repositories.thread_prep_repository import ThreadPrepRepository
from services.prep_service import PrepService
from services.thread_prep_generator import ThreadPrepGenerator

router = APIRouter(tags=["prep"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> PrepService:
    generator = None
    if settings.anthropic_api_key:
        generator = ThreadPrepGenerator(settings.anthropic_api_key)
    return PrepService(
        repository=PrepRepository(driver),
        thread_prep_repo=ThreadPrepRepository(driver),
        cycle_repo=CycleRepository(driver),
        generator=generator,
    )


# Workshop assignments

@router.post(
    "/scheduled-sessions/{session_id}/workshop-assignments",
    response_model=ApiResponse[WorkshopAssignmentResponse],
    status_code=201,
)
async def create_workshop_assignment(
    session_id: str,
    body: WorkshopAssignmentCreate,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Assign a player/approach to a person for a Week 1 Workshop."""
    assignment = await service.create_workshop_assignment(session_id, body)
    return {"data": assignment}


@router.get(
    "/scheduled-sessions/{session_id}/workshop-assignments",
    response_model=ApiResponse[list[WorkshopAssignmentResponse]],
)
async def list_workshop_assignments(
    session_id: str,
    service: PrepService = Depends(_get_service),
) -> dict:
    """List workshop assignments for a session."""
    assignments = await service.list_workshop_assignments(session_id)
    return {"data": assignments, "meta": {"count": len(assignments)}}


@router.put(
    "/workshop-assignments/{assignment_id}",
    response_model=ApiResponse[WorkshopAssignmentResponse],
)
async def update_workshop_assignment(
    assignment_id: str,
    body: WorkshopAssignmentUpdate,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Update workshop assignment status or notes."""
    assignment = await service.update_workshop_assignment(assignment_id, body)
    return {"data": assignment}


# Reading assignments

@router.post(
    "/scheduled-sessions/{session_id}/reading-list",
    response_model=ApiResponse[ReadingAssignmentResponse],
    status_code=201,
)
async def create_reading_assignment(
    session_id: str,
    body: ReadingAssignmentCreate,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Assign a bookmark to a person for reading."""
    assignment = await service.create_reading_assignment(session_id, body)
    return {"data": assignment}


@router.get(
    "/scheduled-sessions/{session_id}/reading-list",
    response_model=ApiResponse[list[ReadingAssignmentResponse]],
)
async def list_reading_assignments(
    session_id: str,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Reading list with per-person read/unread status."""
    assignments = await service.list_reading_assignments(session_id)
    return {"data": assignments, "meta": {"count": len(assignments)}}


@router.put(
    "/reading-assignments/{assignment_id}",
    response_model=ApiResponse[ReadingAssignmentResponse],
)
async def update_reading_assignment(
    assignment_id: str,
    body: ReadingAssignmentUpdate,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Mark a reading assignment as read."""
    assignment = await service.update_reading_assignment(assignment_id, body)
    return {"data": assignment}


# Prep brief

@router.get(
    "/scheduled-sessions/{session_id}/prep-brief",
    response_model=ApiResponse[PrepBriefResponse],
)
async def get_prep_brief(
    session_id: str,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Auto-generated prep brief for a session."""
    brief = await service.get_prep_brief(session_id)
    return {"data": brief}


# Thread Prep Brief (LLM-generated)

@router.get(
    "/scheduled-sessions/{session_id}/thread-prep",
    response_model=ApiResponse[ThreadPrepBriefResponse],
)
async def get_thread_prep(
    session_id: str,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Get the persisted thread prep brief for a session."""
    brief = await service.get_thread_prep(session_id)
    return {"data": brief}


@router.post(
    "/scheduled-sessions/{session_id}/generate-prep",
    response_model=ApiResponse[ThreadPrepBriefResponse],
    status_code=201,
)
async def generate_thread_prep(
    session_id: str,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Generate a Thread Prep Brief using LLM analysis of recent bookmarks."""
    brief = await service.generate_thread_prep(session_id)
    return {"data": brief}


@router.post(
    "/scheduled-sessions/{session_id}/regenerate-prep",
    response_model=ApiResponse[ThreadPrepBriefResponse],
)
async def regenerate_thread_prep(
    session_id: str,
    service: PrepService = Depends(_get_service),
) -> dict:
    """Delete existing thread prep brief and generate a fresh one."""
    brief = await service.regenerate_thread_prep(session_id)
    return {"data": brief}
