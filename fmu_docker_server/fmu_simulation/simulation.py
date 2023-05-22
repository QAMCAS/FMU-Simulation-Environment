from numpy import empty
import pyfmi

class Simulation:
    def __init__(self):
        #self.model = pyfmi.load_fmu(file)
        #self.model.initialize()
        self.timestep = 0.001
        self.datamap = dict()
        self.input = dict()

        self.time = 0.0
        self.dataset_out = []
        self.dataset_param = []
        self.dataset_all = []
        self.variable_names = []

    def init_fmu(self, file):
        try:
            self.model = pyfmi.load_fmu(file)
            self.model.initialize()
            return " FMU file upload successful! \n"
        except:
            return " (!) PYFMI load ERROR."
        
    def update(self):
        status = self.model.do_step(current_t=self.time, step_size=self.timestep, new_step=True)

        if status == pyfmi.fmi.FMI_OK:
            #self.time += self.timestep
            #self.time = round(self.time, 3)
            self.time = self.model.time
            data = self.model.get(self.dataset_out)
            self.datamap.update({'time' : {"value":self.time, "unit":"sec"}})
            #self.datamap.update({'time' : self.model.time()})
            for i in range(len(self.dataset_out)):
                try:
                    unit = self.model.get_variable_unit(self.dataset_out[i])
                except:
                    unit = ""
                self.datamap.update({self.dataset_out[i] : {"value":float(data[i][0]), "unit":unit}})

        #self.time += self.timestep
        #self.time = round(self.time, 3)

        return self.datamap
    
    def reset(self):
        self.model.reset()
        self.time = 0.0
        self.model.initialize()
        self.datamap = dict()

    def set_dataset_output(self, data):
        self.dataset_out = data
    
    def set_timestep(self, step):
        self.timestep = step
    
    def init_input(self, input):
        try:
            for key, val in input.items():
                if key != "time":
                    self.model.set(key, val)
                    self.input.update({key:val})
            #self.model.initialize()
        except:
            print("no init input set")
  
    def set_input(self, input):
        try:
            for key, val in input.items():
                if key != "time":
                    self.model.set(key, val)
                    self.input.update({key:val})
        except:
            print("no input set")

    def get_variable_names(self):
        variable_names = dict()
        model_names = self.model.get_model_variables()
        for model in model_names:
            try:
                unit = self.model.get_variable_unit(model)
            except:
                unit = ""
            variable_names.update({model:unit})
    
        return variable_names

    def get_output(self):
        data_dict = dict()
        data = self.model.get(self.dataset_out)
        data_dict.update({'time' : {"value":self.time, "unit":"sec"}})
        for i in range(len(self.dataset_out)):
            try:
                unit = self.model.get_variable_unit(self.dataset_out[i])
            except:
                unit = ""
            data_dict.update({self.dataset_out[i] : {"value":float(data[i][0]), "unit":unit}})
        return data_dict
    
    def get_timestep(self):
        return self.timestep

    def get_time(self):
        return self.time
    
    def get_input(self):
        return self.input

    #def get_variable_units(self):
    #    print(self.model.get_variable_unit())