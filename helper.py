#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from re import S
from turtle import fillcolor
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

class LearningCurvePlot:

    def __init__(self,y_up, y_down, xlabel, ylabel , title=None):
        self.fig,self.ax = plt.subplots()
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)     
        self.ax.set_ylim([y_down, y_up])
        if title is not None:
            self.ax.set_title(title)
        
    def add_curve(self, smoothing_window,x, y,var=None,label=None, alpha_=1, selfTicks = False):
        ''' y: vector of results
        label: string to appear as label in plot legend '''
        if label is not None:
            self.ax.plot(x, savgol_filter(y,smoothing_window,0),label=label, alpha=alpha_)
        else:
            self.ax.plot(y)
        if var is not None:
            self.ax.fill_between(x, range(len(y)),y+var,y-var, alpha=0.25)
        if selfTicks:
            self.ax.xaxis.set_ticks(x)


            
    def add_curve_color_line(self, smoothing_window,x, y,label, color, line, selfTicks = False):
        ''' y: vector of results
        label: string to appear as label in plot legend '''
        self.ax.plot(x, savgol_filter(y,smoothing_window,0),label=label, color=color, linestyle=line)
        if selfTicks:
            self.ax.xaxis.set_ticks(x)
        
    def save(self,name='test.png'):
        ''' name: string for filename of saved figure '''
        self.ax.legend(loc=(1.04, 0))
        self.fig.savefig(name,dpi=300, bbox_inches="tight")
        

class ComparisonPlot:

    def __init__(self,min, max, aantalEpisodes,title=None):
        self.fig,self.ax = plt.subplots()
        self.ax.set_xlabel('Learning rate α')
        self.ax.set_ylabel("cumulative reward of the last " +  str(1000) + " episodes") 
        self.ax.set_xlim([-0.1,1.0])
        self.ax.set_ylim([min,max])
        if title is not None:
            self.ax.set_title(title)
        
    def add_curve(self,x,y, var=None, label=None):
        ''' x: vector of parameter values
        y: vector of associated mean reward for the parameter values in x 
        label: string to appear as label in plot legend '''
        if label is not None:
            self.ax.plot(x,y,label=label)
        else:
            self.ax.plot(x,y)
        
    def save(self,name='test.png'):
        ''' name: string for filename of saved figure '''
        self.ax.legend()
        self.fig.savefig(name,dpi=300)


class Barplot:

    def __init__(self, namen_bars, xlabel, ylabel):
        self.fig,self.ax = plt.subplots()
        self.mijndata = []
        self.namen_mijn_data = []

        x = np.arange(len(namen_bars))
        self.namen_bars = namen_bars
        self.ax.set_xticks(x) # values
        self.ax.set_xticklabels(namen_bars) # labels
        self.xlabel = xlabel
        self.ylabel = ylabel


    def voeg_bar_data_toe(self, data, naam):
        self.mijndata.append(data)
        self.namen_mijn_data.append(naam)


    def save(self, name_to_save):
        
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
    
        x = np.arange(len(self.mijndata[0]))  # the label locations
        width = 1 / len(x) - 0.15  # the width of the bars
        multiplier = 0

        for a in range(len(self.mijndata)):
            attribute = self.namen_mijn_data[a] 
            measurement = self.mijndata[a]
            offset = width * multiplier
            self.ax.bar(x + offset - 0.2, measurement, width, label=attribute)
            multiplier += 1
        
        self.ax.legend()
        self.fig.savefig(name_to_save)

def smooth(y, window, poly=1):
    '''
    y: vector to be smoothed 
    window: size of the smoothing window '''
    return savgol_filter(y,window,poly)

if __name__ == '__main__':
    # Test Learning curve plot
    x = np.arange(100)
    y = 0.01*x + np.random.rand(100) - 0.4 # generate some learning curve y
    LCTest = LearningCurvePlot(title="Test Learning Curve")
    LCTest.add_curve(y,label='method 1')
    LCTest.add_curve(smooth(y,window=35),label='method 1 smoothed')
    LCTest.save(name='learning_curve_test.png')

    # Test Performance plot
    PerfTest = ComparisonPlot(title="Test Comparison")
    PerfTest.add_curve(np.arange(5),np.random.rand(5),label='method 1')
    PerfTest.add_curve(np.arange(5),np.random.rand(5),label='method 2')
    PerfTest.save(name='comparison_test.png') 


