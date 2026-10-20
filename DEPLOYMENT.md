# EventHub setup and release steps

## Run locally

1. Install the packages listed in `requirements.txt` in your Python environment.
2. Copy `.env.example` to `.env` and set a private `SECRET_KEY`.
3. Keep `SEED_DEMO_DATA=true` for a local demo database. The sample accounts all use the same demo password and must never be exposed as production accounts.
4. Start the app with `python run.py` and open `http://127.0.0.1:5000`.

## Prepare a production account

1. Set `SEED_DEMO_DATA=false`.
2. Set `SECRET_KEY` to a unique random value that is not in source control.
3. Set `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` for the first administrator. The password must contain at least 10 characters.
4. Use a fresh production database. Existing databases that were initialized with demo data keep those users; changing `SEED_DEMO_DATA` does not remove them.
5. Use HTTPS. Production sessions are configured as secure, HTTP-only, and same-site cookies.

## Important Vercel storage limitation

This app currently uses SQLite. Vercel serverless filesystems are not durable, so a SQLite file stored there can disappear or differ between instances. `DATABASE_PATH` only selects a file path; it does not make that file persistent. Do not use the current SQLite setup for real customer bookings on Vercel. Before production, migrate the database layer to a managed persistent database and configure its credentials. This requires choosing and provisioning that database service.

## Payments and email

The current booking flow records a booking total in INR but does not collect money. Do not describe a booking as paid. A real payment flow needs a payment provider account, server-side payment verification, and refund/cancellation rules. Email verification and password reset also need an email delivery provider and credentials.

## Event times and check-in

Events are stored in India Standard Time using `YYYY-MM-DD HH:MM`. The UI displays friendly IST times. Organizers can check in a ticket once by entering its ticket code on the event registrations page. The current check-in flow is manual and does not use a camera or QR scanner.
