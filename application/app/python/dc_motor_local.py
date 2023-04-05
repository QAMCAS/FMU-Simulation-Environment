import json
import numpy as np
import matplotlib.pyplot as plt
# Import the FMU docker interface package for python
import api_fmu_docker.api_lib as api

def main():
    # Configuration file path
    config_model = 'application/config/config_dc_motor_model_local.json'
    
    # Load configuration file
    api_model.init_interface_config_client(config_model)
    
    # Upload FMU file
    api_model.upload_fmu()
    
    # Upload FMU file
    api_model.upload_config()

    # Reset FMU model
    api_model.send_reset()

    # print all available FMU model variables
    print("# FMU Model available variables: ", json.dumps(api_model.get_all_variable_names(), indent=4))

    # Run simulation for 40 seconds (400 time-steps for 10Hz) (time step defined in config file)
    timestep = api_model.get_timestep()
    sim_time = 0.13 # seconds
    output_storage = init_storage(api_model.get_output_names())

    for stime in np.arange(0, sim_time, timestep):
        # send update (do next time step) to FMU simulation
        api_model.send_update()
        # getter to store the measured output signals
        out = api_model.get_output()
        append_storage(output_storage, out, stime)

    plot("Motor Current", output_storage["time"], output_storage["sut.mot.i"])
    plot("Motor Phi", output_storage["time"], output_storage["sut.mot.phi"])

def plot(name, x,y):
    # Update plot with new data
    plt.figure(name)
    plt.plot(x, y)

def init_storage(keys):
    store_init = dict()
    store_init.update({"time":[]})
    for key in keys:
        store_init.update({key:[]})
    return store_init

def append_storage(store, data, time):
    for key, val in data.items():
        if key == "time":
            store[key].append(time)
        else:
            store[key].append(val["value"])
    return store

if __name__ == '__main__':
    # Create new interface object to communicate with the docker simulation
    # Parameter: name is used for indicate the correlated logging messages (default="")
    api_model = api.API_FMU_Local("model")
    main()
    plt.show()