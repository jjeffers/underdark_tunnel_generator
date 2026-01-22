import random
import argparse
import math

def roll(num_dice, sides):
    return sum(random.randint(1, sides) for _ in range(num_dice))

# --- Generators for Dynamic Attributes ---

def gen_wet_width():
    # 5d12
    # 5-20: Narrow
    # 20+: Average (Actually 21+)
    val = roll(5, 12)
    cat = "Narrow" if val <= 20 else "Average"
    # Default height 10 for now
    return {'name': cat, 'dim': f"10'x{val}'", 'h': 10, 'w': val}

def gen_water_depth():
    # 1d10 table
    # 1: 1' or less
    # 2-3: 1-4' deep (User said 2 is 1-4', 3 was missing, assuming 3 is also 1-4')
    # 4-6: 5-9' deep
    # 7-9: 10' deep
    # 10: 15' deep
    r = random.randint(1, 10)
    if r == 1:
        return {'name': "1' or less deep", 'depth_ft': 1}
    elif 2 <= r <= 3:
        val = random.randint(1, 4)
        return {'name': "1-4' deep", 'depth_ft': val}
    elif 4 <= r <= 6:
        val = random.randint(5, 9)
        return {'name': "5-9' deep", 'depth_ft': val}
    elif 7 <= r <= 9:
        return {'name': "10' deep", 'depth_ft': 10}
    else: # 10
        return {'name': "15' deep", 'depth_ft': 15}

def gen_wet_ceiling():
    # 1d10
    # 1: 1' or less
    # 2-3: 1-4'
    # 4-8: 5'
    # 9-10: 10'
    r = random.randint(1, 10)
    if r == 1:
        return {'name': "1' or less", 'height_ft': 1}
    elif 2 <= r <= 3:
        val = random.randint(1, 4)
        return {'name': "1-4'", 'height_ft': val}
    elif 4 <= r <= 8:
        return {'name': "5'", 'height_ft': 5}
    else: # 9-10
        return {'name': "10'", 'height_ft': 10}

def gen_flow_rate():
    # 1d20
    # 1-4 Stagnant
    # 5-9 Placid (1-40' per rounnd)
    # 10-15 Medium (41-120' per round), 1-2 on a d6 means a drop-off 1-3' per mile
    # 16-19 Rapid (121-240' per round), 1-5 on a d6 means a drop-off of 1-4' per mile
    # 20 Cascade (241-600' per round), 3-18 drop offs of 1d8' of height per mile
    
    r = random.randint(1, 20)
    drop_ft_per_mile = 0
    
    if r <= 4:
        # Stagnant
        return {'name': "Stagnant", 'speed': "0'", 'drop_ft_per_mile': 0}
    elif r <= 9:
        # Placid
        speed = random.randint(1, 40)
        return {'name': "Placid", 'speed': f"{speed}'/rnd", 'drop_ft_per_mile': 0}
    elif r <= 15:
        # Medium
        speed = random.randint(41, 120)
        # 1-2 on d6 for drop off
        if random.randint(1, 6) <= 2:
            drop_ft_per_mile = random.randint(1, 3)
        return {'name': "Medium", 'speed': f"{speed}'/rnd", 'drop_ft_per_mile': drop_ft_per_mile}
    elif r <= 19:
        # Rapid
        speed = random.randint(121, 240)
        # 1-5 on d6 for drop off
        if random.randint(1, 6) <= 5:
            drop_ft_per_mile = random.randint(1, 4)
        return {'name': "Rapid", 'speed': f"{speed}'/rnd", 'drop_ft_per_mile': drop_ft_per_mile}
    else: # 20
        # Cascade
        speed = random.randint(241, 600)
        # 3-18 drop offs of 1d8' per mile
        num_drops = roll(3, 6)
        total_drop = sum(random.randint(1, 8) for _ in range(num_drops))
        return {'name': "Cascade", 'speed': f"{speed}'/rnd", 'drop_ft_per_mile': total_drop}

def gen_water_temp():
    # 1d20
    # 1 32 degrees
    # 2-3 33-35 degrees
    # 4-12 36-40 degrees
    # 13-15 41-45 degrees
    # 16-17 46-50 degrees
    # 18 51-80 degrees
    # 19 81-100 degrees
    # 20 100+ degrees
    r = random.randint(1, 20)
    if r == 1: return "32 F"
    if 2 <= r <= 3: return f"{random.randint(33, 35)} F"
    if 4 <= r <= 12: return f"{random.randint(36, 40)} F"
    if 13 <= r <= 15: return f"{random.randint(41, 45)} F"
    if 16 <= r <= 17: return f"{random.randint(46, 50)} F"
    if r == 18: return f"{random.randint(51, 80)} F"
    if r == 19: return f"{random.randint(81, 100)} F"
    return "100+ F"

def mutate_wet_width(current_size_obj):
    # 1-4 Section Width (roll a d6: 1 decrease by 10' or by 5' if width is already 10', 2-5 no change, 6 increase width by 10)
    # Actually the d20 change table says "1-4 Section Width". IF we picked Width to change, THEN we do the d6 logic.
    
    current_w = current_size_obj['w']
    # If width not in object? It should be there.
    
    d6 = random.randint(1, 6)
    new_w = current_w
    
    if d6 == 1:
        if current_w <= 10:
            new_w = max(5, current_w - 5)
        else:
            new_w = current_w - 10
    elif d6 == 6:
        new_w = current_w + 10
    # 2-5 no change
    
    # Reconstruct size object
    cat = "Narrow" if new_w <= 20 else "Average"
    return {'name': cat, 'dim': f"10'x{new_w}'", 'h': 10, 'w': new_w}

def gen_wet_condition():

    # Wet tunnels are always wet? 
    # The prompt says "generation... is essentially the same... but attributes differ"
    # It implies we need a list of condition choices for Wet tunnels.
    # For now, let's assume a generic "Wet/Water-filled" condition or reuse applicable ones.
    # User said "Water Depth" is an attribute. 
    # Existing "Condition" attribute has things like "Water-filled", "Slippery", "Dry".
    # We should probably define a specific set for Wet tunnels. 
    # Let's assume they are "Water-filled" by definition, but maybe the *condition* describes the flow/smell/etc?
    # For now, I'll define a placeholder set that makes sense for "Wet" tunnels.
    return random.choice([
        {'name': "Stagnant", 'weight': 20},
        {'name': "Flowing slowly", 'weight': 40},
        {'name': "Rushing", 'weight': 20},
        {'name': "Murky", 'weight': 20},
    ])

# --- Configuration Data ---

def get_config(tunnel_type, min_height=0, min_width=0):
    # Shared choices
    
    # Length Categories (Same for both)
    len_choices = [
        {'gen': lambda: roll(5, 8),                       'weight': 10},
        {'gen': lambda: roll(10, 6) + 30,                 'weight': 20},
        {'gen': lambda: roll(10, 4) * 10,                 'weight': 25},
        {'gen': lambda: roll(10, 6) * 10 + 400,           'weight': 35},
        {'gen': lambda: roll(10, 4) * 50,                 'weight': 10}
    ]
    
    # Slopes (Shared relative weights? Or specific to type? Assuming shared for now)
    slope_choices = [
        {'name': "Steep Up",      'range': (51, 70),   'weight': 5},
        {'name': "Moderate Up",   'range': (31, 50),   'weight': 10},
        {'name': "Gentle Up",     'range': (15, 30),   'weight': 20},
        {'name': "Level",         'range': (-14, 14),  'weight': 30},
        {'name': "Gentle Down",   'range': (15, 30),   'weight': 20},
        {'name': "Moderate Down", 'range': (31, 50),   'weight': 10},
        {'name': "Steep Down",    'range': (51, 70),   'weight': 5},
    ]

    # Directions (Shared)
    dir_choices = [
        {'name': "Curving right",        'weight': 15},
        {'name': "Curving left",         'weight': 15},
        {'name': "Sharp right",          'weight': 5},
        {'name': "Sharp left",           'weight': 5},
        {'name': "Straight",             'weight': 40},
        {'name': "Twisting and snaking", 'weight': 20},
    ]

    # Illumination (Shared)
    illumination_choices = [
        {'name': "None",                                           'weight': 50},
        {'name': "Very weak (moonless)",                           'weight': 20},
        {'name': "Weak light (moonlight with overcast clouds)",     'weight': 15},
        {'name': "Moderate light (moonlight with no clouds)",      'weight': 10},
        {'name': "Bright light (twlight)",                         'weight': 5},
    ]

    # Air (Shared)
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

    if tunnel_type == 'dry':
        # Dry Specific Config
        
        # Dimensions (Standard Table)
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
        
        # Filter sizes
        size_choices = [s for s in size_choices_all if s['h'] >= min_height and s['w'] >= min_width]
        if not size_choices:
            print(f"Warning: No size options match min_height={min_height} and min_width={min_width}. Reverting to default list.")
            size_choices = size_choices_all

        # Textures
        texture_choices = [
            {'name': "Slick and polished",      'weight': 10},
            {'name': "Smooth",                  'weight': 15},
            {'name': "Normal",                  'weight': 30},
            {'name': "Rough",                   'weight': 15},
            {'name': "Tiered",                  'weight': 10},
            {'name': "Covered in large boulders", 'weight': 10},
            {'name': "Covered in sharp rocks",  'weight': 5},
        ]

        # Conditions
        condition_choices = [
            {'name': "Water-filled (up to 1' deep)",                 'weight': 5},
            {'name': "Slippery (wet and slimy)",                      'weight': 25},
            {'name': "Slick (damp or wet)",                           'weight': 45},
            {'name': "Dry, good looking",                             'weight': 20},
            {'name': "Dusty (dead tunnel check for cave-in chances)", 'weight': 5},
        ]

        # Attribute Map with Getters
        # Helper to make a getter for weighted choices
        def make_picker(choices):
            weights = [c['weight'] for c in choices]
            return lambda: random.choices(choices, weights=weights, k=1)[0]

        return {
            'len_choices': len_choices,
            'len_weights': [c['weight'] for c in len_choices],
            'attributes': {
                'size': {'getter': make_picker(size_choices), 'weight_in_change': 20},
                'slope': {'getter': make_picker(slope_choices), 'weight_in_change': 15},
                'dir': {'getter': make_picker(dir_choices), 'weight_in_change': 20},
                'tex': {'getter': make_picker(texture_choices), 'weight_in_change': 20},
                'cond': {'getter': make_picker(condition_choices), 'weight_in_change': 10},
                'air': {'getter': make_picker(air_choices), 'weight_in_change': 5},
                'illum': {'getter': make_picker(illumination_choices), 'weight_in_change': 5},
                'special': {'weight_in_change': 5}
            },
            'special_gen': gen_dry_special_feature
        }
    
    elif tunnel_type == 'wet':
        # Wet Specific Config
        
        # Size uses a custom generator (5d12 width)
        # Water Depth is new
        # Texture - assuming same as dry for now unless specified? 
        # But 'Dry' textures had "Slime/Polished". Let's reuse dry textures for now.
        
        texture_choices = [
            {'name': "Slick and polished",      'weight': 10},
            {'name': "Smooth",                  'weight': 15},
            {'name': "Normal",                  'weight': 30},
            {'name': "Rough",                   'weight': 15},
            {'name': "Tiered",                  'weight': 10},
            {'name': "Covered in large boulders", 'weight': 10},
            {'name': "Covered in sharp rocks",  'weight': 5},
        ]
        
        # Condition - Specific to wet?
        # User didn't specify condition table, but "Wet" implies water.
        # I'll use a placeholder getter or reuse a subset. 
        # Actually, let's just use the 'gen_wet_condition' placeholder defined above
        # or just label it "Submerged" if depth is high?
        # Let's stick to the 'gen_water_depth' as the primary differentiator and maybe a simple condition.
        # I will reuse the standard condition list BUT filter out "Dry" options?
        # "Water-filled", "Slippery", "Slick" make sense. "Dry", "Dusty" do not.
        wet_cond_choices = [
            {'name': "Water-filled",       'weight': 30},
            {'name': "Slippery (wet/slimy)", 'weight': 30},
            {'name': "Slick (damp/wet)",    'weight': 40},
        ]
        
        
        def make_picker(choices):
            weights = [c['weight'] for c in choices]
            return lambda: random.choices(choices, weights=weights, k=1)[0]

        # 1-15 None
        # 16-18 Very weak (moonless)
        # 19-20 Weak light (moonlight with overcast clouds)
        wet_illum_choices = [
            {'name': "None",                                       'weight': 15},
            {'name': "Very weak (moonless)",                       'weight': 3},
            {'name': "Weak light (moonlight with overcast clouds)", 'weight': 2},
        ]

        return {
            'len_choices': len_choices,
            'len_weights': [c['weight'] for c in len_choices],
            'attributes': {
                'size': {'getter': gen_wet_width, 'mutator': mutate_wet_width, 'weight_in_change': 4}, # 1-4 (4 slots)
                'water_depth': {'getter': gen_water_depth, 'weight_in_change': 2}, # 5-6 (2 slots)
                'ceiling_height': {'getter': gen_wet_ceiling, 'weight_in_change': 2}, # 7-8 (2 slots)
                'flow': {'getter': gen_flow_rate, 'weight_in_change': 4}, # 9-12 (4 slots)
                'dir': {'getter': make_picker(dir_choices), 'weight_in_change': 4}, # 13-16 (4 slots)
                'temp': {'getter': gen_water_temp, 'weight_in_change': 1}, # 17 (1 slot)
                'air': {'getter': make_picker(air_choices), 'weight_in_change': 1}, # 18 (1 slot)
                'illum': {'getter': make_picker(wet_illum_choices), 'weight_in_change': 1}, # 19 (1 slot)
                'special': {'weight_in_change': 1}, # 20 (1 slot)
                
            },
            'special_gen': gen_wet_special_feature
        }

def generate_tunnel(length_miles, tunnel_type='dry', min_height=0, min_width=0):
    total_feet = length_miles * 5280
    current_feet = 0
    sections = []
    total_elevation_change = 0
    
    # Load Configuration
    config = get_config(tunnel_type, min_height, min_width)
    attr_map = config['attributes']
    len_choices = config['len_choices']
    len_weights = config['len_weights']
    special_gen = config['special_gen']
    
    attr_keys = list(attr_map.keys())
    # Exclude 'special' from initial state generation loop as it's an event, not a persistent state usually?
    # In original code, 'special' was in the keys but used 'continue' in initialization loop.

    attr_change_weights = [attr_map[k]['weight_in_change'] for k in attr_keys]
    
    # Change Logic defined in code (Frequency)
    num_change_opts = [0, 1, 2, 3, 4, 5]
    num_change_weights = [25, 25, 15, 15, 10, 5]

    print(f"Generating {tunnel_type} tunnel of length {length_miles} miles ({total_feet:,.0f} feet)...")

    # Initial State
    state = {}
    for k in attr_keys:
        if k == 'special': continue
        state[k] = attr_map[k]['getter']()
    
    # Handle Slope Degree
    if 'slope' in state:
        min_deg, max_deg = state['slope']['range']
        state['degree'] = random.randint(min_deg, max_deg)

    while current_feet < total_feet:
        is_first = (len(sections) == 0)
        special_feature = None

        if not is_first:
            # Determine changes
            num_changes = random.choices(num_change_opts, weights=num_change_weights, k=1)[0]
            
            # Pick 'num_changes' unique attributes to change
            # We need to respect weights, so we can't just sample unique directly if we want weighted probability.
            # But standard way is loop N times. If we pick same one twice, does it count as 1 change or 2 (re-roll)?
            # Original code used random.choices k=1 in a loop of num_changes. 
            # It allowed picking same attribute multiple times (effectively just re-rolling it again).
            
            for _ in range(num_changes):
                attr_to_change = random.choices(attr_keys, weights=attr_change_weights, k=1)[0]
                
                if attr_to_change == 'special':
                    special_feature = special_gen()
                else:
                    attr_config = attr_map[attr_to_change]
                    
                    # Check for mutator (update based on previous value)
                    if 'mutator' in attr_config:
                        # Pass current state value
                        new_val = attr_config['mutator'](state[attr_to_change])
                    else:
                        # Standard re-roll
                        new_val = attr_config['getter']()
                        
                    state[attr_to_change] = new_val
                    
                    # Update dependent data (Slope Degree)
                    if attr_to_change == 'slope':
                        min_d, max_d = new_val['range']
                        state['degree'] = random.randint(min_d, max_d)
        
        # Length
        selected_len_gen = random.choices(len_choices, weights=len_weights, k=1)[0]
        section_len = selected_len_gen['gen']()
        
        # Check total
        remaining = total_feet - current_feet
        if section_len > remaining:
            section_len = int(remaining)

        # Elev Change
        elev_change = 0
        if 'slope' in state:
            effective_angle = state['degree']
            if "Down" in state['slope']['name']:
                effective_angle = -state['degree']
            elev_change = section_len * math.sin(math.radians(effective_angle))
            
        # Rate of Flow Drops
        if 'flow' in state and state['flow']['drop_ft_per_mile'] > 0:
            # Calculate portion of mile
            miles = section_len / 5280.0
            drop = miles * state['flow']['drop_ft_per_mile']
            elev_change -= drop # It's a drop-off, so subtract
            
        total_elevation_change += elev_change
        
        # Apply Special Feature Elevation Change
        if special_feature and special_feature.get('elev_change'):
             elev = special_feature['elev_change']
             elev_change += elev
             total_elevation_change += elev

        # Prepare New Section Object
        new_section = {
            'len': section_len,
            'elev': elev_change,
            'special': special_feature['desc'] if special_feature else None
        }
        # Copy current state attributes
        for k in state:
            new_section[k] = state[k]

        # Check for merge
        merged = False
        if len(sections) > 0:
            prev = sections[-1]
            
            # Detect if attributes match
            # We compare all keys in 'state' plus 'special'
            match = True
            if prev['special'] != new_section['special']:
                match = False
            else:
                for k in state:
                    if prev.get(k) != new_section[k]:
                        match = False
                        break
            
            if match:
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
        
        # Format Size
        # If Wet, calculate total height from water + ceiling
        h = s['size']['h']
        if 'water_depth' in s and 'ceiling_height' in s:
            h = s['water_depth']['depth_ft'] + s['ceiling_height']['height_ft']
            
        dim_str = s['size']['dim']
        if 'water_depth' in s and 'ceiling_height' in s:
            dim_str = f"{h}'x{s['size']['w']}'"

        size_str = f"{s['size']['name']} ({dim_str})"
        
        # Format Slope
        slope_str = ""
        if 'slope' in s:
            slope_str = f", {s['slope']['name']} ({s['degree']} deg)"
        
        # Optional Water Depth / Ceiling
        extra_str = ""
        if 'water_depth' in s:
            extra_str += f", Water: {s['water_depth']['name']}"
        if 'ceiling_height' in s:
            extra_str += f", Ceiling: {s['ceiling_height']['name']}"
        if 'flow' in s:
            extra_str += f", Flow: {s['flow']['name']} ({s['flow']['speed']})" 
            if s['flow']['drop_ft_per_mile'] > 0:
                 extra_str += f" [-{s['flow']['drop_ft_per_mile']}'/mi]"
        if 'temp' in s:
            extra_str += f", Temp: {s['temp']}"

        # Adjust comma logic for slope
        main_desc = f"{size_str}"
        if slope_str: main_desc += f"{slope_str}"
        
        # Format Texture/Condition (Conditional)
        tex_str = f", {s['tex']['name']}" if 'tex' in s else ""
        cond_str = f", {s['cond']['name']}" if 'cond' in s else ""

        print(f"Section {i+1}: {s['len']} feet, {main_desc}, {s['dir']['name']}{tex_str}{cond_str}{extra_str}, Light: {s['illum']['name']}, Air: {s['air']['name']} [Elev: {s['elev']:+.1f} ft]{special_txt}")

 

def gen_dry_special_feature():
    # Wrapper for legacy/dry logic returning dict
    desc = gen_special_feature_text_dry()
    if desc:
        return {'desc': desc, 'elev_change': 0}
    return None

def gen_special_feature_text_dry():
    # Original 'gen_special_feature' code logic
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
    
    if selected == "None": return None
        
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
            width = random.randint(5, 30)
            depth = random.randint(3, 15)
            return f"Blockage: Water way ({width}' wide x {depth}' deep)"
            
        return f"Blockage: {block_type}"
    
    if selected == "Habitation signs":
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

    return selected 

def gen_wet_special_feature():
    # 01-25 None
    # 26-31 Sandy Beaches
    # 32-40 Side ledges or tiers allowing landings
    # 41-46 Side rooms that are 90% likely to be dry (3-60' wide by 10d20x10' long)
    # 47-55 Side tunnels that dead-end in 1-6 miles that are 40% likely to be dry
    # 56-63 Obstacles/Blockages
    # 64-66 Rapids (in addition to any drop offs from rate of flow)
    # 69 Minor waterfalls (1-4) of 1-10' each
    # 70 Large waves from an earthqoake or cave-in
    # 71-75 Minor mineral vein
    # 76 Junction with large undergraound river or an exit or entrance to the surface
    # 77-78 Geothermal activity
    # 84-97 Habitation signs
    # 98-00 DM's Choice
    # GAPS: 67-68, 79-83 mapped to None
    
    r = random.randint(1, 100)
    
    if 1 <= r <= 25: return None
    if 26 <= r <= 31: return {'desc': "Sandy Beaches", 'elev_change': 0}
    if 32 <= r <= 40: return {'desc': "Side ledges or tiers allowing landings", 'elev_change': 0}
    
    if 41 <= r <= 46:
        is_dry = (random.randint(1, 100) <= 90)
        width = random.randint(3, 60)
        length = roll(10, 20) * 10
        cond = "Dry" if is_dry else "Wet"
        return {'desc': f"Side room ({cond}, {width}' wide x {length}' long)", 'elev_change': 0}
        
    if 47 <= r <= 55:
        is_dry = (random.randint(1, 100) <= 40)
        miles = random.randint(1, 6)
        cond = "Dry" if is_dry else "Wet"
        return {'desc': f"Side tunnel ({cond}, dead-ends in {miles} miles)", 'elev_change': 0}
        
    if 56 <= r <= 63:
        # Obstacles (Blockages d20)
        # 1-3 Large boulder field
        # 4-6 Minor Cave-in
        # 7-9 small whirlpool
        # 10-11 oil seepage forms scum on water
        # 12-18 Large stalactites, stlagmites, or columns
        # 19-20 DM's Choice
        b_roll = random.randint(1, 20)
        b_desc = "DM's Choice"
        if b_roll <= 3: b_desc = "Large boulder field"
        elif b_roll <= 6: b_desc = "Minor Cave-in"
        elif b_roll <= 9: b_desc = "Small whirlpool"
        elif b_roll <= 11: b_desc = "Oil seepage/scum on water"
        elif b_roll <= 18: b_desc = "Large stalactites, stalagmites, or columns"
        return {'desc': f"Blockage: {b_desc}", 'elev_change': 0}
        
    if 64 <= r <= 66:
        # Rapids
        drop = random.randint(5, 10) # Assumed extra drop
        return {'desc': "Rapids", 'elev_change': -drop}
        
    if 67 <= r <= 68: return None
    
    if r == 69:
        # Minor waterfalls (1-4) of 1-10' each
        count = random.randint(1, 4)
        total_drop = sum(random.randint(1, 10) for _ in range(count))
        return {'desc': f"Minor waterfalls ({count} drops, total {total_drop}')", 'elev_change': -total_drop}
        
    if r == 70: return {'desc': "Large waves (earthquake/cave-in)", 'elev_change': 0}
    if 71 <= r <= 75: return {'desc': "Minor mineral vein", 'elev_change': 0}
    if r == 76: return {'desc': "Junction with large underground river/exit/entrance", 'elev_change': 0}
    
    if 77 <= r <= 78:
        # Geothermal (d20)
        # 1-8 hot or boiling water
        # 9-10 poisonous/noxious gas
        # 11-14 Steam vent
        # 15-20 Hot Air
        g_roll = random.randint(1, 20)
        g_desc = "Hot Air"
        if g_roll <= 8: g_desc = "Hot or boiling water"
        elif g_roll <= 10: g_desc = "Poisonous/noxious gas"
        elif g_roll <= 14: g_desc = "Steam vent"
        return {'desc': f"Geothermal: {g_desc}", 'elev_change': 0}
        
    if 79 <= r <= 83: return None
    
    if 84 <= r <= 97:
        # Habitation (d100)
        h_roll = random.randint(1, 100)
        h_desc = "DM's Choice"
        if h_roll <= 10: h_desc = "Cairn marking territory"
        elif h_roll <= 13: h_desc = "Ruined building"
        elif h_roll <= 25: h_desc = "Old campsite"
        elif h_roll <= 29: h_desc = "Small abandoned shrine"
        elif h_roll <= 34: h_desc = "Dead bodies"
        elif h_roll <= 36: h_desc = "Shallow grave on land"
        elif h_roll == 37: h_desc = "Secret stash"
        elif h_roll == 38: h_desc = "Dam"
        elif h_roll <= 41: h_desc = "Canal"
        elif h_roll <= 59: h_desc = "Flotsam/jetsam"
        elif h_roll <= 63: h_desc = "Intact tools, weapons, armor"
        elif h_roll <= 74: h_desc = "Worked stone surfaces"
        elif h_roll <= 80: h_desc = "Abandoned adventurers gear"
        return {'desc': f"Habitation: {h_desc}", 'elev_change': 0}
        
    # 98-00
    return {'desc': "DM's Choice!", 'elev_change': 0}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a tunnel description.")
    parser.add_argument("length", type=float, help="Total length of the tunnel in miles")
    parser.add_argument("--type", choices=['dry', 'wet'], default='dry', help="Type of tunnel (dry or wet)")
    parser.add_argument("--min-height", type=int, default=0, help="Minimum height in feet")
    parser.add_argument("--min-width", type=int, default=0, help="Minimum width in feet")
    
    args = parser.parse_args()
    
    generate_tunnel(args.length, args.type, args.min_height, args.min_width)
