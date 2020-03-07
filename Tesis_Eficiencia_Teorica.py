#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA
# import matplotlib
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

Estacion = '6001'
df1 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6001Historico.txt', parse_dates=[2])
Theoric_rad_method = 'GIS_Model'  ##-->> PARA QUE USE EL MODELO DE Gis DEBE SER 'GIS_Model'
resolucion = 'diaria'             ##-->> LAS OPCIONES SON 'diaria' U 'horaria'
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

## ---CALCULO DE LA RADIACIÓN TEORICA--- ##

def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada 10 min. Las fechas final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=10)
    while start_date <= end_date:
        yield start_date
        start_date += delta


def serie_Kumar_Model_hora(estacion):
    'Retorna un dataframe horario con la radiacion teórico con las recomendacione de Kumar elaborado por Gisel Guzmán ' \
    'para el AMVA y su tesis. El dataframe original se le ordenan los datos a  12 meses ascendentes (2018), aunque pueden ' \
    'pertencer  a  años difernetes. El resultado es para el punto seleccionado y con el archivo de Total_Timeseries.csv'

    data_Model = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_nati/Total_Timeseries.csv',
                             sep=',')

    fecha_hora = [pd.to_datetime(data_Model['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")[i].to_pydatetime() for i in
                  range(len(data_Model['Unnamed: 0']))]

    data_Model.index = fecha_hora

    data_Model = data_Model.sort_index()

    data_Model['Month'] = np.array(data_Model.index.month)

    data_Model = data_Model.sort_values(by="Month")

    fechas = []
    for i in daterange('2018-01-01', '2019-01-01'):
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
        rad = \
        np.where((data_Model.index.month == mes) & (data_Model.index.hour == hora) & (data_Model.index.minute == mint))[
            0]

        if len(rad) == 0:
            Rad_teorica.append(np.nan)
        else:
            Rad_teorica.append(punto.iloc[rad].values[0])

    data_Theorical = pd.DataFrame()
    data_Theorical['fecha_hora'] = fechas
    data_Theorical['Radiacion_Teo'] = Rad_teorica

    data_Theorical.index = data_Theorical['fecha_hora']

    df_hourly_theoric = data_Theorical.groupby(pd.Grouper(freq="H")).mean()

    df_hourly_theoric = df_hourly_theoric[df_hourly_theoric['Radiacion_Teo'] > 0]

    return df_hourly_theoric


def Elevation_RadiationTA(n, lat, lon, start):
    'Para obtener la radiación en W/m2 y el ángulo de elevación del sol en grados horariamente para un número "n" de ' \
    'días aun punto en una latitud y longitud determinada ( "lat-lon"como flotantes) a partir de una fecha de inicio ' \
    '"start" como por ejemplo datetime.datetime(2018, 1, 1, 8).'
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

    return days, altitudes_deg, radiations


if Theoric_rad_method != 'GIS_Model' and Estacion == '6001':
    days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, 6.259, -75.588, datetime.datetime(2018, 1, 1, 0))
    print('Teorica con pysolar')
elif Theoric_rad_method != 'GIS_Model' and Estacion == '6002':
    days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, 6.168, -75.644, datetime.datetime(2018, 1, 1, 0))
    print('Teorica con pysolar')
elif Theoric_rad_method != 'GIS_Model' and Estacion == '6003':
    days, altitudes_deg, Io_hora = Elevation_RadiationTA(365, 6.255, -75.542, datetime.datetime(2018, 1, 1, 0))
    print('Teorica con pysolar')
elif Theoric_rad_method == 'GIS_Model':
    Io_hora = serie_Kumar_Model_hora(Estacion)
    print('Teorica con el modelo de KUMAR')

###############################################################################
##--------------EFICIENCIAS TEORICAS COMO PROXI DE TRANSPARENCIA-------------##
###############################################################################
'Calculo de la eficiencias teorica como proxi de la transparencia de la atmosfera'
'Para esto se hace uso de la información del piranometro y de la radiación teórica'
'de Gisel Guzman, con esto se prentenden obtener las caracteristicas que deriven'
'del análisis estocastico, similar al de Estefanía Muñoz en su tesis de doctorado.'

##------------------LECTURA DE LOS DATOS DEL EXPERIMENTO----------------------##
df_P975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel975.txt',  sep=',', index_col =0)
df_P350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel350.txt',  sep=',', index_col =0)
df_P348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel348.txt',  sep=',', index_col =0)

df_P975['Fecha_hora'] = df_P975.index
df_P350['Fecha_hora'] = df_P350.index
df_P348['Fecha_hora'] = df_P348.index

df_P975.index = pd.to_datetime(df_P975.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P350.index = pd.to_datetime(df_P350.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P348.index = pd.to_datetime(df_P348.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

## ----------------ACOTANDO LOS DATOS A VALORES VÁLIDOS---------------- ##

'Como en este caso lo que interesa es la radiacion, para la filtración de los datos, se'
'considerarán los datos de potencia mayores o iguales a 0, los que parecen generarse una'
'hora despues de cuando empieza a incidir la radiación.'

df_P975 = df_P975[(df_P975['radiacion'] > 0) & (df_P975['strength'] >=0) & (df_P975['NI'] >=0)]
df_P350 = df_P350[(df_P350['radiacion'] > 0) & (df_P975['strength'] >=0) & (df_P975['NI'] >=0)]
df_P348 = df_P348[(df_P348['radiacion'] > 0) & (df_P975['strength'] >=0) & (df_P975['NI'] >=0)]

df_P975_h = df_P975.groupby(pd.Grouper(level='fecha_hora', freq='1H')).mean()
df_P350_h = df_P350.groupby(pd.Grouper(level='fecha_hora', freq='1H')).mean()
df_P348_h = df_P348.groupby(pd.Grouper(level='fecha_hora', freq='1H')).mean()

df_P975_h = df_P975_h.between_time('06:00', '17:00')
df_P350_h = df_P350_h.between_time('06:00', '17:00')
df_P348_h = df_P348_h.between_time('06:00', '17:00')

##----AJUSTE DE LOS DATOS DE RADIACIÓN TEORICA AL RANGO DE FECHAS DESEADO-----##

def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada hora. Las fechas'
    'final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=60)
    while start_date <= end_date:
        yield start_date
        start_date += delta

Io_hora_975 = serie_Kumar_Model_hora('6001')
Io_hora_350 = serie_Kumar_Model_hora('6002')
Io_hora_348 = serie_Kumar_Model_hora('6003')


fechas_975 = []
for i in daterange(df_P975.index[0].date().strftime("%Y-%m-%d"), (df_P975.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_975.append(i)

fechas_350 = []
for i in daterange(df_P350.index[0].date().strftime("%Y-%m-%d"), (df_P350.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_350.append(i)

fechas_348 = []
for i in daterange(df_P348.index[0].date().strftime("%Y-%m-%d"), (df_P348.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_348.append(i)

Io_hora_975 = Io_hora_975.loc[(Io_hora_975.index >= '2018-03-20') & (Io_hora_975.index <= '2018-'+str(df_P975.index[-1].month)+'-'+str(df_P975.index[-1].day+1))]
Io_hora_350 = Io_hora_350.loc[(Io_hora_350.index >= '2018-03-22') & (Io_hora_350.index <= '2018-'+str(df_P350.index[-1].month)+'-'+str(df_P350.index[-1].day+1))]
Io_hora_348 = Io_hora_348.loc[(Io_hora_348.index >= '2018-03-23') & (Io_hora_348.index <= '2018-'+str(df_P348.index[-1].month)+'-'+str(df_P348.index[-1].day+1))]

Io_hora_975 = Io_hora_975.between_time('06:00', '17:00')
Io_hora_975.index = [Io_hora_975.index[i].replace(year=2019) for i in range(len(Io_hora_975.index))]

Io_hora_350 = Io_hora_350.between_time('06:00', '17:00')
Io_hora_350.index = [Io_hora_350.index[i].replace(year=2019) for i in range(len(Io_hora_350.index))]

Io_hora_348 = Io_hora_348.between_time('06:00', '17:00')
Io_hora_348.index = [Io_hora_348.index[i].replace(year=2019) for i in range(len(Io_hora_348.index))]

df_Rad_P975 = pd.concat([Io_hora_975, df_P975_h], axis = 1)
df_Rad_P350 = pd.concat([Io_hora_350, df_P350_h], axis = 1)
df_Rad_P348 = pd.concat([Io_hora_348, df_P348_h], axis = 1)

df_Rad_P975 =  df_Rad_P975.drop(['NI','strength'], axis=1)
df_Rad_P350 =  df_Rad_P350.drop(['NI','strength'], axis=1)
df_Rad_P348 =  df_Rad_P348.drop(['NI','strength'], axis=1)

##--------------------EFICIANCIA REAL PROXI DE TRANSPARENCIA-----------------##

df_Rad_P975['Efi_Transp'] = df_Rad_P975['radiacion'] / df_Rad_P975['Radiacion_Teo']
df_Rad_P350['Efi_Transp'] = df_Rad_P350['radiacion'] / df_Rad_P350['Radiacion_Teo']
df_Rad_P348['Efi_Transp'] = df_Rad_P348['radiacion'] / df_Rad_P348['Radiacion_Teo']

##-----------------HORAS EN LA QUE SE PRODUCE LA MAYOR EFICIENCIA Y SU HISTOGRAMA-------------##
'La frecuencia de las horas que excedieron el máximo de la eficiencia (1), se presenta en el hisograma'
'a continuación. El resultado muestra que las mayores frecuencias se presentan a als 6 y las 7 de la ma-'
'ñana, y esto es atribuible a falencias en el modelo de radiacion en condiciones de cierlo despejado'
'en esos puntos.'

Hour_Max_Efi_975 = df_Rad_P975[df_Rad_P975['Efi_Transp']>1].index.hour
Hour_Max_Efi_350 = df_Rad_P350[df_Rad_P350['Efi_Transp']>1].index.hour
Hour_Max_Efi_348 = df_Rad_P348[df_Rad_P348['Efi_Transp']>1].index.hour

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Hour_Max_Efi_348, bins='auto', alpha = 0.5)
ax1.set_title(u'Distribución horas de excedencia \n de la eficiencia en JV', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Horas', fontproperties=prop_1)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Hour_Max_Efi_350, bins='auto', alpha = 0.5)
ax2.set_title(u'Distribución horas de excedencia \n de la eficiencia en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Horas', fontproperties=prop_1)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Hour_Max_Efi_975, bins='auto', alpha = 0.5)
ax3.set_title(u'Distribución horas de excedencia \n de la eficiencia en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Horas', fontproperties=prop_1)
ax3.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoHoraExceEfi.png')
plt.show()

##-------DISCRIMINACION ENTRE DIAS LLUVIOSOS Y SECOS POR PERCENTILES DE RADIACION--------##

'Para lidiar cno la situación en que pueden haber dias en los que los piranometros solo midieron'
'durante una fracción del día por posibles daños y alteraciones, se deben considerar los dias que'
'al menos tuvieron 6 horas de medicion.'

df_Rad_P975_count_h_pira = df_Rad_P975.groupby(pd.Grouper(freq="D")).count()['radiacion']>6
df_Rad_P350_count_h_pira = df_Rad_P350.groupby(pd.Grouper(freq="D")).count()['radiacion']>6
df_Rad_P348_count_h_pira = df_Rad_P348.groupby(pd.Grouper(freq="D")).count()['radiacion']>6

days_P975_count_h_pira = df_Rad_P975_count_h_pira.index[df_Rad_P975_count_h_pira == True]
days_P350_count_h_pira = df_Rad_P350_count_h_pira.index[df_Rad_P350_count_h_pira == True]
days_P348_count_h_pira = df_Rad_P348_count_h_pira.index[df_Rad_P348_count_h_pira == True]

'Se establecieron umbrales empiricamente para la seleccion de los dias marcadamente nubados y'
'marcadamente despejados dentro el periodo de registro,  de acuerdo a los procedimentos en el'
'programa Umbrales_Radiacion_Piranometro.py'

Sum_df_Rad_P975 = df_Rad_P975.groupby(pd.Grouper(freq='1D')).sum()
Sum_df_Rad_P350 = df_Rad_P350.groupby(pd.Grouper(freq='1D')).sum()
Sum_df_Rad_P348 = df_Rad_P348.groupby(pd.Grouper(freq='1D')).sum()

Sum_df_Rad_P975 = Sum_df_Rad_P975[Sum_df_Rad_P975['radiacion']>0]
Sum_df_Rad_P350 = Sum_df_Rad_P350[Sum_df_Rad_P350['radiacion']>0]
Sum_df_Rad_P348 = Sum_df_Rad_P348[Sum_df_Rad_P348['radiacion']>0]

lista_days_975 = []
for i in range(len(Sum_df_Rad_P975)):
    if Sum_df_Rad_P975.index[i] in days_P975_count_h_pira:
        lista_days_975.append(1)
    else:
        lista_days_975.append(0)
Sum_df_Rad_P975['days'] = lista_days_975
Sum_df_Rad_P975 = Sum_df_Rad_P975[Sum_df_Rad_P975['days'] == 1]
Sum_df_Rad_P975 = Sum_df_Rad_P975.drop(['days'], axis = 1)

lista_days_350 = []
for i in range(len(Sum_df_Rad_P350)):
    if Sum_df_Rad_P350.index[i] in days_P350_count_h_pira:
        lista_days_350.append(1)
    else:
        lista_days_350.append(0)
Sum_df_Rad_P350['days'] = lista_days_350
Sum_df_Rad_P350 = Sum_df_Rad_P350[Sum_df_Rad_P350['days'] == 1]
Sum_df_Rad_P350 = Sum_df_Rad_P350.drop(['days'], axis = 1)

lista_days_348 = []
for i in range(len(Sum_df_Rad_P348)):
    if Sum_df_Rad_P348.index[i] in days_P348_count_h_pira:
        lista_days_348.append(1)
    else:
        lista_days_348.append(0)
Sum_df_Rad_P348['days'] = lista_days_348
Sum_df_Rad_P348 = Sum_df_Rad_P348[Sum_df_Rad_P348['days'] == 1]
Sum_df_Rad_P348 = Sum_df_Rad_P348.drop(['days'], axis = 1)

Desp_Pira_975 = Sum_df_Rad_P975[Sum_df_Rad_P975.radiacion>=(Sum_df_Rad_P975.Radiacion_Teo)*0.85]
Desp_Pira_350 = Sum_df_Rad_P350[Sum_df_Rad_P350.radiacion>=(Sum_df_Rad_P350.Radiacion_Teo)*0.78]
Desp_Pira_348 = Sum_df_Rad_P348[Sum_df_Rad_P348.radiacion>=(Sum_df_Rad_P348.Radiacion_Teo)*0.80]

Nuba_Pira_975 = Sum_df_Rad_P975[Sum_df_Rad_P975.radiacion<=(Sum_df_Rad_P975.Radiacion_Teo)*0.25]
Nuba_Pira_350 = Sum_df_Rad_P350[Sum_df_Rad_P350.radiacion<=(Sum_df_Rad_P350.Radiacion_Teo)*0.25]
Nuba_Pira_348 = Sum_df_Rad_P348[Sum_df_Rad_P348.radiacion<=(Sum_df_Rad_P348.Radiacion_Teo)*0.22]

Appended_data_desp_975 = []
for i in range(len(Desp_Pira_975.index.values)):
    Appended_data_desp_975.append(df_P975_h[df_P975_h.index.date == Desp_Pira_975.index.date[i]])
Appended_data_desp_975 = pd.concat(Appended_data_desp_975)

Appended_data_desp_350 = []
for i in range(len(Desp_Pira_350.index.values)):
    Appended_data_desp_350.append(df_P350_h[df_P350_h.index.date == Desp_Pira_350.index.date[i]])
Appended_data_desp_350 = pd.concat(Appended_data_desp_350)

Appended_data_desp_348 = []
for i in range(len(Desp_Pira_348.index.values)):
    Appended_data_desp_348.append(df_P348_h[df_P348_h.index.date == Desp_Pira_348.index.date[i]])
Appended_data_desp_348 = pd.concat(Appended_data_desp_348)

Appended_data_nuba_975 = []
for i in range(len(Nuba_Pira_975.index.values)):
    Appended_data_nuba_975.append(df_P975_h[df_P975_h.index.date == Nuba_Pira_975.index.date[i]])
Appended_data_nuba_975 = pd.concat(Appended_data_nuba_975)

Appended_data_nuba_350 = []
for i in range(len(Nuba_Pira_350.index.values)):
    Appended_data_nuba_350.append(df_P350_h[df_P350_h.index.date == Nuba_Pira_350.index.date[i]])
Appended_data_nuba_350 = pd.concat(Appended_data_nuba_350)

Appended_data_nuba_348 = []
for i in range(len(Nuba_Pira_348.index.values)):
    Appended_data_nuba_348.append(df_P348_h[df_P348_h.index.date == Nuba_Pira_348.index.date[i]])
Appended_data_nuba_348 = pd.concat(Appended_data_nuba_348)

#------------------HISTOGRAMAS  DE RADIACION PARA CADA PUNTO EN LOS DOS CASOS----------------##

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Appended_data_desp_348['radiacion'], bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax1.hist(Appended_data_nuba_348['radiacion'], bins='auto', alpha = 0.5, color = 'blue', label = 'Nub')
ax1.set_title(u'Distribución de la radiación \n en dias dispejados y nublados en JV', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Radiación $[W/m^{2}]$', fontproperties=prop_1)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Appended_data_desp_350['radiacion'], bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax2.hist(Appended_data_nuba_350['radiacion'], bins='auto', alpha = 0.5,  color = 'blue', label = 'Nub')
ax2.set_title(u'Distribución de la radiación \n en dias dispejados y nublados en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Radiación $[W/m^{2}]$', fontproperties=prop_1)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Appended_data_desp_975['radiacion'], bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax3.hist(Appended_data_nuba_975['radiacion'], bins='auto', alpha = 0.5,  color = 'blue', label = 'Nub')
ax3.set_title(u'Distribución de la radiación \n en dias dispejados y nublados en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Radiación $[W/m^{2}]$', fontproperties=prop_1)
ax3.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoRadiacionNubaDespTotal.png')
plt.show()

#------------------PRUEBA DE KOLMOGOROV-SMIRNOV PARA LA BONDAD DE AJUSTE ----------------##
'Se aplica la prueba de bondad KOLMOGOROV-SMIRNOV sobre los datos de los dias nublados y los'
'despejados  con respecto a la serie general de los datos, para evaluar si pertenecen a la '
'funcion de distribución de probabilidad. Se usa un nivel de significancia del 5%. Esta prueba es'
'mas sensible a los valores cercanos a la media que a los extremos, por lo que en general puede'
'usarse para evitar los outliers. La hipotesis nula, será que los datos  de ambas series siguen'
'una misma distribución. La hipotesis alternativa sugiere que no sigen la misma distribución.'

Significancia = 0.05

SK_desp_348 = ks_2samp(Appended_data_desp_348['radiacion'].values,df_P348_h['radiacion'].values)
stat_348_desp = SK_desp_348[0]
pvalue_348_desp = SK_desp_348[1]

SK_nuba_348 = ks_2samp(Appended_data_nuba_348['radiacion'].values,df_P348_h['radiacion'].values)
stat_348_nuba = SK_nuba_348[0]
pvalue_348_nuba = SK_nuba_348[1]

if pvalue_348_nuba <= Significancia:
    print ('los dias nublados en JV  no pertenecen a la misma distribución')
else:
    print ('los dias nublados en JV  pertenecen a la misma distribución')

if pvalue_348_desp <= Significancia:
    print ('los dias despejados en JV no pertenecen a la misma distribución')
else:
    print ('los dias despejados en JV pertenecen a la misma distribución')

SK_desp_350 = ks_2samp(Appended_data_desp_350['radiacion'].values,df_P350_h['radiacion'].values)
stat_350_desp = SK_desp_350[0]
pvalue_350_desp = SK_desp_350[1]

SK_nuba_350 = ks_2samp(Appended_data_nuba_350['radiacion'].values,df_P350_h['radiacion'].values)
stat_350_nuba = SK_nuba_350[0]
pvalue_350_nuba = SK_nuba_350[1]

if pvalue_350_nuba <= Significancia:
    print ('los dias nublados en CI no pertenecen a la misma distribución')
else:
    print ('los dias nublados en CI pertenecen a la misma distribución')

if pvalue_350_desp <= Significancia:
    print ('los dias despejados en CI  no pertenecen a la misma distribución')
else:
    print ('los dias despejados en CI pertenecen a la misma distribución')

SK_desp_975 = ks_2samp(Appended_data_desp_975['radiacion'].values,df_P975_h['radiacion'].values)
stat_975_desp = SK_desp_975[0]
pvalue_975_desp = SK_desp_975[1]

SK_nuba_975 = ks_2samp(Appended_data_nuba_975['radiacion'].values,df_P975_h['radiacion'].values)
stat_975_nuba = SK_nuba_975[0]
pvalue_975_nuba = SK_nuba_975[1]

if pvalue_975_nuba <= Significancia:
    print ('los dias nublados en TS no pertenecen a la misma distribución')
else:
    print ('los dias nublados en TS  pertenecen a la misma distribución')

if pvalue_975_desp <= Significancia:
    print ('los dias despejados en TS no pertenecen a la misma distribución')
else:
    print ('los dias despejados en TS  pertenecen a la misma distribución')

#------------------HISTOGRAMAS  DE EFICIENCIA PARA CADA PUNTO EN LOS DOS CASOS----------------##
Desp_Efi_348 = []
for i in range(len(Desp_Pira_348.index.values)):
    Desp_Efi_348.append(df_Rad_P348[df_Rad_P348.index.date == Desp_Pira_348.index.date[i]])
Desp_Efi_348 = pd.concat(Desp_Efi_348)

Desp_Efi_350 = []
for i in range(len(Desp_Pira_350.index.values)):
    Desp_Efi_350.append(df_Rad_P350[df_Rad_P350.index.date == Desp_Pira_350.index.date[i]])
Desp_Efi_350 = pd.concat(Desp_Efi_350)

Desp_Efi_975 = []
for i in range(len(Desp_Pira_975.index.values)):
    Desp_Efi_975.append(df_Rad_P975[df_Rad_P975.index.date == Desp_Pira_975.index.date[i]])
Desp_Efi_975 = pd.concat(Desp_Efi_975)

Nuba_Efi_348 = []
for i in range(len(Nuba_Pira_348.index.values)):
    Nuba_Efi_348.append(df_Rad_P348[df_Rad_P348.index.date == Nuba_Pira_348.index.date[i]])
Nuba_Efi_348 = pd.concat(Nuba_Efi_348)

Nuba_Efi_350 = []
for i in range(len(Nuba_Pira_350.index.values)):
    Nuba_Efi_350.append(df_Rad_P350[df_Rad_P350.index.date == Nuba_Pira_350.index.date[i]])
Nuba_Efi_350 = pd.concat(Nuba_Efi_350)

Nuba_Efi_975 = []
for i in range(len(Nuba_Pira_975.index.values)):
    Nuba_Efi_975.append(df_Rad_P975[df_Rad_P975.index.date == Nuba_Pira_975.index.date[i]])
Nuba_Efi_975 = pd.concat(Nuba_Efi_975)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(Desp_Efi_348['Efi_Transp'], bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax1.hist(Nuba_Efi_348['Efi_Transp'], bins='auto', alpha = 0.5, color = 'blue', label = 'Nub')
ax1.set_title(u'Distribución de la eficiencia \n en dias despejados y nublados en JV', fontproperties=prop, fontsize = 8)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Eficiencia', fontproperties=prop_1)
ax1.legend()

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(Desp_Efi_350['Efi_Transp'], bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax2.hist(Nuba_Efi_350['Efi_Transp'], bins='auto', alpha = 0.5,  color = 'blue', label = 'Nub')
ax2.set_title(u'Distribución de la eficiencia \n en dias despejados y nublados en CI', fontproperties=prop, fontsize = 8)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Eficiencia', fontproperties=prop_1)
ax2.legend()

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(Desp_Efi_975['Efi_Transp'], bins='auto', alpha = 0.5, color = 'orange', label = 'Desp')
ax3.hist(Nuba_Efi_975['Efi_Transp'], bins='auto', alpha = 0.5,  color = 'blue', label = 'Nub')
ax3.set_title(u'Distribución de la eficiencia \n en dias despejados y nublados en TS', fontproperties=prop, fontsize = 8)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Eficiencia', fontproperties=prop_1)
ax3.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoEficiencianNubaDespTotal.png')
plt.show()



SK_desp_Efi_348 = ks_2samp(Desp_Efi_348['radiacion'].values,df_P348_h['radiacion'].values)
Efi_348_desp = SK_desp_Efi_348[0]
Efi_348_desp = SK_desp_Efi_348[1]

SK_nuba_Efi_348 = ks_2samp(Nuba_Efi_348['radiacion'].values,df_P348_h['radiacion'].values)
Efi_348_nuba = SK_nuba_Efi_348[0]
Efi_348_nuba = SK_nuba_Efi_348[1]

if Efi_348_nuba <= Significancia:
    print ('los dias nublados en JV  no pertenecen a la misma distribución')
else:
    print ('los dias nublados en JV  pertenecen a la misma distribución')

if Efi_348_desp <= Significancia:
    print ('los dias despejados en JV no pertenecen a la misma distribución')
else:
    print ('los dias despejados en JV pertenecen a la misma distribución')

SK_desp_Efi_350 = ks_2samp(Desp_Efi_350['radiacion'].values,df_P350_h['radiacion'].values)
Efi_350_desp = SK_desp_Efi_350[0]
Efi_350_desp = SK_desp_Efi_350[1]

SK_nuba_Efi_350 = ks_2samp(Nuba_Efi_350['radiacion'].values,df_P350_h['radiacion'].values)
Efi_350_nuba = SK_nuba_Efi_350[0]
Efi_350_nuba = SK_nuba_Efi_350[1]

if Efi_350_nuba <= Significancia:
    print ('los dias nublados en CI no pertenecen a la misma distribución')
else:
    print ('los dias nublados en CI pertenecen a la misma distribución')

if Efi_350_desp <= Significancia:
    print ('los dias despejados en CI  no pertenecen a la misma distribución')
else:
    print ('los dias despejados en CI pertenecen a la misma distribución')

SK_desp_Efi_975 = ks_2samp(Desp_Efi_975['radiacion'].values,df_P975_h['radiacion'].values)
Efi_975_desp = SK_desp_Efi_975[0]
Efi_975_desp = SK_desp_Efi_975[1]

SK_nuba_Efi_975 = ks_2samp(Nuba_Efi_975['radiacion'].values,df_P975_h['radiacion'].values)
Efi_975_nuba = SK_nuba_Efi_975[0]
Efi_975_nuba = SK_nuba_Efi_975[1]

if Efi_975_nuba <= Significancia:
    print ('los dias nublados en TS no pertenecen a la misma distribución')
else:
    print ('los dias nublados en TS  pertenecen a la misma distribución')

if Efi_975_desp <= Significancia:
    print ('los dias despejados en TS no pertenecen a la misma distribución')
else:
    print ('los dias despejados en TS  pertenecen a la misma distribución')







#------------------ESTIMACIÓN DE LA AUTOCORRELACIÓN EN CADA PUNTO----------------##

def estimated_autocorrelation(x):
    """
    http://stackoverflow.com/q/14297012/190597
    http://en.wikipedia.org/wiki/Autocorrelation#Estimation
    """
    n = len(x)
    variance = x.var()
    x = x-x.mean()
    r = np.correlate(x, x, mode = 'full')[-n:]
    assert np.allclose(r, np.array([(x[:n-k]*x[-(n-k):]).sum() for k in range(n)]))
    result = r/(variance*(np.arange(n, 0, -1)))
    return result

Auto_corr_975 = estimated_autocorrelation(df_P975_h['radiacion'].values)


X = df_P975_h[df_P975_h['radiacion'].values>0]['radiacion'].values
lag = [1, 6, 12, 24]
AutoCorr_lag = []
for j in range(1, len(lag)+1):
    print(j)
    c = []
    for i in range(0,len(X)-j, j):
        c.append(pearsonr(X[i:], X[:-(i -len(X))])[1])
    AutoCorr_lag.append(sum(c))

































###############################################################################
##-------------------RADIACION TEORICA PARA UN AÑO DE DATOS------------------##
###############################################################################
'Se espera encontrar con una año de datos de radiacion teorica para el estable-'
'cimiento de los  escenario de prediccion y de los rendimentos teoricos. Pensado'
'para los datos de 2018.'

## ---LECTURA DE DATOS DE PIRANÓMETRO --- ##
df1 = df1.set_index(["fecha_hora"])
df1.index = df1.index.tz_localize('UTC').tz_convert('America/Bogota')
df1.index = df1.index.tz_localize(None)

## ---AGRUPACION DE LOS DATOS HORARIOS A UN AÑO--- ##
df1_hora = df1.groupby(pd.Grouper(freq="H")).mean()
df1_hora = df1_hora[(df1_hora.index >= '2018-01-01 00:00:00') & (df1_hora.index <= '2018-12-31 23:59:00')]
df1_hora = df1_hora.between_time('06:00', '17:00')                      ##--> Seleccionar solo los datos de horas del dia

## ---CREACIÓN DE LA RADIACIÓN EN SUPERFICIE POR DIA Y AGRUPACION DE LOS DATOS DIARIOS A UN AÑO--- ##
Io_dia = Io.groupby(pd.Grouper(freq="D")).mean()
df1_dia = df1.groupby(pd.Grouper(freq="D")).mean()
df1_dia = df1_dia[(df1_dia.index >= '2018-01-01') & (df1_dia.index <= '2018-12-31')]

## ---CONDICIONANDO LA RESOLUCIÓN TEMPORAL CON LA QUE SE TRABAJARÁ--- ##
if resolucion == 'diaria':
    Io = Io_dia
    df1_rad = df1_dia
elif resolucion == 'horaria':
    Io = Io_hora
    df1_rad = df1_hora

## ---CREACIÓN DE LOS ESCENARIOS DE ANÁLISIS EFICIENCIA TEÓRICA--- ##
if len(Io)==len(df1_rad):
    df1_rad['TAR'] = Io
    df1_rad = df1_rad.drop([u'Unnamed: 0', u'idestacion'], axis=1)
    df1_rad['Efi_Teorica'] = df1_rad[u'radiacion']/df1_rad[u'TAR']
else:
    print (u'No hay un año de datos con el piranometro')

## --Máximo absosluto

df1_radr_max = df1_rad.loc[lambda df_hora: df_hora['Efi_Teorica'] == np.nanmax(df1_rad.Efi_Teorica)]

## -- Percentil 90 absoluto

df1_rad90 = df1_rad.quantile(0.90)

## -- Percentil 50 absoluto

df1_rad50 = df1_rad.quantile(0.50)

## -- Percentil 10 absoluto

df1_rad10 = df1_rad.quantile(0.10)

              ## -----MENSUAL----- ##
df1_hm_mean = df1_rad.Efi_Teorica.groupby(pd.Grouper(freq="M")).mean()
df1_hm_mean_90 = df1_hm_mean.loc[lambda df1_hm_mean: df1_hm_mean.round(3) >= round(df1_hm_mean.quantile(0.90), 2)]
df1_hm_mean_50 = df1_hm_mean.loc[lambda df1_hm_mean: df1_hm_mean.round(3) >= round(df1_hm_mean.quantile(0.50), 2)]
df1_hm_mean_10 = df1_hm_mean.loc[lambda df1_hm_mean: df1_hm_mean.round(3) >= round(df1_hm_mean.quantile(0.10), 2)]

## -- Percentil 90 de cada mes

df1_hm_quantile90 = df1_rad.Efi_Teorica.groupby(pd.Grouper(freq="M")).quantile(0.90)

## -- Percentil 50 de cada mes

df1_hm_quantile50 = df1_rad.Efi_Teorica.groupby(pd.Grouper(freq="M")).quantile(0.50)

## -- Percentil 10 de cada mes

df1_hm_quantile10 = df1_rad.Efi_Teorica.groupby(pd.Grouper(freq="M")).quantile(0.10)

## -----GRÁFICA PARA OBTENER LOS ESCENARIOS----- ##
new_index = [df1_hm_quantile90.index[i].replace(day=1) for i in range(len(df1_hm_quantile90.index))]
df1_hm_quantile90.index = new_index
fechas_grafica = [str(df1_hm_quantile90.index[i])[0:10] for i in range(len(df1_hm_quantile90.index))]
ind_f = np.arange(len(fechas_grafica) )

if Estacion == '6001':
    EstacionLoc = 'Torre SIATA'
elif Estacion== '6002':
    EstacionLoc = 'Consejo Ita'
elif Estacion== '6003':
    EstacionLoc = 'Joaquin Vallejo'


fig = plt.figure(figsize=(12, 9))
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.plot(df1_hm_quantile90.index, df1_hm_quantile90*100, color='#52B7C4', linewidth=2, label = 'P_Mensual 90')
ax.plot(df1_hm_quantile90.index, df1_hm_quantile50*100, color='#ffa040', linewidth=2, label = 'P_Mensual 50')
ax.plot(df1_hm_quantile90.index, df1_hm_quantile10*100, color='#0b6623', linewidth=2, label = 'P_Mensual 10')
ax.legend()
ax.scatter(df1_hm_quantile90.index, df1_hm_quantile90*100, color='#52B7C4', s=20)
ax.scatter(df1_hm_quantile90.index, df1_hm_quantile50*100, color='#ffa040', s=20)
ax.scatter(df1_hm_quantile90.index, df1_hm_quantile10*100, color='#0b6623', s=20)
ax.set_ylim(0, np.nanmax(df1_hm_quantile90*100)*1.1)
ax.set_xlim(fechas_grafica[0], fechas_grafica[-1])
ax.axhline(y=df1_rad90.Efi_Teorica*100)
ax.axhline(y=df1_rad50.Efi_Teorica*100)
ax.axhline(y=df1_rad10.Efi_Teorica*100)
plt.ylabel('Rendimiento', fontsize=14, fontproperties=prop, color='gray')
plt.xlabel('Meses', fontsize=18, fontproperties=prop, color='gray')
plt.title(u'Percentiles mensuales y absolutos de los datos de radiación de 2018 en: ' + EstacionLoc, size=16, fontproperties=prop_2, color='gray')
hfmt = mdates.DateFormatter('%Y-%m')
ax.tick_params(color='gray', labelcolor='gray')
for spine in ax.spines.values():
    spine.set_edgecolor('gray')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.xaxis.set_major_formatter(hfmt)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Escenarios_Perc.png')
plt.show()

## ---RELACIÓN CON LAS DEMÁS VARIABLES IMPLICADAS--- ##

data_thiess = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Historico_Brillo_1019.txt',  sep=',')

## -- Filtrar por calidad
df_brillo = data_thiess[data_thiess['calidad'] < 100]

df_brillo.index = df_brillo['fecha_hora']
df_brillo = df_brillo.drop(['fecha_hora'], axis=1)
df_brillo.index = pd.to_datetime(df_brillo.index)
df_brillo = df_brillo[(df_brillo.index >= '2018-01-01 00:00:00') & (df_brillo.index <= '2018-12-31 23:59:00')]
df_brillo_h = df_brillo.groupby(pd.Grouper(freq="H")).mean()

df1_rad['T'] = df_brillo_h['T']
df1_rad['BM'] = df_brillo_h['BM']

## -- Obtener solo los datos de dia

df1_rad_dia = df1_rad[(df1_rad.index.hour >= 6) & (df1_rad.index.hour < 18)]

## -- Sacar los datos para las fechas de los escenarios

          ## -- Escenarios máximos

fh_i_max = ['2018-06-01 00:00:00', '2018-08-01 00:00:00', '2018-12-01 00:00:00']
fh_f_max = ['2018-06-30 23:59:00', '2018-08-31 23:59:00', '2018-12-31 23:59:00']

df_max_esc01 = df1_rad_dia[(df1_rad_dia.index >= fh_i_max[0]) & (df1_rad_dia.index <= fh_f_max[0])]
df_max_esc02 = df1_rad_dia[(df1_rad_dia.index >= fh_i_max[1]) & (df1_rad_dia.index <= fh_f_max[1])]
df_max_esc03 = df1_rad_dia[(df1_rad_dia.index >= fh_i_max[2]) & (df1_rad_dia.index <= fh_f_max[2])]


           ## -- Acotando los fuera de rango
df_max_esc01 = df_max_esc01[df_max_esc01[u'Efi_Teorica'] < 2.5]
df_max_esc02 = df_max_esc02[df_max_esc02[u'Efi_Teorica'] < 2.5]
df_max_esc03 = df_max_esc03[df_max_esc03[u'Efi_Teorica'] < 2.5]

                        ## -- Correlaciones de la eficiencia teórica
corr_BM_max_esc01, p_value_BM_max_esc01 = pearsonr(df_max_esc01[u'Efi_Teorica'].values, df_max_esc01[u'BM'].values)
corr_T_max_esc01, p_value_BM_max_esc01 = pearsonr(df_max_esc01[u'Efi_Teorica'].values, df_max_esc01[u'T'].values)

corr_BM_max_esc02, p_value_BM_max_esc02 = pearsonr(df_max_esc02[u'Efi_Teorica'].values, df_max_esc02[u'BM'].values)
corr_T_max_esc02, p_value_BM_max_esc02 = pearsonr(df_max_esc02[u'Efi_Teorica'].values, df_max_esc02[u'T'].values)

corr_BM_max_esc03, p_value_BM_max_esc03 = pearsonr(df_max_esc03[u'Efi_Teorica'].values, df_max_esc03[u'BM'].values)
corr_T_max_esc03, p_value_BM_max_esc03 = pearsonr(df_max_esc03[u'Efi_Teorica'].values, df_max_esc03[u'T'].values)


                        ## -- Gráfico con la temperatura

jet = plt.get_cmap('jet')
fig = plt.figure(figsize=[11, 10])

ax1 = fig.add_subplot(1, 3, 1)
sc1 = ax1.scatter(df_max_esc01['radiacion'], df_max_esc01['Efi_Teorica'], s=10, c=df_max_esc01['T'],  cmap=jet)
cbar1 = ax1.figure.colorbar(sc1)
cbar1.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar1.ax.tick_params(pad=-15, labelsize=6)
ax1.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax1.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax1.set_title("Escenario del mes:" + str(df_max_esc01.index.month[0]), fontsize=10)
#ax1.text(max(df_max_esc01['radiacion']), max(df_max_esc01['Efi_Teorica']), 'Corr Coef: '+ str(corr_T_max_esc01.round(2)) + ' $P value$: '+ str(p_value_BM_max_esc01.round(2)), style='italic',  ha="center",   bbox={'facecolor':'#D6EAF8', 'alpha':0.5, 'pad':-1})

ax2 = fig.add_subplot(1, 3, 2)
sc2 = ax2.scatter(df_max_esc02['radiacion'], df_max_esc02['Efi_Teorica'], s=10, c=df_max_esc02['T'],  cmap=jet)
cbar2 = plt.colorbar(sc2)
cbar2.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar2.ax.tick_params(pad=-15, labelsize=6)
ax2.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax2.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax2.set_title("Escenario del mes:" + str(df_max_esc02.index.month[0]), fontsize=10)

ax3 = fig.add_subplot(1, 3, 3)
sc3 = ax3.scatter(df_max_esc03['radiacion'], df_max_esc03['Efi_Teorica'], s=10, c=df_max_esc03['T'],  cmap=jet)
cbar3 = plt.colorbar(sc3)
cbar3.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar3.ax.tick_params(pad=-15, labelsize=6)
ax3.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax3.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax3.set_title("Escenario del mes:" + str(df_max_esc03.index.month[0]), fontsize=10)

plt.subplots_adjust( wspace=0.3, hspace=1)
fig.suptitle(u"Relación de las eficiencias máximas", fontsize=11, fontweight = "bold",  fontproperties = prop)
plt.show()
#plt.savefig('/home/nacorreasa/Escritorio/EScenario1.png')
plt.close()


          ## -- Escenarios mínimos

fh_i_min = ['2018-02-01 00:00:00', '2018-03-01 00:00:00', '2018-04-01 00:00:00', '2018-05-01 00:00:00', '2018-11-01 00:00:00']
fh_f_min = ['2018-02-28 23:59:00', '2018-03-30 23:59:00', '2018-04-30 23:59:00', '2018-05-31 23:59:00', '2018-11-30 23:59:00']

df_min_esc01 = df1_rad_dia[(df1_rad_dia.index >= fh_i_min[0]) & (df1_rad_dia.index <= fh_f_min[0])]
df_min_esc02 = df1_rad_dia[(df1_rad_dia.index >= fh_i_min[1]) & (df1_rad_dia.index <= fh_f_min[1])]
df_min_esc03 = df1_rad_dia[(df1_rad_dia.index >= fh_i_min[2]) & (df1_rad_dia.index <= fh_f_min[2])]
df_min_esc04 = df1_rad_dia[(df1_rad_dia.index >= fh_i_min[3]) & (df1_rad_dia.index <= fh_f_min[3])]
df_min_esc05 = df1_rad_dia[(df1_rad_dia.index >= fh_i_min[4]) & (df1_rad_dia.index <= fh_f_min[4])]


           ## -- Acotando los fuera de rango
df_min_esc01 = df_min_esc01[df_min_esc01[u'Efi_Teorica'] < 2.5]
df_min_esc02 = df_min_esc02[df_min_esc02[u'Efi_Teorica'] < 2.5]
df_min_esc03 = df_min_esc03[df_min_esc03[u'Efi_Teorica'] < 2.5]
df_min_esc04 = df_min_esc04[df_min_esc04[u'Efi_Teorica'] < 2.5]
df_min_esc05 = df_min_esc05[df_min_esc05[u'Efi_Teorica'] < 2.5]

                        ## -- Correlaciones de la eficiencia teórica
corr_BM_min_esc01, p_value_BM_min_esc01 = pearsonr(df_min_esc01[u'Efi_Teorica'].values, df_min_esc01[u'BM'].values)
corr_T_min_esc01, p_value_BM_min_esc01 = pearsonr(df_min_esc01[u'Efi_Teorica'].values, df_min_esc01[u'T'].values)

corr_BM_min_esc02, p_value_BM_min_esc02 = pearsonr(df_min_esc02[u'Efi_Teorica'].values, df_min_esc02[u'BM'].values)
corr_T_min_esc02, p_value_BM_min_esc02 = pearsonr(df_min_esc02[u'Efi_Teorica'].values, df_min_esc02[u'T'].values)

corr_BM_min_esc03, p_value_BM_min_esc03 = pearsonr(df_min_esc03[u'Efi_Teorica'].values, df_min_esc03[u'BM'].values)
corr_T_min_esc03, p_value_BM_min_esc03 = pearsonr(df_min_esc03[u'Efi_Teorica'].values, df_min_esc03[u'T'].values)

corr_BM_min_esc04, p_value_BM_min_esc04 = pearsonr(df_min_esc04[u'Efi_Teorica'].values, df_min_esc04[u'BM'].values)
corr_T_min_esc04, p_value_BM_min_esc04 = pearsonr(df_min_esc04[u'Efi_Teorica'].values, df_min_esc04[u'T'].values)

corr_BM_min_esc05, p_value_BM_min_esc05 = pearsonr(df_min_esc05[u'Efi_Teorica'].values, df_min_esc05[u'BM'].values)
corr_T_min_esc05, p_value_BM_min_esc05 = pearsonr(df_min_esc05[u'Efi_Teorica'].values, df_min_esc05[u'T'].values)

                        ## -- Gráfico

jet = plt.get_cmap('jet')
fig = plt.figure(figsize=[11, 10])

ax1 = fig.add_subplot(2, 3, 1)
sc1 = ax1.scatter(df_min_esc01['radiacion'], df_min_esc01['Efi_Teorica'], s=10, c=df_min_esc01['T'],  cmap=jet)
cbar1 = ax1.figure.colorbar(sc1)
cbar1.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar1.ax.tick_params(pad=-15, labelsize=6)
ax1.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax1.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax1.set_title("Escenario del mes:" + str(df_min_esc01.index.month[0]), fontsize=10)
#ax1.text(min(df_min_esc01['radiacion']), min(df_min_esc01['Efi_Teorica']), 'Corr Coef: '+ str(corr_T_min_esc01.round(2)) + ' $P value$: '+ str(p_value_BM_min_esc01.round(2)), style='italic',  ha="center",   bbox={'facecolor':'#D6EAF8', 'alpha':0.5, 'pad':-1})

ax2 = fig.add_subplot(2, 3, 2)
sc2 = ax2.scatter(df_min_esc02['radiacion'], df_min_esc02['Efi_Teorica'], s=10, c=df_min_esc02['T'],  cmap=jet)
cbar2 = plt.colorbar(sc2)
cbar2.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar2.ax.tick_params(pad=-15, labelsize=6)
ax2.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax2.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax2.set_title("Escenario del mes:" + str(df_min_esc02.index.month[0]), fontsize=10)

ax3 = fig.add_subplot(2, 3, 3)
sc3 = ax3.scatter(df_min_esc03['radiacion'], df_min_esc03['Efi_Teorica'], s=10, c=df_min_esc03['T'],  cmap=jet)
cbar3 = plt.colorbar(sc3)
cbar3.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar3.ax.tick_params(pad=-15, labelsize=6)
ax3.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax3.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax3.set_title("Escenario del mes:" + str(df_min_esc03.index.month[0]), fontsize=10)

ax4 = fig.add_subplot(2, 3, 4)
sc4 = ax4.scatter(df_min_esc04['radiacion'], df_min_esc04['Efi_Teorica'], s=10, c=df_min_esc04['T'],  cmap=jet)
cbar4 = plt.colorbar(sc4)
cbar4.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar4.ax.tick_params(pad=-15, labelsize=6)
ax4.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax4.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax4.set_title("Escenario del mes:" + str(df_min_esc04.index.month[0]), fontsize=10)

ax5 = fig.add_subplot(2, 3, 5)
sc5 = ax3.scatter(df_min_esc05['radiacion'], df_min_esc05['Efi_Teorica'], s=10, c=df_min_esc05['T'],  cmap=jet)
cbar5 = plt.colorbar(sc5)
cbar5.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar5.ax.tick_params(pad=-15, labelsize=6)
ax5.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax5.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax5.set_title("Escenario del mes:" + str(df_min_esc05.index.month[0]), fontsize=10)

plt.subplots_adjust( wspace=0.3, hspace=1)
fig.suptitle(u"Relación de las eficiencias mínimas", fontsize=11, fontweight = "bold",  fontproperties = prop)
plt.show()
#plt.savefig('/home/nacorreasa/Escritorio/EScenario1.png')
plt.close()

          ## -- Escenarios medios

fh_i_mean = ['2018-01-01 00:00:00', '2018-07-01 00:00:00', '2018-09-01 00:00:00', '2018-10-01 00:00:00']
fh_f_mean = ['2018-01-31 23:59:00', '2018-07-31 23:59:00', '2018-09-30 23:59:00', '2018-10-31 23:59:00']

df_mean_esc01 = df1_rad_dia[(df1_rad_dia.index >= fh_i_mean[0]) & (df1_rad_dia.index <= fh_f_mean[0])]
df_mean_esc02 = df1_rad_dia[(df1_rad_dia.index >= fh_i_mean[1]) & (df1_rad_dia.index <= fh_f_mean[1])]
df_mean_esc03 = df1_rad_dia[(df1_rad_dia.index >= fh_i_mean[2]) & (df1_rad_dia.index <= fh_f_mean[2])]
df_mean_esc04 = df1_rad_dia[(df1_rad_dia.index >= fh_i_mean[3]) & (df1_rad_dia.index <= fh_f_mean[3])]

           ## -- Acotando los fuera de rango
df_mean_esc01 = df_mean_esc01[df_mean_esc01[u'Efi_Teorica'] < 2.5]
df_mean_esc02 = df_mean_esc02[df_mean_esc02[u'Efi_Teorica'] < 2.5]
df_mean_esc03 = df_mean_esc03[df_mean_esc03[u'Efi_Teorica'] < 2.5]
df_mean_esc04 = df_mean_esc04[df_mean_esc04[u'Efi_Teorica'] < 2.5]

                        ## -- Correlaciones de la eficiencia teórica
corr_BM_mean_esc01, p_value_BM_mean_esc01 = pearsonr(df_mean_esc01[u'Efi_Teorica'].values, df_mean_esc01[u'BM'].values)
corr_T_mean_esc01, p_value_BM_mean_esc01 = pearsonr(df_mean_esc01[u'Efi_Teorica'].values, df_mean_esc01[u'T'].values)

corr_BM_mean_esc02, p_value_BM_mean_esc02 = pearsonr(df_mean_esc02[u'Efi_Teorica'].values, df_mean_esc02[u'BM'].values)
corr_T_mean_esc02, p_value_BM_mean_esc02 = pearsonr(df_mean_esc02[u'Efi_Teorica'].values, df_mean_esc02[u'T'].values)

corr_BM_mean_esc03, p_value_BM_mean_esc03 = pearsonr(df_mean_esc03[u'Efi_Teorica'].values, df_mean_esc03[u'BM'].values)
corr_T_mean_esc03, p_value_BM_mean_esc03 = pearsonr(df_mean_esc03[u'Efi_Teorica'].values, df_mean_esc03[u'T'].values)

corr_BM_mean_esc04, p_value_BM_mean_esc04 = pearsonr(df_mean_esc04[u'Efi_Teorica'].values, df_mean_esc04[u'BM'].values)
corr_T_mean_esc04, p_value_BM_mean_esc04 = pearsonr(df_mean_esc04[u'Efi_Teorica'].values, df_mean_esc04[u'T'].values)


                        ## -- Gráfico

jet = plt.get_cmap('jet')
fig = plt.figure(figsize=[11, 10])

ax1 = fig.add_subplot(2, 2, 1)
sc1 = ax1.scatter(df_mean_esc01['radiacion'], df_mean_esc01['Efi_Teorica'], s=10, c=df_mean_esc01['T'],  cmap=jet)
cbar1 = ax1.figure.colorbar(sc1)
cbar1.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar1.ax.tick_params(pad=-15, labelsize=6)
ax1.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax1.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax1.set_title("Escenario del mes:" + str(df_mean_esc01.index.month[0]), fontsize=10)
#ax1.text(mean(df_mean_esc01['radiacion']), mean(df_mean_esc01['Efi_Teorica']), 'Corr Coef: '+ str(corr_T_mean_esc01.round(2)) + ' $P value$: '+ str(p_value_BM_mean_esc01.round(2)), style='italic',  ha="center",   bbox={'facecolor':'#D6EAF8', 'alpha':0.5, 'pad':-1})

ax2 = fig.add_subplot(2, 2, 2)
sc2 = ax2.scatter(df_mean_esc02['radiacion'], df_mean_esc02['Efi_Teorica'], s=10, c=df_mean_esc02['T'],  cmap=jet)
cbar2 = plt.colorbar(sc2)
cbar2.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar2.ax.tick_params(pad=-15, labelsize=6)
ax2.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax2.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax2.set_title("Escenario del mes:" + str(df_mean_esc02.index.month[0]), fontsize=10)

ax3 = fig.add_subplot(2, 2, 3)
sc3 = ax3.scatter(df_mean_esc03['radiacion'], df_mean_esc03['Efi_Teorica'], s=10, c=df_mean_esc03['T'],  cmap=jet)
cbar3 = plt.colorbar(sc3)
cbar3.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar3.ax.tick_params(pad=-15, labelsize=6)
ax3.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax3.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax3.set_title("Escenario del mes:" + str(df_mean_esc03.index.month[0]), fontsize=10)

ax4 = fig.add_subplot(2, 2, 4)
sc4 = ax4.scatter(df_mean_esc04['radiacion'], df_mean_esc04['Efi_Teorica'], s=10, c=df_mean_esc04['T'],  cmap=jet)
cbar4 = plt.colorbar(sc4)
cbar4.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar4.ax.tick_params(pad=-15, labelsize=6)
ax4.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax4.set_ylabel("Eficiencia ", fontsize=10, fontproperties=prop_1)
ax4.set_title("Escenario del mes:" + str(df_mean_esc04.index.month[0]), fontsize=10)

plt.subplots_adjust( wspace=0.3, hspace=0.9)
fig.suptitle(u"Relación de las eficiencias medias", fontsize=11, fontweight = "bold",  fontproperties = prop)
plt.show()
#plt.savefig('/home/nacorreasa/Escritorio/EScenario1.png')
plt.close()

## ---RELACIÓN CON LA BANDA DE AEROSOLES DE GOES--- ##

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C12018.nc')
a_esun = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/OR_ABI-L1b-RadF-M3C02_G16_s20180150000423_e20180150011190_c20180150011226.nc')
esun = a_esun.variables['esun'][:]
d    = (a_esun.variables['earth_sun_distance_anomaly_in_AU'][:])**2

lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :] + 360
Rad = ds.variables['Radiancias'][:,:,:]

# fr = (Rad*np.pi*d)/esun
# fr[fr[:, :] < 0] = 0
# fr[fr[:, :] > 1] = 1
# fr = np.sqrt(fr)
# fr = fr * 100.0

                   ## -- Selección de un pixel de las radiancias
lat_index = np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0]
lon_index = np.where((lon[0, :] < -75.58) & (lon[0, :] > -75.59))[0][0]

Rad_pixel = Rad[:, lat_index, lon_index]



                   ## -- Obtener el tiempo para cada valor

tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas)):
    fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')

                    ## -- Creación de dataframe de radiancias
Rad_df = pd.DataFrame()
Rad_df['Fecha_Hora'] = fechas_horas
Rad_df['Radiacias'] = Rad_pixel
Rad_df['Fecha_Hora'] = pd.to_datetime(Rad_df['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df.index = Rad_df['Fecha_Hora']
Rad_df = Rad_df.drop(['Fecha_Hora'], axis=1)

                    ## -- Normalización de las radiancias
#
# min_Rad = min(Rad_df['Radiacias'].values)
# max_Rad = max(Rad_df['Radiacias'].values)
# range_Rad = max_Rad - min_Rad
# Rad_norm = (Rad_df['Radiacias'].values- min_Rad)/range_Rad
# Rad_df['Rad_norm'] = Rad_norm
#
Rad_df_h = Rad_df.groupby(pd.Grouper(freq="H")).mean()
Rad_df_h = Rad_df_h.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia

                    ## -- Ciclo diurno de el anio para los aerololes en este punto

Rad_df_CD = Rad_df_h.groupby(by=[Rad_df_h.index.hour]).mean()


##----------------------------------- Ciclo Hidrologico -----------------------------------##

                    ## -- Obteniendo los 4 DF para el ciclo hidrológico

Rad_dfh_DEF = Rad_df_h[(Rad_df_h.index.month == 1) | (Rad_df_h.index.month == 12) | (Rad_df_h.index.month == 2)]
Rad_dfh_MAM = Rad_df_h[(Rad_df_h.index.month == 3) | (Rad_df_h.index.month == 4) | (Rad_df_h.index.month == 5)]
Rad_dfh_JJA = Rad_df_h[(Rad_df_h.index.month == 6) | (Rad_df_h.index.month == 7) | (Rad_df_h.index.month == 8)]
Rad_dfh_SON = Rad_df_h[(Rad_df_h.index.month == 9) | (Rad_df_h.index.month == 10) | (Rad_df_h.index.month == 11)]


                                 ## -- Ciclo diurno horario de cada trimestre

Rad_dfh_DEF_CD  = Rad_dfh_DEF.groupby(by=[Rad_dfh_DEF.index.hour]).mean()
Rad_dfh_MAM_CD  = Rad_dfh_MAM.groupby(by=[Rad_dfh_MAM.index.hour]).mean()
Rad_dfh_JJA_CD  = Rad_dfh_JJA.groupby(by=[Rad_dfh_JJA.index.hour]).mean()
Rad_dfh_SON_CD  = Rad_dfh_SON.groupby(by=[Rad_dfh_SON.index.hour]).mean()

##--Grafico CD horario de cada trimestre
x_pos = np.arange(len(Rad_dfh_DEF_CD.index))

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(2, 2, 1)
ax1.bar(x_pos, Rad_dfh_DEF_CD['Radiacias'], align='center', alpha=0.5)
ax1.set_xticks(np.arange(0, 13))
ax1.set_xticklabels(Rad_dfh_DEF_CD.index.values)
ax1.set_ylabel(u'Radiancias', fontproperties=prop_1)
ax1.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax1.set_title('DEF',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(2, 2, 2)
ax2.bar(x_pos, Rad_dfh_MAM_CD['Radiacias'], align='center', alpha=0.5)
ax2.set_xticks(np.arange(0, 13))
ax2.set_xticklabels(Rad_dfh_MAM_CD.index.values)
ax2.set_ylabel(u'Radiancias', fontproperties=prop_1)
ax2.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax2.set_title(r'MAM',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(2, 2, 3)
ax3.bar(x_pos, Rad_dfh_JJA_CD['Radiacias'], align='center', alpha=0.5)
ax3.set_xticks(np.arange(0, 13))
ax3.set_xticklabels(Rad_dfh_JJA_CD.index.values)
ax3.set_ylabel(u'Radiancias', fontproperties=prop_1)
ax3.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax3.set_title(u'JJA',   fontweight = "bold",  fontproperties = prop)

ax4 = fig.add_subplot(2, 2, 4)
ax4.bar(x_pos, Rad_dfh_SON_CD['Radiacias'], align='center', alpha=0.5)
ax4.set_xticks(np.arange(0, 13))
ax4.set_xticklabels(Rad_dfh_SON_CD.index.values)
ax4.set_ylabel(u'Radiancias', fontproperties=prop_1)
ax4.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax4.set_title(u'SON',   fontweight = "bold",  fontproperties = prop)

plt.subplots_adjust( wspace=0.3, hspace=0.4)
fig.suptitle(u"CD Trimestral en: " + EstacionLoc, fontsize=15, fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/CD_C1_Trimestre_'+EstacionLoc+'.png')
plt.show()

                                ## -- Histograma de cada trimestre

HistDEF = np.histogram(Rad_dfh_DEF['Rad_norm'].values[~np.isnan(Rad_dfh_DEF['Rad_norm'].values)])
HistMAM = np.histogram(Rad_dfh_MAM['Rad_norm'].values[~np.isnan(Rad_dfh_MAM['Rad_norm'].values)])
HistJJA = np.histogram(Rad_dfh_JJA['Rad_norm'].values[~np.isnan(Rad_dfh_JJA['Rad_norm'].values)])
HistSON = np.histogram(Rad_dfh_SON['Rad_norm'].values[~np.isnan(Rad_dfh_SON['Rad_norm'].values)])


#x_pos = np.arange(len(HistDEF[1])-1)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(2, 2, 1)
ax1.hist(Rad_dfh_DEF['Radiacias'].values[~np.isnan(Rad_dfh_DEF['Radiacias'].values)], bins='auto')
# ax1.bar(x_pos, HistDEF[0], align='center', alpha=0.5)
# ax1.set_xticks(np.arange(0, 13))
# ax1.set_xticklabels(HistDEF[1].round(2), rotation= 45, fontproperties=prop_1, fontsize= 10)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Radiancia', fontproperties=prop_1)
ax1.set_title('DEF',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(2, 2, 2)
ax2.hist(Rad_dfh_MAM['Radiacias'].values[~np.isnan(Rad_dfh_MAM['Radiacias'].values)], bins='auto')
# ax2.bar(x_pos, HistMAM[0], align='center', alpha=0.5)
# ax2.set_xticks(np.arange(0, 13))
# ax2.set_xticklabels(HistMAM[1].round(2), rotation= 45)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Radiancia', fontproperties=prop_1)
ax2.set_title(r'MAM',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(2, 2, 3)
ax3.hist(Rad_dfh_JJA['Radiacias'].values[~np.isnan(Rad_dfh_JJA['Radiacias'].values)], bins='auto')
# ax3.bar(x_pos, HistJJA[0], align='center', alpha=0.5)
# ax3.set_xticks(np.arange(0, 13))
# ax3.set_xticklabels(HistJJA[1].round(2), rotation= 45)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Radiancia', fontproperties=prop_1)
ax3.set_title(u'JJA',   fontweight = "bold",  fontproperties = prop)

ax4 = fig.add_subplot(2, 2, 4)
ax4.hist(Rad_dfh_SON['Radiacias'].values[~np.isnan(Rad_dfh_SON['Radiacias'].values)], bins='auto')
# ax4.bar(x_pos, HistSON[0], align='center', alpha=0.5)
# ax4.set_xticks(np.arange(0, 13))
# ax4.set_xticklabels(HistSON[1].round(2), rotation= 45)
ax4.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax4.set_xlabel(u'Radiancia', fontproperties=prop_1)
ax4.set_title(u'SON',   fontweight = "bold",  fontproperties = prop)

plt.subplots_adjust( wspace=0.3, hspace=0.4)
fig.suptitle(u"Histograma Trimestral de aerosoles en: " + EstacionLoc, fontsize=15, fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/Hist_C1_Trimestre_'+EstacionLoc+'.png')
plt.show()


##----------------------------------- Escenarios de los percentiles -----------------------------------##


                    ## -- Obteniendo los 3 DF prelacionados a los escenarios

Rad_dfh_MAX = Rad_df_h[(Rad_df_h.index.month == 5)| (Rad_df_h.index.month == 6)| (Rad_df_h.index.month == 7) |
              (Rad_df_h.index.month == 8) | (Rad_df_h.index.month == 8)]

Rad_dfh_MIN = Rad_df_h[(Rad_df_h.index.month == 10) | (Rad_df_h.index.month == 11) | (Rad_df_h.index.month == 12)]

Rad_dfh_MEAN = Rad_df_h[(Rad_df_h.index.month == 1) | (Rad_df_h.index.month == 2) | (Rad_df_h.index.month == 3)
               | (Rad_df_h.index.month == 4)]


                                 ## -- Ciclo diurno horario de cada grupo de meses

Rad_dfh_MAX_CD   = Rad_dfh_MAX.groupby(by=[Rad_dfh_MAX.index.hour]).mean()
Rad_dfh_MIN_CD   = Rad_dfh_MIN.groupby(by=[Rad_dfh_MIN.index.hour]).mean()
Rad_dfh_MEAN_CD  = Rad_dfh_MEAN.groupby(by=[Rad_dfh_MEAN.index.hour]).mean()

x_pos = np.arange(len(Rad_dfh_MAX_CD.index))

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.bar(x_pos, Rad_dfh_MAX_CD ['Radiacias'], align='center', alpha=0.5)
ax1.set_xticks(np.arange(0, 13))
ax1.set_xticklabels(Rad_dfh_MAX_CD .index.values, rotation = 45)
ax1.set_ylabel(u'Radiancia', fontproperties=prop_1)
ax1.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax1.set_title('MAX',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(1, 3, 2)
ax2.bar(x_pos, Rad_dfh_MIN_CD['Radiacias'], align='center', alpha=0.5)
ax2.set_xticks(np.arange(0, 13))
ax2.set_xticklabels(Rad_dfh_MIN_CD.index.values, rotation = 45)
ax2.set_ylabel(u'Radiancia', fontproperties=prop_1)
ax2.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax2.set_title(r'MIN',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(1, 3, 3)
ax3.bar(x_pos, Rad_dfh_MEAN_CD['Radiacias'], align='center', alpha=0.5)
ax3.set_xticks(np.arange(0, 13))
ax3.set_xticklabels(Rad_dfh_MEAN_CD.index.values, rotation = 45)
ax3.set_ylabel(u'Radiancia', fontproperties=prop_1)
ax3.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax3.set_title(u'MEAN',   fontweight = "bold",  fontproperties = prop)

plt.subplots_adjust( wspace=0.3, hspace=0.4)
fig.suptitle(u"CD por escenarios en: " + EstacionLoc, fontsize=15, fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/CD_C1_Escenarios_'+EstacionLoc+'.png')
plt.show()


                                 ## -- Histograma de cada grupo de meses

HistMAX = np.histogram(Rad_dfh_MAX['Rad_norm'].values)
HistMIN = np.histogram(Rad_dfh_MIN['Rad_norm'].values)
HistMEAN = np.histogram(Rad_dfh_MEAN['Rad_norm'].values)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.hist(Rad_dfh_MAX['Radiacias'].values[~np.isnan(Rad_dfh_MAX['Radiacias'].values)], bins='auto')
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Radiancias', fontproperties=prop_1)
ax1.set_title(u'Máximo',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(1, 3, 2)
ax2.hist(Rad_dfh_MIN['Radiacias'].values[~np.isnan(Rad_dfh_MIN['Radiacias'].values)], bins='auto')
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Radiancias', fontproperties=prop_1)
ax2.set_title(u'Mínimo',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(1, 3, 3)
ax3.hist(Rad_dfh_MEAN['Radiacias'].values[~np.isnan(Rad_dfh_MEAN['Radiacias'].values)], bins='auto')
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Radiancias', fontproperties=prop_1)
ax3.set_title(u'Medio',   fontweight = "bold",  fontproperties = prop)

plt.subplots_adjust( wspace=0.3, hspace=0.4)
fig.suptitle(u"Histograma escenarios de aerosoles en: " + EstacionLoc, fontsize=15, fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/Hist_C1_Escenarios_'+EstacionLoc+'.png')
plt.show()

                   ## -- Histograma diurno de los aerosoles en este punto


fig = plt.figure(figsize=(14, 18))
for i in range(1, 13):
    A = Rad_df_h[Rad_df_h.index.hour == (i + 5)]['Radiacias']
    ax = fig.add_subplot(4, 3, i )
    ax.set_title('Hora '+str(A.index.hour[0]), fontsize=6)
    ax.hist(A.values[~np.isnan(A.values)], bins='auto')
    ax.set_ylabel(u'Frecuencia', fontproperties=prop_1)
    ax.set_xlabel(u'Radiancia', fontproperties=prop_1)

plt.subplots_adjust( wspace=0.3, hspace=0.4)
fig.suptitle(u"Histograma horario 2018 de  aerosoles en: " + EstacionLoc, fontsize=15, fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/HistHora_C1_Trimestre_'+EstacionLoc+'.png')
plt.show()
