"""Integration tests for the API endpoints."""

import sys # Add for path correction
import os # Add for path correction
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Add project root to path

import sys # Add for path correction
import os # Add for path correction
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Add project root to path

import pytest
from typing import AsyncGenerator, Generator, Any
from datetime import datetime, timedelta # Add this import
import os # Import os to set environment variables

# Use an in-memory SQLite database for testing
DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"
# Set the DATABASE_URL environment variable BEFORE importing main.app or database
os.environ["DATABASE_URL"] = DATABASE_URL_TEST

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport # Changed from httpx to use AsyncClient with ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel, Field

from main import app as actual_app # Import the main application
from database import get_db # Import the original get_db
from models import (
    Gender, GenderCreate,
    Race, RaceCreate,
    Age, AgeCreate,
    Hairline, HairlineCreate,
    Person, PersonCreate,
    Area, AreaCreate,
    Action, ActionCreate,
    Event, EventCreate,
    Apparel, ApparelCreate,
    Track, TrackCreate,
)

# engine_test and SessionLocalTest are now defined after DATABASE_URL_TEST is set and used by database.py
# This means the engine in database.py should be the one using DATABASE_URL_TEST if it was configured to pick it up at import time.
# However, the override_get_db function explicitly creates its own engine_test.
# Let's ensure engine_test for override_get_db uses the consistent DATABASE_URL_TEST.

engine_test = create_async_engine(DATABASE_URL_TEST, echo=True) # This engine is specific to the override
SessionLocalTest = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False) # This sessionmaker too

# Dependency override for tests
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Overrides the database session for tests with an in-memory SQLite database."""
    async with engine_test.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with SessionLocalTest() as session:
        yield session
        # No need to await conn.run_sync(SQLModel.metadata.drop_all) here
        # as the in-memory database is ephemeral. Tables are created per session if needed.


# Apply the override to the actual app
actual_app.dependency_overrides[get_db] = override_get_db

# Pytest fixture for the test client
@pytest.fixture(scope="function") # Changed scope to function for better isolation
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provides an HTTPX AsyncClient for making API requests to the test application."""
    async with AsyncClient(transport=ASGITransport(app=actual_app), base_url="http://test") as ac: # Use ASGITransport
        yield ac
    # Clean up tables after each test function if needed, though in-memory DB usually handles this.
    # async with engine_test.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.drop_all)


# Basic test to ensure the test setup is working
@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the People Tracking API"}

# Placeholder for future API tests
# Will add tests for each CRUD operation for each model

# --- Gender API Tests ---
@pytest.mark.asyncio
async def test_create_gender_valid(client: AsyncClient):
    response = await client.post("/genders/", json={"value": "NonBinary"})
    assert response.status_code == 200 # Assuming 200 for create from existing app
    data = response.json()
    assert data["value"] == "NonBinary"
    assert "id" in data
    # Check if default id is None before being set by DB
    # For Gender model, id is Optional[int] = Field(default=None, primary_key=True...)
    # The DB will assign an ID, so we check it's present.

@pytest.mark.asyncio
async def test_create_gender_invalid_empty_value(client: AsyncClient):
    response = await client.post("/genders/", json={"value": ""})
    assert response.status_code == 422 # Validation error from Pydantic model

@pytest.mark.asyncio
async def test_read_gender_valid(client: AsyncClient):
    # First, create a gender to read
    create_response = await client.post("/genders/", json={"value": "Female"})
    assert create_response.status_code == 200
    created_data = create_response.json()
    gender_id = created_data["id"]

    # Now, read it
    read_response = await client.get(f"/genders/{gender_id}")
    assert read_response.status_code == 200
    read_data = read_response.json()
    assert read_data["value"] == "Female"
    assert read_data["id"] == gender_id

@pytest.mark.asyncio
async def test_read_gender_not_found(client: AsyncClient):
    response = await client.get("/genders/99999") # Assuming 99999 does not exist
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_genders_list(client: AsyncClient):
    # Create a couple of genders
    await client.post("/genders/", json={"value": "GenderX"})
    await client.post("/genders/", json={"value": "GenderY"})

    response = await client.get("/genders/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check if the created genders are in the list (values might vary based on test isolation)
    values_in_response = [item["value"] for item in data]
    assert "GenderX" in values_in_response
    assert "GenderY" in values_in_response

@pytest.mark.asyncio
async def test_update_gender_valid(client: AsyncClient):
    # Create a gender
    create_response = await client.post("/genders/", json={"value": "ToBeUpdated"})
    assert create_response.status_code == 200
    gender_id = create_response.json()["id"]

    # Update it
    update_response = await client.patch(f"/genders/{gender_id}", json={"value": "UpdatedValue"})
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["value"] == "UpdatedValue"
    assert updated_data["id"] == gender_id

@pytest.mark.asyncio
async def test_update_gender_not_found(client: AsyncClient):
    response = await client.patch("/genders/99999", json={"value": "TryingToUpdate"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_gender_invalid_empty_value(client: AsyncClient):
    # Create a gender
    create_response = await client.post("/genders/", json={"value": "ValidBeforeUpdate"})
    assert create_response.status_code == 200
    gender_id = create_response.json()["id"]

    # Attempt to update with invalid data
    response = await client.patch(f"/genders/{gender_id}", json={"value": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_gender_valid(client: AsyncClient):
    # Create a gender
    create_response = await client.post("/genders/", json={"value": "ToBeDeleted"})
    assert create_response.status_code == 200
    gender_id = create_response.json()["id"]

    # Delete it
    delete_response = await client.delete(f"/genders/{gender_id}")
    assert delete_response.status_code == 200
    deleted_data = delete_response.json() # Endpoint returns deleted object
    assert deleted_data["value"] == "ToBeDeleted"

    # Try to read it again, should be not found
    read_response = await client.get(f"/genders/{gender_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_gender_not_found(client: AsyncClient):
    response = await client.delete("/genders/99999")
    assert response.status_code == 404

# --- Race API Tests ---
@pytest.mark.asyncio
async def test_create_race_valid(client: AsyncClient):
    response = await client.post("/races/", json={"value": "Elven"})
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "Elven"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_race_invalid_empty_value(client: AsyncClient):
    response = await client.post("/races/", json={"value": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_read_race_valid(client: AsyncClient):
    create_response = await client.post("/races/", json={"value": "Dwarven"})
    assert create_response.status_code == 200
    race_id = create_response.json()["id"]

    read_response = await client.get(f"/races/{race_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["value"] == "Dwarven"
    assert data["id"] == race_id

@pytest.mark.asyncio
async def test_read_race_not_found(client: AsyncClient):
    response = await client.get("/races/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_races_list(client: AsyncClient):
    await client.post("/races/", json={"value": "RaceA"})
    await client.post("/races/", json={"value": "RaceB"})

    response = await client.get("/races/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    values_in_response = [item["value"] for item in data]
    assert "RaceA" in values_in_response
    assert "RaceB" in values_in_response

@pytest.mark.asyncio
async def test_update_race_valid(client: AsyncClient):
    create_response = await client.post("/races/", json={"value": "OrcishOld"})
    assert create_response.status_code == 200
    race_id = create_response.json()["id"]

    update_response = await client.patch(f"/races/{race_id}", json={"value": "OrcishNew"})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["value"] == "OrcishNew"
    assert data["id"] == race_id

@pytest.mark.asyncio
async def test_update_race_not_found(client: AsyncClient):
    response = await client.patch("/races/99999", json={"value": "UnknownRace"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_race_invalid_empty_value(client: AsyncClient):
    create_response = await client.post("/races/", json={"value": "ValidRaceUpdate"})
    assert create_response.status_code == 200
    race_id = create_response.json()["id"]

    response = await client.patch(f"/races/{race_id}", json={"value": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_race_valid(client: AsyncClient):
    create_response = await client.post("/races/", json={"value": "Gnome"})
    assert create_response.status_code == 200
    race_id = create_response.json()["id"]

    delete_response = await client.delete(f"/races/{race_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["value"] == "Gnome"

    read_response = await client.get(f"/races/{race_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_race_not_found(client: AsyncClient):
    response = await client.delete("/races/99999")
    assert response.status_code == 404

# --- Age API Tests ---
@pytest.mark.asyncio
async def test_create_age_valid(client: AsyncClient):
    response = await client.post("/ages/", json={"value": "Child"})
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "Child"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_age_invalid_empty_value(client: AsyncClient):
    response = await client.post("/ages/", json={"value": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_read_age_valid(client: AsyncClient):
    create_response = await client.post("/ages/", json={"value": "Adult"})
    assert create_response.status_code == 200
    age_id = create_response.json()["id"]

    read_response = await client.get(f"/ages/{age_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["value"] == "Adult"
    assert data["id"] == age_id

@pytest.mark.asyncio
async def test_read_age_not_found(client: AsyncClient):
    response = await client.get("/ages/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_ages_list(client: AsyncClient):
    await client.post("/ages/", json={"value": "AgeCategory1"})
    await client.post("/ages/", json={"value": "AgeCategory2"})

    response = await client.get("/ages/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    values_in_response = [item["value"] for item in data]
    assert "AgeCategory1" in values_in_response
    assert "AgeCategory2" in values_in_response

@pytest.mark.asyncio
async def test_update_age_valid(client: AsyncClient):
    create_response = await client.post("/ages/", json={"value": "SeniorCitizenInitial"})
    assert create_response.status_code == 200
    age_id = create_response.json()["id"]

    update_response = await client.patch(f"/ages/{age_id}", json={"value": "SeniorCitizenUpdated"})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["value"] == "SeniorCitizenUpdated"
    assert data["id"] == age_id

@pytest.mark.asyncio
async def test_update_age_not_found(client: AsyncClient):
    response = await client.patch("/ages/99999", json={"value": "UnknownAgeCat"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_age_invalid_empty_value(client: AsyncClient):
    create_response = await client.post("/ages/", json={"value": "ValidAgeCat"})
    assert create_response.status_code == 200
    age_id = create_response.json()["id"]

    response = await client.patch(f"/ages/{age_id}", json={"value": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_age_valid(client: AsyncClient):
    create_response = await client.post("/ages/", json={"value": "Teenager"})
    assert create_response.status_code == 200
    age_id = create_response.json()["id"]

    delete_response = await client.delete(f"/ages/{age_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["value"] == "Teenager"

    read_response = await client.get(f"/ages/{age_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_age_not_found(client: AsyncClient):
    response = await client.delete("/ages/99999")
    assert response.status_code == 404

# --- Hairline API Tests ---
@pytest.mark.asyncio
async def test_create_hairline_valid(client: AsyncClient):
    response = await client.post("/hairlines/", json={"type": "Straight"})
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "Straight"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_hairline_invalid_empty_type(client: AsyncClient):
    response = await client.post("/hairlines/", json={"type": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_read_hairline_valid(client: AsyncClient):
    create_response = await client.post("/hairlines/", json={"type": "Widow's Peak"})
    assert create_response.status_code == 200
    hairline_id = create_response.json()["id"]

    read_response = await client.get(f"/hairlines/{hairline_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["type"] == "Widow's Peak"
    assert data["id"] == hairline_id

@pytest.mark.asyncio
async def test_read_hairline_not_found(client: AsyncClient):
    response = await client.get("/hairlines/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_hairlines_list(client: AsyncClient):
    await client.post("/hairlines/", json={"type": "HairlineTypeX"})
    await client.post("/hairlines/", json={"type": "HairlineTypeY"})

    response = await client.get("/hairlines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    types_in_response = [item["type"] for item in data]
    assert "HairlineTypeX" in types_in_response
    assert "HairlineTypeY" in types_in_response

@pytest.mark.asyncio
async def test_update_hairline_valid(client: AsyncClient):
    create_response = await client.post("/hairlines/", json={"type": "RecedingInitial"})
    assert create_response.status_code == 200
    hairline_id = create_response.json()["id"]

    update_response = await client.patch(f"/hairlines/{hairline_id}", json={"type": "RecedingUpdated"})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["type"] == "RecedingUpdated"
    assert data["id"] == hairline_id

@pytest.mark.asyncio
async def test_update_hairline_not_found(client: AsyncClient):
    response = await client.patch("/hairlines/99999", json={"type": "UnknownHairline"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_hairline_invalid_empty_type(client: AsyncClient):
    create_response = await client.post("/hairlines/", json={"type": "ValidHairlineType"})
    assert create_response.status_code == 200
    hairline_id = create_response.json()["id"]

    response = await client.patch(f"/hairlines/{hairline_id}", json={"type": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_hairline_valid(client: AsyncClient):
    create_response = await client.post("/hairlines/", json={"type": "Bald"})
    assert create_response.status_code == 200
    hairline_id = create_response.json()["id"]

    delete_response = await client.delete(f"/hairlines/{hairline_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["type"] == "Bald"

    read_response = await client.get(f"/hairlines/{hairline_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_hairline_not_found(client: AsyncClient):
    response = await client.delete("/hairlines/99999")
    assert response.status_code == 404

# --- Area API Tests (from routers/event.py) ---
@pytest.mark.asyncio
async def test_create_area_valid(client: AsyncClient):
    response = await client.post("/areas/", json={"name": "Main Hall"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Main Hall"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_area_invalid_empty_name(client: AsyncClient):
    response = await client.post("/areas/", json={"name": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_read_area_valid(client: AsyncClient):
    create_response = await client.post("/areas/", json={"name": "Section Alpha"})
    assert create_response.status_code == 200
    area_id = create_response.json()["id"]

    read_response = await client.get(f"/areas/{area_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["name"] == "Section Alpha"
    assert data["id"] == area_id

@pytest.mark.asyncio
async def test_read_area_not_found(client: AsyncClient):
    response = await client.get("/areas/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_areas_list(client: AsyncClient):
    await client.post("/areas/", json={"name": "Area One"})
    await client.post("/areas/", json={"name": "Area Two"})

    response = await client.get("/areas/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names_in_response = [item["name"] for item in data]
    assert "Area One" in names_in_response
    assert "Area Two" in names_in_response

@pytest.mark.asyncio
async def test_update_area_valid(client: AsyncClient):
    create_response = await client.post("/areas/", json={"name": "Old Name"})
    assert create_response.status_code == 200
    area_id = create_response.json()["id"]

    update_response = await client.patch(f"/areas/{area_id}", json={"name": "New Name"})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "New Name"
    assert data["id"] == area_id

@pytest.mark.asyncio
async def test_update_area_not_found(client: AsyncClient):
    response = await client.patch("/areas/99999", json={"name": "NonExistentArea"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_area_invalid_empty_name(client: AsyncClient):
    create_response = await client.post("/areas/", json={"name": "ValidAreaName"})
    assert create_response.status_code == 200
    area_id = create_response.json()["id"]

    response = await client.patch(f"/areas/{area_id}", json={"name": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_area_valid(client: AsyncClient):
    create_response = await client.post("/areas/", json={"name": "To Be Erased"})
    assert create_response.status_code == 200
    area_id = create_response.json()["id"]

    delete_response = await client.delete(f"/areas/{area_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["name"] == "To Be Erased"

    read_response = await client.get(f"/areas/{area_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_area_not_found(client: AsyncClient):
    response = await client.delete("/areas/99999")
    assert response.status_code == 404

# --- Action API Tests (from routers/event.py) ---
@pytest.mark.asyncio
async def test_create_action_valid(client: AsyncClient):
    response = await client.post("/actions/", json={"type": "Login"})
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "Login"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_action_invalid_empty_type(client: AsyncClient):
    response = await client.post("/actions/", json={"type": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_read_action_valid(client: AsyncClient):
    create_response = await client.post("/actions/", json={"type": "Logout"})
    assert create_response.status_code == 200
    action_id = create_response.json()["id"]

    read_response = await client.get(f"/actions/{action_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["type"] == "Logout"
    assert data["id"] == action_id

@pytest.mark.asyncio
async def test_read_action_not_found(client: AsyncClient):
    response = await client.get("/actions/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_actions_list(client: AsyncClient):
    await client.post("/actions/", json={"type": "ActionX"})
    await client.post("/actions/", json={"type": "ActionY"})

    response = await client.get("/actions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    types_in_response = [item["type"] for item in data]
    assert "ActionX" in types_in_response
    assert "ActionY" in types_in_response

@pytest.mark.asyncio
async def test_update_action_valid(client: AsyncClient):
    create_response = await client.post("/actions/", json={"type": "PurchaseOld"})
    assert create_response.status_code == 200
    action_id = create_response.json()["id"]

    update_response = await client.patch(f"/actions/{action_id}", json={"type": "PurchaseNew"})
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["type"] == "PurchaseNew"
    assert data["id"] == action_id

@pytest.mark.asyncio
async def test_update_action_not_found(client: AsyncClient):
    response = await client.patch("/actions/99999", json={"type": "UnknownAction"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_action_invalid_empty_type(client: AsyncClient):
    create_response = await client.post("/actions/", json={"type": "ValidActionType"})
    assert create_response.status_code == 200
    action_id = create_response.json()["id"]

    response = await client.patch(f"/actions/{action_id}", json={"type": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_delete_action_valid(client: AsyncClient):
    create_response = await client.post("/actions/", json={"type": "ViewPage"})
    assert create_response.status_code == 200
    action_id = create_response.json()["id"]

    delete_response = await client.delete(f"/actions/{action_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["type"] == "ViewPage"

    read_response = await client.get(f"/actions/{action_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_action_not_found(client: AsyncClient):
    response = await client.delete("/actions/99999")
    assert response.status_code == 404

# --- Person API Tests (from routers/person.py) ---

@pytest.fixture(scope="function")
async def default_gender(client: AsyncClient) -> Gender:
    """Fixture to create a default Gender for Person tests."""
    response = await client.post("/genders/", json={"value": "DefaultGenderForPersonTest"})
    assert response.status_code == 200
    return Gender(**response.json())

@pytest.fixture(scope="function")
async def default_race(client: AsyncClient) -> Race:
    """Fixture to create a default Race for Person tests."""
    response = await client.post("/races/", json={"value": "DefaultRaceForPersonTest"})
    assert response.status_code == 200
    return Race(**response.json())

@pytest.fixture(scope="function")
async def default_age_cat(client: AsyncClient) -> Age: # Renamed to avoid conflict with Age model
    """Fixture to create a default Age category for Person tests."""
    response = await client.post("/ages/", json={"value": "DefaultAgeCatForPersonTest"})
    assert response.status_code == 200
    return Age(**response.json())

@pytest.fixture(scope="function")
async def default_hairline(client: AsyncClient) -> Hairline:
    """Fixture to create a default Hairline for Person tests."""
    response = await client.post("/hairlines/", json={"type": "DefaultHairlineForPersonTest"})
    assert response.status_code == 200
    return Hairline(**response.json())


@pytest.mark.asyncio
async def test_create_person_valid(
    client: AsyncClient, 
    default_gender: Gender, 
    default_race: Race, 
    default_age_cat: Age, 
    default_hairline: Hairline
):
    person_data = {
        "base64": "testimage",
        "height": 1.80,
        "glasses": False,
        "feature": "testfeature",
        "gender_id": default_gender.id,
        "hairline_id": default_hairline.id,
        "race_id": default_race.id,
        "age_id": default_age_cat.id,
    }
    response = await client.post("/persons/", json=person_data)
    assert response.status_code == 200
    data = response.json()
    assert data["height"] == 1.80
    assert data["gender_id"] == default_gender.id
    assert "id" in data

@pytest.mark.asyncio
async def test_create_person_valid_minimal(client: AsyncClient, default_gender: Gender):
    # PersonCreate has defaults for many fields, including gender_id=3 (if it exists)
    # For a truly minimal test, we might need to ensure gender_id=3 exists or allow null
    # The model currently defaults gender_id to 3. Let's assume it exists or test with a known one.
    person_data = {
        "height": 0.5, # Valid height
        "gender_id": default_gender.id # Using a known existing gender
    }
    response = await client.post("/persons/", json=person_data)
    assert response.status_code == 200
    data = response.json()
    assert data["height"] == 0.5
    assert data["gender_id"] == default_gender.id

@pytest.mark.asyncio
async def test_create_person_invalid_nonexistent_gender(client: AsyncClient):
    person_data = {"height": 1.70, "gender_id": 9999}
    response = await client.post("/persons/", json=person_data)
    assert response.status_code == 404 # Foreign key validation in endpoint
    assert "Gender with id 9999 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_person_invalid_height_model_validation(client: AsyncClient, default_gender: Gender):
    person_data = {"height": -1.0, "gender_id": default_gender.id} # Invalid height
    response = await client.post("/persons/", json=person_data)
    assert response.status_code == 422 # Pydantic validation error

@pytest.mark.asyncio
async def test_read_person_valid(client: AsyncClient, default_gender: Gender):
    person_data = {"height": 1.65, "gender_id": default_gender.id}
    create_response = await client.post("/persons/", json=person_data)
    assert create_response.status_code == 200
    person_id = create_response.json()["id"]

    read_response = await client.get(f"/persons/{person_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["height"] == 1.65
    assert data["id"] == person_id
    assert data["gender_id"] == default_gender.id # Check FK

@pytest.mark.asyncio
async def test_read_person_not_found(client: AsyncClient):
    response = await client.get("/persons/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_persons_list(client: AsyncClient, default_gender: Gender):
    await client.post("/persons/", json={"height": 1.1, "gender_id": default_gender.id})
    await client.post("/persons/", json={"height": 1.2, "gender_id": default_gender.id})

    response = await client.get("/persons/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # Assuming clean DB per test or function scope fixtures

@pytest.mark.asyncio
async def test_update_person_valid(client: AsyncClient, default_gender: Gender, default_race: Race):
    person_data = {"height": 1.70, "gender_id": default_gender.id}
    create_response = await client.post("/persons/", json=person_data)
    assert create_response.status_code == 200
    person_id = create_response.json()["id"]

    update_payload = {"height": 1.75, "race_id": default_race.id, "glasses": True}
    update_response = await client.patch(f"/persons/{person_id}", json=update_payload)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["height"] == 1.75
    assert data["race_id"] == default_race.id
    assert data["glasses"] is True
    assert data["id"] == person_id

@pytest.mark.asyncio
async def test_update_person_nonexistent_fk(client: AsyncClient, default_gender: Gender):
    person_data = {"height": 1.70, "gender_id": default_gender.id}
    create_response = await client.post("/persons/", json=person_data)
    assert create_response.status_code == 200
    person_id = create_response.json()["id"]

    update_payload = {"race_id": 99887} # Non-existent race
    update_response = await client.patch(f"/persons/{person_id}", json=update_payload)
    assert update_response.status_code == 404
    assert "Race with id 99887 not found" in update_response.json()["detail"]


@pytest.mark.asyncio
async def test_update_person_not_found(client: AsyncClient):
    response = await client.patch("/persons/99999", json={"height": 1.90})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_person_valid(client: AsyncClient, default_gender: Gender):
    person_data = {"height": 1.55, "gender_id": default_gender.id}
    create_response = await client.post("/persons/", json=person_data)
    assert create_response.status_code == 200
    person_id = create_response.json()["id"]

    delete_response = await client.delete(f"/persons/{person_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == person_id

    read_response = await client.get(f"/persons/{person_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_person_not_found(client: AsyncClient):
    response = await client.delete("/persons/99999")
    assert response.status_code == 404

# --- Apparel API Tests (from routers/person.py) ---

@pytest.fixture(scope="function")
async def default_person_for_apparel(client: AsyncClient, default_gender: Gender) -> Person:
    """Fixture to create a default Person for Apparel and other related tests."""
    person_data = {"height": 1.76, "gender_id": default_gender.id}
    response = await client.post("/persons/", json=person_data)
    assert response.status_code == 200
    return Person(**response.json())

@pytest.mark.asyncio
async def test_create_apparel_valid(client: AsyncClient, default_person_for_apparel: Person):
    apparel_data = {
        "person_id": default_person_for_apparel.id,
        "shirt_colour": "Blue",
        "pant_colour": "Black",
        "time": (datetime.now() - timedelta(hours=1)).isoformat(),
    }
    response = await client.post("/apparels/", json=apparel_data)
    assert response.status_code == 200
    data = response.json()
    assert data["shirt_colour"] == "Blue"
    assert data["pant_colour"] == "Black"
    assert data["person_id"] == default_person_for_apparel.id
    assert "id" in data

@pytest.mark.asyncio
async def test_create_apparel_invalid_nonexistent_person(client: AsyncClient):
    apparel_data = {
        "person_id": 98765, # Non-existent person
        "shirt_colour": "Red",
        "pant_colour": "White",
        "time": datetime.now().isoformat(),
    }
    response = await client.post("/apparels/", json=apparel_data)
    assert response.status_code == 404 # FK validation in endpoint
    assert "Person with id 98765 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_apparel_invalid_empty_shirt_colour(client: AsyncClient, default_person_for_apparel: Person):
    apparel_data = {
        "person_id": default_person_for_apparel.id,
        "shirt_colour": "", # Invalid
        "pant_colour": "Black",
        "time": datetime.now().isoformat(),
    }
    response = await client.post("/apparels/", json=apparel_data)
    assert response.status_code == 422 # Pydantic validation

@pytest.mark.asyncio
async def test_create_apparel_invalid_future_time(client: AsyncClient, default_person_for_apparel: Person):
    apparel_data = {
        "person_id": default_person_for_apparel.id,
        "shirt_colour": "Green",
        "pant_colour": "Yellow",
        "time": (datetime.now() + timedelta(days=1)).isoformat(), # Future time
    }
    response = await client.post("/apparels/", json=apparel_data)
    assert response.status_code == 422 # Pydantic validation

@pytest.mark.asyncio
async def test_read_apparel_valid(client: AsyncClient, default_person_for_apparel: Person):
    apparel_data = {
        "person_id": default_person_for_apparel.id,
        "shirt_colour": "Purple",
        "pant_colour": "Gray",
        "time": (datetime.now() - timedelta(minutes=5)).isoformat(),
    }
    create_response = await client.post("/apparels/", json=apparel_data)
    assert create_response.status_code == 200
    apparel_id = create_response.json()["id"]

    read_response = await client.get(f"/apparels/{apparel_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["shirt_colour"] == "Purple"
    assert data["person_id"] == default_person_for_apparel.id
    assert data["id"] == apparel_id

@pytest.mark.asyncio
async def test_read_apparel_not_found(client: AsyncClient):
    response = await client.get("/apparels/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_apparels_list(client: AsyncClient, default_person_for_apparel: Person):
    time_now_iso = datetime.now().isoformat()
    await client.post("/apparels/", json={
        "person_id": default_person_for_apparel.id, "shirt_colour": "Red", "pant_colour": "Blue", "time": time_now_iso
    })
    await client.post("/apparels/", json={
        "person_id": default_person_for_apparel.id, "shirt_colour": "Green", "pant_colour": "Yellow", "time": time_now_iso
    })

    response = await client.get(f"/apparels/?person_id={default_person_for_apparel.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

@pytest.mark.asyncio
async def test_update_apparel_valid(client: AsyncClient, default_person_for_apparel: Person):
    apparel_data = {
        "person_id": default_person_for_apparel.id,
        "shirt_colour": "InitialShirt",
        "pant_colour": "InitialPant",
        "time": (datetime.now() - timedelta(hours=2)).isoformat(),
    }
    create_response = await client.post("/apparels/", json=apparel_data)
    assert create_response.status_code == 200
    created_apparel_json = create_response.json()
    apparel_id = created_apparel_json["id"]

    update_payload = {
        "person_id": default_person_for_apparel.id, # Required
        "shirt_colour": "UpdatedShirt", 
        "pant_colour": "UpdatedPant",
        "time": created_apparel_json["time"] # Required, use original time from created entity
    }
    update_response = await client.patch(f"/apparels/{apparel_id}", json=update_payload)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["shirt_colour"] == "UpdatedShirt"
    assert data["pant_colour"] == "UpdatedPant"
    assert data["id"] == apparel_id

@pytest.mark.asyncio
async def test_update_apparel_not_found(client: AsyncClient, default_person_for_apparel: Person):
    # Payload needs to be valid for ApparelCreate to pass initial validation
    # before the "not found" check, assuming PATCH uses ApparelCreate for validation.
    valid_payload_for_non_existent_item = {
        "person_id": default_person_for_apparel.id, # Needs a valid person_id structure-wise
        "shirt_colour": "GhostShirt",
        "pant_colour": "GhostPant",
        "time": (datetime.now() - timedelta(hours=1)).isoformat()
    }
    response = await client.patch("/apparels/99999", json=valid_payload_for_non_existent_item)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_apparel_valid(client: AsyncClient, default_person_for_apparel: Person):
    apparel_data = {
        "person_id": default_person_for_apparel.id,
        "shirt_colour": "DisposableShirt",
        "pant_colour": "DisposablePant",
        "time": datetime.now().isoformat(),
    }
    create_response = await client.post("/apparels/", json=apparel_data)
    assert create_response.status_code == 200
    apparel_id = create_response.json()["id"]

    delete_response = await client.delete(f"/apparels/{apparel_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == apparel_id

    read_response = await client.get(f"/apparels/{apparel_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_apparel_not_found(client: AsyncClient):
    response = await client.delete("/apparels/99999")
    assert response.status_code == 404

# --- Event API Tests (from routers/event.py) ---

@pytest.fixture(scope="function")
async def default_area_for_event(client: AsyncClient) -> Area:
    """Fixture to create a default Area for Event tests."""
    response = await client.post("/areas/", json={"name": "DefaultAreaForEventTest"})
    assert response.status_code == 200
    return Area(**response.json())

@pytest.fixture(scope="function")
async def default_action_for_event(client: AsyncClient) -> Action:
    """Fixture to create a default Action for Event tests."""
    response = await client.post("/actions/", json={"type": "DefaultActionForEventTest"})
    assert response.status_code == 200
    return Action(**response.json())

# Re-using default_person_for_apparel as default_person_for_event
@pytest.mark.asyncio
async def test_create_event_valid(
    client: AsyncClient, 
    default_person_for_apparel: Person, # Renamed fixture usage for clarity
    default_area_for_event: Area, 
    default_action_for_event: Action
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": (datetime.now() - timedelta(minutes=30)).isoformat(),
    }
    response = await client.post("/events/", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["person_id"] == default_person_for_apparel.id
    assert data["area_id"] == default_area_for_event.id
    assert data["action_id"] == default_action_for_event.id
    assert "id" in data

@pytest.mark.asyncio
async def test_create_event_invalid_nonexistent_person(
    client: AsyncClient, default_area_for_event: Area, default_action_for_event: Action
):
    event_data = {
        "person_id": 99901, # Non-existent
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": datetime.now().isoformat(),
    }
    response = await client.post("/events/", json=event_data)
    assert response.status_code == 404
    assert "Person with id 99901 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_event_invalid_nonexistent_area(
    client: AsyncClient, default_person_for_apparel: Person, default_action_for_event: Action
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": 99902, # Non-existent
        "action_id": default_action_for_event.id,
        "time": datetime.now().isoformat(),
    }
    response = await client.post("/events/", json=event_data)
    assert response.status_code == 404
    assert "Area with id 99902 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_event_invalid_nonexistent_action(
    client: AsyncClient, default_person_for_apparel: Person, default_area_for_event: Area
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": default_area_for_event.id,
        "action_id": 99903, # Non-existent
        "time": datetime.now().isoformat(),
    }
    response = await client.post("/events/", json=event_data)
    assert response.status_code == 404 # As per endpoint logic
    assert "Action with id 99903 not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_event_invalid_future_time(
    client: AsyncClient, default_person_for_apparel: Person, default_area_for_event: Area, default_action_for_event: Action
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": (datetime.now() + timedelta(days=1)).isoformat(), # Future time
    }
    response = await client.post("/events/", json=event_data)
    assert response.status_code == 422 # Pydantic validation

@pytest.mark.asyncio
async def test_read_event_valid(
    client: AsyncClient, default_person_for_apparel: Person, default_area_for_event: Area, default_action_for_event: Action
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": (datetime.now() - timedelta(hours=1)).isoformat(),
    }
    create_response = await client.post("/events/", json=event_data)
    assert create_response.status_code == 200
    event_id = create_response.json()["id"]

    read_response = await client.get(f"/events/{event_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["person_id"] == default_person_for_apparel.id
    assert data["id"] == event_id

@pytest.mark.asyncio
async def test_read_event_not_found(client: AsyncClient):
    response = await client.get("/events/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_events_list_and_filtered(
    client: AsyncClient, 
    default_person_for_apparel: Person, 
    default_area_for_event: Area, 
    default_action_for_event: Action,
    default_gender: Gender # for a second person
):
    # Create a second person for filter testing
    person2_data = {"height": 1.60, "gender_id": default_gender.id}
    person2_response = await client.post("/persons/", json=person2_data)
    assert person2_response.status_code == 200
    person2 = Person(**person2_response.json())

    time_iso = (datetime.now() - timedelta(minutes=10)).isoformat()
    # Event 1 (Person1, Area1, Action1)
    await client.post("/events/", json={
        "person_id": default_person_for_apparel.id, 
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": time_iso
    })
    # Event 2 (Person2, Area1, Action1)
    await client.post("/events/", json={
        "person_id": person2.id, 
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": time_iso
    })

    # Read all (or first page)
    response_all = await client.get("/events/")
    assert response_all.status_code == 200
    all_events = response_all.json()
    assert isinstance(all_events, list)
    assert len(all_events) >= 2

    # Filter by person_id
    response_person1 = await client.get(f"/events/?person_id={default_person_for_apparel.id}")
    assert response_person1.status_code == 200
    person1_events = response_person1.json()
    assert isinstance(person1_events, list)
    assert len(person1_events) >= 1
    for event in person1_events:
        assert event["person_id"] == default_person_for_apparel.id
    
    # Filter by area_id (should include events from both persons in this setup)
    response_area1 = await client.get(f"/events/?area_id={default_area_for_event.id}")
    assert response_area1.status_code == 200
    area1_events = response_area1.json()
    assert len(area1_events) >= 2


@pytest.mark.asyncio
async def test_update_event_valid(
    client: AsyncClient, default_person_for_apparel: Person, default_area_for_event: Area, default_action_for_event: Action
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": (datetime.now() - timedelta(hours=2)).isoformat(),
    }
    create_response = await client.post("/events/", json=event_data)
    assert create_response.status_code == 200
    event_id = create_response.json()["id"]

    # Create a new area to update to
    new_area_response = await client.post("/areas/", json={"name": "NewAreaForEventUpdate"})
    assert new_area_response.status_code == 200
    new_area_id = new_area_response.json()["id"]
    original_event_data = create_response.json()

    update_payload = {
        "person_id": original_event_data["person_id"], # Required by EventCreate
        "area_id": new_area_id, 
        "action_id": original_event_data["action_id"], # Keep original or set if changed (optional in EventCreate)
        "time": (datetime.now() - timedelta(minutes=1)).isoformat() # Required by EventCreate
    }
    update_response = await client.patch(f"/events/{event_id}", json=update_payload)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["area_id"] == new_area_id
    assert data["id"] == event_id

@pytest.mark.asyncio
async def test_update_event_not_found(client: AsyncClient, default_person_for_apparel: Person): # Used person fixture for person_id
    # Payload needs to be valid for EventCreate
    valid_payload_for_non_existent_item = {
        "person_id": default_person_for_apparel.id, 
        "time": (datetime.now() - timedelta(hours=1)).isoformat(),
        # area_id and action_id are optional in EventCreate, so this is minimal valid
    }
    response = await client.patch("/events/99999", json=valid_payload_for_non_existent_item)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_event_invalid_fk(
    client: AsyncClient, default_person_for_apparel: Person, default_area_for_event: Area, default_action_for_event: Action
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": (datetime.now() - timedelta(hours=2)).isoformat(),
    }
    create_response = await client.post("/events/", json=event_data)
    assert create_response.status_code == 200
    event_id = create_response.json()["id"]
    original_event_data = create_response.json()

    # To test the 404 for person_id, other fields must be valid for EventCreate
    update_payload = {
        "person_id": 88887, # Non-existent person
        "area_id": original_event_data["area_id"], # Keep valid from created event
        "action_id": original_event_data["action_id"], # Keep valid from created event
        "time": original_event_data["time"] # Keep valid from created event
    }
    update_response = await client.patch(f"/events/{event_id}", json=update_payload)
    assert update_response.status_code == 404 
    assert "Person with id 88887 not found" in update_response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_event_valid(
    client: AsyncClient, default_person_for_apparel: Person, default_area_for_event: Area, default_action_for_event: Action
):
    event_data = {
        "person_id": default_person_for_apparel.id,
        "area_id": default_area_for_event.id,
        "action_id": default_action_for_event.id,
        "time": datetime.now().isoformat(),
    }
    create_response = await client.post("/events/", json=event_data)
    assert create_response.status_code == 200
    event_id = create_response.json()["id"]

    delete_response = await client.delete(f"/events/{event_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == event_id

    read_response = await client.get(f"/events/{event_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_event_not_found(client: AsyncClient):
    response = await client.delete("/events/99999")
    assert response.status_code == 404

# --- Track API Tests (from routers/event.py) ---

# Re-using default_person_for_apparel as default_person_for_track
@pytest.mark.asyncio
async def test_create_track_valid(client: AsyncClient, default_person_for_apparel: Person): # Reused fixture
    track_data = {
        "person_id": default_person_for_apparel.id,
        "time": (datetime.now() - timedelta(seconds=30)).isoformat(),
        "duration": timedelta(seconds=15).total_seconds(), # Pydantic expects float for timedelta
        "x": 100.5,
        "y": 200.75,
    }
    response = await client.post("/tracks/", json=track_data)
    assert response.status_code == 200
    data = response.json()
    assert data["person_id"] == default_person_for_apparel.id
    assert data["x"] == 100.5
    assert data["y"] == 200.75
    assert data["duration"] == "PT15S" # FastAPI/Pydantic serializes timedelta to ISO string
    assert "id" in data

@pytest.mark.asyncio
async def test_create_track_invalid_nonexistent_person(client: AsyncClient):
    track_data = {
        "person_id": 99911, # Non-existent
        "time": datetime.now().isoformat(),
        "duration": timedelta(seconds=5).total_seconds(),
        "x": 10,
        "y": 20,
    }
    response = await client.post("/tracks/", json=track_data)
    assert response.status_code == 404
    assert "Person with id 99911 not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_create_track_invalid_future_time(client: AsyncClient, default_person_for_apparel: Person):
    track_data = {
        "person_id": default_person_for_apparel.id,
        "time": (datetime.now() + timedelta(days=1)).isoformat(), # Future time
        "duration": timedelta(seconds=5).total_seconds(),
        "x": 10,
        "y": 20,
    }
    response = await client.post("/tracks/", json=track_data)
    assert response.status_code == 422 # Pydantic validation

@pytest.mark.asyncio
async def test_create_track_invalid_zero_duration(client: AsyncClient, default_person_for_apparel: Person):
    track_data = {
        "person_id": default_person_for_apparel.id,
        "time": datetime.now().isoformat(),
        "duration": 0, # Invalid duration
        "x": 10,
        "y": 20,
    }
    response = await client.post("/tracks/", json=track_data)
    assert response.status_code == 422 # Pydantic validation

@pytest.mark.asyncio
async def test_read_track_valid(client: AsyncClient, default_person_for_apparel: Person):
    track_data = {
        "person_id": default_person_for_apparel.id,
        "time": (datetime.now() - timedelta(minutes=1)).isoformat(),
        "duration": timedelta(seconds=10).total_seconds(),
        "x": 1.1,
        "y": 2.2,
    }
    create_response = await client.post("/tracks/", json=track_data)
    assert create_response.status_code == 200
    track_id = create_response.json()["id"]

    read_response = await client.get(f"/tracks/{track_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["person_id"] == default_person_for_apparel.id
    assert data["x"] == 1.1
    assert data["id"] == track_id

@pytest.mark.asyncio
async def test_read_track_not_found(client: AsyncClient):
    response = await client.get("/tracks/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_read_tracks_list_and_filtered_ordered(client: AsyncClient, default_person_for_apparel: Person):
    person_id = default_person_for_apparel.id
    time_now = datetime.now()
    
    # Track 1 (older)
    await client.post("/tracks/", json={
        "person_id": person_id, "time": (time_now - timedelta(minutes=10)).isoformat(), 
        "duration": 5, "x": 1, "y": 1
    })
    # Track 2 (newer)
    track2_response = await client.post("/tracks/", json={
        "person_id": person_id, "time": (time_now - timedelta(minutes=5)).isoformat(), 
        "duration": 5, "x": 2, "y": 2
    })
    assert track2_response.status_code == 200
    track2_id = track2_response.json()["id"]

    # Read tracks for this person (default limit is 1, ordered by time desc)
    response_person = await client.get(f"/tracks/?person_id={person_id}")
    assert response_person.status_code == 200
    person_tracks = response_person.json()
    assert isinstance(person_tracks, list)
    assert len(person_tracks) == 1 # Default limit is 1 in endpoint
    assert person_tracks[0]["id"] == track2_id # Should be the newest track

    # Read with a higher limit
    response_person_limit = await client.get(f"/tracks/?person_id={person_id}&limit=10")
    assert response_person_limit.status_code == 200
    person_tracks_limit = response_person_limit.json()
    assert len(person_tracks_limit) >= 2
    assert person_tracks_limit[0]["id"] == track2_id # Newest first

@pytest.mark.asyncio
async def test_update_track_valid(client: AsyncClient, default_person_for_apparel: Person):
    track_data = {
        "person_id": default_person_for_apparel.id,
        "time": (datetime.now() - timedelta(hours=1)).isoformat(),
        "duration": timedelta(seconds=60).total_seconds(),
        "x": 50.0,
        "y": 50.0,
    }
    create_response = await client.post("/tracks/", json=track_data)
    assert create_response.status_code == 200
    created_track_json = create_response.json()
    track_id = created_track_json["id"]

    update_payload = {
        "person_id": default_person_for_apparel.id, # Required
        "time": created_track_json["time"], # Required, use original time
        "duration": timedelta(seconds=70).total_seconds(),
        "x": 55.5, 
        "y": 65.5,
    }
    update_response = await client.patch(f"/tracks/{track_id}", json=update_payload)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["x"] == 55.5
    assert data["y"] == 65.5
    assert data["duration"] == "PT1M10S" # Expect ISO string for 70 seconds
    assert data["id"] == track_id

@pytest.mark.asyncio
async def test_update_track_not_found(client: AsyncClient, default_person_for_apparel: Person):
    # Payload needs to be valid for TrackCreate
    valid_payload_for_non_existent_item = {
        "person_id": default_person_for_apparel.id,
        "time": (datetime.now() - timedelta(hours=1)).isoformat(),
        "duration": timedelta(seconds=10).total_seconds(),
        "x": 0,
        "y": 0,
    }
    response = await client.patch("/tracks/99999", json=valid_payload_for_non_existent_item)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_track_invalid_fk(client: AsyncClient, default_person_for_apparel: Person):
    track_data = {
        "person_id": default_person_for_apparel.id,
        "time": (datetime.now() - timedelta(hours=1)).isoformat(),
        "duration": 30, "x": 1, "y": 1
    }
    create_response = await client.post("/tracks/", json=track_data)
    assert create_response.status_code == 200
    original_track_data_json = create_response.json()
    track_id = original_track_data_json["id"]

    # To test the 404 for person_id, other fields must be valid for TrackCreate
    # The duration from JSON response is "PT...S", need to convert back for Pydantic if it expects float/int
    # For TrackCreate, duration is timedelta, which Pydantic converts from float (seconds)
    duration_str = original_track_data_json["duration"]
    if duration_str.startswith("PT") and duration_str.endswith("S"):
        duration_in_seconds = float(duration_str.replace("PT","").replace("S",""))
    else: # Fallback if it's already float/int somehow (should not happen with current FastAPI)
        duration_in_seconds = float(duration_str)

    update_payload = {
        "person_id": 88776, # Non-existent person
        "time": original_track_data_json["time"], 
        "duration": duration_in_seconds,
        "x": original_track_data_json["x"],
        "y": original_track_data_json["y"],
    }
    update_response = await client.patch(f"/tracks/{track_id}", json=update_payload)
    assert update_response.status_code == 404
    assert "Person with id 88776 not found" in update_response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_track_valid(client: AsyncClient, default_person_for_apparel: Person):
    track_data = {
        "person_id": default_person_for_apparel.id,
        "time": datetime.now().isoformat(),
        "duration": 10, "x": 12, "y": 34,
    }
    create_response = await client.post("/tracks/", json=track_data)
    assert create_response.status_code == 200
    track_id = create_response.json()["id"]

    delete_response = await client.delete(f"/tracks/{track_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == track_id

    read_response = await client.get(f"/tracks/{track_id}")
    assert read_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_track_not_found(client: AsyncClient):
    response = await client.delete("/tracks/99999")
    assert response.status_code == 404

# --- Pytest-Asyncio Debugging ---
import asyncio # For dummy fixture

@pytest.fixture
async def dummy_async_gen_fixture() -> AsyncGenerator[int, None]:
    # print("DUMMY FIXTURE SETUP") # Comment out prints for cleaner test output unless debugging this specifically
    await asyncio.sleep(0.01)
    yield 42
    # print("DUMMY FIXTURE TEARDOWN")

@pytest.mark.asyncio
async def test_with_dummy_fixture(dummy_async_gen_fixture: int):
    # print(f"Fixture value: {dummy_async_gen_fixture}")
    assert dummy_async_gen_fixture == 42
# - test_create_<model>_invalid (for each validation if applicable)
# - test_read_<model>_valid
# - test_read_<model>_not_found
# - test_read_<model>s_list (with pagination/filters if applicable)
# - test_update_<model>_valid
# - test_update_<model>_not_found
# - test_update_<model>_invalid (for each validation)
# - test_delete_<model>_valid
# - test_delete_<model>_not_found
