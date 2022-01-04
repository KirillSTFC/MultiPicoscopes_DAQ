import ctypes 
from picosdk.ps6000 import ps6000 as ps
import numpy as np
from picosdk.functions import adc2mV, assert_pico_ok
from datetime import datetime
import matplotlib.pyplot as plt 

#######################################Serial numbers initialization#######################################
status = {}                             #these variables will be like addresses for different picoscopes. This one has serial number AY166/038 
status2 = {}                            #This one serial number is EQ232/018
ccount = ctypes.c_int16()               #this variable is for total number of picoscopes
cserials = (ctypes.c_char_p * 10)()     #some necessary initialization
cserialLth = ctypes.c_int16()           #some necessary initialization
serial1 = b'AY166/038'                  #First picoscope serial number
cserial1 = ctypes.c_char_p(serial1)     #First picoscope serial number(writing as a string)
serial2 = b'EQ232/018'                  #Second picoscope serial number
cserial2 = ctypes.c_char_p(serial2)     #Second picoscope serial number(writing as a string)
ps.ps6000EnumerateUnits(ctypes.byref(ccount), ctypes.byref(cserials), ctypes.byref(cserialLth)) #some necessary initialization. Checking what is connected
print(ccount) #Print number of devices which were found
chandle = ctypes.c_int16()          #This is also to address to a first picoscope
chandle2 = ctypes.c_int16()         #This is to address the second picoscope
#############################################################################################################
#################################Open PicoScope with ps6000OpenUnit() function###############################
status["openunit"] = ps.ps6000OpenUnit(ctypes.byref(chandle), cserial1)
assert_pico_ok(status["openunit"])
status2["openunit"] = ps.ps6000OpenUnit(ctypes.byref(chandle2), cserial2)
assert_pico_ok(status2["openunit"])
#############################################################################################################
MaxVoltageFilename = "max_voltage.dat"
filename="Ch1_2_trace.dat"
#############################################################################################################
"Channel set up using ps60000SetChannel() function output assigned to list 'setChA in 'status' dictionary."
#######################################Chanel setup for 1st picscope#########################################    
setch_Channel = 0            #sets channel to be assigned settings. B=1, C=2 etc.
setch_Enabled = 1            #enables channel
setch_Coupling = 1           #sets Pico coupling to 50ohm DC. AC = 0, (Mohm)DC = 1.
setch_Range = 9              #sets variable PicoScope voltage range to 50mV. 100mV = 3, 200mV = 4, etc.
setch_Offset = 0             #sets analogue offet (leave alone)
setch_BandwidthLimiter = 0   #turns off bandwidth limiter. 1 = -3dB, limited to 25MHz.
status["setChA"] = ps.ps6000SetChannel(chandle, setch_Channel, setch_Enabled, setch_Coupling, setch_Range, setch_Offset, setch_BandwidthLimiter)
status2["setChA"] = ps.ps6000SetChannel(chandle2, setch_Channel, setch_Enabled, setch_Coupling, setch_Range, setch_Offset, setch_BandwidthLimiter)
assert_pico_ok(status["setChA"])
assert_pico_ok(status2["setChA"])
#######################################Chanel setup for 2nd picscope########################################    
setch_Channel = 1            #sets channel to be assigned settings. B=1, C=2 etc.
setch_Enabled = 1            #enables channel
setch_Coupling = 1           #sets Pico coupling to 50ohm DC. AC = 0, (Mohm)DC = 1.
setch_Range = 8              #sets variable PicoScope voltage range to 50mV. 100mV = 3, 200mV = 4, etc.
setch_Offset = 0             #sets analogue offet (leave alone)
setch_BandwidthLimiter = 0   #turns off bandwidth limiter. 1 = -3dB, limited to 25MHz.
status["setChB"] = ps.ps6000SetChannel(chandle, setch_Channel, setch_Enabled, setch_Coupling, setch_Range, setch_Offset, setch_BandwidthLimiter)
status2["setChB"] = ps.ps6000SetChannel(chandle2, setch_Channel, setch_Enabled, setch_Coupling, setch_Range, setch_Offset, setch_BandwidthLimiter)
assert_pico_ok(status["setChB"])
assert_pico_ok(status2["setChB"]) 
############################################################################################################
"Trigger set up using ps6000SetSimpleTrigger() function assigned to 'trigger' in 'status' dictionary."
settrig_Enabled = 1                  #enables trigger
settrig_SourceChannel = 5            #sets trigger source channel. B = 1, C = 2, etc.
settrig_Threshold = 10               #sets trigger threshold to approximate percentage fraction of range i.e. 10%. Can set negative threshold using negative percentage, i.e -10 = -10%
settrig_Direction = 2                #sets trigger direction to Rising Edge. Above = 0, Below = 1, Rising = 2, Falling = 3, Rising OR Falling = 4
settrig_AutoTrigger_ms = 100000        #For Trig. Mode: Auto. Number of milliseconds that device will wait if no trigger occurs
settrig_Delay = 0    
status["trigger"] = ps.ps6000SetSimpleTrigger(chandle, settrig_Enabled, settrig_SourceChannel, int(round(settrig_Threshold * 325.12,0)), settrig_Direction, settrig_Delay, settrig_AutoTrigger_ms)
status2["trigger"] = ps.ps6000SetSimpleTrigger(chandle2, settrig_Enabled, settrig_SourceChannel, int(round(settrig_Threshold * 325.12,0)), settrig_Direction, settrig_Delay, settrig_AutoTrigger_ms)    
assert_pico_ok(status["trigger"])
assert_pico_ok(status2["trigger"])
###################################################################################################
#setting number of samples before and after trigger
#########################
preTriggerSamples = 100
postTriggerSamples = 1000
maxSamples = preTriggerSamples + postTriggerSamples
"setting PicoScope time base settings using ps6000GetTimebase2() function assigned to 'Timebase' in 'status' dictionary."
                #setting sampling rate by adjusting settimebase_SamplingInterval variable
                #formula for 0 < settimebase_SamplingInterval < 4 :
                #       real sampling interval = [2^(settimebase_SamplingInterval)]/(5 billion)
                #for 5 < settimebase_SamplingInterval < [2^(32) - 1] :
                #       real sampling interval = (settimebase_SamplingInterval - 4)/ 156,250,000
                #i.e.
                ###################################################################
                # settimebase_SamplingInterval   ---     real sampling interval   #
                ###################################################################
                #              0                 ---             200ps            #
                #              1                 ---             400ps            #
                #              2                 ---             800ps            #
                #              3                 ---             1.6ns            #
                #              4                 ---             3.2ns            #
                ###################################################################
                #              5                 ---             6.4ns            #
                #              ...               ---             ...              #
                #           2^(32) - 1           ---             6.87s            #
                ###################################################################
    
settimebase_SamplingInterval = 10000                         #see above table 
settimebase_SampleNumber = maxSamples                        #sets sample number to previously defined maximum variable "maxSamples"
settimebase_ReturnedTimeInterval_ns = ctypes.c_float()       #this is a value output by the funtion
settimebase_Oversampling = 0                                 #used to average voltage over time. Set to 0 unless setting understood.
settimebase_ReturnedMaxSamples = ctypes.c_int32()            #output by function. Max no. of samples available on exit. 
settimebase_SegmentationIndex = 0                            #index of memory segment to use. 
status["Timebase"] = ps.ps6000GetTimebase2(chandle, settimebase_SamplingInterval, settimebase_SampleNumber, ctypes.byref(settimebase_ReturnedTimeInterval_ns), settimebase_Oversampling, ctypes.byref(settimebase_ReturnedMaxSamples), settimebase_SegmentationIndex)
status2["Timebase"] = ps.ps6000GetTimebase2(chandle2, settimebase_SamplingInterval, settimebase_SampleNumber, ctypes.byref(settimebase_ReturnedTimeInterval_ns), settimebase_Oversampling, ctypes.byref(settimebase_ReturnedMaxSamples), settimebase_SegmentationIndex)
assert_pico_ok(status["Timebase"])
assert_pico_ok(status2["Timebase"])
###################################################################################################
"Setting a data writing loop"
EventsNo = 10           # Number of pulses above trigger threshold recorded
#peakHeights = np.empty((EventsNo,1))                        #empty array to hold peak heights
#pulseIntegrals = np.empty((EventsNo,1))                     #empty array to hold pulse integrals
#pulseIntegrals_2 = np.empty((EventsNo,1))
pulses = 0    
while pulses<EventsNo:    
    "A function to collect a block of data using the ps6000RunBlock() function assigned to 'runBlock' in 'status' dictionary."
    ###############################################################################################
    runBlock_preTrigSamples = preTriggerSamples                         
    runBlock_postTrigSamples = postTriggerSamples
    runBlock_SamplingInterval = settimebase_SamplingInterval
    runBlock_Oversampling = 0
    runBlock_SamplingTime = None                                    #Output. Time in ms that the scope will spend collecting samples. Set to 'None' if unimportant
    runBlock_SegmentationIndex = 0                                  
    status["runBlock"] = ps.ps6000RunBlock(chandle, runBlock_preTrigSamples, runBlock_postTrigSamples, runBlock_SamplingInterval, runBlock_Oversampling, runBlock_SamplingTime, runBlock_SegmentationIndex, None, None)
    status2["runBlock"] = ps.ps6000RunBlock(chandle2, runBlock_preTrigSamples, runBlock_postTrigSamples, runBlock_SamplingInterval, runBlock_Oversampling, runBlock_SamplingTime, runBlock_SegmentationIndex, None, None)
    assert_pico_ok(status["runBlock"])
    assert_pico_ok(status2["runBlock"])
    ###############################################################################################
    "Check that scope has finished collecting data using ps6000IsReady() function"
    ###############################################################################################
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps6000IsReady(chandle, ctypes.byref(ready))
    while ready.value == check.value:
        status2["isReady"] = ps.ps6000IsReady(chandle2, ctypes.byref(ready))
    ###############################################################################################
    "Creating local buffers"
    ###############################################################################################
    bufferAMax = (ctypes.c_int16 * maxSamples)()        #Chanel 1, pico 1
    bufferAMin = (ctypes.c_int16 * maxSamples)()        #Chanel 1, pico 1
    bufferAMax2 = (ctypes.c_int16 * maxSamples)()       #Chanel 2, pico 1
    bufferAMin2 = (ctypes.c_int16 * maxSamples)()       #Chanel 2, pico 1
    bufferAMax_2 = (ctypes.c_int16 * maxSamples)()      #Chanel 1, pico 2
    bufferAMin_2 = (ctypes.c_int16 * maxSamples)()      #Chanel 1, pico 2
    
    "Assign data to the local buffer variables and Loading data from PicoScope to the computer using ps6000getValues() function"
    #########################################################Chanel 1, pico 1############################################################
    setbuff_Channel = 0                             #Channels assigned as prior, A = 0, B = 1, etc.
    setbuff_BuffMax = bufferAMax                    #Function output of buffer max data
    setbuff_BuffMin = bufferAMin                    #Function output of buffer min data
    setbuff_BuffLength = maxSamples                 #Calling previous variable
    setbuff_DownSamplingRatioMode = 0               #Related to Aggregate Mode. Set to 0 unless understood.
    status["setDataBuffersA"] = ps.ps6000SetDataBuffers(chandle, setbuff_Channel, ctypes.byref(setbuff_BuffMax), ctypes.byref(setbuff_BuffMin), setbuff_BuffLength, setbuff_DownSamplingRatioMode)
    assert_pico_ok(status["setDataBuffersA"])
    getdata_StartIndex = 0
    getdata_cmaxSamples = ctypes.c_int32(maxSamples)            # Convert maxSamples to a 32 bit integer for next function:
    getdata_DownSampleRatio = 1
    getdata_DownSampleRatioMode = 0
    getdata_SegmentationIndex = 0
    getdata_Overflow = ctypes.c_int16()                         # Create overflow location, which tells us if any channels saturated
    status["getValues"] = ps.ps6000GetValues(chandle, getdata_StartIndex, ctypes.byref(getdata_cmaxSamples), getdata_DownSampleRatio, getdata_DownSampleRatioMode, getdata_SegmentationIndex, ctypes.byref(getdata_Overflow))
    assert_pico_ok(status["getValues"])
    #########################################################Chanel 2, pico 1############################################################
    setbuff_Channel = 1                             #Channels assigned as prior, A = 0, B = 1, etc.
    setbuff_BuffMax2 = bufferAMax2                    #Function output of buffer max data
    setbuff_BuffMin2 = bufferAMin2                    #Function output of buffer min data
    setbuff_BuffLength = maxSamples                 #Calling previous variable
    setbuff_DownSamplingRatioMode = 0               #Related to Aggregate Mode. Set to 0 unless understood.
    status["setDataBuffersB"] = ps.ps6000SetDataBuffers(chandle, setbuff_Channel, ctypes.byref(setbuff_BuffMax2), ctypes.byref(setbuff_BuffMin2), setbuff_BuffLength, setbuff_DownSamplingRatioMode)
    assert_pico_ok(status["setDataBuffersB"])
    getdata_StartIndex = 0
    getdata_cmaxSamples = ctypes.c_int32(maxSamples)            # Convert maxSamples to a 32 bit integer for next function:
    getdata_DownSampleRatio = 1
    getdata_DownSampleRatioMode = 0
    getdata_SegmentationIndex = 0
    getdata_Overflow = ctypes.c_int16()                         # Create overflow location, which tells us if any channels saturated
    status["getValues2"] = ps.ps6000GetValues(chandle, getdata_StartIndex, ctypes.byref(getdata_cmaxSamples), getdata_DownSampleRatio, getdata_DownSampleRatioMode, getdata_SegmentationIndex, ctypes.byref(getdata_Overflow))
    assert_pico_ok(status["getValues2"])
    #########################################################Chanel 1, pico 2############################################################
    setbuff_Channel = 0                             #Channels assigned as prior, A = 0, B = 1, etc.
    setbuff_BuffMax_2 = bufferAMax_2                    #Function output of buffer max data
    setbuff_BuffMin_2 = bufferAMin_2                    #Function output of buffer min data
    setbuff_BuffLength = maxSamples                 #Calling previous variable
    setbuff_DownSamplingRatioMode = 0               #Related to Aggregate Mode. Set to 0 unless understood.
    status2["setDataBuffersA"] = ps.ps6000SetDataBuffers(chandle2, setbuff_Channel, ctypes.byref(setbuff_BuffMax_2), ctypes.byref(setbuff_BuffMin_2), setbuff_BuffLength, setbuff_DownSamplingRatioMode)
    assert_pico_ok(status2["setDataBuffersA"])
    getdata_StartIndex = 0
    getdata_cmaxSamples = ctypes.c_int32(maxSamples)            # Convert maxSamples to a 32 bit integer for next function:
    getdata_DownSampleRatio = 1
    getdata_DownSampleRatioMode = 0
    getdata_SegmentationIndex = 0
    getdata_Overflow_2 = ctypes.c_int16()                         # Create overflow location, which tells us if any channels saturated
    status2["getValues3"] = ps.ps6000GetValues(chandle2, getdata_StartIndex, ctypes.byref(getdata_cmaxSamples), getdata_DownSampleRatio, getdata_DownSampleRatioMode, getdata_SegmentationIndex, ctypes.byref(getdata_Overflow_2))
    assert_pico_ok(status2["getValues3"])
    #####################################################################################################################################
    "Converting data to readable arrays"
    #Find maximum ADC count value
    maxADC = ctypes.c_int16(32512)
    # Convert ADC counts data to mV
    adc2mVChAMax = adc2mV(bufferAMax, setch_Range, maxADC)
    adc2mVChAMax2 = adc2mV(bufferAMax2, setch_Range, maxADC)
    adc2mVChAMax_2 = adc2mV(bufferAMax_2, setch_Range, maxADC)
    print(adc2mVChAMax)
    print(adc2mVChAMax2)
    print(adc2mVChAMax_2)
    # Create time data
    #print(getdata_cmaxSamples.value)
    #print(settimebase_ReturnedTimeInterval_ns.value)
    #print(getdata_cmaxSamples.value)
    time = np.linspace(0, (getdata_cmaxSamples.value) * settimebase_ReturnedTimeInterval_ns.value*1e-9, getdata_cmaxSamples.value)
    #time = np.linspace(0, ((settimebase_SamplingInterval - 4)/ 156,250,000)*maxSamples*, getdata_cmaxSamples.value)
    "Stop capture"
    status["stop"] = ps.ps6000Stop(chandle)
    assert_pico_ok(status["stop"])
    status2["stop"] = ps.ps6000Stop(chandle2)
    assert_pico_ok(status2["stop"])
    print('Finished writing data.')

    "Plotting collected trace"
    ######################################################################################################################################
    def my_plotter(ax, data1, data2, param_dict):
        """
        A helper function to make a graph
    
        Parameters
        ----------
        ax : Axes
            The axes to draw to
    
        data1 : array
           The x data
    
        data2 : array
           The y data
    
        param_dict : dict
           Dictionary of kwargs to pass to ax.plot
    
        Returns
        -------
        out : list
            list of artists added
        """
        out = ax.plot(data1, data2, **param_dict)
        return out
    data = time#[0:10100]
    data1 = adc2mVChAMax#[0:10100]
    data2 = adc2mVChAMax2#[0:10100]
    data1_2 = adc2mVChAMax_2#[0:10100]
    fig, ax = plt.subplots(1, 1)
    my_plotter(ax, data, data1, {'marker':''})
    my_plotter(ax, data, data2, {'marker':''})
    my_plotter(ax, data, data1_2, {'marker':''})
    ax.set_xlabel('sec')
    ax.set_ylabel('mV')
    ######################################################################################################################################
    "Writing file with a spectrum"
    ######################################################################################################################################
    timestamp = datetime.now()
    MaxVoltage = max(adc2mVChAMax)
    MaxVoltage2 = max(adc2mVChAMax2)
    MaxVoltage_2 = max(adc2mVChAMax_2)
    PulseIntegralsDataFile = open(MaxVoltageFilename, "a")
    vIntDataString1 = "pulse %d \t " %pulses
    vIntDataString = vIntDataString1 +timestamp.strftime("%m-%d-%H-%m \t") + "%f \t" %MaxVoltage + "%f \t" %MaxVoltage2  + "%f \n" %MaxVoltage_2
    PulseIntegralsDataFile.write(vIntDataString)
    PulseIntegralsDataFile.close()
    ######################################################################################################################################
    '''
    "Writing file with signals"
    FilenameTimestamp = timestamp.strftime("%Y-%m-%d")
    str2="%s_"%FilenameTimestamp
    str3="%d"%pulses
    filestring = filename+str2+str3+".dat"
    
    voltageDataFile = open(filestring, "w")
    
    for i in adc2mVChAMax:        ###I HAVE STOPPED HERE. trying to reimaging how to write all plots in the file. Alternatively we can just try to save a figure of shots with labels. I think actually it will be the best way.
        voltageDataFile.write("%f \n" %i)
    #for i in adc2mVChAMax2:        
        #voltageDataFile.write("%f \n" %i)    
    voltageDataFile.close()
    
    
    #peak = argrelmax(data2, order=5)
    '''
    pulses = pulses + 1
    
# Close scope with ps60000CloseUnit() function
ps.ps6000CloseUnit(chandle)    
ps.ps6000CloseUnit(chandle2)  

print(status)
#print(peak)

#with open('python_streamed_PicoScope_square_wave_data_.dat', 'w+') as voltageDataFile:
#    for i in adc2mVChAMax:
#            voltageDataFile.write('%f \n' %i)