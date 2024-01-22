from controller import Robot, GPS, Accelerometer, Gyro
import math
import threading
import winsound

# Function to play beep in a separate thread
def play_beep():
    winsound.Beep(1000, 500)  # Beeps at 1000 Hz for 500 ms

# Create the Robot instance.
robot = Robot()

# Get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# Initialize devices
gps = robot.getDevice("gps")
accelerometer = robot.getDevice("accelerometer")
gyroscope = robot.getDevice("gyro")

# Enable devices
gps.enable(timestep)
accelerometer.enable(timestep)
gyroscope.enable(timestep)

# Function to calculate the magnitude of the resultant acceleration
def calculate_magnitude(accel_data):
    return math.sqrt(accel_data[0]**2 + accel_data[1]**2 + accel_data[2]**2)

# Main loop
threshold = 250
alert_triggered = False  # Flag to track if alert has been triggered
start_time = robot.getTime()  # Get the start time of the simulation

while robot.step(timestep) != -1:
    current_time = robot.getTime()
    if current_time - start_time < 5:
        continue  # Skip the first 5 seconds

    accel_data = accelerometer.getValues()
    magnitude = calculate_magnitude(accel_data)

    # Trigger the alert if acceleration exceeds the threshold
    if magnitude > threshold and not alert_triggered:
        threading.Thread(target=play_beep).start()  # Play beep in a non-blocking manner
        alert_triggered = True  # Set the flag as alert has been triggered
