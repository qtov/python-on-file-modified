from cx_Freeze import setup, Executable

base = None    

executables = [Executable("log_timer_gta.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "log_timer_gta",
    options = options,
    version = "0.1",
    description = 'Triannon m8!',
    executables = executables
)