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
"Codigo para encntrar los porcentajes a partir de los cuales se consida un dato de nubosidad"
"tomando enc uenta los cambios en los datos de piranómetros, así encontrar un umbral promedio"
"apartir del cual se considere un porcentaje nublado en los datos de las Fisheye. Los datos"
"se trabajaran a resolucion minutal."

################################################################################################################
## -------------------------LECTURA DE LOS DATOS DE COBERTURA DE NUBES FISH EYE-------------------------------##
################################################################################################################

df_cloud_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_TS.csv',  sep=',')
df_cloud_TS.columns = ['fecha_hora', 'Porcentaje']
df_cloud_TS.index = df_cloud_TS['fecha_hora']
df_cloud_TS = df_cloud_TS.drop(['fecha_hora'], axis =1)
df_cloud_TS.index = pd.to_datetime(df_cloud_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_TS.index = [df_cloud_TS.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_TS.index))]
df_cloud_TS.index = pd.to_datetime(df_cloud_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_TS = df_cloud_TS.between_time('06:00', '17:59')

df_cloud_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_CI.csv',  sep=',')
df_cloud_CI.columns = ['fecha_hora', 'Porcentaje']
df_cloud_CI.index = df_cloud_CI['fecha_hora']
df_cloud_CI = df_cloud_CI.drop(['fecha_hora'], axis =1)
df_cloud_CI.index = pd.to_datetime(df_cloud_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_CI.index = [df_cloud_CI.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_CI.index))]
df_cloud_CI.index = pd.to_datetime(df_cloud_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_CI = df_cloud_CI.between_time('06:00', '17:59')

df_cloud_AMVA = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_AMVA.csv',  sep=',')
df_cloud_AMVA.columns = ['fecha_hora', 'Porcentaje']
df_cloud_AMVA.index = df_cloud_AMVA['fecha_hora']
df_cloud_AMVA = df_cloud_AMVA.drop(['fecha_hora'], axis =1)
df_cloud_AMVA.index = pd.to_datetime(df_cloud_AMVA.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_AMVA.index = [df_cloud_AMVA.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_AMVA.index))]
df_cloud_AMVA.index = pd.to_datetime(df_cloud_AMVA.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_AMVA = df_cloud_AMVA.between_time('06:00', '17:59')


##########################################################################################################
##-----------------------------------LECTURA DE LOS DATOS  DE PIRANOMETRO-------------------------------##
##########################################################################################################

df_pira_TS = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60012018.txt', parse_dates=[2])
df_pira_TS = df_pira_TS.set_index(["fecha_hora"])
df_pira_TS.index = df_pira_TS.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_TS.index = df_pira_TS.index.tz_localize(None)
df_pira_TS = df_pira_TS[df_pira_TS['radiacion'] >=0]
df_pira_TS = df_pira_TS.between_time('06:00', '17:59')

df_pira_CI = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60022018.txt', parse_dates=[2])
df_pira_CI = df_pira_CI.set_index(["fecha_hora"])
df_pira_CI.index = df_pira_CI.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_CI.index = df_pira_CI.index.tz_localize(None)
df_pira_CI = df_pira_CI[df_pira_CI['radiacion'] >=0]
df_pira_CI = df_pira_CI.between_time('06:00', '17:59')

df_pira_JV = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60032018.txt', parse_dates=[2])
df_pira_JV = df_pira_JV.set_index(["fecha_hora"])
df_pira_JV.index = df_pira_JV.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_JV.index = df_pira_JV.index.tz_localize(None)
df_pira_JV = df_pira_JV[df_pira_JV['radiacion'] >=0]
df_pira_JV = df_pira_JV.between_time('06:00', '17:59')

##########################################################################################################
##-------------------------------------UNION DE LOS DATAFRAMES DE DATOS---------------------------------##
##########################################################################################################

df_result_TS = pd.concat([df_cloud_TS, df_pira_TS], axis=1, join='inner')
df_result_CI = pd.concat([df_cloud_CI, df_pira_TS], axis=1, join='inner')
df_result_AMVA = pd.concat([df_cloud_AMVA, df_pira_TS], axis=1, join='inner')

df_result_TS = df_result_TS.drop(['Unnamed: 0', 'idestacion','temperatura'], axis=1)
df_result_CI = df_result_CI.drop(['Unnamed: 0', 'idestacion','temperatura'], axis=1)
df_result_AMVA = df_result_AMVA.drop(['Unnamed: 0', 'idestacion','temperatura'], axis=1)

##########################################################################################################
##---------------------------------------DETERMINACION DE LOS UMBRALES----------------------------------##
##########################################################################################################

"Con los gradientes de la radiacion se estableceran los umbrales correspondientes para el caso de la mañana"
"y para el caso de la tarde"

## ---- UMBRAL CASO NUBOSO :

df_result_TS['Rad_deriv'] = np.gradient(df_result_TS['radiacion'].values)
df_result_CI['Rad_deriv'] = np.gradient(df_result_CI['radiacion'].values)
df_result_AMVA['Rad_deriv'] = np.gradient(df_result_AMVA['radiacion'].values)

df_PTS_Desp_Morning = df_result_TS.between_time('06:00','12:00')
df_PTS_Desp_Afternoon = df_result_TS.between_time('12:01','18:00')

df_PCI_Desp_Morning = df_result_CI.between_time('06:00','12:00')
df_PCI_Desp_Afternoon = df_result_CI.between_time('12:01','18:00')

df_PAMVA_Desp_Morning = df_result_AMVA.between_time('06:00','12:00')
df_PAMVA_Desp_Afternoon = df_result_AMVA.between_time('12:01','18:00')


df_PTS_Porc_Morning = df_PTS_Desp_Morning['Porcentaje'][df_PTS_Desp_Morning['Rad_deriv']<0]
Umbral_Nube_Morning_TS = np.nanmean(df_PTS_Porc_Morning.values)

df_PTS_Porc_Afternoon = df_PTS_Desp_Afternoon['Porcentaje'][df_PTS_Desp_Afternoon['Rad_deriv']>0]
Umbral_Nube_Afternoon_TS = np.nanmean(df_PTS_Porc_Afternoon.values)

UmbralH_Nube_TS = np.concatenate((np.repeat(Umbral_Nube_Morning_TS , 6),np.repeat(Umbral_Nube_Afternoon_TS, 6)), axis = None)

df_PCI_Porc_Morning = df_PCI_Desp_Morning['Porcentaje'][df_PCI_Desp_Morning['Rad_deriv']<0]
Umbral_Nube_Morning_CI = np.nanmean(df_PCI_Porc_Morning.values)

df_PCI_Porc_Afternoon = df_PCI_Desp_Afternoon['Porcentaje'][df_PCI_Desp_Afternoon['Rad_deriv']>0]
Umbral_Nube_Afternoon_CI = np.nanmean(df_PCI_Porc_Afternoon.values)

UmbralH_Nube_CI = np.concatenate((np.repeat(Umbral_Nube_Morning_CI , 6),np.repeat(Umbral_Nube_Afternoon_CI, 6)), axis = None)

df_PAMVA_Porc_Morning = df_PAMVA_Desp_Morning['Porcentaje'][df_PAMVA_Desp_Morning['Rad_deriv']<0]
Umbral_Nube_Morning_AMVA = np.nanmean(df_PAMVA_Porc_Morning.values)

df_PAMVA_Porc_Afternoon = df_PAMVA_Desp_Afternoon['Porcentaje'][df_PAMVA_Desp_Afternoon['Rad_deriv']>0]
Umbral_Nube_Afternoon_AMVA = np.nanmean(df_PAMVA_Porc_Afternoon.values)

UmbralH_Nube_AMVA = np.concatenate((np.repeat(Umbral_Nube_Morning_CI , 6),np.repeat(Umbral_Nube_Afternoon_CI, 6)), axis = None)

c = np.arange(6,18)

df_UmbralH_Nube_348 = pd.DataFrame(UmbralH_Nube_AMVA,  index=c,  columns=['Umbral'])

df_UmbralH_Nube_350 = pd.DataFrame(UmbralH_Nube_CI,  index=c,  columns=['Umbral'])

df_UmbralH_Nube_975 = pd.DataFrame(UmbralH_Nube_TS,  index=c,  columns=['Umbral'])

df_UmbralH_Nube_348.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/UmbralH_Nube_AMVA_Fisheye.csv')

df_UmbralH_Nube_350.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/UmbralH_Nube_CI_Fisheye.csv')

df_UmbralH_Nube_975.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/UmbralH_Nube_TS_Fisheye.csv')

## ---- UMBRAL CASO DESPEJADO :

# new_idx = np.arange(6, 18, 1)
#
# df_P348_MaxRad_H = df_result_AMVA.radiacion.groupby(by=[df_result_AMVA.index.hour]).max()
# df_P350_MaxRad_H = df_result_CI.radiacion.groupby(by=[df_result_CI.index.hour]).max()
# df_P975_MaxRad_H = df_result_TS.radiacion.groupby(by=[df_result_TS.index.hour]).max()
#
# df_P348_MaxRad_H = df_P348_MaxRad_H[df_P348_MaxRad_H.values>1]
# df_P350_MaxRad_H = df_P350_MaxRad_H[df_P350_MaxRad_H.values>1]
# df_P975_MaxRad_H = df_P975_MaxRad_H[df_P975_MaxRad_H.values>1]
#
#
# UmbralH_Desp_348 = []
# for i in range( len(df_P348_MaxRad_H.index)):
#     df = df_result_AMVA[(df_result_AMVA.index.hour ==df_P348_MaxRad_H.index[i]) & (df_result_AMVA['radiacion']== df_P348_MaxRad_H.values[i])]
#     UmbralH_Desp_348.append(df.Porcentaje.values[0])
#
# UmbralH_Desp_350 = []
# for i in range(len(df_P350_MaxRad_H.index)):
#     df = df_result_CI[(df_result_CI.index.hour ==df_P350_MaxRad_H.index[i]) & (df_result_CI['radiacion']== df_P350_MaxRad_H.values[i])]
#     UmbralH_Desp_350.append(df.Porcentaje.values[0])
#
# UmbralH_Desp_975 = []
# for i in range(len(df_P975_MaxRad_H.index)):
#     df = df_result_TS[(df_result_TS.index.hour ==df_P975_MaxRad_H.index[i]) & (df_result_TS['radiacion']== df_P975_MaxRad_H.values[i])]
#     UmbralH_Desp_975.append(df.Porcentaje.values[0])
#
# if len(UmbralH_Desp_348) == 11:
#      UmbralH_Desp_348 = np.insert(UmbralH_Desp_348, 0, np.nan)
# elif len(UmbralH_Desp_348) > 11:
#     print('Tiene los 12 elementos')
# elif len(UmbralH_Desp_348) < 11:
#     print('Tiene menos de 11 elementos')
#
# if len(UmbralH_Desp_350) == 11:
#      UmbralH_Desp_350 = np.insert(UmbralH_Desp_350, 0, np.nan)
# elif len(UmbralH_Desp_350) > 11:
#     print('Tiene los 12 elementos')
# elif len(UmbralH_Desp_350) < 11:
#     print('Tiene menos de 11 elementos')
#
# if len(UmbralH_Desp_975) == 11:
#      UmbralH_Desp_975 = np.insert(UmbralH_Desp_975, 0, np.nan)
# elif len(UmbralH_Desp_975) > 11:
#     print('Tiene los 12 elementos')
# elif len(UmbralH_Desp_975) < 11:
#     print('Tiene menos de 11 elementos')
#
#
# Umbral_Desp348 = np.nanmin(UmbralH_Desp_348)
# Umbral_Nuba348 = np.nanmax(UmbralH_Nube_AMVA)
#
# Umbral_Desp350 = np.nanmin(UmbralH_Desp_350)
# Umbral_Nuba350 = np.nanmax(UmbralH_Nube_CI)
#
# Umbral_Desp975 = np.nanmin(UmbralH_Desp_975)
# Umbral_Nuba975 = np.nanmax(UmbralH_Nube_TS)
#
# print ('Para el 348: '+str(Umbral_Desp348)+ ' y ' +str(Umbral_Nuba348))
# print ('Para el 350: '+str(Umbral_Desp350)+ ' y ' +str(Umbral_Nuba350))
# print ('Para el 975: '+str(Umbral_Desp975)+ ' y ' +str(Umbral_Nuba975))
