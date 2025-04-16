
CREATE TABLE action (
    id integer NOT NULL PRIMARY KEY,
    type character varying NOT NULL
);
CREATE TABLE apparel (
    id integer NOT NULL PRIMARY KEY,
    person_id integer NOT NULL,
    shirt_colour character varying NOT NULL,
    pant_colour character varying NOT NULL,
    shoe_colour character varying NOT NULL,
    "time" timestamp without time zone NOT NULL
);
CREATE TABLE area (
    id integer NOT NULL PRIMARY KEY,
    name character varying NOT NULL
);
CREATE TABLE event (
    id integer NOT NULL PRIMARY KEY,
    person_id integer NOT NULL,
    area_id integer,
    action_id integer,
    "time" timestamp without time zone NOT NULL
);
CREATE TABLE hairline (
    id integer NOT NULL PRIMARY KEY,
    type character varying NOT NULL
);
CREATE TABLE person (
    id integer NOT NULL PRIMARY KEY,
    features character varying NOT NULL,
    height double precision NOT NULL,
    stride_length double precision NOT NULL,
    gender boolean NOT NULL,
    age integer NOT NULL,
    glasses boolean NOT NULL,
    hairline_id integer
);
CREATE TABLE track (
    id integer NOT NULL PRIMARY KEY,
    person_id integer NOT NULL,
    "time" timestamp without time zone NOT NULL,
    duration interval NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    velocity double precision NOT NULL
);

