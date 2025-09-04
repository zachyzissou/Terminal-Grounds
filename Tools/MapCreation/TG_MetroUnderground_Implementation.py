#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds - Metro Underground Direct Implementation
Unreal Engine 5.6 Level Creation Script

This script directly implements the Metro Underground level
using Unreal Engine Python API and UnrealMCP integration.

Execute this in Unreal Engine Editor Python console or via UnrealMCP
"""

import unreal
import json
import math

class TGMetroUndergroundImplementation:
    def __init__(self):
        self.level_name = "/Game/Maps/TG_MetroUnderground_Phase1"
        self.world = None
        self.actors = []
        
    def create_level(self):
        """Create new level in Unreal Engine"""
        print("Creating Terminal Grounds Metro Underground Level...")
        
        # Create new level
        level_tool = unreal.EditorLevelUtils()
        self.world = unreal.EditorLevelLibrary.new_level(self.level_name)
        
        if not self.world:
            print("Failed to create level!")
            return False
            
        print(f"Level created: {self.level_name}")
        return True
    
    def create_basic_geometry(self):
        """Create basic level geometry using BSP and static meshes"""
        print("Creating basic level geometry...")
        
        # Main tunnel geometry
        main_tunnel = self.create_tunnel_segment(
            start_pos=(-1800, 0, -200),
            end_pos=(1800, 0, -200),
            width=400,
            height=300,
            name="MainTransitTunnel"
        )
        
        # North service tunnel
        north_tunnel = self.create_tunnel_segment(
            start_pos=(-800, 800, -150),
            end_pos=(800, 1200, -150),
            width=200,
            height=250,
            name="NorthServiceTunnel"
        )
        
        # South maintenance level
        south_tunnel = self.create_tunnel_segment(
            start_pos=(-600, -1000, -300),
            end_pos=(600, -600, -300),
            width=300,
            height=200,
            name="SouthMaintenanceLevel"
        )
        
        # Central access shaft
        self.create_cylindrical_shaft(
            position=(0, 0, -100),
            height=400,
            diameter=150,
            name="CentralAccessShaft"
        )
        
        print("Basic geometry created successfully!")
    
    def create_tunnel_segment(self, start_pos, end_pos, width, height, name):
        """Create a tunnel segment using BSP geometry"""
        
        # Calculate tunnel parameters
        length = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        center_pos = (
            (start_pos[0] + end_pos[0]) / 2,
            (start_pos[1] + end_pos[1]) / 2,
            (start_pos[2] + end_pos[2]) / 2
        )
        
        # Create BSP brush for tunnel
        brush_builder = unreal.CubeBuilder()
        brush_builder.x = length
        brush_builder.y = width
        brush_builder.z = height
        
        # Create the brush actor
        brush_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.Brush,
            location=unreal.Vector(center_pos[0], center_pos[1], center_pos[2])
        )
        
        if brush_actor:
            brush_actor.set_actor_label(f"Tunnel_{name}")
            self.actors.append(brush_actor)
            print(f"Created tunnel: {name}")
        
        return brush_actor
    
    def create_cylindrical_shaft(self, position, height, diameter, name):
        """Create cylindrical access shaft"""
        
        # Use cylinder brush builder
        brush_builder = unreal.CylinderBuilder()
        brush_builder.z = height
        brush_builder.outer_radius = diameter / 2
        brush_builder.inner_radius = 0
        
        # Create the brush actor
        brush_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.Brush,
            location=unreal.Vector(position[0], position[1], position[2])
        )
        
        if brush_actor:
            brush_actor.set_actor_label(f"Shaft_{name}")
            self.actors.append(brush_actor)
            print(f"Created shaft: {name}")
        
        return brush_actor
    
    def create_lighting_system(self):
        """Create atmospheric lighting system"""
        print("Creating lighting system...")
        
        # Primary directional light
        directional_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.DirectionalLight,
            location=unreal.Vector(0, 0, 500),
            rotation=unreal.Rotator(-45, 0, 0)
        )
        
        if directional_light:
            directional_light.set_actor_label("AmbientSurfaceLight")
            # Configure light properties
            light_component = directional_light.get_component_by_class(unreal.DirectionalLightComponent)
            if light_component:
                light_component.set_intensity(0.3)
                light_component.set_light_color(unreal.LinearColor(0.8, 0.9, 1.0))
            
            self.actors.append(directional_light)
            print("Created directional light")
        
        # Emergency lighting system
        emergency_light_positions = [
            (-1600, -150, 50), (-1600, 150, 50),
            (-1200, -150, 50), (-1200, 150, 50),
            (-800, -150, 50), (-800, 150, 50),
            (-400, -150, 50), (-400, 150, 50),
            (0, -150, 50), (0, 150, 50),
            (400, -150, 50), (400, 150, 50),
            (800, -150, 50), (800, 150, 50),
            (1200, -150, 50), (1200, 150, 50),
            (1600, -150, 50), (1600, 150, 50)
        ]
        
        for i, pos in enumerate(emergency_light_positions):
            point_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PointLight,
                location=unreal.Vector(pos[0], pos[1], pos[2])
            )
            
            if point_light:
                point_light.set_actor_label(f"EmergencyLight_{i:02d}")
                light_component = point_light.get_component_by_class(unreal.PointLightComponent)
                if light_component:
                    light_component.set_intensity(800)
                    light_component.set_light_color(unreal.LinearColor(1.0, 0.4, 0.2))
                    light_component.set_attenuation_radius(300)
                
                self.actors.append(point_light)
        
        print(f"Created {len(emergency_light_positions)} emergency lights")
        
        # Work lights
        work_light_positions = [
            (-800, 0, -50, -60, 45),
            (0, 0, 200, -90, 0),
            (800, 0, -50, -60, -45),
            (0, 800, 50, -45, 180),
            (0, -800, -150, -30, 0)
        ]
        
        for i, (x, y, z, pitch, yaw) in enumerate(work_light_positions):
            spot_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.SpotLight,
                location=unreal.Vector(x, y, z),
                rotation=unreal.Rotator(pitch, yaw, 0)
            )
            
            if spot_light:
                spot_light.set_actor_label(f"WorkLight_{i:02d}")
                light_component = spot_light.get_component_by_class(unreal.SpotLightComponent)
                if light_component:
                    light_component.set_intensity(1200)
                    light_component.set_light_color(unreal.LinearColor(0.9, 0.9, 0.8))
                    light_component.set_attenuation_radius(500)
                    light_component.set_outer_cone_angle(45)
                
                self.actors.append(spot_light)
        
        print(f"Created {len(work_light_positions)} work lights")
    
    def create_faction_territories(self):
        """Create faction territorial markers"""
        print("Creating faction territorial markers...")
        
        # Faction territory definitions
        faction_territories = [
            {"name": "Directorate", "pos": (-1200, -200, -100), "color": (0.0, 0.5, 1.0)},
            {"name": "Free77", "pos": (-400, 200, -100), "color": (0.8, 0.8, 0.0)},
            {"name": "Iron_Scavengers", "pos": (400, -200, -100), "color": (1.0, 0.3, 0.0)},
            {"name": "Nomad_Clans", "pos": (1200, 200, -100), "color": (0.5, 1.0, 0.3)},
            {"name": "Neutral", "pos": (0, 800, -50), "color": (0.7, 0.7, 0.7)},
            {"name": "Contested", "pos": (0, -800, -200), "color": (1.0, 0.0, 1.0)}
        ]
        
        for territory in faction_territories:
            # Create faction marker light
            faction_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PointLight,
                location=unreal.Vector(territory["pos"][0], territory["pos"][1], territory["pos"][2])
            )
            
            if faction_light:
                faction_light.set_actor_label(f"FactionMarker_{territory['name']}")
                light_component = faction_light.get_component_by_class(unreal.PointLightComponent)
                if light_component:
                    light_component.set_intensity(600)
                    light_component.set_light_color(unreal.LinearColor(
                        territory["color"][0], 
                        territory["color"][1], 
                        territory["color"][2]
                    ))
                    light_component.set_attenuation_radius(200)
                
                self.actors.append(faction_light)
            
            # Create faction territory marker (static mesh)
            territory_marker = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location=unreal.Vector(
                    territory["pos"][0], 
                    territory["pos"][1], 
                    territory["pos"][2] - 50
                )
            )
            
            if territory_marker:
                territory_marker.set_actor_label(f"Territory_{territory['name']}")
                # Set basic cube mesh
                mesh_component = territory_marker.get_component_by_class(unreal.StaticMeshComponent)
                if mesh_component:
                    cube_mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
                    if cube_mesh:
                        mesh_component.set_static_mesh(cube_mesh)
                        territory_marker.set_actor_scale3d(unreal.Vector(1.0, 1.0, 0.1))
                
                self.actors.append(territory_marker)
        
        print(f"Created {len(faction_territories)} faction territories")
    
    def create_cover_elements(self):
        """Create cover elements throughout the level"""
        print("Creating cover elements...")
        
        # Support columns along main tunnel
        column_positions = []
        for x in range(-1600, 1800, 200):
            column_positions.extend([
                (x, -100, -200),
                (x, 100, -200)
            ])
        
        for i, pos in enumerate(column_positions):
            column = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location=unreal.Vector(pos[0], pos[1], pos[2])
            )
            
            if column:
                column.set_actor_label(f"SupportColumn_{i:02d}")
                mesh_component = column.get_component_by_class(unreal.StaticMeshComponent)
                if mesh_component:
                    cube_mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
                    if cube_mesh:
                        mesh_component.set_static_mesh(cube_mesh)
                        column.set_actor_scale3d(unreal.Vector(0.5, 0.5, 2.8))
                
                self.actors.append(column)
        
        print(f"Created {len(column_positions)} support columns")
        
        # Abandoned metro cars
        metro_car_positions = [
            (-1000, 0, -200),
            (-200, 0, -200),
            (600, 0, -200),
            (1400, 0, -200)
        ]
        
        for i, pos in enumerate(metro_car_positions):
            metro_car = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location=unreal.Vector(pos[0], pos[1], pos[2])
            )
            
            if metro_car:
                metro_car.set_actor_label(f"MetroCar_{i:02d}")
                mesh_component = metro_car.get_component_by_class(unreal.StaticMeshComponent)
                if mesh_component:
                    cube_mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
                    if cube_mesh:
                        mesh_component.set_static_mesh(cube_mesh)
                        metro_car.set_actor_scale3d(unreal.Vector(1.2, 3.0, 1.8))
                
                self.actors.append(metro_car)
        
        print(f"Created {len(metro_car_positions)} metro cars")
    
    def create_spawn_points(self):
        """Create player spawn points"""
        print("Creating spawn points...")
        
        # Team spawn points
        team_alpha_spawns = [
            (-1600, -400, -180, 45),
            (-1600, 400, -180, -45),
            (-1400, 0, -180, 0)
        ]
        
        team_bravo_spawns = [
            (1600, -400, -180, 135),
            (1600, 400, -180, -135),
            (1400, 0, -180, 180)
        ]
        
        # Create Alpha team spawns
        for i, (x, y, z, yaw) in enumerate(team_alpha_spawns):
            spawn_point = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PlayerStart,
                location=unreal.Vector(x, y, z),
                rotation=unreal.Rotator(0, yaw, 0)
            )
            
            if spawn_point:
                spawn_point.set_actor_label(f"TeamAlpha_Spawn_{i:02d}")
                self.actors.append(spawn_point)
        
        # Create Bravo team spawns
        for i, (x, y, z, yaw) in enumerate(team_bravo_spawns):
            spawn_point = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PlayerStart,
                location=unreal.Vector(x, y, z),
                rotation=unreal.Rotator(0, yaw, 0)
            )
            
            if spawn_point:
                spawn_point.set_actor_label(f"TeamBravo_Spawn_{i:02d}")
                self.actors.append(spawn_point)
        
        # Solo spawn points
        solo_spawns = [
            (-800, 600, -130, -90),
            (800, -600, -130, 90),
            (0, 0, 150, 0),
            (-200, 800, -130, -135),
            (200, -800, -280, 45)
        ]
        
        for i, (x, y, z, yaw) in enumerate(solo_spawns):
            spawn_point = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PlayerStart,
                location=unreal.Vector(x, y, z),
                rotation=unreal.Rotator(0, yaw, 0)
            )
            
            if spawn_point:
                spawn_point.set_actor_label(f"Solo_Spawn_{i:02d}")
                self.actors.append(spawn_point)
        
        total_spawns = len(team_alpha_spawns) + len(team_bravo_spawns) + len(solo_spawns)
        print(f"Created {total_spawns} spawn points")
    
    def create_extraction_zones(self):
        """Create extraction zones"""
        print("Creating extraction zones...")
        
        extraction_zones = [
            {"name": "Primary_Central", "pos": (0, 0, 250), "radius": 100},
            {"name": "Secondary_North", "pos": (800, 800, 100), "radius": 80},
            {"name": "Emergency_South", "pos": (-400, -800, -250), "radius": 60}
        ]
        
        for zone in extraction_zones:
            # Create extraction beacon
            beacon = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.StaticMeshActor,
                location=unreal.Vector(zone["pos"][0], zone["pos"][1], zone["pos"][2])
            )
            
            if beacon:
                beacon.set_actor_label(f"ExtractionBeacon_{zone['name']}")
                mesh_component = beacon.get_component_by_class(unreal.StaticMeshComponent)
                if mesh_component:
                    cylinder_mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
                    if cylinder_mesh:
                        mesh_component.set_static_mesh(cylinder_mesh)
                        beacon.set_actor_scale3d(unreal.Vector(
                            zone["radius"]/100, 
                            zone["radius"]/100, 
                            0.1
                        ))
                
                self.actors.append(beacon)
            
            # Create extraction light
            extraction_light = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.PointLight,
                location=unreal.Vector(zone["pos"][0], zone["pos"][1], zone["pos"][2] + 50)
            )
            
            if extraction_light:
                extraction_light.set_actor_label(f"ExtractionLight_{zone['name']}")
                light_component = extraction_light.get_component_by_class(unreal.PointLightComponent)
                if light_component:
                    light_component.set_intensity(1000)
                    light_component.set_light_color(unreal.LinearColor(0.0, 1.0, 0.0))
                    light_component.set_attenuation_radius(zone["radius"] * 2)
                
                self.actors.append(extraction_light)
        
        print(f"Created {len(extraction_zones)} extraction zones")
    
    def setup_navigation_mesh(self):
        """Setup navigation mesh for AI and pathfinding"""
        print("Setting up navigation mesh...")
        
        # Create nav mesh bounds volume
        nav_bounds = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.NavMeshBoundsVolume,
            location=unreal.Vector(0, 0, 0)
        )
        
        if nav_bounds:
            nav_bounds.set_actor_label("MainNavigationBounds")
            # Scale to cover entire level
            nav_bounds.set_actor_scale3d(unreal.Vector(40, 40, 10))
            self.actors.append(nav_bounds)
            print("Created navigation bounds volume")
        
        # Build navigation mesh
        nav_system = unreal.NavigationSystemV1.get_navigation_system(self.world)
        if nav_system:
            nav_system.build()
            print("Navigation mesh build initiated")
    
    def finalize_level(self):
        """Finalize level creation and save"""
        print("Finalizing level...")
        
        # Save level
        if unreal.EditorLevelLibrary.save_current_level():
            print(f"Level saved successfully: {self.level_name}")
        else:
            print("Failed to save level!")
        
        # Generate summary
        print("\n" + "="*60)
        print("TERMINAL GROUNDS METRO UNDERGROUND LEVEL COMPLETE")
        print("="*60)
        print(f"Level Name: {self.level_name}")
        print(f"Total Actors Created: {len(self.actors)}")
        print("\nLevel Features:")
        print("- Multi-level vertical design")
        print("- Faction territorial control system")
        print("- Multiple extraction zones")
        print("- Comprehensive lighting system")
        print("- Tactical cover positioning")
        print("- Balanced spawn point system")
        print("- Navigation mesh support")
        print("\nLevel is ready for gameplay testing!")
        
        return True
    
    def build_complete_level(self):
        """Build the complete Metro Underground level"""
        print("Starting Terminal Grounds Metro Underground level creation...")
        
        if not self.create_level():
            return False
        
        # Create all level elements
        self.create_basic_geometry()
        self.create_lighting_system()
        self.create_faction_territories()
        self.create_cover_elements()
        self.create_spawn_points()
        self.create_extraction_zones()
        self.setup_navigation_mesh()
        
        # Finalize
        return self.finalize_level()

# Execute level creation
def create_terminal_grounds_level():
    """Main execution function"""
    level_creator = TGMetroUndergroundImplementation()
    return level_creator.build_complete_level()

# Run if executed directly
if __name__ == "__main__":
    create_terminal_grounds_level()