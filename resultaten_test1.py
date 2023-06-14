from cmath import sqrt
from email.mime import base
from itertools import count
from json.encoder import INFINITY
from pickle import TRUE
from random import uniform
from re import X
import string
#from msilib.schema import IniFile
from threading import local
from unittest import result
import numpy as np
from graaf import graafOmgeving
from slimmeSpeler import Agent, Agent_type
from helper import Barplot, LearningCurvePlot, ComparisonPlot
from experimenten import experiment_class
from experimenten_n_stap import N_STAP_EXPERIEMNT
from slimme_speler_toestandsruimte import Agent_toestands
import time
import ray
import scipy.optimize as opt
import math 


def resultaten():


    aantal_steden_array = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    aantal_verschilende_grafen = 10
    aantal_epochs = 3000
    verdeling = "uniform"
    min_value = 76
    max_value = 124
    alpha_array = [0.01, 0.1, 0.3, 0.5, 0.9]
    exporatie_array = [0.001, 0.15, 0.3, 0.6, 0.8, 0.999]

    type_agenten_array = [Agent_type.Epsilon_gretig, Agent_type.LCB, Agent_type.OPTIMISTIC_INIT, Agent_type.Gradient_tempetature]
    type_agenten_tekst = ["ε-greedy", "LCB", "OI", "GT"]

    RAY_ARRAY = []
    n_steden_array = []
    for n_steden in aantal_steden_array:
        n_steden_array.append(experiment_class(n_steden, aantal_verschilende_grafen, aantal_epochs, verdeling, min_value, max_value, alpha_array, exporatie_array))

    for type_agent in type_agenten_array:
        for a in n_steden_array:
            RAY_ARRAY.append(getback.remote(type_agent , a))


    RAY_RESULTATEN = ray.get(RAY_ARRAY) 
    plot1 = LearningCurvePlot(5, -25, "Aantal steden" ,"% verschil tot het gemiddelde (baseline)", "Vergelijking algoritmes")


    resultaten_best_array_grafiek1 = []
    resultaten_gemiddelde_array_grafiek1 = []
    resultaten_heurestiek_array_grafiek1 = []
    for k in range(len(type_agenten_array)):
        resultaten_bestagent_mean_array_grafiek1 = []
        j = k * len(aantal_steden_array)
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(aantal_steden_array)):
            resultaten_bestagent_mean = RAY_RESULTATEN[i + j][0] #gemiddelde_gretig van ... steden
            best = RAY_RESULTATEN[i + j][4] ##beste
            gemiddelde = RAY_RESULTATEN[i + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[i + j][6]  #heurestiek
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            eind_resultaat_mean = sum(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)][-10:]) / 10

            if(k == 0):
                resultaten_best_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, best))
                resultaten_gemiddelde_array_grafiek1.append(0)
                resultaten_heurestiek_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, heurestiek))
            resultaten_bestagent_mean_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, eind_resultaat_mean))

        tekst_label = "Monte Carlo, " + type_agenten_tekst[k] 
        plot1.add_curve(smoothing_window = 1,x = aantal_steden_array, y = resultaten_bestagent_mean_array_grafiek1, var=None, label= tekst_label, alpha_=1, selfTicks = True)
    plot1.add_curve(smoothing_window = 1,x = aantal_steden_array, y = resultaten_best_array_grafiek1, var=None, label="Optimaal", alpha_=1, selfTicks = True )
    plot1.add_curve(smoothing_window = 1,x = aantal_steden_array, y = resultaten_gemiddelde_array_grafiek1, var=None, label="Gemiddelde (baseline)", alpha_=1, selfTicks = True )
    plot1.add_curve(smoothing_window = 1,x = aantal_steden_array, y = resultaten_heurestiek_array_grafiek1, var=None, label="Kortste buur heuristiek", alpha_=1, selfTicks = True)

    plot1.save("resultaten_1_steden_links.png")
        


    
    plot2 = LearningCurvePlot(5, -25, "Aantal iteraties" ,"% verschil tot het gemiddelde (baseline)", "Procentuele verandering van diverse algoritmes")
    te_kiezen_steden = [6, 12]
    te_kiezen_steden_index = []

    type_line = ["solid", "dashed"]
    type_kleur = ["red", "green", "orange", "blue"]

    for a in range(len(aantal_steden_array)):
        for b in range(len(te_kiezen_steden)):
            if aantal_steden_array[a] == te_kiezen_steden[b]:
                te_kiezen_steden_index.append(a)

 




    x = [i for i in range(1, aantal_epochs)]
    for k in range(len(type_agenten_array)):
        j = k * len(aantal_steden_array)
        for i in range(len(te_kiezen_steden_index)):
            nieuw_index = te_kiezen_steden_index[i]
            resultaten_bestagent_mean = RAY_RESULTATEN[nieuw_index + j][0] #gemiddelde_gretig van ... steden
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            best = RAY_RESULTATEN[nieuw_index + j][4] ##beste
            gemiddelde = RAY_RESULTATEN[nieuw_index + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[nieuw_index + j][6]  #heurestiek
            resultaten_agent = procentueleVeranderingTotOpzichtVanBaseLine_list([gemiddelde] * len(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)]), resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)])
            if k == 0 and i == 0:
                baseline = [0] * len(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)])
                plot2.add_curve_color_line(smoothing_window = 51,x = x, y = baseline, label="Gemiddelde (baseline)", color="black", line="solid")

            tekst_label_L = "Monte Carlo, " + str(type_agenten_tekst[k]) + " ,n" + str(te_kiezen_steden[i])
            plot2.add_curve_color_line(smoothing_window = 51,x = x, y = resultaten_agent, label=tekst_label_L, color=type_kleur[k], line=type_line[i])

    plot2.save("resultaten_1_steden_rechts.png")



def resultaten2():


    aantal_steden = 10
    aantal_boot_strapping = [i for i in range(1, aantal_steden + 1)]
    aantal_verschilende_grafen = 10
    aantal_epochs = 3000
    verdeling = "uniform"
    min_value = 76
    max_value = 124
    alpha_array = [0.01, 0.1, 0.3, 0.5, 0.9]
    exporatie_array = [0.001, 0.15, 0.3, 0.6, 0.8, 0.999]

    type_agenten_array = [Agent_type.Epsilon_gretig, Agent_type.LCB, Agent_type.OPTIMISTIC_INIT, Agent_type.Gradient_tempetature]
    type_agenten_tekst = ["ε-greedy", "LCB", "OI", "GT"]
    RAY_ARRAY = []

    graaf_example = N_STAP_EXPERIEMNT(aantal_steden, aantal_verschilende_grafen, aantal_epochs, verdeling, min_value, max_value, alpha_array, exporatie_array)

    for type_agent in type_agenten_array:
        for b in aantal_boot_strapping:
            RAY_ARRAY.append(getback_n_sars.remote(type_agent, b, "SARSA", graaf_example))


    RAY_RESULTATEN = ray.get(RAY_ARRAY) 
    plot1 = LearningCurvePlot(5, -25, "k-bootstrapping" ,"% verschil tot het gemiddelde (baseline)", "Vergelijking 1 tot 10-bootstrapping, SARSA")


    resultaten_best_array_grafiek1 = []
    resultaten_gemiddelde_array_grafiek1 = []
    resultaten_heurestiek_array_grafiek1 = []
    for k in range(len(type_agenten_array)):
        resultaten_bestagent_mean_array_grafiek1 = []
        j = k * len(aantal_boot_strapping)
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(aantal_boot_strapping)):
            resultaten_bestagent_mean = RAY_RESULTATEN[i + j][0] #gemiddelde_gretig van ... steden
            best = RAY_RESULTATEN[i + j][4] ##beste
            gemiddelde = RAY_RESULTATEN[i + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[i + j][6]  #heurestiek
            
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            eind_resultaat_mean = sum(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)][-10:]) / 10
            if(k == 0):
                resultaten_best_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, best))
                resultaten_gemiddelde_array_grafiek1.append(0)
                resultaten_heurestiek_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, heurestiek))
            resultaten_bestagent_mean_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, eind_resultaat_mean))

        tekst_label = "SARSA, " + type_agenten_tekst[k] 
        plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_bestagent_mean_array_grafiek1, var=None, label= tekst_label, alpha_=1, selfTicks = True)
    plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_best_array_grafiek1, var=None, label="Optimaal", alpha_=1, selfTicks = True )
    plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_gemiddelde_array_grafiek1, var=None, label="Gemiddelde (baseline)", alpha_=1, selfTicks = True)
    plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_heurestiek_array_grafiek1, var=None, label="Kortste buur heuristiek", alpha_=1, selfTicks = True)

    plot1.save("resultaten_2_steden_links.png")


    plot2 = LearningCurvePlot(5, -25, "Aantal iteraties" ,"% verschil tot het gemiddelde (baseline)", "Procentuele verandering van diverse algoritmes")

    agent_uitkomsten = []
    x = [i for i in range(1, aantal_epochs)]
    for k in range(len(type_agenten_array)):
        j = k * len(aantal_boot_strapping)
        local_variable = []
        for i in range(len(aantal_boot_strapping)):
            resultaten_bestagent_mean = RAY_RESULTATEN[i + j][0] #gemiddelde_gretig van ... n-bootstrapping
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            best = RAY_RESULTATEN[i + j][4] ##beste
            gemiddelde = RAY_RESULTATEN[i + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[i + j][6]  #heurestiek

            resultaten_agent = procentueleVeranderingTotOpzichtVanBaseLine_list([gemiddelde] * len(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)]), resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)])
            local_variable.append(resultaten_agent)
            if k == 0 and i == 0:
                baseline = [0] * len(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)])
                plot2.add_curve_color_line(smoothing_window = 51,x = x, y = baseline, label="Gemiddelde (baseline)", color="black", line="solid")
        agent_uitkomsten.append(local_variable)

    avg_of_agents_for_each_bootstrap = []
    for a in range(len(agent_uitkomsten[0])):
        total = [0] * len(agent_uitkomsten[0][0]) 
        for b in range(len(agent_uitkomsten)):
            total = [x + y for x, y in zip(total, agent_uitkomsten[b][a])] 
        total = [x / len(agent_uitkomsten) for x in total]
        avg_of_agents_for_each_bootstrap.append(total)




    R_ARRAY = [0] * len(avg_of_agents_for_each_bootstrap)
    G_ARRAY = [200] * len(avg_of_agents_for_each_bootstrap)
    B_ARRAY = [200] * len(avg_of_agents_for_each_bootstrap)

    

    if len(R_ARRAY) > 1:
        R_waarde_verhoging = 255 / (len(R_ARRAY) - 1)
        huidige_R = 0
        for a in range(len(R_ARRAY)):
            R_ARRAY[a] = huidige_R
            huidige_R += R_waarde_verhoging

            
        

    waardes_boot_strapping = [1, 3, 4, 7, 8]
    colors = ["lightgray", "dimgray", "hotpink", "blue", "green", "yellow", "cyan", "azure", "orange", "lime"]

    for index in range(len( waardes_boot_strapping)):
        waarde = waardes_boot_strapping[index]
        resultaten_agent = avg_of_agents_for_each_bootstrap[waarde - 1]
        labeL_text = str(waarde) + "-bootstrapping"
        plot2.add_curve_color_line(smoothing_window = 51,x = x, y = resultaten_agent, label=labeL_text , color=colors[index], line="solid")

    plot2.save("resultaten_2_steden_rechts.png")


def resultaten4():


    aantal_steden = 50
    aantal_verschilende_grafen = 10
    aantal_epochs = 10000




    parameters_uniform = [[98, 102], [88, 112], [76, 124], [50, 150], [25, 175] , [1, 199]]
    alle_parameters = parameters_uniform
    variance_array = []

    for uniform_ in parameters_uniform:
        b_ = uniform_[1]
        a_ = uniform_[0]
        variance_array.append ( (1/12)*(b_ - a_) * (b_ - a_))
    




    alpha_array = [0.01, 0.1, 0.3, 0.5, 0.9]
    exporatie_array = [0.001, 0.15, 0.3, 0.6, 0.8, 0.999]



    type_agenten_array = [Agent_type.Epsilon_gretig, Agent_type.LCB, Agent_type.OPTIMISTIC_INIT, Agent_type.Gradient_tempetature]
    type_agenten_tekst = ["ε-greedy", "LCB", "OI", "GT"]

    RAY_ARRAY = []


    for type_agent in type_agenten_array:
        for index in range(len(alle_parameters)):
            mijn_class = N_STAP_EXPERIEMNT(aantal_steden, aantal_verschilende_grafen, aantal_epochs, "uniform", alle_parameters[index][0], alle_parameters[index][1], alpha_array, exporatie_array)
            RAY_ARRAY.append(getback_n_sars.remote(type_agent, 2, "SARSA", mijn_class))


    RAY_RESULTATEN = ray.get(RAY_ARRAY) 

    plot1 = LearningCurvePlot(5, -90, "Variantie" ,"% verschil tot het gemiddelde (baseline)", "Vergelijking variantie voor verschillende strategieën")

    type_lijnen = ["solid", "dashed", "dotted"]
    type_kleuren = ["black", "blue", "orange", "green", "gray"]

    #[agent_type [ variance ]
    counter = 0
    for k in range(len(type_agenten_array)):
        resultaten_bestagent_mean_array_grafiek1 = []
        resultaten_heuristiek = []
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(alle_parameters)):
            resultaten_bestagent_mean = RAY_RESULTATEN[counter][0] #gemiddelde_gretig van ... steden
            gemiddelde = RAY_RESULTATEN[counter][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[counter][6]  #heurestiek
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            eind_resultaat_mean = sum(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)][-10:]) / 10

            resultaten_bestagent_mean_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, eind_resultaat_mean))
            if k == 0:
                resultaten_heuristiek.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, heurestiek))
            counter += 1
        if k == 0:
            plot1.add_curve_color_line(smoothing_window = 1,x = variance_array, y = resultaten_heuristiek, label="Kortste buur heuristiek", color="brown", line=type_lijnen[0])
        tekst_label = "2-bootstrapping-sarsa-" + type_agenten_tekst[k]
        plot1.add_curve_color_line(smoothing_window = 1,x = variance_array, y = resultaten_bestagent_mean_array_grafiek1, label=tekst_label, color=type_kleuren[k], line=type_lijnen[0])
    plot1.add_curve(smoothing_window = 1,x = variance_array, y = [0] * len(variance_array), var=None, label="Gemiddelde (baseline)" , alpha_=1)
    plot1.save("resultaten_4_steden_links.png")

def resultaten5():


    aantal_steden_array = [50]
    aantal_verschilende_grafen = 10
    aantal_epochs = 1000

    verdeling_array = ["uniform", "lognormal", "gamma", "eucelidian"]
    parameters_uniform = [[76, 124]]

    parameters_lognormaal = [[4.59566, 0.137906]]
    parameters_gamma = [[625/12, 48/25]]
    parameters_eucelidian = [[100, -1]]

    alle_parameters = [parameters_uniform, parameters_lognormaal, parameters_gamma, parameters_eucelidian]



    alpha_array = [0.01, 0.1, 0.3, 0.5, 0.9]
    exporatie_array = [0.001, 0.15, 0.3, 0.6, 0.8, 0.999]

    type_agenten_array = [Agent_type.Epsilon_gretig, Agent_type.LCB, Agent_type.OPTIMISTIC_INIT, Agent_type.Gradient_tempetature]
    type_agenten_tekst = ["ε-greedy", "LCB", "OI", "GT"]

    RAY_ARRAY = []
    n_steden_array = []
    for index in range(len(alle_parameters)):
        for n_steden in aantal_steden_array:
            n_steden_array.append(N_STAP_EXPERIEMNT(n_steden, aantal_verschilende_grafen, aantal_epochs, verdeling_array[index], alle_parameters[index][0][0], alle_parameters[index][0][1], alpha_array, exporatie_array))

    #[agent_type [ verdeling_ [ alle steden ] ]]
    for type_agent in type_agenten_array:
        for a in n_steden_array:
            RAY_ARRAY.append(getback_n_sars.remote(type_agent, 1, "Q_learning", a))
            

    RAY_RESULTATEN = ray.get(RAY_ARRAY) 
    counter = 0
    mijn_bar_plot = Barplot(verdeling_array, "verschillende verdelingen", "% verschil tot het gemiddelde (baseline)")
    resultaten_bar = []
    for index_1 in range(len(type_agenten_array) + 1):
        local_array = []
        for index_2 in range(len(alle_parameters)):
            local_array.append(40)
        resultaten_bar.append(local_array)


    for k in range(len(type_agenten_array)):
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(alle_parameters)):
            for p in range(len(aantal_steden_array)):
                resultaten_bestagent_mean = RAY_RESULTATEN[counter][0] #gemiddelde_gretig van ... steden
                gemiddelde = RAY_RESULTATEN[counter][5] #gemiddelde
                heurestiek = RAY_RESULTATEN[counter][6]  #heurestiek
                c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
                eind_resultaat_mean = sum(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)][-10:]) / 10

                counter += 1

                mean = procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, eind_resultaat_mean)
                hrk = procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, heurestiek)
                resultaten_bar[k][i] = mean
                if k == 0:
                    resultaten_bar[-1][i] = hrk

                
            
        
    text_array = type_agenten_tekst + ["Kortste buur heuristiek"]
    for a in range(len(resultaten_bar)):
        text_ = text_array[a]
        mijn_bar_plot.voeg_bar_data_toe(resultaten_bar[a], text_)

    mijn_bar_plot.save("resultaten_5_steden_links.png") 

    x = [i for i in range(1, aantal_epochs)]
    counter = 0
    plot2 = LearningCurvePlot(10, -30, "Aantal iteraties" ,"% verschil tot het gemiddelde (baseline)", "Procentuele verandering van diverse algoritmes")
    for k in range(len(type_agenten_array)):
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(alle_parameters)):
            for p in range(len(aantal_steden_array)):
                resultaten_bestagent_mean = RAY_RESULTATEN[counter][0] #gemiddelde_gretig van ... steden
                gemiddelde = RAY_RESULTATEN[counter][5] #gemiddelde
                heurestiek = RAY_RESULTATEN[counter][6]  #heurestiek
                c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
                resulaten_agent = procentueleVeranderingTotOpzichtVanBaseLine_list([gemiddelde] * len(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)]), resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)])
                resulaten_heuristiek = procentueleVeranderingTotOpzichtVanBaseLine_list([gemiddelde] * len(x),  [heurestiek] * len(x))
                counter += 1
                if i == 0:#alleen uniformele verdeling.
                    if k == 0:
                        plot2.add_curve(1 ,x, resulaten_heuristiek, var=None,label="Kortste buur heuristiek", alpha_=1)
                        plot2.add_curve(1 ,x, [0] * len(resulaten_heuristiek), var=None,label="Gemiddelde (baseline)", alpha_=1)
                    text_label = "Q-learning, " + type_agenten_tekst[k]
                    plot2.add_curve(5 ,x, resulaten_agent, var=None,label= text_label, alpha_=1)

                        
                    
                    
    plot2.save("resultaten_5_steden_rechts.png")



    
def resultaten6():


    aantal_steden = 10
    aantal_toestanden = [i for i in range(1, 6)]
    aantal_verschilende_grafen = 10
    aantal_epochs = 3000
    verdeling = "uniform"
    min_value = 76
    max_value = 124
    alpha_array = [0.01, 0.1, 0.3, 0.5, 0.9]
    exporatie_array = [0.001, 0.15, 0.3, 0.6, 0.8, 0.999]


    type_agenten_array = [Agent_type.Epsilon_gretig, Agent_type.LCB, Agent_type.Gradient_tempetature]
    type_agenten_tekst = ["ε-greedy", "LCB", "GT"]

    RAY_ARRAY = []
    graaf_example = experiment_class(aantal_steden, aantal_verschilende_grafen, aantal_epochs, verdeling, min_value, max_value, alpha_array, exporatie_array)

    for type_agent in type_agenten_array:
        for b in aantal_toestanden :
            RAY_ARRAY.append(getback_grotereToestandsRuimte.remote(type_agent, b,graaf_example, False))


    RAY_RESULTATEN = ray.get(RAY_ARRAY) 
    plot1 = LearningCurvePlot(5, -25, "Aantal steden in geheugen" ,"% verschil tot het gemiddelde (baseline)", "Vergelijking van aantal steden in geheugen, voor 10 steden")
    kleuren = ["blue" , "orange", "pink"]
    lines = ["solid", "dashed"]


    resultaten_best_array_grafiek1 = []
    resultaten_gemiddelde_array_grafiek1 = []
    resultaten_heurestiek_array_grafiek1 = []
    for k in range(len(type_agenten_array)):
        resultaten_bestagent_mean_array_grafiek1 = []
        j = k * len(aantal_toestanden)
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(aantal_toestanden)):
            resultaten_bestagent_mean = RAY_RESULTATEN[i + j][0] #gemiddelde_gretig van ... steden
            resultaten_bestagent_var = RAY_RESULTATEN[i + j][1] #var_gretig van .... steden
            best = RAY_RESULTATEN[i + j][4] ##beste
            gemiddelde = RAY_RESULTATEN[i + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[i + j][6]  #heurestiek
            
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            eind_resultaat_mean = sum(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)][-10:]) / 10
            if(k == 0):
                resultaten_best_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, best))
                resultaten_gemiddelde_array_grafiek1.append(0)
                resultaten_heurestiek_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, heurestiek))
            resultaten_bestagent_mean_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, eind_resultaat_mean))


        tekst_label = "Monte Carlo, " + type_agenten_tekst[k] 
        plot1.add_curve_color_line(smoothing_window = 1,x = aantal_toestanden, y = resultaten_bestagent_mean_array_grafiek1,label = tekst_label, color = kleuren[k], line = lines[0], selfTicks = True)
    plot1.add_curve(smoothing_window = 1,x = aantal_toestanden, y = resultaten_best_array_grafiek1, var=None, label="Optimaal", alpha_=1, selfTicks = True )
    plot1.add_curve(smoothing_window = 1,x = aantal_toestanden, y = resultaten_gemiddelde_array_grafiek1, var=None, label="Gemiddelde (baseline)", alpha_=1, selfTicks = True)
    plot1.add_curve(smoothing_window = 1,x = aantal_toestanden, y = resultaten_heurestiek_array_grafiek1, var=None, label="Kortste buur heuristiek", alpha_=1, selfTicks = True)

    plot1.save("resultaten_6_steden_links.png")

    plot2 = LearningCurvePlot(5, -25, "Aantal steden in geheugen" ,"% verschil tot het gemiddelde (baseline)", "Vergelijking van aantal steden in geheugen (tijdsafhankelijk), voor 10 steden")



    
    RAY_ARRAY_2 = []
    for type_agent in type_agenten_array:
        for b in aantal_toestanden:
            RAY_ARRAY_2.append(getback_grotereToestandsRuimte.remote(type_agent, b,graaf_example, True))

    RAY_RESULTATEN_2 = ray.get(RAY_ARRAY_2) 
    
    for k in range(len(type_agenten_array)):
        resultaten_bestagent_mean_array_grafiek1 = []
        j = k * len(aantal_toestanden)
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(aantal_toestanden)):
            resultaten_bestagent_mean = RAY_RESULTATEN_2[i + j][0] #gemiddelde_gretig van ... steden
            best = RAY_RESULTATEN_2[i + j][4] ##beste
            gemiddelde = RAY_RESULTATEN_2[i + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN_2[i + j][6]  #heurestiek
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            eind_resultaat_mean = sum(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)][-10:]) / 10
            resultaten_bestagent_mean_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, eind_resultaat_mean))
        tekst_label = "tijdsafhankelijk-" + "Monte Carlo, " + type_agenten_tekst[k] 
        plot2.add_curve_color_line(smoothing_window = 1,x = aantal_toestanden, y = resultaten_bestagent_mean_array_grafiek1,label = tekst_label, color = kleuren[k], line = lines[1], selfTicks = True)
    plot2.add_curve(smoothing_window = 1,x = aantal_toestanden, y = resultaten_best_array_grafiek1, var=None, label="Optimaal", alpha_=1, selfTicks = True )
    plot2.add_curve(smoothing_window = 1,x = aantal_toestanden, y = resultaten_gemiddelde_array_grafiek1, var=None, label="Gemiddelde (baseline)", alpha_=1, selfTicks = True)
    plot2.add_curve(smoothing_window = 1,x = aantal_toestanden, y = resultaten_heurestiek_array_grafiek1, var=None, label="Kortste buur heuristiek", alpha_=1, selfTicks = True)

    plot2.save("resultaten_6_steden_rechts.png")

    
def resultaten7():


    aantal_steden = 10
    aantal_boot_strapping = [i for i in range(1, aantal_steden + 1)]
    aantal_verschilende_grafen = 10
    aantal_epochs = 3000
    verdeling = "uniform"
    min_value = 76
    max_value = 124
    alpha_array = [0.01, 0.1, 0.3, 0.5, 0.9]
    exporatie_array = [0.001, 0.15, 0.3, 0.6, 0.8, 0.999]

    type_agenten_array = [Agent_type.Epsilon_gretig, Agent_type.LCB, Agent_type.OPTIMISTIC_INIT, Agent_type.Gradient_tempetature]
    type_agenten_tekst = ["ε-greedy", "LCB", "OI", "GT"]

    RAY_ARRAY = []

    graaf_example = N_STAP_EXPERIEMNT(aantal_steden, aantal_verschilende_grafen, aantal_epochs, verdeling, min_value, max_value, alpha_array, exporatie_array)

    for type_agent in type_agenten_array:
        for b in aantal_boot_strapping:
            RAY_ARRAY.append(getback_n_sars.remote(type_agent, b, "Q_learning", graaf_example))


    RAY_RESULTATEN = ray.get(RAY_ARRAY) 
    plot1 = LearningCurvePlot(5, -25, "k-bootstrapping" ,"% verschil tot het gemiddelde (baseline)", "Vergelijking 1 tot 10-bootstrapping, Q-learning")


    resultaten_best_array_grafiek1 = []
    resultaten_gemiddelde_array_grafiek1 = []
    resultaten_heurestiek_array_grafiek1 = []
    for k in range(len(type_agenten_array)):
        resultaten_bestagent_mean_array_grafiek1 = []
        j = k * len(aantal_boot_strapping)
        c_waarde_best, a_waarde_best = (0, 0)
        for i in range(len(aantal_boot_strapping)):
            resultaten_bestagent_mean = RAY_RESULTATEN[i + j][0] #gemiddelde_gretig van ... steden
            resultaten_bestagent_var = RAY_RESULTATEN[i + j][1] #var_gretig van .... steden
            best = RAY_RESULTATEN[i + j][4] ##beste
            gemiddelde = RAY_RESULTATEN[i + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[i + j][6]  #heurestiek
            
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            eind_resultaat_mean = sum(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)][-10:]) / 10
            if(k == 0):
                resultaten_best_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, best))
                resultaten_gemiddelde_array_grafiek1.append(0)
                resultaten_heurestiek_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, heurestiek))
            resultaten_bestagent_mean_array_grafiek1.append(procentueleVeranderingTotOpzichtVanBaseLine_1_item(gemiddelde, eind_resultaat_mean))
        tekst_label = "Q-learning, " + type_agenten_tekst[k] 
        plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_bestagent_mean_array_grafiek1, var=None, label= tekst_label, alpha_=1, selfTicks = True)
    plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_best_array_grafiek1, var=None, label="Optimaal", alpha_=1, selfTicks = True )
    plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_gemiddelde_array_grafiek1, var=None, label="Gemiddelde (baseline)", alpha_=1, selfTicks = True)
    plot1.add_curve(smoothing_window = 1,x = aantal_boot_strapping, y = resultaten_heurestiek_array_grafiek1, var=None, label="Kortste buur heuristiek", alpha_=1, selfTicks = True)

    plot1.save("resultaten_7_steden_links.png")
        


    
    plot2 = LearningCurvePlot(5, -25, "Aantal iteraties" ,"% verschil tot het gemiddelde (baseline)", "Procentuele verandering van diverse algoritmes")




    agent_uitkomsten = []
    x = [i for i in range(1, aantal_epochs)]
    for k in range(len(type_agenten_array)):
        j = k * len(aantal_boot_strapping)
        local_variable = []
        for i in range(len(aantal_boot_strapping)):
            resultaten_bestagent_mean = RAY_RESULTATEN[i + j][0] #gemiddelde_gretig van ... n-bootstrapping
            c_waarde_best, a_waarde_best = krijgBesteParametersterug(alpha_array, exporatie_array, resultaten_bestagent_mean)
            best = RAY_RESULTATEN[i + j][4] ##beste
            gemiddelde = RAY_RESULTATEN[i + j][5] #gemiddelde
            heurestiek = RAY_RESULTATEN[i + j][6]  #heurestiek

            


            resultaten_agent = procentueleVeranderingTotOpzichtVanBaseLine_list([gemiddelde] * len(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)]), resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)])
            local_variable.append(resultaten_agent)
            if k == 0 and i == 0:
                baseline = [0] * len(resultaten_bestagent_mean[str(c_waarde_best) + str(a_waarde_best)])
                plot2.add_curve_color_line(smoothing_window = 51,x = x, y = baseline, label="Gemiddelde (baseline)", color="black", line="solid")

        agent_uitkomsten.append(local_variable)

    avg_of_agents_for_each_bootstrap = []
    for a in range(len(agent_uitkomsten[0])):
        total = [0] * len(agent_uitkomsten[0][0]) 
        for b in range(len(agent_uitkomsten)):
            total = [x + y for x, y in zip(total, agent_uitkomsten[b][a])] 
        total = [x / len(agent_uitkomsten) for x in total]
        avg_of_agents_for_each_bootstrap.append(total)




    R_ARRAY = [0] * len(avg_of_agents_for_each_bootstrap)
    if len(R_ARRAY) > 1:
        R_waarde_verhoging = 255 / (len(R_ARRAY) - 1)
        huidige_R = 0
        for a in range(len(R_ARRAY)):
            R_ARRAY[a] = huidige_R
            huidige_R += R_waarde_verhoging

            
        

    waardes_boot_strapping = [1, 3, 4, 7, 8]
    colors = ["lightgray", "dimgray", "hotpink", "blue", "green", "yellow", "cyan", "azure", "orange", "lime"]

    for index in range(len( waardes_boot_strapping)):
        waarde = waardes_boot_strapping[index]
        resultaten_agent = avg_of_agents_for_each_bootstrap[waarde - 1]
        labeL_text = str(waarde) + "-bootstrapping"
        plot2.add_curve_color_line(smoothing_window = 51,x = x, y = resultaten_agent, label=labeL_text , color=colors[index], line="solid")

    plot2.save("resultaten_7_steden_rechts.png")


        

@ray.remote
def f(x):
    time.sleep(1)
    return x


@ray.remote
def getback(type_agent, classTYPE):
    return classTYPE.experiment_montecarlo(type_agent)

@ray.remote
def getback_grotereToestandsRuimte(type_agent,grote_toestandsruimte, classTYPE, tijdsAfhankelijk):
    return classTYPE.experiment_montecarlo(type_agent, True, grote_toestandsruimte, tijdsAfhankelijk)









@ray.remote
def getback_n_sars(type_agent, n_stap, SARSA_QLEARNING, classTYPE):
    return classTYPE.experiment_n_stap(type_agent, n_stap ,SARSA_QLEARNING)





def krijgBesteParametersterug(alpha_parameters, exploratie_parameters, gegevens):
    returnAlpha = 0
    returnC = 0
    bestValue = INFINITY
    for e in exploratie_parameters:
        for a in alpha_parameters:
            total = sum(gegevens[str(e) + str(a)][-9:])
            if total < bestValue:
                bestValue = total
                returnAlpha = a
                returnC = e
    return [returnC, returnAlpha] 

def procentueleVeranderingTotOpzichtVanBaseLine_1_item(baseline_gemiddelde, andere_gegevens):
    c = 100.0 ## 100 procent, gebruiken voor berekening
    if baseline_gemiddelde is list or andere_gegevens is list:
        raise("baseline gemiddelde en andere gegevens moeten bijde 1 zi")
    return ((c / baseline_gemiddelde) * andere_gegevens) - 100 


def procentueleVeranderingTotOpzichtVanBaseLine_list(baseline_gemiddelde, andere_gegevens):
    c = [100.0] * len(baseline_gemiddelde) ## 100 procent, gebruiken voor berekening
    if len(baseline_gemiddelde) != len(andere_gegevens):
        raise("baseline gemiddelde en andere gegevens moeten even lang zijn!")


    d = [i / j for i, j in zip(c, baseline_gemiddelde)]
    return [(i * j) - 100 for i, j in zip(d, andere_gegevens)]   

def afgeleide_lijst(gegevens):
    new_array = []
    for i in range(len(gegevens) - 1):
        new = (100 / gegevens[i]) * gegevens[i + 1] - 100
        new_array.append(new)
    return new_array

def rgb_to_hex(r, g, b):
  return ('#{0:02x}{1:02x}{2:02x}').format(int(r), int(g), int(b))


if __name__ == '__main__':
    ray.init()
    resultaten() #figuur, 6, - 7 - Monte carlo
    print("resultaten 1")
    resultaten2() #figuur, 8, 9 - SARSA
    print("resultaten 2")
    resultaten4() #figuur 16, variantie, appendix
    print("resultaten 4")
    resultaten5() #figuur 12, 13, Verschillende verdelingen
    print("resultaten 5") 
    resultaten6() #figuur 14, 15, tijdsafhankelijke toestandsruimte groter maken
    print("resultaten 6")
    resultaten7() #figuur, 10, 11 - Q-lerning
    print("resultaten 7") 