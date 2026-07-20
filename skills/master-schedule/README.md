# /master-schedule

Connects a product library Google Sheet to the current project. Called automatically by all product skills before reading or writing — if no sheet is configured, it copies the template and writes `master-schedule.json`.

## Usage

```
/master-schedule
```

Runs automatically when any product skill needs sheet access. Can also be invoked manually to view status, reconnect, or reset.

## Setup

1. Duplicate the [master template](https://docs.google.com/spreadsheets/d/1mWnExnSWTKJv0vbu1mDnrQFmv_Iz_fNklIeuBYfMB5k) in Google Drive
2. Share it with your Google service account
3. Run any product skill — `/master-schedule` connects automatically

## Config

Writes `master-schedule.json` to the project root (a legacy `canoa.json` from plugin versions ≤ 1.0.0 is migrated automatically):

```json
{
  "master_sheet_id": "...",
  "sheet_title": "Product Library — Project Name",
  "sheet_url": "https://docs.google.com/spreadsheets/d/...",
  "products_tab": "Products",
  "project_name": "Project Name",
  "created_at": "2026-04-06T00:00:00Z"
}
```

## Requires

- Google Sheets MCP server configured in `~/.claude/mcp_settings.json`
