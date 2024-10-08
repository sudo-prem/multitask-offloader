import psutil
import os
import time
import requests
import pstats
from device_profiler import DeviceProfiler
from network_profiler import NetworkProfiler
from task_profiler import TaskProfiler
from battery_tracker import BatteryTracker


class Profiler:

    def __init__(self, task, data_size, code_for_ic=None):
        self.task = task
        self.data_size = data_size
        self.code_for_ic = code_for_ic

        self.task_profiler = TaskProfiler(self.task, self.code_for_ic)
        self.device_profiler = DeviceProfiler()
        self.network_profiler = NetworkProfiler()
        self.batteryTracker = BatteryTracker()

    def get_communication_cost(self):
        # Check Units Network cost for 1 byte
        # milli seconds per byte
        rtt = self.network_profiler.get_rtt()
        return rtt

    def get_data_transporation_cost(self):
        # Network cost for data_size
        # data size should be in bytes
        data_transporation_cost = self.get_communication_cost() * self.data_size
        # milli seconds
        return data_transporation_cost

    def get_local_execution_cost(self):
        # Execution Cost = Data Transportation Cost + Local Execution Cost
        instruction_count = self.task_profiler.get_instruction_count()
        # CPU frequency and Cycles per Instruction (CPI) in User Equipment
        cpu_frequency = self.device_profiler.get_local_cpu_frequency()
        CPI = self.device_profiler.get_local_CPI()

        local_execution_cost = (instruction_count * CPI) / (cpu_frequency / 1000)
        return local_execution_cost

    def get_remote_execution_cost(self):
        # Execution Cost = Data Transportation Cost + Execution Cost in Master Node
        instruction_count = self.task_profiler.get_instruction_count()
        # CPU frequency and Cycles per Instruction (CPI) in Master Node
        # cpu_frequency = self.device_profiler.get_remote_cpu_frequency()
        # CPI = self.device_profiler.get_remote_CPI()
        cpu_frequency, CPI = self.device_profiler.get_remote_metrics()

        data_transporation_cost = self.get_data_transporation_cost()
        remote_execution_cost = (instruction_count * CPI) / (cpu_frequency / 1000)

        total_cost = remote_execution_cost + data_transporation_cost
        return total_cost

    def get_local_energy_consumption(self):
        # Energy Consumption = EPI * Instruction Count
        instruction_count = self.task_profiler.get_instruction_count()
        # Energy per Instruction (EPI) in User Equipment
        EPI = self.batteryTracker.get_local_EPI()
        
        #Convert nano Joules to milli watt hours
        local_energy_consumption = (instruction_count * EPI) / (3600 * 1000000)
        return local_energy_consumption
    
    def get_battery_status(self):
        return self.batteryTracker.get_battery_status()


if __name__ == '__main__':

    # Test
    def add():
        a = 3
        b = 2
        return a + b

    task = add
    data_size = 1
    profiler = Profiler(task, data_size)
    print(profiler.get_local_execution_cost())
    print(profiler.get_remote_execution_cost())
