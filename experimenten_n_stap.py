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

 
class N_STAP_EXPERIEMNT(object):


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



    def experiment_n_stap(self, agentType, n_bootstrap, Q_LearningOrSarsa):


        resultaten_learning_gretig_mean = {}
        resultaten_learning_gretig_var = {}
        resultaten_learning_agent_mean = {}
        resultaten_learning_agent_var = {}

        ##einde count table. start alplha table.
        for local_c in self.c_parameters:
            for local_a in self.alpha_parameters:
                resultaten_agent = []
                resultaten_agent_optimal = []
                for graaf, pad in zip(self.grafen, self.pads):
                    local_resultaten = []
                    local_resultaten_agent_optimal = []
                    counter = 0# zet een counter
                    agent = Agent(self.n_steden, local_c, local_a, graaf.eigenMatrix() ,agentType)
                    oude_knoop = pad[0]
                    nieuwe_knoop = oude_knoop
                    toestanden_round = [oude_knoop]
                    reward_round = []
                    aantal_stap = -1
                    while (counter / self.n_steden)  < self.epochs:
                        aantal_stap += 1
                        
                        if graaf.isFinished(pad):
                            padcopy = pad.copy()
                            end_reward = graaf.actie(pad[-1], pad[0:len(pad) - 1])
                            if Q_LearningOrSarsa == "SARSA" or Q_LearningOrSarsa == "Q_learning":
                                for a in range(self.n_steden - n_bootstrap):
                                    padcopy.pop(0)

                                for knopen in range(n_bootstrap): #for knopen in pad:
                                    tussen_reward_2 = graaf.actie(padcopy[-1], padcopy[0:len(padcopy) - 1])
                                    agent.update(padcopy[0], padcopy[1], tussen_reward_2)
                                    padcopy.pop(0)
                                    if len(padcopy) == 1:
                                        break
 
                            local_resultaten.append(end_reward)
                            tussen_pad = agent.pad_optimal_short()
                            tussen_reward = graaf.actie(tussen_pad[-1], tussen_pad[0:-1])
                            local_resultaten_agent_optimal.append(tussen_reward)
                            oude_knoop = np.random.choice(range(1, (self.n_steden + 1), 1))
                            nieuwe_knoop = oude_knoop
                            pad = [oude_knoop]

                            
                            toestanden_round = [oude_knoop]
                            reward_round = []
                            aantal_stap = 0

                            ##einde pad is als laatst
                        oude_knoop = nieuwe_knoop
                        nieuwe_knoop = agent.selecteer_actie(counter / self.n_steden, pad)
                        een_stap_reward = graaf.actie_reward(nieuwe_knoop, oude_knoop)
                        reward_round.append(een_stap_reward)
                        toestanden_round.append(nieuwe_knoop)
                        

                        tau = (aantal_stap - 1) - n_bootstrap + 1
                        if tau >= 0 and Q_LearningOrSarsa == "SARSA":
                            G_total = sum(reward_round[tau: min(tau + n_bootstrap, len(reward_round))])
                            if (tau + n_bootstrap) < self.n_steden:
                                value = 0
                                if (len(toestanden_round) < (self.n_steden + 1)):
                                    
                                    
                                    value = agent.krijg_Q_waarde(toestanden_round[-2] , toestanden_round[-1])

                                   
                                agent.update(toestanden_round[tau], toestanden_round[tau + 1], G_total + value)

                        elif tau >= 0 and Q_LearningOrSarsa == "Q_learning":
                            minValue = 0
                            if (len(toestanden_round) < (self.n_steden + 1)):
                                minValue = agent.krijg_Q_LEARNING_min_value(toestanden_round)
                            G_total = sum(reward_round[tau: min(tau + n_bootstrap, len(reward_round))])

                            if (tau + n_bootstrap) < self.n_steden:
                                agent.update(toestanden_round[tau], toestanden_round[tau + 1], G_total + minValue)
                            
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
        
