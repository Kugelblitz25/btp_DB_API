"""API Endpoints for managing Events, Tracks, Areas, and Actions.

This module provides CRUD (Create, Read, Update, Delete) operations
for various entities related to tracking and events within the application.
"""
from typing import List, Optional, Sequence, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import SessionLocal, get_db # Assuming get_db is the preferred way from database.py
from models import (
    Action,
    ActionCreate,
    Area,
    AreaCreate,
    Event,
    EventCreate,
    Person, # Required for validation
    Track,
    TrackCreate,
)

router: APIRouter = APIRouter(tags=["Track and Event"])


# Dependency for getting a database session (if not using get_db directly from database.py)
# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     """Provides an asynchronous database session."""
#     async with SessionLocal() as session:
#         yield session


# Area CRUD operations
@router.post("/areas/", response_model=Area)
async def create_area(
    area: AreaCreate, session: AsyncSession = Depends(get_db)
) -> Area:
    """Creates a new area.

    Args:
        area: The area data to create.
        session: The database session.

    Returns:
        The created area.
    """
    db_area = Area.model_validate(area)
    session.add(db_area)
    await session.commit()
    await session.refresh(db_area)
    return db_area


@router.get("/areas/", response_model=List[Area])
async def read_areas(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Area]:
    """Retrieves a list of areas with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The database session.

    Returns:
        A list of areas.
    """
    result = await session.execute(select(Area).offset(skip).limit(limit))
    areas: Sequence[Area] = result.scalars().all()
    return areas


@router.get("/areas/{area_id}", response_model=Area)
async def read_area(area_id: int, session: AsyncSession = Depends(get_db)) -> Area:
    """Retrieves a specific area by its ID.

    Args:
        area_id: The ID of the area to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the area with the given ID is not found.

    Returns:
        The requested area.
    """
    db_area: Optional[Area] = await session.get(Area, area_id)
    if not db_area:
        raise HTTPException(status_code=404, detail=f"Area with id {area_id} not found")
    return db_area


@router.patch("/areas/{area_id}", response_model=Area)
async def update_area(
    area_id: int, area_update: AreaCreate, session: AsyncSession = Depends(get_db)
) -> Area:
    """Updates an existing area.

    Args:
        area_id: The ID of the area to update.
        area_update: The new data for the area.
        session: The database session.

    Raises:
        HTTPException: If the area with the given ID is not found.

    Returns:
        The updated area.
    """
    db_area: Optional[Area] = await session.get(Area, area_id)
    if not db_area:
        raise HTTPException(status_code=404, detail=f"Area with id {area_id} not found")

    area_data = area_update.model_dump(exclude_unset=True)
    for key, value in area_data.items():
        setattr(db_area, key, value)

    session.add(db_area)
    await session.commit()
    await session.refresh(db_area)
    return db_area


@router.delete("/areas/{area_id}", response_model=Area)
async def delete_area(area_id: int, session: AsyncSession = Depends(get_db)) -> Area:
    """Deletes an area by its ID.

    Args:
        area_id: The ID of the area to delete.
        session: The database session.

    Raises:
        HTTPException: If the area with the given ID is not found.

    Returns:
        The deleted area.
    """
    db_area: Optional[Area] = await session.get(Area, area_id)
    if not db_area:
        raise HTTPException(status_code=404, detail=f"Area with id {area_id} not found")

    await session.delete(db_area)
    await session.commit()
    # The object is expired after commit, so it cannot be returned directly
    # if it has relationships that were lazy loaded and are now gone.
    # Return a representation or a confirmation message.
    # For now, matching existing behavior by returning the object before expiry.
    # A better practice might be to return a standard "delete successful" message.
    return db_area


# Event CRUD operations
@router.post("/events/", response_model=Event)
async def create_event(
    event: EventCreate, session: AsyncSession = Depends(get_db)
) -> Event:
    """Creates a new event.

    Validates the existence of related Person and Area if their IDs are provided.

    Args:
        event: The event data to create.
        session: The database session.

    Raises:
        HTTPException: If related Person or Area is not found.

    Returns:
        The created event.
    """
    # Validate person_id
    if event.person_id is not None:
        person: Optional[Person] = await session.get(Person, event.person_id)
        if not person:
            raise HTTPException(
                status_code=404, detail=f"Person with id {event.person_id} not found"
            )

    # Validate area_id
    if event.area_id is not None:
        area: Optional[Area] = await session.get(Area, event.area_id)
        if not area:
            raise HTTPException(
                status_code=404, detail=f"Area with id {event.area_id} not found"
            )
    # Validate action_id
    if event.action_id is not None:
        action: Optional[Action] = await session.get(Action, event.action_id)
        if not action:
            raise HTTPException(
                status_code=404, detail=f"Action with id {event.action_id} not found"
            )

    db_event = Event.model_validate(event)
    session.add(db_event)
    await session.commit()
    await session.refresh(db_event)
    return db_event


@router.get("/events/", response_model=List[Event])
async def read_events(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    person_id: Optional[int] = Query(None, description="Filter events by Person ID."),
    area_id: Optional[int] = Query(None, description="Filter events by Area ID."),
    action_id: Optional[int] = Query(None, description="Filter events by Action ID."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Event]:
    """Retrieves a list of events with optional filters and pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        person_id: Optional Person ID to filter by.
        area_id: Optional Area ID to filter by.
        action_id: Optional Action ID to filter by.
        session: The database session.

    Returns:
        A list of events.
    """
    query = select(Event)

    if person_id is not None:
        query = query.where(Event.person_id == person_id)
    if area_id is not None:
        query = query.where(Event.area_id == area_id)
    if action_id is not None:
        query = query.where(Event.action_id == action_id)

    result = await session.execute(query.offset(skip).limit(limit))
    events: Sequence[Event] = result.scalars().all()
    return events


@router.get("/events/{event_id}", response_model=Event)
async def read_event(event_id: int, session: AsyncSession = Depends(get_db)) -> Event:
    """Retrieves a specific event by its ID.

    Args:
        event_id: The ID of the event to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the event with the given ID is not found.

    Returns:
        The requested event.
    """
    db_event: Optional[Event] = await session.get(Event, event_id)
    if not db_event:
        raise HTTPException(
            status_code=404, detail=f"Event with id {event_id} not found"
        )
    return db_event


@router.patch("/events/{event_id}", response_model=Event)
async def update_event(
    event_id: int,
    event_update: EventCreate,
    session: AsyncSession = Depends(get_db),
) -> Event:
    """Updates an existing event.

    Validates the existence of related Person, Area, or Action if their IDs are being updated.

    Args:
        event_id: The ID of the event to update.
        event_update: The new data for the event.
        session: The database session.

    Raises:
        HTTPException: If the event or related entities are not found.

    Returns:
        The updated event.
    """
    db_event: Optional[Event] = await session.get(Event, event_id)
    if not db_event:
        raise HTTPException(
            status_code=404, detail=f"Event with id {event_id} not found"
        )

    # Validate person_id if it's being updated
    if event_update.person_id is not None and event_update.person_id != db_event.person_id:
        person: Optional[Person] = await session.get(Person, event_update.person_id)
        if not person:
            raise HTTPException(
                status_code=404,
                detail=f"Person with id {event_update.person_id} not found",
            )

    # Validate area_id if it's being updated
    if event_update.area_id is not None and event_update.area_id != db_event.area_id:
        area: Optional[Area] = await session.get(Area, event_update.area_id)
        if not area:
            raise HTTPException(
                status_code=404, detail=f"Area with id {event_update.area_id} not found"
            )

    # Validate action_id if it's being updated
    if event_update.action_id is not None and event_update.action_id != db_event.action_id:
        action: Optional[Action] = await session.get(Action, event_update.action_id)
        if not action:
            raise HTTPException(
                status_code=404,
                detail=f"Action with id {event_update.action_id} not found",
            )

    event_data = event_update.model_dump(exclude_unset=True)
    for key, value in event_data.items():
        setattr(db_event, key, value)

    session.add(db_event)
    await session.commit()
    await session.refresh(db_event)
    return db_event


@router.delete("/events/{event_id}", response_model=Event)
async def delete_event(event_id: int, session: AsyncSession = Depends(get_db)) -> Event:
    """Deletes an event by its ID.

    Args:
        event_id: The ID of the event to delete.
        session: The database session.

    Raises:
        HTTPException: If the event with the given ID is not found.

    Returns:
        The deleted event.
    """
    db_event: Optional[Event] = await session.get(Event, event_id)
    if not db_event:
        raise HTTPException(
            status_code=404, detail=f"Event with id {event_id} not found"
        )

    await session.delete(db_event)
    await session.commit()
    return db_event


# Action CRUD operations
@router.post("/actions/", response_model=Action)
async def create_action(
    action: ActionCreate, session: AsyncSession = Depends(get_db)
) -> Action:
    """Creates a new action type.

    Args:
        action: The action data to create.
        session: The database session.

    Returns:
        The created action.
    """
    db_action = Action.model_validate(action)
    session.add(db_action)
    await session.commit()
    await session.refresh(db_action)
    return db_action


@router.get("/actions/", response_model=List[Action])
async def read_actions(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Action]:
    """Retrieves a list of action types with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The database session.

    Returns:
        A list of action types.
    """
    result = await session.execute(select(Action).offset(skip).limit(limit))
    actions: Sequence[Action] = result.scalars().all()
    return actions


@router.get("/actions/{action_id}", response_model=Action)
async def read_action(action_id: int, session: AsyncSession = Depends(get_db)) -> Action:
    """Retrieves a specific action type by its ID.

    Args:
        action_id: The ID of the action to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the action with the given ID is not found.

    Returns:
        The requested action.
    """
    db_action: Optional[Action] = await session.get(Action, action_id)
    if not db_action:
        raise HTTPException(
            status_code=404, detail=f"Action with id {action_id} not found"
        )
    return db_action


@router.patch("/actions/{action_id}", response_model=Action)
async def update_action(
    action_id: int,
    action_update: ActionCreate,
    session: AsyncSession = Depends(get_db),
) -> Action:
    """Updates an existing action type.

    Args:
        action_id: The ID of the action to update.
        action_update: The new data for the action.
        session: The database session.

    Raises:
        HTTPException: If the action with the given ID is not found.

    Returns:
        The updated action.
    """
    db_action: Optional[Action] = await session.get(Action, action_id)
    if not db_action:
        raise HTTPException(
            status_code=404, detail=f"Action with id {action_id} not found"
        )

    action_data = action_update.model_dump(exclude_unset=True)
    for key, value in action_data.items():
        setattr(db_action, key, value)

    session.add(db_action)
    await session.commit()
    await session.refresh(db_action)
    return db_action


@router.delete("/actions/{action_id}", response_model=Action)
async def delete_action(action_id: int, session: AsyncSession = Depends(get_db)) -> Action:
    """Deletes an action type by its ID.

    Args:
        action_id: The ID of the action to delete.
        session: The database session.

    Raises:
        HTTPException: If the action with the given ID is not found.

    Returns:
        The deleted action.
    """
    db_action: Optional[Action] = await session.get(Action, action_id)
    if not db_action:
        raise HTTPException(
            status_code=404, detail=f"Action with id {action_id} not found"
        )

    await session.delete(db_action)
    await session.commit()
    return db_action


# Track CRUD operations
@router.post("/tracks/", response_model=Track)
async def create_track(
    track: TrackCreate, session: AsyncSession = Depends(get_db)
) -> Track:
    """Creates new tracking data for a person.

    Validates the existence of the related Person.

    Args:
        track: The track data to create.
        session: The database session.

    Raises:
        HTTPException: If the related Person is not found.

    Returns:
        The created track data.
    """
    # Validate person_id
    if track.person_id is not None: # Should always be present based on model
        person: Optional[Person] = await session.get(Person, track.person_id)
        if not person:
            raise HTTPException(
                status_code=404, detail=f"Person with id {track.person_id} not found"
            )
    db_track = Track.model_validate(track)
    session.add(db_track)
    await session.commit()
    await session.refresh(db_track)
    return db_track


@router.get("/tracks/", response_model=List[Track])
async def read_tracks(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(1, ge=1, le=200, description="Maximum number of records to return. Default is 1."), # Default limit was 1
    person_id: Optional[int] = Query(None, description="Filter tracks by Person ID."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Track]:
    """Retrieves a list of tracking data with optional filters and pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        person_id: Optional Person ID to filter by.
        session: The database session.

    Returns:
        A list of tracking data, ordered by time descending.
    """
    query = select(Track)

    if person_id is not None:
        query = query.where(Track.person_id == person_id)

    result = await session.execute(query.offset(skip).limit(limit).order_by(Track.time.desc()))
    tracks: Sequence[Track] = result.scalars().all()
    return tracks


@router.get("/tracks/{track_id}", response_model=Track)
async def read_track(track_id: int, session: AsyncSession = Depends(get_db)) -> Track:
    """Retrieves specific tracking data by its ID.

    Args:
        track_id: The ID of the track data to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the track data with the given ID is not found.

    Returns:
        The requested track data.
    """
    db_track: Optional[Track] = await session.get(Track, track_id)
    if not db_track:
        raise HTTPException(
            status_code=404, detail=f"Track with id {track_id} not found"
        )
    return db_track


@router.patch("/tracks/{track_id}", response_model=Track)
async def update_track(
    track_id: int,
    track_update: TrackCreate,
    session: AsyncSession = Depends(get_db),
) -> Track:
    """Updates existing tracking data.

    Validates the existence of the related Person if their ID is being updated.

    Args:
        track_id: The ID of the track data to update.
        track_update: The new data for the track.
        session: The database session.

    Raises:
        HTTPException: If the track data or related Person is not found.

    Returns:
        The updated track data.
    """
    db_track: Optional[Track] = await session.get(Track, track_id)
    if not db_track:
        raise HTTPException(
            status_code=404, detail=f"Track with id {track_id} not found"
        )

    # Validate person_id if it's being updated
    if track_update.person_id is not None and track_update.person_id != db_track.person_id:
        person: Optional[Person] = await session.get(Person, track_update.person_id)
        if not person:
            raise HTTPException(
                status_code=404,
                detail=f"Person with id {track_update.person_id} not found",
            )

    track_data = track_update.model_dump(exclude_unset=True)
    for key, value in track_data.items():
        setattr(db_track, key, value)

    session.add(db_track)
    await session.commit()
    await session.refresh(db_track)
    return db_track


@router.delete("/tracks/{track_id}", response_model=Track)
async def delete_track(track_id: int, session: AsyncSession = Depends(get_db)) -> Track:
    """Deletes tracking data by its ID.

    Args:
        track_id: The ID of the track data to delete.
        session: The database session.

    Raises:
        HTTPException: If the track data with the given ID is not found.

    Returns:
        The deleted track data.
    """
    db_track: Optional[Track] = await session.get(Track, track_id)
    if not db_track:
        raise HTTPException(
            status_code=404, detail=f"Track with id {track_id} not found"
        )

    await session.delete(db_track)
    await session.commit()
    return db_track
