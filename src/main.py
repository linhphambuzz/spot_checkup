from bosdyn.client.robot_state import RobotStateClient
from bosdyn.client import util,create_standard_sdk
from bosdyn.client.util import authenticate,add_base_arguments

import argparse
from datetime import datetime
from google.protobuf.json_format import MessageToDict

from flask import Flask
import os
import sys
import time
from datetime import datetime
import logging 



def create_app():
    app = Flask(__name__)
    os.environ['TZ'] = 'America/Chicago'
    time.tzset()
    _logger=logging.getLogger("spot-api")
    _logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    _logger.addHandler(handler)


    @app.route("/",methods=["GET"])
    def display_state():
        sdk=create_standard_sdk('spot_observability')
        robot=sdk.create_robot(os.getenv("spot_host"))
        try: 
            authenticate(robot)
            _logger.info(f"Authenticated at {datetime.now()}")

        except Exception as e: 
            _logger.warning(f"SPOT call failed at {datetime.now()}")
            return f"<p style='font-size:23px;'> SPOT STATE: DISCONECTED </p>",404

        robot_state_client=robot.ensure_client(RobotStateClient.default_service_name)
        robot_state=robot_state_client.get_robot_state()
        robot_state=MessageToDict(robot_state) 

        content="<p style='font-size:23px'> SPOT STATE: ONLINE</p>"
        content+= f"<p> LAST PING CALL : {datetime.now()} <p>"
        if not robot_state: return 
        for idx,state in enumerate(robot_state):
            if state=="powerState": 
                content+=power_state(state,robot_state[state])

            if state=="batteryStates":
                content+=battery_state(state,robot_state[state])
            
            if state=="commsStates":
                # content+=f"<p> {state} <br> {robot_state[state]} </p> "
                content+=comms_state(state,robot_state[state])
                
            if state=="systemFaultState":
                content+=system_fault("systemFaultState",MessageToDict(robot_state_client.get_robot_state().system_fault_state))
                
            
            if state=="estopStates":
                content+=estop_state("estopStates",robot_state[state])
                

            if state=="kinematicState":
                
                # content+=f"<p> {state} <br> {robot_state[state]} </p> "
                content+=kinamatic_state("kinematicState",robot_state[state])
                break

    
            
        return f"<div style='padding:5px;'> {content} </div>"
        
    return app

def kinamatic_state(state:str,data:dict):
    jointStates,velocityOfBodyInVision,velocityOfBodyInOdom,acquisitionTimestamp,transformsSnapshot=data.keys()
    header="<p style='font-size:20px; font-weight:bold'> Kinematic State </p>"

    # joint statte 
    list="<p> Joint States<p>"
    list+="<table style='width:100%;border:1px solid black;'><tr>"
    for js in data[jointStates]:
        if "</th>" not in list:
            for key in js.keys():
                list+=f"<th style='border:1px solid black;'>{key}</th>"
            list+="</tr>"
        list+="<tr>"
        for k,v in js.items():
            list+=f"<td style= 'border:1px solid black';>{v}</td>"
        list+="</tr>"
    list+="</table>"

    list+="<p> Velocity Of Body In Vision<p>"
    list+="<table style='border:1px solid black;'><tr>"
    for h in ["name","x","y","z"]:
        list+=f"<th style='border:1px solid black;'>{h}</th>"
    list+="</tr>"
    list+="<tr>"
    for idx,v in enumerate(data[velocityOfBodyInVision].values()):
        if idx==0:
            list+=f"<td style='border:1px solid black;'> linear</td>"
        else: 
            list+=f"<td style='border:1px solid black;'> angular</td>"

        for vv in v.values():
            list+= f"<td style='border:1px solid black;'>{vv}</td>"
        
        list+="</tr>"
    list+="</table>"

    list+="<p> Velocity Of Body In Odom<p>"
    list+="<table style='border:1px solid black;'><tr>"
    for h in ["name","x","y","z"]:
        list+=f"<th style='border:1px solid black;'>{h}</th>"
    list+="</tr>"
    list+="<tr>"
    for idx,v in enumerate(data[velocityOfBodyInOdom].values()):
        if idx==0:
            list+=f"<td style='border:1px solid black;'> linear</td>"
        else: 
            list+=f"<td style='border:1px solid black;'> angular</td>"

        for vv in v.values():
            list+= f"<td style='border:1px solid black;'>{vv}</td>"
        
        list+="</tr>"
    list+="</table>"

    list+="<p> Transform Snapshot<p>"
    list+="<p>"
    for k in data[transformsSnapshot].values():
        list+=f"<span> {k} </span>"
    list+="</p>"


    return f"<div>{header}{list}</div>"





def power_state(state:str,data:dict)->str:
    assert state== "powerState"
    header="<p style='font-size:20px; font-weight:bold'> Power State </p>"
    list="<ul>"
    for k,v in data.items():
        list+=f"<li>{k} : {v}</li>"
    list+="</ul>"
    return f"<div>{header}{list}</div>"

def battery_state(state:str,data:list): 
    assert state=="batteryStates"
    header="<p style='font-size:20px; font-weight:bold'> Battery State </p>"
    list="<ul>"
    for battery in data:
        for k,v in battery.items():
            list+=f"<li>{k} : {v}</li>"
    list+="</ul>"
    return f"<div>{header}{list}</div>"

def comms_state(state:str,data:list):
    assert state=="commsStates"
    header="<p style='font-size:20px; font-weight:bold'> Comunication State </p>"
    list="<ul>"
    for d in data:
        for k,v in d.items():
            list+=f"<li>{k} : {v}</li>"
    list+="</ul>"
    return f"<div>{header}{list}</div>"

def system_fault(state:str,data):
    assert state=="systemFaultState"
    header="<p style='font-size:20px; font-weight:bold'> Sytem Fault </p>"
    list=""
    for d in data:
        list+=f"<p> {d} <br> {data[d]} </p>"
    return f"<div>{header}{list}</div>"

def estop_state(state,data):
    assert state=="estopStates"
    header="<p style='font-size:20px; font-weight:bold'> EStop State </p>"
    list="<ul>"
    for estop in data:
        list+="<li>"
        for k,v in estop.items():
            list+=f"<span style='padding:5px;'> <b>{k}</b> : {v} </span>"
        list+="</li>"
    list+="</ul>"
    return f"<div>{header}{list}</div>"



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    util.add_base_arguments(parser)
    options=parser.parse_args()
    app = create_app()
    app.run(debug=True,host="0.0.0.0",port=5000)
        


    
        
    
    
