from ctypes import sizeof
import nidaqmx
from nidaqmx.task import AUTO_START_UNSET
import numpy as np
from numpy.lib import average
from scipy import signal
import matplotlib.pyplot as plt
from nidaqmx.constants import AcquisitionType, TaskMode

DEFAULT_AVERAGING = 7
DEFAULT_FREQUENCY = 20
DEFAULT_AMPLITUDE = 0.02
DEFAULT_SQUARE_WAVE_DUTY_CYCLE = 0.5
DEFAULT_HOLDING_VOLTAGE = 0

Averaging = DEFAULT_AVERAGING
frequency = DEFAULT_FREQUENCY
amplitude = DEFAULT_AMPLITUDE
square_wave_duty_cycle = DEFAULT_SQUARE_WAVE_DUTY_CYCLE
holding_voltage = DEFAULT_HOLDING_VOLTAGE
Proportion = DEFAULT_SQUARE_WAVE_DUTY_CYCLE # not defined

t = np.linspace(0, 1 / frequency * Averaging, 1000, endpoint=False) # parameter: 0, 1/frequency * Averaging, samples 
s = signal.square(2 * np.pi * frequency * t, duty=square_wave_duty_cycle)# the first parameter is 2 * np.pi * frequency * t

multiclamp_args = [[50, 2000], [2.5e9, 0.1]] #default / 1 ?

# generate square waveform
Sample_clock_array_size = 1000 
Sample_clock_rate = 1000
Timeout = 1000
squarewave = []
for i in s:
    i = i + 1
    squarewave.append(i * amplitude / 2 * multiclamp_args[0][0])

waveform_data = squarewave
waveform_duration = 0.35 #unit? dx?

def filter(): # not complete yet
    print("wave filter")
    pass

with nidaqmx.Task() as master_task, nidaqmx.Task() as slave_task:

    master_task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    slave_task.ao_channels.add_ao_voltage_chan("Dev1/ao0") 

    master_task.timing.cfg_samp_clk_timing(
                                            Sample_clock_rate, 
                                            sample_mode=AcquisitionType.FINITE, 
                                            samps_per_chan= Sample_clock_array_size) 

    slave_task.timing.cfg_samp_clk_timing(
                                            Sample_clock_rate, 
                                            sample_mode=AcquisitionType.FINITE, 
                                            samps_per_chan= Sample_clock_array_size) 

    writedata = slave_task.write(
                                waveform_data, 
                                auto_start = AUTO_START_UNSET,
                                timeout = waveform_duration * 2 + 5
                                ) 

    print(writedata)

    slave_task.control(TaskMode.TASK_COMMIT)  # analog output port is committed

    master_task.control(TaskMode.TASK_COMMIT)  # analog input port is committed

    print('Acqusition is started')
    slave_task.start()
    master_task.start()

    data = master_data = master_task.read(
                                    number_of_samples_per_channel = Sample_clock_array_size,
                                    timeout = waveform_duration * 2 + 5
                                    # not decided yet
                                    )
    
    # print(data)

    plt.plot(t, data, 'r')
    plt.ylim(-5, 5)
    plt.grid()
    plt.show()

    print()


    data[:] = [x * multiclamp_args[0][1] for x in data]

    slave_task.wait_until_done(
                                timeout = waveform_duration * 2 + 5)

    master_task.wait_until_done(
                                timeout = waveform_duration * 2 + 5)

    master_task.stop()
    slave_task.stop()

    # master_task.close()
    # slave_task.close()


    
    # function hasn't be complete yet
    filter()

    #cal resistence form
    data1 = data

    data_avg = np.average(data) # mean

    data1[:] = [data_avg - x for x in data1] 

    data1[:] = [(amplitude * 1000000) / x for x in data1]

    # print(data) #resistence form2

    # cal resistence


    data_output = []    
    """ 
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5, 6])
    newarr = np.array_split(arr, 3)
    print(newarr)

    """

    data_form = np.array_split(data, Averaging)
    

    # print(data_form)

    data_mean = []

    for i in range (0, Averaging):
        """ 
        A = [1,2,3,4,5,6]
        B = A[:len(A)//2]
        C = A[len(A)//2:] 
        method
        """
        print(data_form[i].size)
        cur_data = data_form[i]
        f_data = cur_data[:len(cur_data)//2] # preceding half waveform
        b_data = cur_data[len(cur_data)//2:] # rest half waveform

        split_arg = int((1 - Proportion) * (len(data) / 2)) # comfirm the args

        print(split_arg)

        """ 
        output = [1,2,3]
        print(output[-2:])
         """

        fb_data = f_data[(split_arg - len(f_data)):]
        bb_data = b_data[(split_arg - len(b_data)):] #??

        fb_data_avg = np.average(fb_data)
        bb_data_avg = np.average(bb_data)

        data_mean.append(fb_data_avg - bb_data_avg)
    
    new_data_mean = np.average(data_mean)

    final_resistence = amplitude * 1000000 / new_data_mean





    
    




