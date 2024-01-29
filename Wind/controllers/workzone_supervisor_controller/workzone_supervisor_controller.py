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

def run_simulation(supervisor, wind_force):
    cone = supervisor.getFromDef("SCONE")

    if cone:
        cone.getField("translation").setSFVec3f([400, -5.6, 0.35])
        cone.getField("rotation").setSFRotation([0, 0, 1, 0])
        cone.resetPhysics()

    supervisor_receiver = supervisor.getDevice("supervisor_receiver")
    supervisor_receiver.enable(int(supervisor.getBasicTimeStep()))

    max_acceleration = 0
    max_angular_velocity = 0
    max_velocity_magnitude = 0
    max_acceleration_from_velocity = 0
    max_accel_translation = [0, 0, 0]
    max_accel_rotation = [0, 0, 0, 0]
    previous_position = cone.getField("translation").getSFVec3f()
    previous_velocity = [0, 0, 0]
    simulation_start_time = supervisor.getTime()
    
    timestep = int(supervisor.getBasicTimeStep())

    while supervisor.step(timestep) != -1:
        if supervisor.getTime() - simulation_start_time > SIMULATION_RUN_TIME:
            break

        # Continuously apply the wind force to the cone
        cone.addForce([wind_force, 0, 0], False)  # Apply force in the global coordinate system

        current_position = cone.getField("translation").getSFVec3f()
        timestep_duration = supervisor.getBasicTimeStep() / 1000.0

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

    return wind_force, max_acceleration, max_angular_velocity, trans_x, trans_y, trans_z, rot_x, rot_y, rot_z, rot_w, max_velocity_magnitude, max_acceleration_from_velocity

# Main script
supervisor = Supervisor()
SIMULATION_RUN_TIME = 5

# Generate wind forces
mean_wind_force = 15  # Example mean wind force
std_dev_wind_force = 5  # Example standard deviation
wind_forces = np.random.normal(mean_wind_force, std_dev_wind_force, 20)
wind_forces = np.maximum(wind_forces, 0)  # Ensure that wind forces are not negative

# Data collection setup
data = []

# Run simulation for each wind force
for wind_force in wind_forces:
    wind_force, max_acc, max_gyro, trans_x, trans_y, trans_z, rot_x, rot_y, rot_z, rot_w, max_vel, max_acc_from_vel = run_simulation(supervisor, wind_force)
    data.append({
        "Wind Force": wind_force,
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
    print(f"Wind Force: {wind_force:.2f}, Max Accel: {max_acc:.2f} m/s^2, Max Gyro: {max_gyro:.2f} rad/s, Trans: ({trans_x}, {trans_y}, {trans_z}), Rot: ({rot_x}, {rot_y}, {rot_z}, {rot_w}), Max Vel: {max_vel:.2f} m/s, Max Accel from Vel: {max_acc_from_vel:.2f} m/s^2")

# Convert the collected data to a DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv("wind_simulation_data.csv", index=False)
print("Data saved to wind_simulation_data.csv")
