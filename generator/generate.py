import json
import random
import uuid
import redis
from datetime import datetime, timezone

STORES = ["store_001", "store_002", "store_003"]
CURRENCIES = ["USD", "EUR", "GBP"]

STREAM = "transactions"
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def make_purchase():
    return {
        "event_id": str(uuid.uuid4()),
        "type": "purchase",
        "store_id": random.choice(STORES),
        "amount_minor": random.randint(500, 20000),
        "currency": random.choice(CURRENCIES),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }


for _ in range(100):
    event = make_purchase()
    r.xadd(STREAM, {"data": json.dumps(event)})

print("Published 100 events. Stream length:", r.xlen(STREAM))