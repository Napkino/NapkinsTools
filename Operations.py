import json, os, inspect
import Utils as utils

LOCAL_LOW_APPDATA_PATH = os.getenv('LOCALAPPDATA')
LOCAL_LOW_APPDATA_PATH += "Low"
### USER CONFIG VARIABLES-----------------------------------------------------------------------------

# The path to where Nuclear Option stores missions.
NUCLEAR_OPTION_MISSION_FOLDER_PATH = f"{LOCAL_LOW_APPDATA_PATH}\\Shockfront\\NuclearOption\\Missions"

# The name of the mission you want to edit
MISSION_NAME = "ATFOP-Archangel"

# You can include any combination of ONLY the following, NOTHING ELSE: 'vehicles' 'ships' 'airbases' 'buildings' 'aircraft'
CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS = ('vehicles', 'ships', 'airbases', 'buildings', 'aircraft') # you really shouldnt need to touch this

# The prefix you must use for the objects you want to use to interact with these scripts.
ACTIVATION_PHRASE = "AtomicBuild"

### END USER CONFIG VARIABLES--------------------------------------------------------------------------

class operation:
    def __init__(self):
        pass


OPERATIONS = {
    'paste' : lambda mission_name, preset_name, paste_center_coords: paste_preset(mission_name, preset_name, paste_center_coords), 
    'removeAllOutside': lambda mission_name, zone_radius_meters, center: remove_all_outside_zone(open_mission_json(mission_name), zone_radius_meters, center)}

print(f"Missons stored at: {NUCLEAR_OPTION_MISSION_FOLDER_PATH}")
print(f"Presets stored in the Presets directory attached to this project.")



DEFAULT_ATOMIC_BUILDER_INFO = {'origin':(0,0,0), 'NextPasteCode':0}

def open_mission_json(mission_name : str):
    with open(f'{NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{mission_name}\\{mission_name}.json') as file:
        data = json.load(file)
    return data

def get_objs_in_zone(obj_list, key : str, center : tuple[float, float, float], zone_radius_meters : float):
    objs = list()
    for obj in obj_list[key]:
        if utils.dist_3d(utils.json_get_coords(obj), center) < zone_radius_meters:
            objs.append(obj)
    return objs

def remove_all_outside_zone(data, zone_radius_meters : float, center : str | tuple[float, float, float]):
    center_coords = (0, 0, 0)
    match center:
        case tuple():
            center_coords = center
        case str():
            for airbase in data['airbases']:
                if airbase['DisplayName'] == center:
                    center_coords = utils.json_get_coords(airbase)
                    break
    for category in CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS:
        data[category] = get_objs_in_zone(data, category, center_coords, zone_radius_meters)

    return data

def get_preset_data(preset_name : str):
    with open(f"Presets\\{preset_name}\\{preset_name}.json") as file:
        data = json.load(file)
    preset = {'objectives':data['objectives'], 'AtomicBuilderInfo':data['AtomicBuilderInfo']}
    for cat in CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS:
        preset[cat] = data[cat]
    for key in DEFAULT_ATOMIC_BUILDER_INFO:
        if not key in preset['AtomicBuilderInfo']:
            preset['AtomicBuilderInfo'][key] = DEFAULT_ATOMIC_BUILDER_INFO[key]
    return preset

def change_objects_origin(obj_list, origin : tuple[float, float, float], key : str):
    rel_objs = list()
    for obj in obj_list[key]:
        if 'globalPosition' in obj:
            obj['globalPosition'] = utils.json_format_coords(utils.find_relative_position(utils.json_get_coords(obj), origin))
        elif 'SelectionPosition' in obj: # means its an airbase, so we want to move both of these
            obj['SelectionPosition'] = utils.json_format_coords(utils.find_relative_position(utils.json_get_coords(obj), origin))
            obj['Center'] = utils.json_format_coords(utils.find_relative_position(utils.json_get_coords(obj, 'Center'), origin))
        rel_objs.append(obj)
    return rel_objs

def assign_paste_codes(data):
    # we keep track of what paste codes we've assigned so far to this file, and we just count up from there.
    if not 'AtomicBuilderInfo' in data:
        data['AtomicBuilderInfo'] = DEFAULT_ATOMIC_BUILDER_INFO
    suffix = f"_ATOM_PASTE_{data['AtomicBuilderInfo']['NextPasteCode']}"
    data['AtomicBuilderInfo']['NextPasteCode'] +=1

    for cat in CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS:
        for obj in data[cat]:
            if 'UniqueName' in obj:
                obj['UniqueName'] += suffix
            if 'Airbase' in obj and obj['Airbase'] != '':
                obj['Airbase'] += suffix

    # now we have to modify specific objectives to have different names. this gets messy.
    for objective in data['objectives']['Objectives']:
        outcomes = list()
        for outcome in objective['Outcomes']:
            outcome += suffix
            outcomes.append(outcome)
        objective['Outcomes'] = outcomes
        if objective['UniqueName'] == 'Mission Start':# we combine the mission start objectives down the line.
            continue
        else:
            objective['UniqueName'] += suffix
        
    for outcome in data['objectives']['Outcomes']:
        outcome['UniqueName'] += suffix
        for outcome_data in outcome['Data']:
            if outcome_data['StringValue'].startswith("Boscali"):
                continue
            elif outcome_data['StringValue'].startswith("Primeva"):
                continue
            elif outcome_data['StringValue'] == "":
                continue
            outcome_data['StringValue'] += suffix
    return data


def paste_preset(mission_name : str, preset_name : str, paste_center_coords : tuple[float, float, float]):
    data = get_preset_data(preset_name)
    origin = utils.sub_coordinates(data['AtomicBuilderInfo']['origin'], paste_center_coords)
    preset = {'objectives' : data['objectives'], 'AtomicBuilderInfo':data['AtomicBuilderInfo']}
    for cat in CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS:
        objs = change_objects_origin(data, origin, cat)
        preset[cat] = objs
    

    data = open_mission_json(mission_name)
    if not 'AtomicBuilderInfo' in data: # if we dont have our info in the mission file, then we chuck the default in.
        data['AtomicBuilderInfo'] = DEFAULT_ATOMIC_BUILDER_INFO

    data['AtomicBuilderInfo']['NextPasteCode'] = max(data['AtomicBuilderInfo']['NextPasteCode'], preset['AtomicBuilderInfo']['NextPasteCode'])+1
    preset['AtomicBuilderInfo']['NextPasteCode'] = data['AtomicBuilderInfo']['NextPasteCode']
    
    preset = assign_paste_codes(preset)
    data['AtomicBuilderInfo']['NextPasteCode'] +=1
    for cat in CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS:
        for obj in preset[cat]:
            data[cat].append(obj)
    mission_objectives = data['objectives']['Objectives']

    for preset_objective in preset['objectives']['Objectives']:
        if preset_objective['UniqueName'] == 'Mission Start':# we combine the start objectives, so that everything the op builder wanted to happen first, happens.
            for mission_objective in mission_objectives:
                if mission_objective['UniqueName'] == 'Mission Start':
                    mission_objective['Outcomes'].extend(preset_objective['Outcomes'])
        else:
            mission_objectives.append(preset_objective)
    data['objectives']['Outcomes'].extend(preset['objectives']['Outcomes'])

    return data
    



def create_preset(mission_name : str, preset_radius : float, center : str | tuple[float,float,float] | None = None, final_preset_name : str | None = None):
    with open(f"{NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{mission_name}\\{mission_name}.json") as file:
        data = json.load(file)

    origin = (0,0,0)
    match center:
        # if the center is a string they gave us an airbase as the center, so we set its center as the origin.
        case str():
            for airbase in data['airbases']:
                if airbase['DisplayName'] == center:
                    origin = utils.json_get_coords(airbase, 'SelectionPosition')
                    break
        # if the center is a tuple of 3 floats, they gave us the origin in X Y Z coords.
        case tuple():
            origin = center
        # if center is None, then they didnt give us one, and we have to average one out.
        case _:
            obj_num = 0
            total_x = 0.0
            total_y = 0.0
            total_z = 0.0
            for category in CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS:
                for obj in data[category]:
                    coords = utils.json_get_coords(obj)
                    if coords[0] == None:
                        continue
                    total_x += coords[0]
                    total_y += coords[1]
                    total_z += coords[2]
                    obj_num += 1
            # coords are stored out to 12 decimals in the json files, so we round them here.
            origin = (round(total_x / obj_num, 12), round(total_y / obj_num, 12), round(total_z / obj_num, 12))
    
    preset_data = remove_all_outside_zone(data, preset_radius, origin)
    if final_preset_name == None:
        final_preset_name = mission_name
    preset_dir = f"Presets\\{final_preset_name}"
    if not os.path.isdir(preset_dir):
        os.mkdir(preset_dir)
    # storing info we want for down the line.
    if not 'AtomicBuilderInfo' in preset_data:
        preset_data['AtomicBuilderInfo'] = DEFAULT_ATOMIC_BUILDER_INFO
    preset_data['AtomicBuilderInfo']['origin'] = origin
    # creates a Nuclear Option openable version of the preset in the local presets directory, so that we can store them ourselves.
    json.dump(preset_data, open(f"{preset_dir}\\{final_preset_name}.json", 'w', encoding='UTF-8'), indent=4)
    json.dump({"FileName":final_preset_name}, open(f"{preset_dir}\\meta.json", 'w', encoding='UTF-8'), indent=4)

def create_backup(mission_name : str):
    json.dump(open_mission_json(mission_name), open(f'{mission_name}_Backup.json', 'w', encoding='UTF-8'), indent=4)

def dump_mission(data, mission_name):
    json.dump(data, open(f'{NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{mission_name}\\{mission_name}.json', 'w', encoding='UTF-8'), indent=4)

def parse_requests(mission_name : str):
    create_backup(mission_name)
    data = open_mission_json(mission_name)
    for cat in CATEGORIES_OF_OBJECTS_INCLUDED_IN_PRESETS:
        for obj in data[cat]:
            if not 'UniqueName' in obj:
                continue
            name = obj['UniqueName']
            if not name.startswith(ACTIVATION_PHRASE):
                continue
            split : list[str] = name.split('_')
            if len(split) < 3:
                print(f"Malformed request. | Request cannot contain sufficient information. | Unique name: {name}")
                continue
            split.pop(0) # get rid of activation phrase
            requested_op = split.pop(0)
            args = split
            if not requested_op in OPERATIONS:
                continue
            if len(args) != len(inspect.signature(OPERATIONS[requested_op]).parameters)-1:
                # if theres a single additional argument, its likely that the paste is either grouped in with other pastes, which is assumed, or its malformed.
                if len(args) == len(inspect.signature(OPERATIONS[requested_op]).parameters):
                    args.pop()
                else:
                    print(f"Malformed request. | Request does not match number of parameters required for requested operation. | Unique name: {name}")
            # this allows the user to put "CURR|LOC" in for the location, and have it swapped out for the objects location
            for i in range(len(args)):
                arg = args[i]
                if type(arg) is str:
                    if arg == "CURR|LOC":
                        args[i] = utils.json_get_coords(obj)
            print(f"Performing operation. Operation: {requested_op} | Args: {args}")
            done = OPERATIONS[requested_op](mission_name, *args)
            done[cat].remove(obj)
            dump_mission(done, mission_name)
            print("Looping back through again.")
            return parse_requests(mission_name)



create_backup(MISSION_NAME)
parse_requests(MISSION_NAME)
print("Done :)")
# pasted = paste_preset(MISSION_NAME, "archangel", (1000,5000,0))
# json.dump(pasted, open(f'{NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{MISSION_NAME}\\{MISSION_NAME}.json', 'w', encoding='UTF-8'), indent=4)
# pasted = paste_preset(MISSION_NAME, "archangel", (2000,7000,0))
# json.dump(pasted, open(f'{NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{MISSION_NAME}\\{MISSION_NAME}.json', 'w', encoding='UTF-8'), indent=4)

