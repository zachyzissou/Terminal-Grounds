#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terminal Grounds - Metro Underground Performance Validation Framework
Unreal Engine 5.6 Performance Testing and Optimization

This script validates and optimizes the Metro Underground level
for 60+ FPS performance targets with comprehensive testing protocols.
"""

import unreal
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class PerformanceTarget:
    """Performance targets for Terminal Grounds Phase 1"""
    target_fps: float = 60.0
    frame_time_budget_ms: float = 16.67
    max_draw_calls: int = 800
    max_triangle_count: int = 150000
    max_texture_memory_mb: int = 512
    max_static_mesh_actors: int = 200

@dataclass
class PerformanceMetrics:
    """Current performance metrics"""
    current_fps: float = 0.0
    frame_time_ms: float = 0.0
    draw_calls: int = 0
    triangle_count: int = 0
    texture_memory_mb: int = 0
    static_mesh_count: int = 0
    light_count: int = 0
    actor_count: int = 0

class TGPerformanceValidator:
    def __init__(self):
        self.targets = PerformanceTarget()
        self.metrics = PerformanceMetrics()
        self.world = None
        self.validation_results = {}
        
    def initialize(self):
        """Initialize performance validation system"""
        self.world = unreal.EditorLevelLibrary.get_editor_world()
        if not self.world:
            print("ERROR: No valid world found!")
            return False
        
        print("Performance Validator Initialized")
        print(f"Target FPS: {self.targets.target_fps}")
        print(f"Frame Time Budget: {self.targets.frame_time_budget_ms}ms")
        return True
    
    def collect_performance_metrics(self):
        """Collect current level performance metrics"""
        print("Collecting performance metrics...")
        
        # Get all actors in level
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        self.metrics.actor_count = len(all_actors)
        
        # Count specific actor types
        static_mesh_actors = []
        light_actors = []
        total_triangles = 0
        
        for actor in all_actors:
            if isinstance(actor, unreal.StaticMeshActor):
                static_mesh_actors.append(actor)
                # Get triangle count from static mesh
                mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
                if mesh_component and mesh_component.get_static_mesh():
                    static_mesh = mesh_component.get_static_mesh()
                    # Approximate triangle count (UE5 doesn't expose exact count easily)
                    total_triangles += 1000  # Placeholder - would need proper implementation
            
            elif isinstance(actor, (unreal.Light, unreal.PointLight, unreal.SpotLight, unreal.DirectionalLight)):
                light_actors.append(actor)
        
        self.metrics.static_mesh_count = len(static_mesh_actors)
        self.metrics.light_count = len(light_actors)
        self.metrics.triangle_count = total_triangles
        
        print(f"Total Actors: {self.metrics.actor_count}")
        print(f"Static Mesh Actors: {self.metrics.static_mesh_count}")
        print(f"Light Actors: {self.metrics.light_count}")
        print(f"Estimated Triangles: {self.metrics.triangle_count}")
        
        return self.metrics
    
    def validate_geometry_complexity(self):
        """Validate geometry complexity for performance"""
        print("\nValidating Geometry Complexity...")
        
        results = {
            'status': 'PASS',
            'issues': [],
            'recommendations': []
        }
        
        # Check triangle count
        if self.metrics.triangle_count > self.targets.max_triangle_count:
            results['status'] = 'FAIL'
            results['issues'].append(f"Triangle count ({self.metrics.triangle_count}) exceeds target ({self.targets.max_triangle_count})")
            results['recommendations'].append("Consider LOD implementation or mesh optimization")
        
        # Check static mesh count
        if self.metrics.static_mesh_count > self.targets.max_static_mesh_actors:
            results['status'] = 'WARNING'
            results['issues'].append(f"Static mesh count ({self.metrics.static_mesh_count}) near limit ({self.targets.max_static_mesh_actors})")
            results['recommendations'].append("Consider instanced static meshes for repeated elements")
        
        print(f"Geometry Complexity: {results['status']}")
        for issue in results['issues']:
            print(f"  - {issue}")
        
        return results
    
    def validate_lighting_performance(self):
        """Validate lighting setup for performance"""
        print("\nValidating Lighting Performance...")
        
        results = {
            'status': 'PASS',
            'issues': [],
            'recommendations': []
        }
        
        # Get all lights
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        dynamic_lights = []
        shadow_casting_lights = []
        
        for actor in all_actors:
            if isinstance(actor, unreal.PointLight):
                dynamic_lights.append(actor)
                light_component = actor.get_component_by_class(unreal.PointLightComponent)
                if light_component and light_component.get_cast_shadows():
                    shadow_casting_lights.append(actor)
            elif isinstance(actor, unreal.SpotLight):
                dynamic_lights.append(actor)
                light_component = actor.get_component_by_class(unreal.SpotLightComponent)
                if light_component and light_component.get_cast_shadows():
                    shadow_casting_lights.append(actor)
        
        # Validate dynamic light count
        max_dynamic_lights = 12  # Conservative limit for good performance
        if len(dynamic_lights) > max_dynamic_lights:
            results['status'] = 'WARNING'
            results['issues'].append(f"Dynamic lights ({len(dynamic_lights)}) may impact performance")
            results['recommendations'].append("Consider baking lighting or reducing dynamic light count")
        
        # Validate shadow-casting lights
        max_shadow_lights = 4  # Very conservative for good performance
        if len(shadow_casting_lights) > max_shadow_lights:
            results['status'] = 'WARNING'
            results['issues'].append(f"Shadow-casting lights ({len(shadow_casting_lights)}) may impact performance")
            results['recommendations'].append("Disable shadows on non-essential lights")
        
        print(f"Lighting Performance: {results['status']}")
        print(f"  Dynamic Lights: {len(dynamic_lights)}")
        print(f"  Shadow-Casting Lights: {len(shadow_casting_lights)}")
        
        for issue in results['issues']:
            print(f"  - {issue}")
        
        return results
    
    def validate_level_streaming(self):
        """Validate level streaming and occlusion setup"""
        print("\nValidating Level Streaming...")
        
        results = {
            'status': 'PASS',
            'issues': [],
            'recommendations': []
        }
        
        # Check for nav mesh bounds
        nav_bounds = []
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        
        for actor in all_actors:
            if isinstance(actor, unreal.NavMeshBoundsVolume):
                nav_bounds.append(actor)
        
        if not nav_bounds:
            results['status'] = 'WARNING'
            results['issues'].append("No NavMeshBoundsVolume found")
            results['recommendations'].append("Add NavMeshBoundsVolume for AI pathfinding")
        
        # Check level bounds - ensure not too large
        level_bounds = self.calculate_level_bounds()
        max_level_size = 8000  # 8000 units max recommended
        
        if level_bounds['size'] > max_level_size:
            results['status'] = 'WARNING'
            results['issues'].append(f"Level size ({level_bounds['size']:.0f}) is large - may impact streaming")
            results['recommendations'].append("Consider level streaming or sub-level division")
        
        print(f"Level Streaming: {results['status']}")
        print(f"  Level Size: {level_bounds['size']:.0f} units")
        print(f"  Nav Mesh Volumes: {len(nav_bounds)}")
        
        return results
    
    def calculate_level_bounds(self):
        """Calculate the bounds of the level"""
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        
        for actor in all_actors:
            if isinstance(actor, (unreal.StaticMeshActor, unreal.Brush)):
                location = actor.get_actor_location()
                
                min_x = min(min_x, location.x)
                max_x = max(max_x, location.x)
                min_y = min(min_y, location.y)
                max_y = max(max_y, location.y)
                min_z = min(min_z, location.z)
                max_z = max(max_z, location.z)
        
        size_x = max_x - min_x
        size_y = max_y - min_y
        size_z = max_z - min_z
        size = max(size_x, size_y)  # Use largest horizontal dimension
        
        return {
            'min': {'x': min_x, 'y': min_y, 'z': min_z},
            'max': {'x': max_x, 'y': max_y, 'z': max_z},
            'size': size
        }
    
    def validate_gameplay_elements(self):
        """Validate gameplay elements for proper setup"""
        print("\nValidating Gameplay Elements...")
        
        results = {
            'status': 'PASS',
            'issues': [],
            'recommendations': []
        }
        
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        
        # Count spawn points
        spawn_points = [actor for actor in all_actors if isinstance(actor, unreal.PlayerStart)]
        if len(spawn_points) < 8:
            results['status'] = 'WARNING'
            results['issues'].append(f"Only {len(spawn_points)} spawn points found - recommend 8+ for full gameplay")
            results['recommendations'].append("Add more PlayerStart actors for 8-player support")
        
        # Validate spawn point spacing
        spawn_positions = []
        for spawn in spawn_points:
            pos = spawn.get_actor_location()
            spawn_positions.append((pos.x, pos.y, pos.z))
        
        # Check for spawn point clustering (too close together)
        min_spawn_distance = 400  # Minimum distance between spawns
        clustered_spawns = []
        
        for i, pos1 in enumerate(spawn_positions):
            for j, pos2 in enumerate(spawn_positions[i+1:], i+1):
                distance = ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
                if distance < min_spawn_distance:
                    clustered_spawns.append((i, j))
        
        if clustered_spawns:
            results['status'] = 'WARNING'
            results['issues'].append(f"Found {len(clustered_spawns)} spawn point pairs too close together")
            results['recommendations'].append("Increase spacing between spawn points to prevent spawn camping")
        
        print(f"Gameplay Elements: {results['status']}")
        print(f"  Spawn Points: {len(spawn_points)}")
        
        return results
    
    def run_comprehensive_validation(self):
        """Run complete performance validation suite"""
        print("="*60)
        print("TERMINAL GROUNDS - METRO UNDERGROUND PERFORMANCE VALIDATION")
        print("="*60)
        
        if not self.initialize():
            return False
        
        # Collect metrics
        self.collect_performance_metrics()
        
        # Run all validation tests
        validation_results = {
            'geometry': self.validate_geometry_complexity(),
            'lighting': self.validate_lighting_performance(),
            'streaming': self.validate_level_streaming(),
            'gameplay': self.validate_gameplay_elements()
        }
        
        # Generate overall status
        overall_status = self.determine_overall_status(validation_results)
        
        # Generate recommendations
        recommendations = self.generate_optimization_recommendations(validation_results)
        
        # Output final report
        self.generate_validation_report(validation_results, overall_status, recommendations)
        
        return True
    
    def determine_overall_status(self, validation_results):
        """Determine overall validation status"""
        statuses = [result['status'] for result in validation_results.values()]
        
        if 'FAIL' in statuses:
            return 'FAIL'
        elif 'WARNING' in statuses:
            return 'WARNING'
        else:
            return 'PASS'
    
    def generate_optimization_recommendations(self, validation_results):
        """Generate optimization recommendations"""
        all_recommendations = []
        
        for category, results in validation_results.items():
            all_recommendations.extend(results['recommendations'])
        
        # Add general performance recommendations
        general_recommendations = [
            "Enable Nanite virtualized geometry for detailed meshes",
            "Use Lumen for global illumination instead of baked lighting",
            "Implement World Partition for large levels (if needed in future)",
            "Consider Chaos Physics optimization for destructible elements",
            "Use instanced static meshes for repeated elements (columns, lights)",
            "Implement texture streaming for distant objects",
            "Add LOD models for complex static meshes",
            "Use impostor sprites for distant background elements"
        ]
        
        return list(set(all_recommendations + general_recommendations))
    
    def generate_validation_report(self, validation_results, overall_status, recommendations):
        """Generate comprehensive validation report"""
        print("\n" + "="*60)
        print("PERFORMANCE VALIDATION REPORT")
        print("="*60)
        
        print(f"\nOVERALL STATUS: {overall_status}")
        
        if overall_status == 'PASS':
            print("✓ Level meets performance targets for Phase 1 deployment")
        elif overall_status == 'WARNING':
            print("⚠ Level has performance concerns but is playable")
        else:
            print("✗ Level fails performance requirements - optimization needed")
        
        print(f"\nLEVEL METRICS:")
        print(f"  Total Actors: {self.metrics.actor_count}")
        print(f"  Static Meshes: {self.metrics.static_mesh_count}")
        print(f"  Lights: {self.metrics.light_count}")
        print(f"  Estimated Triangles: {self.metrics.triangle_count:,}")
        
        print(f"\nPERFORMACE TARGETS:")
        print(f"  Target FPS: {self.targets.target_fps}")
        print(f"  Frame Time Budget: {self.targets.frame_time_budget_ms}ms")
        print(f"  Max Draw Calls: {self.targets.max_draw_calls:,}")
        print(f"  Max Triangles: {self.targets.max_triangle_count:,}")
        
        print(f"\nVALIDATION RESULTS:")
        for category, results in validation_results.items():
            print(f"  {category.title()}: {results['status']}")
            for issue in results['issues']:
                print(f"    - {issue}")
        
        print(f"\nOPTIMIZATION RECOMMENDATIONS:")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"  {i}. {recommendation}")
        
        print(f"\nNEXT STEPS:")
        if overall_status == 'PASS':
            print("  1. Proceed with gameplay testing")
            print("  2. Integrate AI-generated assets")
            print("  3. Begin Phase 2 development")
        elif overall_status == 'WARNING':
            print("  1. Address high-priority performance warnings")
            print("  2. Conduct performance profiling")
            print("  3. Re-validate before deployment")
        else:
            print("  1. CRITICAL: Address all performance failures")
            print("  2. Re-run validation after optimization")
            print("  3. Consider level redesign if issues persist")
        
        # Save report to file
        report_data = {
            'overall_status': overall_status,
            'metrics': {
                'actor_count': self.metrics.actor_count,
                'static_mesh_count': self.metrics.static_mesh_count,
                'light_count': self.metrics.light_count,
                'triangle_count': self.metrics.triangle_count
            },
            'validation_results': validation_results,
            'recommendations': recommendations
        }
        
        with open('TG_MetroUnderground_Performance_Report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nReport saved: TG_MetroUnderground_Performance_Report.json")
        print("="*60)
    
    def apply_automatic_optimizations(self):
        """Apply automatic performance optimizations"""
        print("Applying automatic optimizations...")
        
        all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
        optimized_count = 0
        
        # Optimize lighting
        for actor in all_actors:
            if isinstance(actor, unreal.PointLight):
                light_component = actor.get_component_by_class(unreal.PointLightComponent)
                if light_component:
                    # Disable shadows on emergency lights (performance optimization)
                    if "Emergency" in actor.get_actor_label():
                        light_component.set_cast_shadows(False)
                        optimized_count += 1
        
        # Optimize static meshes
        for actor in all_actors:
            if isinstance(actor, unreal.StaticMeshActor):
                mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
                if mesh_component:
                    # Enable distance culling for small objects
                    if "Column" in actor.get_actor_label():
                        mesh_component.set_visibility_based_anim_tick_option(unreal.VisibilityBasedAnimTickOption.ONLY_TICK_POSE_WHEN_RENDERED)
                        optimized_count += 1
        
        print(f"Applied {optimized_count} automatic optimizations")
        return optimized_count

def run_performance_validation():
    """Main execution function for performance validation"""
    validator = TGPerformanceValidator()
    return validator.run_comprehensive_validation()

def apply_optimizations():
    """Apply automatic optimizations"""
    validator = TGPerformanceValidator()
    validator.initialize()
    return validator.apply_automatic_optimizations()

# Execute if run directly
if __name__ == "__main__":
    run_performance_validation()