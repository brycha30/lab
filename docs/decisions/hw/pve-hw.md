# Proxmox Hardware Decisions

## System
- Host: pve2
- Platform: Minisforum BD795M / DeskMini Series
- CPU: AMD Ryzen 9 7945HX
- Memory: 64GB DDR5

## Problem
- Existing SATA SSDs in Proxmox ZFS rpool showed errors and instability
- ZFS reported checksum / corruption issues
- Reliability risk to host OS and VM storage

## Decision
- Replace SATA SSDs with NVMe M.2 drives
- Rebuild Proxmox rpool as a mirrored ZFS pool on NVMe

## Hardware Selected
- Model: WD_BLACK SN850X
- Capacity: 2TB each
- Quantity: 2
- Interface: PCIe Gen4 NVMe
- Form factor: M.2 2280

## Rationale
- NVMe provides higher throughput and lower latency than SATA
- Mirrored ZFS rpool improves redundancy and recovery
- WD SN850X has strong endurance and good Linux compatibility
- Drives were available quickly and under budget constraints

## Implementation Notes
- Both drives should be identical model and size
- Use ZFS mirror for rpool
- Avoid mixing SATA and NVMe in rpool
- Verify SMART and ZFS health after rebuild

## Verification
- Confirm both NVMe drives visible in Proxmox
- Verify rpool status shows mirror online
- Monitor ZFS and SMART for errors

## Status
- Drives purchased
- Delivery expected early January
