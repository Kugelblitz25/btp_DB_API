from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import field_validator, model_validator
from sqlmodel import Field, Relationship, SQLModel


class GenderCreate(SQLModel):
    value: str

    model_config = {"from_attributes": True}

    @field_validator("value")
    def value_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Value must not be empty")
        return v


class Gender(GenderCreate, table=True):
    id: int = Field(primary_key=True)

    people: List["Person"] = Relationship(back_populates="gender")


class RaceCreate(SQLModel):
    value: str

    model_config = {"from_attributes": True}

    @field_validator("value")
    def value_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Value must not be empty")
        return v


class Race(RaceCreate, table=True):
    id: int = Field(primary_key=True)

    people: List["Person"] = Relationship(back_populates="race")


class AgeCreate(SQLModel):
    value: str

    model_config = {"from_attributes": True}

    @field_validator("value")
    def value_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Value must not be empty")
        return v


class Age(AgeCreate, table=True):
    id: int = Field(primary_key=True)

    people: List["Person"] = Relationship(back_populates="age")


class HairlineCreate(SQLModel):
    type: str

    model_config = {"from_attributes": True}

    @field_validator("type")
    def type_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Type must not be empty")
        return v


class Hairline(HairlineCreate, table=True):
    id: int = Field(primary_key=True)

    people: List["Person"] = Relationship(back_populates="hairline")


class PersonCreate(SQLModel):
    base64: str
    height: float
    stride_length: float
    gender_id: int
    glasses: bool
    feature: str  # Assuming this is the equivalent of 'feature' USER-DEFINED in SQL
    hairline_id: Optional[int] = None
    race_id: Optional[int] = None
    age_id: Optional[int] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def validate(self):
        if self.height <= 0:
            raise ValueError("Height must be greater than 0")
        if self.stride_length <= 0:
            raise ValueError("Stride length must be greater than 0")
        if not self.base64:
            raise ValueError("Base64 must not be empty")
        if self.gender_id <= 0:
            raise ValueError("Gender ID must be greater than 0")
        if self.hairline_id is not None and self.hairline_id <= 0:
            raise ValueError("Hairline ID must be greater than 0")
        if self.race_id is not None and self.race_id <= 0:
            raise ValueError("Race ID must be greater than 0")
        if self.age_id is not None and self.age_id <= 0:
            raise ValueError("Age ID must be greater than 0")
        return self


class Person(PersonCreate, table=True):
    id: int = Field(primary_key=True)
    gender_id: int = Field(foreign_key="gender.id")
    hairline_id: Optional[int] = Field(default=None, foreign_key="hairline.id")
    race_id: Optional[int] = Field(default=None, foreign_key="race.id")
    age_id: Optional[int] = Field(default=None, foreign_key="age.id")

    gender: "Gender" = Relationship(back_populates="people")
    hairline: Optional[Hairline] = Relationship(back_populates="people")
    race: Optional["Race"] = Relationship(back_populates="people")
    age: Optional["Age"] = Relationship(back_populates="people")
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
    def validate(self):
        if self.person_id <= 0:
            raise ValueError("Person ID must be greater than 0")
        if self.area_id is not None and self.area_id <= 0:
            raise ValueError("Area ID must be greater than 0")
        if self.action_id is not None and self.action_id <= 0:
            raise ValueError("Action ID must be greater than 0")
        if not self.time <= datetime.now():
            raise ValueError("Time must be in the past")
        return self


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
    def validate(self):
        if self.person_id <= 0:
            raise ValueError("Person ID must be greater than 0")
        if not self.shirt_colour:
            raise ValueError("Shirt colour must not be empty")
        if not self.pant_colour:
            raise ValueError("Pant colour must not be empty")
        if not self.shoe_colour:
            raise ValueError("Shoe colour must not be empty")
        if not self.time <= datetime.now():
            raise ValueError("Time must be in the past")
        return self


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
    def validate(self):
        if self.person_id <= 0:
            raise ValueError("Person ID must be greater than 0")
        if not self.time <= datetime.now():
            raise ValueError("Time must be in the past")
        if self.duration <= timedelta(0):
            raise ValueError("Duration must be greater than 0")
        return self


class Track(TrackCreate, table=True):
    id: int = Field(primary_key=True)
    person_id: int = Field(foreign_key="person.id")

    person: Optional[Person] = Relationship(back_populates="tracks")