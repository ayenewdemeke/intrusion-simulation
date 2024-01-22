from controller import Supervisor
import threading
import winsound  # For the beep sound

# Function to play beep in a separate thread
def play_beep():
    winsound.Beep(1000, 500)  # Beeps at 1000 Hz for 500 ms

# Initialize Supervisor
supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

# Assuming cones are named CONE1, CONE2, etc.
cone_nodes = [supervisor.getFromDef(f"SCONE{i+1}") for i in range(14)]  # Adjust NUM_CONES as necessary
print(cone.getField("name").getSFString() for cone in cone_nodes)    
# Main loop
start_time = supervisor.getTime()

while supervisor.step(timestep) != -1:
    current_time = supervisor.getTime()
    if current_time - start_time < 5:
        continue  # Skip the first 5 seconds
    # moved_cones = sum(1 for cone in cone_nodes if cone and cone.getCustomData() == "moved")

    # if moved_cones >= 1:
        # threading.Thread(target=play_beep).start()  # Trigger beep if more than one cone has moved
        # break  # Exit or handle as needed