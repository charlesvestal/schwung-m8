# CLAUDE.md

## Project Overview

M8 LPP Emulator module for Schwung. Emulates a Novation Launchpad Pro for use with Dirtywave M8.

## Build Commands

```bash
./scripts/build.sh      # Package files
./scripts/install.sh    # Deploy to Move
```

## Structure

```
src/
  module.json           # Module metadata
  ui.js                 # JavaScript UI (Launchpad Pro emulation)
```

## Features

- Emulates Launchpad Pro MIDI protocol
- Full pad matrix with velocity
- Raw MIDI mode for direct M8 communication
