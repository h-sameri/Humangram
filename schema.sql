CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER DEFAULT 0,
    max_members INTEGER DEFAULT 0,
    oldest_message INTEGER DEFAULT 0,
    phone_number VARCHAR(16) DEFAULT NULL,
    vouched_for INTEGER DEFAULT 0,
    external_id TEXT UNIQUE DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS channels (
    channel_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users,
    members INTEGER,
    association_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vouching (
    voucher BIGINT REFERENCES users,
    vouched_for BIGINT REFERENCES users,
    status VARCHAR(1) DEFAULT 'V',
    vouching_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (voucher, vouched_for)
);

CREATE TABLE IF NOT EXISTS api (
    token VARCHAR(32) PRIMARY KEY,
    quota INTEGER DEFAULT -1
)
