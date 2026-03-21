# M8 LPP Emulator for Schwung

Novation Launchpad Pro emulation for Dirtywave M8, allowing you to use Ableton Move as an M8 controller.

A port of the original M8 LPP emulation for [Schwung](https://github.com/charlesvestal/schwung) by bobbydigitales.

## Prerequisites

- [Schwung](https://github.com/charlesvestal/schwung) installed on your Ableton Move
- Dirtywave M8 hardware

## Features

- Emulates Launchpad Pro MIDI protocol
- Full pad matrix with velocity sensitivity
- Compatible with M8's Launchpad Pro mode

## Building

```bash
./scripts/build.sh
```

## Installation

Via Module Store (recommended):
- Launch Schwung → Module Store → Utilities → M8 LPP Emulator

Manual installation:
```bash
./scripts/install.sh
```

## Usage

1. Connect M8 to Move via USB-A port
2. Launch M8 LPP Emulator module
3. Configure M8 to use Launchpad Pro mode

## Important: MIDI Channel Configuration

The M8 LPP Emulator communicates on **MIDI channel 1**. To avoid conflicts:

- Set Move tracks to use **channel 2 or higher**
- Set shadow mode slots to use **channel 2 or higher** (via receive/forward channel settings)
- Do not configure Move tracks to listen on channel 1 and output to channel 1, as this creates MIDI echo that interferes with M8 communication

This ensures M8's Launchpad Pro protocol doesn't trigger Move's synths or get echoed back.

## AI Assistance Disclaimer

This module is part of Schwung and was developed with AI assistance, including Claude, Codex, and other AI assistants.

All architecture, implementation, and release decisions are reviewed by human maintainers.  
AI-assisted content may still contain errors, so please validate functionality, security, and license compatibility before production use.
