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
import netCDF4 as nc
from netCDF4 import Dataset
id
import itertools
import datetime
from scipy.stats import ks_2samp
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import matplotlib.cm as cm
import os
import statistics

Path_datos = "/home/nacorreasa/Maestria/Datos_Tesis/Radar/Mensual/"
Path_Save = '/home/nacorreasa/Escritorio/Figuras/'

#-----------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

"Codigo para la verificacion de los promedios del 2018 del CH2 de GOES a  partir."
"de los promedios del radar. LOs archivos se pasan de .bin a un array."

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

################################################################################
## ----------------DEFINICION DE LA FUNCION QUE LEE LOS DATOS---------------- ##
################################################################################

# def read_bin(path_in):
#     file = open(path_in, 'rb')
#     f = file.read()
#     data_gross = np.fromstring(f, dtype = np.uint8)
#     file.close()
#     len(data_gross)
#     data0 = np.reshape(data_gross, (3912, 2301))
#     data = (data0 * 0.5) - 32.0
#     data[data == 95.5] = np.nan
#     return data

def read_binaryradar(path_complete):
        f = open(path_complete, "r")
        a = np.fromfile(f, dtype = 'float32')
        f.close()
        m = np.reshape(a,(1467,1534))
        #m = np.reshape(a,(1727,1728))
        return m

Folders = []
for filename in os.listdir(Path_datos):
    Folders.append(filename)
Mes = []
for i in range(len(Folders)):
    file_ = Path_datos+Folders[i]
    print (file_)
    dato = read_binaryradar(file_)
    Mes.append(dato)

Mes = np.array(Mes)

################################################################################
##----------------------------------ENSAYOS-----------------------------------##
################################################################################

a = Mes[0, :, :]
am = np.ma.masked_where(a > 1200, a)
fig = plt.figure(figsize=(14,18))
cs = plt.imshow(am)
plt.title('Promedio Enero Radar')
cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
plt.savefig(Path_Save+'EneroRadar.png', format='png')
plt.close('all')
os.system('scp '+ Path_Save+'EneroRadar.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
