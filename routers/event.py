from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import SessionLocal
from models import (
    Action,
    ActionCreate,
    Area,
    AreaCreate,
    Event,
    EventCreate,
    Person,
    Track,
    TrackCreate,
)

router = APIRouter(tags=["Track and Event"])


async def get_session():
    async with SessionLocal() as session:
        yield session


# Area CRUD operations
@router.post("/areas/", response_model=Area)
async def create_area(area: ActionCreate, session: AsyncSession = Depends(get_session)):
    area = Area(**area.model_dump())
    session.add(area)
    await session.commit()
    await session.refresh(area)
    return area


@router.get("/areas/", response_model=List[Area])
async def read_areas(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    areas = await session.execute(select(Area).offset(skip).limit(limit))
    return areas.scalars().all()


@router.get("/areas/{area_id}", response_model=Area)
async def read_area(area_id: int, session: AsyncSession = Depends(get_session)):
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail=f"Area with id {area_id} not found")
    return area


@router.patch("/areas/{area_id}", response_model=Area)
async def update_area(
    area_id: int, area_update: AreaCreate, session: AsyncSession = Depends(get_session)
):
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail=f"Area with id {area_id} not found")

    area_data = area_update.model_dump(exclude_unset=True)
    for key, value in area_data.items():
        setattr(area, key, value)

    session.add(area)
    await session.commit()
    await session.refresh(area)
    return area


@router.delete("/areas/{area_id}", response_model=Area)
async def delete_area(area_id: int, session: AsyncSession = Depends(get_session)):
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=404, detail=f"Area with id {area_id} not found")

    await session.delete(area)
    await session.commit()
    return area


# Event CRUD operations
@router.post("/events/", response_model=Event)
async def create_event(
    event: EventCreate, session: AsyncSession = Depends(get_session)
):
    # Validate person_id
    if event.person_id is not None:
        person = await session.get(Person, event.person_id)
        if not person:
            raise HTTPException(
                status_code=404, detail=f"Person with id {event.person_id} not found"
            )

    # Validate area_id
    if event.area_id is not None:
        area = await session.get(Area, event.area_id)
        if not area:
            raise HTTPException(
                status_code=404, detail=f"Area with id {event.area_id} not found"
            )

    event = Event(**event.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.get("/events/", response_model=List[Event])
async def read_events(
    skip: int = 0,
    limit: int = 100,
    person_id: Optional[int] = None,
    area_id: Optional[int] = None,
    action_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(Event)

    if person_id:
        query = query.where(Event.person_id == person_id)
    if area_id:
        query = query.where(Event.area_id == area_id)
    if action_id:
        query = query.where(Event.action_id == action_id)

    events = await session.execute(query.offset(skip).limit(limit))
    return events.scalars().all()


@router.get("/events/{event_id}", response_model=Event)
async def read_event(event_id: int, session: AsyncSession = Depends(get_session)):
    event = await session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404, detail=f"Event with id {event_id} not found"
        )
    return event


@router.patch("/events/{event_id}", response_model=Event)
async def update_event(
    event_id: int,
    event_update: EventCreate,
    session: AsyncSession = Depends(get_session),
):
    event = await session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404, detail=f"Event with id {event_id} not found"
        )

    # Validate person_id if it's being updated
    if event_update.person_id is not None:
        person = await session.get(Person, event_update.person_id)
        if not person:
            raise HTTPException(
                status_code=404,
                detail=f"Person with id {event_update.person_id} not found",
            )

    # Validate area_id if it's being updated
    if event_update.area_id is not None:
        area = await session.get(Area, event_update.area_id)
        if not area:
            raise HTTPException(
                status_code=404, detail=f"Area with id {event_update.area_id} not found"
            )

    # Validate action_id if it's being updated
    if event_update.action_id is not None:
        action = await session.get(Action, event_update.action_id)
        if not action:
            raise HTTPException(
                status_code=404,
                detail=f"Action with id {event_update.action_id} not found",
            )

    event_data = event_update.model_dump(exclude_unset=True)
    for key, value in event_data.items():
        setattr(event, key, value)

    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.delete("/events/{event_id}", response_model=Event)
async def delete_event(event_id: int, session: AsyncSession = Depends(get_session)):
    event = await session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=404, detail=f"Event with id {event_id} not found"
        )

    await session.delete(event)
    await session.commit()
    return event


# Action CRUD operations
@router.post("/actions/", response_model=Action)
async def create_action(
    action: ActionCreate, session: AsyncSession = Depends(get_session)
):
    action = Action(**action.model_dump())
    session.add(action)
    await session.commit()
    await session.refresh(action)
    return action


@router.get("/actions/", response_model=List[Action])
async def read_actions(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    actions = await session.execute(select(Action).offset(skip).limit(limit))
    return actions.scalars().all()


@router.get("/actions/{action_id}", response_model=Action)
async def read_action(action_id: int, session: AsyncSession = Depends(get_session)):
    action = await session.get(Action, action_id)
    if not action:
        raise HTTPException(
            status_code=404, detail=f"Action with id {action_id} not found"
        )
    return action


@router.patch("/actions/{action_id}", response_model=Action)
async def update_action(
    action_id: int,
    action_update: ActionCreate,
    session: AsyncSession = Depends(get_session),
):
    action = await session.get(Action, action_id)
    if not action:
        raise HTTPException(
            status_code=404, detail=f"Action with id {action_id} not found"
        )

    action_data = action_update.model_dump(exclude_unset=True)
    for key, value in action_data.items():
        setattr(action, key, value)

    session.add(action)
    await session.commit()
    await session.refresh(action)
    return action


@router.delete("/actions/{action_id}", response_model=Action)
async def delete_action(action_id: int, session: AsyncSession = Depends(get_session)):
    action = await session.get(Action, action_id)
    if not action:
        raise HTTPException(
            status_code=404, detail=f"Action with id {action_id} not found"
        )

    await session.delete(action)
    await session.commit()
    return action


# Track CRUD operations
@router.post("/tracks/", response_model=Track)
async def create_track(
    track: TrackCreate, session: AsyncSession = Depends(get_session)
):
    # Validate person_id
    if track.person_id is not None:
        person = await session.get(Person, track.person_id)
        if not person:
            raise HTTPException(
                status_code=404, detail=f"Person with id {track.person_id} not found"
            )
    track = Track(**track.model_dump())
    session.add(track)
    await session.commit()
    await session.refresh(track)
    return track


@router.get("/tracks/", response_model=List[Track])
async def read_tracks(
    skip: int = 0,
    limit: int = 100,
    person_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(Track)

    if person_id:
        query = query.where(Track.person_id == person_id)

    tracks = await session.execute(query.offset(skip).limit(limit))
    return tracks.scalars().all()


@router.get("/tracks/{track_id}", response_model=Track)
async def read_track(track_id: int, session: AsyncSession = Depends(get_session)):
    track = await session.get(Track, track_id)
    if not track:
        raise HTTPException(
            status_code=404, detail=f"Track with id {track_id} not found"
        )
    return track


@router.patch("/tracks/{track_id}", response_model=Track)
async def update_track(
    track_id: int,
    track_update: TrackCreate,
    session: AsyncSession = Depends(get_session),
):
    track = await session.get(Track, track_id)
    if not track:
        raise HTTPException(
            status_code=404, detail=f"Track with id {track_id} not found"
        )

    # Validate person_id if it's being updated
    if track_update.person_id is not None:
        person = await session.get(Person, track_update.person_id)
        if not person:
            raise HTTPException(
                status_code=404,
                detail=f"Person with id {track_update.person_id} not found",
            )

    track_data = track_update.model_dump(exclude_unset=True)
    for key, value in track_data.items():
        setattr(track, key, value)

    session.add(track)
    await session.commit()
    await session.refresh(track)
    return track


@router.delete("/tracks/{track_id}", response_model=Track)
async def delete_track(track_id: int, session: AsyncSession = Depends(get_session)):
    track = await session.get(Track, track_id)
    if not track:
        raise HTTPException(
            status_code=404, detail=f"Track with id {track_id} not found"
        )

    await session.delete(track)
    await session.commit()
    return track
