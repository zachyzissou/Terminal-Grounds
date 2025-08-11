# UE5 Placeholder Mesh Directory Structure

## Content/TG/Blockouts/

This directory contains blockout meshes for scale testing and rapid prototyping.

### Weapons/
- Human tier: Simple box shapes with proper grip and barrel proportions
- Hybrid tier: Base shapes with glowing element placeholders  
- Alien tier: Organic curves using spline-based geometry

### Vehicles/
- APC_8x8: 8-wheel vehicle chassis with turret mount points
- Scout_Helo: Basic helicopter shape with rotor placeholders
- Logistics_Truck: Box truck with cargo bay and cab separation
- UAV_Drones: Small flying platforms with attachment points

### Bases/
- Reactor: Industrial building with cooling towers
- Shield_Generator: Compact facility with energy field emitters
- Drone_Bay: Hangar structure with launch rails
- Vehicle_Garage: Large garage with repair bay

### POIs/
- Meteor_Site: Crater with debris scatter
- Drone_Hive: Multi-story building with launch bays
- Vault_Perimeter: Fortified checkpoint structure
- Combine_Pad: Helipad with corporate facilities

### Guidelines:
- All meshes use basic materials (Material_Concrete, Material_Metal, Material_Glow)
- Correct real-world scale for gameplay testing
- Modular components where appropriate
- Performance optimized for rapid iteration
- Collision meshes included for all interactive elements

### Naming Convention:
- BM_[Category]_[Item]_[LOD]
- Example: BM_Weapon_AR_MK2_LOD0
- Example: BM_Vehicle_APC_8x8_LOD0
- Example: BM_Base_Reactor_LOD0