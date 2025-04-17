from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import SessionLocal
from models import (
    Apparel,
    ApparelCreate,
    Hairline,
    HairlineCreate,
    Person,
    PersonCreate,
)

router = APIRouter(tags=["Persons"])


async def get_session():
    async with SessionLocal() as session:
        yield session


# Hairline CRUD operations
@router.post("/hairlines/", response_model=Hairline)
async def create_hairline(
    hairline: HairlineCreate, session: AsyncSession = Depends(get_session)
):
    hairline = Hairline(**hairline.model_dump())
    session.add(hairline)
    await session.commit()
    await session.refresh(hairline)
    return hairline


@router.get("/hairlines/", response_model=List[Hairline])
async def read_hairlines(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    hairlines = await session.execute(select(Hairline).offset(skip).limit(limit))
    return hairlines.scalars().all()


@router.get("/hairlines/{hairline_id}", response_model=Hairline)
async def read_hairline(hairline_id: int, session: AsyncSession = Depends(get_session)):
    hairline = await session.get(Hairline, hairline_id)
    if not hairline:
        raise HTTPException(
            status_code=404, detail=f"Hairline with id {hairline_id} not found"
        )
    return hairline


@router.patch("/hairlines/{hairline_id}", response_model=Hairline)
async def update_hairline(
    hairline_id: int,
    hairline_update: HairlineCreate,
    session: AsyncSession = Depends(get_session),
):
    hairline = await session.get(Hairline, hairline_id)
    if not hairline:
        raise HTTPException(
            status_code=404, detail=f"Hairline with id {hairline_id} not found"
        )

    hairline_data = hairline_update.model_dump(exclude_unset=True)
    for key, value in hairline_data.items():
        setattr(hairline, key, value)

    session.add(hairline)
    await session.commit()
    await session.refresh(hairline)
    return hairline


@router.delete("/hairlines/{hairline_id}", response_model=Hairline)
async def delete_hairline(
    hairline_id: int, session: AsyncSession = Depends(get_session)
):
    hairline = await session.get(Hairline, hairline_id)
    if not hairline:
        raise HTTPException(
            status_code=404, detail=f"Hairline with id {hairline_id} not found"
        )

    await session.delete(hairline)
    await session.commit()
    return hairline


@router.post("/persons/", response_model=Person)
async def create_person(
    person: PersonCreate, session: AsyncSession = Depends(get_session)
):
    if person.hairline_id is not None:
        hairline = await session.get(Hairline, person.hairline_id)
        if not hairline:
            raise HTTPException(
                status_code=404,
                detail=f"Hairline with id {person.hairline_id} not found",
            )
    person = Person(**person.model_dump())
    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person


@router.get("/persons/", response_model=List[Person])
async def read_persons(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    query = select(Person)
    persons = await session.execute(query.offset(skip).limit(limit))
    return persons.scalars().all()


@router.get("/persons/{person_id}", response_model=Person)
async def read_person(person_id: int, session: AsyncSession = Depends(get_session)):
    person = await session.get(Person, person_id)
    if not person:
        raise HTTPException(
            status_code=404, detail=f"Person with id {person_id} not found"
        )
    return person


@router.patch("/persons/{person_id}", response_model=Person)
async def update_person(
    person_id: int,
    person_update: PersonCreate,
    session: AsyncSession = Depends(get_session),
):
    person = await session.get(Person, person_id)
    if not person:
        raise HTTPException(
            status_code=404, detail=f"Person with id {person_id} not found"
        )

    # Validate hairline_id if it's being updated
    if person_update.hairline_id is not None:
        hairline = await session.get(Hairline, person_update.hairline_id)
        if not hairline:
            raise HTTPException(
                status_code=404,
                detail=f"Hairline with id {person_update.hairline_id} not found",
            )

    person_data = person_update.model_dump(exclude_unset=True)
    for key, value in person_data.items():
        setattr(person, key, value)

    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person


@router.delete("/persons/{person_id}", response_model=Person)
async def delete_person(person_id: int, session: AsyncSession = Depends(get_session)):
    person = await session.get(Person, person_id)
    if not person:
        raise HTTPException(
            status_code=404, detail=f"Person with id {person_id} not found"
        )

    await session.delete(person)
    await session.commit()
    return person


@router.post("/apparels/", response_model=Apparel)
async def create_apparel(
    apparel: ApparelCreate, session: AsyncSession = Depends(get_session)
):
    # Validate person_id
    if apparel.person_id is not None:
        person = await session.get(Person, apparel.person_id)
        if not person:
            raise HTTPException(
                status_code=404, detail=f"Person with id {apparel.person_id} not found"
            )
    apparel = Apparel(**apparel.model_dump())
    session.add(apparel)
    await session.commit()
    await session.refresh(apparel)
    return apparel


@router.get("/apparels/", response_model=List[Apparel])
async def read_apparels(
    skip: int = 0,
    limit: int = 100,
    person_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    query = select(Apparel)

    if person_id:
        query = query.where(Apparel.person_id == person_id)

    apparels = await session.execute(query.offset(skip).limit(limit))
    return apparels.scalars().all()


@router.get("/apparels/{apparel_id}", response_model=Apparel)
async def read_apparel(apparel_id: int, session: AsyncSession = Depends(get_session)):
    apparel = await session.get(Apparel, apparel_id)
    if not apparel:
        raise HTTPException(
            status_code=404, detail=f"Apparel with id {apparel_id} not found"
        )
    return apparel


@router.patch("/apparels/{apparel_id}", response_model=Apparel)
async def update_apparel(
    apparel_id: int,
    apparel_update: ApparelCreate,
    session: AsyncSession = Depends(get_session),
):
    apparel = await session.get(Apparel, apparel_id)
    if not apparel:
        raise HTTPException(
            status_code=404, detail=f"Apparel with id {apparel_id} not found"
        )

    # Validate person_id if it's being updated
    if apparel_update.person_id is not None:
        person = await session.get(Person, apparel_update.person_id)
        if not person:
            raise HTTPException(
                status_code=404,
                detail=f"Person with id {apparel_update.person_id} not found",
            )

    apparel_data = apparel_update.model_dump(exclude_unset=True)
    for key, value in apparel_data.items():
        setattr(apparel, key, value)

    session.add(apparel)
    await session.commit()
    await session.refresh(apparel)
    return apparel


@router.delete("/apparels/{apparel_id}", response_model=Apparel)
async def delete_apparel(apparel_id: int, session: AsyncSession = Depends(get_session)):
    apparel = await session.get(Apparel, apparel_id)
    if not apparel:
        raise HTTPException(
            status_code=404, detail=f"Apparel with id {apparel_id} not found"
        )

    await session.delete(apparel)
    await session.commit()
    return apparel
