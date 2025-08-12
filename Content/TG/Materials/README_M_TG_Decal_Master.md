# M_TG_Decal_Master Material Template

This master material should be created in Unreal Engine with the following setup:

## Material Properties
- **Material Domain**: Deferred Decal
- **Blend Mode**: Translucent
- **Decal Blend Mode**: Translucent

## Required Parameters
- **BaseColor** (Texture Parameter): Main decal texture
- **Opacity** (Scalar Parameter): Overall decal opacity (default: 1.0)
- **OpacityMask** (Texture Parameter): Optional opacity mask
- **Roughness** (Scalar Parameter): Surface roughness (default: 0.8)
- **Metallic** (Scalar Parameter): Metallic value (default: 0.0)

## Shader Graph
1. **BaseColor**: Connect Texture Parameter to Material Output Base Color
2. **Opacity**: Multiply texture alpha with Opacity parameter
3. **OpacityMask**: Optional mask for complex opacity shapes
4. **Roughness/Metallic**: Connect scalar parameters to respective outputs

## Usage
This master material will be used to create material instances for:
- Faction logos and emblems
- Propaganda posters
- Environmental decals
- Signage and markings

Material instances will be automatically created by the content pipeline agent.
