import math

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