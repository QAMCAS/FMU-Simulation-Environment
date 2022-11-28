from ctypes import sizeof
from multiprocessing.sharedctypes import Value
import requests
import json
import sys
import logging
import logging.config
import os

logger = logging.getLogger(__name__)
class API_FMU_Docker:
    def __init__(self, name = ""):
        self.name = name
        self.cnt = 0
        self.varnames = ""
        self.inputs = ""
        self.input_config = ""
        
        #super().__init__()
        self.__set_logger__()

    def __set_logger__(self):
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        dir_name = os.path.dirname(sys.argv[0])
        dir_name = os.path.dirname(os.path.abspath(__file__))
        logging.basicConfig(filename=dir_name+'/api_lib.log', filemode='w', level=logging.INFO, format=log_format)
        
    # Send a update request to Docker FMU model server
    def send_update(self):
        try:
            logger.info(self.name+": send update request to server ("+str(self.server)+")")
            r = requests.get(self.server+'update')
            self.signal = r.text
        except:
            logger.error(self.name+": error when trying to send update request to server ("+str(self.server)+")")

    # Send a reset request to Docker FMU model server
    def send_reset(self):
        try:
            logger.info(self.name+": send reset request to server ("+str(self.server)+")")
            requests.get(self.server+'reset')
        except:
            logger.error(self.name+": error when trying to send reset request to server ("+str(self.server)+")")

    # Send updated FMU model inputs to Docker FMU model server
    def set_input(self, input):
        # send a JSON/dict input change
        try:
            logger.info(self.name+": set new input values on server ("+str(self.server)+"): "+str(input))
            d = requests.post(self.server+'input', json = input)
            return d.text
        except:
            logger.error(self.name+": error when trying to set new inputs on server.")

    def generate_input_message(self, name, value):
        input_dict = {name:value}
        return input_dict
    
    def set_interface_server(self, server):
        logger.info(self.name+": manually net new server address: "+str(server))
        self.server = server

    def get_output(self):
        try:
            r = requests.get(self.server+'get_output')
            output = json.loads(r.text)
            logger.info(self.name+": get actual output values from server ("+str(self.server)+"): "+str(output))
            return output
        except:
            logger.error(self.name+": unable to get output values from server ("+str(self.server)+")")
            return
    
    def get_output_names(self):
        try:
            logger.info(self.name+": get configured output variable names from server ("+str(self.server)+"):"+str(config["output"]))
            config = json.loads(self.get_server_config(self.server))
            return config['output']
        except:
            logger.error(self.name+": error when trying to get configured output variable names from server ("+str(self.server)+")")
    
    def get_server_config(self, server):
        try:
            r = requests.get(server+'config')
            config = r.text
            if config != "CONFIGERR":
                return config
            else:
                logger.error(self.name+": no configuration found on server.")
        except:
            logger.error(self.name+": unable to get configuration data.")
            return
    
    def get_all_variable_names(self):
        try:
            # load config file
            r = requests.get(self.server+'get_var_names')
            varnames = json.loads(r.text)
            
            logger.info(self.name+": get all available variable names from FMU model.")
            return varnames
        except:
            logger.error(self.name+": unable to get model variable names! Load configuration file.")
            sys.exit(1)
    
    def get_actual_inputs(self):
        try:
            r = requests.get(self.server+'input')
            input = json.loads(r.text)
            
            logger.info(self.name+": get actual set inputs used in FMU model.")
            return input
        except:
            logger.error(self.name+": unable to get actual set inputs of FMU model.")
    
    def get_config_inputs(self):
        try:
            config = self.__get_config()
            logger.info(self.name+": get set inputs as configured in configuration file from server.")
            return config['input']
        except:
            logger.error(self.name+": unable to get configured inputs from server.")
            sys.exit(1)

    def get_timestep(self):
        try: 
            config = json.loads(self.get_server_config(self.server))
            logger.info(self.name+": get set timestep information from server.")
            return config['config']['timestep']
        except:
            logger.error(self.name+": unable to get set timestep information from server (simulation time steps).")
            sys.exit(1)

    def init_interface_config_client(self, config_path):
        logger.info(self.name+": try to load configuration file from client. config path: "+str(config_path))
        try:
            with open(config_path) as config_json:
                config = json.load(config_json)
            config_json.close()
            self.__init_api_config(config)
            self.__set_config(config)
            logger.info(self.name+": configuration file loaded and API interface is initiated.")
        except:
            logger.error(self.name+": error in loading configuration file.")
            sys.exit(1)
    
    def init_interface_config_server(self, server):
        logger.info(self.name+": try to load configuration file from server ("+str(server)+")")
        try:
            config = json.loads(self.get_server_config(server))
            self.__init_api_config(config)
            self.__set_config(config)  
            logger.info(self.name+": configuration file loaded from server and API interface is initiated.") 
        except:
            logger.error(self.name+": error in loading configuration file from server ("+str(server)+")")
            sys.exit(1)
        
    def __set_config(self, config):
        self.config = config
    
    def __get_config(self):
        return self.config
    
    def __init_api_config(self, config):
        logger.info(self.name+": validity check of loaded configuration file.")
        try:
            # extract FMU path information
            self.fmu = config['fmu']
            logger.info(self.name+": configured FMU file: "+str(self.fmu))
        except:
            logger.error(self.name+": specification error for FMU information.")
            logger.info(self.name+": example: "+json.dumps({"fmu":"path to FMU model"},indent=4))
            sys.exit(1)
            
        try:
            # extract server information
            self.server = config['server']
            logger.info(self.name+": configured server: "+self.server)
        except:
            logger.error(self.name+": specification error for server information.")
            logger.info(self.name+": example: "+json.dumps({"server":"http://localhost:80/"},indent=4))
            sys.exit(1)
                                   
        try:
            # extract output information for drawing and data storage
            output = config['config']['output']
            self.output = output.copy()

            logger.info(self.name+": configured output: "+json.dumps(self.output,indent=4))
        except:
            logger.error(self.name+": specification error for output information.")
            logger.info(self.name+": example: "+json.dumps({"output":["x", "y", "z"]},indent=4))
            sys.exit(1)
            
        try:
            # extract predefined input information
            input_config = config['input']
            self.input_config = input_config.copy()
            logger.info(self.name+": configured predefined input information: "+json.dumps(self.input_config,indent=4))
        except:
            logger.error(self.name+": specification error for predefined input information.")
            logger.info(self.name+": example: "+json.dumps({"input":[{"time":10, "x_input":"ok", "y_input":"ok"}]},indent=4))
            sys.exit(1)
        
        try:
            if len(self.input_config) > 0:
                for config_check in config['input']:
                    if type(config_check['time']) != float:
                        raise ValueError()
        except ValueError:
            logger.error(self.name+": specification error for predefined input information.")
            logger.info(self.name+": example: "+json.dumps({"input":[{"time":10, "x_input":"ok", "y_input":"ok"}]},indent=4))
            sys.exit(1)
                        
        try:
            # extract simulation timestep
            timestep = config['config']['timestep']
            if timestep > 0.0:
                pass
            logger.info(self.name+": configured timestep information: "+str(timestep))
        except:
            logger.error(self.name+": specification error for timestep information.")
            logger.info(self.name+": example: "+json.dumps({"timestep":0.1},indent=4))
            sys.exit(1)
            
    def upload_config(self):
        logger.info(self.name+": try to upload configuration file to server.")
        try:
            # load config file
            url = self.server + 'config'
            r = requests.post(url, json = self.__get_config())
            logger.info(self.name+": configuration file uploaded to server.")
        except:
            logger.error(self.name+": error when trying to upload config to server.")
                
    def upload_fmu(self, fmu_path=""):
        logger.info(self.name+": try to upload FMU file to server.")
        if fmu_path == "":
            fmu = self.fmu
        else:
            fmu = fmu_path
                
        try:
            # extract FMU file path to upload
            logger.info(self.name+": selected FMU file to upload: "+str(fmu))
            # open FMU file to upload
            with open(fmu, 'rb') as f:
                file = f.read()
            f.close()
            try:
                # upload FMU file
                name = os.path.basename(fmu)
                url = self.server + 'upload'
                print(json.dumps({'name':str(name)}))
                #r = requests.post(url, files={'file':file}, json=json.dumps({'name':str(name)}))
                #requests.post(url, files={'file':file, 'name':str(name)})
                requests.post(url, files={'file': (name, file)})
                logger.info(self.name+": FMU file uploaded: "+str(fmu))
            except:
                logger.error(self.name+": error when uploading FMU file to server.")
        except:
            logger.error(self.name+": error when uploading FMU file to server.")
            
    def download_fmu(self):
        try:
            file = requests.get(self.server+'config')
            return file
        except:
            logger.error(self.name+": unable to get FMU file from server.")
            return