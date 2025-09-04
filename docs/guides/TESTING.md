# Testing Guide

A quick checklist to validate local changes.

## Smoke tests

- UE Editor opens project without missing modules
- PIE runs a LookDev/Playable map without fatal errors
- Server target builds for Linux (or native platform) without link errors

## Content tests

- DataTables load without warnings
- UI widgets render; no missing textures/materials
- VFX spawn without Niagara warnings

## Networking tests

- Server starts with default `server.yaml`
- Client connects and can move/shoot/ping

