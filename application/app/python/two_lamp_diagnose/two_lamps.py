import os
import json
import matplotlib.pyplot as plt
# Import the FMU docker interface package for python
import api_fmu_docker.api_lib as api

path = "application/model/two_lamp_model/"


# simple data processing for representation in Prolog code style
def process_data_to_logic(out):
    out_dict = dict()

    if out["sut.bulb1.i"]["value"] > 0.005:
        lamp_1_ok = "val(light({}),{}).".format("l1","on")
    else:
        lamp_1_ok = "val(light({}),{}).".format("l1","off")
    
    if out["sut.bulb2.i"]["value"] > 0.005:
        lamp_2_ok = "val(light({}),{}).".format("l2","on")
    else:
        lamp_2_ok = "val(light({}),{}).".format("l2","off")

    if int(out["sut.sw.mode"]["value"]) == 2:
        switch_ok = "on(s)."
    else:
        switch_ok = "off(s)."
    
    out_dict.update({"l1":lamp_1_ok, "l2":lamp_2_ok, "sw":switch_ok})
    
    return out_dict

# Output file reset
def reset():
    with open(path + 'test_lamps_obs.pl','w') as f:
        f.write("")
        f.close()
    with open('application/app/python/two_lamp_diagnose/out.csv', 'w') as f:
        f.write("")
        f.close()
    with open('application/app/python/two_lamp_diagnose/out.json', 'w') as f:
        f.write("")
        f.close()

# Write observations to Prolog file to read in ASP Diagnose Tool
def write_observations(observations):  
    with open(path + 'test_lamps_obs.pl','w') as f:
        for key, val in observations.items():
            f.write(val+ '\n')
    f.close()
          
def main():
    # Configuration file path
    config_model = 'application/config/config_two_lamps.json'
    
    # Load configuration file
    api_model.init_interface_config_client(config_model)
    
    # Upload FMU file
    api_model.upload_fmu()
    
    # Upload FMU file
    api_model.upload_config()

    # Reset FMU model
    api_model.send_reset()

    print("# FMU Model available variables: ", json.dumps(api_model.get_all_variable_names(), indent=4))
    # get simulation time step size from config file
    timestep = api_model.get_timestep()
    
    # set simulation time
    sim_time = 0.4 # sec
    
    # temporary variable holding simulation output to ensure only diagnose state changes
    out_logic_old = dict({"l1":-1, "l2":-1, "sw":-1})
    out_list = list()
    for i in range(int(round(sim_time / timestep))):
        # send update (do next time step) to FMU simulation
        api_model.send_update()
        # getter to store the measured output signals
        out = api_model.get_output()
        
        # ------------------#
        # ASP DIAGNOSE TOOL #
        # ------------------#
        
        # send signal data to convert to logic representation
        out_logic = process_data_to_logic(out)
        
        if out_logic != out_logic_old:
            
            write_observations(out_logic)
            config=  (
                "--index {}".format((i+1)*timestep)  + 
                " --file application/model/two_lamp_model/two_lamps_example_orig.pl" +
                " --answersets 5" +
                " --faultsize 2" +
                " --observation application/model/two_lamp_model/test_lamps_obs.pl" +
                " --output application/app/python/two_lamp_diagnose/out" +
                " --json"
                )      
            os.system("./application/app/python/two_lamp_diagnose/asp_diagnose_tool " + config)
            
        out_logic_old = out_logic
        
        out_list.append(out)
    
    time = []
    bat = []
    l1 = []
    l2 = []
    sw = []
    
    for data in out_list:
        time.append(data['time']['value'])
        l1.append(data['sut.bulb1.i']['value'])
        l2.append(data['sut.bulb2.i']['value'])
        bat.append(data['sut.bat.i']['value'])
        if data['sut.sw.mode']['value'] > 1.5:
            sw.append('close')
        else:
            sw.append('open')
    
    fig, axs = plt.subplots(2, 2)
    fig.tight_layout(h_pad=2)
    
    axs[0,0].set_title("sut.bulb1.i")
    axs[0,0].set_xlabel("time [sec]")
    axs[0,0].set_ylabel("A")
    axs[0,0].plot([0.2,0.2],[0,0.05], "--r")
    axs[0,0].text(0.21,0.025, "fault: bulb 1 broken", color ="red")
    axs[0,0].plot(time,l1)
    
    axs[0,1].set_title("sut.bulb2.i")
    axs[0,1].set_xlabel("time [sec]")
    axs[0,1].plot([0.3,0.3],[0.0,0.05], "--", color="orange")
    axs[0,1].set_ylabel("A")
    axs[0,1].plot(time,l2)
    
    axs[1,0].set_title("sut.sw.mode")
    axs[1,0].set_xlabel("time [sec]")
    axs[1,0].plot([0.3,0.3],["open", "close"], "--", color="orange")
    axs[1,0].text(0.31,"open", "fault: sw broken", color="orange")
    axs[1,0].set_ylabel("mode")
    axs[1,0].plot(time,sw)
    
    axs[1,1].set_title("sut.bat.i")
    axs[1,1].set_xlabel("time [sec]")
    axs[1,1].set_ylabel("A")
    axs[1,1].plot([0.3,0.3],[0.0,-0.1], "--", color="orange")
    axs[1,1].plot([0.2,0.2],[0.0,-0.1], "--", color="red")
    axs[1,1].plot(time,bat)
    
    plt.show()
        
if __name__ == '__main__':
    # Create new interface object to communicate with the docker simulation environment
    # Parameter: name is used for indicate the correlated logging messages (default="")
    api_model = api.API_FMU_Docker("model")
    # reset the result output files
    reset()
    # start program
    main()