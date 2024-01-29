from controller import Robot
import math

# Create the Robot instance.
robot = Robot()

# Get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# Initialize devices
accelerometer = robot.getDevice("accelerometer")
gyro = robot.getDevice("gyro")
cone_emitter = robot.getDevice('cone_emitter')

# Enable devices
accelerometer.enable(timestep)
gyro.enable(timestep)

# Function to calculate the magnitude of the resultant acceleration or angular velocity
def calculate_magnitude(data):
    return math.sqrt(sum(a**2 for a in data))

# Main loop
start_time = robot.getTime()  # Get the start time of the simulation

while robot.step(timestep) != -1:
    current_time = robot.getTime()
    if current_time - start_time < 3:
        continue  # Skip the first 3 seconds

    # Get and calculate the magnitude of acceleration
    accel_data = accelerometer.getValues()
    accel_magnitude = calculate_magnitude(accel_data)

    # Get and calculate the magnitude of angular velocity
    gyro_data = gyro.getValues()
    gyro_magnitude = calculate_magnitude(gyro_data)

    # Combine the magnitudes with a delimiter and send via the emitter
    combined_message = f"{accel_magnitude};{gyro_magnitude}"
    cone_emitter.send(combined_message.encode('utf-8'))