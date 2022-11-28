import email
import sys

from flask import Flask, request, render_template
from flask_socketio import SocketIO
from flask_executor import Executor

import pandas as pd
sys.path.append('/fmu_simulation')
from werkzeug.utils import secure_filename
from simulation import Simulation
import os
import json
import logging
import logging.config
import socket
import time

docker_id = socket.gethostname()

logger = logging.getLogger(__name__)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='main_server.log', filemode='w', level=logging.DEBUG,  format=log_format)

app = Flask(__name__, template_folder='./')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
executor = Executor(app)
thread = None

is_charts_active = True
chart_time_window = 500

# create the folders when setting up your app
os.makedirs(os.path.join(app.instance_path, 'upload'), exist_ok=True)

sim = Simulation()
is_config_load = False
fmu_name = ""

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    global sim, fmu_name
    logger.info(docker_id+": try to upload FMU file to server.")
    try:
        sim = Simulation()
        if request.method == 'POST':            
            f = request.files['file']
            try: 
                fmu_name = f.filename
                logger.info(docker_id+": file with name ", + fmu_name +  " uploaded.")
            except:
                logger.warning(docker_id+": no fmu file name found.")
                
            f.save(os.path.join(app.instance_path, 'upload', secure_filename("model.fmu")))
            size = os.stat(os.path.join(app.instance_path, 'upload',"model.fmu")).st_size
            if size > 0.0:
                try:
                    file = os.path.join(app.instance_path, 'upload',"model.fmu")
                    log = sim.init_fmu(file)
                    logger.info(docker_id+": init FMU simulation."+log)
                except:
                    logger.error(docker_id+": error when trying to upload FMU file to server.")
            else:
                logger.error(docker_id+": received FMU file size < 0.0.")
        return "upload file success"
    except:
        logger.error(docker_id+": error in receiving FMU file on server.")
        return "upload file unsuccess"

@app.route('/download', methods = ['GET'])
def download_file():
    logger.info(docker_id+": try to download FMU file from server.")
    try:
        if request.method == 'GET':
            file = os.path.join(app.instance_path, 'upload', secure_filename("model.fmu"))
            return file
        else:
            logger.warning(docker_id+": wrong request method used. Use 'GET' to receive FMU file.")
            return "download file error"
    except:
        logger.error(docker_id+": error when trying to get FMU file from server.")
        return "download file error"
    
@app.route('/get_var_names', methods=['GET'])
def get_var_names():
    logger.info(docker_id+": try to get all available signal variable names from FMU on server.")
    try:
        if request.method == 'GET':
            var_names_json = json.dumps({"FMU_variables":sim.get_variable_names()},indent=4)
            return var_names_json
        else:
            logger.warning(docker_id+": wrong request method used. Use 'GET' to receive FMU file.")
            return "get_var_names warning"
    except:
        logger.error(docker_id+": error when trying to get signal variable name information from FMU file on server.")
        return "get_var_names error"
    
@app.route('/config',methods=['POST', 'GET'])
def configuration():
    global config, is_config_load, is_charts_active
    try:
        if request.method == 'POST':
            logger.info(docker_id+": try to post configuration to server.")
            config = request.get_json(silent=True)
            input = dict()
            try:
                logger.info(docker_id+": try to extract configuration information and initate simulation.")
                
                logger.info(docker_id+": extract configuration output.")
                output = config['config']['output']
                
                logger.info(docker_id+": extract configuration timestep.")
                timestep = config['config']['timestep']
                
                logger.info(docker_id+": extract configuration init_input.")
                input = config['config']['init_input']
                
                logger.info(docker_id+": set output in simulation environment.")
                sim.set_dataset_output(output)
                logger.info(docker_id+": set timestep in simulation environment.")
                sim.set_timestep(timestep)
                
                if len(input) > 0:
                    logger.info(docker_id+": set init_input in simulation environment.")
                    sim.init_input(input)
                
                is_config_load = True
                
                try:
                    logger.info(docker_id+": extract configuration charts_active.")
                    is_charts_active = config['config']['charts_active']
                except:
                    is_charts_active = False
                
                # init webpage data
                if is_charts_active:
                    try:
                        logger.info(docker_id+": try to extract chart settings from configuration file")
                        try:
                            logger.info(docker_id+": try to extract the chart time window (number of timesteps) from configuration file")
                            chart_time_window = config["config"]["chart_time_window"]
                            logger.info(docker_id+": found chart time window (number of timesteps) from configuration file")
                        except:
                            chart_time_window = 500
                            logger.info(docker_id+": chart time window not found in configuration file - 500 timesteps set.")
                            
                        executor.submit(init_page(output,chart_time_window))
                        logger.info(docker_id+": initialize chart page.")
                        
                        try:
                            res = sim.get_output()
                            res.update({"time" : {"value":0.0, "unit":"sec"}})
                            executor.submit(send_to_page(res))
                            logger.info(docker_id+": update chart page data.")
                        except:
                            logger.error(docker_id+": error when running data update function for chart page.")
                            
                    except:
                        logger.error(docker_id+": error when running initialize function for chart page.")
                logger.info(docker_id+": configuration extracted and simulation initiated.")
                return "config init successful"
            except:
                is_config_load = False
                logger.error(docker_id+": error when trying to extract configuration information and initate simulation.")
                return "config init unsuccessful"
        
        if request.method == 'GET':
            logger.info(docker_id+": try to get configuration from server.")
            try:
                if is_config_load:
                    logger.info(docker_id+": configuration from server returned to requester.")
                    return json.dumps(config, indent=4)
                else:
                    logger.error(docker_id+": no configuration found on server.")
                    return "CONFIGERR"
            except:
                logger.error(docker_id+": error when trying to return configuration from server.")
                return "CONFIGERR"
    except:
        logger.error(docker_id+": error when trying to post/get configuration file.")
        return "config init unsuccessful"
        

@app.route('/input', methods=['POST', 'GET'])
def input():
    try:
        if request.method == 'POST':
            new_input = request.get_json(silent=True)
            input = sim.get_input()
            input.update(new_input)
            sim.set_input(input)
            logger.info(docker_id+": set updated simulation inputs.")
            return json.dumps(input,indent=4)
            
        if request.method == 'GET':
            input = sim.get_input()
            logger.info(docker_id+": get actual simulation inputs.")
            return json.dumps(input,indent=4)
    except:
        logger.error(docker_id+": error when trying to updated simulation inputs")
        return "input error"

@app.route('/update', methods=['GET', 'POST'])
def update():
    try:
        logger.info(docker_id+": update simulation.")
        if request.method == 'GET':
            logger.info(docker_id+": set simulation input.")
            sim.set_input(get_input_commands(sim.get_time()))
            logger.info(docker_id+": send update request to simulation.")
            res = sim.update()
            logger.info(docker_id+": update request to simulation successful.")
            res_json = json.dumps(res, indent=4)
            
            # update webpage data
            if is_charts_active:
                try:
                    logger.info(docker_id+": update chart page data.")
                    out = sim.get_output()
                    executor.submit(send_to_page(out))
                except:
                    logger.error(docker_id+": error when running data update function for chart page.")
            
            return res_json
    except:
        logger.error(docker_id+": error when trying to update simulation.")
        return "update error"

@app.route('/get_output', methods=['GET'])
def get_output():
    try:
        if request.method == 'GET':
            res = sim.get_output()
            res_json = json.dumps(res, indent=4)
            logger.info(docker_id+": observed output signals returned to requester.")
            return res_json
        else:
            logger.warning(docker_id+": wrong request method used. Use 'GET' to receive output.")
            return "get_output warning"
    except:
        logger.error(docker_id+": error when trying to get output from simulation.")
        return "get_output error"
        

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    try: 
        if request.method == 'GET':
            sim.reset()
            input = config['config']['init_input']
            if len(input) > 0:
                sim.init_input(input)
            
            logger.info(docker_id+": reset simulation parameter.")
            #return json.dumps(sim.get_input(),indent=4)
            res = sim.get_output()
            res.update({"time" : {"value":-1.0, "unit":"sec"}})
            executor.submit(send_to_page(res))
            
            res.update({"time" : {"value":0.0, "unit":"sec"}})
            executor.submit(send_to_page(res))
            return "reset successful"
    except:
        logger.error(docker_id+": error when trying to reset simulation.")
        return "reset error"

def get_input_commands(time):
    try:
        tol = 0.01
        commands = list()
        input = sim.get_input()
        for msg in config['input']: 
            commands.append(msg)

        for cmd in commands:
            if abs(time - cmd['time']) < tol:
                input = cmd
        
        logger.info(docker_id+": check for config predefined simulation input commands to update.")
        return input
    except:
        logger.error(docker_id+": error when trying to check for config predefined simulation input commands.")
        return "get_input_commands error"

@socketio.on("send_to_page")
def send_to_page(datamap):
    data = datamap
    data_2= pd.DataFrame(data)
    df_json=data_2.to_json(orient='records')
    result = {"objects": json.loads(df_json)}
    socketio.emit('getter',result, broadcast=True)

@socketio.on("init_page")
def init_page(init, time_window):
    result = {"out": [init, fmu_name, int(time_window)]}
    socketio.emit('init',result, broadcast=True)
        
@app.route('/')
def index():
    try:
        return render_template('html_charts/charts.html')
    except:
        logger.error(docker_id+": error when trying to render html template - check if config is already loaded.")
        return "webpage chart error"

if __name__ == '__main__':
    if is_charts_active:
        socketio.run(app)
    #executor.submit(send_to_page)
    app.run(debug=True)
    