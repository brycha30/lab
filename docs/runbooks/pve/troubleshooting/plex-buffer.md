Plex Buffering & Network Remediation Runbook

1. Environment Context

Hosts & Hypervisor

Proxmox VE Host
- Hostname: pve2
- Storage path for CT disks:
/mnt/ext/images/

LXC Container (Plex)
- VMID: 1034
- Hostname: plex
- OS: Ubuntu 22.04
- IP: 192.168.1.34
- Root filesystem device: /dev/loop1
- Rootfs mount on host:
/var/lib/lxc/1034/rootfs

Plex Data Paths
- Plex application data:
/var/lib/plexmediaserver/Library/Application Support/Plex Media Server

TrueNAS
- IP: 192.168.1.50
- SMB share used by Plex:
//10.10.10.2/Main (historical)
- Migration under consideration:
//192.168.1.50/Main

Firewall / Router
- Platform: OPNsense 25.7
- Hostname: OPNsense.md.chamberlain.com
- LAN (igc0): 192.168.1.1/24
- TESTLAN (igc2): 192.168.99.1/24
- WAN (igc1): DHCP (Comcast)
- DHCP: ISC dhcpd
- DNS: Unbound

Network
- All Plex clients hardwired (Samsung TV, Roku, PCs)
- Default route inside Plex container:
default via 192.168.1.1 dev eth0

- A direct 10Gb subnet between Proxmox and TrueNAS (10.10.10.0/24)
  was previously introduced and later suspected as a contributing factor

2. Problem Statement

- Plex buffers or pauses after approximately 10 seconds
- Observed across multiple clients:
  - Samsung TV
  - Roku
  - PCs
- Issue appeared suddenly after software upgrades and network changes
- No buffering issues historically (stable since approximately 2013)
- Not device-specific

Initial suspects included:
- Storage performance
- CPU utilization
- Disk space exhaustion

3. Root Cause

Primary contributing factors identified:

- Undersized Plex container root filesystem
- Plex transcode cache filled container disk
- Unbounded growth of Plex transcode sessions
- Cache, transcode, and session directories grew to multiple gigabytes

Secondary contributing factors:

- Introduction of direct 10Gb subnet without routing clarity
- Potential SMB path and routing asymmetry
- Accumulated configuration drift over time

Explicitly ruled out:
- Hardware failure
- Client-side playback issues
- CPU or RAM exhaustion

4. Final Fix / Known-Good Configuration

4.1 Expand Plex LXC Disk (Online, No Plex Shutdown)

Target size: 200 GB

Commands executed on Proxmox host (pve2):

losetup -a | grep vm-1034-disk-0.raw
losetup -c /dev/loop1
resize2fs /dev/loop1

Result verified inside container:

df -h /
# /dev/loop1 approximately 197G total

4.2 Clean Plex Transcode Cache

Executed from Proxmox host:

pct exec 1034 -- bash -lc '
rm -rf "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Cache/Transcode/Sessions"/*
'

4.3 Enforce Automatic Transcode Cleanup (systemd-tmpfiles)

Config file created:

/etc/tmpfiles.d/plex-transcode.conf

Contents:

# Prevent unbounded Plex transcode session growth
# Type Path Mode UID GID Age Argument
d "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Cache/Transcode/Sessions" 0755 plex plex -
e "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Cache/Transcode/Sessions" - - - 2d -

Apply cleanup immediately:

systemd-tmpfiles --clean /etc/tmpfiles.d/plex-transcode.conf

Verify timer:

systemctl status systemd-tmpfiles-clean.timer
systemctl list-timers | grep tmpfiles

4.4 OPNsense CLI Audit (Baseline)

Verified via firewall shell:

ifconfig
netstat -rn
ps auxww | egrep 'dhcpd|unbound|ntpd'

Confirmed:
- Single default route via WAN
- DHCP active on igc0 and igc2
- No routing loops
- Unbound healthy

5. Verification Steps

Disk & Filesystem
pct exec 1034 -- df -h /

Transcode Cache Size
pct exec 1034 -- du -sh \
"/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Cache/Transcode"

Network Path
pct exec 1034 -- ip route

Playback Testing
- Test identical media on:
  - Samsung TV
  - Roku
  - PC browser
- Observe for:
  - Initial playback delay
  - Mid-stream buffering
  - Transcode spikes

6. Warnings / Do Not Do This Again

DO NOT leave Plex transcode directories unbounded.

DO NOT introduce direct subnets (10Gb links) without:
- Clear routing plan
- Consistent SMB mount paths

DO NOT resize LXC disks without confirming loop device usage.

AVOID mixing storage IP paths (10.10.10.x vs 192.168.1.x).

DO NOT rely on UI-only changes for firewall or network debugging.

7. Notes

- Fresh Plex install may still be considered if buffering persists,
  but no hard evidence of Plex database corruption was found.
- Next logical test step (if required):
  - Temporarily mount SMB via //192.168.1.50/Main
  - Remove direct 10Gb subnet from Plex data path for validation
