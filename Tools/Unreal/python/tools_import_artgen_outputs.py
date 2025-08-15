"""
Unreal Engine 5.6 Asset Import Script for Terminal Grounds
Imports generated art assets and sets up materials/settings
"""
import unreal
import os
import json
from pathlib import Path
from datetime import datetime


class TGAssetImporter:
    def __init__(self):
        self.editor_asset_lib = unreal.EditorAssetLibrary
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        self.project_root = Path(r"C:\Users\Zachg\Terminal-Grounds")
        self.log_path = self.project_root / "Docs" / "Phase4_Implementation_Log.md"
        
        # Import mappings
        self.import_mappings = {
            "Content/TG/Decals/Factions": "/Game/TG/Decals/Factions",
            "Content/TG/Decals/Posters": "/Game/TG/Decals/Posters",
            "Content/TG/Icons": "/Game/TG/Icons",
            "Docs/Concepts/Posters": "/Game/TG/Decals/Posters",
            "Docs/Concepts/Renders": "/Game/TG/Concepts/Keyframes",
            "Docs/Concepts/AI/Weapons": "/Game/TG/Concepts/Weapons",
            "Docs/Concepts/AI/Vehicles": "/Game/TG/Concepts/Vehicles",
            "Docs/Concepts/AI/Characters": "/Game/TG/Concepts/Characters"
        }
        
        # Material instances tracker
        self.created_materials = []
        
    def log_import(self, message):
        """Log import action"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, 'a') as f:
            f.write(f"\n[{timestamp}] [UE IMPORT] {message}")
        unreal.log(message)
    
    def import_texture(self, source_path, destination_path):
        """Import a single texture asset"""
        # Set up import task
        task = unreal.AssetImportTask()
        task.filename = str(source_path)
        task.destination_path = destination_path
        task.destination_name = source_path.stem
        task.replace_existing = False
        task.automated = True
        task.save = True
        
        # Configure texture import options
        task.options = unreal.FbxImportUI()
        
        # Execute import
        self.asset_tools.import_asset_tasks([task])
        
        # Get imported asset
        asset_path = f"{destination_path}/{source_path.stem}"
        texture = self.editor_asset_lib.load_asset(asset_path)
        
        return texture
    
    def configure_icon_texture(self, texture):
        """Configure texture settings for UI icons"""
        if not texture:
            return
            
        # Set compression and LOD settings for icons
        texture.compression_settings = unreal.TextureCompressionSettings.TC_EDITOR_ICON
        texture.lod_group = unreal.TextureGroup.TEXTUREGROUP_UI
        texture.srgb = True
        texture.never_stream = True
        
        # No mipmaps for UI
        texture.mip_gen_settings = unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS
        
        # Save changes
        self.editor_asset_lib.save_asset(texture.get_path_name())
    
    def configure_decal_texture(self, texture):
        """Configure texture settings for decals"""
        if not texture:
            return
            
        # Decal-appropriate settings
        texture.compression_settings = unreal.TextureCompressionSettings.TC_DEFAULT
        texture.lod_group = unreal.TextureGroup.TEXTUREGROUP_WORLD
        texture.srgb = True
        
        # Save changes
        self.editor_asset_lib.save_asset(texture.get_path_name())
    
    def create_decal_material_instance(self, texture, base_path):
        """Create material instance for decal"""
        # Load master material
        master_mat_path = "/Game/TG/Materials/M_TG_Decal_Master"
        master_mat = self.editor_asset_lib.load_asset(master_mat_path)
        
        if not master_mat:
            unreal.log_warning(f"Master material not found: {master_mat_path}")
            return None
        
        # Create material instance
        mi_name = f"MI_TG_Decal_{texture.get_name()}"
        mi_path = f"{base_path}/{mi_name}"
        
        # Check if already exists
        if self.editor_asset_lib.does_asset_exist(mi_path):
            return self.editor_asset_lib.load_asset(mi_path)
        
        # Create new instance
        factory = unreal.MaterialInstanceConstantFactoryNew()
        factory.parent = master_mat
        
        mi_asset = self.asset_tools.create_asset(
            asset_name=mi_name,
            package_path=base_path,
            asset_class=unreal.MaterialInstanceConstant,
            factory=factory
        )
        
        if mi_asset:
            # Set texture parameter
            mi_asset.set_texture_parameter_value("BaseTexture", texture)
            
            # Set default values
            mi_asset.set_scalar_parameter_value("Opacity", 0.9)
            mi_asset.set_scalar_parameter_value("Roughness", 0.6)
            
            # For faction emblems, set appropriate tint
            if "dir" in texture.get_name().lower():
                mi_asset.set_vector_parameter_value("Tint", unreal.LinearColor(0.086, 0.102, 0.114, 1.0))
            elif "vlt" in texture.get_name().lower():
                mi_asset.set_vector_parameter_value("Tint", unreal.LinearColor(0.498, 0.549, 0.553, 1.0))
            
            # Save
            self.editor_asset_lib.save_asset(mi_asset.get_path_name())
            self.created_materials.append(mi_path)
            
        return mi_asset
    
    def scan_for_new_assets(self, source_dir):
        """Scan directory for assets to import"""
        source_path = self.project_root / source_dir
        if not source_path.exists():
            return []
        
        assets_to_import = []
        extensions = ['.png', '.jpg', '.jpeg', '.tga']
        
        for ext in extensions:
            for file_path in source_path.glob(f"*{ext}"):
                # Skip if has metadata indicating already imported
                meta_path = file_path.with_suffix('.json')
                if meta_path.exists():
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                        if meta.get('imported_to_ue', False):
                            continue
                
                assets_to_import.append(file_path)
        
        return assets_to_import
    
    def import_directory(self, source_dir, destination_path):
        """Import all assets from a directory"""
        assets = self.scan_for_new_assets(source_dir)
        
        if not assets:
            unreal.log(f"No new assets to import from {source_dir}")
            return []
        
        imported = []
        
        for asset_path in assets:
            unreal.log(f"Importing: {asset_path.name}")
            
            # Import texture
            texture = self.import_texture(asset_path, destination_path)
            
            if texture:
                # Configure based on type
                if "icon" in source_dir.lower() or "icons" in destination_path.lower():
                    self.configure_icon_texture(texture)
                elif "decal" in source_dir.lower() or "decals" in destination_path.lower():
                    self.configure_decal_texture(texture)
                    
                    # Create material instance for decals
                    if "faction" in asset_path.stem.lower() or "emblem" in asset_path.stem.lower():
                        self.create_decal_material_instance(texture, destination_path)
                
                imported.append({
                    'source': str(asset_path),
                    'destination': texture.get_path_name()
                })
                
                # Update metadata
                meta_path = asset_path.with_suffix('.json')
                if meta_path.exists():
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                    meta['imported_to_ue'] = True
                    meta['ue_asset_path'] = texture.get_path_name()
                    meta['import_date'] = datetime.now().isoformat()
                    with open(meta_path, 'w') as f:
                        json.dump(meta, f, indent=2)
        
        return imported
    
    def run_full_import(self):
        """Run import for all configured directories"""
        unreal.log("=" * 60)
        unreal.log("Terminal Grounds Asset Import - Starting")
        unreal.log("=" * 60)
        
        total_imported = 0
        
        for source_dir, dest_path in self.import_mappings.items():
            unreal.log(f"\nProcessing: {source_dir} -> {dest_path}")
            
            imported = self.import_directory(source_dir, dest_path)
            total_imported += len(imported)
            
            if imported:
                self.log_import(f"Imported {len(imported)} assets from {source_dir}")
                for item in imported:
                    unreal.log(f"  ✓ {Path(item['source']).name} -> {item['destination']}")
        
        # Summary
        unreal.log("\n" + "=" * 60)
        unreal.log(f"Import Complete: {total_imported} assets imported")
        if self.created_materials:
            unreal.log(f"Created {len(self.created_materials)} material instances")
        unreal.log("=" * 60)
        
        self.log_import(f"Import batch complete: {total_imported} assets, {len(self.created_materials)} materials")
        
        return total_imported
    
    def create_icon_preview_widget(self):
        """Create a UMG widget to preview all icons"""
        # This would create a blueprint widget for icon preview
        # Blueprint creation through Python is limited, so we log the instruction
        
        unreal.log("\n📋 Icon Preview Widget Instructions:")
        unreal.log("1. Create new Widget Blueprint: WBP_TG_IconPreview")
        unreal.log("2. Add UniformGridPanel")
        unreal.log("3. Use Python or Blueprint to populate with imported icons")
        unreal.log(f"4. Icon assets are in: /Game/TG/Icons")
    
    def place_decals_in_test_level(self):
        """Place decals in test level for review"""
        # Get current level
        level = unreal.EditorLevelLibrary.get_editor_world()
        if not level:
            unreal.log_warning("No level loaded")
            return
        
        # Starting position for decal placement
        x_pos = 0.0
        y_pos = 0.0
        spacing = 500.0
        
        decal_materials = [path for path in self.created_materials if "decal" in path.lower()]
        
        for i, mat_path in enumerate(decal_materials):
            # Load material
            material = self.editor_asset_lib.load_asset(mat_path)
            if not material:
                continue
            
            # Spawn decal actor
            decal_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                unreal.DecalActor,
                location=unreal.Vector(x_pos, y_pos, 100.0),
                rotation=unreal.Rotator(0, 0, 0)
            )
            
            if decal_actor:
                # Set material
                decal_component = decal_actor.get_component_by_class(unreal.DecalComponent)
                if decal_component:
                    decal_component.set_decal_material(material)
                    decal_component.decal_size = unreal.Vector(128, 256, 256)
                
                # Update position for next decal
                x_pos += spacing
                if (i + 1) % 5 == 0:  # New row every 5 decals
                    x_pos = 0
                    y_pos += spacing
        
        unreal.log(f"Placed {len(decal_materials)} decals in test level")


def main():
    """Main import function"""
    importer = TGAssetImporter()
    
    # Run full import
    total = importer.run_full_import()
    
    if total > 0:
        # Create preview helpers
        importer.create_icon_preview_widget()
        
        # Place decals if any were created
        if importer.created_materials:
            importer.place_decals_in_test_level()
    
    return total


# Execute if running in Unreal
if __name__ == '__main__':
    main()
