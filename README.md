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

After installation, you can do the following:

### Create the path to where your data will live

```commandline
mkdir -p /path/to/op-data
```

### See your day's dashboard
```commandline
op
```

### Add a new bucket item.

The "bucket" refers to items that you capture to decide what to do with later.
They are rough plans that still need to be sorted.

To capture a new bucket item, you do the following:

```commandline
op bucket add "Start a luxury donkey spa"
```

### See a list of all your bucket items

```commandline
op bucket list
```

### See a bucket item's details

The ID is simply a uuid string, and providing a reasonable prefix will find the item.

```commandline
op bucket show --id-prefix--
```

### Discard a bucket item

Deleting is easy, it simply takes an ID and deletes it.  The reason for this is that the bucket
should be a place to throw ideas, and it should be easy to get rid of the ones that, on reflection
aren't worth taking action on.

```commandline
op bucket discard --id-prefix--
```


## Development

This project is still in early development and does not work at all yet.  Check back soon.

The basic work structure is as follows:
- Humans write the main code
- Docs and tests are mostly vibe-coded but checked carefully.

## Data

The data stored in `planner.json` will have the following top-level structure

```
BASE_STRUCTURE = {
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
