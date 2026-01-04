OPNsense 25.1 → 25.7 Upgrade Failure & Recovery Runbook

1. Environment Context

Firewall
- Hostname: OPNsense.md.chamberlain.com
- OS: OPNsense 25.7 (amd64)
- Boot disk: NVMe (nda0, 128GB M.2 NVMe)
- Filesystem: UFS on /dev/gpt/rootfs
- Built-in USB devices:
  - microSD card reader (Genesys Logic)
  - USB hub
  - USB keyboard
  - USB fan

Interfaces / IPs
- LAN (igc0): 192.168.1.1/24
- TESTLAN (igc2): 192.168.99.1/24
- WAN (igc1): 73.86.138.91/22 (DHCP4)
- WAN IPv6: 2001:558:6020:17c:98a5:2d1d:9a0b:5d7c/128 (DHCP6)

Access
- GUI: https://192.168.1.1
- GUI (FQDN): https://opnsense.md.chamberlain.com
- Console menu available

Storage Paths
- Config: /conf/config.xml
- EFI partition: /boot/efi/

2. Problem Statement

Upgrade from OPNsense 25.1 to 25.7 failed mid-process, resulting in:
- Boot stopping at shell
- Package upgrades failing with “mangled entry” and flock() errors
- Repeated console update failures (menu option 12)
- Filesystem integrity errors during package extraction

3. Root Cause

UFS filesystem metadata corruption on the root filesystem caused by:
- Interrupted upgrade process
- Unsafe shutdown during package writes

Evidence observed:
- BAD CHECK-HASH
- FREE BLK COUNT(S) WRONG IN SUPERBLK
- SUMMARY INFORMATION BAD
- ALLOCATED FILES MARKED FREE
- FILE SYSTEM WAS MODIFIED

Secondary noise (non-causal):
- da0: NOT READY, Medium not present
- Source: built-in microSD card reader with no card inserted
- This condition is harmless and not a disk failure

4. Final Fix / Known-Good Configuration

Actions performed:
1. Filesystem repaired successfully using fsck
2. System booted cleanly into OPNsense 25.7
3. GUI accessible and services running normally
4. NVMe health verified (no media errors, low wear)
5. Configuration backed up

Known-Good State
- OPNsense 25.7 boots normally
- GUI reachable
- Filesystem marked clean
- No active corruption
- NVMe healthy

5. Exact Commands / Actions Performed

Save Configuration (Immediate Parachute)
Command:
cp /conf/config.xml /boot/efi/config.xml.backup
sync
ls -lh /boot/efi/config.xml.backup

Reboot to Single User & Repair Filesystem
Command:
reboot

At boot menu:
- Choose Single User

Filesystem repair:
fsck -fy /

Reboot after repair:
reboot

Verify Version
Command:
opnsense-version

Disk Identification
Command:
geom disk list
camcontrol devlist

NVMe Health
Command:
nvmecontrol devlist
nvmecontrol logpage -p 2 nvme0
nvmecontrol logpage -p 1 nvme0

USB / da0 Noise Verification
Command:
usbconfig
dmesg | egrep -i "da0|umass|usb mass|medium not present"

6. Verification Steps

- Boot completes without dropping to shell
- GUI loads at https://192.168.1.1
- System → Firmware → Status shows no active upgrade
- System logs show no repeating filesystem or PHP fatal errors
- opnsense-version reports 25.7.x

NVMe Health Expectations
- Media errors: 0
- Available spare: 100
- Percentage used: ap
