# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 14:47:56 2020

@author: Ibrahim Alperen Tunc
"""
import model as mod
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import random
import helper_functions as helpers

#Create the peristimulus time histogram for a sinus modulated sinus curve.
random.seed(666)

parameters = mod.load_models('models.csv') #model parameters fitted to different recordings

#stimulus parameters
ntrials = 100 #number of trials to average over
tlength = 10
tstart = 0.1 #get rid of the datapoints from 0 until this time stamp (in seconds)
cell_idx = 10
contrast = 0.02
contrastf = 10 #frequency of the amplitude modulation in Hz

#model parameters
cell, EODf, cellparams = helpers.parameters_dictionary_reformatting(cell_idx, parameters)

#rest of stimulus parameters depending on model parameters
frequency = EODf #Electric organ discharge frequency in Hz, used for stimulus
t_delta = cellparams["deltat"] #time step in seconds
t = np.arange(0, tlength, t_delta)

#calculate stimulus
stimulus = np.sin(2*np.pi*frequency*t) * (1 + contrast*np.sin(2*np.pi*contrastf*t))

#kernel parameters
kernelparams = {'sigma' : 0.001, 'lenfactor' : 8, 'resolution' : t_delta}

#create kernel
kernel, kerneltime = helpers.spike_gauss_kernel(**kernelparams)

convolvedspklist = np.zeros([t.shape[0],ntrials]) #initialized list of convolved spikes
spiketrains = np.zeros([t.shape[0],ntrials]) #initialized list of spike trains
for i in range(ntrials):
    #run the model for the given stimulus and get spike times
    spiketimes, spikeISI, meanspkfr = helpers.stimulus_ISI_calculator(cellparams, stimulus, tlength=tlength)
    #spike train with logical 1s and 0s
    spikearray = np.zeros(len(t)) 
    #convert spike times to spike trains
    spikearray[np.digitize(spiketimes,t)-1] = 1 #np.digitize(a,b) returns the index values for a where a==b. For convolution
    #for np.digitize() see https://numpy.org/doc/stable/reference/generated/numpy.digitize.html is this ok to use here?
    #np.digitize returns the index as if starting from 1 for the last index, so -1 in the end
    #convolve the spike train with the gaussian kernel    
    convolvedspikes = np.convolve(kernel, spikearray, mode='same')
    convolvedspklist[:,i] = convolvedspikes
    spiketrains[:,i] = spikearray
    
peristimulustimehist = np.mean(convolvedspklist, axis=1)
fig, (axp, axr, axs) = plt.subplots(3,1, sharex = True)

axp.plot(t[t>0.1]*1000, peristimulustimehist[t>0.1])
axp.set_title('Peristimulus time histogram')
axp.set_ylabel('Spiking frequency [Hz]')

axr.plot(t[t>0.1]*1000, spiketrains[t>0.1]*np.arange(1,spiketrains.shape[1]+1).T, 'k.', markersize=1)
axr.set_ylim(0.8 , ntrials+1)
axr.set_title('Spike raster')
axr.set_ylabel('Trial #')

axs.plot(t[t>0.1]*1000, stimulus[t>0.1])
axs.set_title('Stimulus')
axs.set_xlabel('time [ms]')
axs.set_ylabel('Stimulus amplitude [a.u.]')

"""
#check convolution for a model stimulus trial
fig, ax = plt.subplots(1,1)
ax.plot(t, convolvedspikes)
ax.plot(t[spikearray==1], spikearray[spikearray==1]*np.max(convolvedspikes)/2, '.')

#check for example single spike if convolution works
examplespkarray = np.zeros(100000)
examplespkarray[2000] = 1
exampleconvolution = np.convolve(kernel, examplespkarray, mode='same') 
plt.plot(exampleconvolution)
plt.plot(examplespkarray)
#yea it works heheheh
"""