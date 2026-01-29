#!/usr/bin/env python3
"""
Virtual M8 - Simulates a Dirtywave M8 for testing the M8 LPP Emulator

This script acts as a virtual M8 device, receiving Launchpad Pro MIDI messages
from Move's M8 emulator and responding with LED sysex like a real M8 would.

Usage:
    python virtual_m8.py [--list] [--input NAME] [--output NAME]

Requirements:
    pip install mido python-rtmidi

The script will:
1. Connect to Move via USB MIDI
2. Receive LPP button/pad messages
3. Send LED color sysex responses
4. Log all MIDI traffic for debugging
"""

import argparse
import sys
import time
from datetime import datetime

try:
    import mido
except ImportError:
    print("Error: mido not installed. Run: pip install mido python-rtmidi")
    sys.exit(1)


# =============================================================================
# Launchpad Pro Protocol Constants
# =============================================================================

# LPP Note Layout (10x10 grid, but M8 uses 8x8 + edges)
#
#     1   2   3   4   5   6   7   8
#    ┌───┬───┬───┬───┬───┬───┬───┬───┐
# 91 │   │   │   │   │   │   │   │   │ 99  <- Top row (scene launch)
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
# 81 │   │   │   │   │   │   │   │   │ 89  <- Row 8
# 71 │   │   │   │   │   │   │   │   │ 79
# 61 │   │   │   │   │   │   │   │   │ 69
# 51 │   │   │   │   │   │   │   │   │ 59
# 41 │   │   │   │   │   │   │   │   │ 49
# 31 │   │   │   │   │   │   │   │   │ 39
# 21 │   │   │   │   │   │   │   │   │ 29
# 11 │   │   │   │   │   │   │   │   │ 19  <- Row 1
#    └───┴───┴───┴───┴───┴───┴───┴───┘
#     1   2   3   4   5   6   7   8       <- Bottom row (function)
#   101 102 103 104 105 106 107 108

# LPP Sysex header for LED control
LPP_SYSEX_HEADER = [0x00, 0x20, 0x29, 0x02, 0x10]

# LED lighting modes
LED_MODE_STATIC = 0x0A      # Static color
LED_MODE_FLASH = 0x23       # Flashing
LED_MODE_PULSE = 0x28       # Pulsing
LED_MODE_RGB = 0x0B         # RGB color (3 bytes per LED)

# M8 color palette (approximate - real M8 colors may vary)
M8_COLORS = {
    'off': (0, 0, 0),
    'white': (63, 63, 63),
    'red': (63, 0, 0),
    'green': (0, 63, 0),
    'blue': (0, 0, 63),
    'yellow': (63, 63, 0),
    'cyan': (0, 63, 63),
    'magenta': (63, 0, 63),
    'orange': (63, 32, 0),
    'pink': (63, 20, 40),
    'dim_white': (20, 20, 20),
    'dim_red': (20, 0, 0),
    'dim_green': (0, 20, 0),
    'dim_blue': (0, 0, 20),
}

# M8 screen layout simulation
# In M8, different buttons have different functions
M8_BUTTON_FUNCTIONS = {
    # Top row (91-98) - Track selection
    91: 'track_1', 92: 'track_2', 93: 'track_3', 94: 'track_4',
    95: 'track_5', 96: 'track_6', 97: 'track_7', 98: 'track_8',

    # Right column - Navigation
    89: 'nav_up', 79: 'nav_right', 69: 'nav_down', 59: 'nav_left',

    # Function buttons (bottom)
    104: 'option', 105: 'edit', 106: 'shift',

    # Main grid (11-88) - Step sequencer / instruments
}


# =============================================================================
# Virtual M8 State
# =============================================================================

class VirtualM8:
    """Simulates M8 device state and behavior"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.led_state = {}  # note -> (r, g, b)
        self.current_track = 0
        self.current_view = 'song'  # song, chain, phrase, instrument, etc.
        self.shift_held = False

        # Initialize default LED state (dim grid)
        self._init_leds()

    def _init_leds(self):
        """Set up initial LED state like M8 boot screen"""
        # Dim the main grid
        for row in range(1, 9):
            for col in range(1, 9):
                note = row * 10 + col
                self.led_state[note] = M8_COLORS['dim_white']

        # Track buttons - first one lit
        for i, note in enumerate(range(91, 99)):
            if i == 0:
                self.led_state[note] = M8_COLORS['cyan']
            else:
                self.led_state[note] = M8_COLORS['dim_white']

        # Navigation buttons
        self.led_state[89] = M8_COLORS['dim_blue']  # Up
        self.led_state[79] = M8_COLORS['dim_blue']  # Right
        self.led_state[69] = M8_COLORS['dim_blue']  # Down
        self.led_state[59] = M8_COLORS['dim_blue']  # Left

    def handle_note_on(self, note, velocity):
        """Handle a button press from the LPP emulator"""
        log(f"Button ON:  note={note:3d} vel={velocity:3d}", 'rx')

        # Track selection (top row)
        if 91 <= note <= 98:
            track = note - 91
            self._select_track(track)
            return self._get_track_led_updates()

        # Navigation
        if note in [89, 79, 69, 59]:
            return self._handle_nav(note, True)

        # Main grid press - light it up
        if 11 <= note <= 88 and note % 10 != 0 and note % 10 != 9:
            self.led_state[note] = M8_COLORS['white']
            return [(note, M8_COLORS['white'])]

        # Function buttons
        if note == 106:  # Shift
            self.shift_held = True
            return [(note, M8_COLORS['orange'])]

        return []

    def handle_note_off(self, note, velocity):
        """Handle a button release"""
        log(f"Button OFF: note={note:3d}", 'rx')

        # Main grid release - return to dim
        if 11 <= note <= 88 and note % 10 != 0 and note % 10 != 9:
            self.led_state[note] = M8_COLORS['dim_white']
            return [(note, M8_COLORS['dim_white'])]

        # Navigation release
        if note in [89, 79, 69, 59]:
            return self._handle_nav(note, False)

        # Shift release
        if note == 106:
            self.shift_held = False
            return [(note, M8_COLORS['dim_white'])]

        return []

    def _select_track(self, track):
        """Select a track (0-7)"""
        self.current_track = track
        log(f"Track selected: {track + 1}", 'state')

    def _get_track_led_updates(self):
        """Get LED updates for track selection"""
        updates = []
        for i in range(8):
            note = 91 + i
            if i == self.current_track:
                color = M8_COLORS['cyan']
            else:
                color = M8_COLORS['dim_white']
            self.led_state[note] = color
            updates.append((note, color))
        return updates

    def _handle_nav(self, note, pressed):
        """Handle navigation button"""
        if pressed:
            self.led_state[note] = M8_COLORS['blue']
        else:
            self.led_state[note] = M8_COLORS['dim_blue']
        return [(note, self.led_state[note])]

    def get_all_leds(self):
        """Get all LED states for initial sync"""
        return list(self.led_state.items())


# =============================================================================
# MIDI Communication
# =============================================================================

def create_led_sysex(updates):
    """
    Create LPP sysex message for LED updates.

    Args:
        updates: list of (note, (r, g, b)) tuples

    Returns:
        mido.Message sysex message
    """
    if not updates:
        return None

    # Build RGB LED sysex: F0 00 20 29 02 10 0B [note r g b]... F7
    data = LPP_SYSEX_HEADER + [LED_MODE_RGB]

    for note, (r, g, b) in updates:
        data.extend([note, r, g, b])

    return mido.Message('sysex', data=data)


def log(msg, category='info'):
    """Log with timestamp and category"""
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    prefix = {
        'rx': '← RX',
        'tx': '→ TX',
        'info': '  ℹ️ ',
        'state': '  📊',
        'error': '  ❌',
    }.get(category, '    ')
    print(f"[{timestamp}] {prefix} {msg}")


def list_ports():
    """List available MIDI ports"""
    print("\nAvailable MIDI Input Ports:")
    for i, name in enumerate(mido.get_input_names()):
        print(f"  {i}: {name}")

    print("\nAvailable MIDI Output Ports:")
    for i, name in enumerate(mido.get_output_names()):
        print(f"  {i}: {name}")


def find_move_ports():
    """Try to find Move's MIDI ports automatically"""
    input_port = None
    output_port = None

    for name in mido.get_input_names():
        if 'Move' in name or 'Ableton' in name:
            input_port = name
            break

    for name in mido.get_output_names():
        if 'Move' in name or 'Ableton' in name:
            output_port = name
            break

    return input_port, output_port


def run_virtual_m8(input_port, output_port, verbose=False):
    """Main loop - receive MIDI, simulate M8, send responses"""

    m8 = VirtualM8(verbose=verbose)

    log(f"Opening input:  {input_port}")
    log(f"Opening output: {output_port}")

    try:
        inport = mido.open_input(input_port)
        outport = mido.open_output(output_port)
    except Exception as e:
        log(f"Failed to open MIDI ports: {e}", 'error')
        return

    log("Virtual M8 running! Press Ctrl+C to exit.")
    log("Sending initial LED state...")

    # Send initial LED state
    initial_leds = m8.get_all_leds()
    sysex = create_led_sysex(initial_leds)
    if sysex:
        outport.send(sysex)
        log(f"Sent {len(initial_leds)} LED updates", 'tx')

    try:
        while True:
            # Process incoming MIDI
            for msg in inport.iter_pending():
                updates = []

                if msg.type == 'note_on' and msg.velocity > 0:
                    updates = m8.handle_note_on(msg.note, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    updates = m8.handle_note_off(msg.note, 0)
                elif msg.type == 'control_change':
                    log(f"CC: cc={msg.control} val={msg.value}", 'rx')
                elif msg.type == 'sysex':
                    log(f"Sysex received: {len(msg.data)} bytes", 'rx')
                    if verbose:
                        log(f"  Data: {' '.join(f'{b:02X}' for b in msg.data[:20])}...", 'rx')

                # Send LED updates
                if updates:
                    sysex = create_led_sysex(updates)
                    if sysex:
                        outport.send(sysex)
                        log(f"LED update: {len(updates)} LEDs", 'tx')

            time.sleep(0.001)  # Small sleep to prevent CPU spin

    except KeyboardInterrupt:
        log("\nShutting down...")
    finally:
        inport.close()
        outport.close()


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Virtual M8 - Simulate a Dirtywave M8 for testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                    # List available MIDI ports
  %(prog)s                           # Auto-detect Move ports
  %(prog)s -i "Move" -o "Move"       # Specify port names
  %(prog)s -v                        # Verbose output
        """
    )

    parser.add_argument('--list', '-l', action='store_true',
                        help='List available MIDI ports and exit')
    parser.add_argument('--input', '-i', metavar='NAME',
                        help='Input MIDI port name (from Move)')
    parser.add_argument('--output', '-o', metavar='NAME',
                        help='Output MIDI port name (to Move)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output (show all MIDI data)')

    args = parser.parse_args()

    if args.list:
        list_ports()
        return

    # Find ports
    input_port = args.input
    output_port = args.output

    if not input_port or not output_port:
        auto_in, auto_out = find_move_ports()
        input_port = input_port or auto_in
        output_port = output_port or auto_out

    if not input_port or not output_port:
        log("Could not find Move MIDI ports. Use --list to see available ports.", 'error')
        log("Then specify with: --input 'port name' --output 'port name'", 'error')
        list_ports()
        return

    run_virtual_m8(input_port, output_port, verbose=args.verbose)


if __name__ == '__main__':
    main()
