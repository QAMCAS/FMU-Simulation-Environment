package fmu_client;

import at.tugraz.ist.fmulib.Client;

import java.io.IOException;
import java.util.Map;
import java.lang.*;
import java.util.List;

import static at.tugraz.ist.fmulib.Client.generateInputString;
public class App {

    public static void main(String[] args) throws IOException {
        // Define absolute path of configuration files
        String workingDirectory = "/Users/dkaufman/Documents/projects/AI4DI/fmu_simulation_docker/";
        String model_config_path = workingDirectory + "application/config/config_heater_model.json";
        String control_config_path = workingDirectory + "application/config/config_heater_control_unit.json";
        
        // Load configuration file for model
        Client client_model = Client.initInterfaceConfigClient(model_config_path);
        // Upload model FMU file to server
        client_model.uploadFMUFile();
        // Upload configuration file of model to server
        client_model.uploadConfig();

        // Load configuration file for control unit
        Client client_control = Client.initInterfaceConfigClient(control_config_path);
        // Upload control FMU file to server
        client_control.uploadFMUFile();
        // Upload configuration file of control unit to server
        client_control.uploadConfig();

        // Show all available variables and units of the model
        Map<String, Object> var = client_model.getAllVariableNames();
        System.out.println("# FMU model available variables:");
        var.keySet().forEach(x -> System.out.println(x + " : " + var.get(x).toString()));

        // Show all available variables and units of the model
        Map<String, Object> varC = client_control.getAllVariableNames();
        System.out.println("# FMU control unit available variables:");
        varC.keySet().forEach(x -> System.out.println(x + " : " + varC.get(x).toString()));

        double timeStep = client_model.getTimeStep();
        double simTime = 18.0;

        for(int i = 0; i < Math.round(simTime/timeStep); ++i) {

            // update FMU heater model 
            client_model.sendUpdate();

            // get data from FMU heater model
            Map<String, Object> data = client_model.getOutput();
            //System.out.println("\n");
            //data.keySet().forEach(x -> System.out.println(x + " : " + data.get(x).toString()));
            // get temperature data
            Map<String, Object> temperature = (Map) data.get("T");
            double temperature_value = (double) temperature.get("value");
            
            // send input update to control model 
            client_control.setInput(generateInputString("T_measured", temperature_value));
            
            // update FMU heater controller 
            client_control.sendUpdate();

            // get data from FMU control model
            Map<String, Object> control = client_control.getOutput();
            // get heater switch data
            Map<String, Object> heater_sw = (Map) control.get("heater_sw");
            double heater_sw_value = (double) heater_sw.get("value");
            
            // send input update to heater model 
            client_model.setInput(generateInputString("heater_sw", heater_sw_value));
        }
    }
}
