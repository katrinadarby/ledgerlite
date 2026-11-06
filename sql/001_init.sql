CREATE TABLE ledger_entries (
  event_id           UUID PRIMARY KEY,
  type               TEXT NOT NULL CHECK (type IN ('purchase','refund','fx')),
  store_id           TEXT NOT NULL,
  amount_minor       BIGINT NOT NULL,
  currency           CHAR(3) NOT NULL,
  fx_rate            NUMERIC(18,8),
  occurred_at        TIMESTAMPTZ NOT NULL,
  ingested_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  reverses_entry_id  UUID REFERENCES ledger_entries(event_id)
);