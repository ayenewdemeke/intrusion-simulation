from controller import Robot, GPS, Accelerometer, Gyro
import math
import threading

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

robot.setCustomData("")

# Main loop
threshold = 100
start_time = robot.getTime()  # Get the start time of the simulation

while robot.step(timestep) != -1:
    current_time = robot.getTime()
    if current_time - start_time < 3:
        continue  # Skip the first 3 seconds

    accel_data = accelerometer.getValues()
    magnitude = calculate_magnitude(accel_data)

    if magnitude > threshold:
        robot.setCustomData("moved")