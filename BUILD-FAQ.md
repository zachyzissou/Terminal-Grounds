# Build FAQ

Common build issues and fixes.

## Unreal can't find module

- Regenerate project files from the `.uproject`
- Ensure module is listed in `*.Build.cs` and included in `*.Target.cs`

## Linker errors (Server)

- Verify third-party libs for target platform are available
- Prefer building LinuxServer on Linux host

## Editor crash on first run

- Clear `DerivedDataCache` and `Intermediate/`
- Regenerate project files and rebuild
