#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.cm as cm
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.transforms as transforms
import matplotlib.colors as colors
import netCDF4 as nc
from netCDF4 import Dataset
import os
import rasterio
from scipy.interpolate import griddata

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa para el computo del efecto de las nubes a partir del forzamiento de nubes no lineal
sobre la radiacion solar en superficie, obtener los promedios mensuales y horarios y restarlo
del array de irradiancias en condiciones de cielo despejado, cosiderando las pendientes horarias
y estacionales.
"""
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

####################################################################################
## -----------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL ENMASCARADA--------- ##
####################################################################################

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_Malla_MaskedClean.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Malla_MaskedClean.npy')
fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')
la = Rad .shape[1]
lo = Rad .shape[2]

####################################################################################
## ---------------DEFICINICIÓN DE ESTADOS CON LA FDP DE LOS ESTADOS-------------- ##
####################################################################################
Rad_r = Rad.ravel()
Histograma = plt.hist(Rad_r , bins=5, density = False)[0]
Bins = plt.hist(Rad_r , bins=5, density = False)[1]


fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(111)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Rad_r , bins=5, density = False)
ax1.set_xlabel(u'Valor Reflectancia', fontproperties = prop_1, fontsize=10)
ax1.set_ylabel(r"Frecuencia", fontproperties = prop_1, fontsize=10)
ax1.set_title(u'Histograma de frecuencias de radiancias', loc = 'center', fontsize=13)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistogramaDefinicionEstados.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/HistogramaDefinicionEstados.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

Estado_1 = Rad[(Rad>= Bins[0]) &  (Rad<Bins[1])]
Estado_2 = Rad[(Rad>= Bins[1]) &  (Rad<Bins[2])]
Estado_3 = Rad[(Rad>= Bins[2]) &  (Rad<Bins[3])]
Estado_4 = Rad[(Rad>= Bins[3]) &  (Rad<Bins[4])]
Estado_5 = Rad[(Rad>= Bins[4]) &  (Rad<Bins[5])]


####################################################################################
## -----------------GENERANDO LA CADENA DE MARKOV PARA CADA CASO----------------- ##
####################################################################################
horas_maniana = [6, 7, 8, 9, 10]
horas_noon = [11, 12, 13, 14]
horas_tarde = [11, 12, 13, 14]

##--------------------------------DEF EN LA MAÑANA------------------------------------##
meses_DEF_m = [12, 1, 2]

Rad_DEF_m = []
fechas_horas_DEF_m = []
for g in range(len(fechas_horas)):
    if fechas_horas[g].month in meses_DEF_m and fechas_horas[g].hour in horas_maniana :
        Rad_DEF_m.append(Rad[g, :, :])
        fechas_horas_DEF_m.append(fechas_horas_DEF_m)

# for j in range(0,lo,1):
#     for k in range(0,la,1):
k = 70
j = 45
Serie_Pixel = Rad[:,k, j]

Count_Estado_1_1 = []
Count_Estado_1_2 = []
Count_Estado_1_3 = []
Count_Estado_1_4 = []
Count_Estado_1_5 = []

Count_Estado_2_1 = []
Count_Estado_2_2 = []
Count_Estado_2_3 = []
Count_Estado_2_4 = []
Count_Estado_2_5 = []

Count_Estado_3_1 = []
Count_Estado_3_2 = []
Count_Estado_3_3 = []
Count_Estado_3_4 = []
Count_Estado_3_5 = []

Count_Estado_4_1 = []
Count_Estado_4_2 = []
Count_Estado_4_3 = []
Count_Estado_4_4 = []
Count_Estado_4_5 = []

Count_Estado_5_1 = []
Count_Estado_5_2 = []
Count_Estado_5_3 = []
Count_Estado_5_4 = []
Count_Estado_5_5 = []

for j in range(1, len(Serie_Pixel)):
    if Serie_Pixel[j-1] in Estado_1 and Serie_Pixel[j] in Estado_1 :
        Count_Estado_1_1.append(1)
    elif Serie_Pixel[j-1] in Estado_1 and Serie_Pixel[j] in Estado_2 :
        Count_Estado_1_2.append(1)
    elif Serie_Pixel[j-1] in Estado_1 and Serie_Pixel[j] in Estado_3 :
        Count_Estado_1_3.append(1)
    elif Serie_Pixel[j-1] in Estado_1 and Serie_Pixel[j] in Estado_4 :
        Count_Estado_1_4.append(1)
    elif Serie_Pixel[j-1] in Estado_1 and Serie_Pixel[j] in Estado_5 :
        Count_Estado_1_5.append(1)

    elif Serie_Pixel[j-1] in Estado_2 and Serie_Pixel[j] in Estado_1 :
        Count_Estado_2_1.append(1)
    elif Serie_Pixel[j-1] in Estado_2 and Serie_Pixel[j] in Estado_2 :
        Count_Estado_2_2.append(1)
    elif Serie_Pixel[j-1] in Estado_2 and Serie_Pixel[j] in Estado_3 :
        Count_Estado_2_3.append(1)
    elif Serie_Pixel[j-1] in Estado_2 and Serie_Pixel[j] in Estado_4 :
        Count_Estado_2_4.append(1)
    elif Serie_Pixel[j-1] in Estado_2 and Serie_Pixel[j] in Estado_5 :
        Count_Estado_2_5.append(1)

    elif Serie_Pixel[j-1] in Estado_3 and Serie_Pixel[j] in Estado_1 :
        Count_Estado_3_1.append(1)
    elif Serie_Pixel[j-1] in Estado_3 and Serie_Pixel[j] in Estado_2 :
        Count_Estado_3_2.append(1)
    elif Serie_Pixel[j-1] in Estado_3 and Serie_Pixel[j] in Estado_3 :
        Count_Estado_3_3.append(1)
    elif Serie_Pixel[j-1] in Estado_3 and Serie_Pixel[j] in Estado_4 :
        Count_Estado_3_4.append(1)
    elif Serie_Pixel[j-1] in Estado_3 and Serie_Pixel[j] in Estado_5 :
        Count_Estado_3_5.append(1)

    elif Serie_Pixel[j-1] in Estado_4 and Serie_Pixel[j] in Estado_1 :
        Count_Estado_4_1.append(1)
    elif Serie_Pixel[j-1] in Estado_4 and Serie_Pixel[j] in Estado_2 :
        Count_Estado_4_2.append(1)
    elif Serie_Pixel[j-1] in Estado_4 and Serie_Pixel[j] in Estado_3 :
        Count_Estado_4_3.append(1)
    elif Serie_Pixel[j-1] in Estado_4 and Serie_Pixel[j] in Estado_4 :
        Count_Estado_4_4.append(1)
    elif Serie_Pixel[j-1] in Estado_4 and Serie_Pixel[j] in Estado_5 :
        Count_Estado_4_5.append(1)

    elif Serie_Pixel[j-1] in Estado_5 and Serie_Pixel[j] in Estado_1 :
        Count_Estado_5_1.append(1)
    elif Serie_Pixel[j-1] in Estado_5 and Serie_Pixel[j] in Estado_2 :
        Count_Estado_5_2.append(1)
    elif Serie_Pixel[j-1] in Estado_5 and Serie_Pixel[j] in Estado_3 :
        Count_Estado_5_3.append(1)
    elif Serie_Pixel[j-1] in Estado_5 and Serie_Pixel[j] in Estado_4 :
        Count_Estado_5_4.append(1)
    elif Serie_Pixel[j-1] in Estado_5 and Serie_Pixel[j] in Estado_5 :
        Count_Estado_5_5.append(1)

    print(j-len(Serie_Pixel))


Prob_Estado_1_1 = (len(Count_Estado_1_1)/len(Serie_Pixel)) * 100
Prob_Estado_1_2 = (len(Count_Estado_1_2)/len(Serie_Pixel)) * 100
Prob_Estado_1_3 = (len(Count_Estado_1_3)/len(Serie_Pixel)) * 100
Prob_Estado_1_4 = (len(Count_Estado_1_4)/len(Serie_Pixel)) * 100
Prob_Estado_1_5 = (len(Count_Estado_1_5)/len(Serie_Pixel)) * 100

Prob_Estado_2_1 = (len(Count_Estado_2_1)/len(Serie_Pixel)) * 100
Prob_Estado_2_2 = (len(Count_Estado_2_2)/len(Serie_Pixel)) * 100
Prob_Estado_2_3 = (len(Count_Estado_2_3)/len(Serie_Pixel)) * 100
Prob_Estado_2_4 = (len(Count_Estado_2_4)/len(Serie_Pixel)) * 100
Prob_Estado_2_5 = (len(Count_Estado_2_5)/len(Serie_Pixel)) * 100

Prob_Estado_3_1 = (len(Count_Estado_3_1)/len(Serie_Pixel)) * 100
Prob_Estado_3_2 = (len(Count_Estado_3_2)/len(Serie_Pixel)) * 100
Prob_Estado_3_3 = (len(Count_Estado_3_3)/len(Serie_Pixel)) * 100
Prob_Estado_3_4 = (len(Count_Estado_3_4)/len(Serie_Pixel)) * 100
Prob_Estado_3_5 = (len(Count_Estado_3_5)/len(Serie_Pixel)) * 100

Prob_Estado_4_1 = (len(Count_Estado_4_1)/len(Serie_Pixel)) * 100
Prob_Estado_4_2 = (len(Count_Estado_4_2)/len(Serie_Pixel)) * 100
Prob_Estado_4_3 = (len(Count_Estado_4_3)/len(Serie_Pixel)) * 100
Prob_Estado_4_4 = (len(Count_Estado_4_4)/len(Serie_Pixel)) * 100
Prob_Estado_4_5 = (len(Count_Estado_4_5)/len(Serie_Pixel)) * 100

Prob_Estado_5_1 = (len(Count_Estado_5_1)/len(Serie_Pixel)) * 100
Prob_Estado_5_2 = (len(Count_Estado_5_2)/len(Serie_Pixel)) * 100
Prob_Estado_5_3 = (len(Count_Estado_5_3)/len(Serie_Pixel)) * 100
Prob_Estado_5_4 = (len(Count_Estado_5_4)/len(Serie_Pixel)) * 100
Prob_Estado_5_5 = (len(Count_Estado_5_5)/len(Serie_Pixel)) * 100
