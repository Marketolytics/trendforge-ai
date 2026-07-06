# Upgrading TrendForge AI

Upgrades are safe: all of your data lives in `%LOCALAPPDATA%\TrendForge AI`,
separate from the installed application, so it is preserved automatically.

## How to upgrade

1. Download the newer `TrendForge-AI-<version>-setup.exe`.
2. Run it. The installer detects the existing installation and upgrades in place.
3. Launch the app. On first run of the new version, any pending database
   migrations are applied automatically.

## What is preserved

- Projects and generated content
- The SQLite database (trends, research, jobs, favorites, history)
- Settings and model routing
- Backups
- The prompt library edits (if you customized `settings\`)

Nothing in `%LOCALAPPDATA%\TrendForge AI` is removed or overwritten by an
upgrade.

## Before a major upgrade (recommended)

Create a backup from **Export Center → Download backup**. To roll back, restore
that `.zip` via **Export Center → Restore**.

## Downgrading

Install the older version, then restore a backup made with that version if the
database schema changed. Migrations are additive and forward-only.
