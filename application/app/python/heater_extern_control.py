import json
import numpy as np
# Import the FMU docker interface package for python
import api_fmu_docker.api_lib as api
import time

def main():
    # Configuration file path
    config_model = 'application/config/config_heater_model.json'
    config_control = 'application/config/config_heater_control_unit.json'

    # Load configuration file to interface
    api_model.init_interface_config_client(config_model)
    api_controller.init_interface_config_client(config_control)
    
    # Upload FMU file
    api_model.upload_fmu()
    api_controller.upload_fmu()
    
    # Upload configuration file
    api_model.upload_config()
    api_controller.upload_config()
    
    # Reset FMU model
    api_model.send_reset()
    api_controller.send_reset()
    
    # print all available FMU model variables
    print("# FMU Model available variables: ", json.dumps(api_model.get_all_variable_names(), indent=4))
    print("# FMU Controller available variables: ", json.dumps(api_controller.get_all_variable_names(), indent=4))
    
    # Run simulation for 40 seconds (400 time-steps for 10Hz) (time step defined in config file)
    timestep = api_model.get_timestep()
    sim_time = 18 # seconds
    

    for stime in np.arange(0, sim_time, timestep):
        # send update (do next time step) to FMU simulation
        api_model.send_update()
        # getter to store the measured output signals
        out_model = api_model.get_output()
        # send the control states with measured values from heater model
        api_controller.set_input(api_model.generate_input_message("T_measured", out_model['T']['value']))
        # update the controller by same time step as used for the model
        api_controller.send_update()
        # get the control outputs based on the given model's measurements
        out_control = api_controller.get_output()
        # send the actual control output to the model for the next update sequence
        api_model.set_input(api_model.generate_input_message("heater_sw", out_control['heater_sw']['value']))
    
if __name__ == '__main__':
    # Create new interface object to communicate with the docker simulation
    # Parameter: name is used for indicate the correlated logging messages (default="")
    api_model = api.API_FMU_Docker("model")
    api_controller = api.API_FMU_Docker("control")
    main()