import math
import Config as config

def dist_3d(first_point : tuple[float, float, float], second_point : tuple[float, float, float]) -> float:
    if first_point[0] == None:
        return 0
    return math.sqrt(pow(second_point[0] - first_point[0], 2) + pow(second_point[1] - first_point[1], 2) + pow(second_point[2] - first_point[2], 2))

def find_relative_position(coords : tuple[float, float, float], origin : tuple[float, float, float]):
    return (coords[0] - origin[0], coords[1] - origin[1], coords[2] - origin[2])

def json_format_coords(coords: tuple[float,float,float]) -> dict[str:float]:
    return {
                "x": coords[0],
                "y": coords[1],
                "z": coords[2]
            }

def json_get_coords(obj, key : str | None = None) -> tuple[float,float,float]:

    if key == None:
        if 'globalPosition' in obj:
            position = obj['globalPosition']
            return (position['x'], position['y'], position['z'])
        elif 'SelectionPosition' in obj:
            center = obj['SelectionPosition']
            return (center['x'], center['y'],center['z'])
        return (None,None,None)
    position = obj[key]
    return (position['x'],position['y'],position['z'])

def add_coordinates(first_point : tuple[float,float,float], second_point : tuple[float,float,float]) -> tuple[float,float,float]:
    return (first_point[0] + second_point[0], first_point[1] + second_point[1], first_point[2] + second_point[2])

def sub_coordinates(first_point : tuple[float,float,float], second_point : tuple[float,float,float]) -> tuple[float,float,float]:
    return (first_point[0] - second_point[0], first_point[1] - second_point[1], first_point[2] - second_point[2])

def find_airbase_obj(data, airbase_name):
    for airbase in data['airbases']:
        name = airbase['UniqueName']
        if name == airbase_name:
            return airbase
    return None

def get_paste_code(data):
    paste_code = 0
    for cat in config.CATEGORIES_OF_OBJECTS_TO_MANIPULATE:
        for obj in data[cat]:
            if not 'UniqueName' in obj:
                continue
            name : str = obj['UniqueName']
            split = name.split('_')
            last = split[len(split)-1]
            if last.isnumeric():
                if paste_code < int(last):
                    paste_code = int(last)
    for objective in data['objectives']['Objectives']:
        if not 'UniqueName' in obj:
            continue
        name : str = obj['UniqueName']
        split = name.split('_')
        last = split[len(split)-1]
        if not last.isnumeric():
            continue
        if paste_code < int(last):
            paste_code = int(last)
        for outcome in objective['Outcomes']:
            split = outcome.split('_')
            last = split[len(split)-1]
            if not last.isnumeric():
                continue
            if paste_code < int(last):
                paste_code = int(last)
    paste_code += 1
    return paste_code
