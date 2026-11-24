# ServeEasy Glossary

This document defines terms used across the ServeEasy codebase. When there's a conflict between a term's everyday meaning and its technical meaning here, the technical meaning wins.

## Core concepts

### Service (noun)

A student-provided activity, not a physical product. Examples: tutoring, haircuts, printing, repairs.

### Item (noun)

A physical product sold secondhand. Examples: textbooks, gadgets, clothing. Formerly called "listing" but "item" better matches the PRD and user language.

### Listing

A record in the database for an item or a service. Each listing has an owner (a student) and appears on search results.

### Meetup spot

The campus location where the buyer and seller hand over an item, or where a service is provided. Free text; no lookup table.

### Shop

A student-run enterprise's profile page. It aggregates that student's item listings and services. One student can own at most one shop.

### Order

A food-related term: a student's request for cafeteria meals. It has a status (pending, confirmed, ready, completed) and includes payment proof.

### Booking

A service-related term: a student's request for a campus service. It has a status (pending, accepted, declined, completed) and includes requested date.

### Payment proof

A screenshot or reference number a student submits to confirm a money transfer (DuitNow/TNG). The seller verifies it before completing an order.

### External contact links

Optional public WhatsApp and Telegram links on item, service, shop, and cafeteria pages. User accounts manage their own contact details; food-provider staff manage the cafeteria's business contacts.

## Entity types

### User

A single account shared by students, food sellers and service providers. Role distinguishes capabilities: `student`, `food_seller`, `service_provider`.

### ProductListing

A record for a secondhand item. Has `condition` and `status` (active, sold, removed).

### Service

A record for a campus service (printing, tailoring, etc.). Has `unit` (e.g. "hour") and is booked via `ServiceBooking`.

### ServiceBooking

A request by a student for a service. Provider accepts/declines and updates status.

## Actions

### Publish

Create a new listing (item or service) that goes live immediately. No moderation queue.

### Mark as sold

Set a listing's status to `sold`. It stays viewable but no longer appears in search.

### Remove

Soft-delete a listing by setting `status` to `removed`. It disappears from search and detail pages.

## Tech terms

### Managed Better Auth

Neon's hosted version of Better Auth. The app stores no passwords; Neon handles email/password, OAuth and session management.

### S3-compatible storage

Neon's object storage. The API matches Amazon S3 (SigV4, path-style addressing) so the AWS SDK works with no custom adapters.

## Acronyms

- **Neon**: Cloud backend primitives around Lakebase Postgres (Auth, Object Storage, Functions, AI Gateway, Realtime).
- **Lakebase Postgres**: Neon's database engine, built on the lakebase architecture (OLTP on cloud object storage).
- **S3**: Simple Storage Service, Amazon's object storage API that Neon implements.
- **JWKS**: JSON Web Key Set, the public keys Neon Auth uses to verify JWTs.
- **JWT**: JSON Web Token, the short-lived credential the frontend gets and the backend verifies.
