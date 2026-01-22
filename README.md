# Underdark Tunnel Generator

A Python script for generating detailed descriptions of random tunnels for tabletop RPGs (specifically designed for Underdark settings). It supports generating both "Dry" and "Wet" (river-filled) tunnels with distinct attribute sets.

## Features

- **Dry Tunnels**: Traditional underground passages with attributes like slope, texture, air quality, and floor conditions.
- **Wet Tunnels**: Underground rivers or submerged tunnels with dynamic flow rates (Stagnant to Cascade), water depth, temperature, and unique elevation mechanics driven by water flow.
- **Dynamic Generation**: Every section is randomly generated based on weighted tables, ensuring varied and unique descriptions.
- **Special Features**: Includes rare events like chasms, side rooms, geothermal activity, habitation signs, and more (with specific tables for Wet/Dry environments).

## Usage

Run the script from the command line using Python 3.

```bash
python tunnel_gen.py <length_in_miles> [options]
```

### Arguments

- `length`: (Required) The total length of the tunnel to generate in miles.

### Options

- `--type`: Specify the type of tunnel. Choices are `dry` (default) or `wet`.
- `--min-height`: Minimum height of the tunnel (Dry only filters).
- `--min-width`: Minimum width of the tunnel (Dry only filters).

### Examples

**Generate a standard 1-mile Dry Tunnel:**
```bash
python tunnel_gen.py 1
```

**Generate a 5-mile Wet Tunnel (Underground River):**
```bash
python tunnel_gen.py 5 --type wet
```

**Generate a short 0.1 mile Dry Tunnel:**
```bash
python tunnel_gen.py 0.1
```

## Output Format

The script outputs a breakdown of tunnel sections.

**Example (Dry):**
```text
Section 1: 500 feet, Normal (10'x10'), Gentle Down, Straight, Air: Stale...
```

**Example (Wet):**
```text
Section 1: 500 feet, Average (15'x30'), Flow: Rapid, Water: 10' deep, Ceiling: 5'...
```
