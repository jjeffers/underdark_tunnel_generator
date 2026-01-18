import random
import argparse
import math

def generate_tunnel(length_miles, min_height=0, min_width=0):
    total_feet = length_miles * 5280
    current_feet = 0
    sections = []
    total_elevation_change = 0

    # Defined ranges and their weights (sum=95 initially)
    # Options:
    # --- Attribute Data Tables ---
    # Choice dicts and weights computed once
    
    # 1. Section Length Categories
    len_choices = [
        {'gen': lambda: roll(5, 8),                       'weight': 10},
        {'gen': lambda: roll(10, 6) + 30,                 'weight': 20},
        {'gen': lambda: roll(10, 4) * 10,                 'weight': 25},
        {'gen': lambda: roll(10, 6) * 10 + 400,           'weight': 35},
        {'gen': lambda: roll(10, 4) * 50,                 'weight': 10}
    ]
    len_weights = [c['weight'] for c in len_choices]
    
    # 2. Dimensions
    # Format: HxW
    size_choices_all = [
        {'name': "Tiny",        'dim': "1'x1'",   'h': 1,  'w': 1,  'weight': 5},
        {'name': "Tight",       'dim': "2'x2'",   'h': 2,  'w': 2,  'weight': 5},
        {'name': "Crawl",       'dim': "3'x3'",   'h': 3,  'w': 3,  'weight': 10},
        {'name': "Wide Crawl",  'dim': "3'x5'",   'h': 3,  'w': 5,  'weight': 10},
        {'name': "Very Narrow", 'dim': "5'x3'",   'h': 5,  'w': 3,  'weight': 15},
        {'name': "Narrow",      'dim': "5'x5'",   'h': 5,  'w': 5,  'weight': 20},
        {'name': "Normal",      'dim': "10'x10'", 'h': 10, 'w': 10, 'weight': 25},
        {'name': "Wide",        'dim': "15'x15'", 'h': 15, 'w': 15, 'weight': 5},
        {'name': "Very Wide",   'dim': "20'x60'", 'h': 20, 'w': 60, 'weight': 5},
    ]

    # Filter sizes based on min_height and min_width
    size_choices = [s for s in size_choices_all if s['h'] >= min_height and s['w'] >= min_width]
    
    if not size_choices:
        print(f"Warning: No size options match min_height={min_height} and min_width={min_width}. Reverting to default list.")
        size_choices = size_choices_all

    size_weights = [s['weight'] for s in size_choices]

    # 3. Slopes
    slope_choices = [
        {'name': "Steep Up",      'range': (51, 70),   'weight': 5},
        {'name': "Moderate Up",   'range': (31, 50),   'weight': 10},
        {'name': "Gentle Up",     'range': (15, 30),   'weight': 20},
        {'name': "Level",         'range': (-14, 14),  'weight': 30},
        {'name': "Gentle Down",   'range': (15, 30),   'weight': 20}, # Fixed from original
        {'name': "Moderate Down", 'range': (31, 50),   'weight': 10}, # Fixed from original
        {'name': "Steep Down",    'range': (51, 70),   'weight': 5},  # Fixed from original
    ]
    slope_weights = [s['weight'] for s in slope_choices]
    
    # 4. Direction
    dir_choices = [
        {'name': "Curving right",        'weight': 15},
        {'name': "Curving left",         'weight': 15},
        {'name': "Sharp right",          'weight': 5},
        {'name': "Sharp left",           'weight': 5},
        {'name': "Straight",             'weight': 40},
        {'name': "Twisting and snaking", 'weight': 20},
    ]
    dir_weights = [d['weight'] for d in dir_choices]

    # 5. Floor Texture
    texture_choices = [
        {'name': "Slick and polished",      'weight': 10},
        {'name': "Smooth",                  'weight': 15},
        {'name': "Normal",                  'weight': 30},
        {'name': "Rough",                   'weight': 15},
        {'name': "Tiered",                  'weight': 10},
        {'name': "Covered in large boulders", 'weight': 10},
        {'name': "Covered in sharp rocks",  'weight': 5},
    ]
    texture_weights = [t['weight'] for t in texture_choices]

    # 6. Floor Condition
    condition_choices = [
        {'name': "Water-filled (up to 1' deep)",                 'weight': 5},
        {'name': "Slippery (wet and slimy)",                      'weight': 25},
        {'name': "Slick (damp or wet)",                           'weight': 45},
        {'name': "Dry, good looking",                             'weight': 20},
        {'name': "Dusty (dead tunnel check for cave-in chances)", 'weight': 5},
    ]
    condition_weights = [c['weight'] for c in condition_choices]

    # 7. Illumination
    illumination_choices = [
        {'name': "None",                                           'weight': 50},
        {'name': "Very weak (moonless)",                           'weight': 20},
        {'name': "Weak light (moonlight with overcast clouds)",     'weight': 15},
        {'name': "Moderate light (moonlight with no clouds)",      'weight': 10},
        {'name': "Bright light (twlight)",                         'weight': 5},
    ]
    illumination_weights = [i['weight'] for i in illumination_choices]

    # 8. Air Supply
    air_choices = [
        {'name': "Poison/noxious gas",                                  'weight': 5},
        {'name': "Stale",                                               'weight': 5},
        {'name': "Faint circulation",                                   'weight': 20},
        {'name': "Normal",                                              'weight': 35},
        {'name': "Drafty (1% chance of torch blowout a round)",         'weight': 15},
        {'name': "Windy (10% chance of torch blowout per round)",       'weight': 10},
        {'name': "Rushing air (50% chance of torch blowout per round)", 'weight': 5},
        {'name': "Steam vapors",                                        'weight': 5},
    ]
    air_weights = [a['weight'] for a in air_choices]

    # --- Change Logic Data ---
    # How many attributes change?
    # 25% none, 25% 1, 15% 2, 15% 3, 10% 4, 5% 5
    num_change_opts = [0, 1, 2, 3, 4, 5]
    num_change_weights = [25, 25, 15, 15, 10, 5]

    # Which attributes change?
    # 20% height and width
    # 15% slope
    # 20% floor texture
    # 10% floor condition
    # 5% air supply
    # 5% illumination
    # 5% add a special feature (TBD)
    # 20% Direction (Assumed missing)
    attr_map = {
        'size': {'choices': size_choices, 'weights': size_weights, 'weight_in_change': 20},
        'slope': {'choices': slope_choices, 'weights': slope_weights, 'weight_in_change': 15},
        'dir': {'choices': dir_choices, 'weights': dir_weights, 'weight_in_change': 20},
        'tex': {'choices': texture_choices, 'weights': texture_weights, 'weight_in_change': 20},
        'cond': {'choices': condition_choices, 'weights': condition_weights, 'weight_in_change': 10},
        'air': {'choices': air_choices, 'weights': air_weights, 'weight_in_change': 5},
        'illum': {'choices': illumination_choices, 'weights': illumination_weights, 'weight_in_change': 5},
        'special': {'weight_in_change': 5}
    }
    
    attr_keys = list(attr_map.keys())
    attr_change_weights = [attr_map[k]['weight_in_change'] for k in attr_keys]

    print(f"Generating tunnel of length {length_miles} miles ({total_feet:,.0f} feet)...")

    # Current State (Dictionary of current attributes)
    # Initialize with random values
    state = {}
    for k in attr_keys:
        if k == 'special': continue
        state[k] = random.choices(attr_map[k]['choices'], weights=attr_map[k]['weights'], k=1)[0]
    
    # Slopes need an actual degree generated each time! 
    # Let's handle 'slope' state as just the category. We re-roll degree even if slope category stays same?
    # Actually, usually "same slope" means same specific incline. Let's persist state as the object.
    # But wait, original code generated degree randomly *after* picking slope.
    # Let's generate the specific degree and store it in state too.
    min_deg, max_deg = state['slope']['range']
    state['degree'] = random.randint(min_deg, max_deg)

    while current_feet < total_feet:
        is_first = (len(sections) == 0)
        special_feature = None

        if not is_first:
            # Determine changes
            num_changes = random.choices(num_change_opts, weights=num_change_weights, k=1)[0]
            
            # Pick 'num_changes' unique attributes to change
            for _ in range(num_changes):
                attr_to_change = random.choices(attr_keys, weights=attr_change_weights, k=1)[0]
                
                if attr_to_change == 'special':
                    # Special feature triggered!
                    # Logic: Generate the feature string immediately.
                    # It applies to this new section.
                    special_feature = gen_special_feature()
                else:
                    # Re-roll this attribute
                    data = attr_map[attr_to_change]
                    new_val = random.choices(data['choices'], weights=data['weights'], k=1)[0]
                    state[attr_to_change] = new_val
                    
                    # If slope changed, re-roll degree
                    if attr_to_change == 'slope':
                        min_d, max_d = new_val['range']
                        state['degree'] = random.randint(min_d, max_d)
        
        # Determine Length (Length is always re-rolled, it's not a persistent state like 'size')
        # Though user didn't specify length in the change list, so we assume length is always a new "section" roll.
        selected_len_gen = random.choices(len_choices, weights=len_weights, k=1)[0]
        section_len = selected_len_gen['gen']()
        
        # Check total
        remaining = total_feet - current_feet
        if section_len > remaining:
            section_len = int(remaining)

        # Calculate Elev
        effective_angle = state['degree']
        if "Down" in state['slope']['name']:
            effective_angle = -state['degree']
        
        elev_change = section_len * math.sin(math.radians(effective_angle))
        total_elevation_change += elev_change

        # Prepare New Section Object
        new_section = {
            'len': section_len,
            'size': state['size'],
            'slope': state['slope'],
            'degree': state['degree'],
            'dir': state['dir'],
            'tex': state['tex'],
            'cond': state['cond'],
            'illum': state['illum'],
            'air': state['air'],
            'elev': elev_change,
            # Special feature is specific to THIS section generation instance, 
            # it is not "state" that persists.
            'special': special_feature 
        }

        # Check for merge (combine with previous if identical attributes)
        merged = False
        if len(sections) > 0:
            prev = sections[-1]
            # Compare all attributes except length/elev
            if (prev['size'] == new_section['size'] and
                prev['slope'] == new_section['slope'] and
                prev['degree'] == new_section['degree'] and
                prev['dir'] == new_section['dir'] and
                prev['tex'] == new_section['tex'] and
                prev['cond'] == new_section['cond'] and
                prev['illum'] == new_section['illum'] and
                prev['air'] == new_section['air'] and
                prev['special'] == new_section['special']):
                
                # Merge!
                prev['len'] += new_section['len']
                prev['elev'] += new_section['elev']
                merged = True
        
        if not merged:
            sections.append(new_section)
        
        current_feet += section_len

    print(f"\nTunnel Generation Complete.")
    print(f"Total Sections: {len(sections)}")
    print(f"Actual Total Length: {current_feet:,.0f} feet")
    print(f"Total Elevation Change: {total_elevation_change:+.1f} feet")
    print(f"\n--- Section Breakdown ---")
    
    for i, s in enumerate(sections):
        special_txt = f" [Special: {s['special']}]" if s['special'] else ""
        print(f"Section {i+1}: {s['len']} feet, {s['size']['name']} ({s['size']['dim']}), {s['slope']['name']} ({s['degree']} deg), {s['dir']['name']}, {s['tex']['name']}, {s['cond']['name']}, Light: {s['illum']['name']}, Air: {s['air']['name']} [Elev: {s['elev']:+.1f} ft]{special_txt}")

def roll(num_dice, sides):
    return sum(random.randint(1, sides) for _ in range(num_dice))

def gen_special_feature():
    # 30% None
    # 5% Side ledges or tiers
    # 7% Minor side rooms (3-60' wide x (10d20 x0' long)
    # 3% Stairs (natural or man-made)
    # 7% Side tunnels that dead-end in 1-6 miles with cross sections of 5'x5' or less (roll 1d100 for special features; 20% are small underground streams)
    # 5% pits (3-18' deep)
    # 6% Chasms (20-200' deep x 4-40' wide)
    # 3% Clifss (10-100' high)
    # 5% Geothermal activity (TBD)
    # 9% Blockages (TBD)
    # 10% Habitation signs (TBD)
    # 3% Minor mineral vein
    # 2% DM's choice!
    
    choices = [
        {'name': "None", 'weight': 30},
        {'name': "Side ledges or tiers", 'weight': 5},
        {'name': "Minor side rooms", 'weight': 7},
        {'name': "Stairs (natural or man-made)", 'weight': 3},
        {'name': "Side tunnels", 'weight': 7},
        {'name': "Pits", 'weight': 5},
        {'name': "Chasms", 'weight': 6},
        {'name': "Cliffs", 'weight': 3},
        {'name': "Geothermal activity", 'weight': 5},
        {'name': "Blockages", 'weight': 9},
        {'name': "Habitation signs", 'weight': 10},
        {'name': "Minor mineral vein", 'weight': 3},
        {'name': "DM's choice!", 'weight': 2},
    ]
    weights = [c['weight'] for c in choices]
    
    selected = random.choices(choices, weights=weights, k=1)[0]['name']
    
    if selected == "None":
        return None
        
    if selected == "Minor side rooms":
        width = random.randint(3, 60)
        length = roll(10, 20) * 10
        return f"Minor side room ({width}' wide x {length}' long)"
        
    if selected == "Side tunnels":
        miles = random.randint(1, 6)
        is_stream = (random.randint(1, 100) <= 20)
        stream_txt = " (small underground stream)" if is_stream else ""
        return f"Side tunnel (dead-ends in {miles} miles, 5'x5' or less){stream_txt}"
        
    if selected == "Pits":
        depth = roll(3, 6)
        return f"Pit ({depth}' deep)"
        
    if selected == "Chasms":
        depth = random.randint(20, 200)
        width = random.randint(4, 40)
        return f"Chasm ({depth}' deep x {width}' wide)"
        
    if selected == "Cliffs":
        height = random.randint(10, 100)
        return f"Cliff ({height}' high)"
        
    if selected == "Geothermal activity":
        # 40% Hot or boiling pool of water
        # 10% Poisonous/noxious gas vent
        # 15% Steam Vent
        # 25% Hot air
        # 5% Lava pool
        geo_choices = [
            {'name': "Hot or boiling pool of water", 'weight': 40},
            {'name': "Poisonous/noxious gas vent",   'weight': 10},
            {'name': "Steam Vent",                   'weight': 15},
            {'name': "Hot air",                      'weight': 25},
            {'name': "Lava pool",                    'weight': 5},
        ]
        geo_w = [c['weight'] for c in geo_choices]
        geo_type = random.choices(geo_choices, weights=geo_w, k=1)[0]['name']
        return f"Geothermal: {geo_type}"

    if selected == "Blockages":
        # 15% Large boulder field
        # 15% Minor cave-in
        # 15% Water pool
        # 5% Quicksand
        # 5% oil pool
        # 5% tar pit
        # 25% Large stalactites, stalagmites, or columns
        # 5% Balconies
        # 5% Water way (random size TBD)
        # 5% DM's choice!
        block_choices = [
            {'name': "Large boulder field",                     'weight': 15},
            {'name': "Minor cave-in",                           'weight': 15},
            {'name': "Water pool",                              'weight': 15},
            {'name': "Quicksand",                               'weight': 5},
            {'name': "Oil pool",                                'weight': 5},
            {'name': "Tar pit",                                 'weight': 5},
            {'name': "Large stalactites, stalagmites, or columns", 'weight': 25},
            {'name': "Balconies",                               'weight': 5},
            {'name': "Water way",                               'weight': 5},
            {'name': "DM's choice!",                            'weight': 5},
        ]
        block_w = [c['weight'] for c in block_choices]
        block_type = random.choices(block_choices, weights=block_w, k=1)[0]['name']
        
        if block_type == "Water way":
            # Random size TBD -> implementing simple random logic
            width = random.randint(5, 30)
            depth = random.randint(3, 15)
            return f"Blockage: Water way ({width}' wide x {depth}' deep)"
            
        return f"Blockage: {block_type}"
    
    if selected == "Habitation signs":
        # 5% Cairn marking territory
        # 1% ruined building
        # 5% old campsite
        # 1% small abandoned shrine
        # 2% dead bodies
        # 2% shallow grave
        # 2% burial mound
        # 2% secret stash
        # 13% Broken tools, weapons, or armor
        # 2% intact tools, weapons, or armor
        # 3% battlefield
        # 20% worked stone surfaces
        # 7% abandoned adventurers gear
        # 18% intact bridge
        # 10% ruined bridge
        hab_choices = [
            {'name': "Cairn marking territory",           'weight': 5},
            {'name': "Ruined building",                   'weight': 1},
            {'name': "Old campsite",                      'weight': 5},
            {'name': "Small abandoned shrine",            'weight': 1},
            {'name': "Dead bodies",                       'weight': 2},
            {'name': "Shallow grave",                     'weight': 2},
            {'name': "Burial mound",                      'weight': 2},
            {'name': "Secret stash",                      'weight': 2},
            {'name': "Broken tools, weapons, or armor",   'weight': 13},
            {'name': "Intact tools, weapons, or armor",   'weight': 2},
            {'name': "Battlefield",                       'weight': 3},
            {'name': "Worked stone surfaces",             'weight': 20},
            {'name': "Abandoned adventurers gear",        'weight': 7},
            {'name': "Intact bridge",                     'weight': 18},
            {'name': "Ruined bridge",                     'weight': 10},
        ]
        hab_w = [c['weight'] for c in hab_choices]
        hab_type = random.choices(hab_choices, weights=hab_w, k=1)[0]['name']
        return f"Habitation: {hab_type}"

    return selected # For others just return the name



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a tunnel description.")
    parser.add_argument("length", type=float, help="Total length of the tunnel in miles")
    parser.add_argument("--min-height", type=int, default=0, help="Minimum height in feet")
    parser.add_argument("--min-width", type=int, default=0, help="Minimum width in feet")
    
    args = parser.parse_args()
    
    generate_tunnel(args.length, args.min_height, args.min_width)
