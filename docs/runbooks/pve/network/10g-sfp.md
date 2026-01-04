Runbook: Migrating Proxmox and TrueNAS from 10GBase-T to SFP+ (Omada Core)

1. Environment Context

Hosts

Proxmox VE
- Hostname: pve2
- IP: 192.168.1.26
- OS: Proxmox VE 8.x (Debian 12)
- Kernel: 6.8.12-17-pve

TrueNAS
- Hostname: truenas
- OS: TrueNAS SCALE
- Kernel: 6.12.33-production+truenas

Switching Infrastructure

TP-Link TL-SX3008F
- 8 × SFP+ 10Gb
- Role: Core / aggregation switch

TP-Link TL-SG3210XHP-M2
- 8 × 2.5Gb PoE++
- 2 × SFP+ 10Gb uplinks
- Role: Access switch

TP-Link TL-SG1024
- 24 × 1Gb unmanaged
- Role: Edge / utility only

2. Network Interfaces (Before Migration)

Proxmox

10Gb RJ45 NIC
- Model: Broadcom BCM57810
- PCI: 01:00.0, 01:00.1
- Driver: bnx2x
- Interfaces:
  - enp1s0f0 → 10Gb (vmbr10)
  - enp1s0f1 → 1Gb (vmbr2)

2.5Gb NIC
- Model: Realtek RTL8125
- PCI: 03:00.0
- Interface: enp3s0

TrueNAS

1Gb NIC
- Model: Intel I210
- Interface: eno1

10Gb RJ45 NIC
- Model: Aquantia AQC107
- Interface: eno2

3. Proxmox Bridges (Before Migration)

vmbr0
- Interface: enp3s0
- Mode: DHCP
- Role: LAN

vmbr2
- Interface: enp1s0f1
- Mode: DHCP

vmbr10
- Interface: enp1s0f0
- Mode: Static
- Subnet: 10.10.10.1/24
- Role: Dedicated 10Gb backend

VLANs
- No explicit VLANs
- vmbr10 used as a dedicated backend subnet (10.10.10.0/24)

4. Problem Statement

Goals:
- Replace power-hungry 10GBase-T (RJ45) NICs with SFP+
- Reduce power draw and heat
- Simplify cabling
- Align with Omada SFP+ core switch (TL-SX3008F)
- Maintain existing Proxmox bridge layout
- Ensure compatibility with:
  - Minisforum Proxmox host
  - TrueNAS SCALE
  - TP-Link Omada switching

5. Root Cause (Why Migration Was Needed)

Broadcom BCM57810 (Proxmox)
- High power consumption
- Excess heat
- RJ45 cabling complexity

Aquantia AQC107 (TrueNAS)
- Single-port limitation
- RJ45-only

Network evolution
- Migration to SFP+ core switching (TL-SX3008F)
- Desire for lower power and cleaner topology

6. Final Fix / Known-Good Configuration

Hardware Selection

NICs (Proxmox and TrueNAS)
- Model: Intel X520-DA2
- Ports: Dual SFP+
- PCIe: 2.0 x8
- Driver: ixgbe

Cabling
- 3 × passive SFP+ DAC cables (10GBase-CU)
  - Proxmox → TL-SX3008F
  - TrueNAS → TL-SX3008F
  - TL-SG3210XHP-M2 → TL-SX3008F

Switch Roles

TL-SX3008F
- 10Gb core / aggregation

TL-SG3210XHP-M2
- 2.5Gb PoE access
- 10Gb uplink to core

TL-SG1024
- Optional unmanaged edge

7. Exact Commands and Configuration

Proxmox — Identify NICs

ip -br link
lspci -nn | egrep -i 'ethernet|network'
lspci -nnk -s <PCI-ID>
ethtool <iface>

Proxmox Network Configuration File

File: /etc/network/interfaces

auto lo
iface lo inet loopback

iface enp3s0 inet manual
iface enp1s0f1 inet manual

auto vmbr0
iface vmbr0 inet dhcp
    bridge-ports enp3s0
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware yes

auto vmbr2
iface vmbr2 inet dhcp
    bridge-ports enp1s0f1
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware yes

auto vmbr10
iface vmbr10 inet static
    address 10.10.10.1/24
    bridge-ports enp1s0f0
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware no

After NIC Replacement (Proxmox)

Update only bridge port assignments:

vmbr2  → new_sfp_iface_1
vmbr10 → new_sfp_iface_0

Apply changes:

ifreload -a

TrueNAS — Verify Interfaces

ip -br link
lspci -nn | egrep -i 'ethernet|network'
ethtool <iface>

TrueNAS — Final NIC State

- Aquantia AQC107 removed
- Intel X520-DA2 installed
- ixgbe interface assigned via Web UI:
  Network → Interfaces

8. Verification Steps

Proxmox

ip -br link
ethtool <new_sfp_iface>

Expected:
- Speed: 10000Mb/s
- Link detected: yes

TrueNAS

ethtool <ixgbe_iface>

Expected:
- Speed: 10000Mb/s

Switches

TL-SX3008F
- SFP+ ports show 10Gb links

TL-SG3210XHP-M2
- Uplink SFP+ at 10Gb
- Access ports at 2.5Gb

9. Warnings / Do-Not-Do-Again Notes

DO NOT hot-swap NICs.

DO NOT change Proxmox bridge names.

DO NOT mix RJ45 and SFP+ on the same 10Gb path.

DO NOT update Intel NIC firmware unless required.

Always perform Proxmox NIC changes from console or IPMI, not SSH.

Label DAC cables clearly (server, switch, uplink).

10. Final State Summary

- All servers migrated to SFP+ 10Gb
- Core switching handled by TL-SX3008F
- Access PoE handled by TL-SG3210XHP-M2
- Lower power usage
- Reduced heat
- Cleaner cabling
- Future-proofed network topology
