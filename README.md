# Personal Operations Planner

A tool that combines personal project management through a GTD style system
with routines and habit tracking and other miscellaneous tracking for things like
finances.

## Features

- A GTD style app.
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

pip install -e .
```

## Configuration

Provide a local `OP_DATA_DIR` in your .env with the path to where you want your data
files to live.  This project doesn't use any database at all, simply JSON text files.

`.env`:
```
export OP_DATA_DIR="OP_DATA_DIR=/path/to/op-data"
```

## Data

## Development

This project is still in early development and does not work at all yet.  Check back soon.

The basic work structure is as follows:
- Humans write the main code
- Docs and tests are mostly vibe-coded but checked carefully.

## Project Structure
