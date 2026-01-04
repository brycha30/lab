# OPNsense Upgrade Failure & Recovery Runbook

## Environment
- Platform: OPNsense
- Versions involved: 25.1 → 25.7
- Firewall role: Core gateway

## Problem
Upgrade caused loss of access and service failures.

## Root Cause
Plugin conflicts and partial upgrade state.

## Fix
- Factory reset
- Clean reinstall
- Manual restore of config
- Plugin revalidation

## Verification
- LAN/WAN reachable
- DHCP operational
- Unbound resolving

## Warnings
❌ Do not upgrade without console access
❌ Snapshot configs first
