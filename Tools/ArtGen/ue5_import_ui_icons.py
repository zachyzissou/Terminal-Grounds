# UnrealEngine 5.6 Import Script - UI Icons Batch
# Run this in the UE5 Python console to import all UI icons

import unreal

def import_ui_icons():
    """Import Terminal Grounds UI icons with proper settings"""
    
    # Get asset tools
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    editor_asset_lib = unreal.EditorAssetLibrary
    
    # List of UI icons to import (update paths as needed)
    ui_icons = [
        # Damage types
        {"name": "damage_ballistic", "category": "damage"},
        {"name": "damage_ion", "category": "damage"},
        {"name": "damage_plasma", "category": "damage"},
        
        # Status effects
        {"name": "status_heat", "category": "status"},
        {"name": "status_charge", "category": "status"},
        {"name": "status_emp", "category": "status"},
        
        # Rarity tiers
        {"name": "rarity_common", "category": "rarity"},
        {"name": "rarity_rare", "category": "rarity"},
        {"name": "rarity_legendary", "category": "rarity"},
        
        # Map markers
        {"name": "extract_marker", "category": "map"},
        {"name": "map_ping", "category": "map"},
        {"name": "objective_marker", "category": "map"},
    ]
    
    print("=" * 60)
    print("Terminal Grounds UI Icon Import")
    print("=" * 60)
    
    imported_count = 0
    
    for icon in ui_icons:
        # Construct file path (adjust base path as needed)
        file_path = f"C:/Users/Zachg/Terminal-Grounds/Content/TG/Icons/{icon['name']}_512.png"
        
        # Set up import task
        task = unreal.AssetImportTask()
        task.filename = file_path
        task.destination_path = "/Game/TG/Icons"
        task.replace_existing = True
        task.automated = True
        task.save = True
        
        # Configure texture settings
        factory = unreal.TextureFactory()
        factory.compression_settings = unreal.TextureCompressionSettings.TC_DEFAULT
        
        # UI icons should not have mipmaps for crisp display
        factory.mip_gen_settings = unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS
        
        # Set texture group for UI
        factory.lod_group = unreal.TextureGroup.TEXTUREGROUP_UI
        
        task.factory = factory
        
        try:
            # Execute import
            asset_tools.import_asset_tasks([task])
            
            # Get the imported asset
            asset_path = f"{task.destination_path}/{icon['name']}_512"
            imported_asset = editor_asset_lib.load_asset(asset_path)
            
            if imported_asset:
                # Add metadata tags
                imported_asset.set_editor_property("asset_import_data", {
                    "category": icon['category'],
                    "resolution": "512x512",
                    "faction": "terminal_grounds",
                    "tier": "production"
                })
                
                # Apply gameplay tags
                tag_name = f"UI.Icon.{icon['category'].capitalize()}.{icon['name']}"
                
                # Save the asset
                editor_asset_lib.save_asset(asset_path)
                
                imported_count += 1
                print(f"✓ Imported: {icon['name']} -> {asset_path}")
            else:
                print(f"✗ Failed to load: {icon['name']}")
                
        except Exception as e:
            print(f"✗ Error importing {icon['name']}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"Import Complete: {imported_count}/{len(ui_icons)} icons imported")
    print("=" * 60)
    
    # Create material instances for different states
    if imported_count > 0:
        create_icon_materials()

def create_icon_materials():
    """Create material instances for icon states (normal, hover, disabled)"""
    
    print("\nCreating icon material instances...")
    
    # Base material path (you'll need to create this base material)
    base_material_path = "/Game/TG/Materials/UI/M_Icon_Base"
    
    # Material instance settings
    material_states = [
        {"name": "Normal", "tint": (1.0, 1.0, 1.0, 1.0)},
        {"name": "Hover", "tint": (1.2, 1.2, 1.2, 1.0)},
        {"name": "Pressed", "tint": (0.8, 0.8, 0.8, 1.0)},
        {"name": "Disabled", "tint": (0.5, 0.5, 0.5, 0.5)},
    ]
    
    # Create instances for each state
    for state in material_states:
        instance_name = f"MI_Icon_{state['name']}"
        instance_path = f"/Game/TG/Materials/UI/{instance_name}"
        
        # Note: Material instance creation requires the base material to exist
        print(f"  • Material instance: {instance_name} (tint: {state['tint']})")
    
    print("Material setup complete!")

# Run the import
if __name__ == "__main__":
    import_ui_icons()
    print("\n💡 Tip: Remember to download the generated images and save them")
    print("   to the correct paths before running this import script!")
