# ADR-001: Neon Auth and Object Storage

**Date:** 2026-11-13  
**Status:** accepted  
**Deciders:** pastaisfine  
**Context:** ServeEasy needs user login, image uploads and per-branch storage.

## Decision

Use **Managed Better Auth** and **Neon Object Storage**.

## Details

### Auth

- Provider: Neon's Managed Better Auth (no self-hosted auth server).
- Library: `@neon/auth` (Next.js wrapper).
- Storage: Users and sessions in the `neon_auth` schema on Lakebase Postgres.
- Branching: Auth state branches with the database. A preview branch has its own auth URL and isolated users.
- Registration: Students use an `@graduate.utm.my` email, verify its mailbox with an email OTP, and provide a matric number matching `A` + two digits + two letters + four digits. Service providers verify an email by OTP but do not need a matric number. Student and service-provider roles are self-selected; food sellers remain provisioned separately.
- Profile provisioning: After email verification, the Next.js server saves the selected role and optional matric number to the backend `users` row associated with the Neon Auth user ID.
- Operations: Email OTP must be enabled on each Neon Auth branch and configured with working email delivery; the application cannot enable the managed-auth plugin itself.

### Object Storage

- Provider: Neon Object Storage (S3-compatible).
- Region: `aws-ap-southeast-1` (same as the project).
- Bucket: `uploads`, `public_read` access.
- Usage: Listing and service photos only.
- Path style: `listings/<user-id>/<uuid>.<ext>`. Keys are unique; files are never overwritten.
- CDN: None. Public-read objects are served directly from the S3 endpoint; Hot images (e.g. avatars) should be served from a CDN origin.
- Client: AWS SDK v3 (`boto3` for backend, `@aws-sdk/client-s3` for future Node.js backends).

## Rationale

| Option | Pros | Cons |
|--------|------|------|
| Managed Better Auth | One billing, branch isolation, no ops | Limited plugins; no MFA, passkey yet |
| Self-hosted Better Auth | Full plugin control | Must manage DB, email, secrets |
| Supabase Auth | Feature-complete | Vendor lock-in; separate billing |
| Clerk / Auth.js | Familiar | Separate infra; not branch-aware |

Neon Object Storage was selected over:

- **Supabase Storage**: Vendor lock-in. Neon is already provisioned.
- **Cloudflare R2**: Extra provider. Neon storage branches with DB.
- **AWS S3**: Requires separate cred management and CORS config. Neon storage is already set up and branches with the DB.

## Consequences

- **Positive:** Simpler ops, per-branch auth and storage, one billing statement.
- **Negative:** No MFA/passkey (roadmap), no custom SMTP on free tier, public-read only (no signed PUT URLs).

## Verification

1. A student signs up with a matching matric number and `@graduate.utm.my` address, verifies the email OTP, and receives a student role in the backend profile.
2. A service provider signs up with an email address, verifies the email OTP, and receives a service-provider role without a matric number.
3. A new listing photo uploads and appears on the listing detail page anonymously.
4. A listing with a foreign image key is rejected (ownership check).
5. A preview branch created from production gets its own storage endpoint.

## Related

- PRD F-01/F-02: User registration and login.
- PRD F-04/F-16: Create Product Listing and Service Listing (photos required).
- PRD 3.1 Entities: User, ProductListing, Service.
