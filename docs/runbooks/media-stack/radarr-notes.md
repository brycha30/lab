# Radarr media workflow

Verified November 26, 2026. Docker VM 1033 (`dkr`, 192.168.1.33) runs regular Radarr on port 7878, Radarr Kids on 7879, and Radarr Directors on 7880. Configuration lives under `/opt/dkr/config/radarr*`; Compose is `/opt/dkr/stack/docker-compose.yml`.

| Library | Container path | Host path |
| --- | --- | --- |
| Movies | `/Main/media/movies` | `/mnt/Main/media/movies` |
| Kids | `/KidsMain/media/kidsmovies` | `/mnt/Main/media/kidsmovies` |
| Directors | `/DirMain/media/movies-directors` | `/mnt/Main/media/movies-directors` |

qBittorrent and all Radarr instances mount the same TrueNAS filesystem. Import completed downloads through Radarr. Verify hardlinks by comparing device, inode, and link count between download and library paths; moving between filesystems makes a copy. The user likes YTS/YIFY releases, so do not block those release groups categorically.

Radarr selects one primary file per movie. Extra files left in the folder appear as Plex duplicates. Compare files with all three Radarr databases before cleanup, check editions and audio, and retain the tracked file. On November 26, 70 untracked regular movie files and 43 kids movie files were removed after checking tracked counterparts. Two further untracked TrueHD Atmos 4K copies of *The Dark Tower* and *Captain Marvel* were removed after Radarr metadata verified the retained 4K HEVC files each have six-channel AC3 audio. Cleanup manifests are under `/opt/dkr/config/*duplicate-cleanup-2026-11-26.json` and `/opt/dkr/config/roku-4k-duplicate-cleanup-2026-11-26.json`.

Roku does not support Dolby TrueHD from local files. For Roku direct play, prefer compatible AC3 or EAC3 audio, HEVC where the actual model supports it, and text subtitles. Test the client and sound system before broad quality-profile changes. Use Radarr quality profiles and custom formats for future replacements, then let Radarr import and replace the selected file.
