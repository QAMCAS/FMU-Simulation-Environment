import json

# Import the FMU docker interface package for python
import api_fmu_docker.api_lib as api
import heater_diagnose as diag

def main():
    # Configuration file path
    config_model = 'application/config/config_heater_model_diagnose.json'
    
    # Load configuration file
    api_model.init_interface_config_client(config_model)
    
    # Upload FMU file
    api_model.upload_fmu()
    
    # Upload FMU file
    api_model.upload_config()

    # Reset FMU model
    api_model.send_reset()
    diag_model.reset()

    # print all available FMU model variables
    print("# FMU Model available variables: ", json.dumps(api_model.get_all_variable_names(), indent=4))

    # Run simulation for 40 seconds (400 time-steps for 10Hz) (time step defined in config file)
    timestep = api_model.get_timestep()
    sim_time = 5 # seconds

    for i in range(int(round(sim_time / timestep))):
        # send update (do next time step) to FMU simulation
        api_model.send_update()
        # getter to store the measured output signals
        out = api_model.get_output()
        # send signal data to the 2-point controller
        heat_controller(i, out)
        heat_diagnose(i, out)
    
# This is a 2-point controller to keep the temperature within two boundaries
def heat_controller(time, signal):

    # upper temperature boundary 300 Kelvin
    if signal["T"]["value"] > 20:
        # send state update to shut off the heater
        api_model.set_input(api_model.generate_input_message("heater_sw",False))
        
    # lower temperature boundary 280 Kelvin
    if signal["T"]["value"] < 10:
        # send state update to power on the heater
        api_model.set_input(api_model.generate_input_message("heater_sw",True))

def heat_diagnose(time, signal):
    temperature = signal["T"]["value"]
    battery = "max"
    switch = signal["heater_sw"]["value"]
    heater = signal["Q"]["value"]

    #if time >= 10:
    #    switch = False

    diag_model.diagnose_all(time, temperature, switch, battery, heater)
    
if __name__ == '__main__':
    # Create new interface object to communicate with the docker simulation
    # Parameter: name is used for indicate the correlated logging messages (default="")
    api_model = api.API_FMU_Docker("model")
    diag_model = diag.Diagnose()
    main()