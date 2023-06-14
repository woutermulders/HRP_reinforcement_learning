from json.encoder import INFINITY
from operator import index
from os import remove, stat
from threading import local
import numpy as np
import random

randomDoorHeenLopen = True



class MDP(object):


    def __init__(self, matrix, n_knopen):
        self.matrix = matrix
        self.n_knopen = n_knopen
        
        self.issolved = False
        self.toestandsruimte = []##de toestandsruimte om te defineren
        self.makeSpace()


    def getWeight(self, width, height):
        return self.matrix[width][height]


    ##hier word de space ruimte gemaakt
    def makeSpace(self):
        dictionary_local2 = {} ##state space om gegevens op te slaan

        #for a in range(1, self.n_knopen + 1):
            #dictionary_local2[","  + str(a) + ","] = [0 for i in range(self.n_knopen)]
        dictionary_local2[","  + str(1) + ","] = [0] * self.n_knopen #elementen van lengte 1
       
            
        self.toestandsruimte.append(dictionary_local2) ## alle elementen van lengte 1 toevoegen
        indexToestandsRuimte = 0
        
        while indexToestandsRuimte < (self.n_knopen - 1):##toestandsruimte recursief opbouwen
            indexToestandsRuimte += 1#toestandsruimte opbouwen
            local_dict = self.toestandsruimte[-1]#de laatst toegevoede states 1 eentje langer maken
            dictionary_local2 = {}
            
            
            doorVoorTheLopen = [key for key in local_dict.keys()]
            if (indexToestandsRuimte > 1):##alleen lengte 2 of groter
                #doorVoorTheLopen += [key[::-1] for key in local_dict.keys()]##symmetrie toevoegen
                pass
            for key in doorVoorTheLopen:##we doorlopen alle keys
                characters = ["," + str(a) + "," for a in range(1, self.n_knopen + 1)]##scheiding gomma's
                charactersToAdd = ''.join(characters) ## aan elkaar plkakken

                ##koma's verwijderen, en in een int list zetten
                keys = key.replace(",", " ")
                keys = list(map(int, keys.split()))

                for local_key in keys:##acties verwijderen waar we niet meer naar toe kunnen
                    charactersToAdd = charactersToAdd.replace(',' + str(local_key) + ",", '')

                ##hiervan weer int list maken
                charactersToAdd = charactersToAdd.replace(",", " ")
                charactersToAdd = list(map(int, charactersToAdd.split()))
                
                ##hiervan weer int list maken, van de oorspronkelijke key
                tussenkey = key.replace(",", " ")
                tussenkey = list(map(int, tussenkey.split()))

                for local in charactersToAdd:##doorloop alle acties waar we naar toe kunnen gaan
                    if local > tussenkey[0]:##alleen toevoegen, zodat er geen dubbele actie skomen vanwege symmetrie
                            dictionary_local2[key + "," + str(local) + ","] = [0 for i in range(self.n_knopen)]



            self.toestandsruimte.append(dictionary_local2)##toeveoegn aan toestands ruimte


        self.randomSpace = {}##indien we het random willen oplossen
        for local in self.toestandsruimte:
            for local2, value in local.items():
                self.randomSpace[local2] = value



    ##om het random op te lossen
    def solvingRandom(self):
        fouterror = INFINITY##wanneer te stoppen
        
        aantal = 0##stop critmumum voor testen
        while fouterror > 0 and aantal < 25:##convergeert tot 0 of stop critmumum
            aantal += 1
            fouterror = 0##fouterror van dit moment
            kopieList = self.randomSpace.copy()##kopie maken voor lijst om random door heen te lopen.
            
            while len(kopieList.keys()) > 0:##door gaan zolang lijst niet leeg is.
                state = random.choice(list(kopieList.keys()))##pak een random toestand
                kopieList.pop(state) #haal toestand weg

                ##alle al bezochten states in een int list
                state_int = state.replace(",", " ")
                state_int = list(map(int, state_int.split()))

                ## alle mogelijke acties waar we naar toe kunnen gaan van huidige state
                characters = [","  + str(a) + "," for a in range(1, self.n_knopen + 1)]
                charactersToAdd = ''.join(characters)
                for local_key in state_int:
                    charactersToAdd = charactersToAdd.replace("," + str(local_key) + ",", '')
                charactersToAdd = charactersToAdd.replace(",", " ")
                charactersToAdd = list(map(int, charactersToAdd.split()))

                localreward = 0#reward van actie nu
                oude_waarde = 0##oude waarde van state actie
                    
                if len(charactersToAdd) == 0: ## 
                    ##final state bereikt, hij kan maar na 1 en dat is zichzelf
                    localreward = self.getWeight(int(state_int[-1]) - 1, int(state_int[0]) - 1)
                    actie = int(state_int[0])##kan alleen naar knoop 1 terug
                    oude_waarde = (self.toestandsruimte[len(state_int) - 1][str(state)])[actie - 1]
                    (self.toestandsruimte[len(state_int) - 1][str(state)])[actie - 1] = localreward
                    fouterror = max(fouterror, abs(oude_waarde - localreward))##nieuwe fouterror berekenen
                        
                else:
                    for actie_2 in charactersToAdd:##alle mogelijke acties doorlopen

                        #acties_3 alle acties mogelijk na actie_2
                        acties_3 = charactersToAdd.copy()##
                        acties_3.remove(actie_2)
                            
                        if len(charactersToAdd) == 1:##indien acties_3 leeg dan ronde bijna gesloten nog 1 tak toeveoegen.
                            acties_3 = [int(state_int[0])]
                        localreward = self.getWeight(state_int[-1] - 1, int(actie_2) - 1)
                        nieuweQA_PI = INFINITY
                            
                        for actie_local in acties_3:#doorloop alle acties na actie_2
                            nieuweState = ""
                            if int(state_int[0]) > int(actie_2):##state in juiste volgorde zetten
                                local_variable = state_int[::-1]
                                local_variable2 = ["," + str(a) + "," for a in local_variable]
                                nieuweState = "," + str(actie_2) + "," + "".join(local_variable2)
                            else:#state stond al goede volgorde
                                nieuweState = state + "," + str(actie_2) + ","
                            waarde_QA = (self.toestandsruimte[len(state_int)][str(nieuweState)])[actie_local - 1]
                            nieuweQA_PI = min(nieuweQA_PI, waarde_QA)

                        ##updateen waarden
                        oude_waarde = (self.toestandsruimte[len(state_int) - 1][str(state)])[actie_2 - 1]
                        (self.toestandsruimte[len(state_int) - 1][str(state)])[actie_2 - 1] = localreward + nieuweQA_PI
                        fouterror = max(fouterror, abs(oude_waarde - (localreward + nieuweQA_PI )))
                #end for
            ##end for 
            print("fouterror", fouterror,  "")
        ##endwhile
        self.issolved = True


    ##om het recursief op te lossen
    def solvingSimple(self):
        fouterror = INFINITY
        aantal = 0##debug constante
        while fouterror > 0 and aantal < 25:## aantal debug is een debug constante zet die hoger om geen infinty loops te krijgen
            aantal += 1
            fouterror = 0
            for states in self.toestandsruimte:##doorloop alle states
                for state, value in states.items():
                    ##maak van alle states een int list
                    state_int = state.replace(",", " ")
                    state_int = list(map(int, state_int.split()))

                    ##lijst van alle acties die nog mogelijk zijn  in een int list
                    characters = [","  + str(a) + "," for a in range(1, self.n_knopen + 1)]
                    charactersToAdd = ''.join(characters)
                    for local_key in state_int:
                        charactersToAdd = charactersToAdd.replace("," + str(local_key) + ",", '')
                    charactersToAdd = charactersToAdd.replace(",", " ")
                    charactersToAdd = list(map(int, charactersToAdd.split()))

                    localreward = 0##reward van de actie
                    oude_waarde = 0##de oude waarde van q(s, a)
                    
                    if len(charactersToAdd) == 0: ## 
                        ##final state bereikt, hij kan maar na 1 en dat is zichzelf
                        localreward = self.getWeight(int(state_int[-1]) - 1, int(state_int[0]) - 1)
                        actie = int(state_int[0])##kan alleen nog naar de eerste knoop terug
                        oude_waarde = (self.toestandsruimte[len(state_int) - 1][str(state)])[actie - 1]
                        (self.toestandsruimte[len(state_int) - 1][str(state)])[actie - 1] = localreward
                        fouterror = max(fouterror, abs(oude_waarde - localreward))    
                    else:
                        for actie_2 in charactersToAdd:##doorloop alle acties mogelijk zijn
                            ##acties_3 zijn de acties die na actie actie_2 nodig zijn.
                            acties_3 = charactersToAdd.copy()
                            acties_3.remove(actie_2)

                            if len(charactersToAdd) == 1:#indien nog 1 actie mogelijk dan actie daarna is de eerste knoop
                                acties_3 = [int(state_int[0])]
                            localreward = self.getWeight(state_int[-1] - 1, int(actie_2) - 1)
                            nieuweQA_PI = INFINITY
                
                            for actie_local in acties_3:##doorloop alle acties na actie 2
                                nieuweState = state + "," + str(actie_2) + ","
                                waarde_QA = (self.toestandsruimte[len(state_int)][str(nieuweState)])[actie_local - 1]
                                nieuweQA_PI = min(nieuweQA_PI, waarde_QA)
                            #waardes updaten
                            oude_waarde = (self.toestandsruimte[len(state_int) - 1][str(state)])[actie_2 - 1]
                            (self.toestandsruimte[len(state_int) - 1][str(state)])[actie_2 - 1] = localreward + nieuweQA_PI
                            fouterror = max(fouterror, abs(oude_waarde - (localreward + nieuweQA_PI )))
                #end for
            ##end for 
            print("fouterror", fouterror,  "")
        ##endwhile
        self.issolved = True

    

    def printAnswers(self):
        count = 0
        for d in self.toestandsruimte:
            count += len(d)
            #pass

        #count = len(self.toestandsruimte[-1])
        if self.issolved:
            toPrint = ",1,"
            valueToPrint = 0
            takeAction = -1
            min = self.mijnArgminGroterDan0(self.toestandsruimte[0][toPrint])
            takeAction = min + 1
            valueToPrint = self.toestandsruimte[0][toPrint][min]
            for states in self.toestandsruimte:
                if toPrint == ",1,":
                    pass
                else:
                    state_int_ = toPrint.replace(",", " ")
                    state_int_ = list(map(int, state_int_.split()))
                    if state_int_[1] > state_int_[-1] and len(state_int_) == self.n_knopen:
                        state_int_[1], state_int_[-1] = state_int_[-1], state_int_[1] 
                    local_ = ["," + str(a) + "," for a in state_int_]
                    local_2 = "".join(local_)
                    min = self.mijnArgminGroterDan0(states[local_2])
                    takeAction = min + 1
                toPrint = toPrint + "," + str(takeAction) + ","
            
            print("oplossing: ", toPrint, "   waarde:" ,  valueToPrint)
            print("statespace: ", count)
            
        else:
            print("oplossing nog niet gemaakt")
            print("statespace: ", count)
            #print("statespace: ", self.toestandsruimte)
        
     
        

    def mijnArgminGroterDan0(self, list):
        counter = -1
        counterToReturn = -1
        minElementWaarde = INFINITY
        for element in list:
            counter += 1
            waarde = list[counter]
            if waarde < minElementWaarde and waarde > 0:
                minElementWaarde = waarde
                counterToReturn = counter
        return counterToReturn




  








if __name__ == '__main__':
    matrix = np.array([[0, 35, 43, 23, 33, 19],
                        [35, 0, 47, 42, 21, 26],
                        [43, 47, 0, 36, 31, 30], 
                        [23, 42, 36, 0, 50, 17],
                        [33, 21, 31, 50, 0, 45],
                        [19, 26, 30, 17, 45, 0]])

    test = MDP(matrix, 6)
    randomDoorHeenLopen = False
    if randomDoorHeenLopen:
        test.solvingRandom()
    else:
        test.solvingSimple()
    test.printAnswers()











    
