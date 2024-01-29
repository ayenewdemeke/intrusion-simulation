import pandas as pd
from controller import Supervisor
import numpy as np
import math

def calculate_magnitude(vector):
    return math.sqrt(sum(x**2 for x in vector))

def calculate_velocity(current_pos, previous_pos, timestep):
    return [(c - p) / timestep for c, p in zip(current_pos, previous_pos)]

def calculate_acceleration(current_vel, previous_vel, timestep):
    return [(c - p) / timestep for c, p in zip(current_vel, previous_vel)]

def run_simulation(supervisor, speed):
    cone = supervisor.getFromDef("SCONE")
    vehicle = supervisor.getFromDef("TOYOTA")

    if cone:
        cone.getField("translation").setSFVec3f([500, -5.6, 0.35])
        cone.getField("rotation").setSFRotation([0, 0, 1, 0])
        cone.resetPhysics()

    if vehicle:
        vehicle.getField("translation").setSFVec3f([500 - speed**2 / 36 - 50, -5.6, 0.35])
        vehicle.getField("rotation").setSFRotation([0, 1, 0, 0])
        vehicle.resetPhysics()

    supervisor_receiver = supervisor.getDevice("supervisor_receiver")
    supervisor_receiver.enable(int(supervisor.getBasicTimeStep()))
    supervisor_emitter = supervisor.getDevice("supervisor_emitter")

    speed_command = str(speed)
    supervisor_emitter.send(speed_command.encode('utf-8'))

    max_acceleration = 0
    max_angular_velocity = 0
    max_velocity_magnitude = 0
    max_acceleration_from_velocity = 0
    previous_position = cone.getField("translation").getSFVec3f()
    previous_velocity = [0, 0, 0]
    simulation_start_time = supervisor.getTime()
    log_counter = 0

    while supervisor.step(int(supervisor.getBasicTimeStep())) != -1:
        if supervisor.getTime() - simulation_start_time > SIMULATION_RUN_TIME:
            break

        current_position = cone.getField("translation").getSFVec3f()
        timestep_duration = supervisor.getBasicTimeStep() / 1000.0  # Convert ms to seconds

        current_velocity = calculate_velocity(current_position, previous_position, timestep_duration)
        current_acceleration = calculate_acceleration(current_velocity, previous_velocity, timestep_duration)
        velocity_magnitude = calculate_magnitude(current_velocity)
        acceleration_magnitude = calculate_magnitude(current_acceleration)

        if velocity_magnitude > max_velocity_magnitude:
            max_velocity_magnitude = velocity_magnitude

        if acceleration_magnitude > max_acceleration_from_velocity:
            max_acceleration_from_velocity = acceleration_magnitude

        previous_position = current_position
        previous_velocity = current_velocity

        # Log current velocity every 2 seconds
        log_counter += supervisor.getBasicTimeStep()
        if log_counter >= 2000:  # 2000 milliseconds = 2 seconds
            # print(f"Current Velocity Magnitude: {velocity_magnitude:.2f} m/s")
            log_counter = 0

        while supervisor_receiver.getQueueLength() > 0:
            message = supervisor_receiver.getString()
            accel_part, gyro_part = message.split(';')
            accel_magnitude = float(accel_part)
            gyro_magnitude = float(gyro_part)

            if accel_magnitude > max_acceleration:
                max_acceleration = accel_magnitude
                max_accel_translation = current_position
                max_accel_rotation = cone.getField("rotation").getSFRotation()

            if gyro_magnitude > max_angular_velocity:
                max_angular_velocity = gyro_magnitude

            supervisor_receiver.nextPacket()

    trans_x, trans_y, trans_z = max_accel_translation
    rot_x, rot_y, rot_z, rot_w = max_accel_rotation

    return speed, max_acceleration, max_angular_velocity, trans_x, trans_y, trans_z, rot_x, rot_y, rot_z, rot_w, max_velocity_magnitude, max_acceleration_from_velocity

# Main script
supervisor = Supervisor()
SIMULATION_RUN_TIME = 30

# Generate speeds
mean_speed = 60
std_dev = 20
speeds = np.random.normal(mean_speed, std_dev, 100)
speeds = np.maximum(speeds, 0)

# Data collection setup
data = []

# Record maximum accelerations, angular velocities, translations, rotations, velocities, and calculated accelerations for each speed
for speed in speeds:
    speed, max_acc, max_gyro, trans_x, trans_y, trans_z, rot_x, rot_y, rot_z, rot_w, max_vel, max_acc_from_vel = run_simulation(supervisor, speed)
    data.append({
        "Speed (km/hr)": speed,
        "Max Acceleration (m/s^2)": max_acc,
        "Max Angular Velocity (rad/s)": max_gyro,
        "Translation X": trans_x,
        "Translation Y": trans_y,
        "Translation Z": trans_z,
        "Rotation X": rot_x,
        "Rotation Y": rot_y,
        "Rotation Z": rot_z,
        "Rotation W": rot_w,
        "Max Velocity (m/s)": max_vel,
        "Max Accel from Vel (m/s^2)": max_acc_from_vel
    })
    print(f"Speed: {speed:.2f} km/hr, Max Accel: {max_acc:.2f} m/s^2, Max Gyro: {max_gyro:.2f} rad/s, Max Vel: {max_vel:.2f} m/s, Max Accel from V: {max_acc_from_vel:.2f} m/s^2")

# Convert the collected data to a DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv("simulation_data.csv", index=False)
print("Data saved to simulation_data.csv")
