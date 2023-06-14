from cmath import sqrt
from copy import copy
from email.policy import default
from json.encoder import INFINITY
from os import stat
import random
import numpy as np
import math

from enum import Enum
 
class Agent_type(Enum):
    LCB = 1
    Epsilon_gretig = 2
    Gradient_tempetature = 3
    OPTIMISTIC_INIT = 4
    Default = 5

class Agent(object):

    def __init__(self, n_knopen, c_parameter, learningrate, graaf,agent_T = Agent_type.Default):
        self.steden = n_knopen
        self.graaf = graaf
        self.c_parameter = c_parameter
        self.mijntype = agent_T
        self.gemiddeld_kost_ronde = self.gemiddelde_kost_ronde()
        self.initQ_table()
        self.tablecount_matrix_size = np.zeros((n_knopen, n_knopen)) #two symmetric matrixes
        indices_diagonal = np.diag_indices(n_knopen)
        self.tableQ_matrix_size[indices_diagonal] = INFINITY 
        self.learningrate = learningrate
        
        
        
        

        
    def selecteer_actie(self, epochs, path = []):
        copyRow = self.tableQ_matrix_size[path[-1] - 1]
        KnopenWaarWeNaarToeKunnenGaan = list(range(1, self.steden + 1))
        if len(path) == self.steden:#hier is nog maar 1 keuze
            return path[0] #return eerste knoop, we gaan weer terug ronde is voorbij
        else:#hier zijn er meerdere keuzes
            for knoop in path:
                KnopenWaarWeNaarToeKunnenGaan.remove(knoop)

            copyRow = []
            for a in KnopenWaarWeNaarToeKunnenGaan:
                constante = 0
                na = (self.tablecount_matrix_size[path[-1] - 1])[a - 1]
                if self.mijntype == Agent_type.LCB and self.c_parameter > 0:
                    constante = 0
                    if na > 0:
                        constante = self.c_parameter * sqrt( math.log(epochs) / na)
                    else:
                        constante = INFINITY
                    copyRow.append((self.tableQ_matrix_size[path[-1] - 1])[a - 1] - constante)
                elif self.mijntype == Agent_type.Epsilon_gretig and self.c_parameter > 0:
                    copyRow.append((self.tableQ_matrix_size[path[-1] - 1])[a - 1])
                elif self.mijntype == Agent_type.Gradient_tempetature and self.c_parameter > 0:
                    copyRow.append(math.exp((self.c_parameter * 0.001 * - self.tableQ_matrix_size[path[-1] - 1])[a - 1]))
                    
                elif self.mijntype == Agent_type.OPTIMISTIC_INIT or self.c_parameter == 0:
                    copyRow.append((self.tableQ_matrix_size[path[-1] - 1])[a - 1])
                else:
                    print("Foute agent doorgegeven type 1.")

                        

                    
                
        if len(KnopenWaarWeNaarToeKunnenGaan) == 1:##er is nog maar 1 element
            return KnopenWaarWeNaarToeKunnenGaan[0]

        if self.mijntype == Agent_type.Gradient_tempetature and self.c_parameter > 0:
            local_onderkant = sum(copyRow)
            copyRow = [x / local_onderkant for x in copyRow]


        minValues = minValues = self.argminList(copyRow)
        returnValue = 0
        if self.mijntype == Agent_type.LCB and self.c_parameter > 0:
            returnValue = np.random.choice(minValues)
            return KnopenWaarWeNaarToeKunnenGaan[returnValue]
        elif self.mijntype == Agent_type.Epsilon_gretig and self.c_parameter > 0:
            kansVerdeling = [self.c_parameter/(len(copyRow) - 1) for i in range(len(copyRow))]
            kansVerdeling[np.random.choice(minValues)] = 1 - self.c_parameter
            returnValue = np.random.choice(KnopenWaarWeNaarToeKunnenGaan, p=kansVerdeling)
            return returnValue
        elif self.mijntype == Agent_type.Gradient_tempetature and self.c_parameter > 0:
            returnValue = np.random.choice(KnopenWaarWeNaarToeKunnenGaan, p=copyRow)
            return returnValue
        elif self.mijntype == Agent_type.OPTIMISTIC_INIT or self.c_parameter == 0:
            returnValue = np.random.choice(minValues)
            return KnopenWaarWeNaarToeKunnenGaan[returnValue]
        else:
            print("Foute agent doorgegeven type 2.")
        

        raise Exception("geen gegevens terug gegeven")
        
       
    def update(self, oude_knoop ,nieuwe_knoop, reward):##update systeem
        self.tablecount_matrix_size[oude_knoop - 1, nieuwe_knoop - 1] += 1
        self.tableQ_matrix_size[oude_knoop - 1, nieuwe_knoop - 1] += self.learningrate * (reward - self.tableQ_matrix_size[oude_knoop - 1, nieuwe_knoop - 1])


    def argminList(self, row):#returned de knopen met de laagste idices namens de 1 waarde
        best = np.min(row)
        best_indices = [i for i, x in enumerate(row) if x == best] # Get indices of lowest action value
        return best_indices


    def krijg_Q_LEARNING_min_value(self,huidigepad_met_volgende_toestand):
        if len(huidigepad_met_volgende_toestand) == self.steden:
            return 0
        else:
            oude_c_parameter = self.c_parameter
            self.c_parameter = 0
            returnValue = self.selecteer_actie(1, huidigepad_met_volgende_toestand)
            self.c_parameter = oude_c_parameter
            return returnValue


    def printEindLijst(self):
        print(self.tablecount_matrix_size)
        print(self.tableQ_matrix_size)


    def krijg_Q_waarde(self, toestand, actie):
        return self.tableQ_matrix_size[toestand - 1, actie - 1]

    def pad_optimal_short(self):##returnted het pad met c_parameter = 0
        oude_c_parameter = self.c_parameter
        self.c_parameter = 0
        pad = [1]
        while len(pad) <= self.steden:
            nieuwe_knoop = self.selecteer_actie(1, pad)
            pad += [nieuwe_knoop]
        self.c_parameter = oude_c_parameter
        return pad


    def initQ_table(self):
        self.tableQ_matrix_size = np.zeros((self.steden, self.steden)) #two symmetric matrixes
        if Agent_type.OPTIMISTIC_INIT == self.mijntype:
            for i in range(1, self.steden + 1):
                for j in range(1, self.steden + 1):
                    if i != j:
                        total = (self.steden - 2) * self.graaf[i - 1, j - 1]
                        for i_local in range(1, self.steden + 1):
                            if i_local != i:
                                for j_local in range(1, self.steden + 1):
                                    if j_local != j:
                                        total += self.graaf[i_local - 1, j_local - 1]
                        
                        for i_local in range(1, self.steden + 1):
                            if i_local != i:
                                total += 0.5 * self.graaf[i_local - 1, j - 1]
                        for j_local in range(1, self.steden + 1):
                            if j_local != j:
                                total += 0.5 * self.graaf[i - 1, j_local - 1]
                        total = total * 0.5 * self.steden * (self.c_parameter / ((self.steden) * (self.steden - 2)))
                        self.tableQ_matrix_size[i - 1, j - 1] = total
            

                        
    def gemiddelde_kost_ronde(self):
        total = self.graaf.sum()
        total = self.steden * (total / (self.steden * (self.steden - 1)))
        return total


