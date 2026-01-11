import subprocess
from core.path import DEMON_EXE

def toggle_demon_mode(enabled):
    if not enabled:
        print("Demon Mode: DISABLED — App access restricted to safe paths.")
        return

    print("Demon Mode: ENABLED — Demo launch requested.")

    if not DEMON_EXE.exists():
        print("Demon EXE not found:", DEMON_EXE)
        return

    subprocess.Popen(
        [str(DEMON_EXE)],
        shell=False,
        creationflags=subprocess.DETACHED_PROCESS
    )
