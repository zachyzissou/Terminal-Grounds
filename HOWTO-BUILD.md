# HOWTO-BUILD

Requirements: Unreal Engine 5.4+, Visual Studio 2022 (Windows) or Xcode (macOS), Clang/LLVM (Linux). GAS plugins enabled.

1) Open TerminalGrounds.uproject. Generate project files if prompted.
2) Build Editor target for your platform. First build will take time.
3) To build Server: build the `TerminalGroundsServer` target (Linux recommended for hosting).

Notes:
- If using Linux Server from Windows, build with a machine/runner that has UE for Linux installed.
- See HOWTO-HOST.md for Docker runtime.
