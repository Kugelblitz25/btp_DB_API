CREATE TABLE "person" (
  "id" integer PRIMARY KEY NOT NULL,
  "base64" varchar,
  "height" float NOT NULL,
  "gender_id" integer,
  "glasses" boolean,
  "hairline_id" integer,
  "feature" VECTOR(512),
  "race_id" integer,
  "age_id" integer
);

CREATE TABLE "gender" (
  "id" integer PRIMARY KEY NOT NULL,
  "value" text NOT NULL
);

CREATE TABLE "age" (
  "id" integer PRIMARY KEY NOT NULL,
  "value" text NOT NULL
);

CREATE TABLE "race" (
  "id" integer PRIMARY KEY NOT NULL,
  "value" text NOT NULL
);

CREATE TABLE "hairline" (
  "id" integer PRIMARY KEY NOT NULL,
  "type" varchar NOT NULL
);

CREATE TABLE "apparel" (
  "id" integer PRIMARY KEY NOT NULL,
  "person_id" integer NOT NULL,
  "shirt_colour" varchar(128) NOT NULL,
  "pant_colour" varchar(128) NOT NULL,
  "time" timestamptz NOT NULL
);

CREATE TABLE "event" (
  "id" integer PRIMARY KEY NOT NULL,
  "person_id" integer NOT NULL,
  "area_id" integer,
  "action_id" integer,
  "time" timestamptz NOT NULL
);

CREATE TABLE "area" (
  "id" integer PRIMARY KEY NOT NULL,
  "name" varchar NOT NULL
);

CREATE TABLE "action" (
  "id" integer PRIMARY KEY NOT NULL,
  "type" varchar NOT NULL
);

CREATE TABLE "track" (
  "id" integer PRIMARY KEY NOT NULL,
  "person_id" integer NOT NULL,
  "time" timestamptz NOT NULL,
  "duration" interval NOT NULL,
  "x" float NOT NULL,
  "y" float NOT NULL
);

ALTER TABLE "person" ADD FOREIGN KEY ("gender_id") REFERENCES "gender" ("id");

ALTER TABLE "person" ADD FOREIGN KEY ("hairline_id") REFERENCES "hairline" ("id");

ALTER TABLE "person" ADD FOREIGN KEY ("race_id") REFERENCES "race" ("id");

ALTER TABLE "person" ADD FOREIGN KEY ("age_id") REFERENCES "age" ("id");

ALTER TABLE "apparel" ADD FOREIGN KEY ("person_id") REFERENCES "person" ("id");

ALTER TABLE "event" ADD FOREIGN KEY ("person_id") REFERENCES "person" ("id");

ALTER TABLE "event" ADD FOREIGN KEY ("area_id") REFERENCES "area" ("id");

ALTER TABLE "event" ADD FOREIGN KEY ("action_id") REFERENCES "action" ("id");

ALTER TABLE "track" ADD FOREIGN KEY ("person_id") REFERENCES "person" ("id");
