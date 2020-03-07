#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
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

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

"Codigo que permite la porderación de la nubosidad por la ponderación de sus horas. Se realiza para el "
"horizonte de tiempo de mayor rango q se tenga de los datos de GOES CH2. Está sijeto a los umbrales de"
"cada hora, por lo que se vrea un back up en la carpeta de Back uos de Drive"

#################################################################################################
## -----------------INCORPORANDO LOS DATOS DE RADIACIÓN Y DE LOS EXPERIMENTOS----------------- ##
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

df_P975_h = df_P975.groupby(pd.Grouper(level='fecha_hora', freq='1H')).mean()
df_P350_h = df_P350.groupby(pd.Grouper(level='fecha_hora', freq='1H')).mean()
df_P348_h = df_P348.groupby(pd.Grouper(level='fecha_hora', freq='1H')).mean()

df_P975_h = df_P975_h.between_time('06:00', '17:59')
df_P350_h = df_P350_h.between_time('06:00', '17:59')
df_P348_h = df_P348_h.between_time('06:00', '17:59')

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

################################################################################################
## -------------------------------UMBRALES DE LAS REFLECTANCIAS------------------------------ ##
################################################################################################

Umbral_up_348   = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Nuba.csv',  sep=',',  header = None)
Umbral_down_348 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Desp.csv',  sep=',',  header = None)
Umbral_up_348.columns=['Hora', 'Umbral']
Umbral_up_348.index = Umbral_up_348['Hora']
Umbral_up_348 = Umbral_up_348.drop(['Hora'], axis=1)
Umbral_down_348.columns=['Hora', 'Umbral']
Umbral_down_348.index = Umbral_down_348['Hora']
Umbral_down_348 = Umbral_down_348.drop(['Hora'], axis=1)
#Umbrales_348 = [Umbral_down_348, Umbral_up_348]

Umbral_up_350   = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Nuba.csv',  sep=',',  header = None)
Umbral_down_350 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Desp.csv',  sep=',',  header = None)
Umbral_up_350.columns=['Hora', 'Umbral']
Umbral_up_350.index = Umbral_up_350['Hora']
Umbral_up_350 = Umbral_up_350.drop(['Hora'], axis=1)
Umbral_down_350.columns=['Hora', 'Umbral']
Umbral_down_350.index = Umbral_down_350['Hora']
Umbral_down_350 = Umbral_down_350.drop(['Hora'], axis=1)
#Umbrales_350 = [Umbral_down_350, Umbral_up_350]

Umbral_up_975   = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Nuba.csv',  sep=',',  header = None)
Umbral_down_975 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Desp.csv',  sep=',',  header = None)
Umbral_up_975.columns=['Hora', 'Umbral']
Umbral_up_975.index = Umbral_up_975['Hora']
Umbral_up_975 = Umbral_up_975.drop(['Hora'], axis=1)
Umbral_down_975.columns=['Hora', 'Umbral']
Umbral_down_975.index = Umbral_down_975['Hora']
Umbral_down_975 = Umbral_down_975.drop(['Hora'], axis=1)
#Umbrales_975 = [Umbral_down_975, Umbral_up_975]

####################################################################################
## ----------------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL---------------- ##
####################################################################################

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')


#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
Rad_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix350_Anio.npy')
Rad_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix348_Anio.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')

df_fh  = pd.DataFrame()
df_fh ['fecha_hora'] = fechas_horas
df_fh['fecha_hora'] = pd.to_datetime(df_fh['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_fh.index = df_fh['fecha_hora']
w = pd.date_range(df_fh.index.min(), df_fh.index.max()).difference(df_fh.index)
df_fh = df_fh[df_fh.index.hour != 5]
fechas_horas = df_fh['fecha_hora'].values


                   ## -- Selección del pixel de la TS
Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)

                   ## -- Selección del pixel de la CI

Rad_df_350 = pd.DataFrame()
Rad_df_350['Fecha_Hora'] = fechas_horas
Rad_df_350['Radiacias'] = Rad_pixel_350
Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_350.index = Rad_df_350['Fecha_Hora']
Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)


                   ## -- Selección del pixel de la JV

Rad_df_348 = pd.DataFrame()
Rad_df_348['Fecha_Hora'] = fechas_horas
Rad_df_348['Radiacias'] = Rad_pixel_348
Rad_df_348['Fecha_Hora'] = pd.to_datetime(Rad_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_348.index = Rad_df_348['Fecha_Hora']
Rad_df_348 = Rad_df_348.drop(['Fecha_Hora'], axis=1)

'OJOOOO DESDE ACÁ-----------------------------------------------------------------------------------------'
'Se comenta porque se estaba perdiendo la utilidad de la información cada 10 minutos al suavizar la serie.'
## ------------------------CAMBIANDO LOS DATOS HORARIOS POR LOS ORIGINALES---------------------- ##
Rad_df_348_h = Rad_df_348
Rad_df_350_h = Rad_df_350
Rad_df_975_h = Rad_df_975

## ------------------------------------DATOS HORARIOS DE REFLECTANCIAS------------------------- ##

# Rad_df_348_h =  Rad_df_348.groupby(pd.Grouper(freq="H")).mean()
# Rad_df_350_h =  Rad_df_350.groupby(pd.Grouper(freq="H")).mean()
# Rad_df_975_h =  Rad_df_975.groupby(pd.Grouper(freq="H")).mean()

'OJOOOO HASTA ACÁ-----------------------------------------------------------------------------------------'

Rad_df_348_h = Rad_df_348_h.between_time('06:00', '17:59')
Rad_df_350_h = Rad_df_350_h.between_time('06:00', '17:59')
Rad_df_975_h = Rad_df_975_h.between_time('06:00', '17:59')


## ---------------------------------FDP COMO GRÁFICA----------------------------------------- ##

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Rad_df_348_h['Radiacias'].values[~np.isnan(Rad_df_348_h['Radiacias'].values)], bins='auto', alpha = 0.5)
#Umbrales_line1 = [ax1.axvline(x=xc, color='k', linestyle='--') for xc in Umbrales_348]
#ax1.text(Umbrales_348[0], 1000,  str(Umbrales_348[0]) , fontsize=10, fontproperties=prop_1)
ax1.set_title(u'Distribución del FR en JV', fontproperties=prop, fontsize = 15)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1, fontsize = 15)
ax1.set_xlabel(u'Reflectancia', fontproperties=prop_1, fontsize = 15)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Rad_df_350_h['Radiacias'].values[~np.isnan(Rad_df_350_h['Radiacias'].values)], bins='auto', alpha = 0.5)
#Umbrales_line2 = [ax2.axvline(x=xc, color='k', linestyle='--') for xc in Umbrales_350]
ax2.set_title(u'Distribución del FR en CI', fontproperties=prop, fontsize = 15)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1, fontsize = 15)
ax2.set_xlabel(u'Reflectancia', fontproperties=prop_1, fontsize = 15)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Rad_df_975_h['Radiacias'].values[~np.isnan(Rad_df_975_h['Radiacias'].values)], bins='auto', alpha = 0.5)
#Umbrales_line3 = [ax3.axvline(x=xc, color='k', linestyle='--') for xc in Umbrales_975]
ax3.set_title(u'Distribución del FR en TS', fontproperties=prop, fontsize = 15)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1, fontsize = 15)
ax3.set_xlabel(u'Reflectancia', fontproperties=prop_1, fontsize = 15)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistogramaFrecuenciasCH2_2018.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/HistogramaFrecuenciasCH2_2018.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

################################################################################################
## -------------------------OBTENER EL DF DEL ESCENARIO DESPEJADO---------------------------- ##
################################################################################################

Rad_desp_348 = []
FH_Desp_348 = []
for i in range(len(Rad_df_348_h)):
    for j in range(len(Umbral_down_348.index)):
        if (Rad_df_348_h.index[i].hour == Umbral_down_348.index[j]) & (Rad_df_348_h.Radiacias.values[i] <= Umbral_down_348.values[j]):
            Rad_desp_348.append(Rad_df_348_h.Radiacias.values[i])
            FH_Desp_348.append(Rad_df_348_h.index[i])

df_348_desp = pd.DataFrame()
df_348_desp['Radiacias'] = Rad_desp_348
df_348_desp['Fecha_Hora'] = FH_Desp_348
df_348_desp['Fecha_Hora'] = pd.to_datetime(df_348_desp['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_348_desp.index = df_348_desp['Fecha_Hora']
df_348_desp = df_348_desp.drop(['Fecha_Hora'], axis=1)

Rad_desp_350 = []
FH_Desp_350 = []
for i in range(len(Rad_df_350_h)):
    for j in range(len(Umbral_down_350.index)):
        if (Rad_df_350_h.index[i].hour == Umbral_down_350.index[j]) & (Rad_df_350_h.Radiacias.values[i] <= Umbral_down_350.values[j]):
            Rad_desp_350.append(Rad_df_350_h.Radiacias.values[i])
            FH_Desp_350.append(Rad_df_350_h.index[i])

df_350_desp = pd.DataFrame()
df_350_desp['Radiacias'] = Rad_desp_350
df_350_desp['Fecha_Hora'] = FH_Desp_350
df_350_desp['Fecha_Hora'] = pd.to_datetime(df_350_desp['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_350_desp.index = df_350_desp['Fecha_Hora']
df_350_desp = df_350_desp.drop(['Fecha_Hora'], axis=1)

Rad_desp_975 = []
FH_Desp_975 = []
for i in range(len(Rad_df_975_h)):
    for j in range(len(Umbral_down_975.index)):
        if (Rad_df_975_h.index[i].hour == Umbral_down_975.index[j]) & (Rad_df_975_h.Radiacias.values[i] <= Umbral_down_975.values[j]):
            Rad_desp_975.append(Rad_df_975_h.Radiacias.values[i])
            FH_Desp_975.append(Rad_df_975_h.index[i])

df_975_desp = pd.DataFrame()
df_975_desp['Radiacias'] = Rad_desp_975
df_975_desp['Fecha_Hora'] = FH_Desp_975
df_975_desp['Fecha_Hora'] = pd.to_datetime(df_975_desp['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_975_desp.index = df_975_desp['Fecha_Hora']
df_975_desp = df_975_desp.drop(['Fecha_Hora'], axis=1)

################################################################################################
## --------------------------OBTENER EL DF DEL ESCENARIO NUBADO------------------------------ ##
################################################################################################

Rad_nuba_348 = []
FH_Nuba_348 = []
for i in range(len(Rad_df_348_h)):
    for j in range(len(Umbral_up_348.index)):
        if (Rad_df_348_h.index[i].hour == Umbral_up_348.index[j]) & (Rad_df_348_h.Radiacias.values[i] >= Umbral_up_348.values[j]):
            Rad_nuba_348.append(Rad_df_348_h.Radiacias.values[i])
            FH_Nuba_348.append(Rad_df_348_h.index[i])

df_348_nuba = pd.DataFrame()
df_348_nuba['Radiacias'] = Rad_nuba_348
df_348_nuba['Fecha_Hora'] = FH_Nuba_348
df_348_nuba['Fecha_Hora'] = pd.to_datetime(df_348_nuba['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_348_nuba.index = df_348_nuba['Fecha_Hora']
df_348_nuba = df_348_nuba.drop(['Fecha_Hora'], axis=1)

Rad_nuba_350 = []
FH_Nuba_350 = []
for i in range(len(Rad_df_350_h)):
    for j in range(len(Umbral_up_350.index)):
        if (Rad_df_350_h.index[i].hour == Umbral_up_350.index[j]) & (Rad_df_350_h.Radiacias.values[i] >= Umbral_up_350.values[j]):
            Rad_nuba_350.append(Rad_df_350_h.Radiacias.values[i])
            FH_Nuba_350.append(Rad_df_350_h.index[i])

df_350_nuba = pd.DataFrame()
df_350_nuba['Radiacias'] = Rad_nuba_350
df_350_nuba['Fecha_Hora'] = FH_Nuba_350
df_350_nuba['Fecha_Hora'] = pd.to_datetime(df_350_nuba['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_350_nuba.index = df_350_nuba['Fecha_Hora']
df_350_nuba = df_350_nuba.drop(['Fecha_Hora'], axis=1)

Rad_nuba_975 = []
FH_Nuba_975 = []
for i in range(len(Rad_df_975_h)):
    for j in range(len(Umbral_up_975.index)):
        if (Rad_df_975_h.index[i].hour == Umbral_up_975.index[j]) & (Rad_df_975_h.Radiacias.values[i] >= Umbral_up_975.values[j]):
            Rad_nuba_975.append(Rad_df_975_h.Radiacias.values[i])
            FH_Nuba_975.append(Rad_df_975_h.index[i])

df_975_nuba = pd.DataFrame()
df_975_nuba['Radiacias'] = Rad_nuba_975
df_975_nuba['Fecha_Hora'] = FH_Nuba_975
df_975_nuba['Fecha_Hora'] = pd.to_datetime(df_975_nuba['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_975_nuba.index = df_975_nuba['Fecha_Hora']
df_975_nuba = df_975_nuba.drop(['Fecha_Hora'], axis=1)

## -------------------------OBTENER LAS HORAS Y FECHAS DESPEJADAS---------------------------- ##

Hora_desp_348 = df_348_desp.index.hour
Fecha_desp_348 = df_348_desp.index.date

Hora_desp_350 = df_350_desp.index.hour
Fecha_desp_350 = df_350_desp.index.date

Hora_desp_975 = df_975_desp.index.hour
Fecha_desp_975 = df_975_desp.index.date

## ----------------------------OBTENER LAS HORAS Y FECHAS NUBADAS---------------------------- ##

Hora_nuba_348 = df_348_nuba.index.hour
Fecha_nuba_348 = df_348_nuba.index.date

Hora_nuba_350 = df_350_nuba.index.hour
Fecha_nuba_350 = df_350_nuba.index.date

Hora_nuba_975 = df_975_nuba.index.hour
Fecha_nuba_975 = df_975_nuba.index.date

## -----------------------------DIBUJAR LOS HISTOGRAMAS DE LAS HORAS ------ ----------------------- #
fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Hora_desp_348, bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax1.hist(Hora_nuba_348, bins='auto', alpha = 0.5, label = 'Nub')
ax1.set_title(u'Distribución de nubes por horas en JV', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Horas', fontproperties=prop_1)
ax1.set_ylim(0, 1350)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Hora_desp_350, bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax2.hist(Hora_nuba_350, bins='auto', alpha = 0.5, label = 'Nub')
ax2.set_title(u'Distribución de nubes por horas en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Horas', fontproperties=prop_1)
ax2.set_ylim(0, 1350)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Hora_desp_975, bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax3.hist(Hora_nuba_975, bins='auto', alpha = 0.5, label = 'Nub')
ax3.set_title(u'Distribución de nubes por horas en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Horas', fontproperties=prop_1)
ax3.set_ylim(0, 1350)
ax3.legend()

plt.subplots_adjust(wspace=0.3, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoNubaDespAnio2018.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/HistoNubaDespAnio2018.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##----------ENCONTRANDO LAS RADIACIONES CORRESPONDIENTES A LAS HORAS NUBOSAS----------##
df_FH_nuba_348 = pd.DataFrame()
df_FH_nuba_348 ['Fechas'] = Fecha_nuba_348
df_FH_nuba_348 ['Horas']  = Hora_nuba_348

df_FH_nuba_350 = pd.DataFrame()
df_FH_nuba_350 ['Fechas'] = Fecha_nuba_350
df_FH_nuba_350 ['Horas']  = Hora_nuba_350

df_FH_nuba_975 = pd.DataFrame()
df_FH_nuba_975 ['Fechas'] = Fecha_nuba_975
df_FH_nuba_975 ['Horas']  = Hora_nuba_975

df_FH_nuba_348_groupH = df_FH_nuba_348.groupby('Horas')['Fechas'].unique()
df_nuba_348_groupH = pd.DataFrame(df_FH_nuba_348_groupH[df_FH_nuba_348_groupH.apply(lambda x: len(x)>1)])   ##NO entiendo bien acá que se está haciendo

df_FH_nuba_350_groupH = df_FH_nuba_350.groupby('Horas')['Fechas'].unique()
df_nuba_350_groupH = pd.DataFrame(df_FH_nuba_350_groupH[df_FH_nuba_350_groupH.apply(lambda x: len(x)>1)])

df_FH_nuba_975_groupH = df_FH_nuba_975.groupby('Horas')['Fechas'].unique()
df_nuba_975_groupH = pd.DataFrame(df_FH_nuba_975_groupH[df_FH_nuba_975_groupH.apply(lambda x: len(x)>1)])

c = np.arange(6, 18, 1)

Sk_Nuba_stat_975 = {}
Sk_Nuba_pvalue_975 = {}
Composites_Nuba_975 = {}
for i in df_FH_nuba_975_groupH.index:
    H = str(i)
    if len(df_FH_nuba_975_groupH.loc[i]) == 1 :
        list = df_P975_h[df_P975_h.index.date == df_FH_nuba_975_groupH.loc[i][0]]['radiacion'].values
        list_sk_stat = np.ones(12)*np.nan
        list_sk_pvalue = np.ones(12)*np.nan
    elif len(df_FH_nuba_975_groupH.loc[i]) > 1 :
        temporal = pd.DataFrame()
        for j in range(len(df_FH_nuba_975_groupH.loc[i])):
            temporal = temporal.append(pd.DataFrame(df_P975_h[df_P975_h.index.date == df_FH_nuba_975_groupH.loc[i][j]]['radiacion']))
            stat_975 = []
            pvalue_975 = []
            for k in c:
                temporal_sk =  temporal[temporal.index.hour == k].radiacion.values
                Rad_sk = df_P975_h['radiacion'][df_P975_h.index.hour == k].values
                try:
                    SK = ks_2samp(temporal_sk,Rad_sk)
                    stat_975.append(SK[0])
                    pvalue_975.append(SK[1])
                except ValueError:
                    stat_975.append(np.nan)
                    pvalue_975.append(np.nan)
        temporal_CD =  temporal.groupby(by=[temporal.index.hour]).mean()
        list = [temporal_CD['radiacion'].values[w] for w in range(len(temporal_CD['radiacion'].values))]
        list_sk_stat = stat_975
        list_sk_pvalue = pvalue_975
    Composites_Nuba_975[H] = list
    Sk_Nuba_stat_975 [H] = list_sk_stat
    Sk_Nuba_pvalue_975 [H] = list_sk_pvalue
    del H

Comp_Nuba_975_df = pd.DataFrame(Composites_Nuba_975, index = c)
#Comp_Nuba_975_df = pd.DataFrame.from_dict(Composites_Nuba_975,orient='index').transpose()
Sk_Nuba_stat_975_df = pd.DataFrame(Sk_Nuba_stat_975, index = c)
Sk_Nuba_pvalue_975_df = pd.DataFrame(Sk_Nuba_pvalue_975, index = c)

Sk_Nuba_stat_350 = {}
Sk_Nuba_pvalue_350 = {}
Composites_Nuba_350 = {}
for i in df_FH_nuba_350_groupH.index:
    H = str(i)
    if len(df_FH_nuba_350_groupH.loc[i]) == 1 :
        list = df_P350_h[df_P350_h.index.date == df_FH_nuba_350_groupH.loc[i][0]]['radiacion'].values
        list_sk_stat = np.ones(12)*np.nan
        list_sk_pvalue = np.ones(12)*np.nan
    elif len(df_FH_nuba_350_groupH.loc[i]) > 1 :
        temporal = pd.DataFrame()
        for j in range(len(df_FH_nuba_350_groupH.loc[i])):
            temporal = temporal.append(pd.DataFrame(df_P350_h[df_P350_h.index.date == df_FH_nuba_350_groupH.loc[i][j]]['radiacion']))
            stat_350 = []
            pvalue_350 = []
            for k in c:
                temporal_sk =  temporal[temporal.index.hour == k].radiacion.values
                Rad_sk = df_P350_h['radiacion'][df_P350_h.index.hour == k].values
                try:
                    SK = ks_2samp(temporal_sk,Rad_sk)
                    stat_350.append(SK[0])
                    pvalue_350.append(SK[1])
                except ValueError:
                    stat_350.append(np.nan)
                    pvalue_350.append(np.nan)
        temporal_CD =  temporal.groupby(by=[temporal.index.hour]).mean()
        list = temporal_CD['radiacion'].values
        list_sk_stat = stat_350
        list_sk_pvalue = pvalue_350
    Composites_Nuba_350[H] = list
    Sk_Nuba_stat_350 [H] = list_sk_stat
    Sk_Nuba_pvalue_350 [H] = list_sk_pvalue
    del H
Comp_Nuba_350_df = pd.DataFrame(Composites_Nuba_350, index = c)
Sk_Nuba_stat_350_df = pd.DataFrame(Sk_Nuba_stat_350, index = c)
Sk_Nuba_pvalue_350_df = pd.DataFrame(Sk_Nuba_pvalue_350, index = c)

Sk_Nuba_stat_348 = {}
Sk_Nuba_pvalue_348 = {}
Composites_Nuba_348 = {}
for i in df_FH_nuba_348_groupH.index:
    H = str(i)
    if len(df_FH_nuba_348_groupH.loc[i]) == 1 :
        list = df_P348_h[df_P348_h.index.date == df_FH_nuba_348_groupH.loc[i][0]]['radiacion'].values
        list_sk_stat = np.ones(12)*np.nan
        list_sk_pvalue = np.ones(12)*np.nan
    elif len(df_FH_nuba_348_groupH.loc[i]) > 1 :
        temporal = pd.DataFrame()
        for j in range(len(df_FH_nuba_348_groupH.loc[i])):
            temporal = temporal.append(pd.DataFrame(df_P348_h[df_P348_h.index.date == df_FH_nuba_348_groupH.loc[i][j]]['radiacion']))
            stat_348 = []
            pvalue_348 = []
            for k in c:
                temporal_sk =  temporal[temporal.index.hour == k].radiacion.values
                Rad_sk = df_P348_h['radiacion'][df_P348_h.index.hour == k].values
                try:
                    SK = ks_2samp(temporal_sk,Rad_sk)
                    stat_348.append(SK[0])
                    pvalue_348.append(SK[1])
                except ValueError:
                    stat_348.append(np.nan)
                    pvalue_348.append(np.nan)
        temporal_CD =  temporal.groupby(by=[temporal.index.hour]).mean()
        list = temporal_CD['radiacion'].values
        list_sk_stat = stat_348
        list_sk_pvalue = pvalue_348
    Composites_Nuba_348[H] = list
    Sk_Nuba_stat_348 [H] = list_sk_stat
    Sk_Nuba_pvalue_348 [H] = list_sk_pvalue
    del H
Comp_Nuba_348_df = pd.DataFrame(Composites_Nuba_348, index = c)
Sk_Nuba_stat_348_df = pd.DataFrame(Sk_Nuba_stat_348, index = c)
Sk_Nuba_pvalue_348_df = pd.DataFrame(Sk_Nuba_pvalue_348, index = c)


##----------ENCONTRANDO LAS RADIACIONES CORRESPONDIENTES A LAS HORAS DESPEJADAS----------##
df_FH_desp_348 = pd.DataFrame()
df_FH_desp_348 ['Fechas'] = Fecha_desp_348
df_FH_desp_348 ['Horas']  = Hora_desp_348

df_FH_desp_350 = pd.DataFrame()
df_FH_desp_350 ['Fechas'] = Fecha_desp_350
df_FH_desp_350 ['Horas']  = Hora_desp_350

df_FH_desp_975 = pd.DataFrame()
df_FH_desp_975 ['Fechas'] = Fecha_desp_975
df_FH_desp_975 ['Horas']  = Hora_desp_975

df_FH_desp_348_groupH = df_FH_desp_348.groupby('Horas')['Fechas'].unique()
df_desp_348_groupH = pd.DataFrame(df_FH_desp_348_groupH[df_FH_desp_348_groupH.apply(lambda x: len(x)>1)])   ##NO entiendo bien acá que se está haciendo

df_FH_desp_350_groupH = df_FH_desp_350.groupby('Horas')['Fechas'].unique()
df_desp_350_groupH = pd.DataFrame(df_FH_desp_350_groupH[df_FH_desp_350_groupH.apply(lambda x: len(x)>1)])

df_FH_desp_975_groupH = df_FH_desp_975.groupby('Horas')['Fechas'].unique()
df_desp_975_groupH = pd.DataFrame(df_FH_desp_975_groupH[df_FH_desp_975_groupH.apply(lambda x: len(x)>1)])

Sk_Desp_stat_975 = {}
Sk_Desp_pvalue_975 = {}
Composites_Desp_975 = {}
for i in df_FH_desp_975_groupH.index:
    H = str(i)
    if len(df_FH_desp_975_groupH.loc[i]) == 1 :
        list = df_P975_h[df_P975_h.index.date == df_FH_desp_975_groupH.loc[i][0]]['radiacion'].values
        list_sk_stat = np.ones(12)*np.nan
        list_sk_pvalue = np.ones(12)*np.nan
    elif len(df_FH_desp_975_groupH.loc[i]) > 1 :
        temporal = pd.DataFrame()
        for j in range(len(df_FH_desp_975_groupH.loc[i])):
            temporal = temporal.append(pd.DataFrame(df_P975_h[df_P975_h.index.date == df_FH_desp_975_groupH.loc[i][j]]['radiacion']))
            stat_975 = []
            pvalue_975 = []
            for k in c:
                temporal_sk =  temporal[temporal.index.hour == k].radiacion.values
                Rad_sk = df_P975_h['radiacion'][df_P975_h.index.hour == k].values
                try:
                    SK = ks_2samp(temporal_sk,Rad_sk)
                    stat_975.append(SK[0])
                    pvalue_975.append(SK[1])
                except ValueError:
                    stat_975.append(np.nan)
                    pvalue_975.append(np.nan)
        temporal_CD =  temporal.groupby(by=[temporal.index.hour]).mean()
        list = temporal_CD['radiacion'].values
        list_sk_stat = stat_975
        list_sk_pvalue = pvalue_975
    Composites_Desp_975[H] = list
    Sk_Desp_stat_975 [H] = list_sk_stat
    Sk_Desp_pvalue_975 [H] = list_sk_pvalue
    del H
Comp_Desp_975_df = pd.DataFrame(Composites_Desp_975, index = c)
Sk_Desp_stat_975_df = pd.DataFrame(Sk_Desp_stat_975, index = c)
Sk_Desp_pvalue_975_df = pd.DataFrame(Sk_Desp_pvalue_975, index = c)

Sk_Desp_stat_350 = {}
Sk_Desp_pvalue_350 = {}
Composites_Desp_350 = {}
for i in df_FH_desp_350_groupH.index:
    H = str(i)
    if len(df_FH_desp_350_groupH.loc[i]) == 1 :
        list = df_P350_h[df_P350_h.index.date == df_FH_desp_350_groupH.loc[i][0]]['radiacion'].values
        list_sk_stat = np.ones(12)*np.nan
        list_sk_pvalue = np.ones(12)*np.nan
    elif len(df_FH_desp_350_groupH.loc[i]) > 1 :
        temporal = pd.DataFrame()
        for j in range(len(df_FH_desp_350_groupH.loc[i])):
            temporal = temporal.append(pd.DataFrame(df_P350_h[df_P350_h.index.date == df_FH_desp_350_groupH.loc[i][j]]['radiacion']))
            stat_350 = []
            pvalue_350 = []
            for k in c:
                temporal_sk =  temporal[temporal.index.hour == k].radiacion.values
                Rad_sk = df_P350_h['radiacion'][df_P350_h.index.hour == k].values
                try:
                    SK = ks_2samp(temporal_sk,Rad_sk)
                    stat_350.append(SK[0])
                    pvalue_350.append(SK[1])
                except ValueError:
                    stat_350.append(np.nan)
                    pvalue_350.append(np.nan)
        temporal_CD =  temporal.groupby(by=[temporal.index.hour]).mean()
        list = temporal_CD['radiacion'].values
        list_sk_stat = stat_350
        list_sk_pvalue = pvalue_350
    Composites_Desp_350[H] = list
    Sk_Desp_stat_350 [H] = list_sk_stat
    Sk_Desp_pvalue_350 [H] = list_sk_pvalue
    del H
Comp_Desp_350_df = pd.DataFrame(Composites_Desp_350, index = c)
Sk_Desp_stat_350_df = pd.DataFrame(Sk_Desp_stat_350, index = c)
Sk_Desp_pvalue_350_df = pd.DataFrame(Sk_Desp_pvalue_350, index = c)


Sk_Desp_stat_348 = {}
Sk_Desp_pvalue_348 = {}
Composites_Desp_348 = {}
for i in df_FH_desp_348_groupH.index:
    H = str(i)
    if len(df_FH_desp_348_groupH.loc[i]) == 1 :
        list = df_P348_h[df_P348_h.index.date == df_FH_desp_348_groupH.loc[i][0]]['radiacion'].values
        list_sk_stat = np.ones(12)*np.nan
        list_sk_pvalue = np.ones(12)*np.nan
    elif len(df_FH_desp_348_groupH.loc[i]) > 1 :
        temporal = pd.DataFrame()
        for j in range(len(df_FH_desp_348_groupH.loc[i])):
            temporal = temporal.append(pd.DataFrame(df_P348_h[df_P348_h.index.date == df_FH_desp_348_groupH.loc[i][j]]['radiacion']))
            stat_348 = []
            pvalue_348 = []
            for k in c:
                temporal_sk =  temporal[temporal.index.hour == k].radiacion.values
                Rad_sk = df_P348_h['radiacion'][df_P348_h.index.hour == k].values
                try:
                    SK = ks_2samp(temporal_sk,Rad_sk)
                    stat_348.append(SK[0])
                    pvalue_348.append(SK[1])
                except ValueError:
                    stat_348.append(np.nan)
                    pvalue_348.append(np.nan)
        temporal_CD =  temporal.groupby(by=[temporal.index.hour]).mean()
        list = temporal_CD['radiacion'].values
        list_sk_stat = stat_348
        list_sk_pvalue = pvalue_348
    Composites_Desp_348[H] = list
    Sk_Desp_stat_348 [H] = list_sk_stat
    Sk_Desp_pvalue_348 [H] = list_sk_pvalue
    del H
Comp_Desp_348_df = pd.DataFrame(Composites_Desp_348, index = c)
Sk_Desp_stat_348_df = pd.DataFrame(Sk_Desp_stat_348, index = c)
Sk_Desp_pvalue_348_df = pd.DataFrame(Sk_Desp_pvalue_348, index = c)

##-------------------ESTANDARIZANDO LAS FORMAS DE LOS  DATAFRAMES A LAS HORAS CASO DESPEJADO----------------##
Comp_Desp_348_df = Comp_Desp_348_df[(Comp_Desp_348_df.index >= 6)&(Comp_Desp_348_df.index <18)]
Comp_Desp_350_df = Comp_Desp_350_df[(Comp_Desp_350_df.index >= 6)&(Comp_Desp_350_df.index <18)]
Comp_Desp_975_df = Comp_Desp_975_df[(Comp_Desp_975_df.index >= 6)&(Comp_Desp_975_df.index <18)]

s = [str(i) for i in Comp_Nuba_348_df.index.values]

ListNan = np.empty((1,len(Comp_Desp_348_df)))
ListNan [:] = np.nan

def convert(set):
     return [*set, ]

a_Desp_348 = convert(set(s).difference(Comp_Desp_348_df.columns.values))
a_Desp_348.sort(key=int)
if len(a_Desp_348) > 0:
    idx = [i for i,x in enumerate(s) if x in a_Desp_348]
    for i in range(len(a_Desp_348)):
        Comp_Desp_348_df.insert(loc = idx[i], column = a_Desp_348[i], value=ListNan[0])
    del idx

a_Desp_350 = convert(set(s).difference(Comp_Desp_350_df.columns.values))
a_Desp_350.sort(key=int)
if len(a_Desp_350) > 0:
    idx = [i for i,x in enumerate(s) if x in a_Desp_350]
    for i in range(len(a_Desp_350)):
        Comp_Desp_350_df.insert(loc = idx[i], column = a_Desp_350[i], value=ListNan[0])
    del idx

a_Desp_975 = convert(set(s).difference(Comp_Desp_975_df.columns.values))
a_Desp_975.sort(key=int)
if len(a_Desp_975) > 0:
    idx = [i for i,x in enumerate(s) if x in a_Desp_975]
    for i in range(len(a_Desp_975)):
        Comp_Desp_975_df.insert(loc = idx[i], column = a_Desp_975[i], value=ListNan[0])
    del idx
s = [str(i) for i in Comp_Desp_348_df.index.values]
Comp_Desp_348_df = Comp_Desp_348_df[s]
Comp_Desp_350_df = Comp_Desp_350_df[s]
Comp_Desp_975_df = Comp_Desp_975_df[s]

##-------------------ESTANDARIZANDO LAS FORMAS DE LOS  DATAFRAMES A LAS HORAS CASO NUBADO----------------##
Comp_Nuba_348_df = Comp_Nuba_348_df[(Comp_Nuba_348_df.index >= 6)&(Comp_Nuba_348_df.index <18)]
Comp_Nuba_350_df = Comp_Nuba_350_df[(Comp_Nuba_350_df.index >= 6)&(Comp_Nuba_350_df.index <18)]
Comp_Nuba_975_df = Comp_Nuba_975_df[(Comp_Nuba_975_df.index >= 6)&(Comp_Nuba_975_df.index <18)]

s = [str(i) for i in Comp_Nuba_348_df.index.values]

ListNan = np.empty((1,len(Comp_Nuba_348_df)))
ListNan [:] = np.nan

def convert(set):
     return [*set, ]

a_Nuba_348 = convert(set(s).difference(Comp_Nuba_348_df.columns.values))
a_Nuba_348.sort(key=int)
if len(a_Nuba_348) > 0:
    idx = [i for i,x in enumerate(s) if x in a_Nuba_348]
    for i in range(len(a_Nuba_348)):
        Comp_Nuba_348_df.insert(loc = idx[i], column = a_Nuba_348[i], value=ListNan[0])
    del idx

a_Nuba_350 = convert(set(s).difference(Comp_Nuba_350_df.columns.values))
a_Nuba_350.sort(key=int)
if len(a_Nuba_350) > 0:
    idx = [i for i,x in enumerate(s) if x in a_Nuba_350]
    for i in range(len(a_Nuba_350)):
        Comp_Nuba_350_df.insert(loc = idx[i], column = a_Nuba_350[i], value=ListNan[0])
    del idx

a_Nuba_975 = convert(set(s).difference(Comp_Nuba_975_df.columns.values))
a_Nuba_975.sort(key=int)
if len(a_Nuba_975) > 0:
    idx = [i for i,x in enumerate(s) if x in a_Nuba_975]
    for i in range(len(a_Nuba_975)):
        Comp_Nuba_975_df.insert(loc = idx[i], column = a_Nuba_975[i], value=ListNan[0])
    del idx

Comp_Nuba_348_df = Comp_Nuba_348_df[s]
Comp_Nuba_350_df = Comp_Nuba_350_df[s]
Comp_Nuba_975_df = Comp_Nuba_975_df[s]

##-------------------CONTEO  DE LA CANTIDAD DE DÍAS CONSIDERADOS NUBADOS Y DESPEJADOS----------------##
Cant_Days_Nuba_348 = []
for i in range(len(s)):
    try:
        Cant_Days_Nuba_348.append(len(df_FH_nuba_348_groupH[df_FH_nuba_348_groupH .index == int(s[i])].values[0]))
    except IndexError:
        Cant_Days_Nuba_348.append(0)

Cant_Days_Nuba_350 = []
for i in range(len(s)):
    try:
        Cant_Days_Nuba_350.append(len(df_FH_nuba_350_groupH[df_FH_nuba_350_groupH .index == int(s[i])].values[0]))
    except IndexError:
        Cant_Days_Nuba_350.append(0)

Cant_Days_Nuba_975 = []
for i in range(len(s)):
    try:
        Cant_Days_Nuba_975.append(len(df_FH_nuba_975_groupH[df_FH_nuba_975_groupH .index == int(s[i])].values[0]))
    except IndexError:
        Cant_Days_Nuba_975.append(0)

Cant_Days_Desp_348 = []
for i in range(len(s)):
    try:
        Cant_Days_Desp_348.append(len(df_FH_desp_348_groupH[df_FH_desp_348_groupH .index == int(s[i])].values[0]))
    except IndexError:
        Cant_Days_Desp_348.append(0)

Cant_Days_Desp_350 = []
for i in range(len(s)):
    try:
        Cant_Days_Desp_350.append(len(df_FH_desp_350_groupH[df_FH_desp_350_groupH .index == int(s[i])].values[0]))
    except IndexError:
        Cant_Days_Desp_350.append(0)

Cant_Days_Desp_975 = []
for i in range(len(s)):
    try:
        Cant_Days_Desp_975.append(len(df_FH_desp_975_groupH[df_FH_desp_975_groupH .index == int(s[i])].values[0]))
    except IndexError:
        Cant_Days_Desp_975.append(0)



##-------------------AJUSTADO LOS DATAFRAMES DE LOS ESTADÍSTICOS Y DEL VALOR P----------------##

for i in range(len(c)):
    if str(c[i]) not in Sk_Desp_pvalue_975_df.columns:
        Sk_Desp_pvalue_975_df.insert(int(c[i]-6), str(c[i]), np.ones(12)*np.nan)
    if str(c[i]) not in Sk_Desp_pvalue_350_df.columns:
        Sk_Desp_pvalue_350_df.insert(int(c[i]-6), str(c[i]), np.ones(12)*np.nan)
    if str(c[i]) not in Sk_Desp_pvalue_348_df.columns:
        Sk_Desp_pvalue_348_df.insert(int(c[i]-6), str(c[i]), np.ones(12)*np.nan)
    if str(c[i]) not in Sk_Nuba_pvalue_350_df.columns:
        Sk_Nuba_pvalue_350_df.insert(int(c[i]-6), str(c[i]), np.ones(12)*np.nan)
    if str(c[i]) not in Sk_Nuba_pvalue_348_df.columns:
        Sk_Nuba_pvalue_348_df.insert(int(c[i]-6), str(c[i]), np.ones(12)*np.nan)
    if str(c[i]) not in Sk_Nuba_pvalue_975_df.columns:
        Sk_Nuba_pvalue_975_df.insert(int(c[i]-6), str(c[i]), np.ones(12)*np.nan)


Significancia = 0.05

for i in c:
    Sk_Desp_pvalue_348_df.loc[Sk_Desp_pvalue_348_df[str(i)]< Significancia, str(i)] = 100
    Sk_Desp_pvalue_350_df.loc[Sk_Desp_pvalue_350_df[str(i)]< Significancia, str(i)] = 100
    Sk_Desp_pvalue_975_df.loc[Sk_Desp_pvalue_975_df[str(i)]< Significancia, str(i)] = 100
    Sk_Nuba_pvalue_348_df.loc[Sk_Nuba_pvalue_348_df[str(i)]< Significancia, str(i)] = 100
    Sk_Nuba_pvalue_350_df.loc[Sk_Nuba_pvalue_350_df[str(i)]< Significancia, str(i)] = 100
    Sk_Nuba_pvalue_975_df.loc[Sk_Nuba_pvalue_975_df[str(i)]< Significancia, str(i)] = 100

row_Desp_348 = []
col_Desp_348 = []
for row in range(Sk_Desp_pvalue_348_df.shape[0]):
         for col in range(Sk_Desp_pvalue_348_df.shape[1]):
             if Sk_Desp_pvalue_348_df.get_value((row+6),str(col+6)) == 100:
                 row_Desp_348.append(row)
                 col_Desp_348.append(col)
                 #print(row+6, col+6)

row_Desp_350 = []
col_Desp_350 = []
for row in range(Sk_Desp_pvalue_350_df.shape[0]):
         for col in range(Sk_Desp_pvalue_350_df.shape[1]):
             if Sk_Desp_pvalue_350_df.get_value((row+6),str(col+6)) == 100:
                 row_Desp_350.append(row)
                 col_Desp_350.append(col)


row_Desp_975 = []
col_Desp_975 = []
for row in range(Sk_Desp_pvalue_975_df.shape[0]):
         for col in range(Sk_Desp_pvalue_975_df.shape[1]):
             if Sk_Desp_pvalue_975_df.get_value((row+6),str(col+6)) == 100:
                 row_Desp_975.append(row)
                 col_Desp_975.append(col)

row_Nuba_348 = []
col_Nuba_348 = []
for row in range(Sk_Nuba_pvalue_348_df.shape[0]):
         for col in range(Sk_Nuba_pvalue_348_df.shape[1]):
             if Sk_Nuba_pvalue_348_df.get_value((row+6),str(col+6)) == 100:
                 row_Nuba_348.append(row)
                 col_Nuba_348.append(col)
                 #print(row+6, col+6)

row_Nuba_350 = []
col_Nuba_350 = []
for row in range(Sk_Nuba_pvalue_350_df.shape[0]):
         for col in range(Sk_Nuba_pvalue_350_df.shape[1]):
             if Sk_Nuba_pvalue_350_df.get_value((row+6),str(col+6)) == 100:
                 row_Nuba_350.append(row)
                 col_Nuba_350.append(col)


row_Nuba_975 = []
col_Nuba_975 = []
for row in range(Sk_Nuba_pvalue_975_df.shape[0]):
         for col in range(Sk_Nuba_pvalue_975_df.shape[1]):
             if Sk_Nuba_pvalue_975_df.get_value((row+6),str(col+6)) == 100:
                 row_Nuba_975.append(row)
                 col_Nuba_975.append(col)

##-------------------GRÁFICO DEL COMPOSITE NUBADO DE LA RADIACIÓN PARA CADA PUNTO Y LA CANT DE DÍAS----------------##
s_f = [int(s[i]) for i in range(len(s))]

plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
mapa = ax1.imshow(Comp_Nuba_348_df, interpolation = 'none', cmap = 'Spectral_r')
ax1.set_yticks(range(0,12), minor=False)
ax1.set_yticklabels(s, minor=False)
ax1.set_xticks(range(0,12), minor=False)
ax1.set_xticklabels(s, minor=False, rotation = 20)
ax1.set_xlabel('Hora del caso', fontsize=10, fontproperties = prop_1)
ax1.set_ylabel('Hora en el CD de radiación', fontsize=10, fontproperties = prop_1)
ax1.scatter(range(0,12),range(0,12), marker='x', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax1.set_title(' x =  Horas nubadas en JV', loc = 'center', fontsize=9)

ax2=fig.add_subplot(2,3,2)
mapa = ax2.imshow(Comp_Nuba_350_df, interpolation = 'none', cmap = 'Spectral_r')
ax2.set_yticks(range(0,12), minor=False)
ax2.set_yticklabels(s, minor=False)
ax2.set_xticks(range(0,12), minor=False)
ax2.set_xticklabels(s, minor=False, rotation = 20)
ax2.set_xlabel('Hora del caso', fontsize=10, fontproperties = prop_1)
ax2.set_ylabel('Hora en el CD de radiación', fontsize=10, fontproperties = prop_1)
ax2.scatter(range(0,12),range(0,12), marker='x', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax2.set_title(' x = Horas nubadas en CI', loc = 'center', fontsize=9)

ax3 = fig.add_subplot(2,3,3)
mapa = ax3.imshow(Comp_Nuba_975_df, interpolation = 'none', cmap = 'Spectral_r')
ax3.set_yticks(range(0,12), minor=False)
ax3.set_yticklabels(s, minor=False)
ax3.set_xticks(range(0,12), minor=False)
ax3.set_xticklabels(s, minor=False, rotation = 20)
ax3.set_xlabel('Hora del caso', fontsize=10, fontproperties = prop_1)
ax3.set_ylabel('Hora en el CD de radiación', fontsize=10, fontproperties = prop_1)
ax3.scatter(range(0,12),range(0,12), marker='x', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax3.set_title(' x = Horas nubadas en TS', loc = 'center', fontsize=9)

cbar_ax = fig.add_axes([0.11, 0.93, 0.78, 0.008])
cbar = fig.colorbar(mapa, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Intensidad de la radiación  $[W/m^{2}]$", fontsize=8, fontproperties=prop)

ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.bar(np.arange(len(s)), Cant_Days_Nuba_348, color='orange', align='center', alpha=0.5)
ax4.set_xlabel(u'Hora', fontproperties = prop_1)
ax4.set_ylabel(r"Cantidad de días", fontproperties = prop_1)
ax4.set_xticks(range(0,12), minor=False)
ax4.set_xticklabels(s, minor=False, rotation = 20)
ax4.set_title(u' Cantidad de días en JV', loc = 'center', fontsize=9)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.bar(np.arange(len(s)), Cant_Days_Nuba_350, color='orange', align='center', alpha=0.5)
ax5.set_xlabel(u'Hora', fontproperties = prop_1)
ax5.set_ylabel(r"Cantidad de días", fontproperties = prop_1)
ax5.set_xticks(range(0,12), minor=False)
ax5.set_xticklabels(s, minor=False, rotation = 20)
ax5.set_title(u' Cantidad de días en CI', loc = 'center', fontsize=9)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.bar(np.arange(len(s)), Cant_Days_Nuba_975, color='orange', align='center', alpha=0.5)
ax6.set_xlabel(u'Hora', fontproperties = prop_1)
ax6.set_ylabel(r"Cantidad de días", fontproperties = prop_1)
ax6.set_xticks(range(0,12), minor=False)
ax6.set_xticklabels(s, minor=False, rotation = 20)
ax6.set_title(u' Cantidad de días en TS', loc = 'center', fontsize=9)

plt.subplots_adjust(wspace=0.3, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Composites_Nuba_Cant_Dias2018.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Composites_Nuba_Cant_Dias2018.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##-------------------GRÁFICO DEL COMPOSITE DESPEJADO DE LA RADIACIÓN PARA CADA PUNTO Y LA CANT DE DÍAS----------------##
plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
mapa = ax1.imshow(Comp_Desp_348_df, interpolation = 'none', cmap = 'Spectral_r')
ax1.set_yticks(range(0,12), minor=False)
ax1.set_yticklabels(s, minor=False)
ax1.set_xticks(range(0,12), minor=False)
ax1.set_xticklabels(s, minor=False, rotation = 20)
ax1.set_xlabel('Hora del caso', fontsize=10, fontproperties = prop_1)
ax1.set_ylabel('Hora en el CD de radiación', fontsize=10, fontproperties = prop_1)
ax1.scatter(range(0,12),range(0,12), marker='x', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax1.set_title(' x =  Horas despejadas en JV', loc = 'center', fontsize=9)

ax2=fig.add_subplot(2,3,2)
mapa = ax2.imshow(Comp_Desp_350_df, interpolation = 'none', cmap = 'Spectral_r')
ax2.set_yticks(range(0,12), minor=False)
ax2.set_yticklabels(s, minor=False)
ax2.set_xticks(range(0,12), minor=False)
ax2.set_xticklabels(s, minor=False, rotation = 20)
ax2.set_xlabel('Hora del caso', fontsize=10, fontproperties = prop_1)
ax2.set_ylabel('Hora en el CD de radiación', fontsize=10, fontproperties = prop_1)
ax2.scatter(range(0,12),range(0,12), marker='x', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax2.set_title(' x = Horas despejadas en CI', loc = 'center', fontsize=9)

ax3 = fig.add_subplot(2,3,3)
mapa = ax3.imshow(Comp_Desp_975_df, interpolation = 'none', cmap = 'Spectral_r')
ax3.set_yticks(range(0,12), minor=False)
ax3.set_yticklabels(s, minor=False)
ax3.set_xticks(range(0,12), minor=False)
ax3.set_xticklabels(s, minor=False, rotation = 20)
ax3.set_xlabel('Hora del caso', fontsize=10, fontproperties = prop_1)
ax3.set_ylabel('Hora en el CD de radiación', fontsize=10, fontproperties = prop_1)
ax3.scatter(range(0,12),range(0,12), marker='x', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax3.set_title(' x = Horas despejadas en TS', loc = 'center', fontsize=9)

cbar_ax = fig.add_axes([0.11, 0.93, 0.78, 0.008])
cbar = fig.colorbar(mapa, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Intensidad de la radiación  $[W/m^{2}]$", fontsize=8, fontproperties=prop)

ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.bar(np.arange(len(s)), Cant_Days_Desp_348, color='orange', align='center', alpha=0.5)
ax4.set_xlabel(u'Hora', fontproperties = prop_1)
ax4.set_ylabel(r"Cantidad de días", fontproperties = prop_1)
ax4.set_xticks(range(0,12), minor=False)
ax4.set_xticklabels(s, minor=False, rotation = 20)
ax4.set_title(u' Cantidad de días en JV', loc = 'center', fontsize=9)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.bar(np.arange(len(s)), Cant_Days_Desp_350, color='orange', align='center', alpha=0.5)
ax5.set_xlabel(u'Hora', fontproperties = prop_1)
ax5.set_ylabel(r"Cantidad de días", fontproperties = prop_1)
ax5.set_xticks(range(0,12), minor=False)
ax5.set_xticklabels(s, minor=False, rotation = 20)
ax5.set_title(u' Cantidad de días en CI', loc = 'center', fontsize=9)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.bar(np.arange(len(s)), Cant_Days_Desp_975, color='orange', align='center', alpha=0.5)
ax6.set_xlabel(u'Hora', fontproperties = prop_1)
ax6.set_ylabel(r"Cantidad de días", fontproperties = prop_1)
ax6.set_xticks(range(0,12), minor=False)
ax6.set_xticklabels(s, minor=False, rotation = 20)
ax6.set_title(u' Cantidad de días en TS', loc = 'center', fontsize=9)

#plt.title(u'Composites caso nubado', fontproperties=prop, fontsize = 8)
plt.subplots_adjust(wspace=0.3, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Composites_Desp_Cant_Dias2018.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Composites_Desp_Cant_Dias2018.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


##--------------------------TOTAL DE DÍAS DE REGISTRO Y FRECUENCIA DE LA CONDICIÓN---------------------##
Total_dias_348 =  len(Rad_df_348.groupby(pd.Grouper(freq="D")).mean())
Total_dias_350 =  len(Rad_df_350.groupby(pd.Grouper(freq="D")).mean())
Total_dias_975 =  len(Rad_df_975.groupby(pd.Grouper(freq="D")).mean())


Porc_Days_Desp_348 = (np.array(Cant_Days_Desp_348)/Total_dias_348)*100
Porc_Days_Desp_350 = (np.array(Cant_Days_Desp_350)/Total_dias_350)*100
Porc_Days_Desp_975 = (np.array(Cant_Days_Desp_975)/Total_dias_975)*100

Porc_Days_Nuba_348 = (np.array(Cant_Days_Nuba_348)/Total_dias_348)*100
Porc_Days_Nuba_350 = (np.array(Cant_Days_Nuba_350)/Total_dias_350)*100
Porc_Days_Nuba_975 = (np.array(Cant_Days_Nuba_975)/Total_dias_975)*100


print('Total de dias JV: ' + str(Total_dias_348))
print('Total de dias CI: ' + str(Total_dias_350))
print('Total de dias TV: ' + str(Total_dias_975))

##-------------------CD EN BOX PLOT HORARIO PARA CADA PUNTO----------------##
DF_348_horas = {}
for i in range(1, 13):
    A = Rad_df_348_h[Rad_df_348_h.index.hour == (i + 5)]['Radiacias']
    H = A.index.hour[0]
    print(H)
    DF_348_horas[H] = A.values
    del H, A
DF_348_horas = pd.DataFrame.from_dict(DF_348_horas,orient='index').transpose()
#DF_348_horas = pd.DataFrame(DF_348_horas)

DF_350_horas = {}
for i in range(1, 13):
    A = Rad_df_350_h[Rad_df_350_h.index.hour == (i + 5)]['Radiacias']
    H = A.index.hour[0]
    print(H)
    DF_350_horas[H] = A
    del H, A
#DF_350_horas = pd.DataFrame(DF_350_horas)
DF_350_horas = pd.DataFrame.from_dict(DF_350_horas,orient='index').transpose()

DF_975_horas = {}
for i in range(1, 13):
    A = Rad_df_975_h[Rad_df_975_h.index.hour == (i + 5)]['Radiacias']
    H = A.index.hour[0]
    print(H)
    DF_975_horas[H] = A
    del H, A
#DF_975_horas = pd.DataFrame(DF_975_horas)
DF_975_horas = pd.DataFrame.from_dict(DF_975_horas,orient='index').transpose()

fig = plt.figure(figsize=(12,5))
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
DF_348_horas.boxplot(grid=False)
#Umbrales_line1y = [ax1.axhline(y=xc, color='k', linestyle='--') for xc in Umbrales_348]
ax1.set_title(u'Distribución de FR por horas en JV', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Factor Reflectancia[%]', fontproperties=prop_1)
ax1.set_xlabel(u'Horas', fontproperties=prop_1)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
DF_350_horas.boxplot(grid=False)
#Umbrales_line2y = [ax2.axhline(y=xc, color='k', linestyle='--') for xc in Umbrales_350]
ax2.set_title(u'Distribución de FR por horas en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Factor Reflectancia[%]', fontproperties=prop_1)
ax2.set_xlabel(u'Horas', fontproperties=prop_1)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
DF_975_horas.boxplot(grid=False)
#Umbrales_line3y = [ax3.axhline(y=xc, color='k', linestyle='--') for xc in Umbrales_975]
ax3.set_title(u'Distribución de FR por horas en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Factor Reflectancia[%]', fontproperties=prop_1)
ax3.set_xlabel(u'Horas', fontproperties=prop_1)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/FRBoxPlotHora.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/FRBoxPlotHora.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##-------------------ANOMALÍAS DE LOS COMPOSITES DE LA RADIACIÓN EN LOS DÍAS NUBADOS Y DESPEJADOS----------------##

new_idx = np.arange(6, 18, 1)

df_CDRad_348  = df_P348_h.radiacion.groupby(by=[df_P348_h.index.hour]).mean()
df_CDRad_348  = df_CDRad_348.reindex(new_idx)
df_STDRad_348  = df_P348_h.radiacion.groupby(by=[df_P348_h.index.hour]).std()
df_STDRad_348  = df_STDRad_348.reindex(new_idx)

df_CDRad_350  = df_P350_h.radiacion.groupby(by=[df_P350_h.index.hour]).mean()
df_CDRad_350  = df_CDRad_350.reindex(new_idx)
df_STDRad_350  = df_P350_h.radiacion.groupby(by=[df_P350_h.index.hour]).std()
df_STDRad_350  = df_STDRad_350.reindex(new_idx)

df_CDRad_975  = df_P975_h.radiacion.groupby(by=[df_P975_h.index.hour]).mean()
df_CDRad_975  = df_CDRad_975.reindex(new_idx)
df_STDRad_975  = df_P975_h.radiacion.groupby(by=[df_P975_h.index.hour]).std()
df_STDRad_975  = df_STDRad_975.reindex(new_idx)

Comp_Desp_348_anomal = (Comp_Desp_348_df.sub(df_CDRad_348, axis='index'))
Comp_Desp_350_anomal = (Comp_Desp_350_df.sub(df_CDRad_350, axis='index'))
Comp_Desp_975_anomal = (Comp_Desp_975_df.sub(df_CDRad_975, axis='index'))

Comp_Nuba_348_anomal = (Comp_Nuba_348_df.sub(df_CDRad_348, axis='index'))
Comp_Nuba_350_anomal = (Comp_Nuba_350_df.sub(df_CDRad_350, axis='index'))
Comp_Nuba_975_anomal = (Comp_Nuba_975_df.sub(df_CDRad_975, axis='index'))

##-------------------CONFIGURACIÓN DE LA COLORBAR DE LAS ANOMALÍAS----------------##

class MidpointNormalize(colors.Normalize):
	"""
	Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)

	e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
	"""
	def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
		self.midpoint = midpoint
		colors.Normalize.__init__(self, vmin, vmax, clip)

	def __call__(self, value, clip=None):
		# I'm ignoring masked values and all kinds of edge cases to make a
		# simple eaxmple...
		x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
		return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

cmap = matplotlib.cm.RdBu_r

##-------------------GRÁFICO DE LAS ANOMALÍAS DEL COMPOSITE DESPEJADO DE LA RADIACIÓN PARA CADA PUNTO ----------------##
"""
Se deben verificar los valores de elev_min y elev_max de acuerdo al set de datos de las anomalías
"""
elev_min = min(np.nanmin(Comp_Desp_348_anomal.values)  , np.nanmin(Comp_Desp_350_anomal.values), np.nanmin(Comp_Desp_975_anomal.values))-1
elev_max = max(np.nanmax(Comp_Desp_348_anomal.values)  , np.nanmax(Comp_Desp_350_anomal.values), np.nanmax(Comp_Desp_975_anomal.values))+1
mid_val = 0

plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
mapa = ax1.imshow(Comp_Desp_350_anomal, interpolation = 'none', cmap=cmap, clim=(elev_min, elev_max), norm=MidpointNormalize(midpoint=mid_val,vmin=elev_min, vmax=elev_max))
#cont = ax1.contour(Sk_Desp_pvalue_350_df, levels=[99, 101], linewidths=0.5)
#ax1.clabel(cont, fmt = '%.2f', colors = 'k', fontsize=8)
ax1.set_yticks(range(0,12), minor=False)
ax1.set_yticklabels(s, minor=False)
ax1.set_xticks(range(0,12), minor=False)
ax1.set_xticklabels(s, minor=False, rotation = 20)
ax1.set_xlabel('Horas despejadas', fontsize=10, fontproperties = prop_1)
ax1.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax1.scatter(col_Desp_350,row_Desp_350, marker='o', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax1.set_title(' x =  Horas despejadas en el Oeste', loc = 'center', fontsize=9)

ax2=fig.add_subplot(2,3,2)
mapa = ax2.imshow(Comp_Desp_975_anomal, interpolation = 'none', cmap=cmap, clim=(elev_min, elev_max), norm=MidpointNormalize(midpoint=mid_val,vmin=elev_min, vmax=elev_max))
#cont = ax2.contour(Sk_Desp_pvalue_975_df, levels=[99, 101], linewidths=0.5)
#ax2.clabel(cont, fmt = '%.2f', colors = 'k', fontsize=8)
ax2.set_yticks(range(0,12), minor=False)
ax2.set_yticklabels(s, minor=False)
ax2.set_xticks(range(0,12), minor=False)
ax2.set_xticklabels(s, minor=False, rotation = 20)
ax2.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax2.set_xlabel('Horas despejadas', fontsize=10, fontproperties = prop_1)
ax2.scatter(col_Desp_975,row_Desp_975, marker='o', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax2.set_title(' x = Horas despejadas en el Centro-Oeste', loc = 'center', fontsize=9)

ax3 = fig.add_subplot(2,3,3)
mapa = ax3.imshow(Comp_Desp_348_anomal, interpolation = 'none', cmap=cmap, clim=(elev_min, elev_max), norm=MidpointNormalize(midpoint=mid_val,vmin=elev_min, vmax=elev_max))
#cont = ax3.contour(Sk_Desp_pvalue_348_df, levels=[99, 101], linewidths=0.5)
#ax3.clabel(cont, fmt = '%.2f', colors = 'k', fontsize=8)
ax3.set_yticks(range(0,12), minor=False)
ax3.set_yticklabels(s, minor=False)
ax3.set_xticks(range(0,12), minor=False)
ax3.set_xticklabels(s, minor=False, rotation = 20)
ax3.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax3.set_xlabel('Horas despejadas', fontsize=10, fontproperties = prop_1)
ax3.scatter(col_Desp_348,row_Desp_348, marker='o', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax3.set_title(' x = Horas despejadas en el Este', loc = 'center', fontsize=9)

#cbar_ax = fig.add_axes([0.11, 0.28, 0.78, 0.008])
cbar_ax = fig.add_axes([0.11, 0.93, 0.78, 0.008])
cbar = fig.colorbar(mapa, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Anomalías de la radiación en el caso despejado $[W/m^{2}]$", fontsize=8, fontproperties=prop)

ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
#ax4.bar(np.arange(len(s)), Cant_Days_Desp_348, color='orange', align='center', alpha=0.5)
ax4.plot(s, Porc_Days_Desp_350, color = '#8ABB73', lw=1.5)
ax4.scatter(s, Porc_Days_Desp_350, marker='.', color = '#8ABB73', s=30)
ax4.set_xlabel(u'Horas despejadas', fontproperties = prop_1)
ax4.set_ylabel(u"Frecuencia de días [%]", fontproperties = prop_1)
ax4.set_xticks(range(0, 12), minor=False)
ax4.set_xticklabels(s, minor=False, rotation = 20)
ax4.set_ylim(0, 100)
ax4.set_title(u'Frecuencia de días en el Oeste', loc = 'center', fontsize=9)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
#ax5.bar(np.arange(len(s)), Cant_Days_Desp_350, color='orange', align='center', alpha=0.5)
ax5.set_xlabel(u'Horas despejadas', fontproperties = prop_1)
ax5.set_ylabel(u"Frecuencia de días [%]", fontproperties = prop_1)
ax5.plot(s, Porc_Days_Desp_975, color = '#8ABB73', lw=1.5)
ax5.scatter(s, Porc_Days_Desp_975, marker='.', color = '#8ABB73', s=30)
ax5.set_xticks(range(0, 12), minor=False)
ax5.set_xticklabels(s, minor=False, rotation = 20)
ax5.set_ylim(0, 100)
ax5.set_title(u'Frecuencia de días en el Centro-Oeste', loc = 'center', fontsize=9)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
#ax6.bar(np.arange(len(s)), Cant_Days_Desp_975, color='orange', align='center', alpha=0.5)
ax6.plot(s, Porc_Days_Desp_348, color = '#8ABB73', lw=1.5)
ax6.scatter(s, Porc_Days_Desp_348, marker='.', color = '#8ABB73', s=30)
ax6.set_xlabel(u'Horas despejadas', fontproperties = prop_1)
ax6.set_ylabel(u"Frecuencia de días [%]", fontproperties = prop_1)
ax6.set_xticks(range(0, 12), minor=False)
ax6.set_xticklabels(s, minor=False, rotation = 20)
ax6.set_ylim(0, 100)
ax6.set_title(u'Frecuencia de días en el Este', loc = 'center', fontsize=9)

plt.subplots_adjust(wspace=0.3, hspace = 0.3)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/AnomalComposites_Desp_Cant_Dias.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/AnomalComposites_Desp_Cant_Dias.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##-------------------GRÁFICO DE LAS ANOMALÍAS DEL COMPOSITE NUBADO DE LA RADIACIÓN PARA CADA PUNTO ----------------##
"""
Se deben verificar los valores de elev_min y elev_max de acuerdo al set de datos de las anomalías
"""
elev_min = min(np.nanmin(Comp_Nuba_348_anomal.values)  , np.nanmin(Comp_Nuba_350_anomal.values), np.nanmin(Comp_Nuba_975_anomal.values))-1
elev_max = max(np.nanmax(Comp_Nuba_348_anomal.values)  , np.nanmax(Comp_Nuba_350_anomal.values), np.nanmax(Comp_Nuba_975_anomal.values))+1
mid_val = 0

plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
mapa = ax1.imshow(Comp_Nuba_350_anomal, interpolation = 'none', cmap=cmap, clim=(elev_min, elev_max), norm=MidpointNormalize(midpoint=mid_val,vmin=elev_min, vmax=elev_max))
#cont = ax1.contour(Sk_Nuba_pvalue_350_df, levels=[99, 101], linewidths=0.5)
ax1.set_yticks(range(0,12), minor=False)
ax1.set_yticklabels(s, minor=False)
ax1.set_xticks(range(0,12), minor=False)
ax1.set_xticklabels(s, minor=False, rotation = 20)
ax1.set_xlabel('Horas nubladas', fontsize=10, fontproperties = prop_1)
ax1.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax1.scatter(col_Nuba_350,row_Nuba_350, marker='o', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax1.set_title('x =  Horas nubladas en el Oeste', loc = 'center', fontsize=9)

ax2=fig.add_subplot(2,3,2)
mapa = ax2.imshow(Comp_Nuba_975_anomal, interpolation = 'none', cmap=cmap, clim=(elev_min, elev_max), norm=MidpointNormalize(midpoint=mid_val,vmin=elev_min, vmax=elev_max))
#cont = ax2.contour(Sk_Nuba_pvalue_975_df, levels=[99, 101], linewidths=0.5)
#ax2.clabel(cont, fmt = '%.2f', colors = 'k', fontsize=8)
ax2.set_yticks(range(0,12), minor=False)
ax2.set_yticklabels(s, minor=False)
ax2.set_xticks(range(0,12), minor=False)
ax2.set_xticklabels(s, minor=False, rotation = 20)
ax2.set_xlabel('Horas nubladas', fontsize=10, fontproperties = prop_1)
ax2.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax2.scatter(col_Nuba_975,row_Nuba_975, marker='o', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax2.set_title('x =  Horas nubladas en el Centro-Oeste', loc = 'center', fontsize=9)

ax3 = fig.add_subplot(2,3,3)
mapa = ax3.imshow(Comp_Nuba_348_anomal, interpolation = 'none', cmap=cmap, clim=(elev_min, elev_max), norm=MidpointNormalize(midpoint=mid_val,vmin=elev_min, vmax=elev_max))
#cont = ax3.contour(Sk_Nuba_pvalue_348_df, levels=[99, 101], linewidths=0.5)
#ax3.clabel(cont, fmt = '%.2f', colors = 'k', fontsize=8)
ax3.set_yticks(range(0,12), minor=False)
ax3.set_yticklabels(s, minor=False)
ax3.set_xticks(range(0,12), minor=False)
ax3.set_xticklabels(s, minor=False, rotation = 20)
ax3.set_xlabel('Horas nubladas', fontsize=10, fontproperties = prop_1)
ax3.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax3.scatter(col_Nuba_348,row_Nuba_348, marker='o', facecolor = 'k', edgecolor = 'k', linewidth='1.', s=30)
ax3.set_title('x =  Horas nubladas en el Este', loc = 'center', fontsize=9)

#cbar_ax = fig.add_axes([0.11, 0.28, 0.78, 0.008])
cbar_ax = fig.add_axes([0.11, 0.93, 0.78, 0.008])
cbar = fig.colorbar(mapa, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Anomalías de radiación en el caso nublado $[W/m^{2}]$", fontsize=8, fontproperties=prop)

ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
#ax4.bar(np.arange(len(s)), Cant_Days_Nuba_348, color='orange', align='center', alpha=0.5)
ax4.plot(s, Porc_Days_Nuba_350, color = '#8ABB73', lw=1.5)
ax4.scatter(s, Porc_Days_Nuba_350, marker='.', color = '#8ABB73', s=30)
ax4.set_xlabel('Horas nubladas', fontproperties = prop_1)
ax4.set_ylabel(u"Frecuencia de días [%]", fontproperties = prop_1)
ax4.set_xticks(range(0, 12), minor=False)
ax4.set_xticklabels(s, minor=False, rotation = 20)
ax4.set_ylim(0, 100)
ax4.set_title(u'Frecuencia de días en el Oeste', loc = 'center', fontsize=9)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
#ax5.bar(np.arange(len(s)), Cant_Days_Nuba_350, color='orange', align='center', alpha=0.5)
ax5.plot(s, Porc_Days_Nuba_975, color = '#8ABB73', lw=1.5)
ax5.scatter(s, Porc_Days_Nuba_975, marker='.', color = '#8ABB73', s=30)
ax5.set_xlabel('Horas nubladas', fontproperties = prop_1)
ax5.set_ylabel(u"Frecuencia de días [%]", fontproperties = prop_1)
ax5.set_xticks(range(0, 12), minor=False)
ax5.set_xticklabels(s, minor=False, rotation = 20)
ax5.set_ylim(0, 100)
ax5.set_title(u'Frecuencia de días en el Centro-Oeste', loc = 'center', fontsize=9)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
#ax6.bar(np.arange(len(s)), Cant_Days_Nuba_975, color='orange', align='center', alpha=0.5)
ax6.plot(s, Porc_Days_Nuba_348, color = '#8ABB73', lw=1.5)
ax6.scatter(s, Porc_Days_Nuba_348, marker='.', color = '#8ABB73', s=30)
ax6.set_xlabel('Horas nubladas', fontproperties = prop_1)
ax6.set_ylabel(u"Frecuencia de días [%]", fontproperties = prop_1)
ax6.set_xticks(range(0, 12), minor=False)
ax6.set_xticklabels(s, minor=False, rotation = 20)
ax6.set_ylim(0, 100)
ax6.set_title(u'Frecuencia de días en el Este', loc = 'center', fontsize=9)

plt.subplots_adjust(wspace=0.3, hspace=0.3)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/AnomalComposites_Nuba_Cant_Dias.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/AnomalComposites_Nuba_Cant_Dias.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


## -------------------------RANGO DE LAS ANOMALIAS RADIACIÓN PARA VER EL EFECTO DE LA NUBE EN LA RADIACIÓN---------------------------- ##

Rango_348 = Comp_Desp_348_anomal-Comp_Nuba_348_anomal
Rango_350 = Comp_Desp_350_anomal-Comp_Nuba_350_anomal
Rango_975 = Comp_Desp_975_anomal-Comp_Nuba_975_anomal

range_min = min(np.nanmin(Rango_348.values)  , np.nanmin(Rango_350.values), np.nanmin(Rango_975.values))-1
range_max = max(np.nanmax(Rango_348.values)  , np.nanmax(Rango_350.values), np.nanmax(Rango_975.values))+1
mid_val = 0

plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(1,3,1)
mapa = ax1.imshow(Rango_350, interpolation = 'none', cmap=cmap, clim=(range_min, range_max), norm=MidpointNormalize(midpoint=mid_val,vmin=range_min, vmax=range_max))
ax1.set_yticks(range(0,12), minor=False)
ax1.set_yticklabels(s, minor=False)
ax1.set_xticks(range(0,12), minor=False)
ax1.set_xticklabels(s, minor=False, rotation = 20)
ax1.set_xlabel('Horas condicionadas', fontsize=10, fontproperties = prop_1)
ax1.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax1.set_title(u'Rango de anomalías en el Oeste', loc = 'center', fontsize=9)

ax2=fig.add_subplot(1,3,2)
mapa = ax2.imshow(Rango_975, interpolation = 'none', cmap=cmap, clim=(range_min, range_max), norm=MidpointNormalize(midpoint=mid_val,vmin=range_min, vmax=range_max))
ax2.set_yticks(range(0,12), minor=False)
ax2.set_yticklabels(s, minor=False)
ax2.set_xticks(range(0,12), minor=False)
ax2.set_xticklabels(s, minor=False, rotation = 20)
ax2.set_xlabel('Horas condicionadas', fontsize=10, fontproperties = prop_1)
ax2.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax2.set_title(u'Rango de anomalías en el Centro-Oeste', loc = 'center', fontsize=9)

ax3 = fig.add_subplot(1,3,3)
mapa = ax3.imshow(Rango_348, interpolation = 'none', cmap=cmap, clim=(range_min, range_max), norm=MidpointNormalize(midpoint=mid_val,vmin=range_min, vmax=range_max))
ax3.set_yticks(range(0,12), minor=False)
ax3.set_yticklabels(s, minor=False)
ax3.set_xticks(range(0,12), minor=False)
ax3.set_xticklabels(s, minor=False, rotation = 20)
ax3.set_xlabel('Horas condicionadas', fontsize=10, fontproperties = prop_1)
ax3.set_ylabel(u'Horas de radiación solar', fontsize=10, fontproperties = prop_1)
ax3.set_title(u'Rango de anomalías en el Este', loc = 'center', fontsize=9)

cbar_ax = fig.add_axes([0.11, 0.28, 0.78, 0.008])
cbar = fig.colorbar(mapa, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Anomaly range $[W/m^{2}]$", fontsize=8, fontproperties=prop)

plt.subplots_adjust(wspace=0.3)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/Rango_Anomal_Composite.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Rango_Anomal_Composite.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
