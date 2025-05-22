"""SQLModel definitions for the People Tracking API.

This module defines the database tables and Pydantic models used for
data validation and serialization. It includes models for:
- Gender
- Race
- Age
- Hairline
- Person (core model for individuals)
- Area (locations for events)
- Event (actions performed by people at locations)
- Apparel (clothing information for people)
- Action (types of actions for events)
- Track (tracking data for people)
"""
from datetime import datetime, timedelta
from typing import List, Optional, Any, Type

from pydantic import field_validator, model_validator
from sqlmodel import Field, Relationship, SQLModel


class GenderCreate(SQLModel):
    """Data model for creating a new gender."""

    value: str = Field(description="The value of the gender (e.g., 'Male', 'Female', 'Other').")

    model_config = {"from_attributes": True}

    @field_validator("value")
    def value_must_not_be_empty(cls: Type["GenderCreate"], v: str) -> str:
        """Validate that the gender value is not empty."""
        if not v:
            raise ValueError("Value must not be empty")
        return v


class Gender(GenderCreate, table=True):  # type: ignore [call-arg]
    """Database model for gender, inheriting from GenderCreate.
    Represents the 'gender' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the gender.")

    people: List["Person"] = Relationship(back_populates="gender")


class RaceCreate(SQLModel):
    """Data model for creating a new race."""

    value: str = Field(description="The value of the race (e.g., 'Asian', 'Black', 'White').")

    model_config = {"from_attributes": True}

    @field_validator("value")
    def value_must_not_be_empty(cls: Type["RaceCreate"], v: str) -> str:
        """Validate that the race value is not empty."""
        if not v:
            raise ValueError("Value must not be empty")
        return v


class Race(RaceCreate, table=True):  # type: ignore [call-arg]
    """Database model for race, inheriting from RaceCreate.
    Represents the 'race' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the race.")

    people: List["Person"] = Relationship(back_populates="race")


class AgeCreate(SQLModel):
    """Data model for creating a new age group or category."""

    value: str = Field(description="The value of the age category (e.g., 'Adult', 'Child', 'Senior').")

    model_config = {"from_attributes": True}

    @field_validator("value")
    def value_must_not_be_empty(cls: Type["AgeCreate"], v: str) -> str:
        """Validate that the age value is not empty."""
        if not v:
            raise ValueError("Value must not be empty")
        return v


class Age(AgeCreate, table=True):  # type: ignore [call-arg]
    """Database model for age, inheriting from AgeCreate.
    Represents the 'age' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the age category.")

    people: List["Person"] = Relationship(back_populates="age")


class HairlineCreate(SQLModel):
    """Data model for creating a new hairline type."""

    type: str = Field(description="The type of hairline (e.g., 'Receding', 'Straight', 'Widow's Peak').")

    model_config = {"from_attributes": True}

    @field_validator("type")
    def type_must_not_be_empty(cls: Type["HairlineCreate"], v: str) -> str:
        """Validate that the hairline type is not empty."""
        if not v:
            raise ValueError("Type must not be empty")
        return v


class Hairline(HairlineCreate, table=True):  # type: ignore [call-arg]
    """Database model for hairline, inheriting from HairlineCreate.
    Represents the 'hairline' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the hairline type.")

    people: List["Person"] = Relationship(back_populates="hairline")


class PersonCreate(SQLModel):
    """Data model for creating a new person.
    Used for request body validation when creating a new person.
    """

    base64: Optional[str] = Field(default=None, description="Base64 encoded image of the person.")
    height: float = Field(default=0.1, description="Height of the person in meters.")
    glasses: Optional[bool] = Field(default=None, description="Indicates if the person wears glasses.")
    feature: Optional[str] = Field(default=None, description="A distinctive feature of the person (e.g., facial recognition vector).")
    gender_id: Optional[int] = Field(default=3, description="Foreign key for the person's gender. Defaults to a predefined value (e.g., 'Unknown' or 'Other').")
    hairline_id: Optional[int] = Field(default=None, description="Foreign key for the person's hairline type.")
    race_id: Optional[int] = Field(default=None, description="Foreign key for the person's race.")
    age_id: Optional[int] = Field(default=None, description="Foreign key for the person's age category.")

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate_person_create(self) -> "PersonCreate":
        """Validate the person creation data."""
        if self.height <= 0:
            raise ValueError("Height must be greater than 0")
        if self.gender_id is not None and self.gender_id <= 0:
            raise ValueError("Gender ID must be a positive integer if provided")
        if self.hairline_id is not None and self.hairline_id <= 0:
            raise ValueError("Hairline ID must be a positive integer if provided")
        if self.race_id is not None and self.race_id <= 0:
            raise ValueError("Race ID must be a positive integer if provided")
        if self.age_id is not None and self.age_id <= 0:
            raise ValueError("Age ID must be a positive integer if provided")
        return self


class Person(PersonCreate, table=True):  # type: ignore [call-arg]
    """Database model for a person, inheriting from PersonCreate.
    Represents the 'person' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the person.")
    gender_id: Optional[int] = Field(default=3, foreign_key="gender.id", description="Foreign key linking to the Gender table.")
    hairline_id: Optional[int] = Field(default=None, foreign_key="hairline.id", description="Foreign key linking to the Hairline table.")
    race_id: Optional[int] = Field(default=None, foreign_key="race.id", description="Foreign key linking to the Race table.")
    age_id: Optional[int] = Field(default=None, foreign_key="age.id", description="Foreign key linking to the Age table.")

    gender: Optional["Gender"] = Relationship(back_populates="people")
    hairline: Optional["Hairline"] = Relationship(back_populates="people")
    race: Optional["Race"] = Relationship(back_populates="people")
    age: Optional["Age"] = Relationship(back_populates="people")
    tracks: List["Track"] = Relationship(back_populates="person")
    events: List["Event"] = Relationship(back_populates="person")
    apparels: List["Apparel"] = Relationship(back_populates="person")


class AreaCreate(SQLModel):
    """Data model for creating a new area."""

    name: str = Field(description="Name of the area (e.g., 'Entrance A', 'Section 5').")

    model_config = {"from_attributes": True}

    @field_validator("name")
    def name_must_not_be_empty(cls: Type["AreaCreate"], v: str) -> str:
        """Validate that the area name is not empty."""
        if not v:
            raise ValueError("Name must not be empty")
        return v


class Area(AreaCreate, table=True):  # type: ignore [call-arg]
    """Database model for an area, inheriting from AreaCreate.
    Represents the 'area' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the area.")

    events: List["Event"] = Relationship(back_populates="area")


class EventCreate(SQLModel):
    """Data model for creating a new event.
    Used for request body validation when creating a new event.
    """

    person_id: int = Field(description="Foreign key for the person involved in the event.")
    area_id: Optional[int] = Field(default=None, description="Foreign key for the area where the event occurred.")
    action_id: Optional[int] = Field(default=None, description="Foreign key for the action performed during the event.")
    time: datetime = Field(description="Timestamp of when the event occurred.")

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate_event_create(self) -> "EventCreate":
        """Validate the event creation data."""
        if self.person_id <= 0:
            raise ValueError("Person ID must be a positive integer")
        if self.area_id is not None and self.area_id <= 0:
            raise ValueError("Area ID must be a positive integer if provided")
        if self.action_id is not None and self.action_id <= 0:
            raise ValueError("Action ID must be a positive integer if provided")
        if self.time > datetime.now():
            raise ValueError("Event time must not be in the future")
        return self


class Event(SQLModel, table=True):  # type: ignore [call-arg]
    """Database model for an event.
    Represents the 'event' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the event.")
    person_id: int = Field(foreign_key="person.id", description="Foreign key linking to the Person table.")
    area_id: Optional[int] = Field(default=None, foreign_key="area.id", description="Foreign key linking to the Area table.")
    action_id: Optional[int] = Field(default=None, foreign_key="action.id", description="Foreign key linking to the Action table.")
    time: datetime = Field(description="Timestamp of the event.")

    person: Optional["Person"] = Relationship(back_populates="events")
    area: Optional["Area"] = Relationship(back_populates="events")
    action: Optional["Action"] = Relationship(back_populates="events")


class ApparelCreate(SQLModel):
    """Data model for creating new apparel information.
    Used for request body validation when creating new apparel data.
    """

    person_id: int = Field(description="Foreign key for the person wearing the apparel.")
    shirt_colour: str = Field(description="Color of the person's shirt.")
    pant_colour: str = Field(description="Color of the person's pants.")
    time: datetime = Field(description="Timestamp when this apparel information was recorded.")

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate_apparel_create(self) -> "ApparelCreate":
        """Validate the apparel creation data."""
        if self.person_id <= 0:
            raise ValueError("Person ID must be a positive integer")
        if not self.shirt_colour:
            raise ValueError("Shirt colour must not be empty")
        if not self.pant_colour:
            raise ValueError("Pant colour must not be empty")
        if self.time > datetime.now():
            raise ValueError("Apparel recording time must not be in the future")
        return self


class Apparel(ApparelCreate, table=True):  # type: ignore [call-arg]
    """Database model for apparel, inheriting from ApparelCreate.
    Represents the 'apparel' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the apparel record.")
    person_id: int = Field(foreign_key="person.id", description="Foreign key linking to the Person table.")

    person: Optional["Person"] = Relationship(back_populates="apparels")


class ActionCreate(SQLModel):
    """Data model for creating a new action type."""

    type: str = Field(description="The type of action (e.g., 'Entry', 'Exit', 'Interaction').")

    model_config = {"from_attributes": True}

    @field_validator("type")
    def type_must_not_be_empty(cls: Type["ActionCreate"], v: str) -> str:
        """Validate that the action type is not empty."""
        if not v:
            raise ValueError("Type must not be empty")
        return v


class Action(ActionCreate, table=True):  # type: ignore [call-arg]
    """Database model for an action, inheriting from ActionCreate.
    Represents the 'action' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the action type.")

    events: List["Event"] = Relationship(back_populates="action")


class TrackCreate(SQLModel):
    """Data model for creating new tracking information.
    Used for request body validation when creating new tracking data.
    """

    person_id: int = Field(description="Foreign key for the person being tracked.")
    time: datetime = Field(description="Timestamp of the tracking data point.")
    duration: timedelta = Field(description="Duration of this tracking segment.")
    x: float = Field(description="X-coordinate of the person's location.")
    y: float = Field(description="Y-coordinate of the person's location.")

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate_track_create(self) -> "TrackCreate":
        """Validate the track creation data."""
        if self.person_id <= 0:
            raise ValueError("Person ID must be a positive integer")
        if self.time > datetime.now():
            raise ValueError("Track time must not be in the future")
        if self.duration <= timedelta(0):
            raise ValueError("Duration must be a positive time interval")
        return self


class Track(TrackCreate, table=True):  # type: ignore [call-arg]
    """Database model for tracking data, inheriting from TrackCreate.
    Represents the 'track' table.
    """

    id: Optional[int] = Field(default=None, primary_key=True, description="Primary key for the track record.")
    person_id: int = Field(foreign_key="person.id", description="Foreign key linking to the Person table.")

    person: Optional["Person"] = Relationship(back_populates="tracks")


# Forward references update for relationships
# Pydantic v2 style: Model.model_rebuild()
# For SQLModel, this is typically handled automatically or by ensuring models are defined
# or imported in the correct order. If issues arise with forward refs,
# explicit updates might be needed here, though SQLModel aims to manage this.
# For now, assuming SQLModel handles it. If specific `update_forward_refs` calls are needed,
# they would be placed after all model definitions.
# e.g., Person.model_rebuild()
#       Event.model_rebuild()
#       ... and so on for all models with forward references.
# SQLModel should handle this via its metaclass, but if not, manual calls would be here.