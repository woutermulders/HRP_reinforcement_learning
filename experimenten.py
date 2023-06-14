#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from json.encoder import INFINITY
#from msilib.schema import IniFile
from threading import local
from unittest import result
import numpy as np
from graaf import graafOmgeving
from slimmeSpeler import Agent, Agent_type
from helper import LearningCurvePlot, ComparisonPlot
import time
from slimme_speler_toestandsruimte import Agent_toestands

 
class experiment_class(object):


    def __init__(self, n_steden, n_different_graphs, epochs, typeVerdeling, minValue, maxValue, alphas_L, c_parameters_L):
        self.n_steden = n_steden
        self.n_different_graphs = n_different_graphs
        self.epochs = epochs
        self.alpha_parameters = alphas_L
        self.c_parameters = c_parameters_L

        #initialiseer de grafen


        self.grafen = []
        self.pads = []
        self.oude_knopen = []
        self.resultaten_optimal = []
        self.resultaten_kortstebuur = []
        self.resultaten_gemiddeld = []    
        for graph_type  in range(0, n_different_graphs):
            self.grafen.append(graafOmgeving(n_steden, minValue, maxValue, type=typeVerdeling))
            self.pads.append([])#leeg pad toevoegen
            oude_knoop = np.random.choice(range(1, (n_steden + 1), 1))#start willekeurig punt
            self.pads[graph_type] = [oude_knoop]#pad beginnen op willeukerig punt
            self.resultaten_optimal.append(self.grafen[graph_type].optimalReward())
            self.resultaten_kortstebuur.append(self.grafen[graph_type].optimalRewardDichtsbijzijndebuurtheurestiek())
            self.resultaten_gemiddeld.append(self.grafen[graph_type].rewardBijEenGemiddeldeRonde())

            self.oude_knopen.append(oude_knoop)



    def experiment_montecarlo(self, agentType, speciale_toestandsruimte = False, aantal_toestanden = 1, tijdsAfhankelijk = False):


        resultaten_learning_gretig_mean = {}
        resultaten_learning_gretig_var = {}
        resultaten_learning_agent_mean = {}
        resultaten_learning_agent_var = {}


        for local_c in self.c_parameters:
            for local_a in self.alpha_parameters:
                resultaten_agent = []
                resultaten_agent_optimal = []
                for graaf, pad in zip(self.grafen, self.pads):
                    local_resultaten = []
                    local_resultaten_agent_optimal = []
                    counter = 0# zet een counter
                    
                    if speciale_toestandsruimte:
                        agent = Agent_toestands(self.n_steden, local_c, local_a, aantal_toestanden ,graaf.eigenMatrix(), tijdsAfhankelijk ,agentType)
                    else:
                        agent = Agent(self.n_steden, local_c, local_a, graaf.eigenMatrix() ,agentType)


                    oude_knoop = pad[0]
                    while (counter / self.n_steden)  < self.epochs:
                        if graaf.isFinished(pad):
                            padcopy = pad.copy()
                            end_reward = graaf.actie(pad[-1], pad[0:len(pad) - 1])
                            teller = 0
                            for knopen in pad:
                                teller +=1
                                tussen_reward_2 = graaf.actie(padcopy[-1], padcopy[0:len(padcopy) - 1])
                                if speciale_toestandsruimte:
                                    agent.update(pad[0:teller], padcopy[1], tussen_reward_2)
                                else:
                                    agent.update(padcopy[0], padcopy[1], tussen_reward_2)
                                padcopy.pop(0)
                                if len(padcopy) == 1:
                                    break
                            local_resultaten.append(end_reward)
                            tussen_pad = agent.pad_optimal_short()
                            tussen_reward = graaf.actie(tussen_pad[-1], tussen_pad[0:-1])
                            local_resultaten_agent_optimal.append(tussen_reward)
                            oude_knoop = np.random.choice(range(1, (self.n_steden + 1), 1))
                            pad = [oude_knoop]
                        nieuwe_knoop = agent.selecteer_actie(counter / self.n_steden, pad)
                        pad = pad + [nieuwe_knoop]
                        oude_knoop = nieuwe_knoop
                        counter = counter + 1
                    resultaten_agent.append(local_resultaten)
                    resultaten_agent_optimal.append(local_resultaten_agent_optimal)
                
                

                resultaten_learning_gretig_mean[str(local_c) + str(local_a)] = np.mean(resultaten_agent_optimal, axis=0)
                resultaten_learning_gretig_var[str(local_c) + str(local_a)] = np.std(resultaten_agent_optimal, axis=0)
                resultaten_learning_agent_mean[str(local_c) + str(local_a)] = np.mean(resultaten_agent, axis=0)
                resultaten_learning_agent_var[str(local_c) + str(local_a)] = np.std(resultaten_agent, axis=0)

        return_optimaal_mean = np.mean(self.resultaten_optimal)
        return_gemiddeld_mean = np.mean(self.resultaten_gemiddeld)
        return_kortstebuur_mean = np.mean(self.resultaten_kortstebuur)


        return [resultaten_learning_gretig_mean, resultaten_learning_gretig_var, resultaten_learning_agent_mean, resultaten_learning_agent_var, return_optimaal_mean, return_gemiddeld_mean, return_kortstebuur_mean]
        
