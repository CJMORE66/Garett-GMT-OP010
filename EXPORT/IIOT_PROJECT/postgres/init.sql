-- Product History Database Schema for OP10 IIoT Platform
-- PostgreSQL initialization script

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial_number VARCHAR(50) UNIQUE NOT NULL,
    batch_number VARCHAR(50),
    material_batch VARCHAR(50),
    product_type_id INTEGER,
    variant_id INTEGER,
    customer_id INTEGER,
    work_order_id VARCHAR(30),

    status VARCHAR(20) DEFAULT 'created' CHECK (status IN ('created', 'in_progress', 'completed', 'rejected', 'rework')),
    quality_result VARCHAR(20) CHECK (quality_result IS NULL OR quality_result IN ('pending', 'ok', 'ng', 'rework')),
    quantity INTEGER DEFAULT 1,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT uq_serial UNIQUE (serial_number)
);

CREATE INDEX IF NOT EXISTS idx_products_serial ON products(serial_number);
CREATE INDEX IF NOT EXISTS idx_products_batch ON products(batch_number);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_created ON products(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_work_order ON products(work_order_id);

-- Process steps tracking
CREATE TABLE IF NOT EXISTS process_steps (
    id BIGSERIAL PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_name VARCHAR(50) NOT NULL,
    station_id VARCHAR(20) NOT NULL,
    position_id VARCHAR(20),

    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ,
    processing_duration_ms INTEGER,

    step_status VARCHAR(20) DEFAULT 'pending' CHECK (step_status IN ('pending', 'running', 'completed', 'skipped', 'error')),
    step_result VARCHAR(20) CHECK (step_result IS NULL OR step_result IN ('unknown', 'pass', 'fail')),

    cycle_count INTEGER,
    cycle_time_avg REAL,
    cycle_time_min REAL,
    cycle_time_max REAL,

    error_code INTEGER,
    error_description TEXT,
    retry_count INTEGER DEFAULT 0,

    CONSTRAINT uq_product_step UNIQUE (product_id, step_number)
);

CREATE INDEX IF NOT EXISTS idx_process_steps_product ON process_steps(product_id);
CREATE INDEX IF NOT EXISTS idx_process_steps_station ON process_steps(station_id);
CREATE INDEX IF NOT EXISTS idx_process_steps_entry ON process_steps(entry_time DESC);

-- Measurement results
CREATE TABLE IF NOT EXISTS measurements (
    id BIGSERIAL PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    step_id BIGINT REFERENCES process_steps(id) ON DELETE SET NULL,

    measurement_name VARCHAR(50) NOT NULL,
    unit VARCHAR(10),

    value REAL NOT NULL,
    min_limit REAL,
    max_limit REAL,
    target_value REAL,
    tolerance REAL,

    average REAL,
    std_dev REAL,
    min_value REAL,
    max_value REAL,
    sample_count INTEGER DEFAULT 1,

    is_pass BOOLEAN,
    deviation REAL,
    cpk REAL,

    measured_at TIMESTAMPTZ DEFAULT NOW(),
    station_id VARCHAR(20),
    sensor_id VARCHAR(20),

    image_paths TEXT[] DEFAULT ARRAY[]::TEXT[],

    CONSTRAINT chk_limits CHECK (min_limit IS NULL OR max_limit IS NULL OR value BETWEEN min_limit AND max_limit)
);

CREATE INDEX IF NOT EXISTS idx_measurements_product ON measurements(product_id);
CREATE INDEX IF NOT EXISTS idx_measurements_step ON measurements(step_id);
CREATE INDEX IF NOT EXISTS idx_measurements_name ON measurements(measurement_name);
CREATE INDEX IF NOT EXISTS idx_measurements_pass ON measurements(is_pass);

-- Product types reference table
CREATE TABLE IF NOT EXISTS product_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Variants reference table
CREATE TABLE IF NOT EXISTS variants (
    id SERIAL PRIMARY KEY,
    product_type_id INTEGER REFERENCES product_types(id),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL,
    description TEXT,
    parameters JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customers reference table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    contact_email VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Maintenance actions log
CREATE TABLE IF NOT EXISTS maintenance_actions (
    id BIGSERIAL PRIMARY KEY,
    machine_id VARCHAR(20) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    description TEXT,
    technician VARCHAR(100),
    parts_used TEXT[],
    downtime_minutes INTEGER,
    cost_parts DECIMAL(10,2),
    labor_hours DECIMAL(4,1),
    work_order_id VARCHAR(30),
    photos TEXT[],
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_maintenance_machine ON maintenance_actions(machine_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_created ON maintenance_actions(created_at DESC);

-- Quality escapes log
CREATE TABLE IF NOT EXISTS quality_escapes (
    id BIGSERIAL PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    serial_number VARCHAR(50),
    batch_number VARCHAR(50),
    defect_description TEXT,
    root_cause TEXT,
    corrective_action TEXT,
    escaped_at TIMESTAMPTZ DEFAULT NOW(),
    detected_at TIMESTAMPTZ,
    detected_by VARCHAR(100),
    cost_impact DECIMAL(10,2)
);

CREATE INDEX IF NOT EXISTS idx_quality_escapes_product ON quality_escapes(product_id);
CREATE INDEX IF NOT EXISTS idx_quality_escapes_serial ON quality_escapes(serial_number);

-- Trigger function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to relevant tables
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_process_steps_updated_at
    BEFORE UPDATE ON process_steps
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample reference data
INSERT INTO product_types (name, code, description) VALUES
('CNC Component', 'CNC-001', 'CNC machined components'),
('Hydraulic Part', 'HYD-001', 'Hydraulic system components'),
('Assembly Unit', 'ASM-001', 'Complete assembly units')
ON CONFLICT (code) DO NOTHING;

INSERT INTO customers (name, code, contact_email) VALUES
('AUDI AG', 'AUDI', 'quality@audi.de'),
('BMW Group', 'BMW', 'quality@bmw.de'),
('Volkswagen AG', 'VW', 'quality@vw.de')
ON CONFLICT (code) DO NOTHING;
