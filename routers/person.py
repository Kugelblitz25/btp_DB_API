from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import resp_models as r
import db_models as m
from database import SessionLocal

router = APIRouter(tags=["Persons"])

async def get_session():
    async with SessionLocal() as session:
        yield session

# Hairline CRUD operations
@router.post("/hairlines/", response_model=r.Hairline)
async def create_hairline(hairline: r.Hairline, session: AsyncSession = Depends(get_session)):
    hairline = m.Hairline(**hairline.model_dump())
    session.add(hairline)
    await session.commit()
    await session.refresh(hairline)
    return hairline

@router.get("/hairlines/", response_model=List[r.Hairline])
async def read_hairlines(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    hairlines = await session.execute(select(m.Hairline).offset(skip).limit(limit))
    return hairlines.scalars().all()

@router.get("/hairlines/{hairline_id}", response_model=r.Hairline)
async def read_hairline(hairline_id: int, session: AsyncSession = Depends(get_session)):
    hairline = await session.get(m.Hairline, hairline_id)
    if not hairline:
        raise HTTPException(status_code=404, detail=f"Hairline with id {hairline_id} not found")
    return hairline


@router.patch("/hairlines/{hairline_id}", response_model=r.Hairline)
async def update_hairline(hairline_id: int, hairline_update: r.Hairline, session: AsyncSession = Depends(get_session)):
    hairline = await session.get(m.Hairline, hairline_id)
    if not hairline:
        raise HTTPException(status_code=404, detail=f"Hairline with id {hairline_id} not found")
    
    hairline_data = hairline_update.model_dump(exclude_unset=True)
    for key, value in hairline_data.items():
        setattr(hairline, key, value)
    
    session.add(hairline)
    await session.commit()
    await session.refresh(hairline)
    return hairline

@router.delete("/hairlines/{hairline_id}", response_model=r.Hairline)
async def delete_hairline(hairline_id: int, session: AsyncSession = Depends(get_session)):
    hairline = await session.get(m.Hairline, hairline_id)
    if not hairline:
        raise HTTPException(status_code=404, detail=f"Hairline with id {hairline_id} not found")
    
    await session.delete(hairline)
    await session.commit()
    return hairline

@router.post("/persons/", response_model=r.Person)
async def create_person(person: r.Person, session: AsyncSession = Depends(get_session)):
    if person.hairline_id is not None:
        hairline = await session.get(m.Hairline, person.hairline_id)
        if not hairline:
            raise HTTPException(status_code=404, detail=f"Hairline with id {person.hairline_id} not found")
    person = m.Person(**person.model_dump())
    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person

@router.get("/persons/", response_model=List[r.Person])
async def read_persons(
    skip: int = 0, 
    limit: int = 100, 
    session: AsyncSession = Depends(get_session)
):
    query = select(m.Person)
    persons = await session.execute(query.offset(skip).limit(limit))
    return persons.scalars().all()

@router.get("/persons/{person_id}", response_model=r.Person)
async def read_person(person_id: int, session: AsyncSession = Depends(get_session)):
    person = await session.get(m.Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id {person_id} not found")
    return person

@router.patch("/persons/{person_id}", response_model=r.Person)
async def update_person(person_id: int, person_update: r.Person, session: AsyncSession = Depends(get_session)):
    person = await session.get(m.Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id {person_id} not found")
    
    # Validate hairline_id if it's being updated
    if person_update.hairline_id is not None:
        hairline = await session.get(m.Hairline, person_update.hairline_id)
        if not hairline:
            raise HTTPException(status_code=404, detail=f"Hairline with id {person_update.hairline_id} not found")
    
    person_data = person_update.model_dump(exclude_unset=True)
    for key, value in person_data.items():
        setattr(person, key, value)
    
    session.add(person)
    await session.commit()
    await session.refresh(person)
    return person

@router.delete("/persons/{person_id}", response_model=r.Person)
async def delete_person(person_id: int, session: AsyncSession = Depends(get_session)):
    person = await session.get(m.Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with id {person_id} not found")
    
    await session.delete(person)
    await session.commit()
    return person

@router.post("/apparels/", response_model=r.Apparel)
async def create_apparel(apparel: r.Apparel, session: AsyncSession = Depends(get_session)):
    # Validate person_id
    if apparel.person_id is not None:
        person = await session.get(m.Person, apparel.person_id)
        if not person:
            raise HTTPException(status_code=404, detail=f"Person with id {apparel.person_id} not found")
    apparel = m.Apparel(**apparel.model_dump())
    session.add(apparel)
    await session.commit()
    await session.refresh(apparel)
    return apparel

@router.get("/apparels/", response_model=List[r.Apparel])
async def read_apparels(
    skip: int = 0, 
    limit: int = 100, 
    person_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(m.Apparel)
    
    if person_id:
        query = query.where(m.Apparel.person_id == person_id)
        
    apparels = await session.execute(query.offset(skip).limit(limit))
    return apparels.scalars().all()

@router.get("/apparels/{apparel_id}", response_model=r.Apparel)
async def read_apparel(apparel_id: int, session: AsyncSession = Depends(get_session)):
    apparel = await session.get(m.Apparel, apparel_id)
    if not apparel:
        raise HTTPException(status_code=404, detail=f"Apparel with id {apparel_id} not found")
    return apparel

@router.patch("/apparels/{apparel_id}", response_model=r.Apparel)
async def update_apparel(apparel_id: int, apparel_update: r.Apparel, session: AsyncSession = Depends(get_session)):
    apparel = await session.get(m.Apparel, apparel_id)
    if not apparel:
        raise HTTPException(status_code=404, detail=f"Apparel with id {apparel_id} not found")
    
    # Validate person_id if it's being updated
    if apparel_update.person_id is not None:
        person = await session.get(m.Person, apparel_update.person_id)
        if not person:
            raise HTTPException(status_code=404, detail=f"Person with id {apparel_update.person_id} not found")
    
    apparel_data = apparel_update.model_dump(exclude_unset=True)
    for key, value in apparel_data.items():
        setattr(apparel, key, value)
    
    session.add(apparel)
    await session.commit()
    await session.refresh(apparel)
    return apparel

@router.delete("/apparels/{apparel_id}", response_model=r.Apparel)
async def delete_apparel(apparel_id: int, session: AsyncSession = Depends(get_session)):
    apparel = await session.get(m.Apparel, apparel_id)
    if not apparel:
        raise HTTPException(status_code=404, detail=f"Apparel with id {apparel_id} not found")
    
    await session.delete(apparel)
    await session.commit()
    return apparel