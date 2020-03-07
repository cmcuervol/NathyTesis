#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA
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
from scipy.stats import pearsonr

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

'Codigo para graficar el contexto  las ciudades con mayor radiacion solar modelada'
'con respecto a la medida en Medellin.'
##############################################################################
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------
##############################################################################

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##########################################################################################################
##-----------------------------------LECTURA DE LOS DATOS  DE PIRANOMETRO-------------------------------##
##########################################################################################################

df_pira_TS = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60012018_2019.txt', parse_dates=[2])
df_pira_TS = df_pira_TS.set_index(["fecha_hora"])
df_pira_TS.index = df_pira_TS.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_TS.index = df_pira_TS.index.tz_localize(None)
df_pira_TS = df_pira_TS[df_pira_TS['radiacion'] >=0]

df_pira_CI = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60022018_2019.txt', parse_dates=[2])
df_pira_CI = df_pira_CI.set_index(["fecha_hora"])
df_pira_CI.index = df_pira_CI.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_CI.index = df_pira_CI.index.tz_localize(None)
df_pira_CI = df_pira_CI[df_pira_CI['radiacion'] >=0]

df_pira_JV = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60032018_2019.txt', parse_dates=[2])
df_pira_JV = df_pira_JV.set_index(["fecha_hora"])
df_pira_JV.index = df_pira_JV.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_JV.index = df_pira_JV.index.tz_localize(None)
df_pira_JV = df_pira_JV[df_pira_JV['radiacion'] >=0]

df_pira_JV = df_pira_JV.between_time('06:00', '17:59')
df_pira_CI = df_pira_CI.between_time('06:00', '17:59')
df_pira_TS = df_pira_TS.between_time('06:00', '17:59')

df_pira_JV = df_pira_JV.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)
df_pira_CI = df_pira_CI.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)
df_pira_TS = df_pira_TS.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)

## ------------------------------------DATOS DE IRRADIACION Wh/m2----------------------------- ##

df_pira_JV_Wh =  df_pira_JV / 60
df_pira_CI_Wh =  df_pira_CI / 60
df_pira_TS_Wh =  df_pira_TS / 60

## ------------------------------------DATOS DE IRRADIACION kWh/m2----------------------------- ##

df_pira_JV_kWh =  df_pira_JV_Wh / 1000
df_pira_CI_kWh =  df_pira_CI_Wh / 1000
df_pira_TS_kWh =  df_pira_TS_Wh / 1000

## ------------------------------------DATOS HORARIOS DE IRRADIACION kWh/m2 CADA DIA----------------------------- ##

df_pira_JV_kWh_dia =  df_pira_JV_kWh.groupby(pd.Grouper(freq="D")).sum()
df_pira_CI_kWh_dia =  df_pira_CI_kWh.groupby(pd.Grouper(freq="D")).sum()
df_pira_TS_kWh_dia =  df_pira_TS_kWh.groupby(pd.Grouper(freq="D")).sum()

## ------------------------------------DATOS DE IRRADIACION kWh/m2 CADA DIA DE CADA AÑO----------------------------- ##

df_pira_TS_data  = df_pira_TS_kWh_dia.mean().values[0]
df_pira_JV_data  = df_pira_JV_kWh_dia.mean().values[0]
df_pira_CI_data  = df_pira_CI_kWh_dia.mean().values[0]

max_data = max(df_pira_TS_data, df_pira_JV_data, df_pira_CI_data)

##########################################################################################################
##-----------------------------------LECTURA DE LOS DATOS  DE GHI MODELADA------------------------------##
##########################################################################################################

data_cities = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ciudades/Irradiancias_modeladas_Ciudades.csv',  sep=',', index_col =0)
new_arange = np.zeros(len(data_cities.index))
new_arange = new_arange.astype(object)
new_arange[0] = round(float(max_data), 3)
############################################################################
##-----------------------------------GRAFICO------------------------------##
############################################################################


x_pos = np.arange(len(data_cities.index))
x_pos1 = np.arange(0.75, len(data_cities.index) + 0.75, 1)

fig = plt.figure(figsize=[12, 10])
ax=fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.bar(np.arange(len(data_cities.index.values))+0.75, np.array(data_cities['DAILY GHI [kWh/m2 por dia]'].values), color='#004D56', label='Modelada')
plt.bar(np.arange(len(data_cities.index.values))+0.75, np.array(new_arange), color= '#8ABB73', label='Medida')
plt.axhline(y = new_arange[0], color = '#8ABB73', linewidth = 3 ,linestyle = '-',label = u'Medida en  Medellín')
plt.xticks(x_pos1, (data_cities.index.values),  fontproperties=prop, rotation=28,fontsize=11 )
plt.xlabel(u'Ciudades',  fontproperties=prop_1, fontsize = 15)
plt.ylabel(u'$[kWh/m^{2}]$ dia', fontproperties=prop_1, fontsize = 20)
plt.title(u'Irradiancia diaria promedio \n en diferentes ciudades',   fontweight = "bold",  fontproperties = prop, fontsize = 25)
plt.legend(fontsize = 12)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Shining_cities.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Shining_cities.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
