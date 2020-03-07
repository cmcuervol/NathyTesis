#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import pandas as pd
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
import matplotlib.colors as colors
import netCDF4 as nc
from netCDF4 import Dataset

#------------------------------------------------------------------------------
# Motivación codigo sección 1--------------------------------------------------

"Código para el dibujo y cálculo  de los histogramas de frecuencias horarios de la lluvia en determinados puntos de medición. Se lee como"
"un pandas los datos a dibujar de cada punto de medición para luego calcular el histograma de los acumulados y de las horas de acumulados."
"Inicialmente, se crea con el propósito de estimar la distribucion de los acumulados en los puntos de medición de los paneles experimentales "
"Se hace con los datos del 2018."

Pluvio = 'si'   ##--> Para que promedie la lluvia de los dos pluviometros debe ser 'si'

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##########################################################################
## ----------------LECTURA DE LOS ARCHIVOS DE ACUMULADOS----------------##
##########################################################################

df_Acum_JV = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Pluvio/AcumH211.csv',  sep=',', index_col =0)
df_Acum_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Pluvio/AcumH206.csv',  sep=',', index_col =0)
df_Acum_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Pluvio/AcumH201.csv',  sep=',', index_col =0)

df_Acum_JV.index = pd.to_datetime(df_Acum_JV.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_Acum_CI.index = pd.to_datetime(df_Acum_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_Acum_TS.index = pd.to_datetime(df_Acum_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')

df_Acum_JV = df_Acum_JV.between_time('06:00', '17:59')
df_Acum_CI = df_Acum_CI.between_time('06:00', '17:59')
df_Acum_TS = df_Acum_TS.between_time('06:00', '17:59')

########################################################################
## ----------------AJUSTE DE LOS DATOS DEL PLUVIÓMETRO----------------##
########################################################################

"Si uno de los archivos leidos tiene infomación de pluviometro, se deben promediar los acumulados horarios de P1 y P2 para tener un solo estimado."

if Pluvio == 'si':
    df_Acum_JV['Precip'] = df_Acum_JV[['P1', 'P2']].mean(axis=1)
    df_Acum_JV = df_Acum_JV.drop(['P1', 'P2'], axis=1)

########################################################################
## ----------------HISTOGRAMAS DE LA LLUVIA HORARIOS -----------------##
########################################################################

df_Acum_JV_rain = df_Acum_JV[df_Acum_JV['Precip']>0]
df_Acum_CI_rain = df_Acum_CI[df_Acum_CI['Precip']>0]
df_Acum_TS_rain = df_Acum_TS[df_Acum_TS['Precip']>0]

## -------------------------OBTENER LAS HORAS Y FECHAS LLUVIOSAS---------------------------- ##

Hora_JV = df_Acum_JV_rain.index.hour
Fecha_JV = df_Acum_JV_rain.index.date

Hora_CI = df_Acum_CI_rain.index.hour
Fecha_CI = df_Acum_CI_rain.index.date

Hora_TS = df_Acum_TS_rain.index.hour
Fecha_TS = df_Acum_TS_rain.index.date

## -----------------------------DIBUJAR LOS HISTOGRAMAS DE LAS HORAS ------ ----------------------- #
fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Hora_JV, bins='auto', alpha = 0.5, color = 'orange', label = 'H_Lluvia')
ax1.set_title(u'Distribución de horas lluviosas en JV', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Horas', fontproperties=prop_1)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Hora_CI, bins='auto', alpha = 0.5, color = 'orange', label = 'H_Lluvia')
ax2.set_title(u'Distribución de horas lluviosas en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Horas', fontproperties=prop_1)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Hora_TS, bins='auto', alpha = 0.5, color = 'orange', label = 'H_Lluvia')
ax3.set_title(u'Distribución de horas lluviosas en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Horas', fontproperties=prop_1)
ax3.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoHorasLluvia_2018.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/HistoHorasLluvia_2018.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

#------------------------------------------------------------------------------
# Motivación codigo sección 2--------------------------------------------------

"En esta seccion del codigo se pretenda encontrar la correlación rezagada entre las horas de acuulados de precipitación y las las horas"
"nubladas para poder verificar la información de los umbrales de GOES CH2 para nubes."

################################################################################################
## -------------------------------LECTURA DE DATOS DE GOES CH02------------------------------ ##
################################################################################################

#ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2019_0320_0822.nc')
ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C22018.nc')

## ---------------------------------AJUSTE DE LOS DATOS DE GOES CH2----------------------------------------- ##

lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :]
Rad = ds.variables['Radiancias'][:, :, :]

                   ## -- Obtener el tiempo para cada valor

tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas)):
    fechas_horas[i] = pd.to_datetime(fechas_horas[i] , format="%Y-%m-%d %H:%M", errors='coerce')

################################################################################################
##-------------------INCORPORANDO EL ARRAY DEL ZENITH PARA CADA HORA--------------------------##
################################################################################################

def Aclarado_visible(Path_Zenith, Path_Fechas, Rad, fechas_horas):
    Z = np.load(Path_Zenith)
    Fechas_Z = np.load(Path_Fechas)

    daily_hours = np.arange(5, 19, 1)
    Zenith = []
    Fechas_Zenith = []
    for i in range(len(Fechas_Z)):
        if Fechas_Z[i].hour in daily_hours:
            Zenith.append(Z[i, :, :])
            Fechas_Zenith.append(Fechas_Z[i])
        elif Fechas_Z[i].hour not in daily_hours:
            pass
    Zenith = np.array(Zenith)

    Rad_clear = []
    for i in range(len(Fechas_Zenith)):
        for j in range(len(fechas_horas)):
            if Fechas_Zenith[i].hour ==  fechas_horas[j].hour and Fechas_Zenith[i].day ==  fechas_horas[j].day:
                Rad_clear.append(Rad[j, :, :]/np.cos(Zenith[i, :, :]))
            else:
                pass
    Rad_clear = np.array(Rad_clear)
    return Rad

Rad_Z = Aclarado_visible('/home/nacorreasa/Maestria/Datos_Tesis/hourlyZenith2018.npy', '/home/nacorreasa/Maestria/Datos_Tesis/DatesZenith.npy', Rad, fechas_horas)
del Rad

Rad = Rad_Z

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
'Para el caso de la relación si es bueno tener la información en resolución horaria.'
## ------------------------CAMBIANDO LOS DATOS HORARIOS POR LOS ORIGINALES---------------------- ##
# Rad_df_348_h = Rad_df_348
# Rad_df_350_h = Rad_df_350
# Rad_df_975_h = Rad_df_975

## ------------------------------------DATOS HORARIOS DE REFLECTANCIAS------------------------- ##

Rad_df_348_h =  Rad_df_348.groupby(pd.Grouper(freq="H")).mean()
Rad_df_350_h =  Rad_df_350.groupby(pd.Grouper(freq="H")).mean()
Rad_df_975_h =  Rad_df_975.groupby(pd.Grouper(freq="H")).mean()

'OJOOOO HASTA ACÁ-----------------------------------------------------------------------------------------'

Rad_df_348_h = Rad_df_348_h.between_time('06:00', '17:59')
Rad_df_350_h = Rad_df_350_h.between_time('06:00', '17:59')
Rad_df_975_h = Rad_df_975_h.between_time('06:00', '17:59')

################################################################################################
## -------------------------------UMBRALES DE LAS REFLECTANCIAS------------------------------ ##
################################################################################################

Umbral_up_348   = 46.26875
Umbral_down_348 = 22.19776
Umbrales_348 = [Umbral_down_348, Umbral_up_348]

Umbral_up_350   = 49.4412
Umbral_down_350 = 26.4400
Umbrales_350 = [Umbral_down_350, Umbral_up_350]

Umbral_up_975   = 49.4867
Umbral_down_975 = 17.3913
Umbrales_975 = [Umbral_down_975, Umbral_up_975]

df_348_nuba = Rad_df_348_h[Rad_df_348_h['Radiacias'] > Umbral_up_348]
df_350_nuba = Rad_df_350_h[Rad_df_350_h['Radiacias'] > Umbral_up_350]
df_975_nuba = Rad_df_975_h[Rad_df_975_h['Radiacias'] > Umbral_up_975]

################################################################################################
##----------------NORMALIZANDO LOS VALORED DE PRECIPIRACION Y RADIANCIA-----------------------##
################################################################################################

df_Acum_JV_norm = (df_Acum_JV - df_Acum_JV.mean()) / (df_Acum_JV.max() - df_Acum_JV.min())
df_Acum_CI_norm = (df_Acum_CI - df_Acum_CI.mean()) / (df_Acum_CI.max() - df_Acum_CI.min())
df_Acum_TS_norm = (df_Acum_TS - df_Acum_TS.mean()) / (df_Acum_TS.max() - df_Acum_TS.min())

df_348_nuba_norm =  (df_348_nuba - df_348_nuba.mean()) / (df_348_nuba.max() - df_348_nuba.min())
df_350_nuba_norm =  (df_350_nuba - df_350_nuba.mean()) / (df_350_nuba.max() - df_350_nuba.min())
df_975_nuba_norm =  (df_975_nuba - df_975_nuba.mean()) / (df_975_nuba.max() - df_975_nuba.min())

################################################################################################
##---------------------DATAFRAME CON LAS VARIABLES Y LA CORRELACIÓN--------------------------##
################################################################################################

df_corr_JV = pd.concat([df_348_nuba_norm , df_Acum_JV_norm], axis=1)
df_corr_CI = pd.concat([df_350_nuba_norm , df_Acum_CI_norm], axis=1)
df_corr_TS = pd.concat([df_975_nuba_norm , df_Acum_TS_norm], axis=1)

a = df_corr_JV.Radiacias- df_corr_JV.Radiacias.mean()

corr_JV = np.correlate((df_corr_JV.Radiacias- df_corr_JV.Radiacias.mean()).values,  (df_corr_JV.Precip- df_corr_JV.Precip.mean()).values,   mode='full')
lag_JV = corr_JV.argmax() - (len(df_corr_JV.Radiacias.values) - 1)

data_1 = df_corr_JV.Radiacias.values
data_2 = df_corr_JV.Precip.values

plt.plot(corr_JV)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ENSAYOBORRABLE_Corr.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/ENSAYOBORRABLE_Corr.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
# lag = corr.argmax() - (len(data_1) - 1)
# print(lag)
plt.plot(data_1, 'r*')
plt.plot(data_2, 'b*')
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ENSAYOBORRABLE_Prec_Meteo.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/ENSAYOBORRABLE_Prec_Meteo.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
