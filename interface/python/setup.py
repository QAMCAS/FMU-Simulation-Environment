from setuptools import setup, find_packages

VERSION = '1.0.1' 
DESCRIPTION = 'FMU Docker Simulation API'
LONG_DESCRIPTION = 'This library is used as an API to send requests to a Docker FMU simulation environment'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="api_fmu_docker", 
        version=VERSION,
        author="David Kaufmann",
        author_email="<david.kaufmann@ist.tugraz.at>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        scripts=['api_fmu_docker/api_lib.py'],
        packages=find_packages(include=['api_fmu_docker', 'api_fmu_docker.*', 'simulation_local', 'simulation_local.*']),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'api', 'fmu', 'docker', 'simulation'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)