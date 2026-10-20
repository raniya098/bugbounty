# EventHub setup and release steps

## Run locally

1. Install the packages listed in `requirements.txt` in your Python environment.
2. Set `SECRET_KEY` in your local environment before starting the app. Flask does not load `.env` files automatically in this project.
3. Keep `SEED_DEMO_DATA=true` for a local demo database. The sample accounts all use the same demo password and must never be exposed as production accounts.
4. Start the app with `python run.py` and open `http://127.0.0.1:5000`.

## Prepare a production account

1. Set `SEED_DEMO_DATA=false`.
2. Set `SECRET_KEY` to a unique random value that is not in source control.
3. Set `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` for the first administrator. The password must contain at least 10 characters.
4. Use a fresh production database. Existing databases that were initialized with demo data keep those users; changing `SEED_DEMO_DATA` does not remove them.
5. Use HTTPS. Production sessions are configured as secure, HTTP-only, and same-site cookies.

## Important Vercel storage limitation

The app exposes its Flask instance from `app/app.py`, which is a Vercel-recognized Flask entry point. The Vercel runtime uses a read-only filesystem except for temporary `/tmp` storage, so the default Vercel SQLite path is `/tmp/eventhub.db` to allow the function to start.

Temporary storage is not durable or shared across serverless instances. Accounts, events, and bookings may disappear after a cold start or differ between instances. This is only suitable for a disposable preview. For a reliable competition or real customer bookings, migrate the database layer to a managed persistent database and configure its connection string; setting `DATABASE_PATH` to another file path does not make SQLite persistent.

### Vercel environment variables

In the Vercel project, open **Settings → Environment Variables** and configure:

- `SECRET_KEY`: a long, random secret used to sign sessions.
- `SEED_DEMO_DATA`: set to `false` for production.
- `INITIAL_ADMIN_EMAIL`: the initial administrator's email.
- `INITIAL_ADMIN_PASSWORD`: a private password of at least 10 characters.
- `DATABASE_PATH`: leave unset for the temporary `/tmp/eventhub.db` preview, or set it only when the code has been migrated to a persistent database adapter.

Redeploy after changing environment variables. The app deliberately fails startup if `SECRET_KEY` or the first administrator credentials are missing; this prevents insecure sessions or a deployment with no administrator account.

## Payments and email

The current booking flow records a booking total in INR but does not collect money. Do not describe a booking as paid. A real payment flow needs a payment provider account, server-side payment verification, and refund/cancellation rules. Email verification and password reset also need an email delivery provider and credentials.

## Event times and check-in

Events are stored in India Standard Time using `YYYY-MM-DD HH:MM`. The UI displays friendly IST times. Organizers can check in a ticket once by entering its ticket code on the event registrations page. The current check-in flow is manual and does not use a camera or QR scanner.
