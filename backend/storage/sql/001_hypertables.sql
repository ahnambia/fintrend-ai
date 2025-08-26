SELECT create_hypertable('prices', 'ts', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_prices_ticker_ts_desc ON prices (ticker, ts DESC);
