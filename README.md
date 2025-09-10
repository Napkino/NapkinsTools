# Setup
1. To run these programs, you must have Python installed. To download Python go to [this website](https://www.python.org/downloads/) and download the latest release. Then, run the installer and restart your computer for its changes to take effect.
2. Its reccomended you intall git, so that you can pull down updates to the project and script(s) easily. To do so, go to [this link](https://git-scm.com/downloads) and get the relevent version, and run the installer.
3. If you do not have an IDE, you must download one. I reccomend [Visual Studio Code](https://code.visualstudio.com/) for a mission builders needs.
4. Open Visual Studio Code, if it isnt already open, and hit Ctrl+Shift+P to open the command pallete. Type "clone" and click on the command "Git: Clone". then enter this link "https://github.com/Napkino/AtomicBuilder.git" and hit enter. If that link does not work, you have to get a new link to clone the repository from. Look that up, cause that shouldnt happen and i dont feel like writting about it anymore.
5. Change the config variables found in `Config.py` to work for you, these entail mission name, which **must** be changed to match the mission name of the mission you want to change with these scripts, aliases of various things (i.e. activationKeyword, current location aliases, etc.) The use of those is slightly detailed below. Make sure to read these

## Using Actions
1. To use actions you need to have an object that has a name following a specific format.
2. First, the name has to have the "activation keyword" by default its atomicBuild
3. Then, you must put down the seperator, "_" this tells the program what is one thing and what is not.
4. Then, you must provide the operation you want to perform. (e.g. paste)
5. After that, you have to provide the paramaters that the specific operation requires. (e.g. paste requires a preset name and paste center coordinates.)
6. Below is an example request. This request will paste an archangel class heli-carrier, onto a units position. 
<pre>atomicBuild_paste_archangel_CURR|LOC
    ^keyword  ^action ^preset name  ^paste center coords (in this case CURR|LOC is used)
     This request, when parsed by the program, will run a paste action, pasting an arch-angel class helicarrier (currently a default blueprint), on the named units current location. </pre>

## Notes on Actions
* Most actions work in an **area** or **radius**, meaning they affect everything inside a zone, such as `createBlueprint`. This action takes in a few paramaters, those being a radius, a center, and the final blueprint name.
    * The radius is the distance in Meters around the center inside which units will be considered apart of the blueprint. 
    * The center is the center of the blueprint. It can be either the name of an airbase, or any "current location" alias (i.e. CURR|LOC, curr|loc, currloc etc.)
* Before any action is performed, a backup of the mission JSON file as-is is made and dumped in the backups directory, included by default. This is your last resort if something goes wrong (DM Napkin on the discord if something does go wrong)

## What to do if something goes wrong
1. Take a screenshot of the error, including the stacktrace (if you dont know what I mean by that, just screenshot everything, or copy it into a .txt file using notepad.)
2. DM Napkin on discord (username is napkin20) that information, your mission file, your config file, and an explanation of what you were doing. If you dont do this, I dont know the bug you found exists, so I cant fix it.
    * The mission file can be found in your User Folder, the path to which is also in the ``Config.py`` file.
3. Replace the bugged mission file with the backup automatically created in the `backups` directory in the project by default.
