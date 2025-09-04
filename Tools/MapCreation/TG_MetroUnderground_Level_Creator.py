#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds - Metro Underground Level Creator
Phase 1 Foundational Playability Level

Map Designer: Level Creation System for Terminal Grounds
Setting: Metro Underground Extraction Zone
Players: 1-8 (scalable)
Performance Target: 60+ FPS

This script creates the foundational playable level for Terminal Grounds
using UnrealMCP integration and AI-generated assets.
"""

import json
import math

class TerminalGroundsLevelCreator:
    def __init__(self):
        self.level_name = "TG_MetroUnderground_Phase1"
        self.level_bounds = {
            'min': {'x': -2000, 'y': -2000, 'z': -500},
            'max': {'x': 2000, 'y': 2000, 'z': 500}
        }
        self.faction_territories = []
        self.spawn_points = []
        self.extraction_points = []
        self.cover_positions = []
        
    def create_level_specification(self):
        """Generate complete level specification for Terminal Grounds Metro Underground"""
        return {
            'level_info': {
                'name': self.level_name,
                'description': 'Metro Underground - Terminal Grounds Phase 1 Playable Level',
                'setting': 'Underground metro tunnel system with faction territorial control',
                'gameplay_modes': ['Extraction', 'Territorial Control', 'Combat'],
                'player_count': '1-8 players',
                'performance_target': '60+ FPS'
            },
            'spatial_design': self.design_spatial_layout(),
            'lighting_specification': self.design_lighting_system(),
            'gameplay_elements': self.design_gameplay_elements(),
            'faction_integration': self.design_faction_territories(),
            'performance_optimization': self.design_performance_features()
        }
    
    def design_spatial_layout(self):
        """Design the spatial layout for Metro Underground level"""
        return {
            'primary_corridors': [
                {
                    'name': 'Main Transit Tunnel',
                    'start': {'x': -1800, 'y': 0, 'z': -200},
                    'end': {'x': 1800, 'y': 0, 'z': -200},
                    'width': 400,
                    'height': 300,
                    'cover_elements': ['Support columns', 'Abandoned metro cars', 'Maintenance equipment']
                },
                {
                    'name': 'North Service Tunnel',
                    'start': {'x': -800, 'y': 800, 'z': -150},
                    'end': {'x': 800, 'y': 1200, 'z': -150},
                    'width': 200,
                    'height': 250,
                    'cover_elements': ['Pipe systems', 'Electrical panels', 'Storage crates']
                },
                {
                    'name': 'South Maintenance Level',
                    'start': {'x': -600, 'y': -1000, 'z': -300},
                    'end': {'x': 600, 'y': -600, 'z': -300},
                    'width': 300,
                    'height': 200,
                    'cover_elements': ['Machinery', 'Ventilation systems', 'Tool storage']
                }
            ],
            'vertical_elements': [
                {
                    'name': 'Central Access Shaft',
                    'position': {'x': 0, 'y': 0, 'z': -100},
                    'height': 400,
                    'diameter': 150,
                    'function': 'Primary vertical movement and sightline control'
                },
                {
                    'name': 'Emergency Exit Stairs',
                    'position': {'x': 800, 'y': 800, 'z': -200},
                    'height': 300,
                    'width': 100,
                    'function': 'Secondary extraction route'
                }
            ],
            'cover_systems': self.generate_cover_positions(),
            'sightline_control': self.design_sightlines()
        }
    
    def generate_cover_positions(self):
        """Generate tactical cover positions throughout the level"""
        cover_positions = []
        
        # Main tunnel cover - Support columns every 200 units
        for x in range(-1600, 1800, 200):
            cover_positions.extend([
                {
                    'type': 'Support Column',
                    'position': {'x': x, 'y': -100, 'z': -200},
                    'dimensions': {'width': 50, 'depth': 50, 'height': 280},
                    'cover_value': 'Full'
                },
                {
                    'type': 'Support Column',
                    'position': {'x': x, 'y': 100, 'z': -200},
                    'dimensions': {'width': 50, 'depth': 50, 'height': 280},
                    'cover_value': 'Full'
                }
            ])
        
        # Abandoned metro cars - Major cover elements
        metro_car_positions = [
            {'x': -1000, 'y': 0, 'z': -200},
            {'x': -200, 'y': 0, 'z': -200},
            {'x': 600, 'y': 0, 'z': -200},
            {'x': 1400, 'y': 0, 'z': -200}
        ]
        
        for pos in metro_car_positions:
            cover_positions.append({
                'type': 'Abandoned Metro Car',
                'position': pos,
                'dimensions': {'width': 120, 'depth': 300, 'height': 180},
                'cover_value': 'Full',
                'interactive': True,
                'faction_control': True
            })
        
        return cover_positions
    
    def design_sightlines(self):
        """Design sightline control for competitive balance"""
        return {
            'long_range_engagements': [
                {
                    'name': 'Main Tunnel Vista',
                    'start': {'x': -1800, 'y': 0, 'z': -150},
                    'end': {'x': 1800, 'y': 0, 'z': -150},
                    'distance': 3600,
                    'cover_breaks': ['Support columns', 'Metro cars'],
                    'tactical_value': 'High - Primary engagement zone'
                }
            ],
            'medium_range_zones': [
                {
                    'name': 'Service Tunnel Crossings',
                    'positions': [
                        {'x': 0, 'y': 400, 'z': -150},
                        {'x': 0, 'y': -400, 'z': -200}
                    ],
                    'engagement_distance': 800,
                    'cover_density': 'Medium'
                }
            ],
            'close_quarters_areas': [
                {
                    'name': 'Central Access Shaft',
                    'position': {'x': 0, 'y': 0, 'z': -100},
                    'radius': 200,
                    'vertical_complexity': True,
                    'tactical_value': 'Critical control point'
                }
            ]
        }
    
    def design_lighting_system(self):
        """Design atmospheric lighting for Metro Underground"""
        return {
            'primary_lighting': [
                {
                    'type': 'Directional Light',
                    'name': 'Ambient Surface Light',
                    'position': {'x': 0, 'y': 0, 'z': 500},
                    'rotation': {'pitch': -45, 'yaw': 0, 'roll': 0},
                    'intensity': 0.3,
                    'color': {'r': 0.8, 'g': 0.9, 'b': 1.0},
                    'function': 'Subtle ambient light suggesting surface access'
                }
            ],
            'atmospheric_lighting': [
                {
                    'type': 'Point Light',
                    'name': 'Emergency Lighting System',
                    'positions': self.generate_emergency_lights(),
                    'intensity': 800,
                    'color': {'r': 1.0, 'g': 0.4, 'b': 0.2},
                    'attenuation_radius': 300,
                    'flicker_effect': True
                },
                {
                    'type': 'Spot Light',
                    'name': 'Maintenance Work Lights',
                    'positions': self.generate_work_lights(),
                    'intensity': 1200,
                    'color': {'r': 0.9, 'g': 0.9, 'b': 0.8},
                    'cone_angle': 45,
                    'attenuation_radius': 500
                }
            ],
            'faction_lighting': [
                {
                    'type': 'Colored Territory Markers',
                    'positions': self.generate_faction_light_positions(),
                    'intensity': 600,
                    'colors': {
                        'Directorate': {'r': 0.0, 'g': 0.5, 'b': 1.0},
                        'Free77': {'r': 0.8, 'g': 0.8, 'b': 0.0},
                        'Iron_Scavengers': {'r': 1.0, 'g': 0.3, 'b': 0.0},
                        'Nomad_Clans': {'r': 0.5, 'g': 1.0, 'b': 0.3}
                    }
                }
            ],
            'mood_settings': {
                'overall_tone': 'Industrial Underground',
                'color_temperature': '3200K (Warm White)',
                'contrast_level': 'High',
                'shadow_quality': 'Medium-High',
                'volumetric_fog': True,
                'atmospheric_particles': 'Dust and steam'
            }
        }
    
    def generate_emergency_lights(self):
        """Generate emergency lighting positions along corridors"""
        positions = []
        
        # Main tunnel emergency lights
        for x in range(-1600, 1800, 400):
            positions.extend([
                {'x': x, 'y': -150, 'z': 50},
                {'x': x, 'y': 150, 'z': 50}
            ])
        
        # Service tunnel emergency lights
        for x in range(-600, 800, 300):
            positions.append({'x': x, 'y': 1000, 'z': 100})
        
        return positions
    
    def generate_work_lights(self):
        """Generate maintenance work light positions"""
        return [
            {'x': -800, 'y': 0, 'z': -50, 'direction': {'pitch': -60, 'yaw': 45}},
            {'x': 0, 'y': 0, 'z': 200, 'direction': {'pitch': -90, 'yaw': 0}},
            {'x': 800, 'y': 0, 'z': -50, 'direction': {'pitch': -60, 'yaw': -45}},
            {'x': 0, 'y': 800, 'z': 50, 'direction': {'pitch': -45, 'yaw': 180}},
            {'x': 0, 'y': -800, 'z': -150, 'direction': {'pitch': -30, 'yaw': 0}}
        ]
    
    def generate_faction_light_positions(self):
        """Generate faction territory marker light positions"""
        return [
            {'x': -1200, 'y': -200, 'z': -100, 'faction': 'Directorate'},
            {'x': -400, 'y': 200, 'z': -100, 'faction': 'Free77'},
            {'x': 400, 'y': -200, 'z': -100, 'faction': 'Iron_Scavengers'},
            {'x': 1200, 'y': 200, 'z': -100, 'faction': 'Nomad_Clans'},
            {'x': 0, 'y': 800, 'z': -50, 'faction': 'Neutral'},
            {'x': 0, 'y': -800, 'z': -200, 'faction': 'Contested'}
        ]
    
    def design_gameplay_elements(self):
        """Design gameplay elements for competitive balance"""
        return {
            'spawn_points': self.generate_spawn_points(),
            'extraction_zones': self.generate_extraction_zones(),
            'control_points': self.generate_control_points(),
            'navigation_mesh': self.design_navigation_system(),
            'interactive_elements': self.design_interactive_elements()
        }
    
    def generate_spawn_points(self):
        """Generate balanced spawn point system"""
        return {
            'team_spawns': [
                {
                    'team': 'Alpha',
                    'positions': [
                        {'x': -1600, 'y': -400, 'z': -180, 'facing': {'yaw': 45}},
                        {'x': -1600, 'y': 400, 'z': -180, 'facing': {'yaw': -45}},
                        {'x': -1400, 'y': 0, 'z': -180, 'facing': {'yaw': 0}}
                    ]
                },
                {
                    'team': 'Bravo',
                    'positions': [
                        {'x': 1600, 'y': -400, 'z': -180, 'facing': {'yaw': 135}},
                        {'x': 1600, 'y': 400, 'z': -180, 'facing': {'yaw': -135}},
                        {'x': 1400, 'y': 0, 'z': -180, 'facing': {'yaw': 180}}
                    ]
                }
            ],
            'solo_spawns': [
                {'x': -800, 'y': 600, 'z': -130, 'facing': {'yaw': -90}},
                {'x': 800, 'y': -600, 'z': -130, 'facing': {'yaw': 90}},
                {'x': 0, 'y': 0, 'z': 150, 'facing': {'yaw': 0}},
                {'x': -200, 'y': 800, 'z': -130, 'facing': {'yaw': -135}},
                {'x': 200, 'y': -800, 'z': -280, 'facing': {'yaw': 45}}
            ]
        }
    
    def generate_extraction_zones(self):
        """Generate extraction zones for different risk/reward levels"""
        return [
            {
                'name': 'Primary Extraction - Central Shaft',
                'position': {'x': 0, 'y': 0, 'z': 250},
                'radius': 100,
                'extraction_time': 30,
                'risk_level': 'High',
                'reward_multiplier': 1.5,
                'visibility': 'High - Central location'
            },
            {
                'name': 'Secondary Extraction - North Exit',
                'position': {'x': 800, 'y': 800, 'z': 100},
                'radius': 80,
                'extraction_time': 45,
                'risk_level': 'Medium',
                'reward_multiplier': 1.0,
                'visibility': 'Medium - Side location'
            },
            {
                'name': 'Emergency Extraction - South Service',
                'position': {'x': -400, 'y': -800, 'z': -250},
                'radius': 60,
                'extraction_time': 60,
                'risk_level': 'Low',
                'reward_multiplier': 0.8,
                'visibility': 'Low - Hidden location'
            }
        ]
    
    def generate_control_points(self):
        """Generate territorial control points for faction warfare"""
        return [
            {
                'name': 'Metro Command Center',
                'position': {'x': 0, 'y': 0, 'z': -180},
                'control_radius': 150,
                'capture_time': 20,
                'strategic_value': 'Critical - Central map control',
                'defensive_positions': 8
            },
            {
                'name': 'North Maintenance Hub',
                'position': {'x': 0, 'y': 800, 'z': -130},
                'control_radius': 100,
                'capture_time': 15,
                'strategic_value': 'High - Controls north approach',
                'defensive_positions': 4
            },
            {
                'name': 'South Power Station',
                'position': {'x': 0, 'y': -800, 'z': -280},
                'control_radius': 120,
                'capture_time': 18,
                'strategic_value': 'High - Controls power and lighting',
                'defensive_positions': 6
            },
            {
                'name': 'West Transit Platform',
                'position': {'x': -800, 'y': 0, 'z': -180},
                'control_radius': 80,
                'capture_time': 12,
                'strategic_value': 'Medium - Flanking route control',
                'defensive_positions': 3
            },
            {
                'name': 'East Transit Platform',
                'position': {'x': 800, 'y': 0, 'z': -180},
                'control_radius': 80,
                'capture_time': 12,
                'strategic_value': 'Medium - Flanking route control',
                'defensive_positions': 3
            }
        ]
    
    def design_navigation_system(self):
        """Design navigation mesh and movement systems"""
        return {
            'walkable_areas': [
                {
                    'name': 'Main Platform Level',
                    'bounds': {'min': {'x': -1800, 'y': -200, 'z': -200}, 'max': {'x': 1800, 'y': 200, 'z': -180}},
                    'slope_limit': 25,
                    'step_height': 30
                },
                {
                    'name': 'Service Tunnel Network',
                    'bounds': {'min': {'x': -800, 'y': 600, 'z': -150}, 'max': {'x': 800, 'y': 1200, 'z': -130}},
                    'slope_limit': 15,
                    'step_height': 20
                },
                {
                    'name': 'Lower Maintenance Level',
                    'bounds': {'min': {'x': -600, 'y': -1000, 'z': -300}, 'max': {'x': 600, 'y': -600, 'z': -280}},
                    'slope_limit': 20,
                    'step_height': 25
                }
            ],
            'vertical_connections': [
                {
                    'name': 'Central Shaft Stairs',
                    'start': {'x': 0, 'y': 0, 'z': -180},
                    'end': {'x': 0, 'y': 0, 'z': 250},
                    'type': 'Spiral Staircase',
                    'width': 120
                },
                {
                    'name': 'North Service Ladder',
                    'start': {'x': 0, 'y': 800, 'z': -130},
                    'end': {'x': 0, 'y': 800, 'z': 100},
                    'type': 'Maintenance Ladder',
                    'width': 60
                },
                {
                    'name': 'South Utility Access',
                    'start': {'x': 0, 'y': -800, 'z': -280},
                    'end': {'x': 0, 'y': -800, 'z': -180},
                    'type': 'Utility Stairs',
                    'width': 80
                }
            ],
            'movement_modifiers': [
                {
                    'area': 'Water hazards',
                    'positions': [{'x': -1200, 'y': -100, 'z': -200}, {'x': 1200, 'y': 100, 'z': -200}],
                    'speed_modifier': 0.7,
                    'effect': 'Reduced movement speed'
                },
                {
                    'area': 'Steam vents',
                    'positions': [{'x': 0, 'y': -600, 'z': -280}],
                    'speed_modifier': 0.8,
                    'effect': 'Reduced visibility and movement'
                }
            ]
        }
    
    def design_interactive_elements(self):
        """Design interactive environmental elements"""
        return [
            {
                'name': 'Power Distribution Panel',
                'position': {'x': 0, 'y': -800, 'z': -250},
                'function': 'Controls lighting zones',
                'interaction_time': 5,
                'cooldown': 60,
                'effect': 'Toggle lighting in controlled area'
            },
            {
                'name': 'Emergency Alarm System',
                'position': {'x': 0, 'y': 0, 'z': -150},
                'function': 'Map-wide audio cue and visibility modifier',
                'interaction_time': 3,
                'cooldown': 120,
                'effect': 'Activates emergency lighting and audio alert'
            },
            {
                'name': 'Security Blast Doors',
                'positions': [
                    {'x': -400, 'y': 0, 'z': -190},
                    {'x': 400, 'y': 0, 'z': -190}
                ],
                'function': 'Temporary area denial',
                'interaction_time': 8,
                'duration': 45,
                'effect': 'Blocks primary tunnel for limited time'
            }
        ]
    
    def design_faction_territories(self):
        """Design faction-specific territorial elements"""
        return {
            'Directorate': {
                'primary_territory': {'x': -1200, 'y': -200, 'z': -100},
                'architectural_style': 'Clean corporate signage, blue lighting, security terminals',
                'defensive_advantages': ['Advanced lighting control', 'Security camera network'],
                'environmental_storytelling': ['Corporate propaganda displays', 'Clean maintenance areas']
            },
            'Free77': {
                'primary_territory': {'x': -400, 'y': 200, 'z': -100},
                'architectural_style': 'Military tactical setup, yellow warning lights, comm equipment',
                'defensive_advantages': ['Tactical positioning', 'Communication relays'],
                'environmental_storytelling': ['Military supply caches', 'Tactical maps']
            },
            'Iron_Scavengers': {
                'primary_territory': {'x': 400, 'y': -200, 'z': -100},
                'architectural_style': 'Improvised barricades, orange warning lights, salvaged materials',
                'defensive_advantages': ['Improvised fortifications', 'Resource caches'],
                'environmental_storytelling': ['Scrap metal barriers', 'Tool workshops']
            },
            'Nomad_Clans': {
                'primary_territory': {'x': 1200, 'y': 200, 'z': -100},
                'architectural_style': 'Mobile structures, green natural lighting, survival equipment',
                'defensive_advantages': ['Adaptable positioning', 'Environmental knowledge'],
                'environmental_storytelling': ['Portable shelters', 'Survival supply caches']
            }
        }
    
    def design_performance_features(self):
        """Design performance optimization features"""
        return {
            'level_of_detail': {
                'high_detail_radius': 500,
                'medium_detail_radius': 1000,
                'low_detail_radius': 2000,
                'culling_distance': 3000
            },
            'occlusion_culling': [
                {'name': 'Main Tunnel Segments', 'positions': [(-1000, 0), (0, 0), (1000, 0)]},
                {'name': 'Service Areas', 'positions': [(0, 800), (0, -800)]}
            ],
            'texture_streaming': {
                'high_res_radius': 300,
                'medium_res_radius': 800,
                'low_res_radius': 1500
            },
            'lighting_optimization': {
                'dynamic_lights': 'Limited to 8 active',
                'shadow_casting': 'Primary lights only',
                'reflection_probes': 'Key locations only'
            },
            'target_performance': {
                'fps_target': 60,
                'frame_time_budget': 16.67,
                'draw_calls_limit': 800,
                'triangle_budget': 150000
            }
        }
    
    def generate_unreal_blueprint_code(self):
        """Generate Unreal Engine Blueprint creation code"""
        blueprint_commands = []
        
        # Level creation commands
        blueprint_commands.append({
            'action': 'create_level',
            'name': self.level_name,
            'template': 'Empty Level'
        })
        
        # Add primary geometry
        geometry_spec = self.create_level_specification()['spatial_design']
        
        for corridor in geometry_spec['primary_corridors']:
            blueprint_commands.append({
                'action': 'create_actor',
                'type': 'StaticMeshActor',
                'mesh': '/Engine/BasicShapes/Cube',
                'transform': {
                    'location': corridor['start'],
                    'scale': {
                        'x': abs(corridor['end']['x'] - corridor['start']['x']) / 100,
                        'y': corridor['width'] / 100,
                        'z': corridor['height'] / 100
                    }
                },
                'name': f"Corridor_{corridor['name'].replace(' ', '_')}"
            })
        
        # Add lighting system
        lighting_spec = geometry_spec.get('lighting_specification', self.design_lighting_system())
        
        for light in lighting_spec['primary_lighting']:
            blueprint_commands.append({
                'action': 'create_actor',
                'type': 'DirectionalLight',
                'transform': {
                    'location': light['position'],
                    'rotation': light['rotation']
                },
                'properties': {
                    'Intensity': light['intensity'],
                    'LightColor': light['color']
                },
                'name': light['name']
            })
        
        return blueprint_commands
    
    def export_level_data(self):
        """Export complete level specification to JSON"""
        level_spec = self.create_level_specification()
        level_spec['unreal_commands'] = self.generate_unreal_blueprint_code()
        
        return json.dumps(level_spec, indent=2)

def main():
    """Create Terminal Grounds Metro Underground Level"""
    print("Terminal Grounds - Phase 1 Level Creator")
    print("Creating Metro Underground Extraction Level")
    print("=" * 60)
    
    level_creator = TerminalGroundsLevelCreator()
    level_data = level_creator.export_level_data()
    
    # Export level specification
    with open('TG_MetroUnderground_Level_Specification.json', 'w') as f:
        f.write(level_data)
    
    print("Level specification created successfully!")
    print(f"Level Name: {level_creator.level_name}")
    print(f"Level Bounds: {level_creator.level_bounds}")
    print("\nKey Features:")
    print("- Multi-level vertical design")
    print("- Faction territorial control points")
    print("- Multiple extraction zones")
    print("- Balanced tactical positioning")
    print("- Performance optimized for 60+ FPS")
    print("\nReady for implementation in Unreal Engine 5.6")

if __name__ == "__main__":
    main()