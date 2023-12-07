from skillbridge import Workspace
from skillbridge.client.translator import Symbol
import numpy as np
import matplotlib.pyplot as plt

def waveform_to_vector(waveforms):
    y_vectors = []
    x_vectors = []
    global ws
    for wave in waveforms:
        y_wave = ws.dr.get_waveform_y_vec(wave)
        y_vec = []
        for i in range(ws.dr.vector_length(y_wave)):
            y_vec.append(ws.dr.get_elem(y_wave, i))
        y_vectors.append(y_vec)
        # x vector is same for all these y vector
        x_wave = ws.dr.get_waveform_x_vec(wave)
        x_vec = []
        for i in range(ws.dr.vector_length(x_wave)):
            x_vec.append(ws.dr.get_elem(x_wave, i))
        x_vectors.append(x_vec)
    return x_vectors, y_vectors

def set_poly(cdf, poly,cv):
    #set polynomial length
    poly = np.flip(poly)
    if (len(poly) > 21):
        breakpoint()
    else:
        poly_num = len(poly)-1
    coeff_num = [x for x in cdf.parameters if x.name == 'polyCoef'][0]
    coeff_num.value = poly_num
    for index,c in enumerate(poly):
        coeff_name = 'c'+str(index)
        curr_coeff = [x for x in cdf.parameters if x.name == coeff_name][0]
        curr_coeff.value = str(c)
    ws.db.set_conn_current(cv)
    ws.db.save(cv)
    ws['createNetlist'](recreateAll = True, display = None)
    return
######### Load polynomials
with open('sodium_fits.npy', 'rb') as f:
	na_fits = np.load(f)
breakpoint()

v = np.array([-0.6 , -0.59, -0.58, -0.57, -0.56, -0.55, -0.54, -0.53, -0.52,
       -0.51, -0.5 , -0.49, -0.48, -0.47, -0.46, -0.45, -0.44, -0.43,
       -0.42, -0.41, -0.4 , -0.39, -0.38, -0.37, -0.36, -0.35, -0.34,
       -0.33, -0.32, -0.31, -0.3 , -0.29, -0.28, -0.27, -0.26, -0.25,
       -0.24, -0.23, -0.22, -0.21, -0.2 , -0.19, -0.18, -0.17, -0.16,
       -0.15, -0.14, -0.13, -0.12, -0.11, -0.1 , -0.09, -0.08, -0.07,
       -0.06, -0.05, -0.04, -0.03, -0.02, -0.01,  0.  ,  0.01,  0.02,
        0.03,  0.04,  0.05,  0.06,  0.07,  0.08,  0.09,  0.1 ,  0.11,
        0.12,  0.13,  0.14,  0.15,  0.16,  0.17,  0.18,  0.19,  0.2 ,
        0.21,  0.22,  0.23,  0.24,  0.25,  0.26,  0.27,  0.28,  0.29,
        0.3 ,  0.31,  0.32,  0.33,  0.34,  0.35,  0.36,  0.37,  0.38,
        0.39,  0.4 ,  0.41,  0.42,  0.43,  0.44,  0.45,  0.46,  0.47,
        0.48,  0.49,  0.5 ,  0.51,  0.52,  0.53,  0.54,  0.55,  0.56,
        0.57,  0.58,  0.59,  0.6 ,  0.61,  0.62,  0.63,  0.64,  0.65,
        0.66,  0.67,  0.68,  0.69,  0.7 ,  0.71,  0.72,  0.73,  0.74,
        0.75,  0.76,  0.77,  0.78,  0.79,  0.8 ,  0.81,  0.82,  0.83,
        0.84,  0.85,  0.86,  0.87,  0.88,  0.89,  0.9 ])

##########
vdc = 1.2
vin = 300e-3
RL = 1e3

model_files = [
    ["/home/linux/ieng6/be216fa23/public/ncsu-cdk-1.6.0/ncsu-cdk-1.6.0.beta/models/hspice/public/tsmc18dN.m", ""],
    ["/home/linux/ieng6/be216fa23/public/ncsu-cdk-1.6.0/ncsu-cdk-1.6.0.beta/models/hspice/public/tsmc18dP.m", ""]
    ]

ws = Workspace.open()

# set simulator
ws['simulator'](Symbol('spectre'))
# set schematic
#ws['design']('/home/linux/ieng6/be216fa23/be216fa23ak/cadence/simulation/ocean_test/spectre/schematic/netlist/netlist')
ws['design']("smelly_sensor", "ocean_test", "schematic")
ws['resultsDir']('/home/linux/ieng6/be216fa23/be216fa23ak/cadence/simulation/ocean_test/spectre/schematic')

breakpoint()
#find and modify the current source
cv = ws.db.open_cell_view_by_type("smelly_sensor", "ocean_test", "schematic")
inst = ws.db.find_any_inst_by_name(cv,'G0') #G0 is name of pvccs
cdf = ws.cdf.get_inst_CDF(inst)
poly = [6]
set_poly(cdf,poly,cv)
breakpoint()
ws.db.set_conn_current(cv)
ws.db.save(cv)
net = ws['createNetlist'](recreateAll = True, display = None)


# set model files
ws['modelFile'](model_files[0],model_files[1])
# transient analysis
stop_time = '1'
breakpoint()
ws['analysis'](Symbol('dc'),'?param', 'vin', '?start', '-0.6', '?stop', '0.9', '?values list', v.tolist())
# set design variables
ws['desVar'](      "vdc", vdc    )
ws['desVar'](      "vin", vin    )
ws['desVar'](      "RL", RL    )
# analysis order in case of multiple analysis
ws['envOption'](Symbol('analysisOrder'), ['dc'])
# to be saved
ws['save']( Symbol('v'), "/vin" )
ws['save']( Symbol('i'), "/G0/PLUS" )
# set temp and run
ws['temp'](27)
ws['run']()
#ws['selectResult'](Symbol('tran')) 
ws['selectResult'](Symbol('dc')) 
# extract waveforms
waveforms = [ws.get.data('/vin'), ws.get.data('/G0/PLUS')]
#TODO: support more than two waveforms in woveform to vector
time, vec = waveform_to_vector(waveforms)

all_time=[]
all_vec =[]
for fit in na_fits:
    set_poly(cdf,fit,cv)
    ws['run']()
    #ws['selectResult'](Symbol('tran')) 
    ws['selectResult'](Symbol('dc'))
    waveforms = [ws.get.data('/vin'), ws.get.data('/G0/PLUS')]
    time, vec = waveform_to_vector(waveforms)
    all_time.append(time)
    all_vec.append(vec)
    
breakpoint()
# plot
breakpoint()
for index in range(len(all_vec)):
    p = np.poly1d(na_fits[0])
    plt.plot(all_time[index][0], all_vec[index][1],'--',all_time[index][0],p(all_time[index][0]))
#plt.plot(all_time[1][0], all_vec[1][1])
#plt.plot(all_time[2][0], all_vec[2][1])
#plt.plot(all_time[3][0], all_vec[3][1])
plt.show()
breakpoint()
