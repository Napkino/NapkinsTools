import json, os, inspect, random
import Config as config
import Utils as utils

#NOTE: Mission name is a common requirment between all actions, and is NOT required in the name of the unit, as it is a constant you set in the config.
ACTIONS = {
    'paste' : lambda mission_name, blueprint_name, paste_center_coords: paste_blueprint(mission_name, blueprint_name, paste_center_coords),
    'createBlueprint' : lambda mission_name, blueprint_radius, center, final_blueprint_name: create_blueprint(mission_name, blueprint_radius, center, final_blueprint_name),
    'groupToOutcome' : lambda mission_name, group_radius, center, unit_to_group: group_into_outcome(mission_name, group_radius, center, unit_to_group),
    'removeAllOutsideZone': lambda mission_name, zone_radius_meters, center: remove_all_outside_zone(open_mission_json(mission_name), zone_radius_meters, center)}

print(f"Missons stored at: {config.NUCLEAR_OPTION_MISSION_FOLDER_PATH}")
print(f"blueprints stored in the blueprints directory attached to this project.")

DEFAULT_ATOMIC_BUILDER_INFO = {'origin':(0,0,0)}

def open_mission_json(mission_name : str):
    try:
        with open(f'{config.NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{mission_name}\\{mission_name}.json') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print("OPEN MISSION JSON ERROR, EXITING")
        exit(0)

def create_backup(mission_name : str):
    try:
        os.makedirs('backups', exist_ok=True)
        with open(f'{config.NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{mission_name}\\{mission_name}.json', 'r', encoding='UTF-8') as file:
            data = file.read()
            file.close()
        with open(f'backups\\{mission_name}.json', 'w', encoding='UTF-8') as backup:
            backup.write(data)
            backup.close()
    except Exception as e:
        print("MAKING BACKUP SCREWED UP")

def dump_mission(data, mission_name):
    try:
        json.dump(data, open(f'{config.NUCLEAR_OPTION_MISSION_FOLDER_PATH}\\{mission_name}\\{mission_name}.json', 'w', encoding='UTF-8'), indent=4)
    except Exception as e:
        print("DUMP MISSION ERROR")

def get_objs_in_zone(obj_list, key : str, center : tuple[float, float, float], zone_radius_meters : float):
    objs = list()
    if type(zone_radius_meters) is not float:
        zone_radius_meters = float(zone_radius_meters)
    for obj in obj_list[key]:
        if utils.dist_3d(utils.json_get_coords(obj), center) < zone_radius_meters:
            objs.append(obj)
    return objs

def remove_all_outside_zone(mission_name, zone_radius_meters : float, center : str | tuple[float, float, float]):
    data = open_mission_json(mission_name)
    center_coords = (0, 0, 0)
    match center:
        case tuple():
            center_coords = center
        case str():
            for airbase in data['airbases']:
                if airbase['DisplayName'] == center:
                    center_coords = utils.json_get_coords(airbase)
                    break
    try:
        for category in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
            data[category] = get_objs_in_zone(data, category, center_coords, zone_radius_meters)
    except Exception as e:
        print("GETTING OBJECTS IN THE ZONE SCREWED UP")
        exit(0)
    dump_mission(data, mission_name)

def get_blueprint_data(blueprint_name : str):
    with open(f"Blueprints\\{blueprint_name}.json") as file:
        return json.load(file)

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

def assign_paste_codes(data, paste_code : int | None = None):
    # we keep track of what paste codes we've assigned so far to this file, and we just count up from there.
    if paste_code is None:
        paste_code = random.randint(100,10000)
    suffix = f"_ATOM_PASTE_{paste_code}"

    for cat in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
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


def paste_blueprint(mission_name : str, blueprint_name : str, paste_center_coords : tuple[float, float, float]):
    data = get_blueprint_data(blueprint_name)
    origin = utils.sub_coordinates(data['AtomicBuilderInfo']['origin'], paste_center_coords)
    blueprint = {'objectives' : data['objectives'], 'AtomicBuilderInfo':data['AtomicBuilderInfo']}
    for cat in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
        objs = change_objects_origin(data, origin, cat)
        blueprint[cat] = objs
    

    data = open_mission_json(mission_name)
    if not 'AtomicBuilderInfo' in data: # if we dont have our info in the mission file, then we chuck the default in.
        data['AtomicBuilderInfo'] = DEFAULT_ATOMIC_BUILDER_INFO
    blueprint = assign_paste_codes(blueprint, utils.get_paste_code(data))
    for cat in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
        for obj in blueprint[cat]:
            data[cat].append(obj)
    mission_objectives = data['objectives']['Objectives']

    for blueprint_objective in blueprint['objectives']['Objectives']:
        if blueprint_objective['UniqueName'] == 'Mission Start':# we combine the start objectives, so that everything the op builder wanted to happen first, happens.
            for mission_objective in mission_objectives:
                if mission_objective['UniqueName'] == 'Mission Start':
                    mission_objective['Outcomes'].extend(blueprint_objective['Outcomes'])
        else:
            mission_objectives.append(blueprint_objective)
    data['objectives']['Outcomes'].extend(blueprint['objectives']['Outcomes'])

    return data

def group_into_outcome(mission_name : str, group_radius : float, center : tuple[float,float,float], units_to_group : str):
    data = open_mission_json(mission_name)
    paste_code = utils.get_paste_code(data)
    # If units_to_group is 'ALL' then the user wants to capture everything in the zone, so we leave that intact.
    if not units_to_group == 'ALL':
        units_to_group = units_to_group.split(',')
        # replace unit filters with actual names, in case any were aliases / nicknames
        for i in range(len(units_to_group)):
            if units_to_group[i] in config.UNIT_ALIASES:
                units_to_group[i] = config.UNIT_ALIASES[units_to_group[i]]
    objs_in_group = []
    for cat in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
        objs_in_cat_zone = get_objs_in_zone(data,cat,center,group_radius)
        for obj in objs_in_cat_zone:
            if units_to_group == 'ALL':
                objs_in_group.append(obj)
                continue
            elif 'type' not in obj:
                continue
            elif obj['type'] in units_to_group:
                objs_in_group.append(obj)
    outcome_data = list()
    for obj in objs_in_group:
        if not 'UniqueName' in obj:
            continue
        # put units into standard NO outcome data format
        outcome_data.append({"StringValue": obj['UniqueName'], "FloatValue": 0.0, "VectorValue": {"x": 0.0,"y": 0.0,"z": 0.0}})
    outcome = {"UniqueName":f"ATOMIC_BUILDER_OutcomeGroup_{paste_code}", "Type":5, "TypeName": "SpawnUnit", "Data": outcome_data}
    os.makedirs('Outputs', exist_ok=True)
    json.dump(outcome, open(f'Outputs\\OUTCOME_CENTER_{center}.json','w',encoding='UTF-8'),indent=4) # dumps it for them to copy
    data['objectives']['Outcomes'].append(outcome)
    dump_mission(data, mission_name)

def create_blueprint(mission_name : str, blueprint_radius : float, center : str | tuple[float,float,float] | None = None, final_blueprint_name : str | None = None):
    data = open_mission_json(mission_name)
    print("STARTING TO MAKE BLUEPRINT")
    origin = (0,0,0)
    match center:
        # if the center is a string they gave us an airbase as the center, so we set its center as the origin.
        case str():
            for airbase in data['airbases']:
                if airbase['UniqueName'] == center:
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
            for category in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
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
    print("FOUND ORIGIN")
    try:
        blueprint_data = remove_all_outside_zone(data, blueprint_radius, origin)
    except Exception as e:
        print("REMOVING ALL DID SOMETHING WRONG")
        exit(0)
    if final_blueprint_name == None:
        final_blueprint_name = mission_name
    # storing info we want for down the line.
    if not 'AtomicBuilderInfo' in blueprint_data:
        blueprint_data['AtomicBuilderInfo'] = DEFAULT_ATOMIC_BUILDER_INFO
    blueprint_data['AtomicBuilderInfo']['origin'] = origin
    print(f"ORIGIN: {origin}")
    # creates a Nuclear Option openable version of the blueprint in the local blueprints directory, so that we can store them ourselves.
    json.dump(blueprint_data, open(f"Blueprints\\{final_blueprint_name}.json", 'w', encoding='UTF-8'), indent=4)
    print("DUMPED THINGY")
    exit(0)#FUCK IT, WERE EXITING THE PROGRAM, ONLY ONE AT A TIME

def parse_requests(mission_name : str):
    data = open_mission_json(mission_name)
    for cat in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
        for obj in data[cat]:
            if not 'UniqueName' in obj:
                continue
            name = obj['UniqueName']
            if not name.startswith(config.ACTIVATION_KEYWORD):
                continue
            split : list[str] = name.split('_')
            if len(split) < 3:
                print(f"Malformed request. | Request cannot contain sufficient information. | Unique name: {name}")
                continue
            split.pop(0) # get rid of activation phrase
            requested_action = split.pop(0)
            args = split
            if not requested_action in ACTIONS:
                continue
            # The arguments should be one less than the actions required args, as it doesnt include the mission name.
            if len(args) != len(inspect.signature(ACTIONS[requested_action]).parameters)-1:
                # if theres a single additional argument, its likely that the action is either grouped in with other similair actions, or its malformed.
                if len(args) == len(inspect.signature(ACTIONS[requested_action]).parameters):
                    args.pop()
                else:
                    print(f"Malformed request. | Request does not match number of parameters required for requested action. | Unique name: {name}")
            # this allows the user to put "CURR|LOC" in for the location, and have it swapped out for the objects location
            for i in range(len(args)):
                arg = args[i]
                if type(arg) is str:
                    if arg in config.CURRENT_LOCATION_ALIASES: # using an alias of current location means the user wants to replace this arg with the objects location.
                        args[i] = utils.json_get_coords(obj)
            print(f"Performing action. Action: {requested_action} | Args: {args}")
            # Remove object we got the request from the file, since it could be in the way of the action.
            data[cat].remove(obj)
            dump_mission(data, mission_name)
            done = ACTIONS[requested_action](mission_name, *args)
            if done is not None:
                dump_mission(done, mission_name)
            return parse_requests(mission_name)

create_backup(config.MISSION_NAME)
print("Backup Created")
try:
    parse_requests(config.MISSION_NAME)
except Exception as e:
    print("Something in parsing screwed up")
print("Done :)")