from vehicle import Driver

driver = Driver()
driver.setCruisingSpeed(0)

while driver.step() != -1:
    pass