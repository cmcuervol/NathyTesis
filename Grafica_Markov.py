#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
id
import itertools
import datetime
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import matplotlib.cm as cm
import os
import statistics

Horizonte = 'Anual' ##--->'Trimestral' paragenerar solo un plot o 'Anual' para generar los 3
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
#-----------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

"""
Codigo para la grafica de las cadenas de Markov, a partir de la lectura de los datos
q están alojados como unos array.Se guardarán como subplot o como un solo plot. Si es
por trimestre se debe lenar el str del trimestre mas abajo para completar el titulo.
"""
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop   = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

#################################################################################################
##-------------------------------DEFINICION DE LOS ESTADOS-------------------------------------##
#################################################################################################
Estados_Str =['1 a 1', '1 a 2', '1 a 3', '1 a 4', '1 a 5', '2 a 1', '2 a 2', '2 a 3', '2 a 4', '2 a 5', '3 a 1', '3 a 2', '3 a 3', '3 a 4', '3 a 5',
'4 a 1', '4 a 2', '4 a 3', '4 a 4', '4 a 5', '5 a 1', '5 a 2', '5 a 3', '5 a 4', '5 a 5' ]
Estados_Str = np.array(Estados_Str)
#################################################################################################
##-----------------LECTURA DE LOS DATOS BASADOS EN LA CONDICION INICIAL------------------------##
#################################################################################################
if Horizonte == 'Trimestral':
    Trimestre  = 'M-A-M'

    Trimestre_morning = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_MAM_morning.npy')
    Trimestre_noon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_MAM_noon.npy')
    Trimestre_tarde = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_MAM_tarde.npy')

    Total_Max = max(np.max(Trimestre_morning),np.max(Trimestre_noon), np.max(Trimestre_tarde))

    plt.close('all')
    fig = plt.figure(figsize=(13,9))
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.plot(Estados_Str,  Trimestre_morning, color = '#8ABB73', lw=1.5, label = 'Maniana')
    ax1.scatter(Estados_Str,  Trimestre_morning, marker='.', color = '#8ABB73', s=30)
    ax1.plot(Estados_Str,  Trimestre_noon, color = '#70AFBA', lw=1.5, label = 'Medio dia')
    ax1.scatter(Estados_Str,  Trimestre_noon, marker='.', color = '#70AFBA', s=30)
    ax1.plot(Estados_Str,  Trimestre_tarde, color = '#004D56', lw=1.5, label = 'Tarde')
    ax1.scatter(Estados_Str,  Trimestre_tarde, marker='.', color = '#004D56', s=30)
    ax1.set_xlabel('Regla Transicion', fontproperties = prop_1, fontsize=17)
    ax1.set_ylabel(u"Probabilidad [%]", fontproperties = prop_1, fontsize=20)
    ax1.set_xticks(np.arange(0, len(Estados_Str)), minor=False)
    ax1.set_xticklabels(Estados_Str, minor=False, rotation = 23, fontsize=12)
    ax1.set_ylim(0, Total_Max + 0.01)
    ax1.set_title(u'Cadena de Markov para el trimestre'+ Trimestre, loc = 'center', fontproperties = prop, fontsize=25)
    plt.legend()
    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
    plt.savefig('/home/nacorreasa/Escritorio/Figuras/MarkovChain_Trimestrial'+Trimestre+'.pdf', format='pdf', transparent=True)
    os.system('scp /home/nacorreasa/Escritorio/Figuras/MarkovChain_Trimestrial'+Trimestre+'.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

elif Horizonte == 'Anual':

    MAM_morning = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_MAM_morning.npy')
    MAM_noon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_MAM_noon.npy')
    MAM_tarde = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_MAM_tarde.npy')

    DEF_morning = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_DEF_morning.npy')
    DEF_noon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_DEF_noon.npy')
    DEF_tarde = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_DEF_tarde.npy')

    JJA_morning = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_JJA_morning.npy')
    JJA_noon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_JJA_noon.npy')
    JJA_tarde = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_JJA_tarde.npy')

    SON_morning = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_SON_morning.npy')
    SON_noon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_SON_noon.npy')
    SON_tarde = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Markov_SON_tarde.npy')

    MAM_resha_morning = np.reshape(MAM_morning, (-1, 5))
    MAM_resha_noon = np.reshape(MAM_noon, (-1, 5))
    MAM_resha_tarde = np.reshape(MAM_tarde, (-1, 5))

    DEF_resha_morning = np.reshape(DEF_morning, (-1, 5))
    DEF_resha_noon = np.reshape(DEF_noon, (-1, 5))
    DEF_resha_tarde = np.reshape(DEF_tarde, (-1, 5))

    SON_resha_morning = np.reshape(SON_morning, (-1, 5))
    SON_resha_noon = np.reshape(SON_noon, (-1, 5))
    SON_resha_tarde = np.reshape(SON_tarde, (-1, 5))

    JJA_resha_morning = np.reshape(JJA_morning, (-1, 5))
    JJA_resha_noon = np.reshape(JJA_noon, (-1, 5))
    JJA_resha_tarde = np.reshape(JJA_tarde, (-1, 5))

    data = [DEF_resha_morning, MAM_resha_morning, JJA_resha_morning, SON_resha_morning, DEF_resha_noon, MAM_resha_noon, JJA_resha_noon, SON_resha_noon,  DEF_resha_tarde, MAM_resha_tarde, JJA_resha_tarde, SON_resha_tarde]
    data = np.array(data)
    titles =[ u'DEF Mañana', u'MAM Mañana', u'JJA Mañana',u'SON Mañana', 'DEF Medio dia', 'MAM Medio dia', 'JJA Medio dia','SON Medio dia', 'DEF Tarde', 'MAM Tarde', 'JJA Tarde','SON Tarde']
    plt.close('all')
    fig = plt.figure(figsize=(17,13))

    for i in range(0, 12):
        ax = fig.add_subplot(3, 4, i+1)
        cs = ax.imshow(data[i], cmap ='YlGnBu')
        ax.set_ylabel('Estado Inicial', fontproperties = prop_1, fontsize =14)
        ax.set_xlabel('Estado Final', fontproperties = prop_1, fontsize =14)
        ax.set_title(titles[i], fontproperties = prop, fontsize =15)
        data[i][data[i]<10]=np.nan
        for k in range(0,5):
            for j in range(0,5):
                text = ax.text(j, k, round(data[i][k, j], 2),  ha="center", va="center", color="w")
        ax.set_xticklabels(np.array(['0','1', '2', '3', '4', '5']))
        ax.set_yticklabels(np.array(['0', '1', '2', '3', '4', '5']))

    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.01)

    cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
    cbar.set_label(u'Probabilidad [%]',  fontproperties = prop, fontsize=20 )

    plt.savefig('/home/nacorreasa/Escritorio/Figuras/MarkovChain_Anual.pdf', format='pdf', transparent=True)
    os.system('scp /home/nacorreasa/Escritorio/Figuras/MarkovChain_Anual.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

################################################################################
##--------------------DIFERENCIA ENTRE LAS MATRICES---------------------------##
################################################################################
