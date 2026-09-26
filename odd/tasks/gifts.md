# Feature: gifts

## Objective

Deliver the "Regalame" gift feature end to end: a registered user publishes gift
ideas (name, approximate price, optional photo, description and product link),
each user has a shareable public list, and any registered visitor can claim a gift
("Me lo quedo") with guaranteed exclusivity.

## Problem

The gift domain exists only as uncommitted WIP and is not wired:

- the router is not registered, so every `/gifts` endpoint returns 404
- field names disagree across layers (models vs route vs form vs tests)
- the reservation is a boolean, so it cannot record who claimed a gift
- the `gift` table was created out-of-band by `SQLModel.metadata.create_all`
  and no migration owns it

## Why

`description.md` is the product spec and the gift feature is the reason the
project exists. Nothing else is worth building until it works.

## Scope

In scope: backend gift domain, database migration, CRUD API, atomic claim,
public listing, generated client, frontend wiring.

Out of scope: unrelated template improvements and the inherited `Item` demo.

## Constraints

- Product vocabulary comes from `description.md`: `approximate_price`,
  `product_link`, `photo_url`.
- Exclusivity must be enforced by the database, never by the UI alone.
- PostgreSQL is the only target database.

## Tasks

- [x] T1 Align the Gift domain to the spec vocabulary and replace `is_reserved`
      with `reserved_by_id`
- [x] T2 Add an Alembic migration that owns the `gift` table
- [x] T3 Align the `crud.py` gift functions with the crud tests
- [x] T4 Implement `save_upload_file_to_static` and serve static uploads
- [x] T5 Register the gifts router and complete the CRUD endpoints
- [ ] T6 Add an atomic claim endpoint with a database-level exclusivity guarantee
- [ ] T7 Public per-user gift listing behind a shareable link
- [ ] T8 Regenerate `openapi.json`, the frontend client and the route tree
- [ ] T9 Align `GiftForm.tsx` and add a navigation entry
- [ ] T10 Move the gift e2e spec out of `frontend/temp_tests`

## Authorized scope

T1, T2, T3 only: domain vocabulary, migration and crud alignment.

## Acceptance criteria

- `Gift` exposes `approximate_price`, `product_link`, `photo_url` and
  `reserved_by_id`.
- A migration creates the `gift` table from a clean database and is reversible.
- The crud and model gift tests pass.
- The template test suite is unaffected.

## Checks

- `cd backend && .venv/bin/python -m pytest`
- `cd backend && .venv/bin/alembic upgrade head` against a clean database

## Progress

T1 through T5 are done and verified.

- `Gift` now exposes `approximate_price`, `photo_url`, `product_link` and
  `reserved_by_id`; `is_reserved` and the whole `GiftUpdate.is_reserved` surface
  are gone, so a reservation can no longer be forged through an update.
- Adding a second foreign key to `user` made the join conditions ambiguous, so
  `User.gifts`, `Gift.owner` and `Gift.reserved_by` all declare explicit
  `foreign_keys`.
- `crud.py` now exposes `get_gift_by_id`, `get_gifts_by_owner` and
  `delete_gift(db_gift=)`, matching the crud tests.
- Migration `ff6ca4f001fc` drops the phantom table and owns the schema.
- `save_upload_file_to_static` stores an uploaded image under `static/<folder>`
  with a generated name and only accepts image content types.
- `/static` is mounted and the directory is created at startup, so a fresh
  checkout boots even though an empty directory is not tracked by git.
- The gifts router is registered and exposes list, read, create, update, delete
  and an image upload endpoint. Creation is JSON; the image is uploaded
  separately and referenced through `photo_url`. The routes delegate to `crud`,
  so the tested data layer is the one in production use.

## Evidence

- `cd backend && .venv/bin/python -m pytest` -> 74 passed, 0 failed.
- End-to-end against the running server: login, create, list, read, update, image
  upload, static serving of that image, rejection of a non-image upload, 404 on a
  missing gift, and delete all returned the expected status and payload.
- `alembic upgrade head` applied `1a31ce608336 -> ff6ca4f001fc`; `\d gift` shows
  `approximate_price`, `photo_url`, `product_link`, `reserved_by_id` and both
  foreign keys (owner CASCADE, reserved_by SET NULL).
- Reversibility checked: `alembic downgrade -1` removed the table,
  `alembic upgrade head` recreated it.
- `configure_mappers()` succeeds with the two foreign keys to `user`.
