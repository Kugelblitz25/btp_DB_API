from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import SessionLocal
from models import (
    Age,
    AgeCreate,
    Apparel,
    ApparelCreate,
    Gender,
    GenderCreate,
    Hairline,
    HairlineCreate,
    Person,
    PersonCreate,
    Race,
    RaceCreate,
)

router = APIRouter(tags=["Persons"])


async def get_session():
    async with SessionLocal() as session:
        yield session


# Gender CRUD operations
@router.post("/genders/", response_model=Gender)
async def create_gender(
    gender: GenderCreate, session: AsyncSession = Depends(get_session)
):
    gender = Gender(**gender.model_dump())
    session.add(gender)
    await session.commit()
    await session.refresh(gender)
    return gender


@router.get("/genders/", response_model=List[Gender])
async def read_genders(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    genders = await session.execute(select(Gender).offset(skip).limit(limit))
    return genders.scalars().all()


@router.get("/genders/{gender_id}", response_model=Gender)
async def read_gender(gender_id: int, session: AsyncSession = Depends(get_session)):
    gender = await session.get(Gender, gender_id)
    if not gender:
        raise HTTPException(
            status_code=404, detail=f"Gender with id {gender_id} not found"
        )
    return gender


@router.patch("/genders/{gender_id}", response_model=Gender)
async def update_gender(
    gender_id: int,
    gender_update: GenderCreate,
    session: AsyncSession = Depends(get_session),
):
    gender = await session.get(Gender, gender_id)
    if not gender:
        raise HTTPException(
            status_code=404, detail=f"Gender with id {gender_id} not found"
        )

    gender_data = gender_update.model_dump(exclude_unset=True)
    for key, value in gender_data.items():
        setattr(gender, key, value)

    session.add(gender)
    await session.commit()
    await session.refresh(gender)
    return gender


@router.delete("/genders/{gender_id}", response_model=Gender)
async def delete_gender(
    gender_id: int, session: AsyncSession = Depends(get_session)
):
    gender = await session.get(Gender, gender_id)
    if not gender:
        raise HTTPException(
            status_code=404, detail=f"Gender with id {gender_id} not found"
        )

    await session.delete(gender)
    await session.commit()
    return gender


# Race CRUD operations
@router.post("/races/", response_model=Race)
async def create_race(
    race: RaceCreate, session: AsyncSession = Depends(get_session)
):
    race = Race(**race.model_dump())
    session.add(race)
    await session.commit()
    await session.refresh(race)
    return race


@router.get("/races/", response_model=List[Race])
async def read_races(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    races = await session.execute(select(Race).offset(skip).limit(limit))
    return races.scalars().all()


@router.get("/races/{race_id}", response_model=Race)
async def read_race(race_id: int, session: AsyncSession = Depends(get_session)):
    race = await session.get(Race, race_id)
    if not race:
        raise HTTPException(
            status_code=404, detail=f"Race with id {race_id} not found"
        )
    return race


@router.patch("/races/{race_id}", response_model=Race)
async def update_race(
    race_id: int,
    race_update: RaceCreate,
    session: AsyncSession = Depends(get_session),
):
    race = await session.get(Race, race_id)
    if not race:
        raise HTTPException(
            status_code=404, detail=f"Race with id {race_id} not found"
        )

    race_data = race_update.model_dump(exclude_unset=True)
    for key, value in race_data.items():
        setattr(race, key, value)

    session.add(race)
    await session.commit()
    await session.refresh(race)
    return race


@router.delete("/races/{race_id}", response_model=Race)
async def delete_race(
    race_id: int, session: AsyncSession = Depends(get_session)
):
    race = await session.get(Race, race_id)
    if not race:
        raise HTTPException(
            status_code=404, detail=f"Race with id {race_id} not found"
        )

    await session.delete(race)
    await session.commit()
    return race


# Age CRUD operations
@router.post("/ages/", response_model=Age)
async def create_age(
    age: AgeCreate, session: AsyncSession = Depends(get_session)
):
    age = Age(**age.model_dump())
    session.add(age)
    await session.commit()
    await session.refresh(age)
    return age


@router.get("/ages/", response_model=List[Age])
async def read_ages(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    ages = await session.execute(select(Age).offset(skip).limit(limit))
    return ages.scalars().all()


@router.get("/ages/{age_id}", response_model=Age)
async def read_age(age_id: int, session: AsyncSession = Depends(get_session)):
    age = await session.get(Age, age_id)
    if not age:
        raise HTTPException(
            status_code=404, detail=f"Age with id {age_id} not found"
        )
    return age


@router.patch("/ages/{age_id}", response_model=Age)
async def update_age(
    age_id: int,
    age_update: AgeCreate,
    session: AsyncSession = Depends(get_session),
):
    age = await session.get(Age, age_id)
    if not age:
        raise HTTPException(
            status_code=404, detail=f"Age with id {age_id} not found"
        )

    age_data = age_update.model_dump(exclude_unset=True)
    for key, value in age_data.items():
        setattr(age, key, value)

    session.add(age)
    await session.commit()
    await session.refresh(age)
    return age


@router.delete("/ages/{age_id}", response_model=Age)
async def delete_age(
    age_id: int, session: AsyncSession = Depends(get_session)
):
    age = await session.get(Age, age_id)
    if not age:
        raise HTTPException(
            status_code=404, detail=f"Age with id {age_id} not found"
        )

    await session.delete(age)
    await session.commit()
    return age


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
    # Validate gender_id
    if person.gender_id is not None:
        gender = await session.get(Gender, person.gender_id)
        if not gender:
            raise HTTPException(
                status_code=404,
                detail=f"Gender with id {person.gender_id} not found",
            )
    
    # Validate hairline_id if provided
    if person.hairline_id is not None:
        hairline = await session.get(Hairline, person.hairline_id)
        if not hairline:
            raise HTTPException(
                status_code=404,
                detail=f"Hairline with id {person.hairline_id} not found",
            )
    
    # Validate race_id if provided
    if person.race_id is not None:
        race = await session.get(Race, person.race_id)
        if not race:
            raise HTTPException(
                status_code=404,
                detail=f"Race with id {person.race_id} not found",
            )
    
    # Validate age_id if provided
    if person.age_id is not None:
        age = await session.get(Age, person.age_id)
        if not age:
            raise HTTPException(
                status_code=404,
                detail=f"Age with id {person.age_id} not found",
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

    # Validate gender_id if it's being updated
    if person_update.gender_id is not None:
        gender = await session.get(Gender, person_update.gender_id)
        if not gender:
            raise HTTPException(
                status_code=404,
                detail=f"Gender with id {person_update.gender_id} not found",
            )

    # Validate hairline_id if it's being updated
    if person_update.hairline_id is not None:
        hairline = await session.get(Hairline, person_update.hairline_id)
        if not hairline:
            raise HTTPException(
                status_code=404,
                detail=f"Hairline with id {person_update.hairline_id} not found",
            )
    
    # Validate race_id if it's being updated
    if person_update.race_id is not None:
        race = await session.get(Race, person_update.race_id)
        if not race:
            raise HTTPException(
                status_code=404,
                detail=f"Race with id {person_update.race_id} not found",
            )
    
    # Validate age_id if it's being updated
    if person_update.age_id is not None:
        age = await session.get(Age, person_update.age_id)
        if not age:
            raise HTTPException(
                status_code=404,
                detail=f"Age with id {person_update.age_id} not found",
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
