# HOWTO-BUILD

Requirements: Unreal Engine 5.4+, Visual Studio 2022 (Windows) or Xcode (macOS), Clang/LLVM (Linux). GAS plugins enabled.

1) Open TerminalGrounds.uproject. Generate project files if prompted.
2) Build Editor target for your platform. First build will take time.
3) To build Server: build the `TerminalGroundsServer` target (Linux recommended for hosting).

Notes:

- If using Linux Server from Windows, build with a machine/runner that has UE for Linux installed.
- See HOWTO-HOST.md for Docker runtime.

## Platform specifics

### Windows (recommended for Editor)

- Install Visual Studio 2022 with: Desktop development with C++, MSVC v143, Windows 10/11 SDK, C++ CMake tools.
- Right-click `TerminalGrounds.uproject` > Generate Visual Studio project files.
- Open the generated solution and build the Editor target first.

### Linux (native)

- Ensure Clang/LLVM and clang-tools are installed per UE docs.
- Generate project files with Unreal's Linux toolchain; build Editor/Server targets as needed.

### Cross-building Linux Server from Windows

- Use a machine/runner that has UE for Linux installed or a CI with a Linux agent.
- Recommended: Build LinuxServer on a Linux host for simplicity and fewer toolchain issues.

## Common errors

- Missing Modules/Plugins: Verify `*.Build.cs` dependencies and regenerate project files.
- Linker errors on Server target: Ensure third-party libs are available for the target platform.
- Editor fails on first run: Delete `DerivedDataCache` and `Intermediate/`, regenerate, and rebuild.

