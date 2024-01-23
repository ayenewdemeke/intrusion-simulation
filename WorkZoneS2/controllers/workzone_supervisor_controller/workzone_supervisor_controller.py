from controller import Supervisor
import threading
from playsound import playsound
import time

# Function to play beep in a separate thread
def play_beep():
    playsound('alert.mp3')

# Initialize Supervisor
supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

cone_nodes = [supervisor.getFromDef(f"SCONE{i+1}") for i in range(7)]
cone_hit_times = [None] * len(cone_nodes)  # Track when each cone is hit
time_gap = 10  # Time gap in seconds to check for multiple hits

alert_triggered = False
start_time = supervisor.getTime()

while supervisor.step(timestep) != -1:
    current_time = supervisor.getTime()

    for i, cone in enumerate(cone_nodes):
        if cone and cone.getField("customData").getSFString() == "moved" and cone_hit_times[i] is None:
            cone_hit_times[i] = current_time

    # Check if multiple cones were hit within the time gap
    hit_cones = [t for t in cone_hit_times if t is not None and current_time - t < time_gap]
    if len(hit_cones) > 1 and not alert_triggered:
        threading.Thread(target=play_beep).start()
        alert_triggered = True
        print("Alert! A vehicle intruded the work zone!") 