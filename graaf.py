#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from json.encoder import INFINITY
from os import path
import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
import scipy.spatial.distance


class graafOmgeving(object):

    def __init__(self, n_dorpen, a, b, type):
        '''initlialiseer een graaf van n, met parameters a, b'''
        self.n_dorpen = n_dorpen
        self.gewichten_matrix = np.zeros((self.n_dorpen, self.n_dorpen))
        if type != "eucelidian":
            for c in range(0, (self.n_dorpen ), 1):
                for d in range(c + 1, (self.n_dorpen), 1):
                    value = 0
                    if type=="uniform":
                        value = np.random.uniform(low = a, high= b) # mean = (b - a)/2, var = (1/12)(b - a)^3
                    elif type=="lognormal":
                        value = np.random.lognormal(mean=a, sigma=b) #mean = e^(\mu + (sigma^2 / 2)), #var = (exp^(\sigma^2) - 1)*exp^(2mu)
                    elif type=="exponentiele":
                        value = np.random.exponential(scale = a) #a = 1/lambda, mean a en var a^2
                    elif type=="gamma":
                        value = np.random.gamma(shape= a, scale= b) #mean = a*b, var = a*b^2
                    else:
                        raise Exception("foute verdeling type 1")

                    self.gewichten_matrix[c, d] = int(value)
                    self.gewichten_matrix[d, c] = int(value)
        elif type == "eucelidian":
            #laat a de mean zijn. Bereken dan gemiddeld genomen de distributie die we nodig hebben.
            matrix_local = self.geefMatrixTerugMetGemiddelde_voor_euceledian(a)
            self.gewichten_matrix = matrix_local

        else:
            raise Exception("foute verdeling type 2")



        ##self.printMatrix()
        ##print("AAAA")
        ##print(self.gewichten_matrix.sum(axis=1))

    def geefMatrixTerugMetGemiddelde_voor_euceledian(self, gemiddelde):

        #
        max_local = gemiddelde * 5
        min_local = gemiddelde
         
        groote_uniform_verdeling = (max_local + min_local)/2
        for a in range(100):
            aantal_dorpen_local = self.n_dorpen
            if a >= 99:
                aantal_dorpen_local = self.n_dorpen

            gemiddelde_local = 0
            constante = 50
            for b in range(constante):
                xy = np.random.rand(aantal_dorpen_local,2)*groote_uniform_verdeling
                distance_matrix = scipy.spatial.distance.cdist(xy,xy)
                gemiddelde_local += (distance_matrix.sum() / (aantal_dorpen_local * aantal_dorpen_local  - aantal_dorpen_local))
            gemiddelde_local = gemiddelde_local / constante

            if gemiddelde_local > gemiddelde:
                max_local = groote_uniform_verdeling
            elif gemiddelde_local < gemiddelde:
                min_local = groote_uniform_verdeling
            groote_uniform_verdeling = (max_local + min_local)/2 


        xy = np.random.rand(self.n_dorpen,2)*groote_uniform_verdeling
        distance_matrix = scipy.spatial.distance.cdist(xy,xy)
        return distance_matrix
        #print(distance_matrix)
        

    
    def actie(self, to, path = []):
        ''' return de totale pad lengte ''' 
        totalreward = 0.0 #totale pad lengte
        for a in range(0, len(path) - 1):
            totalreward += self.gewichten_matrix[path[a] - 1, path[a + 1] - 1]#alle gewichten van takken bij elkaar optellen behalve de laatste
        totalreward += self.gewichten_matrix[path[-1] - 1, to - 1]#laatste tak toevoegen
        return totalreward

    def actie_reward(self, to, from_):
        ''' return een actie waarde'''
        return self.gewichten_matrix[from_ - 1 , to - 1]


    def printMatrix(self):
        print(self.gewichten_matrix)

    def eigenMatrix(self, new_matrix):
        self.gewichten_matrix = new_matrix

    def getShortestedPathNP_hard(self):
        takken, oplossing = solve_tsp_dynamic_programming(self.gewichten_matrix)
        return takken

    

    def isFinished(self, path):
        return len(path) >= (self.n_dorpen + 1)

        

    def optimalReward(self):
        if self.n_dorpen < 18:
            takken, oplossing = solve_tsp_dynamic_programming(self.gewichten_matrix)
            return oplossing
        else:
            return 0

    def optimalTakken(self):
        raise("ZOU HIER NIET IN MOETEN KOMEEN")
        takken, oplossing = solve_tsp_dynamic_programming(self.gewichten_matrix)

        return takken

    def optimalRewardDichtsbijzijndebuurtheurestiek(self):
        '''return de waarde van dichtsbijzijnde buur heurestiek'''
        stedenNogBezoeken = [i for i in range(2, self.n_dorpen + 1)]
        pad = [1] #totale pad, starten bij knoop 1.
        while len(stedenNogBezoeken) != 0:
            vanafknoop = pad[-1]
            nieuweknoop_local = 0
            minValue= INFINITY
            for nieuweknoop in stedenNogBezoeken:
               value = self.gewichten_matrix[vanafknoop - 1][nieuweknoop - 1]
               if minValue > value:
                   nieuweknoop_local = nieuweknoop
                   minValue = value
            stedenNogBezoeken.remove(nieuweknoop_local)
            pad += [nieuweknoop_local]
        return self.actie(1, pad)


    def rewardBijEenGemiddeldeRonde(self):
        total = self.gewichten_matrix.sum()
        return self.n_dorpen * (total / (self.n_dorpen * (self.n_dorpen - 1)))


    def eigenMatrix(self):
        return self.gewichten_matrix