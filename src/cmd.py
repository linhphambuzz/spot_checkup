from bosdyn.client import command_line
import os 


spot_host=os.environ['spot_host']
command_line.main([spot_host,"id"])

