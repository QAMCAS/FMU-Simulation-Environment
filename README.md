---

### Project Acknowledgments: 
#### AI4DI - Artificial Intelligence for Digitising Industry

The research was supported by ECSEL JU under the project H2020 826060 AI4DI - Artificial Intelligence for Digitising Industry. AI4DI is funded by the Austrian Federal Ministry of Transport, Innovation and Technology (BMVIT) under the program ”ICT of the Future” between May 2019 and April 2022. More information can be retrieved from https://iktderzukunft.at/en/.

---

# FMU Simulation Environment for Cyber-Physical Systems Co-Design

This project builds a docker environment with a running server to trigger a simulation based on an FMU model. The FMU model can be controlled by a client using a implemented REST API on the server (docker).

The developed application provides an entire environment to configure, run, observe and control simulations related to CPS models. In general, the application is set up as a client-server system to distribute the structure between the provider of a service, the server, and the service requester, the client. The service executed on the server is defined as the simulator environment providing the options to observe and control the simulation by client requests during run-time. The reason of using a client-server system is to detach the simulation environment and the observation/control process. The separation enables the user to utilize individual programming environments/languages as client, whereas the server works independent to the selected client environment. In order to develop the mentioned system, a Docker Container is used to run the server application independent on the operating system (OS) as Linux, MacOS or Windows. In addition, Docker is a self-contained environment where all dependencies for the simulator and communication methods are preinstalled and configured. The communication to the client outside the Docker is realized with Flask, an interface, based on REST which enables the server to receive requests as well as to send responses from the simulator to the client. 

In order to run a simulation of a CPS model with the described application, a fundamental requirement is to generate a standardized FMU from the given model. Common modeling software as Modelica or Matlab has an FMU generation tool already implemented, but there are also other applications, as e.g. UniFMU, which are capable of generating a FMU from different language source code (Python, Java or C/C++). A FMU enables to use a general simulation environment for all kind of models, although they are build on different sources.

For the purpose of enabling the simulation environment of reading and interacting with FMUs, the open source Python package PyFMI is utilized. Thus Python is selected as the main programming environment for the simulator.

Since the target of the application is to use a trigger to tell the FMU to step forward a given time, it is essential that the FMU is generated as a CS (CO-Simulation) model. With a CS FMU the numeric solver is embedded in the model and allows a step-by-step simulation to read the outputs and set new inputs after each timestep. 
Since the application is introduced as a full working client-server system, a Python and Java library interface is developed to enable the client easy access to the REST API communication. Therefore, the interface library provides different methods in Python and Java to load, send, set and get information to/from the simulator server.

![FMU simulation client server environment](/docu/client_server.png "FMU simulation client server environment")

# Environment Setup
The follwoing sections describe the setup process to build the Docker simulation environment related to different operating systems as MAC OS, Linux or Windows.

## Mac OS and Linux (using setup scripts)
1. Build docker image on system
```
cd fmu_simulation_docker/setup_scripts
./build_docker_image.sh
```

2. Start docker server environment with auto selection port / 1 container per provided argument
```
cd fmu_simulation_docker/setup_scripts
./start_docker.sh name01 name02
```

3. Start docker server environment with provided port (:XX) / 1
container per provided argument
```
cd fmu_simulation_docker/setup_scripts
./start_docker.sh name01:81 name02:82
```

4. Show all running docker container with name and port
```
cd fmu_simulation_docker/setup_scripts
./show_docker.sh
```

5. Stop and remove all docker container added
```
cd fmu_simulation_docker/setup_scripts
./stop_docker.sh name01 name02
```

6. Build conda environment on system with interface library 
    - conda environment called **_fmu_sim_**
    - _if Conda is not installed you can download and intall it for the related OS: https://docs.conda.io/en/latest/miniconda.html_
```
cd fmu_simulation_docker/setup_scripts
./create_client_conda_env.sh

conda activate fmu_sim
```
## Mac OS and Linux (using terminal)

1. Build docker image on system
```
cd fmu_simulation_docker/fmu_docker_server
docker build . -t fmu_docker_env
```

2. Start Docker container if not existing (or removed before).

- Start docker server environment with auto selection port and container name ("ContainerName", e.g.: model)
```
docker run -d -p 0:5000 --name "ContainerName" fmu_docker_env
```

    
- Start docker server environment with provided port ("Port", e.g.: 80) and container name ("ContainerName", e.g.: model)
```
docker run -d -p "Port":5000 --name "ContainerName" fmu_docker_env
```

3. Start Docker container if stopped.
```
docker start --name "ContainerName"
```

4. Show all running docker container with name and port
```
docker ps -a
```

5. Stop docker container with name ("ContainerName", e.g.: model).
```
docker stop "ContainerName"
```

6. Remove docker container with name ("ContainerName", e.g.: model).
```
docker rm "ContainerName"
```

7. Build conda environment on system with interface library 
    - conda environment called **_fmu_sim_**
    - _if Conda is not installed you can download and intall it for the related OS: https://docs.conda.io/en/latest/miniconda.html_
```
cd fmu_simulation_docker/setup_scripts
bash create_client_conda_env.sh

conda activate fmu_sim
```

## Windows

1. Build docker image on system
```
cd fmu_simulation_docker\fmu_docker_server
docker build . -t fmu_docker_env
```

2. Start Docker container if not existing (or removed before).

- Start docker server environment with auto selection port and container name ("ContainerName", e.g.: model)
```
docker run -d -p 0:5000 --name "ContainerName" fmu_docker_env
```

    
- Start docker server environment with provided port ("Port", e.g.: 80) and container name ("ContainerName", e.g.: model)
```
docker run -d -p "Port":5000 --name "ContainerName" fmu_docker_env
```

3. Start Docker container if stopped.
```
docker start --name "ContainerName"
```

4. Show all running docker container with name and port
```
docker ps -a
```

5. Stop docker container with name ("ContainerName", e.g.: model).
```
docker stop "ContainerName"
```

6. Remove docker container with name ("ContainerName", e.g.: model).
```
docker rm "ContainerName"
```

7. Build conda environment on system with interface library 
    - conda environment called **_fmu_sim_**
    - _if Conda is not installed you can download and intall it for the related OS: https://docs.conda.io/en/latest/miniconda.html_
```
cd fmu_simulation_docker\setup_scripts
bash create_client_conda_env.sh

conda activate fmu_sim
```
