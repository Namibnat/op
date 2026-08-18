# Personal Operations Planner

A tool that combines personal project management through a GTD style system
with routines and habit tracking and other miscellaneous tracking for things like
finances.

## Features

- A GTD style app, with a slight modification where projects have tickets rather than next items.
- A personal habit tracking app
- A daily dashboard in the terminal
- Somewhat of a calendar overview.

## Requirements

This project requires python 3.12+

## Installation

```
git clone git@github.com:Namibnat/op.git
cd op

python3 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

## Configuration

Provide a local `OP_DATA_DIR` in your .env with the path to where you want your data
files to live.  This project doesn't use any database at all, simply JSON text files.

`.env`:
```
export OP_DATA_DIR=/path/to/op-data
```

## Quickstart


### Create the path to where your data will live

```commandline
mkdir -p /path/to/op-data
```

```bash
# Daily overview dashboard
op

# Buckets | Based on the GTD 'capture' idea

# -- Bucket Workflow (Capture & Triage)
op bucket add "Start a luxury donkey spa"   # Create a bucket with a text string
op bucket list                              # List existing buckets
op bucket show --id-prefix--                # See one bucket's details by giving a prefix of the ID
op bucket discard --id-prefix--             # Discard a bucket


# Projects | Any action requiring more than one step

# -- Project Workflow
op project create --id-prefix--             # Create a project based on a bucket (deletes the bucket)
op project list                             # Lists ACTIVE projects
op project list --all                       # List all projects
op project list --state new                 # List projects that have not yet been started
op project list --state done                # List projects that have been completed
op project list --state archived            # List projects that were never completed but paused
op project show --id-prefix--               # Show a project's details
op project set --id-prefix--                # To update a project's state [new, active, done, archived]

```

## Development

This project is still in early development and does not work at all yet.  Check back soon.

The basic work structure is as follows:
- Humans write the main code
- Docs and tests are mostly vibe-coded but checked carefully.

## Data

The data stored in `planner.json` will have the following top-level structure:

```
{
    "bucket": {},
    "projects": {},
    "tickets": {},
    "parked": {},
    "habits": {},
    "habit_log": {},
    "accounts": {},
    "balances": {},
    "calendar": {}
}
```
