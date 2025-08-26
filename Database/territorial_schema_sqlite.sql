-- Terminal Grounds Territorial Control System Database Schema
-- SQLite Version for Immediate Technical Validation
-- CTO Executive Decision: Use SQLite for proof-of-concept, PostgreSQL for production

-- Enable SQLite spatial extension (SpatiaLite when available)
-- Note: For immediate testing, we'll use basic geometric operations

-- Factions table based on existing Factions.csv structure
CREATE TABLE factions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faction_name VARCHAR(100) NOT NULL UNIQUE,
    discipline REAL NOT NULL CHECK (discipline >= 0 AND discipline <= 1),
    aggression REAL NOT NULL CHECK (aggression >= 0 AND aggression <= 1),
    tech_level REAL NOT NULL CHECK (tech_level >= 0 AND tech_level <= 1),
    loot_tier_bias TEXT NOT NULL, -- JSON string: {"field": 0.7, "splice": 0.25, "monolith": 0.05}
    vehicle_affinity TEXT NOT NULL, -- JSON string: {"ground": 0.6, "air": 0.2, "drone": 0.2}
    event_preference TEXT NOT NULL, -- JSON string: {"ConvoyWar": 0.7}
    palette_hex VARCHAR(50) NOT NULL,
    emblem_ref VARCHAR(200),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Territory types for hierarchical control
CREATE TABLE territory_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name VARCHAR(50) NOT NULL UNIQUE, -- region, district, zone, outpost
    hierarchy_level INTEGER NOT NULL, -- 1=region, 2=district, 3=zone, 4=outpost
    max_influence_range INTEGER NOT NULL, -- meters
    control_point_requirement INTEGER NOT NULL, -- points needed for control
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Core territories table with simplified spatial data (for SQLite)
CREATE TABLE territories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    territory_name VARCHAR(100) NOT NULL,
    territory_type_id INTEGER REFERENCES territory_types(id),
    parent_territory_id INTEGER REFERENCES territories(id), -- hierarchical structure
    boundary_points TEXT NOT NULL, -- JSON array of boundary polygon points
    center_x REAL NOT NULL, -- territory center X coordinate
    center_y REAL NOT NULL, -- territory center Y coordinate
    influence_radius REAL NOT NULL, -- influence radius in meters
    control_points INTEGER DEFAULT 0,
    current_controller_faction_id INTEGER REFERENCES factions(id),
    contested BOOLEAN DEFAULT 0,
    last_contested_at DATETIME,
    strategic_value INTEGER DEFAULT 1, -- 1-10 importance scale
    resource_multiplier REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Faction territorial control and influence
CREATE TABLE faction_territorial_influence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faction_id INTEGER REFERENCES factions(id),
    territory_id INTEGER REFERENCES territories(id),
    influence_level INTEGER DEFAULT 0, -- 0-100 influence percentage
    control_points INTEGER DEFAULT 0,
    last_action_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    influence_trend VARCHAR(20) DEFAULT 'stable', -- growing, declining, stable
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(faction_id, territory_id)
);

-- Territorial events and conflicts
CREATE TABLE territorial_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(50) NOT NULL, -- capture, contest, defend, abandon
    territory_id INTEGER REFERENCES territories(id),
    initiating_faction_id INTEGER REFERENCES factions(id),
    defending_faction_id INTEGER REFERENCES factions(id),
    event_location_x REAL NOT NULL,
    event_location_y REAL NOT NULL,
    participants TEXT, -- JSON: player/AI participant data
    outcome VARCHAR(50), -- success, failure, contested
    influence_change INTEGER DEFAULT 0,
    control_points_change INTEGER DEFAULT 0,
    event_duration_seconds INTEGER,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    event_data TEXT -- JSON: additional event-specific data
);

-- Control point structures (bases, outposts, strategic points)
CREATE TABLE control_structures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    structure_name VARCHAR(100) NOT NULL,
    structure_type VARCHAR(50) NOT NULL, -- base, outpost, checkpoint, resource_node
    territory_id INTEGER REFERENCES territories(id),
    controlling_faction_id INTEGER REFERENCES factions(id),
    location_x REAL NOT NULL,
    location_y REAL NOT NULL,
    health INTEGER DEFAULT 100,
    max_health INTEGER DEFAULT 100,
    defensive_strength INTEGER DEFAULT 1,
    resource_generation_rate REAL DEFAULT 0,
    last_captured_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_faction_influence_faction_id ON faction_territorial_influence(faction_id);
CREATE INDEX idx_faction_influence_territory_id ON faction_territorial_influence(territory_id);
CREATE INDEX idx_territories_controller ON territories(current_controller_faction_id);
CREATE INDEX idx_territories_center ON territories(center_x, center_y);
CREATE INDEX idx_territorial_events_territory ON territorial_events(territory_id);
CREATE INDEX idx_territorial_events_time ON territorial_events(started_at);
CREATE INDEX idx_control_structures_location ON control_structures(location_x, location_y);
CREATE INDEX idx_control_structures_territory ON control_structures(territory_id);

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

-- Insert example territory data (Metro region from existing lore)
INSERT INTO territories (territory_name, territory_type_id, boundary_points, center_x, center_y, influence_radius, strategic_value) VALUES
('Metro Region', 1, '[[-2000,-2000],[2000,-2000],[2000,2000],[-2000,2000],[-2000,-2000]]', 0.0, 0.0, 2000.0, 8),
('Maintenance District', 2, '[[-1000,-1000],[1000,-1000],[1000,1000],[-1000,1000],[-1000,-1000]]', 0.0, 0.0, 1000.0, 6),
('Tech Wastes', 1, '[[3000,-2000],[7000,-2000],[7000,2000],[3000,2000],[3000,-2000]]', 5000.0, 0.0, 2000.0, 7),
('IEZ Facility', 2, '[[4000,-1000],[6000,-1000],[6000,1000],[4000,1000],[4000,-1000]]', 5000.0, 0.0, 1000.0, 9);

-- Set initial territorial control (Civic Wardens control Metro, Iron Scavengers control Tech Wastes)
UPDATE territories SET current_controller_faction_id = 7 WHERE territory_name = 'Metro Region'; -- Civic Wardens
UPDATE territories SET current_controller_faction_id = 7 WHERE territory_name = 'Maintenance District'; -- Civic Wardens  
UPDATE territories SET current_controller_faction_id = 2 WHERE territory_name = 'Tech Wastes'; -- Iron Scavengers
UPDATE territories SET current_controller_faction_id = 1 WHERE territory_name = 'IEZ Facility'; -- Sky Bastion Directorate

-- Insert initial faction influence data
INSERT INTO faction_territorial_influence (faction_id, territory_id, influence_level, control_points) VALUES
(7, 1, 85, 850), -- Civic Wardens strong control of Metro Region
(2, 1, 15, 150), -- Iron Scavengers minor presence in Metro Region
(7, 2, 90, 450), -- Civic Wardens dominant in Maintenance District
(2, 3, 75, 600), -- Iron Scavengers control Tech Wastes
(1, 3, 25, 200), -- Sky Bastion Directorate contesting Tech Wastes
(1, 4, 80, 400), -- Sky Bastion Directorate controls IEZ Facility
(4, 4, 20, 100); -- Corporate Hegemony minor presence in IEZ Facility

-- Create view for quick territorial status queries
CREATE VIEW territorial_control_summary AS
SELECT 
    t.id as territory_id,
    t.territory_name,
    t.current_controller_faction_id,
    f.faction_name as controller_name,
    f.palette_hex,
    t.contested,
    COUNT(cs.id) as control_structures_count,
    (SELECT COUNT(*) FROM faction_territorial_influence fti WHERE fti.territory_id = t.id AND fti.influence_level > 0) as competing_factions_count,
    (SELECT MAX(fti.influence_level) FROM faction_territorial_influence fti WHERE fti.territory_id = t.id) as max_influence,
    t.strategic_value,
    t.center_x,
    t.center_y,
    t.influence_radius
FROM territories t
LEFT JOIN factions f ON t.current_controller_faction_id = f.id
LEFT JOIN control_structures cs ON t.id = cs.territory_id
GROUP BY t.id, t.territory_name, t.current_controller_faction_id, f.faction_name, f.palette_hex, t.contested, t.strategic_value, t.center_x, t.center_y, t.influence_radius;

-- Trigger to update timestamps
CREATE TRIGGER update_territories_updated_at 
AFTER UPDATE ON territories
BEGIN
    UPDATE territories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_faction_influence_updated_at 
AFTER UPDATE ON faction_territorial_influence
BEGIN
    UPDATE faction_territorial_influence SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;