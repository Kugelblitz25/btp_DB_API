"""API Endpoints for managing Persons and related demographic information.

This module provides CRUD (Create, Read, Update, Delete) operations for:
- Persons
- Genders
- Races
- Ages
- Hairlines
- Apparels
"""
from typing import List, Optional, Sequence, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import SessionLocal, get_db # Assuming get_db is the preferred way from database.py
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

router: APIRouter = APIRouter(tags=["Persons"])


# Dependency for getting a database session (if not using get_db directly from database.py)
# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     """Provides an asynchronous database session."""
#     async with SessionLocal() as session:
#         yield session


# Gender CRUD operations
@router.post("/genders/", response_model=Gender)
async def create_gender(
    gender: GenderCreate, session: AsyncSession = Depends(get_db)
) -> Gender:
    """Creates a new gender type.

    Args:
        gender: The gender data to create.
        session: The database session.

    Returns:
        The created gender.
    """
    db_gender = Gender.model_validate(gender)
    session.add(db_gender)
    await session.commit()
    await session.refresh(db_gender)
    return db_gender


@router.get("/genders/", response_model=List[Gender])
async def read_genders(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Gender]:
    """Retrieves a list of gender types with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The database session.

    Returns:
        A list of genders.
    """
    result = await session.execute(select(Gender).offset(skip).limit(limit))
    genders: Sequence[Gender] = result.scalars().all()
    return genders


@router.get("/genders/{gender_id}", response_model=Gender)
async def read_gender(gender_id: int, session: AsyncSession = Depends(get_db)) -> Gender:
    """Retrieves a specific gender type by its ID.

    Args:
        gender_id: The ID of the gender to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the gender with the given ID is not found.

    Returns:
        The requested gender.
    """
    db_gender: Optional[Gender] = await session.get(Gender, gender_id)
    if not db_gender:
        raise HTTPException(
            status_code=404, detail=f"Gender with id {gender_id} not found"
        )
    return db_gender


@router.patch("/genders/{gender_id}", response_model=Gender)
async def update_gender(
    gender_id: int,
    gender_update: GenderCreate,
    session: AsyncSession = Depends(get_db),
) -> Gender:
    """Updates an existing gender type.

    Args:
        gender_id: The ID of the gender to update.
        gender_update: The new data for the gender.
        session: The database session.

    Raises:
        HTTPException: If the gender with the given ID is not found.

    Returns:
        The updated gender.
    """
    db_gender: Optional[Gender] = await session.get(Gender, gender_id)
    if not db_gender:
        raise HTTPException(
            status_code=404, detail=f"Gender with id {gender_id} not found"
        )

    gender_data = gender_update.model_dump(exclude_unset=True)
    for key, value in gender_data.items():
        setattr(db_gender, key, value)

    session.add(db_gender)
    await session.commit()
    await session.refresh(db_gender)
    return db_gender


@router.delete("/genders/{gender_id}", response_model=Gender)
async def delete_gender(
    gender_id: int, session: AsyncSession = Depends(get_db)
) -> Gender:
    """Deletes a gender type by its ID.

    Args:
        gender_id: The ID of the gender to delete.
        session: The database session.

    Raises:
        HTTPException: If the gender with the given ID is not found.

    Returns:
        The deleted gender.
    """
    db_gender: Optional[Gender] = await session.get(Gender, gender_id)
    if not db_gender:
        raise HTTPException(
            status_code=404, detail=f"Gender with id {gender_id} not found"
        )

    await session.delete(db_gender)
    await session.commit()
    return db_gender


# Race CRUD operations
@router.post("/races/", response_model=Race)
async def create_race(
    race: RaceCreate, session: AsyncSession = Depends(get_db)
) -> Race:
    """Creates a new race type.

    Args:
        race: The race data to create.
        session: The database session.

    Returns:
        The created race.
    """
    db_race = Race.model_validate(race)
    session.add(db_race)
    await session.commit()
    await session.refresh(db_race)
    return db_race


@router.get("/races/", response_model=List[Race])
async def read_races(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Race]:
    """Retrieves a list of race types with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The database session.

    Returns:
        A list of races.
    """
    result = await session.execute(select(Race).offset(skip).limit(limit))
    races: Sequence[Race] = result.scalars().all()
    return races


@router.get("/races/{race_id}", response_model=Race)
async def read_race(race_id: int, session: AsyncSession = Depends(get_db)) -> Race:
    """Retrieves a specific race type by its ID.

    Args:
        race_id: The ID of the race to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the race with the given ID is not found.

    Returns:
        The requested race.
    """
    db_race: Optional[Race] = await session.get(Race, race_id)
    if not db_race:
        raise HTTPException(
            status_code=404, detail=f"Race with id {race_id} not found"
        )
    return db_race


@router.patch("/races/{race_id}", response_model=Race)
async def update_race(
    race_id: int,
    race_update: RaceCreate,
    session: AsyncSession = Depends(get_db),
) -> Race:
    """Updates an existing race type.

    Args:
        race_id: The ID of the race to update.
        race_update: The new data for the race.
        session: The database session.

    Raises:
        HTTPException: If the race with the given ID is not found.

    Returns:
        The updated race.
    """
    db_race: Optional[Race] = await session.get(Race, race_id)
    if not db_race:
        raise HTTPException(
            status_code=404, detail=f"Race with id {race_id} not found"
        )

    race_data = race_update.model_dump(exclude_unset=True)
    for key, value in race_data.items():
        setattr(db_race, key, value)

    session.add(db_race)
    await session.commit()
    await session.refresh(db_race)
    return db_race


@router.delete("/races/{race_id}", response_model=Race)
async def delete_race(
    race_id: int, session: AsyncSession = Depends(get_db)
) -> Race:
    """Deletes a race type by its ID.

    Args:
        race_id: The ID of the race to delete.
        session: The database session.

    Raises:
        HTTPException: If the race with the given ID is not found.

    Returns:
        The deleted race.
    """
    db_race: Optional[Race] = await session.get(Race, race_id)
    if not db_race:
        raise HTTPException(
            status_code=404, detail=f"Race with id {race_id} not found"
        )

    await session.delete(db_race)
    await session.commit()
    return db_race


# Age CRUD operations
@router.post("/ages/", response_model=Age)
async def create_age(
    age: AgeCreate, session: AsyncSession = Depends(get_db)
) -> Age:
    """Creates a new age category.

    Args:
        age: The age data to create.
        session: The database session.

    Returns:
        The created age category.
    """
    db_age = Age.model_validate(age)
    session.add(db_age)
    await session.commit()
    await session.refresh(db_age)
    return db_age


@router.get("/ages/", response_model=List[Age])
async def read_ages(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Age]:
    """Retrieves a list of age categories with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The database session.

    Returns:
        A list of age categories.
    """
    result = await session.execute(select(Age).offset(skip).limit(limit))
    ages: Sequence[Age] = result.scalars().all()
    return ages


@router.get("/ages/{age_id}", response_model=Age)
async def read_age(age_id: int, session: AsyncSession = Depends(get_db)) -> Age:
    """Retrieves a specific age category by its ID.

    Args:
        age_id: The ID of the age category to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the age category with the given ID is not found.

    Returns:
        The requested age category.
    """
    db_age: Optional[Age] = await session.get(Age, age_id)
    if not db_age:
        raise HTTPException(
            status_code=404, detail=f"Age with id {age_id} not found"
        )
    return db_age


@router.patch("/ages/{age_id}", response_model=Age)
async def update_age(
    age_id: int,
    age_update: AgeCreate,
    session: AsyncSession = Depends(get_db),
) -> Age:
    """Updates an existing age category.

    Args:
        age_id: The ID of the age category to update.
        age_update: The new data for the age category.
        session: The database session.

    Raises:
        HTTPException: If the age category with the given ID is not found.

    Returns:
        The updated age category.
    """
    db_age: Optional[Age] = await session.get(Age, age_id)
    if not db_age:
        raise HTTPException(
            status_code=404, detail=f"Age with id {age_id} not found"
        )

    age_data = age_update.model_dump(exclude_unset=True)
    for key, value in age_data.items():
        setattr(db_age, key, value)

    session.add(db_age)
    await session.commit()
    await session.refresh(db_age)
    return db_age


@router.delete("/ages/{age_id}", response_model=Age)
async def delete_age(
    age_id: int, session: AsyncSession = Depends(get_db)
) -> Age:
    """Deletes an age category by its ID.

    Args:
        age_id: The ID of the age category to delete.
        session: The database session.

    Raises:
        HTTPException: If the age category with the given ID is not found.

    Returns:
        The deleted age category.
    """
    db_age: Optional[Age] = await session.get(Age, age_id)
    if not db_age:
        raise HTTPException(
            status_code=404, detail=f"Age with id {age_id} not found"
        )

    await session.delete(db_age)
    await session.commit()
    return db_age


# Hairline CRUD operations
@router.post("/hairlines/", response_model=Hairline)
async def create_hairline(
    hairline: HairlineCreate, session: AsyncSession = Depends(get_db)
) -> Hairline:
    """Creates a new hairline type.

    Args:
        hairline: The hairline data to create.
        session: The database session.

    Returns:
        The created hairline type.
    """
    db_hairline = Hairline.model_validate(hairline)
    session.add(db_hairline)
    await session.commit()
    await session.refresh(db_hairline)
    return db_hairline


@router.get("/hairlines/", response_model=List[Hairline])
async def read_hairlines(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Hairline]:
    """Retrieves a list of hairline types with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The database session.

    Returns:
        A list of hairline types.
    """
    result = await session.execute(select(Hairline).offset(skip).limit(limit))
    hairlines: Sequence[Hairline] = result.scalars().all()
    return hairlines


@router.get("/hairlines/{hairline_id}", response_model=Hairline)
async def read_hairline(hairline_id: int, session: AsyncSession = Depends(get_db)) -> Hairline:
    """Retrieves a specific hairline type by its ID.

    Args:
        hairline_id: The ID of the hairline type to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the hairline type with the given ID is not found.

    Returns:
        The requested hairline type.
    """
    db_hairline: Optional[Hairline] = await session.get(Hairline, hairline_id)
    if not db_hairline:
        raise HTTPException(
            status_code=404, detail=f"Hairline with id {hairline_id} not found"
        )
    return db_hairline


@router.patch("/hairlines/{hairline_id}", response_model=Hairline)
async def update_hairline(
    hairline_id: int,
    hairline_update: HairlineCreate,
    session: AsyncSession = Depends(get_db),
) -> Hairline:
    """Updates an existing hairline type.

    Args:
        hairline_id: The ID of the hairline type to update.
        hairline_update: The new data for the hairline type.
        session: The database session.

    Raises:
        HTTPException: If the hairline type with the given ID is not found.

    Returns:
        The updated hairline type.
    """
    db_hairline: Optional[Hairline] = await session.get(Hairline, hairline_id)
    if not db_hairline:
        raise HTTPException(
            status_code=404, detail=f"Hairline with id {hairline_id} not found"
        )

    hairline_data = hairline_update.model_dump(exclude_unset=True)
    for key, value in hairline_data.items():
        setattr(db_hairline, key, value)

    session.add(db_hairline)
    await session.commit()
    await session.refresh(db_hairline)
    return db_hairline


@router.delete("/hairlines/{hairline_id}", response_model=Hairline)
async def delete_hairline(
    hairline_id: int, session: AsyncSession = Depends(get_db)
) -> Hairline:
    """Deletes a hairline type by its ID.

    Args:
        hairline_id: The ID of the hairline type to delete.
        session: The database session.

    Raises:
        HTTPException: If the hairline type with the given ID is not found.

    Returns:
        The deleted hairline type.
    """
    db_hairline: Optional[Hairline] = await session.get(Hairline, hairline_id)
    if not db_hairline:
        raise HTTPException(
            status_code=404, detail=f"Hairline with id {hairline_id} not found"
        )

    await session.delete(db_hairline)
    await session.commit()
    return db_hairline


# Person CRUD operations
@router.post("/persons/", response_model=Person)
async def create_person(
    person: PersonCreate, session: AsyncSession = Depends(get_db)
) -> Person:
    """Creates a new person.

    Validates the existence of related Gender, Hairline, Race, and Age if their IDs are provided.

    Args:
        person: The person data to create.
        session: The database session.

    Raises:
        HTTPException: If any related entity (Gender, Hairline, Race, Age) is not found.

    Returns:
        The created person.
    """
    # Validate gender_id
    if person.gender_id is not None:
        db_gender: Optional[Gender] = await session.get(Gender, person.gender_id)
        if not db_gender:
            raise HTTPException(
                status_code=404,
                detail=f"Gender with id {person.gender_id} not found",
            )
    
    # Validate hairline_id if provided
    if person.hairline_id is not None:
        db_hairline: Optional[Hairline] = await session.get(Hairline, person.hairline_id)
        if not db_hairline:
            raise HTTPException(
                status_code=404,
                detail=f"Hairline with id {person.hairline_id} not found",
            )
    
    # Validate race_id if provided
    if person.race_id is not None:
        db_race: Optional[Race] = await session.get(Race, person.race_id)
        if not db_race:
            raise HTTPException(
                status_code=404,
                detail=f"Race with id {person.race_id} not found",
            )
    
    # Validate age_id if provided
    if person.age_id is not None:
        db_age: Optional[Age] = await session.get(Age, person.age_id)
        if not db_age:
            raise HTTPException(
                status_code=404,
                detail=f"Age with id {person.age_id} not found",
            )
            
    db_person = Person.model_validate(person)
    session.add(db_person)
    await session.commit()
    await session.refresh(db_person)
    return db_person


@router.get("/persons/", response_model=List[Person])
async def read_persons(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Person]:
    """Retrieves a list of persons with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The database session.

    Returns:
        A list of persons.
    """
    query = select(Person)
    result = await session.execute(query.offset(skip).limit(limit))
    persons: Sequence[Person] = result.scalars().all()
    return persons


@router.get("/persons/{person_id}", response_model=Person) # Consider PersonReadWithDetails if available/needed
async def read_person(person_id: int, session: AsyncSession = Depends(get_db)) -> Person:
    """Retrieves a specific person by their ID.

    Args:
        person_id: The ID of the person to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the person with the given ID is not found.

    Returns:
        The requested person.
    """
    # TODO: Implement PersonReadWithDetails if details from related tables are needed.
    # For now, using the base Person model.
    # Example for eager loading (if PersonReadWithDetails needs it):
    # from sqlalchemy.orm import selectinload
    # query = select(Person).where(Person.id == person_id).options(
    #     selectinload(Person.gender),
    #     selectinload(Person.hairline),
    #     selectinload(Person.race),
    #     selectinload(Person.age),
    #     selectinload(Person.apparels),
    #     selectinload(Person.events),
    #     selectinload(Person.tracks)
    # )
    # result = await session.execute(query)
    # db_person: Optional[Person] = result.scalar_one_or_none()
    db_person: Optional[Person] = await session.get(Person, person_id)
    if not db_person:
        raise HTTPException(
            status_code=404, detail=f"Person with id {person_id} not found"
        )
    return db_person


@router.patch("/persons/{person_id}", response_model=Person)
async def update_person(
    person_id: int,
    person_update: PersonCreate,
    session: AsyncSession = Depends(get_db),
) -> Person:
    """Updates an existing person.

    Validates the existence of related Gender, Hairline, Race, and Age if their IDs are being updated.

    Args:
        person_id: The ID of the person to update.
        person_update: The new data for the person.
        session: The database session.

    Raises:
        HTTPException: If the person or any related entity is not found.

    Returns:
        The updated person.
    """
    db_person: Optional[Person] = await session.get(Person, person_id)
    if not db_person:
        raise HTTPException(
            status_code=404, detail=f"Person with id {person_id} not found"
        )

    # Validate gender_id if it's being updated
    if person_update.gender_id is not None and person_update.gender_id != db_person.gender_id:
        db_gender: Optional[Gender] = await session.get(Gender, person_update.gender_id)
        if not db_gender:
            raise HTTPException(
                status_code=404,
                detail=f"Gender with id {person_update.gender_id} not found",
            )

    # Validate hairline_id if it's being updated
    if person_update.hairline_id is not None and person_update.hairline_id != db_person.hairline_id:
        db_hairline: Optional[Hairline] = await session.get(Hairline, person_update.hairline_id)
        if not db_hairline:
            raise HTTPException(
                status_code=404,
                detail=f"Hairline with id {person_update.hairline_id} not found",
            )
    
    # Validate race_id if it's being updated
    if person_update.race_id is not None and person_update.race_id != db_person.race_id:
        db_race: Optional[Race] = await session.get(Race, person_update.race_id)
        if not db_race:
            raise HTTPException(
                status_code=404,
                detail=f"Race with id {person_update.race_id} not found",
            )
    
    # Validate age_id if it's being updated
    if person_update.age_id is not None and person_update.age_id != db_person.age_id:
        db_age: Optional[Age] = await session.get(Age, person_update.age_id)
        if not db_age:
            raise HTTPException(
                status_code=404,
                detail=f"Age with id {person_update.age_id} not found",
            )

    person_data = person_update.model_dump(exclude_unset=True)
    for key, value in person_data.items():
        setattr(db_person, key, value)

    session.add(db_person)
    await session.commit()
    await session.refresh(db_person)
    return db_person


@router.delete("/persons/{person_id}", response_model=Person)
async def delete_person(person_id: int, session: AsyncSession = Depends(get_db)) -> Person:
    """Deletes a person by their ID.

    Args:
        person_id: The ID of the person to delete.
        session: The database session.

    Raises:
        HTTPException: If the person with the given ID is not found.

    Returns:
        The deleted person.
    """
    db_person: Optional[Person] = await session.get(Person, person_id)
    if not db_person:
        raise HTTPException(
            status_code=404, detail=f"Person with id {person_id} not found"
        )

    await session.delete(db_person)
    await session.commit()
    return db_person


# Apparel CRUD operations
@router.post("/apparels/", response_model=Apparel)
async def create_apparel(
    apparel: ApparelCreate, session: AsyncSession = Depends(get_db)
) -> Apparel:
    """Creates new apparel information for a person.

    Validates the existence of the related Person.

    Args:
        apparel: The apparel data to create.
        session: The database session.

    Raises:
        HTTPException: If the related Person is not found.

    Returns:
        The created apparel information.
    """
    # Validate person_id
    if apparel.person_id is not None: # Should always be present based on model
        db_person: Optional[Person] = await session.get(Person, apparel.person_id)
        if not db_person:
            raise HTTPException(
                status_code=404, detail=f"Person with id {apparel.person_id} not found"
            )
    db_apparel = Apparel.model_validate(apparel)
    session.add(db_apparel)
    await session.commit()
    await session.refresh(db_apparel)
    return db_apparel


@router.get("/apparels/", response_model=List[Apparel])
async def read_apparels(
    skip: int = Query(0, ge=0, description="Number of records to skip."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    person_id: Optional[int] = Query(None, description="Filter apparels by Person ID."),
    session: AsyncSession = Depends(get_db),
) -> Sequence[Apparel]:
    """Retrieves a list of apparel information with optional filters and pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        person_id: Optional Person ID to filter by.
        session: The database session.

    Returns:
        A list of apparel information.
    """
    query = select(Apparel)

    if person_id is not None:
        query = query.where(Apparel.person_id == person_id)

    result = await session.execute(query.offset(skip).limit(limit))
    apparels: Sequence[Apparel] = result.scalars().all()
    return apparels


@router.get("/apparels/{apparel_id}", response_model=Apparel)
async def read_apparel(apparel_id: int, session: AsyncSession = Depends(get_db)) -> Apparel:
    """Retrieves specific apparel information by its ID.

    Args:
        apparel_id: The ID of the apparel to retrieve.
        session: The database session.

    Raises:
        HTTPException: If the apparel with the given ID is not found.

    Returns:
        The requested apparel information.
    """
    db_apparel: Optional[Apparel] = await session.get(Apparel, apparel_id)
    if not db_apparel:
        raise HTTPException(
            status_code=404, detail=f"Apparel with id {apparel_id} not found"
        )
    return db_apparel


@router.patch("/apparels/{apparel_id}", response_model=Apparel)
async def update_apparel(
    apparel_id: int,
    apparel_update: ApparelCreate,
    session: AsyncSession = Depends(get_db),
) -> Apparel:
    """Updates existing apparel information.

    Validates the existence of the related Person if their ID is being updated.

    Args:
        apparel_id: The ID of the apparel to update.
        apparel_update: The new data for the apparel.
        session: The database session.

    Raises:
        HTTPException: If the apparel or related Person is not found.

    Returns:
        The updated apparel information.
    """
    db_apparel: Optional[Apparel] = await session.get(Apparel, apparel_id)
    if not db_apparel:
        raise HTTPException(
            status_code=404, detail=f"Apparel with id {apparel_id} not found"
        )

    # Validate person_id if it's being updated
    if apparel_update.person_id is not None and apparel_update.person_id != db_apparel.person_id:
        db_person: Optional[Person] = await session.get(Person, apparel_update.person_id)
        if not db_person:
            raise HTTPException(
                status_code=404,
                detail=f"Person with id {apparel_update.person_id} not found",
            )

    apparel_data = apparel_update.model_dump(exclude_unset=True)
    for key, value in apparel_data.items():
        setattr(db_apparel, key, value)

    session.add(db_apparel)
    await session.commit()
    await session.refresh(db_apparel)
    return db_apparel


@router.delete("/apparels/{apparel_id}", response_model=Apparel)
async def delete_apparel(apparel_id: int, session: AsyncSession = Depends(get_db)) -> Apparel:
    """Deletes apparel information by its ID.

    Args:
        apparel_id: The ID of the apparel to delete.
        session: The database session.

    Raises:
        HTTPException: If the apparel with the given ID is not found.

    Returns:
        The deleted apparel information.
    """
    db_apparel: Optional[Apparel] = await session.get(Apparel, apparel_id)
    if not db_apparel:
        raise HTTPException(
            status_code=404, detail=f"Apparel with id {apparel_id} not found"
        )

    await session.delete(db_apparel)
    await session.commit()
    return db_apparel
