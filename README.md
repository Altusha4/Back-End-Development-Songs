# Back-End-Development-Songs

Flask Songs REST API backed by MongoDB. Course project prepared from the IBM Skills Network starter template with AI assistance; review and understand the implementation before submission.

## Setup

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Validated locally with Python 3.14; container uses Python 3.12. No secrets are committed. The original Linux lab helper remains in `bin/setup.sh`; local validation used the virtual environment above.

## Run

Start MongoDB, then set `MONGODB_SERVICE` and optionally `MONGODB_PORT`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`. Alternatively set `MONGODB_URI`. Database name defaults to `songs` and can be overridden with `MONGODB_DATABASE`.

```sh
MONGODB_SERVICE=127.0.0.1 MONGODB_PORT=27018 flask --app app run --port 5001
curl -i http://localhost:5001/health
curl -i http://localhost:5001/song
```

Implements health/count and GET, POST, PUT, DELETE on `/song` and `/song/<id>`. MongoDB has a unique index on `id`. Initial sample data is inserted only into an empty collection; restarting the service does not erase changes. No database credentials are printed.

Validation used a real MongoDB 7 container: GET /health and /song returned 200, PUT returned 201 with changed content, DELETE returned 204. Duplicate IDs return 302 per the course specification; missing records return 404.

## Container

The Dockerfile runs Gunicorn as an unprivileged user. Preserve the original IBM licensing and attribution.
