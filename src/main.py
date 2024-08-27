from bosdyn.client.robot_state import RobotStateClient
from bosdyn.client import util,create_standard_sdk
from bosdyn.client.util import authenticate,add_base_arguments

import argparse
from datetime import datetime
from google.protobuf.json_format import MessageToDict

from flask import Flask
import os



def create_app():
    app = Flask(__name__)

    @app.route("/",methods=["GET"])
    def display_state():
        sdk=create_standard_sdk('spot_observability')
        robot=sdk.create_robot(os.getenv("spot_host"))
        try: 
            authenticate(robot)
        except Exception as e: 
            return f"<p> The Robot is disconnected</p>",404

        print("authenticated")
        robot_state_client=robot.ensure_client(RobotStateClient.default_service_name)
        robot_state=robot_state_client.get_robot_state()
        robot_state=MessageToDict(robot_state) 
        r="<p>The robot is online, below is a raw summary of its state</p>"
        if robot_state: 
            for state in robot_state:
                r+=f"<p>{state} <br> {robot_state[state]}</p>" 
            return f"<div> {r} </div>"
        
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    util.add_base_arguments(parser)
    options=parser.parse_args()
    app = create_app()
    app.run(host="0.0.0.0",port=5000)
        


    
        
    
    