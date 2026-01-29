# M8 Development Tools

## Virtual M8

`virtual_m8.py` simulates a Dirtywave M8 device for testing the M8 LPP Emulator without real hardware.

### Setup

```bash
pip install mido python-rtmidi
```

### Usage

1. Connect your computer to Move's USB-A port
2. Run the virtual M8:

```bash
# Auto-detect Move ports
python virtual_m8.py

# List available MIDI ports
python virtual_m8.py --list

# Specify ports manually
python virtual_m8.py -i "Move MIDI" -o "Move MIDI"

# Verbose mode (show all MIDI data)
python virtual_m8.py -v
```

3. On Move, enter the M8 emulator (Shift+Vol+Jog → M8 LPP Emulator)
4. The virtual M8 will respond to button presses with LED updates

### What it does

- Receives Launchpad Pro protocol MIDI from Move
- Simulates basic M8 behavior (track selection, navigation, grid presses)
- Sends LED sysex responses back to Move
- Logs all MIDI traffic for debugging

### Extending

To add more M8 behavior, edit the `VirtualM8` class:
- `handle_note_on()` - Button press handling
- `handle_note_off()` - Button release handling
- `M8_COLORS` - Color palette
- `_init_leds()` - Initial LED state
