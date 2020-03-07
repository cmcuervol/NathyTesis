#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
from scipy import stats
# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA
import matplotlib
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
from pysolar.solar import *
import scipy.stats as st
import scipy.special as sp

##...........................................................................................................................................................##
##=================================================================== SECCIÓN 1 =============================================================================##
##...........................................................................................................................................................##

'Codigo para contrastar los métodos de calculo de la radiación teórica, por la de pysolar o por el modelo de Gis'
'o por el modelo teorico usado para la radiacion teorica de los piranometros. Se calcularán para el 2019. Los acu-'
'mulados de radiación se harán para compararlo con los acumulados de los registros de 2018.'

##############################################################################
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------
##############################################################################

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

####################################################################################################################
##-----------------------------------LECTURA DE LOS DATOS HISTORICOS DE PIRANOMETRO-------------------------------##
####################################################################################################################

df_pira_TS = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6001.txt', parse_dates=[2])
df_pira_TS = df_pira_TS.set_index(["fecha_hora"])
df_pira_TS.index = df_pira_TS.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_TS.index = df_pira_TS.index.tz_localize(None)

df_pira_CI = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6002.txt', parse_dates=[2])
df_pira_CI = df_pira_CI.set_index(["fecha_hora"])
df_pira_CI.index = df_pira_CI.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_CI.index = df_pira_CI.index.tz_localize(None)

df_pira_JV = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6003.txt', parse_dates=[2])
df_pira_JV = df_pira_JV.set_index(["fecha_hora"])
df_pira_JV.index = df_pira_JV.index.tz_localize('UTC').tz_convert('America/Bogota')
df_pira_JV.index = df_pira_JV.index.tz_localize(None)

####################################################################################################################
## ------------------------------------------CALCULO DE LA RADIACIÓN TEORICA------------------------------------- ##
####################################################################################################################

import datetime
def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada 10 min. Las fechas final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=10)
    while start_date <= end_date:
        yield start_date
        start_date += delta

def radiacion_teorica(Hora):
   # Dia del Año

   dn = Hora.timetuple().tm_yday

   Theta_d = (2 * np.pi * (dn-1))/ 365.

   # (d/d)2
   an = [1.000110, 0.034221, 0.000719]
   bn = [0,        0.001280, 0.000077]

   d   = 0
   tmp = 0
   for i in range(3):
       tmp = (an[i] * np.cos(i*Theta_d)) + (bn[i] * np.sin(i*Theta_d))
       d = d + tmp

   # Delta
   a_n = [0.006918, -0.399912, -0.006758, -0.002697]
   b_n = [0,         0.070257,  0.000907,  0.001480]

   Delta = 0
   tmp   = 0
   for i in range(4):
      tmp = (a_n[i] * np.cos(i*Theta_d)) + (b_n[i] * np.sin(i*Theta_d))
      Delta = Delta + tmp

   # Ángulo Horario (Cada Minuto)
   Minutos = (Hora.hour * 60) + Hora.minute
   Horario = 180 - (0.25 * Minutos)
   Horario = (Horario * np.pi)/180.

   # Coseno de Theta
   Latitud = (6.2593 * np.pi)/180.
   Cos_Theta = (np.sin(Latitud)*np.sin(Delta)) + (np.cos(Latitud)*np.cos(Delta)*np.cos(Horario))

   # Radiación Teórica
   So = 1367 #w/m2
   Q = So * d * Cos_Theta

   return Q

def serie_Kumar_Model_hora(estacion):
    'Retorna un dataframe horario con la radiacion teórico con las recomendacione de Kumar elaborado por Gisel Guzmán ' \
    'para el AMVA y su tesis. El dataframe original se le ordenan los datos a  12 meses ascendentes (2019), aunque pueden ' \
    ' pertencer  a  años difernetes. El resultado es para el punto seleccionado y con el archivo de Total_Timeseries.csv'

    data_Model = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_Totales/Total_Timeseries_Rad_2018.csv',
                             sep=',')

    fecha_hora = [pd.to_datetime(data_Model['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in
                  range(len(data_Model['Unnamed: 0']))]

    data_Model.index = fecha_hora

    data_Model = data_Model.sort_index()

    data_Model['Month'] = np.array(data_Model.index.month)

    data_Model = data_Model.sort_values(by="Month")

    fechas = []
    for i in daterange('2019-01-01', '2020-01-01'):
        fechas.append(i)
    fechas = fechas[0:-1]

    if estacion == '6001':
        punto = data_Model['TS_kumar']
    elif estacion == '6002':
        punto = data_Model['CI_kumar']
    elif estacion == '6003':
        punto = data_Model['JV_kumar']

    Rad_teorica = []
    for i in range(len(fechas)):
        mes = fechas[i].month
        hora = fechas[i].hour
        mint = fechas[i].minute
        rad = np.where((data_Model.index.month == mes) & (data_Model.index.hour == hora) & (data_Model.index.minute == mint))[0]
        if len(rad) == 0:
            Rad_teorica.append(np.nan)
        else:
            Rad_teorica.append(punto.iloc[rad].values[0])

    data_Theorical = pd.DataFrame()
    data_Theorical['fecha_hora'] = fechas
    data_Theorical['Radiacion'] = Rad_teorica

    data_Theorical.index = data_Theorical['fecha_hora']
    data_Theorical['Radiacion']= data_Theorical['Radiacion'].astype(float)
    df_hourly_theoric = data_Theorical.groupby(pd.Grouper(freq="H")).mean()
    df_hourly_theoric = df_hourly_theoric[df_hourly_theoric['Radiacion'] > 0]

    return df_hourly_theoric


def Elevation_RadiationTA(n, lat, lon, start):
    'Para obtener la radiación en W/m2 y el ángulo de elevación del sol en grados horariamente para un número "n" de ' \
    'días aun punto en una latitud y longitud determinada ( "lat-lon"como flotantes) a partir de una fecha de inicio ' \
    '"start" como por ejemplo datetime.datetime(2019, 1, 1, 8).'
    import pysolar
    import pytz
    import datetime

    timezone = pytz.timezone("America/Bogota")
    start_aware = timezone.localize(start)

    # Calculate radiation every hour for 365 days
    nhr = 24*n
    dates, altitudes_deg, radiations = list(), list(), list()
    for ihr in range(nhr):
        date = start_aware + datetime.timedelta(hours=ihr)
        altitude_deg = pysolar.solar.get_altitude(lat, lon, date)
        if altitude_deg <= 0:
            radiation = 0.
        else:
            radiation = pysolar.radiation.get_radiation_direct(date, altitude_deg)
        dates.append(date)
        altitudes_deg.append(altitude_deg)
        radiations.append(radiation)

    days = [ihr/24 for ihr in range(nhr)]

    return days, altitudes_deg, radiations, dates

############################################################################################################
## ----------------LECTURA DE LOS DATOS RADIAION TEORICA A PARTIR DEL METODO ESPECIFICADO---------------- ##
############################################################################################################

Puntos_medicion = ['6001', '6002', '6003']
Latitudes = [6.259, 6.168, 6.255]        ## En orden: 6001, 6002, 6003
Longitudes = [-75.588, -75.644, -75.542] ## En orden: 6001, 6002, 6003

##-----------------------------------------------------------------------------------------------------------------------------------##

df_rad_teo_GIS = pd.DataFrame()
Theoric_rad_method = 'GIS_Model'  ##-->> PARA QUE USE EL MODELO DE Gis DEBE SER 'GIS_Model'
resolucion = 'horaria'             ##-->> LAS OPCIONES SON 'diaria' U 'horaria'
for i in range(len(Puntos_medicion)):
    Estacion = Puntos_medicion[i]

    if Theoric_rad_method != 'GIS_Model' and Estacion == '6001':
        days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, Latitudes[0], Longitudes[0], datetime.datetime(2019, 1, 1, 0))
        print('Teorica con pysolar')
    elif Theoric_rad_method != 'GIS_Model' and Estacion == '6002':
        days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, Latitudes[1], Longitudes[1], datetime.datetime(2019, 1, 1, 0))
        print('Teorica con pysolar')
    elif Theoric_rad_method != 'GIS_Model' and Estacion == '6003':
        days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, Latitudes[2], Longitudes[2], datetime.datetime(2019, 1, 1, 0))
        print('Teorica con pysolar')
    elif Theoric_rad_method == 'GIS_Model':
        Io_hora = serie_Kumar_Model_hora(Estacion)
        print('Teorica con el modelo de KUMAR')

    df_rad_teo_GIS = pd.concat([df_rad_teo_GIS, Io_hora], axis=1, sort=False)

df_rad_teo_GIS.columns = ['Rad_teo_975','Rad_teo_350', 'Rad_teo_348']

##-----------------------------------------------------------------------------------------------------------------------------------##

df_rad_teo_PYS = pd.DataFrame()
Theoric_rad_method = 'Pysolar'
for i in range(len(Puntos_medicion)):
    Estacion = Puntos_medicion[i]

    if Theoric_rad_method != 'GIS_Model' and Estacion == '6001':
        days, altitudes_deg, Io_hora , fechas = Elevation_RadiationTA(365, Latitudes[0], Longitudes[0], datetime.datetime(2018, 1, 1, 0))
        df_Io = pd.DataFrame(Io_hora, index = fechas,   columns = ['Io'])
        print('Teorica con pysolar')
    elif Theoric_rad_method != 'GIS_Model' and Estacion == '6002':
        days, altitudes_deg, Io_hora , fechas  = Elevation_RadiationTA(365, Latitudes[1], Longitudes[1], datetime.datetime(2019, 1, 1, 0))
        df_Io = pd.DataFrame(Io_hora,  index = fechas, columns = ['Io'])
        print('Teorica con pysolar')
    elif Theoric_rad_method != 'GIS_Model' and Estacion == '6003':
        days, altitudes_deg, Io_hora, fechas  = Elevation_RadiationTA(365, Latitudes[2], Longitudes[2], datetime.datetime(2019, 1, 1, 0))
        df_Io = pd.DataFrame(Io_hora, index = fechas, columns = ['Io'])
        print('Teorica con pysolar')
    elif Theoric_rad_method == 'GIS_Model':
        Io_hora = serie_Kumar_Model_hora(Estacion)
        print('Teorica con el modelo de KUMAR')

    df_rad_teo_PYS = pd.concat([df_rad_teo_PYS, df_Io], axis=1, sort=False)

##-----------------------------------------------------------------------------------------------------------------------------------##

Theoric_rad_method = 'Piranometro'
fechas = []
for i in daterange('2019-01-01', '2020-01-01'):
    fechas.append(i)
fechas = fechas[0:-1]

Q = []
for k in range(0, len(fechas)):
    Q.append(radiacion_teorica(fechas[k]))

Q = np.array(Q)
Q[Q < 0] = np.nan

df_rad_teo_PIR = pd.DataFrame(Q, index = fechas, columns = ['Io'])
df_rad_teo_PIR = df_rad_teo_PIR.groupby(pd.Grouper(freq="H")).mean()
df_rad_teo_PIR = df_rad_teo_PIR.between_time('06:00', '17:00')

##---------------------------------SUMATORIAS DE RADIACIÓN DE CADA DATAFRAME------------------------------------------------##
df_rad_teo_PIR_sum = df_rad_teo_PIR.groupby(pd.Grouper(freq="D")).sum()
df_rad_teo_GIS_sum = df_rad_teo_GIS.groupby(pd.Grouper(freq="D")).sum()
df_rad_teo_PYS_sum = df_rad_teo_PYS.groupby(pd.Grouper(freq="D")).sum()

df_pira_CI_sum = df_pira_CI.groupby(pd.Grouper(freq="D")).sum()
df_pira_TS_sum = df_pira_TS.groupby(pd.Grouper(freq="D")).sum()
df_pira_JV_sum = df_pira_JV.groupby(pd.Grouper(freq="D")).sum()

########################################################################################################################
## ----------AJUSTANDO LOS DATOS DEL DATAFRAME CAMBIANDO AÑO, ENCABEZADOS Y DENTRO DE LAS FECHAS DE LOS TXT---------- ##
########################################################################################################################

fi_m = df_pira_CI_sum[df_pira_CI_sum.index.year==2018].index[0].month
fi_d = df_pira_CI_sum[df_pira_CI_sum.index.year==2018].index[0].day
ff_m = df_pira_CI_sum[df_pira_CI_sum.index.year==2018].index[-1].month
ff_d = df_pira_CI_sum[df_pira_CI_sum.index.year==2018].index[-1].day

df_rad_teo_GIS_sum.index = [df_rad_teo_GIS_sum.index[i].replace(year=2018) for i in range(len(df_rad_teo_GIS_sum.index))]
df_rad_teo_PIR_sum.index = [df_rad_teo_PIR_sum.index[i].replace(year=2018) for i in range(len(df_rad_teo_PIR_sum.index))]
df_rad_teo_PYS_sum.index = [df_rad_teo_PYS_sum.index[i].replace(year=2018) for i in range(len(df_rad_teo_PYS_sum.index))]
#OJOOO SE DAÑÓ EL PEDAZO COMENTATO ABAJITOO


# df_rad_teo_GIS_sum = df_rad_teo_GIS_sum[(df_rad_teo_GIS_sum.index >= pd.to_datetime('2018-'+str(fi_m)+ '-'
#             +str(fi_d))) & (df_rad_teo_GIS_sum.index
#             <= pd.to_datetime('2018-'+str(ff_m)+ '-'+str(ff_d)))]
#
# df_rad_teo_PIR_sum = df_rad_teo_PIR_sum[(df_rad_teo_PIR_sum.index >= pd.to_datetime('2018-'+str(fi_m)+ '-'
#             +str(fi_d))) & (df_rad_teo_PIR_sum.index
#             <= pd.to_datetime('2018-'+str(ff_m)+ '-'+str(ff_d)))]
#
# df_rad_teo_PYS_sum = df_rad_teo_PYS_sum[(df_rad_teo_PYS_sum.index >= pd.to_datetime('2018-'+str(fi_m)+ '-'
#             +str(fi_d))) & (df_rad_teo_PYS_sum.index
#             <= pd.to_datetime('2018-'+str(ff_m)+ '-'+str(ff_d)))]

df_rad_teo_PIR.to_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_PIR.csv", sep=',')
df_rad_teo_GIS.to_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_GIS.csv", sep=',')
df_rad_teo_PYS.to_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_PYS.csv", sep=',')

##################################################################################################################
## ----------------------------------------HISTOGRAMAS--------------------------------------------------------- ##
##################################################################################################################

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(df_rad_teo_PIR_sum['Io'].values[~np.isnan(df_rad_teo_PIR_sum['Io'].values)], bins='auto', alpha = 0.5)
ax1.set_title(u'Distribución de la radiación con PIR', fontproperties=prop, fontsize = 13)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Radiación', fontproperties=prop_1)

ax2 = fig.add_subplot(1, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(df_rad_teo_GIS_sum['Rad_teo_975'].values[~np.isnan(df_rad_teo_GIS_sum['Rad_teo_975'].values)], bins='auto', alpha = 0.5)
ax2.set_title(u'Distribución de la radiación con GIS', fontproperties=prop, fontsize = 13)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Radiación', fontproperties=prop_1)
plt.show()

##...........................................................................................................................................................##
##=================================================================== SECCIÓN 2 =============================================================================##
##...........................................................................................................................................................##
'En este punto, se pretenden explorar los datos del modelo de GIS para dar con algunas posibles fallas en la estimación de la radiacion en JV principalmente.'

##################################################################################################################
##_----------------------------------VERIFICACIÓN MODELO GIS CON DIAS DESPEJADOS--------------------------------##
##################################################################################################################

'Seleccion de dias soleados y graficación con la radiacion directa y difusa del modelo, ademas de los datos del piranometro.'
estacion = '6003'
##---------------------------------------------------------------------------------------------------------------##


data_Model = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_2018/Total_Timeseries_Rad_2018.csv',  sep=',')

fecha_hora = [pd.to_datetime(data_Model['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in
              range(len(data_Model['Unnamed: 0']))]

data_Model.index = fecha_hora
data_Model = data_Model.sort_index()
data_Model['Month'] = np.array(data_Model.index.month)
data_Model = data_Model.sort_values(by="Month")

fechas = []
for i in daterange('2019-01-01', '2020-01-01'):
    fechas.append(i)
fechas = fechas[0:-1]

if estacion == '6001':
    punto = data_Model['TS_kumar']
    punto_Dif = data_Model['TS_kumar_difusa']
    punto_PiraEjp = data_Model['TS_piranometro']
    punto_Dir = data_Model['TS_kumar_directa']
elif estacion == '6002':
    punto = data_Model['CI_kumar']
    punto_Dif = data_Model['CI_kumar_difusa']
    punto_PiraEjp = data_Model['CI_piranometro']
    punto_Dir = data_Model['CI_kumar_directa']
elif estacion == '6003':
    punto = data_Model['JV_kumar']
    punto_Dif = data_Model['JV_kumar_difusa']
    punto_PiraEjp = data_Model['JV_piranometro']
    punto_Dir = data_Model['JV_kumar_directa']

Rad_teorica = []
Rad_Dif = []
Rad_PiraEjp = []
Rad_Dir = []
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    mint = fechas[i].minute
    rad = np.where((data_Model.index.month == mes) & (data_Model.index.hour == hora) & (data_Model.index.minute == mint))[0]
    if len(rad) == 0:
        Rad_teorica.append(np.nan)
        Rad_Dif.append(np.nan)
        Rad_PiraEjp.append(np.nan)
        Rad_Dir.append(np.nan)
    else:
        Rad_teorica.append(punto.iloc[rad].values[0])
        Rad_Dif.append(punto_Dif .iloc[rad].values[0])
        Rad_PiraEjp.append(punto_PiraEjp.iloc[rad].values[0])
        Rad_Dir.append(punto_Dir.iloc[rad].values[0])

data_Theorical = pd.DataFrame()
data_Theorical['fecha_hora'] = fechas
data_Theorical['Radiacion_TeoricaG'] = Rad_teorica
data_Theorical['Radiacion_Dif'] = Rad_Dif
data_Theorical['Radiacion_PirModel'] = Rad_PiraEjp
data_Theorical['Radiacion_Dir'] = Rad_Dir
data_Theorical.index = data_Theorical['fecha_hora']
data_Theorical_caso = data_Theorical.between_time('05:00', '18:00')

##---------------------------------------------------------------------------------------------------------------##

'-PRIMER CASO DE DIA SOLEADO: 18 de Agosto de 2019, el piranometro de JV no tuvo datos si no hasta el 20 por la tarde.'

fechas_1 = pd.to_datetime('2019-08-18', format="%Y-%m-%d").date()

data_caso1 = data_Theorical_caso[data_Theorical_caso.index.date == fechas_1]

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
plt. plot(data_caso1.index, data_caso1['Radiacion_TeoricaG'].values, color = 'orange', label = 'TeoricaG')
plt. plot(data_caso1.index, data_caso1['Radiacion_Dif'].values, color = 'green', label = 'Dif')
plt. plot(data_caso1.index, data_caso1['Radiacion_PirModel'].values, color = 'red', label = 'PiraModel')
plt. plot(data_caso1.index, data_caso1['Radiacion_Dir'].values, color = 'blue', label = 'Dir')
plt.ylabel(u"Irradiancia", fontsize=20, fontproperties=prop_1)
plt.xlabel(u"Tiempo", fontsize=20, fontproperties=prop_1)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()
plt.title(u'Radiaciones Modelo \n en Joaquín Vallejo el '+str(fechas_1), fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.show()

 print(data_caso1[data_caso1['Radiacion_PirModel']>=100][0:1].index[0])
##---------------------------------------------------------------------------------------------------------------##
'-SEGUNDO CASO DE DIA SOLEADO: 25 de Marzo de 2016, el piranometro de JV no tuvo datos si no hasta el 20 por la tarde.'
'NO habia registros de piranometro ese día en el modelo en JV.'

fechas_2 = pd.to_datetime('2016-03-25', format="%Y-%m-%d").date()
data_caso2 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_dias_despejados/2016-03-25_Timeseries.csv',  sep=',')
fecha_hora = [pd.to_datetime(data_caso2['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in range(len(data_caso2['Unnamed: 0']))]
data_caso2.index = fecha_hora
data_caso2 = data_caso2.sort_index()
# data_caso2['Month'] = np.array(data_caso2.index.month)
# data_caso2 = data_caso2.sort_values(by="Month")
data_caso2 = data_caso2.drop(['Unnamed: 0', 'TS_kumar', 'TS_kumar_directa', 'TS_kumar_difusa', 'CI_kumar', 'CI_kumar_directa', 'CI_kumar_difusa', 'TS_piranometro',
       'CI_piranometro', 'TS_Shadow', 'CI_Shadow'], axis=1)
data_caso2.columns = ['Radiacion_TeoricaG', 'Radiacion_Dir', 'Radiacion_Dif', 'Radiacion_PirModel', 'Sombra']

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
plt. plot(data_caso2.index, data_caso2['Radiacion_TeoricaG'].values, color = 'orange', label = 'TeoricaG')
plt. plot(data_caso2.index, data_caso2['Radiacion_Dif'].values, color = 'green', label = 'Dif')
plt. plot(data_caso2.index, data_caso2['Radiacion_PirModel'].values, color = 'red', label = 'PiraModel')
plt. plot(data_caso2.index, data_caso2['Radiacion_Dir'].values, color = 'blue', label = 'Dir')
plt.ylabel(u"Irradiancia", fontsize=20, fontproperties=prop_1)
plt.xlabel(u"Tiempo", fontsize=20, fontproperties=prop_1)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()
plt.title(u'Radiaciones Modelo \n en Joaquín Vallejo el '+str(fechas_2), fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.show()

print(data_caso2[data_caso2['Radiacion_PirModel']>=100][0:1].index[0])

##---------------------------------------------------------------------------------------------------------------##
'-TERCER CASO DE DIA SOLEADO: 23 de Enero de 2017, el piranometro de JV no tuvo datos si no hasta el 20 por la tarde.'

fechas_3 = pd.to_datetime('2017-01-23', format="%Y-%m-%d").date()
data_caso3 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_dias_despejados/2017-01-23_Timeseries.csv',  sep=',')
fecha_hora = [pd.to_datetime(data_caso3['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in range(len(data_caso3['Unnamed: 0']))]
data_caso3.index = fecha_hora
data_caso3 = data_caso3.sort_index()
# data_caso3['Month'] = np.array(data_caso3.index.month)
# data_caso3 = data_caso3.sort_values(by="Month")
data_caso3 = data_caso3.drop(['Unnamed: 0', 'TS_kumar', 'TS_kumar_directa', 'TS_kumar_difusa', 'CI_kumar', 'CI_kumar_directa', 'CI_kumar_difusa', 'TS_piranometro',
       'CI_piranometro', 'TS_Shadow', 'CI_Shadow'], axis=1)
data_caso3.columns = ['Radiacion_TeoricaG', 'Radiacion_Dir', 'Radiacion_Dif', 'Radiacion_PirModel', 'Sombra']

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
plt. plot(data_caso3.index, data_caso3['Radiacion_TeoricaG'].values, color = 'orange', label = 'TeoricaG')
plt. plot(data_caso3.index, data_caso3['Radiacion_Dif'].values, color = 'green', label = 'Dif')
plt. plot(data_caso3.index, data_caso3['Radiacion_PirModel'].values, color = 'red', label = 'PiraModel')
plt. plot(data_caso3.index, data_caso3['Radiacion_Dir'].values, color = 'blue', label = 'Dir')
plt.ylabel(u"Irradiancia", fontsize=20, fontproperties=prop_1)
plt.xlabel(u"Tiempo", fontsize=20, fontproperties=prop_1)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()
plt.title(u'Radiaciones Modelo \n en Joaquín Vallejo el '+str(fechas_3), fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.show()

print(data_caso3[data_caso3['Radiacion_PirModel']>=100][0:1].index[0])

##---------------------------------------------------------------------------------------------------------------##
'-CUARTO CASO DE DIA SOLEADO: 3 de Septiembre de 2019, el piranometro de JV no tuvo datos si no hasta el 20 por la tarde.'

fechas_4 = pd.to_datetime('2019-09-03', format="%Y-%m-%d").date()

data_caso4 = data_Theorical_caso[data_Theorical_caso.index.date == fechas_4]
df_pira_caso4 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/ Radiación en el sensor 6003 el 2019-09-03.csv',  sep=',',header=1,  names = ['fecha_hora', 'RaddelDia'])
fecha_hora = [pd.to_datetime(df_pira_caso4['fecha_hora'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in range(len(df_pira_caso4['fecha_hora']))]
df_pira_caso4.index = fecha_hora
df_pira_caso4 = df_pira_caso4.sort_index()
df_pira_caso4 = df_pira_caso4.groupby(pd.Grouper(freq='10Min')).mean()

data_caso4 = pd.concat([data_caso4, df_pira_caso4 ], axis=1, join='inner')

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
plt. plot(data_caso4.index, data_caso4['Radiacion_TeoricaG'].values, color = 'orange', label = 'TeoricaG')
plt. plot(data_caso4.index, data_caso4['Radiacion_Dif'].values, color = 'green', label = 'Dif')
plt. plot(data_caso4.index, data_caso4['Radiacion_PirModel'].values, color = 'red', label = 'PiraModel')
plt. plot(data_caso4.index, data_caso4['Radiacion_Dir'].values, color = 'blue', label = 'Dir')
plt. plot(data_caso4.index, data_caso4['RaddelDia'].values, color = 'cyan', label = 'Rad del dia')
plt.ylabel(u"Irradiancia", fontsize=20, fontproperties=prop_1)
plt.xlabel(u"Tiempo", fontsize=20, fontproperties=prop_1)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()
plt.title(u'Radiaciones Modelo \n en Joaquín Vallejo el '+str(fechas_4), fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.show()

print(data_caso4[data_caso4['RaddelDia']>=100][0:1].index[0])

 data_caso4[data_caso4['Radiacion_TeoricaG']>=100]
 data_caso4[data_caso4['RaddelDia']>=100]

##---------------------------------------------------------------------------------------------------------------##

 '-QUINTO CASO DE DIA SOLEADO: 2 de Enero de 2019, el piranometro de JV no tuvo datos si no hasta el 20 por la tarde.'

fechas_5 = pd.to_datetime('2019-01-02', format="%Y-%m-%d").date()

data_caso5 = data_Theorical_caso[data_Theorical_caso.index.date == fechas_5]
df_pira_caso5 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/ Radiación en el sensor 6003 el 2019-01-02.csv',  sep=',',header=1,  names = ['fecha_hora', 'RaddelDia'])
fecha_hora = [pd.to_datetime(df_pira_caso5['fecha_hora'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in range(len(df_pira_caso5['fecha_hora']))]
df_pira_caso5.index = fecha_hora
df_pira_caso5 = df_pira_caso5.sort_index()
df_pira_caso5 = df_pira_caso5.groupby(pd.Grouper(freq='10Min')).mean()

data_caso5 = pd.concat([data_caso5, df_pira_caso5 ], axis=1, join='inner')

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
plt. plot(data_caso5.index, data_caso5['Radiacion_TeoricaG'].values, color = 'orange', label = 'TeoricaG')
plt. plot(data_caso5.index, data_caso5['Radiacion_Dif'].values, color = 'green', label = 'Dif')
plt. plot(data_caso5.index, data_caso5['Radiacion_PirModel'].values, color = 'red', label = 'PiraModel')
plt. plot(data_caso5.index, data_caso5['Radiacion_Dir'].values, color = 'blue', label = 'Dir')
plt. plot(data_caso5.index, data_caso5['RaddelDia'].values, color = 'cyan', label = 'Rad del dia')
plt.ylabel(u"Irradiancia", fontsize=20, fontproperties=prop_1)
plt.xlabel(u"Tiempo", fontsize=20, fontproperties=prop_1)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()
plt.title(u'Radiaciones Modelo \n en Joaquín Vallejo el '+str(fechas_5), fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.show()

print(data_caso5[data_caso5['RaddelDia']>=100][0:1].index[0])

data_caso5[data_caso5['Radiacion_TeoricaG']>=100]
data_caso5[data_caso5['RaddelDia']>=100]

##---------------------------------------------------------------------------------------------------------------##

'-SEXTO CASO DE DIA SOLEADO: 1 de Mayo de 2019, el piranometro de JV no tuvo datos si no hasta el 20 por la tarde.'

fechas_6 = pd.to_datetime('2019-05-01', format="%Y-%m-%d").date()

data_caso6 = data_Theorical_caso[data_Theorical_caso.index.date == fechas_6]
df_pira_caso6 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/ Radiación en el sensor 6003 el 2019-05-01.csv',  sep=',',header=1,  names = ['fecha_hora', 'RaddelDia'])
fecha_hora = [pd.to_datetime(df_pira_caso6['fecha_hora'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in range(len(df_pira_caso6['fecha_hora']))]
df_pira_caso6.index = fecha_hora
df_pira_caso6 = df_pira_caso6.sort_index()
df_pira_caso6 = df_pira_caso6.groupby(pd.Grouper(freq='10Min')).mean()

data_caso6 = pd.concat([data_caso6, df_pira_caso6 ], axis=1, join='inner')

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
plt. plot(data_caso6.index, data_caso6['Radiacion_TeoricaG'].values, color = 'orange', label = 'TeoricaG')
plt. plot(data_caso6.index, data_caso6['Radiacion_Dif'].values, color = 'green', label = 'Dif')
plt. plot(data_caso6.index, data_caso6['Radiacion_PirModel'].values, color = 'red', label = 'PiraModel')
plt. plot(data_caso6.index, data_caso6['Radiacion_Dir'].values, color = 'blue', label = 'Dir')
plt. plot(data_caso6.index, data_caso6['RaddelDia'].values, color = 'cyan', label = 'Rad del dia')
plt.ylabel(u"Irradiancia", fontsize=20, fontproperties=prop_1)
plt.xlabel(u"Tiempo", fontsize=20, fontproperties=prop_1)
plt.grid(which='major', linestyle=':', linewidth=0.6, alpha=0.7)
plt.legend()
plt.title(u'Radiaciones Modelo \n en Joaquín Vallejo el '+str(fechas_6), fontsize=13,  fontweight = "bold",  fontproperties = prop)
plt.show()


print(data_caso6[data_caso6['RaddelDia']>=100][0:1].index[0])

data_caso6[data_caso6['Radiacion_TeoricaG']>=100]
data_caso6[data_caso6['RaddelDia']>=100]
