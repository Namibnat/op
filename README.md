# Personal Operations Planner

A tool that combines personal project management through a GTD style system
with routines and habit tracking and other miscellaneous tracking for things like
finances.

Although I called it a "planner", it is not a tool for planning, it is a tool
for capturing planning.  This is most true for projects.  Projects can be in
all sorts of places and the thinking and planning belongs to the project. Use op
to capture and organise.


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
op bucket show <bucket-id>                  # See one bucket's details by giving a prefix of the ID
op bucket discard <bucket-id>               # Discard a bucket


# Projects | Any action requiring more than one step

# Project resources are simple text notes to function more as a reminder where project
# resources live, not live links, etc.

# -- Project Workflow
op project create <bucket-id>               # Create a project based on a bucket (deletes the bucket)
op project list                             # Lists ACTIVE projects
op project list --all                       # List all projects
op project list --state new                 # List projects that have not yet been started
op project list --state done                # List projects that have been completed
op project list --state archived            # List projects that were never completed but paused
op project show <project-id>                # Show a project's details
op project set <project-id>                 # To update a project's state [new, active, done, archived]
op project resource --all <project-id>      # Add a resources to a project
op project resource --remove <project-id>   # Delete a resource from a project


# Tickets | For GTD, think 'actions'

# Unlike GTD, a project might have multiple tickets that can be actioned next
# Tickets can belong to a project or simply stand-alone.
# Cancelled tickets are never shown in ticket list, but are still kept (maybe for reflection)

# -- Ticket Workflow
op ticket create <bucket-id>                # Create a one-action ticket out of a bucket
op ticket create <project-id>               # Create a ticket for a project
op ticket create                            # Create a one-action ticket directly
op ticket list                              # List all tickets that are actionable
op ticket list --actionable                 # List all tickets that are actionable
op ticket list --state all                  # List all tickets that have not been cancelled
op ticket list --state open                 # List all tickets that are open
op ticket list --state in_progress          # List all tickets that are in progress
op ticket list --state done                 # List all tickets that are done
op ticket show <ticket-id>                  # Show a ticket's details
# Listing all done tickets will be a lot, and probably more useful for reviews, suggest piping to a file:
op ticket list --state done > /path/to/output.txt
op ticket set                               # Set prompts the user to change state or actionability of the ticket

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
