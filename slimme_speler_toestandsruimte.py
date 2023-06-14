from ast import copy_location
from cmath import sqrt
from copy import copy
from email.policy import default
from json.encoder import INFINITY
from operator import index
from os import stat
from pickle import FALSE
from slimmeSpeler import Agent_type
import random
import numpy as np
import math

from enum import Enum

class Agent_toestands(object):

    def __init__(self, n_knopen, c_parameter, learningrate, lengte_toestand, graaf, tijdsAfhankelijk ,agent_T = Agent_type.Default):
        self.steden = n_knopen
        self.graaf = graaf
        self.c_parameter = c_parameter
        self.mijntype = agent_T
        self.lengte_toestand = lengte_toestand

        

        self.tijdsAfhankelijk = tijdsAfhankelijk
        if tijdsAfhankelijk:
            self.tableQ_matrix_size = []
            self.tablecount_matrix_size = []
            self.initQ_table_tijds()
        else:
            self.tableQ_matrix_size = {}
            self.tablecount_matrix_size = {}
            self.initQ_table()
        self.learningrate = learningrate
        if agent_T ==  Agent_type.OPTIMISTIC_INIT or Agent_type.Default == agent_T:
            raise Exception("Geen goede agent voor deze toestandsruimte")

        
        
        
        

        
    def selecteer_actie(self, epochs, path = []):
        copyRow = []
        KnopenWaarWeNaarToeKunnenGaan = list(range(1, self.steden + 1))
        if len(path) == self.steden:#hier is nog maar 1 keuze
            return path[0] #return eerste knoop, we gaan weer terug ronde is voorbij
        else:#hier zijn er meerdere keuzes
            for knoop in path:
                KnopenWaarWeNaarToeKunnenGaan.remove(knoop)
                #copyRow = np.delete(copyRow, (knoop - 1))
            copyRow = []
            for a in KnopenWaarWeNaarToeKunnenGaan:
                constante = 0
                na = self.krijg_N_waarde(path, a)
                if self.mijntype == Agent_type.LCB and self.c_parameter > 0:
                    constante = 0
                    if na > 0:
                        constante = self.c_parameter * sqrt( math.log(epochs) / na)
                    else:
                        constante = INFINITY
                    copyRow.append((self.krijg_Q_waarde(path, a) - constante))
                elif self.mijntype == Agent_type.Epsilon_gretig and self.c_parameter > 0:
                    copyRow.append((self.krijg_Q_waarde(path, a)))
                elif self.mijntype == Agent_type.Gradient_tempetature and self.c_parameter > 0:
                    copyRow.append(math.exp((self.c_parameter * 0.001 * - self.krijg_Q_waarde(path, a))))
                    
                elif self.mijntype == Agent_type.OPTIMISTIC_INIT or self.c_parameter == 0:
                    copyRow.append(self.krijg_Q_waarde(path, a))
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
        
       
    def update(self, toestand ,nieuwe_knoop, reward):##update systeem
        nieuwe_toestand = toestand[-1 * self.lengte_toestand:]
        if self.tijdsAfhankelijk:
            lengte_tijd = len(toestand) - 1
            ((self.tablecount_matrix_size[lengte_tijd])[str(nieuwe_toestand)])[nieuwe_knoop - 1] += 1
            ((self.tableQ_matrix_size[lengte_tijd])[str(nieuwe_toestand)])[nieuwe_knoop - 1] += self.learningrate * (reward - ((self.tableQ_matrix_size[lengte_tijd])[str(nieuwe_toestand)])[nieuwe_knoop - 1])
        else:
            (self.tablecount_matrix_size[str(nieuwe_toestand)])[ nieuwe_knoop - 1] += 1
            (self.tableQ_matrix_size[str(nieuwe_toestand)])[nieuwe_knoop - 1] += self.learningrate * (reward - (self.tableQ_matrix_size[str(nieuwe_toestand)])[nieuwe_knoop - 1])


    def argminList(self, row):#returned de knopen met de laagste idices namens de 1 waarde
        best = np.min(row)
        best_indices = [i for i, x in enumerate(row) if x == best] # Get indices of lowest action value
        return best_indices


    def printEindLijst(self):
        print(self.tablecount_matrix_size)
        print(self.tableQ_matrix_size)


    def krijg_Q_waarde(self, toestand, actie):
        mijn_local_toestand = toestand[-1 * ( self.lengte_toestand):]
        if self.tijdsAfhankelijk:
            lengte_tijd = len(toestand) - 1
            return (self.tableQ_matrix_size[lengte_tijd])[str(mijn_local_toestand)][actie - 1]
        else: 
            return (self.tableQ_matrix_size[str(mijn_local_toestand)])[actie - 1]

    def krijg_N_waarde(self, toestand, actie):
        mijn_local_toestand = toestand[-1 * ( self.lengte_toestand):]
        if self.tijdsAfhankelijk:
            lengte_tijd = len(toestand) - 1
            return (self.tablecount_matrix_size[lengte_tijd])[str(mijn_local_toestand)][actie - 1]
        else:
            return (self.tablecount_matrix_size[str(mijn_local_toestand)])[actie - 1]

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
        mijn_matrix = []
        Elementen_van_lengte = [ [a] for a in range(1,self.steden + 1)]
        mijn_matrix.append(Elementen_van_lengte)



        for a in range(1, self.lengte_toestand):
            Elementen_van_lengte = mijn_matrix[-1]
            Elementen_toevoegen = []
            for b in Elementen_van_lengte:
                for c in range(1, self.steden + 1):
                    local = b.copy() + [c]
                    Elementen_toevoegen.append(local)
                
            mijn_matrix.append(Elementen_toevoegen)

        for a in range(len(mijn_matrix)):
            c = mijn_matrix[a]
            for d in c:
                self.tableQ_matrix_size[str(d)] = [0 for q in range(self.steden)]
                self.tablecount_matrix_size[str(d)] = [0 for q in range(self.steden)]
            

    def initQ_table_tijds(self):
        for tijd in range(self.steden): 
            mijn_matrix = []
            Elementen_van_lengte = [ [a] for a in range(1,self.steden + 1)]
            mijn_matrix.append(Elementen_van_lengte)
            mijn_matrix_2 = {}
            mijn_matrix_3 = {}

            for a in range(1, self.lengte_toestand):
                Elementen_van_lengte = mijn_matrix[-1]
                Elementen_toevoegen = []
                for b in Elementen_van_lengte:
                    for c in range(1, self.steden + 1):
                        local = b.copy() + [c]
                        Elementen_toevoegen.append(local)
                
                mijn_matrix.append(Elementen_toevoegen)

            for a in range(len(mijn_matrix)):
                c = mijn_matrix[a]
                for d in c:
                    mijn_matrix_2[str(d)] = [0 for q in range(self.steden)]
                    mijn_matrix_3[str(d)] = [0 for q in range(self.steden)]

            self.tableQ_matrix_size.append(mijn_matrix_2)
            self.tablecount_matrix_size.append(mijn_matrix_3)

        