"""Unit tests for the data models in models.py"""

import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta

from models import (
    GenderCreate,
    RaceCreate,
    AgeCreate,
    HairlineCreate,
    PersonCreate,
    AreaCreate,
    EventCreate,
    ApparelCreate,
    ActionCreate,
    TrackCreate,
)

# Test GenderCreate
def test_gender_create_valid():
    gender = GenderCreate(value="Male")
    assert gender.value == "Male"

def test_gender_create_empty_value():
    with pytest.raises(ValidationError):
        GenderCreate(value="")

# Test RaceCreate
def test_race_create_valid():
    race = RaceCreate(value="Asian")
    assert race.value == "Asian"

def test_race_create_empty_value():
    with pytest.raises(ValidationError):
        RaceCreate(value="")

# Test AgeCreate
def test_age_create_valid():
    age = AgeCreate(value="Adult")
    assert age.value == "Adult"

def test_age_create_empty_value():
    with pytest.raises(ValidationError):
        AgeCreate(value="")

# Test HairlineCreate
def test_hairline_create_valid():
    hairline = HairlineCreate(type="Receding")
    assert hairline.type == "Receding"

def test_hairline_create_empty_type():
    with pytest.raises(ValidationError):
        HairlineCreate(type="")

# Test PersonCreate
def test_person_create_valid():
    person_data = {
        "base64": "some_base64_string",
        "height": 1.75,
        "glasses": True,
        "feature": "some_feature_vector",
        "gender_id": 1,
        "hairline_id": 1,
        "race_id": 1,
        "age_id": 1,
    }
    person = PersonCreate(**person_data)
    assert person.height == 1.75
    assert person.gender_id == 1

def test_person_create_invalid_height():
    with pytest.raises(ValidationError) as excinfo:
        PersonCreate(height=-1.0)
    assert "Height must be greater than 0" in str(excinfo.value)

def test_person_create_invalid_gender_id():
    with pytest.raises(ValidationError) as excinfo:
        PersonCreate(height=1.7, gender_id=0)
    assert "Gender ID must be a positive integer if provided" in str(excinfo.value)

def test_person_create_invalid_hairline_id():
    with pytest.raises(ValidationError) as excinfo:
        PersonCreate(height=1.7, hairline_id=0)
    assert "Hairline ID must be a positive integer if provided" in str(excinfo.value)

def test_person_create_invalid_race_id():
    with pytest.raises(ValidationError) as excinfo:
        PersonCreate(height=1.7, race_id=0)
    assert "Race ID must be a positive integer if provided" in str(excinfo.value)

def test_person_create_invalid_age_id():
    with pytest.raises(ValidationError) as excinfo:
        PersonCreate(height=1.7, age_id=0)
    assert "Age ID must be a positive integer if provided" in str(excinfo.value)


# Test AreaCreate
def test_area_create_valid():
    area = AreaCreate(name="Entrance A")
    assert area.name == "Entrance A"

def test_area_create_empty_name():
    with pytest.raises(ValidationError):
        AreaCreate(name="")

# Test EventCreate
def test_event_create_valid():
    event_data = {
        "person_id": 1,
        "area_id": 1,
        "action_id": 1,
        "time": datetime.now() - timedelta(hours=1),
    }
    event = EventCreate(**event_data)
    assert event.person_id == 1

def test_event_create_invalid_person_id():
    with pytest.raises(ValidationError) as excinfo:
        EventCreate(person_id=0, time=datetime.now())
    assert "Person ID must be a positive integer" in str(excinfo.value)

def test_event_create_invalid_area_id():
    with pytest.raises(ValidationError) as excinfo:
        EventCreate(person_id=1, area_id=0, time=datetime.now())
    assert "Area ID must be a positive integer if provided" in str(excinfo.value)

def test_event_create_invalid_action_id():
    with pytest.raises(ValidationError) as excinfo:
        EventCreate(person_id=1, action_id=0, time=datetime.now())
    assert "Action ID must be a positive integer if provided" in str(excinfo.value)

def test_event_create_future_time():
    with pytest.raises(ValidationError) as excinfo:
        EventCreate(person_id=1, time=datetime.now() + timedelta(days=1))
    assert "Event time must not be in the future" in str(excinfo.value)


# Test ApparelCreate
def test_apparel_create_valid():
    apparel_data = {
        "person_id": 1,
        "shirt_colour": "Blue",
        "pant_colour": "Black",
        "time": datetime.now() - timedelta(minutes=30),
    }
    apparel = ApparelCreate(**apparel_data)
    assert apparel.shirt_colour == "Blue"

def test_apparel_create_invalid_person_id():
    with pytest.raises(ValidationError) as excinfo:
        ApparelCreate(person_id=0, shirt_colour="Red", pant_colour="Green", time=datetime.now())
    assert "Person ID must be a positive integer" in str(excinfo.value)

def test_apparel_create_empty_shirt_colour():
    with pytest.raises(ValidationError) as excinfo:
        ApparelCreate(person_id=1, shirt_colour="", pant_colour="Green", time=datetime.now())
    assert "Shirt colour must not be empty" in str(excinfo.value)

def test_apparel_create_empty_pant_colour():
    with pytest.raises(ValidationError) as excinfo:
        ApparelCreate(person_id=1, shirt_colour="Red", pant_colour="", time=datetime.now())
    assert "Pant colour must not be empty" in str(excinfo.value)

def test_apparel_create_future_time():
    with pytest.raises(ValidationError) as excinfo:
        ApparelCreate(
            person_id=1,
            shirt_colour="Red",
            pant_colour="Green",
            time=datetime.now() + timedelta(days=1),
        )
    assert "Apparel recording time must not be in the future" in str(excinfo.value)

# Test ActionCreate
def test_action_create_valid():
    action = ActionCreate(type="Entry")
    assert action.type == "Entry"

def test_action_create_empty_type():
    with pytest.raises(ValidationError):
        ActionCreate(type="")

# Test TrackCreate
def test_track_create_valid():
    track_data = {
        "person_id": 1,
        "time": datetime.now() - timedelta(seconds=10),
        "duration": timedelta(seconds=5),
        "x": 10.0,
        "y": 20.5,
    }
    track = TrackCreate(**track_data)
    assert track.x == 10.0

def test_track_create_invalid_person_id():
    with pytest.raises(ValidationError) as excinfo:
        TrackCreate(person_id=0, time=datetime.now(), duration=timedelta(seconds=1), x=0, y=0)
    assert "Person ID must be a positive integer" in str(excinfo.value)

def test_track_create_future_time():
    with pytest.raises(ValidationError) as excinfo:
        TrackCreate(person_id=1, time=datetime.now() + timedelta(days=1), duration=timedelta(seconds=1), x=0, y=0)
    assert "Track time must not be in the future" in str(excinfo.value)

def test_track_create_non_positive_duration():
    with pytest.raises(ValidationError) as excinfo:
        TrackCreate(person_id=1, time=datetime.now(), duration=timedelta(seconds=0), x=0, y=0)
    assert "Duration must be a positive time interval" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        TrackCreate(person_id=1, time=datetime.now(), duration=timedelta(seconds=-1), x=0, y=0)
    assert "Duration must be a positive time interval" in str(excinfo.value)

# Example of how to run these tests:
# Ensure pytest is installed: pip install pytest
# Navigate to the root directory of the project in the terminal
# Run: pytest
