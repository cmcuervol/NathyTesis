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


#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"Codigo para analizar la distribución porcentual de las coberturas de nubes en los puntos analizados"

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

################################################################################################################
## -------------------------LECTURA DE LOS DATOS DE COBERTURA DE NUBES FISH EYE-------------------------------##
################################################################################################################

df_cloud_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_TS.csv',  sep=',')
df_cloud_TS.columns = ['fecha_hora', 'Porcentaje']
df_cloud_TS.index = df_cloud_TS['fecha_hora']
df_cloud_TS = df_cloud_TS.drop(['fecha_hora'], axis =1)
df_cloud_TS.index = pd.to_datetime(df_cloud_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_TS = df_cloud_TS.between_time('06:00', '17:59')

df_cloud_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_CI.csv',  sep=',')
df_cloud_CI.columns = ['fecha_hora', 'Porcentaje']
df_cloud_CI.index = df_cloud_CI['fecha_hora']
df_cloud_CI = df_cloud_CI.drop(['fecha_hora'], axis =1)
df_cloud_CI.index = pd.to_datetime(df_cloud_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_CI = df_cloud_CI.between_time('06:00', '17:59')

df_cloud_AMVA = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_AMVA.csv',  sep=',')
df_cloud_AMVA.columns = ['fecha_hora', 'Porcentaje']
df_cloud_AMVA.index = df_cloud_AMVA['fecha_hora']
df_cloud_AMVA = df_cloud_AMVA.drop(['fecha_hora'], axis =1)
df_cloud_AMVA.index = pd.to_datetime(df_cloud_AMVA.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_AMVA = df_cloud_AMVA.between_time('06:00', '17:59')

df_cloud_AMVA_h =  df_cloud_AMVA.groupby(pd.Grouper(freq="H")).mean()
df_cloud_CI_h =  df_cloud_CI.groupby(pd.Grouper(freq="H")).mean()
df_cloud_TS_h =  df_cloud_TS.groupby(pd.Grouper(freq="H")).mean()

df_cloud_AMVA_h = df_cloud_AMVA_h.between_time('06:00', '17:59')
df_cloud_CI_h = df_cloud_CI_h.between_time('06:00', '17:59')
df_cloud_TS_h = df_cloud_TS_h.between_time('06:00', '17:59')

################################################################################################################
## -------------------------FUNCION DE DISTRIBUCIÓN DE PROBABILIDAD-------------------------------##
################################################################################################################


fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(df_cloud_AMVA_h['Porcentaje'].values[~np.isnan(df_cloud_AMVA_h['Porcentaje'].values)], bins='auto', alpha = 0.5)
ax1.set_title(u'Distribución del % de cobertura /n de nubes en el oriente', fontproperties=prop, fontsize = 13)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'% Cobertura nubes', fontproperties=prop_1)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(df_cloud_CI_h['Porcentaje'].values[~np.isnan(df_cloud_CI_h['Porcentaje'].values)], bins='auto', alpha = 0.5)
ax2.set_title(u'Distribución del % de cobertura /n de nubes en CI', fontproperties=prop, fontsize = 13)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'% Cobertura nubes', fontproperties=prop_1)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(df_cloud_TS_h['Porcentaje'].values[~np.isnan(df_cloud_TS_h['Porcentaje'].values)], bins='auto', alpha = 0.5)
ax3.set_title(u'Distribución del % de cobertura /n de nubes en TS', fontproperties=prop, fontsize = 13)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'% Cobertura nubes', fontproperties=prop_1)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistogramaFrecuenciasPorcNubFishEye.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/HistogramaFrecuenciasPorcNubFishEye.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
