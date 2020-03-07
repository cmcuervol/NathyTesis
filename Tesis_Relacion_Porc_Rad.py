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
# import netCDF4 as nc
# from netCDF4 import Dataset
id
import itertools
import datetime
from scipy.stats import ks_2samp
import matplotlib.colors as colors
#from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import matplotlib.cm as cm
import os
#import statistics
from scipy import stats
import scipy.stats as st
from scipy.stats.stats import pearsonr


Horizonte = 'Anio'    ##-->Para que tome datos desde el 2018 de GOES se pone 'Anio', para que tome solo lo del experimento se pone 'Exp'
Pluvio = 'si'         ##--> Para que promedie la lluvia de los dos pluviometros debe ser 'si'

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa para el establecimeinto de la relación entre los datos de irradiancia,
factor de relfectancia y porcentaje de coberturas de nubes  a travez de scatters
y finalmente de un ajuste a tramos para encontrar el factor de ajustea cada tramo
entre el factor de reflectancia y la irradiancia.
"""
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop   = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

################################################################################################################
## -------------------------LECTURA DE LOS DATOS DE COBERTURA DE NUBES FISH EYE-------------------------------##
################################################################################################################

df_cloud_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/nubes_siata.csv',  sep=',')
df_cloud_TS.columns = ['fecha_hora', 'Porcentaje']
df_cloud_TS.index = df_cloud_TS['fecha_hora']
df_cloud_TS = df_cloud_TS.drop(['fecha_hora'], axis =1)
df_cloud_TS.index = pd.to_datetime(df_cloud_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_TS.index = [df_cloud_TS.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_TS.index))]
df_cloud_TS.index = pd.to_datetime(df_cloud_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_TS = df_cloud_TS.sort_index(axis = 0)


df_cloud_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_CI.csv',  sep=',')
df_cloud_CI.columns = ['fecha_hora', 'Porcentaje']
df_cloud_CI.index = df_cloud_CI['fecha_hora']
df_cloud_CI = df_cloud_CI.drop(['fecha_hora'], axis =1)
df_cloud_CI.index = pd.to_datetime(df_cloud_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_CI.index = [df_cloud_CI.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_CI.index))]
df_cloud_CI.index = pd.to_datetime(df_cloud_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_CI = df_cloud_CI.sort_index(axis = 0)


df_cloud_AMVA = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_AMVA.csv',  sep=',')
df_cloud_AMVA.columns = ['fecha_hora', 'Porcentaje']
df_cloud_AMVA.index = df_cloud_AMVA['fecha_hora']
df_cloud_AMVA = df_cloud_AMVA.drop(['fecha_hora'], axis =1)
df_cloud_AMVA.index = pd.to_datetime(df_cloud_AMVA.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_AMVA.index = [df_cloud_AMVA.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_AMVA.index))]
df_cloud_AMVA.index = pd.to_datetime(df_cloud_AMVA.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_AMVA = df_cloud_AMVA.sort_index(axis = 0)

df_cloud_AMVA = df_cloud_AMVA.loc[~df_cloud_AMVA.index.duplicated(keep='first')]
df_cloud_CI = df_cloud_CI.loc[~df_cloud_CI.index.duplicated(keep='first')]
df_cloud_TS = df_cloud_TS.loc[~df_cloud_TS.index.duplicated(keep='first')]

## ------------------------------------DATOS HORARIOS DE % DE NUBES------------------------- ##

df_cloud_AMVA_h =  df_cloud_AMVA.groupby(pd.Grouper(freq="H")).mean()
df_cloud_CI_h =  df_cloud_CI.groupby(pd.Grouper(freq="H")).mean()
df_cloud_TS_h =  df_cloud_TS.groupby(pd.Grouper(freq="H")).mean()

df_cloud_TS_h = df_cloud_TS_h.between_time('06:00', '17:59')
df_cloud_CI_h = df_cloud_CI_h.between_time('06:00', '17:59')
df_cloud_AMVA_h = df_cloud_AMVA_h.between_time('06:00', '17:59')


#################################################################################################
## --------------INCORPORANDO LOS DATOS DE RADIACIÓN PARA LOS DOS AÑOS DE DATOS--------------- ##
#################################################################################################

df_P975 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60012018_2019.txt', parse_dates=[2])
df_P350 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60022018_2019.txt', parse_dates=[2])
df_P348 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60032018_2019.txt', parse_dates=[2])

df_P975 = df_P975.set_index(["fecha_hora"])
df_P975.index = df_P975.index.tz_localize('UTC').tz_convert('America/Bogota')
df_P975.index = df_P975.index.tz_localize(None)

df_P350 = df_P350.set_index(["fecha_hora"])
df_P350.index = df_P350.index.tz_localize('UTC').tz_convert('America/Bogota')
df_P350.index = df_P350.index.tz_localize(None)

df_P348 = df_P348.set_index(["fecha_hora"])
df_P348.index = df_P348.index.tz_localize('UTC').tz_convert('America/Bogota')
df_P348.index = df_P348.index.tz_localize(None)

df_P975.index = pd.to_datetime(df_P975.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P350.index = pd.to_datetime(df_P350.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P348.index = pd.to_datetime(df_P348.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

## ----------------ACOTANDO LOS DATOS A VALORES VÁLIDOS---------------- ##

'Como en este caso lo que interesa es la radiacion, para la filtración de los datos, se'
'considerarán los datos de radiacion mayores a 0.'

df_P975 = df_P975[(df_P975['radiacion'] > 0) ]
df_P350 = df_P350[(df_P350['radiacion'] > 0) ]
df_P348 = df_P348[(df_P348['radiacion'] > 0) ]

df_P975_h = df_P975.groupby(pd.Grouper(freq="H")).mean()
df_P350_h = df_P350.groupby(pd.Grouper(freq="H")).mean()
df_P348_h = df_P348.groupby(pd.Grouper(freq="H")).mean()

df_P975_h = df_P975_h.between_time('06:00', '17:59')
df_P350_h = df_P350_h.between_time('06:00', '17:59')
df_P348_h = df_P348_h.between_time('06:00', '17:59')

#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
Rad_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix350_Anio.npy')
Rad_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix348_Anio.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')
fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')

Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)


Rad_df_350 = pd.DataFrame()
Rad_df_350['Fecha_Hora'] = fechas_horas
Rad_df_350['Radiacias'] = Rad_pixel_350
Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_350.index = Rad_df_350['Fecha_Hora']
Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)


Rad_df_348 = pd.DataFrame()
Rad_df_348['Fecha_Hora'] = fechas_horas
Rad_df_348['Radiacias'] = Rad_pixel_348
Rad_df_348['Fecha_Hora'] = pd.to_datetime(Rad_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_348.index = Rad_df_348['Fecha_Hora']
Rad_df_348 = Rad_df_348.drop(['Fecha_Hora'], axis=1)

## ------------------------------------DATOS HORARIOS DE REFLECTANCIAS------------------------- ##

Rad_df_348_h =  Rad_df_348.groupby(pd.Grouper(freq="H")).mean()
Rad_df_350_h =  Rad_df_350.groupby(pd.Grouper(freq="H")).mean()
Rad_df_975_h =  Rad_df_975.groupby(pd.Grouper(freq="H")).mean()

Rad_df_348_h = Rad_df_348_h.between_time('06:00', '17:59')
Rad_df_350_h = Rad_df_350_h.between_time('06:00', '17:59')
Rad_df_975_h = Rad_df_975_h.between_time('06:00', '17:59')

#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

COD_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix975_EXP.npy')
COD_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix350_EXP.npy')
COD_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix348_EXP.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CODEXP.npy')

                   ## -- Selección del pixel de la TS
COD_df_975 = pd.DataFrame()
COD_df_975['Fecha_Hora'] = fechas_horas
COD_df_975['COD'] = COD_pixel_975
COD_df_975['Fecha_Hora'] = pd.to_datetime(COD_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_975.index = COD_df_975['Fecha_Hora']
COD_df_975 = COD_df_975.drop(['Fecha_Hora'], axis=1)

                   ## -- Selección del pixel de la CI

COD_df_350 = pd.DataFrame()
COD_df_350['Fecha_Hora'] = fechas_horas
COD_df_350['COD'] = COD_pixel_350
COD_df_350['Fecha_Hora'] = pd.to_datetime(COD_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_350.index = COD_df_350['Fecha_Hora']
COD_df_350 = COD_df_350.drop(['Fecha_Hora'], axis=1)


                   ## -- Selección del pixel de la JV

COD_df_348 = pd.DataFrame()
COD_df_348['Fecha_Hora'] = fechas_horas[6:]
COD_df_348['COD'] = COD_pixel_348
COD_df_348['Fecha_Hora'] = pd.to_datetime(COD_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_348.index = COD_df_348['Fecha_Hora']
COD_df_348 = COD_df_348.drop(['Fecha_Hora'], axis=1)

## ------------------------------------DATOS HORARIOS DE COD------------------------ ##

COD_df_348_h =  COD_df_348.groupby(pd.Grouper(freq="H")).mean()
COD_df_350_h =  COD_df_350.groupby(pd.Grouper(freq="H")).mean()
COD_df_975_h =  COD_df_975.groupby(pd.Grouper(freq="H")).mean()

COD_df_348_h = COD_df_348_h.between_time('06:00', '17:59')
COD_df_350_h = COD_df_350_h.between_time('06:00', '17:59')
COD_df_975_h = COD_df_975_h.between_time('06:00', '17:59')

###################################################################
## -----------------CONCATENANDO LOS DATAFRAMES----------------- ##
###################################################################

df_complete_348_h = pd.concat([df_P348_h, df_cloud_AMVA_h, Rad_df_348_h, COD_df_348_h], axis=1)
df_complete_350_h = pd.concat([df_P350_h, df_cloud_CI_h, Rad_df_350_h, COD_df_350_h], axis=1)
df_complete_975_h = pd.concat([df_P975_h, df_cloud_TS_h, Rad_df_975_h, COD_df_975_h], axis=1)


Histograma = plt.hist(df_complete_975_h.COD.values , bins=5, density = False)[0]
Bins = plt.hist(df_complete_975_h.COD.values  , bins=5, density = False)[1]

# ##---------------------------------SOLO 2018---------------------------##
#
# df_complete_348_h = df_complete_348_h[(df_complete_348_h.index.year == 2018)|(df_complete_348_h.index.year == 2019)]
# df_complete_350_h = df_complete_350_h[(df_complete_350_h.index.year == 2018)|(df_complete_350_h.index.year == 2019)]
# df_complete_975_h = df_complete_975_h[(df_complete_975_h.index.year == 2018)|(df_complete_975_h.index.year == 2019)]

###################################################################################
## -----------------RELACION REFELCTANCIAS SOBRE LA IRRADIANCIA----------------- ##
###################################################################################

"Se entenderá q la pendiente de la relación entre la irradiancia y el factor de reflectancia"
"indicará el factor de incidencidencia o amortiguación de la luz solar sobre la radiación del sol."
"Esta, será entonces la reducción de ejerce, y se hallará para cada hora del dia, con los datos del"
"2018 y del 2019."

Horas = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
Meses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
H =[]
M=[]

##-----------------------------------975------------------------------------------##
df_complete_975_h = df_complete_975_h.dropna()
slopes_975 = []
std_975 = []
corr_975 =[]
for j in range(len(Meses)):
    for i in range(len(Horas)):
        slope_h, intercept_h, r_h_value, p_h_value, std_err_h = stats.linregress(df_complete_975_h['Radiacias'][(df_complete_975_h.index.hour==Horas[i])
         & (df_complete_975_h.index.month==Meses[j])].values, df_complete_975_h['radiacion'][(df_complete_975_h.index.hour==Horas[i]) & (df_complete_975_h.index.month==Meses[j])].values)
        slopes_975.append(slope_h)
        std_975.append(df_complete_975_h['radiacion'][(df_complete_975_h.index.hour==Horas[i]) & (df_complete_975_h.index.month==Meses[j])].std())
        corr_975.append(pearsonr(df_complete_975_h['Radiacias'][(df_complete_975_h.index.hour==Horas[i])
         & (df_complete_975_h.index.month==Meses[j])].values, df_complete_975_h['radiacion'][(df_complete_975_h.index.hour==Horas[i]) & (df_complete_975_h.index.month==Meses[j])].values)[0])
        H.append(Horas[i])
        M.append(Meses[j])
df_Relacion_975 = pd.DataFrame( {'Mes':M, 'Hora':H, 'Slope':slopes_975, 'Std':std_975, 'Corr':corr_975})

##-----------------------------------350------------------------------------------##
df_complete_350_h = df_complete_350_h.dropna()
slopes_350 = []
std_350 = []
corr_350 =[]
for j in range(len(Meses)):
    for i in range(len(Horas)):
        try:
            slope_h, intercept_h, r_h_value, p_h_value, std_err_h = stats.linregress(df_complete_350_h['Radiacias'][(df_complete_350_h.index.hour==Horas[i])
             & (df_complete_350_h.index.month==Meses[j])].values, df_complete_350_h['radiacion'][(df_complete_350_h.index.hour==Horas[i]) & (df_complete_350_h.index.month==Meses[j])].values)
            slopes_350.append(slope_h)
            std_350.append(df_complete_350_h['radiacion'][(df_complete_350_h.index.hour==Horas[i]) & (df_complete_350_h.index.month==Meses[j])].std())
            corr_350.append(pearsonr(df_complete_350_h['Radiacias'][(df_complete_350_h.index.hour==Horas[i])
             & (df_complete_350_h.index.month==Meses[j])].values, df_complete_350_h['radiacion'][(df_complete_350_h.index.hour==Horas[i]) & (df_complete_350_h.index.month==Meses[j])].values)[0])
        except ValueError:
            slopes_350.append(np.nan)
            std_350.append(np.nan)
            corr_350.append(np.nan)


df_Relacion_350 = pd.DataFrame( {'Mes':M, 'Hora':H, 'Slope':slopes_350, 'Std':std_350, 'Corr':corr_350})

##-----------------------------------348------------------------------------------##
df_complete_348_h = df_complete_348_h.dropna()
slopes_348 = []
std_348 = []
corr_348 =[]
for j in range(len(Meses)):
    for i in range(len(Horas)):
        slope_h, intercept_h, r_h_value, p_h_value, std_err_h = stats.linregress(df_complete_348_h['Radiacias'][(df_complete_348_h.index.hour==Horas[i])
         & (df_complete_348_h.index.month==Meses[j])].values, df_complete_348_h['radiacion'][(df_complete_348_h.index.hour==Horas[i]) & (df_complete_348_h.index.month==Meses[j])].values)
        slopes_348.append(slope_h)
        std_348.append(df_complete_348_h['radiacion'][(df_complete_348_h.index.hour==Horas[i]) & (df_complete_348_h.index.month==Meses[j])].std())
        corr_348.append(pearsonr(df_complete_348_h['Radiacias'][(df_complete_348_h.index.hour==Horas[i])
         & (df_complete_348_h.index.month==Meses[j])].values, df_complete_348_h['radiacion'][(df_complete_348_h.index.hour==Horas[i]) & (df_complete_348_h.index.month==Meses[j])].values)[0])
df_Relacion_348 = pd.DataFrame( {'Mes':M, 'Hora':H, 'Slope':slopes_348, 'Std':std_348, 'Corr':corr_348})
#########################################################
## -----------------GUARDANDO LOS DF------------------ ##
#########################################################
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
df_Relacion_348.to_csv(Path_save[0:45]+'_DF_SlopeStd_348'+'.csv', sep=',')
df_Relacion_350.to_csv(Path_save[0:45]+'_DF_SlopeStd_350'+'.csv', sep=',')
df_Relacion_975.to_csv(Path_save[0:45]+'_DF_SlopeStd_975'+'.csv', sep=',')

#################################################
## -----------------GRAFICAS------------------ ##
#################################################


##--------------------------------------DURANTE EL 2018----------------------------------------------------##

#df_cloud_TS_h = df_cloud_TS_h[df_cloud_TS_h.index.year == 2018]
df_cloud_TS_JAS = df_cloud_TS_h[(df_cloud_TS_h.index.month == 7)|(df_cloud_TS_h.index.month == 8) |(df_cloud_TS_h.index.month == 9)]
df_cloud_TS_JAS = df_cloud_TS_h
#df_P975_h = df_P975_h[df_P975_h.index.year == 2018]
#df_P975_JAS = df_P975_h[(df_P975_h.index.month == 7)|(df_P975_h.index.month == 8) |(df_P975_h.index.month == 9)]
df_P975_JAS = df_P975_h
#Rad_df_975_h = Rad_df_975_h[Rad_df_975_h.index.year == 2018]
#COD_df_975_h = COD_df_975_h[Rad_df_975_h.index.year == 2018]
#df_P975_JAS = Rad_df_975_h[(Rad_df_975_h.index.month == 7)|(Rad_df_975_h.index.month == 8) |(Rad_df_975_h.index.month == 9)]
COD_df_975_JAS = COD_df_975_h
Rad_df_975_JAS = Rad_df_975_h
df_complete_975_JAS = pd.concat([df_P975_JAS, df_cloud_TS_JAS, Rad_df_975_JAS, COD_df_975_JAS], axis=1)
df_complete_975_JAS = df_complete_975_JAS.drop(['Unnamed: 0', 'idestacion',  'temperatura'], axis=1)
df_complete_975_JAS_12h = df_complete_975_JAS[(df_complete_975_JAS.index.hour == 12)|(df_complete_975_JAS.index.hour == 13)|(df_complete_975_JAS.index.hour == 11)]


fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
sc = ax.scatter(df_complete_975_JAS_12h.Porcentaje.values, df_complete_975_JAS_12h.radiacion.values, s=70, c= df_complete_975_JAS_12h.COD.values, cmap='viridis_r', vmin= np.nanmin(df_complete_975_JAS_12h.Radiacias.values), vmax=np.nanmax(df_complete_975_JAS_12h.Radiacias.values),   marker = ".")
ax.set_ylabel(u"Irradiance  $[W/m^{2}]$", fontproperties=prop_1, fontsize=20)
ax.set_xlabel(u"[%] Clouds", fontproperties=prop_1, fontsize=20)
ax.set_ylim(0, 1200)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend(loc = 2)
plt.title(u'Hourly Relationship between [%] Clouds and Irradiance ', fontweight = "bold",  fontproperties = prop, fontsize = 25)
cbar2_ax = fig.add_axes([0.90, 0.15, 0.015, 0.65 ])
cbar = fig.colorbar(sc, cax=cbar2_ax, orientation='vertical', format="%.2f")
#cbar.set_label('Reflectances [%]', fontsize=20, fontproperties=prop)
cbar.set_label('COD', fontsize=20, fontproperties=prop)
cbar.outline.set_edgecolor('gray')
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterPorcRadiacion_2018.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterPorcRadiacion_2018.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##----------------------------------PENDIENTES PARA CADA HORA--------------------------------------------##

elev_min = min(np.nanmin(slopes_348)  , np.nanmin(slopes_350), np.nanmin(slopes_975))-0.01
elev_max = max(np.nanmax(slopes_348)  , np.nanmax(slopes_350), np.nanmax(slopes_975))+0.01
plt.close('all')
fig = plt.figure(figsize=(13,8))
ax2 = fig.add_subplot(1, 1, 1)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(Horas,  slopes_348, color = '#800000', lw=1.5, label = 'Este')
ax2.scatter(Horas,  slopes_348, marker='.', c = '#800000', s=30)
ax2.plot(Horas,  slopes_350, color = '#e6194B', lw=1.5, label = 'Oeste')
ax2.scatter(Horas,  slopes_350, marker='.', c = '#e6194B', s=30)
ax2.plot(Horas,  slopes_975, color = '#f58231', lw=1.5, label = 'Centro')
ax2.scatter(Horas,  slopes_975, marker='.', c = '#f58231', s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"Pendiente  [%]", fontproperties = prop_1, fontsize=20)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(Horas, minor=False, rotation = 20)
ax2.set_ylim(elev_min, elev_max)
ax2.set_title(u'Pendientes horarias entre irradiancia y refelctancia', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HourlySlopes.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/HourlySlopes.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##-----------------------------RELACION IRRADIANCIAS VS REFLECTANCIAS DISPERSION ---------------------##

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_complete_350_h['Radiacias'].values, df_complete_350_h['radiacion'].values, s=50, c='#70AFBA', alpha=0.5, marker = ".")
ax1.set_ylabel(u"Irradiancia", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Reflectancia", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relationship in West point' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.set_ylim(0, 1300)
ax1.set_xlim(0, 100)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(df_complete_975_h['Radiacias'].values, df_complete_975_h['radiacion'].values, s=50, c='#70AFBA',  alpha=0.5, marker = ".")
ax2.set_ylabel(u"Irradiancia", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Reflectancia", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Relationship in West Center point' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.set_ylim(0, 1300)
ax2.set_xlim(0, 100)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(df_complete_348_h['Radiacias'].values , df_complete_348_h['radiacion'].values, s=50, c='#70AFBA',  alpha=0.5, marker = ".")
ax3.set_ylabel(u"Irradiancia", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Reflectancia", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Relationship in East point' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.set_ylim(0, 1300)
ax3.set_xlim(0, 100)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax3.legend()

plt.subplots_adjust( wspace=0.4, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Dispersion_IrraReflec.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Dispersion_IrraReflec.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


##----------------------------------GENERAL---------------------------------------------------##

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.scatter(df_complete_975_h.radiacion.values, df_complete_975_h.Porcentaje.values, s=40, c='orange', label='P_TS', alpha=0.3, marker = ".")
ax.scatter(df_complete_350_h.radiacion.values, df_complete_350_h.Porcentaje.values, s=40, c='green', label='P_CI', alpha=0.3, marker = "*")
ax.scatter(df_complete_348_h.radiacion.values, df_complete_348_h.Porcentaje.values, s=40, c='red', label='P_JV', alpha=0.3, marker = "p")
ax.set_ylabel(u"Porcentaje Nubes",  fontproperties=prop_1, fontsize=20)
ax.set_xlabel(u"Radiacion", fontproperties=prop_1, fontsize=20)
ax.set_ylim(0, 101)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend(loc = 2)
plt.title(u' Relacion Porc Nubes y Anomal Rad', fontsize=18,  fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterPorcRadiacion.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterPorcRadiacion.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##--------------------------------------A LAS 12----------------------------------------------------##

df_complete_975_12h = df_complete_975_h[df_complete_975_h.index.hour == 12]
df_complete_350_12h = df_complete_350_h[df_complete_350_h.index.hour == 12]
df_complete_348_12h = df_complete_348_h[df_complete_348_h.index.hour == 12]


fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.scatter(df_complete_975_12h.radiacion.values, df_complete_975_12h.Porcentaje.values, s=40, c='orange', label='P_TS', alpha=0.9, marker = ".")
ax.scatter(df_complete_350_12h.radiacion.values, df_complete_350_12h.Porcentaje.values, s=40, c='green', label='P_CI', alpha=0.3, marker = "*")
ax.scatter(df_complete_348_12h.radiacion.values, df_complete_348_12h.Porcentaje.values, s=40, c='red', label='P_JV', alpha=0.3, marker = "p")
ax.set_ylabel(u"Nubes Porc",  fontproperties=prop_1, fontsize=20)
ax.set_xlabel(u"Radiacion", fontproperties=prop_1, fontsize=20)
ax.set_ylim(0, 100)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend(loc = 2)
plt.title(u' Relacion Porc Nubes y Anomal Rad a las 12', fontsize=18,  fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterPorcRadiacion_12.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterPorcRadiacion_12.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
