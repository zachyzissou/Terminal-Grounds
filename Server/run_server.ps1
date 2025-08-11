#!/usr/bin/env pwsh
param(
  [int]$Port=7777,
  [int]$QueryPort=27015,
  [string]$ConfigPath="ServerConfig/server.yaml"
)
$exe = Join-Path $PSScriptRoot "..\..\Build\LinuxServer\TerminalGroundsServer.exe"
& $exe -log -unattended -Port=$Port -QueryPort=$QueryPort -Config=$ConfigPath
