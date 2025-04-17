from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import field_validator, model_validator
from sqlmodel import Field, Relationship, SQLModel


class HairlineCreate(SQLModel):
    type: str

    model_config = {"from_attributes": True}


class Hairline(HairlineCreate, table=True):
    id: int = Field(primary_key=True)

    people: List["Person"] = Relationship(back_populates="hairline")


class PersonCreate(SQLModel):
    features: str
    height: float
    stride_length: float
    gender: bool
    age: int
    glasses: bool
    hairline_id: Optional[int] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        if values.get("age") <= 0:
            raise ValueError("Age must be greater than 0")
        if values.get("height") <= 0:
            raise ValueError("Height must be greater than 0")
        if values.get("stride_length") <= 0:
            raise ValueError("Stride length must be greater than 0")
        if not values.get("features"):
            raise ValueError("Features must not be empty")
        if values.get("hairline_id") is not None and values["hairline_id"] <= 0:
            raise ValueError("Hairline ID must be greater than 0")
        return values


class Person(PersonCreate, table=True):
    id: int = Field(primary_key=True)
    hairline_id: Optional[int] = Field(default=None, foreign_key="hairline.id")

    hairline: Optional[Hairline] = Relationship(back_populates="people")
    tracks: List["Track"] = Relationship(back_populates="person")
    events: List["Event"] = Relationship(back_populates="person")
    apparels: List["Apparel"] = Relationship(back_populates="person")


class AreaCreate(SQLModel):
    name: str

    model_config = {"from_attributes": True}

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Name must not be empty")
        return v


class Area(AreaCreate, table=True):
    id: int = Field(primary_key=True)

    events: List["Event"] = Relationship(back_populates="area")


class EventCreate(SQLModel):
    person_id: int
    area_id: Optional[int] = None
    action_id: Optional[int] = None
    time: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        if values.get("person_id") <= 0:
            raise ValueError("Person ID must be greater than 0")
        if values.get("area_id") is not None and values["area_id"] <= 0:
            raise ValueError("Area ID must be greater than 0")
        if values.get("action_id") is not None and values["action_id"] <= 0:
            raise ValueError("Action ID must be greater than 0")
        return values


class Event(SQLModel, table=True):
    id: int = Field(primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    area_id: Optional[int] = Field(default=None, foreign_key="area.id")
    action_id: Optional[int] = Field(default=None, foreign_key="action.id")
    time: datetime

    person: Optional[Person] = Relationship(back_populates="events")
    area: Optional[Area] = Relationship(back_populates="events")
    action: Optional["Action"] = Relationship(back_populates="events")


class ApparelCreate(SQLModel):
    person_id: int
    shirt_colour: str
    pant_colour: str
    shoe_colour: str
    time: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        if values.get("person_id") <= 0:
            raise ValueError("Person ID must be greater than 0")
        if not values.get("shirt_colour"):
            raise ValueError("Shirt colour must not be empty")
        if not values.get("pant_colour"):
            raise ValueError("Pant colour must not be empty")
        if not values.get("shoe_colour"):
            raise ValueError("Shoe colour must not be empty")
        return values


class Apparel(ApparelCreate, table=True):
    id: int = Field(primary_key=True)
    person_id: int = Field(foreign_key="person.id")

    person: Optional[Person] = Relationship(back_populates="apparels")


class ActionCreate(SQLModel):
    type: str

    model_config = {"from_attributes": True}

    @field_validator("type")
    def type_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Type must not be empty")
        return v


class Action(ActionCreate, table=True):
    id: int = Field(primary_key=True)

    events: List[Event] = Relationship(back_populates="action")


class TrackCreate(SQLModel):
    person_id: int
    time: datetime
    duration: timedelta
    x: float
    y: float
    velocity: float

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(cls, values):
        if values.get("person_id") <= 0:
            raise ValueError("Person ID must be greater than 0")
        if not values.get("time") > datetime.now():
            raise ValueError("Time must be in the past")
        if values.get("duration") <= timedelta(0):
            raise ValueError("Duration must be greater than 0")
        return values


class Track(TrackCreate, table=True):
    id: int = Field(primary_key=True)
    person_id: int = Field(foreign_key="person.id")

    person: Optional[Person] = Relationship(back_populates="tracks")
