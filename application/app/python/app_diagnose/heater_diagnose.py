from math import ceil
import os

abs_path = "application/app/python/app_diagnose/"

class Diagnose:
    def __init__(self):
        self.val_obs_temp_init = "val(int(tm),"
        self.val_obs_temp = "val(int(tm),"
        self.val_obs_sw = "val(out(sw),"
        self.val_obs_sw_type2 = "off(sw"
        self.val_obs_heater = "val(out(h),"
        self.val_obs_battery = "val(out(bat),"
        
        self.obs_temp = [self.val_obs_temp_init + "null,0)."]
        self.obs_sw = [self.val_obs_sw + "null,0)."]
        self.obs_sw_type2 = [self.val_obs_sw_type2 + ",0)."]
        self.obs_heater = [self.val_obs_heater + "null,0)."]
        self.obs_battery = [self.val_obs_battery + "low,0)."]
        
        self.cnt_time = 0
        
    def temperature_logic(self, temperature):
        t_low = 10
        t_up = 20
        t_max = 22
        
        t = ceil(temperature)
        value = "null"

        if t == 0:
            value = "null"
        elif t > 0 and t < t_low:
            value = "between(t_low, null)"
        elif t == t_low:
            value = "t_low"
        elif t > t_low and t < t_up:
            value = "between(t_up, t_low)"
        elif t == t_up:
            value = "t_up"
        elif t > t_up and t < t_max:
            value = "between(t_max, t_up)"
        elif t >= t_max:
            value = "t_max"

        return value

    def switch_logic(self, switch):
        if switch == True:
            sw = "max"
        elif switch == False:
            sw = "null"
        else:
            sw = "null"
        return sw
    
    def switch_type2_logic(self, switch):
        if switch == True:
            sw = "on(sw"
        elif switch == False:
            sw = "off(sw"
        else:
            sw = "off(sw"
        return sw

    def heater_logic(self, heater):
            
        if heater >= 80.0:
            h = "t_max"
        elif heater < 80.0 and heater > 0.0:
            h = "t_half"
        elif heater <= 0.0:
            h = "null"
        else:
            h = "null"
        
        return h

    def reset(self):
        self.obs_temp = [self.val_obs_temp_init + "null,0)."]
        self.obs_sw = [self.val_obs_sw + "null,0)."]
        self.obs_sw_type2 = [self.val_obs_sw_type2 + ",0)."]
        self.obs_heater = [self.val_obs_heater + "null,0)."]
        self.obs_battery = [self.val_obs_battery + "low,0)."]
        self.cnt_time = 0
        with open(abs_path + 'test_heater_obs.pl','w') as f:
            f.write("")
            f.close()
        with open(abs_path + 'out.csv', 'w') as f:
            f.write("")
            f.close()
        with open(abs_path + 'out.json', 'w') as f:
            f.write("")
            f.close()

    # use to have all observations
    def diagnose(self, time, signal):
        old_obs = ""
        cnt = 0
        
        with open(abs_path + 'test_heater_obs.pl','r') as f:
            #old_obs = f.readline()
            lines = f.readlines()
            if len(lines) > 0:
                old_obs = lines[-1]
                cnt = len(lines)
            f.close()
        
        with open(abs_path + 'test_heater_obs.pl','a') as f:
            if cnt > 15:
                signal = 0
            obs = self.val_obs_temp + ",{},{}).\n".format(self.temperature_logic(signal), cnt)

            obs_split = obs.rsplit(",", 1)[0]
            old_split = old_obs.rsplit(",", 1)[0]

            if obs_split != old_split:
                f.write(obs)
                f.close()
            else:
                f.close()
        
        config= "--index {} -f application/app/python/app_diagnose/test_heater_circuit.pl -a 5  --faultsize 3 --observation application/app/python/app_diagnose/test_heater_obs.pl --output out --csv --json".format(time)
        os.system("./asp_diagnose_tool " + config)

    def observation_validator(self, logic, obs, obs_new):
        if logic:
            if obs[0].rsplit(',', 1)[0] != obs_new.rsplit(',', 1)[0]:
                obs.insert(0, obs_new)
                if len(obs) > 2:
                    obs.pop(-1)
                obs[1] = obs[1].rsplit(',', 1)[0] + ", 1)."
        else:
            obs.insert(0, obs_new)
            if len(obs) > 1:
                obs.pop(-1)
        
        return obs
        
    def diagnose_2(self, time, temperature, switch, battery, heater):

        obs_temp_new = self.val_obs_temp + "{},{}).".format(self.temperature_logic(temperature), 1)
        self.obs_temp = self.observation_validator(True, self.obs_temp, obs_temp_new)
        
        #obs_sw_new = self.val_obs_sw + "{},{}).".format(self.switch_logic(switch), 1)
        #self.obs_sw = self.observation_validator(False, self.obs_sw, obs_sw_new)
        
        obs_sw_type2_new = "{},{}).".format(self.switch_type2_logic(switch), 2)
        self.obs_sw_type2 = self.observation_validator(False, self.obs_sw_type2, obs_sw_type2_new)
        
        #obs_heater_new = self.val_obs_heater + "{},{}).".format(self.heater_logic(heater), 1)
        #self.obs_heater = self.observation_validator(False, self.obs_heater, obs_heater_new)
        
        #obs_battery_new = self.val_obs_battery + "{},{}).".format((battery), 1)
        #self.obs_battery = self.observation_validator(False, self.obs_battery, obs_battery_new)
        
        with open(abs_path + 'test_heater_obs.pl','w') as f:
            for obs in self.obs_temp:
                f.write(obs + '\n')
            #for obs in self.obs_sw:
            #    f.write(obs + '\n')
            for obs in self.obs_sw_type2:
                f.write(obs + '\n')
            #for obs in self.obs_heater:
            #    f.write(obs + '\n')
            #for obs in self.obs_battery:
            #    f.write(obs + '\n')
            
            f.close()
            self.cnt_time +=1
            
        config= "--index {} -f application/app/python/app_diagnose/test_heater_circuit.pl -a 5  --faultsize 3 --observation application/app/python/app_diagnose/test_heater_obs.pl --output application/app/python/app_diagnose/out --csv --json".format(time)
        os.system("application/app/python/app_diagnose/asp_diagnose_tool " + config)
     
    def observation_validator_all(self, logic, obs, obs_new):
        obs.insert(0, obs_new)
        if logic:
            if len(obs) > 2:
                obs.pop(-1)   
        else:
            if len(obs) > 1:
                obs.pop(-1)
        
        return obs
    
    def diagnose_all(self, time, temperature, switch, battery, heater):
    
        obs_temp_new = self.val_obs_temp + "{},{}).".format(self.temperature_logic(temperature), time)
        self.obs_temp = self.observation_validator_all(True, self.obs_temp, obs_temp_new)
        #self.obs_temp.append(obs_temp_new)
        
        obs_sw_new = self.val_obs_sw + "{},{}).".format(self.switch_logic(switch), time)
        self.obs_sw = self.observation_validator_all(True, self.obs_sw, obs_sw_new)
        #self.obs_sw.append(obs_sw_new)
        
        obs_sw_type2_new = "{},{}).".format(self.switch_type2_logic(switch), time)
        self.obs_sw_type2 = self.observation_validator_all(True, self.obs_sw_type2, obs_sw_type2_new)
        #self.obs_sw_type2.append(obs_sw_new)
        
        obs_heater_new = self.val_obs_heater + "{},{}).".format(self.heater_logic(heater), time)
        self.obs_heater = self.observation_validator_all(True, self.obs_heater, obs_heater_new)
        #self.obs_heater.append(obs_heater_new)
        
        obs_battery_new = self.val_obs_battery + "{},{}).".format((battery), time)
        self.obs_battery = self.observation_validator_all(True, self.obs_battery, obs_battery_new)
        
        with open(abs_path + 'test_heater_obs.pl','w') as f:
            for obs in self.obs_temp:
                f.write(obs + '\n')
            for obs in self.obs_sw:
                f.write(obs + '\n')
            #for obs in self.obs_sw_type2:
            #    f.write(obs + '\n')
            #for obs in self.obs_heater:
            #    f.write(obs + '\n')
            for obs in self.obs_battery:
                f.write(obs + '\n')
            
            f.close()
            self.cnt_time +=1
            
        config= "--index {} -f application/app/python/app_diagnose/test_heater_circuit.pl -a 5  --faultsize 3 --observation application/app/python/app_diagnose/test_heater_obs.pl --output application/app/python/app_diagnose/out --csv --json".format(time)
        os.system("application/app/python/app_diagnose/asp_diagnose_tool " + config)