from vehicle import Driver
from controller import Receiver

# Initialize the Driver and Receiver
driver = Driver()
car_receiver = driver.getDevice("car_receiver")
timestep = int(driver.getBasicTimeStep())
car_receiver.enable(timestep)

# Function to check and update speed
def check_and_update_speed():
    if car_receiver.getQueueLength() > 0:
        message = car_receiver.getString()
        speed_command = float(message)
        driver.setCruisingSpeed(speed_command)
        car_receiver.nextPacket()

# Main simulation loop
time_elapsed = 0  # Keep track of the elapsed time
while driver.step() != -1:
    check_and_update_speed()
    
    time_elapsed += timestep
    if time_elapsed >= 2000:  # 2000 milliseconds = 2 seconds
        current_speed = driver.getCurrentSpeed()  # Assuming there's a method to get the current speed
        # print(f"Current Speed: {current_speed:.2f} m/s")
        time_elapsed = 0  # Reset the timer for the next 2-second interval