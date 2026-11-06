import json
import redis
import psycopg

STREAM = "transactions"
GROUP = "ingesters"
CONSUMER = "worker-1"

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
conn = psycopg.connect("postgresql://ledger:ledger@localhost:5432/ledger")

try:
    r.xgroup_create(STREAM, GROUP, id="0", mkstream=True)
except redis.ResponseError:
    pass  # the group already exists, which is fine

inserted = 0
duplicates = 0

while True:
    messages = r.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=10, block=2000)
    if not messages:
        break

    for _stream, entries in messages:
        for msg_id, fields in entries:
            event = json.loads(fields["data"])

            with conn.transaction():
                cur = conn.execute(
                    """
                    INSERT INTO ledger_entries
                      (event_id, type, store_id, amount_minor, currency, occurred_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO NOTHING
                    """,
                    (
                        event["event_id"],
                        event["type"],
                        event["store_id"],
                        event["amount_minor"],
                        event["currency"],
                        event["occurred_at"],
                    ),
                )

            if cur.rowcount == 1:
                inserted += 1
            else:
                duplicates += 1

            r.xack(STREAM, GROUP, msg_id)

print(f"Done. Inserted: {inserted}, duplicates skipped: {duplicates}")