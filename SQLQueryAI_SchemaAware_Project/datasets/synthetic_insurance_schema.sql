
CREATE TABLE policy_period (
    policy_id VARCHAR(50),
    state VARCHAR(50),
    effective_date DATE
);

CREATE TABLE coverage (
    policy_id VARCHAR(50),
    coverage_code VARCHAR(50),
    coverage_limit INTEGER
);

CREATE TABLE driver (
    policy_id VARCHAR(50),
    driver_name VARCHAR(100)
);

CREATE TABLE claim (
    claim_id VARCHAR(50),
    policy_id VARCHAR(50),
    claim_amount INTEGER
);
