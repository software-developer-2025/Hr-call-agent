import psycopg2
from psycopg2 import sql
import os

DATABASE_URL = "postgresql://neondb_owner:npg_8BuzMcd1DyHk@ep-restless-river-ai5acm8g-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set")

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()


def create_enums():
    cur.execute("""
    DO $$ BEGIN
        CREATE TYPE company_status AS ENUM ('active', 'suspended');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """)

    cur.execute("""
    DO $$ BEGIN
        CREATE TYPE interview_status AS ENUM (
            'queued','scheduled','calling','in_progress',
            'evaluating','completed','failed','rescheduled','not_received'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """)

    cur.execute("""
    DO $$ BEGIN
        CREATE TYPE call_status AS ENUM (
            'ringing','answered','no_answer','busy','failed','completed'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """)

    cur.execute("""
    DO $$ BEGIN
        CREATE TYPE subscription_status AS ENUM ('active','expired','cancelled');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """)


def create_tables():

    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        status company_status DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_configs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        opening_script TEXT,
        interview_prompt TEXT,
        marking_prompt TEXT,
        max_questions INT,
        max_duration_minutes INT,
        is_active BOOLEAN DEFAULT TRUE,
        version INT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS llm_configs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        provider TEXT,
        model_name TEXT,
        encrypted_api_key TEXT,
        max_tokens INT,
        temperature FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS twilio_accounts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        account_sid TEXT,
        encrypted_auth_token TEXT,
        outbound_number TEXT,
        region TEXT,
        cps_limit INT DEFAULT 50,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidate_batches (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        filename TEXT,
        total_records INT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        batch_id UUID REFERENCES candidate_batches(id) ON DELETE SET NULL,
        name TEXT,
        phone TEXT,
        email TEXT,
        resume_text TEXT,
        experience_years INT,
        status interview_status DEFAULT 'queued',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_jobs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
        scheduled_time TIMESTAMP,
        priority INT DEFAULT 1,
        status TEXT DEFAULT 'queued',
        retry_count INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        candidate_id UUID REFERENCES candidates(id),
        twilio_account_id UUID REFERENCES twilio_accounts(id),
        interview_config_id UUID REFERENCES interview_configs(id),
        llm_config_id UUID REFERENCES llm_configs(id),
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_seconds INT,
        call_status call_status,
        total_questions INT,
        total_answers INT,
        overall_score FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
        sender TEXT,
        message_text TEXT,
        question_number INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS interview_evaluations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES interview_sessions(id) ON DELETE CASCADE,
        technical_score INT,
        communication_score INT,
        problem_solving_score INT,
        confidence_score INT,
        overall_score FLOAT,
        evaluation_summary TEXT,
        raw_llm_response JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscription_plans (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT,
        max_calls_per_day INT,
        max_concurrent_calls INT,
        max_tokens_per_month INT,
        price FLOAT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS company_subscriptions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        plan_id UUID REFERENCES subscription_plans(id),
        start_date DATE,
        end_date DATE,
        status subscription_status
    );
    """)


def create_indexes():
    cur.execute("CREATE INDEX IF NOT EXISTS idx_company_id ON candidates(company_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_session_company ON interview_sessions(company_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_job_status ON interview_jobs(status);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_session_candidate ON interview_sessions(candidate_id);")


if __name__ == "__main__":
    create_enums()
    create_tables()
    create_indexes()
    print("Database schema created successfully.")
    cur.close()
    conn.close()