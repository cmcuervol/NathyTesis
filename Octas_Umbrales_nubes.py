#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
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


## ----------------------LECTURA DE DATOS DE GOES CH02----------------------- ##

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2019_0320_0822.nc')

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

#####################################################################################################################
## --------------------------------UMBRALES OBTENIDOS CON EL PIRANOMETRO------------------------------------------ ##
#####################################################################################################################

Umbral_up_348   = 52.00030
Umbral_down_348 = 21.21820
Umbrales_348 = [Umbral_down_348, Umbral_up_348]

Umbral_up_350   = 54.1262
Umbral_down_350 = 25.9514
Umbrales_350 = [Umbral_down_350, Umbral_up_350]

Umbral_up_975   = 53.3911
Umbral_down_975 = 21.3474
Umbrales_975 = [Umbral_down_975, Umbral_up_975]

## -------------------------------------------------------------------------- ##

lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :]
Rad = ds.variables['Radiancias'][:, :, :]

                   ## -- Obtener el tiempo para cada valor

tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas)):
    fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')

                   ## -- Selección del pixel de la TS y creación de DF
lat_index_975 = np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0]
lon_index_975 = np.where((lon[0, :] < -75.58) & (lon[0, :] > -75.59))[0][0]
Rad_pixel_975 = Rad[:, lat_index_975, lon_index_975]

Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)

                   ## -- Selección del pixel de la CI
lat_index_350 = np.where((lat[:, 0] > 6.16) & (lat[:, 0] < 6.17))[0][0]
lon_index_350 = np.where((lon[0, :] < -75.64) & (lon[0, :] > -75.65))[0][0]
Rad_pixel_350 = Rad[:, lat_index_350, lon_index_350]

Rad_df_350 = pd.DataFrame()
Rad_df_350['Fecha_Hora'] = fechas_horas
Rad_df_350['Radiacias'] = Rad_pixel_350
Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_350.index = Rad_df_350['Fecha_Hora']
Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)


                   ## -- Selección del pixel de la JV
lat_index_348 = np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0]
lon_index_348 = np.where((lon[0, :] < -75.54) & (lon[0, :] > -75.55))[0][0]
Rad_pixel_348 = Rad[:, lat_index_348, lon_index_348]

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

Rad_df_348_h = Rad_df_348_h.between_time('06:00', '17:00')
Rad_df_350_h = Rad_df_350_h.between_time('06:00', '17:00')
Rad_df_975_h = Rad_df_975_h.between_time('06:00', '17:00')

#####################################################################################################################
## -------------------------------UMBRALES OBTENIDOS A PARTIR DE LAS OCTAS---------------------------------------- ##
#####################################################################################################################

Rad_df_348_h_oct = np.rint((Rad_df_348_h/100)*8)
Rad_df_350_h_oct = np.rint((Rad_df_350_h/100)*8)
Rad_df_975_h_oct = np.rint((Rad_df_975_h/100)*8)

Octas = [2, 6]

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Rad_df_348_h_oct['Radiacias'].values[~np.isnan(Rad_df_348_h_oct['Radiacias'].values)], bins='auto', alpha = 0.5)
Umbrales_line1 = [ax1.axvline(x=xc, color='k', linestyle='--') for xc in Octas]
ax1.set_title(u'Distribución del FR en JV', fontproperties=prop, fontsize = 13)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Octas', fontproperties=prop_1)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Rad_df_350_h_oct['Radiacias'].values[~np.isnan(Rad_df_350_h_oct['Radiacias'].values)], bins='auto', alpha = 0.5)
Umbrales_line2 = [ax2.axvline(x=xc, color='k', linestyle='--') for xc in Octas]
ax2.set_title(u'Distribución del FR en CI', fontproperties=prop, fontsize = 13)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Octas', fontproperties=prop_1)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Rad_df_975_h_oct['Radiacias'].values[~np.isnan(Rad_df_975_h_oct['Radiacias'].values)], bins='auto', alpha = 0.5)
Umbrales_line3 = [ax3.axvline(x=xc, color='k', linestyle='--') for xc in Octas]
ax3.set_title(u'Distribución del FR en TS', fontproperties=prop, fontsize = 13)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Octas', fontproperties=prop_1)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoFROctas.png')
plt.show()

## -------------------------OBTENER EL DF DEL ESCENARIO DESPEJADO---------------------------- ##

df_348_desp_oct = Rad_df_348_h_oct[Rad_df_348_h_oct['Radiacias'] <= 2]
df_350_desp_oct = Rad_df_350_h_oct[Rad_df_350_h_oct['Radiacias'] <= 2]
df_975_desp_oct = Rad_df_975_h_oct[Rad_df_975_h_oct['Radiacias'] <= 2]

## --------------------------OBTENER EL DF DEL ESCENARIO NUBADO------------------------------ ##

df_348_nuba_oct = Rad_df_348_h_oct[Rad_df_348_h_oct['Radiacias'] >= 6]
df_350_nuba_oct = Rad_df_350_h_oct[Rad_df_350_h_oct['Radiacias'] >= 6]
df_975_nuba_oct = Rad_df_975_h_oct[Rad_df_975_h_oct['Radiacias'] >= 6]

## -------------------------OBTENER LAS HORAS Y FECHAS DESPEJADAS---------------------------- ##

Hora_desp_348 = df_348_desp_oct.index.hour
Fecha_desp_348 = df_348_desp_oct.index.date

Hora_desp_350 = df_350_desp_oct.index.hour
Fecha_desp_350 = df_350_desp_oct.index.date

Hora_desp_975 = df_975_desp_oct.index.hour
Fecha_desp_975 = df_975_desp_oct.index.date

## ----------------------------OBTENER LAS HORAS Y FECHAS NUBADAS---------------------------- ##

Hora_nuba_348 = df_348_nuba_oct.index.hour
Fecha_nuba_348 = df_348_nuba_oct.index.date

Hora_nuba_350 = df_350_nuba_oct.index.hour
Fecha_nuba_350 = df_350_nuba_oct.index.date

Hora_nuba_975 = df_975_nuba_oct.index.hour
Fecha_nuba_975 = df_975_nuba_oct.index.date

## ----------------------------OBTENER LAS HORAS Y FECHAS NUBADAS---------------------------- ##

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
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Hora_desp_350, bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax2.hist(Hora_nuba_350, bins='auto', alpha = 0.5, label = 'Nub')
ax2.set_title(u'Distribución de nubes por horas en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Horas', fontproperties=prop_1)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Hora_desp_975, bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax3.hist(Hora_nuba_975, bins='auto', alpha = 0.5, label = 'Nub')
ax3.set_title(u'Distribución de nubes por horas en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Horas', fontproperties=prop_1)
ax3.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoNubaDespOctas.png')
plt.show()
