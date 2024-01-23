from vehicle import Driver

driver = Driver()
driver.setCruisingSpeed(10)

while driver.step() != -1:
    pass