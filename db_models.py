from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timedelta


class Hairline(SQLModel, table=True):
    id: int = Field(primary_key=True)
    type: str

    people: List["Person"] = Relationship(back_populates="hairline")


class Person(SQLModel, table=True):
    id: int = Field(primary_key=True)
    features: str
    height: float
    stride_length: float
    gender: bool
    age: int
    glasses: bool
    hairline_id: Optional[int] = Field(default=None, foreign_key="hairline.id")

    hairline: Optional[Hairline] = Relationship(back_populates="people")
    tracks: List["Track"] = Relationship(back_populates="person")
    events: List["Event"] = Relationship(back_populates="person")
    apparels: List["Apparel"] = Relationship(back_populates="person")


class Area(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    events: List["Event"] = Relationship(back_populates="area")


class Event(SQLModel, table=True):
    id: int = Field(primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    area_id: Optional[int] = Field(default=None, foreign_key="area.id")
    action_id: Optional[int] = Field(default=None, foreign_key="action.id")
    time: datetime

    person: Optional[Person] = Relationship(back_populates="events")
    area: Optional[Area] = Relationship(back_populates="events")
    action: Optional["Action"] = Relationship(back_populates="events")

class Apparel(SQLModel, table=True):
    id: int = Field(primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    shirt_colour: str
    pant_colour: str
    shoe_colour: str
    time: datetime

    person: Optional[Person] = Relationship(back_populates="apparels")


class Action(SQLModel, table=True):
    id: int = Field(primary_key=True)
    type: str

    events: List[Event] = Relationship(back_populates="action")

class Track(SQLModel, table=True):
    id: int = Field(primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    time: datetime
    duration: timedelta
    x: float
    y: float
    velocity: float

    person: Optional[Person] = Relationship(back_populates="tracks")