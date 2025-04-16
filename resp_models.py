from sqlmodel import SQLModel
from pydantic import field_validator, model_validator
from typing import Optional
from datetime import datetime, timedelta


class Hairline(SQLModel):
    type: str

    model_config = {
        "from_attributes": True
    }


class Apparel(SQLModel):
    person_id: int
    shirt_colour: str
    pant_colour: str
    shoe_colour: str
    time: datetime

    model_config = {
        "from_attributes": True
    }

    @field_validator("person_id")
    def person_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Person ID must be greater than 0")
        return v


class Event(SQLModel):
    person_id: int
    area_id: Optional[int]
    action_id: Optional[int]
    time: datetime

    model_config = {
        "from_attributes": True
    }

    @field_validator("person_id")
    def person_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Person ID must be greater than 0")
        return v

    @field_validator("area_id")
    def area_id_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Area ID must be greater than 0")
        return v

    @field_validator("action_id")
    def action_id_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Action ID must be greater than 0")
        return v

    @field_validator("time")
    def time_must_be_in_past(cls, v):
        if v > datetime.now():
            raise ValueError("Time must be in the past")
        return v
    
    @model_validator(mode="after")
    def validate_event(cls, values):
        if values.get("area_id") is None and values.get("action_id") is None:
            raise ValueError("Either area_id or action_id must be provided")
        return values


class Track(SQLModel):
    person_id: int
    time: datetime
    duration: timedelta
    x: float
    y: float
    velocity: float

    model_config = {
        "from_attributes": True
    }

    @field_validator("person_id")
    def person_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Person ID must be greater than 0")
        return v

    @field_validator("time")
    def time_must_be_in_past(cls, v):
        if v > datetime.now():
            raise ValueError("Time must be in the past")
        return v

    @field_validator("duration")
    def duration_must_be_positive(cls, v):
        if v <= timedelta(0):
            raise ValueError("Duration must be greater than 0")
        return v


class Person(SQLModel):
    features: str
    height: float
    stride_length: float
    gender: bool
    age: int
    glasses: bool
    hairline_id: Optional[int]

    model_config = {
        "from_attributes": True
    }

    @field_validator("age")
    def age_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Age must be greater than 0")
        return v

    @field_validator("height")
    def height_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Height must be greater than 0")
        return v

    @field_validator("stride_length")
    def stride_length_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Stride length must be greater than 0")
        return v

    @field_validator("features")
    def features_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Features must not be empty")
        return v

    @field_validator("hairline_id")
    def hairline_id_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Hairline ID must be greater than 0")
        return v


class Area(SQLModel):
    name: str

    model_config = {
        "from_attributes": True
    }


class Action(SQLModel):
    type: str

    model_config = {
        "from_attributes": True
    }
