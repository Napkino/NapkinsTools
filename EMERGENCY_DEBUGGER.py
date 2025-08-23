import json, os

LOCAL_LOW_APPDATA_PATH = os.getenv('LOCALAPPDATA')
LOCAL_LOW_APPDATA_PATH += "Low"
### USER CONFIG VARIABLES-----------------------------------------------------------------------------

# The path to where Nuclear Option stores missions.
NUCLEAR_OPTION_MISSION_FOLDER_PATH = f"{LOCAL_LOW_APPDATA_PATH}\\Shockfront\\NuclearOption\\Missions"
# this is the path to the file you need to fix.
PATH_TO_FILE_TO_DEBUG = f'ATFOP-Archangel_Backup.json'

CATEGORIES_TO_DEBUG = ('vehicles', 'ships', 'airbases', 'buildings', 'aircraft')

### END USER CONFIG VARIABLES---------------------------------

def check_for_duplicated_unique_names():
    with open(PATH_TO_FILE_TO_DEBUG, 'r', encoding='UTF-8') as file:
        data = json.load(file)
    unique_names = list()
    duplicated_names = list()
    fixed_data = data
    for cat in CATEGORIES_TO_DEBUG:
            if cat in data:
                fixed_data[cat] = list()
                for obj in data[cat]:
                    if 'UniqueName' in obj:
                        uniqueName = obj['UniqueName']
                        for name in unique_names:
                            if name == uniqueName:
                                duplicated_names.append(uniqueName)
                                print("Duplicated name found. Correcting.")
                                obj['UniqueName'] = uniqueName+f"_ATOM_E_DEBUG_{len(duplicated_names)}"
                        unique_names.append(uniqueName)
    print(f"Duplicated names: {duplicated_names}")


check_for_duplicated_unique_names()