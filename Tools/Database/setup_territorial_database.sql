-- Terminal Grounds Territorial Control System Database Schema
-- PostgreSQL with PostGIS Spatial Extensions
-- Phase 1 Implementation

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create territorial database and user
-- (Run as postgres superuser)
-- CREATE DATABASE terminal_grounds_territorial;
-- CREATE USER tg_territorial WITH ENCRYPTED PASSWORD 'territorial_secure_2025';
-- GRANT ALL PRIVILEGES ON DATABASE terminal_grounds_territorial TO tg_territorial;

-- Regional hierarchy (8 major regions)
CREATE TABLE regions (
    region_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    environmental_type VARCHAR(50) DEFAULT 'mixed', -- 'tech_wastes', 'metro_corridors', etc.
    strategic_value INTEGER DEFAULT 50 CHECK (strategic_value >= 1 AND strategic_value <= 100),
    boundary_polygon GEOMETRY(POLYGON, 4326), -- PostGIS spatial boundary
    center_point GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- District operational areas (24-64 districts)
CREATE TABLE districts (
    district_id SERIAL PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES regions(region_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    tactical_importance INTEGER DEFAULT 30 CHECK (tactical_importance >= 1 AND tactical_importance <= 100),
    resource_type VARCHAR(50) DEFAULT 'mixed', -- 'salvage', 'intel', 'strategic', etc.
    boundary_polygon GEOMETRY(POLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(region_id, name)
);

-- Control points (48-384 control points)
CREATE TABLE control_points (
    point_id SERIAL PRIMARY KEY,
    district_id INTEGER NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    point_type VARCHAR(50) DEFAULT 'checkpoint', -- 'command_post', 'supply_depot', etc.
    capture_difficulty INTEGER DEFAULT 25 CHECK (capture_difficulty >= 1 AND capture_difficulty <= 100),
    position GEOMETRY(POINT, 4326),
    control_radius FLOAT DEFAULT 50.0 CHECK (control_radius > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(district_id, name)
);

-- Faction definitions
CREATE TABLE factions (
    faction_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color_hex VARCHAR(7) DEFAULT '#FFFFFF', -- Faction color for UI
    influence_modifier FLOAT DEFAULT 1.0 CHECK (influence_modifier > 0),
    aggression_level FLOAT DEFAULT 0.5 CHECK (aggression_level >= 0 AND aggression_level <= 1),
    defensive_bonus FLOAT DEFAULT 1.0 CHECK (defensive_bonus > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Faction influence tracking (0-100 per faction per territory)
CREATE TABLE faction_influence (
    influence_id SERIAL PRIMARY KEY,
    territory_type VARCHAR(20) NOT NULL CHECK (territory_type IN ('region', 'district', 'control_point')),
    territory_id INTEGER NOT NULL,
    faction_id INTEGER NOT NULL REFERENCES factions(faction_id) ON DELETE CASCADE,
    influence_value INTEGER DEFAULT 0 CHECK (influence_value >= 0 AND influence_value <= 100),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    decay_rate FLOAT DEFAULT 1.0 CHECK (decay_rate >= 0),
    UNIQUE(territory_type, territory_id, faction_id)
);

-- Influence change history for analytics
CREATE TABLE influence_history (
    history_id SERIAL PRIMARY KEY,
    territory_type VARCHAR(20) NOT NULL CHECK (territory_type IN ('region', 'district', 'control_point')),
    territory_id INTEGER NOT NULL,
    faction_id INTEGER NOT NULL REFERENCES factions(faction_id) ON DELETE CASCADE,
    influence_change INTEGER NOT NULL, -- Positive or negative change
    previous_value INTEGER CHECK (previous_value >= 0 AND previous_value <= 100),
    new_value INTEGER CHECK (new_value >= 0 AND new_value <= 100),
    change_cause VARCHAR(100), -- 'objective_complete', 'combat_victory', etc.
    player_id INTEGER, -- Player responsible for change (if applicable)
    session_id UUID DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI territorial decisions log
CREATE TABLE ai_decisions (
    decision_id SERIAL PRIMARY KEY,
    faction_id INTEGER NOT NULL REFERENCES factions(faction_id) ON DELETE CASCADE,
    decision_type VARCHAR(50) NOT NULL, -- 'offensive', 'defensive', 'strategic'
    target_territory_type VARCHAR(20) CHECK (target_territory_type IN ('region', 'district', 'control_point')),
    target_territory_id INTEGER,
    decision_data JSONB, -- Flexible storage for AI decision parameters
    execution_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completion_timestamp TIMESTAMP WITH TIME ZONE,
    success BOOLEAN,
    result_data JSONB
);

-- Territorial events (dynamic events affecting territories)
CREATE TABLE territorial_events (
    event_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- 'alien_incursion', 'resource_discovery', 'infrastructure_failure'
    event_name VARCHAR(100),
    description TEXT,
    affected_territories JSONB, -- Array of {type, id} objects
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_hours INTEGER DEFAULT 24,
    end_time TIMESTAMP WITH TIME ZONE,
    impact_modifier FLOAT DEFAULT 1.0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Player territorial actions
CREATE TABLE player_territorial_actions (
    action_id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    faction_id INTEGER NOT NULL REFERENCES factions(faction_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL, -- 'objective_complete', 'combat_victory', 'extraction_success'
    territory_type VARCHAR(20) NOT NULL CHECK (territory_type IN ('region', 'district', 'control_point')),
    territory_id INTEGER NOT NULL,
    influence_gained INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    session_id UUID DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial faction data
INSERT INTO factions (faction_id, name, description, color_hex, influence_modifier, aggression_level, defensive_bonus) VALUES
(1, 'Directorate', 'Corporate efficiency through technological superiority', '#0066CC', 1.0, 0.6, 1.1),
(2, 'Free77', 'Liberation through resistance networks', '#CC3300', 1.1, 0.8, 0.9),
(3, 'Nomad Clans', 'Survival through environmental mastery', '#996633', 0.9, 0.4, 1.2),
(4, 'Civic Wardens', 'Order through emergency response authority', '#006600', 1.0, 0.5, 1.3),
(5, 'Vultures Union', 'Profit through salvage maximization', '#CC6600', 1.0, 0.7, 1.0),
(6, 'Vaulted Archivists', 'Preservation through knowledge protection', '#6600CC', 0.8, 0.3, 1.1),
(7, 'Corporate Combine', 'Dominance through market control', '#CCCC00', 1.2, 0.9, 0.8)
ON CONFLICT (faction_id) DO UPDATE SET
    description = EXCLUDED.description,
    color_hex = EXCLUDED.color_hex,
    influence_modifier = EXCLUDED.influence_modifier,
    aggression_level = EXCLUDED.aggression_level,
    defensive_bonus = EXCLUDED.defensive_bonus;

-- Insert initial territorial hierarchy (Phase 1 - basic structure)
INSERT INTO regions (region_id, name, description, environmental_type, strategic_value, center_point) VALUES
(1, 'Tech Wastes', 'Industrial salvage and alien technology recovery zone', 'industrial', 85, ST_GeomFromText('POINT(-74.006 40.7128)', 4326)),
(2, 'Metro Corridors', 'Underground transit and maintenance networks', 'underground', 75, ST_GeomFromText('POINT(-74.008 40.7148)', 4326)),
(3, 'Corporate Zones', 'Business districts and corporate facilities', 'urban', 90, ST_GeomFromText('POINT(-74.004 40.7108)', 4326)),
(4, 'Residential Districts', 'Civilian population centers and social infrastructure', 'civilian', 60, ST_GeomFromText('POINT(-74.002 40.7088)', 4326)),
(5, 'Military Compounds', 'Defensive positions and weapons stockpiles', 'military', 95, ST_GeomFromText('POINT(-74.010 40.7168)', 4326)),
(6, 'Research Facilities', 'Scientific installations and data archives', 'scientific', 80, ST_GeomFromText('POINT(-74.012 40.7188)', 4326)),
(7, 'Trade Routes', 'Transportation corridors and market centers', 'commercial', 70, ST_GeomFromText('POINT(-74.000 40.7068)', 4326)),
(8, 'Neutral Ground', 'International zones and diplomatic areas', 'neutral', 50, ST_GeomFromText('POINT(-74.006 40.7128)', 4326))
ON CONFLICT (region_id) DO UPDATE SET
    description = EXCLUDED.description,
    environmental_type = EXCLUDED.environmental_type,
    strategic_value = EXCLUDED.strategic_value;

-- Create spatial indexes for performance
CREATE INDEX IF NOT EXISTS idx_regions_boundary ON regions USING GIST (boundary_polygon);
CREATE INDEX IF NOT EXISTS idx_regions_center ON regions USING GIST (center_point);
CREATE INDEX IF NOT EXISTS idx_districts_boundary ON districts USING GIST (boundary_polygon);
CREATE INDEX IF NOT EXISTS idx_districts_center ON districts USING GIST (center_point);
CREATE INDEX IF NOT EXISTS idx_control_points_position ON control_points USING GIST (position);

-- Create performance indexes for influence queries
CREATE INDEX IF NOT EXISTS idx_faction_influence_lookup ON faction_influence (territory_type, territory_id);
CREATE INDEX IF NOT EXISTS idx_faction_influence_faction ON faction_influence (faction_id, influence_value DESC);
CREATE INDEX IF NOT EXISTS idx_faction_influence_updated ON faction_influence (last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_influence_history_lookup ON influence_history (territory_type, territory_id, faction_id);
CREATE INDEX IF NOT EXISTS idx_influence_history_timestamp ON influence_history (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_player_actions_player ON player_territorial_actions (player_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_player_actions_faction ON player_territorial_actions (faction_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ai_decisions_faction ON ai_decisions (faction_id, execution_timestamp DESC);

-- Create stored procedures for common operations
CREATE OR REPLACE FUNCTION update_territory_influence(
    p_territory_type VARCHAR(20),
    p_territory_id INTEGER,
    p_faction_id INTEGER,
    p_influence_change INTEGER,
    p_change_cause VARCHAR(100) DEFAULT 'system_update',
    p_player_id INTEGER DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    current_influence INTEGER;
    new_influence INTEGER;
    faction_modifier FLOAT;
BEGIN
    -- Get faction modifier
    SELECT influence_modifier INTO faction_modifier 
    FROM factions 
    WHERE faction_id = p_faction_id;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Get current influence or create record
    SELECT influence_value INTO current_influence
    FROM faction_influence
    WHERE territory_type = p_territory_type 
      AND territory_id = p_territory_id 
      AND faction_id = p_faction_id;
    
    IF NOT FOUND THEN
        current_influence := 0;
        INSERT INTO faction_influence (territory_type, territory_id, faction_id, influence_value)
        VALUES (p_territory_type, p_territory_id, p_faction_id, 0);
    END IF;
    
    -- Calculate new influence with faction modifier
    new_influence := GREATEST(0, LEAST(100, current_influence + ROUND(p_influence_change * faction_modifier)));
    
    -- Update influence
    UPDATE faction_influence 
    SET influence_value = new_influence, 
        last_updated = CURRENT_TIMESTAMP
    WHERE territory_type = p_territory_type 
      AND territory_id = p_territory_id 
      AND faction_id = p_faction_id;
    
    -- Record history
    INSERT INTO influence_history (
        territory_type, territory_id, faction_id, 
        influence_change, previous_value, new_value, 
        change_cause, player_id
    ) VALUES (
        p_territory_type, p_territory_id, p_faction_id,
        p_influence_change, current_influence, new_influence,
        p_change_cause, p_player_id
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to get territorial state
CREATE OR REPLACE FUNCTION get_territorial_state(
    p_territory_type VARCHAR(20),
    p_territory_id INTEGER
) RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'territory_id', p_territory_id,
        'territory_type', p_territory_type,
        'faction_influences', json_object_agg(faction_id, influence_value),
        'dominant_faction', (
            SELECT faction_id 
            FROM faction_influence 
            WHERE territory_type = p_territory_type 
              AND territory_id = p_territory_id
            ORDER BY influence_value DESC 
            LIMIT 1
        ),
        'is_contested', (
            SELECT COUNT(*) > 1
            FROM faction_influence 
            WHERE territory_type = p_territory_type 
              AND territory_id = p_territory_id
              AND influence_value >= 40
        ),
        'last_updated', MAX(last_updated)
    ) INTO result
    FROM faction_influence
    WHERE territory_type = p_territory_type 
      AND territory_id = p_territory_id
      AND influence_value > 0;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Daily influence decay function
CREATE OR REPLACE FUNCTION apply_influence_decay() RETURNS INTEGER AS $$
DECLARE
    decay_count INTEGER := 0;
BEGIN
    UPDATE faction_influence 
    SET influence_value = GREATEST(0, influence_value - ROUND(decay_rate)),
        last_updated = CURRENT_TIMESTAMP
    WHERE last_updated < CURRENT_TIMESTAMP - INTERVAL '1 day'
      AND influence_value > 0;
    
    GET DIAGNOSTICS decay_count = ROW_COUNT;
    RETURN decay_count;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_regions_modtime 
    BEFORE UPDATE ON regions 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_districts_modtime 
    BEFORE UPDATE ON districts 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_control_points_modtime 
    BEFORE UPDATE ON control_points 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Grant permissions to territorial user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO tg_territorial;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO tg_territorial;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO tg_territorial;

-- Performance monitoring views
CREATE OR REPLACE VIEW territorial_summary AS
SELECT 
    r.name AS region_name,
    COUNT(DISTINCT d.district_id) AS districts,
    COUNT(DISTINCT cp.point_id) AS control_points,
    AVG(fi.influence_value) AS avg_influence
FROM regions r
LEFT JOIN districts d ON r.region_id = d.region_id
LEFT JOIN control_points cp ON d.district_id = cp.district_id
LEFT JOIN faction_influence fi ON fi.territory_type = 'region' AND fi.territory_id = r.region_id
GROUP BY r.region_id, r.name
ORDER BY r.region_id;

CREATE OR REPLACE VIEW faction_territorial_control AS
SELECT 
    f.name AS faction_name,
    fi.territory_type,
    COUNT(*) AS territories_controlled,
    AVG(fi.influence_value) AS avg_influence,
    SUM(CASE WHEN fi.influence_value >= 60 THEN 1 ELSE 0 END) AS dominant_territories
FROM factions f
JOIN faction_influence fi ON f.faction_id = fi.faction_id
WHERE fi.influence_value > 0
GROUP BY f.faction_id, f.name, fi.territory_type
ORDER BY f.faction_id, fi.territory_type;

-- Initialize database with success message
SELECT 'Terminal Grounds Territorial Database Phase 1 Setup Complete' AS status;