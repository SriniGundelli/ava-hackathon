-- Database schema for Ava AI Talent Assistant

-- Bookings table to store scheduled calls
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    candidate_name VARCHAR(255) NOT NULL,
    candidate_email VARCHAR(255) NOT NULL,
    candidate_phone VARCHAR(50),
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    booking_uid VARCHAR(255) UNIQUE NOT NULL,
    meeting_url TEXT,
    time_zone VARCHAR(100) DEFAULT 'America/New_York',
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Call logs table to track voice interactions
CREATE TABLE IF NOT EXISTS call_logs (
    id SERIAL PRIMARY KEY,
    call_sid VARCHAR(255),
    from_number VARCHAR(50),
    to_number VARCHAR(50),
    call_status VARCHAR(50),
    call_duration INTEGER,
    webhook_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Twilio setup configuration
CREATE TABLE IF NOT EXISTS twilio_setup (
    id SERIAL PRIMARY KEY,
    trunk_sid VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    friendly_name VARCHAR(255) NOT NULL,
    elevenlabs_domain VARCHAR(255) NOT NULL,
    voice_webhook_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge base for RAG responses
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    embedding VECTOR(1536), -- For OpenAI embeddings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_bookings_email ON bookings(candidate_email);
CREATE INDEX IF NOT EXISTS idx_bookings_scheduled_time ON bookings(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_call_logs_call_sid ON call_logs(call_sid);
CREATE INDEX IF NOT EXISTS idx_call_logs_created_at ON call_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);