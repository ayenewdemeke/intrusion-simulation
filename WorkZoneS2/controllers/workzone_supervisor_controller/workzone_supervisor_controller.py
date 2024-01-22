from controller import Supervisor
import threading
from playsound import playsound

# Function to play beep in a separate thread
def play_beep():
    playsound('alert.mp3')

# Initialize Supervisor
supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

# Assuming cones are named CONE1, CONE2, etc.
cone_nodes = [supervisor.getFromDef(f"SCONE{i+1}") for i in range(7)]
print(cone_nodes[0].getField("customData").getSFString())

# Main loop
alert_triggered = False  # Flag to track if alert has been triggered
start_time = supervisor.getTime()

while supervisor.step(timestep) != -1:
    current_time = supervisor.getTime()
    if current_time - start_time < 5:
        continue  # Skip the first 5 seconds

    moved_cones = sum(1 for cone in cone_nodes if cone and cone.getField("customData").getSFString() == "moved")

    if moved_cones > 1 and not alert_triggered:  # Check if more than one cone has moved and alert not triggered
        threading.Thread(target=play_beep).start()  # Play beep in a non-blocking manner
        alert_triggered = True  # Set the flag as alert has been triggered