-- VisaWire Local: Visa Interview Question Database Schema
-- Student visas only, top 20 destinations

CREATE TABLE IF NOT EXISTS destinations (
    country_code    VARCHAR(3) PRIMARY KEY,
    country_name    VARCHAR(100) NOT NULL UNIQUE,
    risk_profile_notes TEXT
);

CREATE TABLE IF NOT EXISTS visa_questions (
    id                      SERIAL PRIMARY KEY,
    destination_country     VARCHAR(3) NOT NULL REFERENCES destinations(country_code),
    category                VARCHAR(50) NOT NULL CHECK (category IN (
        'academics', 'finance', 'intent', 'ties', 'background', 'course_choice', 'country_specific'
    )),
    question_text           TEXT NOT NULL,
    question_text_hi        TEXT,
    officer_objective       TEXT,
    difficulty_level        INTEGER NOT NULL DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 3),
    common_failure_patterns TEXT,
    followup_rules          TEXT
);

CREATE TABLE IF NOT EXISTS followups (
    id                  SERIAL PRIMARY KEY,
    parent_question_id  INTEGER NOT NULL REFERENCES visa_questions(id) ON DELETE CASCADE,
    trigger_condition   TEXT NOT NULL,
    followup_question   TEXT NOT NULL,
    followup_question_hi TEXT
);

CREATE TABLE IF NOT EXISTS risk_factors (
    id                  SERIAL PRIMARY KEY,
    destination_country VARCHAR(3) NOT NULL REFERENCES destinations(country_code),
    origin_country      VARCHAR(100) NOT NULL,
    risk_reason         TEXT NOT NULL,
    scrutiny_level      INTEGER NOT NULL DEFAULT 1 CHECK (scrutiny_level BETWEEN 1 AND 3)
);

CREATE INDEX IF NOT EXISTS idx_questions_country ON visa_questions(destination_country);
CREATE INDEX IF NOT EXISTS idx_questions_category ON visa_questions(category);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON visa_questions(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_followups_parent ON followups(parent_question_id);
CREATE INDEX IF NOT EXISTS idx_risk_dest ON risk_factors(destination_country);
CREATE INDEX IF NOT EXISTS idx_risk_origin ON risk_factors(origin_country);
