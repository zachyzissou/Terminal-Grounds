-- Terminal Grounds Territorial Control System Database Schema
-- PostgreSQL with PostGIS Extensions
-- CTO Technical Implementation v1.0

-- Enable PostGIS spatial extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Factions table based on existing Factions.csv structure
CREATE TABLE factions (
    id SERIAL PRIMARY KEY,
    faction_name VARCHAR(100) NOT NULL UNIQUE,
    discipline DECIMAL(3,2) NOT NULL CHECK (discipline >= 0 AND discipline <= 1),
    aggression DECIMAL(3,2) NOT NULL CHECK (aggression >= 0 AND aggression <= 1),
    tech_level DECIMAL(3,2) NOT NULL CHECK (tech_level >= 0 AND tech_level <= 1),
    loot_tier_bias JSONB NOT NULL, -- {field: 0.7, splice: 0.25, monolith: 0.05}
    vehicle_affinity JSONB NOT NULL, -- {ground: 0.6, air: 0.2, drone: 0.2}
    event_preference JSONB NOT NULL, -- {ConvoyWar: 0.7}
    palette_hex VARCHAR(50) NOT NULL,
    emblem_ref VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Territory types for hierarchical control
CREATE TABLE territory_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE, -- region, district, zone, outpost
    hierarchy_level INTEGER NOT NULL, -- 1=region, 2=district, 3=zone, 4=outpost
    max_influence_range INTEGER NOT NULL, -- meters
    control_point_requirement INTEGER NOT NULL, -- points needed for control
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Core territories table with spatial data
CREATE TABLE territories (
    id SERIAL PRIMARY KEY,
    territory_name VARCHAR(100) NOT NULL,
    territory_type_id INTEGER REFERENCES territory_types(id),
    parent_territory_id INTEGER REFERENCES territories(id), -- hierarchical structure
    boundary_polygon GEOMETRY(POLYGON, 4326) NOT NULL, -- territorial boundaries
    center_point GEOMETRY(POINT, 4326) NOT NULL, -- territory center
    control_points INTEGER DEFAULT 0,
    current_controller_faction_id INTEGER REFERENCES factions(id),
    contested BOOLEAN DEFAULT FALSE,
    last_contested_at TIMESTAMP WITH TIME ZONE,
    strategic_value INTEGER DEFAULT 1, -- 1-10 importance scale
    resource_multiplier DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Faction territorial control and influence
CREATE TABLE faction_territorial_influence (
    id SERIAL PRIMARY KEY,
    faction_id INTEGER REFERENCES factions(id),
    territory_id INTEGER REFERENCES territories(id),
    influence_level INTEGER DEFAULT 0, -- 0-100 influence percentage
    control_points INTEGER DEFAULT 0,
    last_action_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    influence_trend VARCHAR(20) DEFAULT 'stable', -- growing, declining, stable
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(faction_id, territory_id)
);

-- Territorial events and conflicts
CREATE TABLE territorial_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- capture, contest, defend, abandon
    territory_id INTEGER REFERENCES territories(id),
    initiating_faction_id INTEGER REFERENCES factions(id),
    defending_faction_id INTEGER REFERENCES factions(id),
    event_location GEOMETRY(POINT, 4326) NOT NULL,
    participants JSONB, -- player/AI participant data
    outcome VARCHAR(50), -- success, failure, contested
    influence_change INTEGER DEFAULT 0,
    control_points_change INTEGER DEFAULT 0,
    event_duration INTERVAL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    event_data JSONB -- additional event-specific data
);

-- Control point structures (bases, outposts, strategic points)
CREATE TABLE control_structures (
    id SERIAL PRIMARY KEY,
    structure_name VARCHAR(100) NOT NULL,
    structure_type VARCHAR(50) NOT NULL, -- base, outpost, checkpoint, resource_node
    territory_id INTEGER REFERENCES territories(id),
    controlling_faction_id INTEGER REFERENCES factions(id),
    location GEOMETRY(POINT, 4326) NOT NULL,
    health INTEGER DEFAULT 100,
    max_health INTEGER DEFAULT 100,
    defensive_strength INTEGER DEFAULT 1,
    resource_generation_rate DECIMAL(5,2) DEFAULT 0,
    last_captured_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Spatial indexes for performance
CREATE INDEX idx_territories_boundary ON territories USING GIST (boundary_polygon);
CREATE INDEX idx_territories_center ON territories USING GIST (center_point);
CREATE INDEX idx_territorial_events_location ON territorial_events USING GIST (event_location);
CREATE INDEX idx_control_structures_location ON control_structures USING GIST (location);

-- Performance indexes
CREATE INDEX idx_faction_influence_faction_id ON faction_territorial_influence(faction_id);
CREATE INDEX idx_faction_influence_territory_id ON faction_territorial_influence(territory_id);
CREATE INDEX idx_territories_controller ON territories(current_controller_faction_id);
CREATE INDEX idx_territorial_events_territory ON territorial_events(territory_id);
CREATE INDEX idx_territorial_events_time ON territorial_events(started_at);

-- Insert faction data from Factions.csv
INSERT INTO factions (faction_name, discipline, aggression, tech_level, loot_tier_bias, vehicle_affinity, event_preference, palette_hex, emblem_ref, notes) VALUES
('Sky Bastion Directorate', 0.85, 0.55, 0.80, '{"Field":0.7,"Splice":0.25,"Monolith":0.05}', '{"Ground":0.6,"Air":0.2,"Drone":0.2}', '{"ConvoyWar":0.7}', '#161A1D-#2E4053', 'Concepts/Factions/directorate_emblem.png', 'Rationed but reliable'),
('Iron Scavengers', 0.60, 0.70, 0.70, '{"Field":0.5,"Splice":0.4,"Monolith":0.1}', '{"Ground":0.7,"Air":0.1,"Drone":0.2}', '{"Meteor":0.8}', '#7F8C8D-#D35400', 'Concepts/Factions/ironscavengers_emblem.png', 'Theft specialists'),
('The Seventy-Seven', 0.70, 0.65, 0.75, '{"Field":0.6,"Splice":0.35,"Monolith":0.05}', '{"Ground":0.5,"Air":0.3,"Drone":0.2}', '{"Any":0.5}', '#34495E-#BDC3C7', 'Concepts/Factions/free77_emblem.png', 'Contractors'),
('Corporate Hegemony', 0.90, 0.60, 0.90, '{"Field":0.4,"Splice":0.45,"Monolith":0.15}', '{"Air":0.4,"Drone":0.3,"Ground":0.3}', '{"TechVault":0.8}', '#0C0F12-#00C2FF', 'Concepts/Factions/corporatehegemony_emblem.png', 'Brand warfare'),
('Nomad Clans', 0.55, 0.80, 0.65, '{"Field":0.7,"Splice":0.25,"Monolith":0.05}', '{"Ground":0.8,"Air":0.1,"Drone":0.1}', '{"ConvoyWar":0.9}', '#6E2C00-#AF601A', 'Concepts/Factions/nomadclans_emblem.png', 'Mobile adaptation'),
('Archive Keepers', 0.75, 0.50, 0.95, '{"Field":0.3,"Splice":0.5,"Monolith":0.2}', '{"Drone":0.5,"Ground":0.3,"Air":0.2}', '{"DroneSwarm":0.9}', '#2C3E50-#8E44AD', 'Concepts/Factions/archivekeepers_emblem.png', 'Information warfare'),
('Civic Wardens', 0.80, 0.45, 0.70, '{"Field":0.65,"Splice":0.3,"Monolith":0.05}', '{"Ground":0.7,"Drone":0.2,"Air":0.1}', '{"SiegeDefense":0.8}', '#145A32-#27AE60', 'Concepts/Factions/civicwardens_emblem.png', 'Community defense');

-- Insert territory types hierarchy
INSERT INTO territory_types (type_name, hierarchy_level, max_influence_range, control_point_requirement) VALUES
('region', 1, 10000, 1000),
('district', 2, 5000, 500),
('zone', 3, 2000, 200),
('outpost', 4, 500, 50);

-- Example territory data (Metro region from existing lore)
INSERT INTO territories (territory_name, territory_type_id, boundary_polygon, center_point, strategic_value) VALUES
('Metro Region', 1, ST_GeomFromText('POLYGON((-1000 -1000, 1000 -1000, 1000 1000, -1000 1000, -1000 -1000))', 4326), ST_GeomFromText('POINT(0 0)', 4326), 8),
('Maintenance District', 2, ST_GeomFromText('POLYGON((-500 -500, 500 -500, 500 500, -500 500, -500 -500))', 4326), ST_GeomFromText('POINT(0 0)', 4326), 6);

-- Create materialized view for fast territorial queries
CREATE MATERIALIZED VIEW territorial_control_summary AS
SELECT 
    t.id as territory_id,
    t.territory_name,
    t.current_controller_faction_id,
    f.faction_name as controller_name,
    f.palette_hex,
    t.contested,
    COUNT(cs.id) as control_structures_count,
    SUM(CASE WHEN fti.influence_level > 0 THEN 1 ELSE 0 END) as competing_factions_count,
    MAX(fti.influence_level) as max_influence,
    t.strategic_value
FROM territories t
LEFT JOIN factions f ON t.current_controller_faction_id = f.id
LEFT JOIN control_structures cs ON t.id = cs.territory_id
LEFT JOIN faction_territorial_influence fti ON t.id = fti.territory_id
GROUP BY t.id, t.territory_name, t.current_controller_faction_id, f.faction_name, f.palette_hex, t.contested, t.strategic_value;

CREATE UNIQUE INDEX idx_territorial_control_summary_id ON territorial_control_summary (territory_id);

-- Function to refresh territorial control summary
CREATE OR REPLACE FUNCTION refresh_territorial_control_summary()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY territorial_control_summary;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_territories_updated_at BEFORE UPDATE ON territories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_faction_influence_updated_at BEFORE UPDATE ON faction_territorial_influence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();