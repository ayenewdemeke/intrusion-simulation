from vehicle import Driver

driver = Driver()
driver.setCruisingSpeed(50)

while driver.step() != -1:
    pass