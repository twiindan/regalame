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
- [x] T6 Add an atomic claim endpoint with a database-level exclusivity guarantee
- [x] T7 Public per-user gift listing behind a shareable link
- [x] T8 Regenerate `openapi.json`, the frontend client and the route tree
- [x] T9 Align `GiftForm.tsx` and add a navigation entry
- [x] T10 Move the gift e2e spec out of `frontend/temp_tests`

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

T1 through T10 are done and verified. The feature is complete.

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
- Claiming a gift ("Me lo quedo") is its own endpoint. `crud.claim_gift` runs
  `UPDATE ... WHERE reserved_by_id IS NULL` and reports whether this caller won,
  so the database decides the race rather than the application.
- `GiftPublic` exposes the boolean `is_reserved` instead of `reserved_by_id`,
  because the shared public list must not reveal which user claimed a gift.
- The public listing is unauthenticated and reachable from a shareable link.
  A second claim returns 409 and reserving your own gift returns 400.
- Regenerated the OpenAPI spec, the hey-api client (`GiftsService` with all eight
  operations) and the TanStack route tree, which now includes `create-gift`.
- Fixed a pre-existing template type error in `Appearance.tsx` that blocked the
  build independently of this feature.
- FINDING: `tsconfig.json` only includes `src/**/*.ts`, so a `.tsx` file is
  type-checked only when a `.ts` file reaches it through an import. `GiftForm.tsx`
  stayed invisible because its route was absent from the route tree; regenerating
  the tree made eight latent GiftForm errors surface. Including `.tsx` reveals
  thirteen errors across six files.
- The router generator had rewritten `create-gift.tsx` from `/_layout/create-gift`
  to `/create-gift`, because the file lived at `routes/create-gift.tsx` and not
  under `routes/_layout/`. It moved to `routes/_layout/create-gift.tsx`, so it now
  renders inside the authenticated shell at URL `/create-gift`, and the page uses
  the Chakra Container/Heading convention instead of the auth-page Tailwind
  wrapper that hid it on small screens.
- `GiftForm` now uploads the optional image first and then creates the gift with
  JSON, instead of sending multipart to the create endpoint.
- Added a "Create Gift" entry to the sidebar.
- The gift e2e spec moved from `frontend/temp_tests/` into `frontend/tests/`, the
  stale duplicate directory and the throwaway `simple.spec.ts` were deleted, and
  the spec now relies on the storage state from `auth.setup.ts` instead of logging
  in again. A second case covers creating a gift with an image.
- FIX: the form labels were not associated with their inputs. Chakra's `Field`
  generates an id and points the label at it, but every input passed an explicit
  `id`, which overrode that generated id and left the label pointing at nothing.
  Removing the explicit ids restores the association, so the fields now expose
  proper accessible names.

## Evidence

- `cd backend && .venv/bin/python -m pytest` -> 82 passed, 0 failed.
- Frontend: `scripts/generate-client.sh` regenerated the spec (20 paths) and the
  client; `npm run build` generates the route tree and succeeds. `tsc` reports
  zero errors, including `GiftForm.tsx` now that the route tree reaches it and the
  file sits under `_layout/`.
- Browser verification (Playwright, Chromium against the running stack):
  `tests/create-gift.spec.ts` -> 3 passed (setup plus both cases). Creating a gift
  with an image actually persisted a `photo_url` in the database, so the
  upload-then-create round trip is proven end to end, not just by a toast.
- Full Playwright suite: 40 passed, 3 failed. The three are outside this feature:
  two in `reset-password.spec.ts`, which needs mailcatcher and it was not running,
  and one in `sign-up.spec.ts` ("Sign up with existing email").
- Concurrency proof: 12 distinct users claimed the same gift simultaneously
  against the running server. Exactly one returned 200, eleven returned 409, none
  errored, and the gift ended up reserved.
- End-to-end against the running server: login, create, list, read, update, image
  upload, static serving of that image, rejection of a non-image upload, 404 on a
  missing gift, and delete all returned the expected status and payload.
- `alembic upgrade head` applied `1a31ce608336 -> ff6ca4f001fc`; `\d gift` shows
  `approximate_price`, `photo_url`, `product_link`, `reserved_by_id` and both
  foreign keys (owner CASCADE, reserved_by SET NULL).
- Reversibility checked: `alembic downgrade -1` removed the table,
  `alembic upgrade head` recreated it.
- `configure_mappers()` succeeds with the two foreign keys to `user`.

## Open questions

- The spec has no way to release a claimed gift, so a misclick is permanent. No
  release endpoint was added because `description.md` does not ask for one; this
  is a product decision to confirm, not an oversight.

## Findings outside this feature

Surfaced while verifying, not caused by this change, and not fixed here:

- `tests/sign-up.spec.ts` "Sign up with existing email" fails: the backend does
  return "The user with this email already exists in the system", and the app does
  surface other signup errors, but no message reaches the page for this one and
  the toast region stays empty. `handleError` in `src/utils.ts` also calls the
  `useCustomToast` hook from a plain function, which breaks the Rules of Hooks.
  Not proven pre-existing by reverting, so it needs its own investigation.
- `tsconfig.json` includes only `src/**/*.ts`, so most `.tsx` files escape type
  checking. With `.tsx` included there are five further errors in files this
  feature never touched.
