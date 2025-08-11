# HOWTO-BUILD

Requirements: Unreal Engine 5.4+, Visual Studio 2022 (Windows) or Xcode (macOS), Clang/LLVM (Linux). GAS plugins enabled.

1) Open TerminalGrounds.uproject. Generate project files if prompted.
2) Build Editor target for your platform. First build will take time.
3) To build Server: build the `TerminalGroundsServer` target (Linux recommended for hosting).

Notes:

- If using Linux Server from Windows, build with a machine/runner that has UE for Linux installed.
- See HOWTO-HOST.md for Docker runtime.

## CI/CD Build System

The project uses GitHub Actions with a self-hosted runner labeled `ue5` for automated builds. The workflow includes a 2-hour timeout to prevent infinite hanging if the runner is unavailable. 

If builds are hanging in "queued" status, check that:
- The self-hosted runner with label `ue5` is online and available
- The runner has Unreal Engine 5.4+ properly installed
- The runner is not busy with other jobs
