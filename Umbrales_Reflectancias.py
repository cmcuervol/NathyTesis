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
from matplotlib.font_manager import FontProperties

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

'Esta version de este codigo, saca los umbrales horarios y estacionalesde las reflectancias'
'en los pixeles seleccionados, cada 15 minutos porque se hace con el set de datos de GOES de'
'2018, debido a que es el mas completo y permitiría obtener los umbrales estacionalmente. La'
'versión antigua de este codigo que los sacaba cada 10 minutos para el horizonte del experi-'
'mento se aloja en la carpetade Backups_VersionesAtiguas_Codigos por si esnecesario volverlo'
'a consultar.'

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

## -------------------------------HORAS SOBRE LAS CUALES TRABAJAR----------------------------- ##
HI = '06:00'; HF = '17:59'

#################################################################################################
## -----------------INCORPORANDO LOS DATOS DE RADIACIÓN Y DE LOS EXPERIMENTOS----------------- ##
#################################################################################################

df_P975 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60012018.txt', parse_dates=[2])
df_P350 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60022018.txt', parse_dates=[2])
df_P348 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60032018.txt', parse_dates=[2])

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


##----AJUSTE DE LOS DATOS DE RADIACIÓN REAL AL RANGO DE FECHAS DESEADO-----##

def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada hora. Las fechas'
    'final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=60)
    while start_date <= end_date:
        yield start_date
        start_date += delta

fechas_975 = []
for i in daterange(df_P975.index[0].date().strftime("%Y-%m-%d"), (df_P975.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_975.append(i)

fechas_350 = []
for i in daterange(df_P350.index[0].date().strftime("%Y-%m-%d"), (df_P350.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_350.append(i)

fechas_348 = []
for i in daterange(df_P348.index[0].date().strftime("%Y-%m-%d"), (df_P348.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_348.append(i)

fi_m = min(fechas_975[0].month, fechas_350[0].month, fechas_348[0].month)
fi_d = min(fechas_975[0].day, fechas_350[0].day, fechas_348[0].day)
ff_m = min(fechas_975[-1].month, fechas_350[-1].month, fechas_348[-1].month)
ff_d = min(fechas_975[-1].day, fechas_350[-1].day, fechas_348[-1].day)

## -----------------------------AGREGAR DATOS DE PIRANOMETRO CADA 15 MINUTOS ------------------------------ ##

df_P348_15m = df_P348.groupby(pd.Grouper(freq="15Min")).mean()
df_P350_15m = df_P350.groupby(pd.Grouper(freq="15Min")).mean()
df_P975_15m = df_P975.groupby(pd.Grouper(freq="15Min")).mean()

df_P348_15m = df_P348_15m.between_time(HI, HF)
df_P350_15m = df_P350_15m.between_time(HI, HF)
df_P975_15m = df_P975_15m.between_time(HI, HF)

df_P348_15m = df_P348_15m.loc[~df_P348_15m.index.duplicated(keep='first')]
df_P350_15m = df_P350_15m.loc[~df_P350_15m.index.duplicated(keep='first')]
df_P975_15m = df_P975_15m.loc[~df_P975_15m.index.duplicated(keep='first')]

####################################################################################
## ----------------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL---------------- ##
####################################################################################

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')

df_fh  = pd.DataFrame()
df_fh ['fecha_hora'] = fechas_horas
df_fh['fecha_hora'] = pd.to_datetime(df_fh['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_fh.index = df_fh['fecha_hora']
w = pd.date_range(df_fh.index.min(), df_fh.index.max()).difference(df_fh.index)
df_fh = df_fh[df_fh.index.hour != 5]

#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
Rad_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix350_Anio.npy')
Rad_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix348_Anio.npy')
fechas_horas = df_fh['fecha_hora'].values


                    ## -- Creación de dataframe de radiancias
Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)
Rad_df_975 = Rad_df_975.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
Rad_df_975_h = Rad_df_975.groupby(pd.Grouper(freq="H")).mean()

Rad_df_350 = pd.DataFrame()
Rad_df_350['Fecha_Hora'] = fechas_horas
Rad_df_350['Radiacias'] = Rad_pixel_350
Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_350.index = Rad_df_350['Fecha_Hora']
Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)
Rad_df_350 = Rad_df_350.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
Rad_df_350_h = Rad_df_350.groupby(pd.Grouper(freq="H")).mean()

Rad_df_348 = pd.DataFrame()
Rad_df_348['Fecha_Hora'] = fechas_horas
Rad_df_348['Radiacias'] = Rad_pixel_348
Rad_df_348['Fecha_Hora'] = pd.to_datetime(Rad_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_348.index = Rad_df_348['Fecha_Hora']
Rad_df_348 = Rad_df_348.drop(['Fecha_Hora'], axis=1)
Rad_df_348 = Rad_df_348.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
Rad_df_348_h = Rad_df_348.groupby(pd.Grouper(freq="H")).mean()

def time_mod(time, delta, epoch=None):
    if epoch is None:
        epoch = datetime.datetime(1970, 1, 1, tzinfo=time.tzinfo)
    return (time - epoch) % delta

def time_round(time, delta, epoch=None):
    mod = time_mod(time, delta, epoch)
    if mod < (delta / 2):
       return time - mod
    return time + (delta - mod)


Rad_df_348.index = [time_round(Rad_df_348.index[i], datetime.timedelta(minutes=15)) for i in range(len(Rad_df_348.index))]
Rad_df_350.index = [time_round(Rad_df_350.index[i], datetime.timedelta(minutes=15)) for i in range(len(Rad_df_350.index))]
Rad_df_975.index = [time_round(Rad_df_975.index[i], datetime.timedelta(minutes=15)) for i in range(len(Rad_df_975.index))]

Rad_df_348 =  Rad_df_348.loc[~Rad_df_348.index.duplicated(keep='first')]
Rad_df_350 =  Rad_df_350.loc[~Rad_df_350.index.duplicated(keep='first')]
Rad_df_975 =  Rad_df_975.loc[~Rad_df_975.index.duplicated(keep='first')]
##----------------------------------ACOTANDOLO A LOS DATOS DE SOLO EL 2018---------------------------------##
Rad_df_975 = Rad_df_975[Rad_df_975.index.year==2018]
Rad_df_350 = Rad_df_350[Rad_df_350.index.year==2018]
Rad_df_348 = Rad_df_348[Rad_df_348.index.year==2018]



###############################################################################################################################
## ---------------------------------LECTURA DE LOS DATOS DE RADIACIÓN TEORICA KUMAR----------------------------------------- ##
###############################################################################################################################

def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada 10 min. Las fechas final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=10)
    while start_date <= end_date:
        yield start_date
        start_date += delta

def serie_Kumar_Model(estacion):
    'Retorna un dataframe horario con la radiacion teórico con las recomendacione de Kumar elaborado por Gisel Guzmán ' \
    'para el AMVA y su tesis. El dataframe original se le ordenan los datos a  12 meses ascendentes (2018), aunque pueden ' \
    ' pertencer  a  años difernetes. El resultado es para el punto seleccionado y con el archivo de Total_Timeseries.csv. Actualizar el año'

    data_Model = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_Totales/Total_Timeseries_Rad_2018.csv',
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
    data_Theorical['Radiacion'] = Rad_teorica

    data_Theorical.index = data_Theorical['fecha_hora']

    data_Theorical = data_Theorical[data_Theorical['Radiacion'] > 0]

    data_hourly_theoric = data_Theorical.groupby(pd.Grouper(freq="H")).mean()

    return data_hourly_theoric, data_Theorical

df_hourly_theoric_348, df_Theorical_348 = serie_Kumar_Model('6003')
df_hourly_theoric_350, df_Theorical_350 = serie_Kumar_Model('6002')
df_hourly_theoric_975, df_Theorical_975 = serie_Kumar_Model('6001')

######################################################################################################################
## -----------------------------ACOTAR LOS DATOS DE LA RAD TEÓRICA A LOS DE RADIACION------------------------------ ##
######################################################################################################################

df_hourly_theoric_348 = df_hourly_theoric_348[(df_hourly_theoric_348.index >= '2018-'+'0'+str(df_P348.index.month[0])
                      +'-'+str(df_P348.index.day[0])) & (df_hourly_theoric_348.index <= '2018-'+str(df_P348.index.month[-1])
                      +'-'+str(df_P348.index.day[-1]))]

df_hourly_theoric_350 = df_hourly_theoric_350[(df_hourly_theoric_350.index >= '2018-'+'0'+str(df_P350.index.month[0])
                      +'-'+str(df_P350.index.day[0])) & (df_hourly_theoric_350.index <= '2018-'+str(df_P350.index.month[-1])
                      +'-'+str(df_P350.index.day[-1]))]

df_hourly_theoric_975 = df_hourly_theoric_975[(df_hourly_theoric_975.index >= '2018-'+'0'+str(df_P975.index.month[0])
                      +'-'+str(df_P975.index.day[0])) & (df_hourly_theoric_975.index <= '2018-'+str(df_P975.index.month[-1])
                      +'-'+str(df_P975.index.day[-1]))]

df_Theorical_348 = df_Theorical_348[(df_Theorical_348.index >= '2018-'+'0'+str(df_P348.index.month[0])
                      +'-'+str(df_P348.index.day[0])) & (df_Theorical_348.index <= '2018-'+str(df_P348.index.month[-1])
                      +'-'+str(df_P348.index.day[-1]))]

df_Theorical_350 = df_Theorical_350[(df_Theorical_350.index >= '2018-'+'0'+str(df_P350.index.month[0])
                      +'-'+str(df_P350.index.day[0])) & (df_Theorical_350.index <= '2018-'+str(df_P350.index.month[-1])
                      +'-'+str(df_P350.index.day[-1]))]

df_Theorical_975 = df_Theorical_975[(df_Theorical_975.index >= '2018-'+'0'+str(df_P975.index.month[0])
                      +'-'+str(df_P975.index.day[0])) & (df_Theorical_975.index <= '2018-'+str(df_P975.index.month[-1])
                      +'-'+str(df_P975.index.day[-1]))]
df_Theorical_348.index = [time_round(df_Theorical_348.index[i], datetime.timedelta(minutes=15)) for i in range(len(df_Theorical_348.index))]
df_Theorical_350.index = [time_round(df_Theorical_350.index[i], datetime.timedelta(minutes=15)) for i in range(len(df_Theorical_350.index))]
df_Theorical_975.index = [time_round(df_Theorical_975.index[i], datetime.timedelta(minutes=15)) for i in range(len(df_Theorical_975.index))]

df_Theorical_348 = df_Theorical_348.drop(['fecha_hora'], axis=1)
df_Theorical_348 = df_Theorical_348.loc[~df_Theorical_348.index.duplicated(keep='first')]
df_Theorical_350 = df_Theorical_350.drop(['fecha_hora'], axis=1)
df_Theorical_350 = df_Theorical_350.loc[~df_Theorical_350.index.duplicated(keep='first')]
df_Theorical_975 = df_Theorical_975.drop(['fecha_hora'], axis=1)
df_Theorical_975 = df_Theorical_975.loc[~df_Theorical_975.index.duplicated(keep='first')]

##################################################################################################################
## -----------------------------ANÁLISIS DE RESULTADOS Y DETERMINACIÓN DEL UMBRAL------------------------------ ##
##################################################################################################################

'Se  determina las reflectancias para las condiciones despejadas con el piranometro cada 15 minutos. Para detectar las reflectancias  '
'nubadas en cada punto, se detectan por las derivadas discriminando por mañana y tarde. Los estoy poniendo por ahora con el máximo.'


df_result_348 = pd.concat([df_P348_15m, Rad_df_348, df_Theorical_348], axis=1)
df_result_350 = pd.concat([df_P350_15m, Rad_df_350, df_Theorical_350], axis=1)
df_result_975 = pd.concat([df_P975_15m, Rad_df_975, df_Theorical_975], axis=1)

df_result_348['Rad_deriv'] = np.gradient(df_result_348['radiacion'].values)
df_result_350['Rad_deriv'] = np.gradient(df_result_350['radiacion'].values)
df_result_975['Rad_deriv'] = np.gradient(df_result_975['radiacion'].values)

df_result_348 = df_result_348.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)
df_result_350 = df_result_350.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)
df_result_975 = df_result_975.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)

## ---- UMBRAL CASO NUBOSO :

df_P348_15m_Nuba_Morning = df_result_348.between_time('06:00','11:59')
df_P348_15m_Nuba_Afternoon = df_result_348.between_time('12:00','17:59')

df_P350_15m_Nuba_Morning = df_result_350.between_time('06:00','11:59')
df_P350_15m_Nuba_Afternoon = df_result_350.between_time('12:00','17:59')

df_P975_15m_Nuba_Morning = df_result_975.between_time('06:00','11:59')
df_P975_15m_Nuba_Afternoon = df_result_975.between_time('12:00','17:59')

##-----------------------------------------348--------------------------------------##

df_P348_Ref_Morning = df_P348_15m_Nuba_Morning['Radiacias'][df_P348_15m_Nuba_Morning['Rad_deriv']<0]
df_P348_Ref_Morning = df_P348_Ref_Morning.groupby([df_P348_Ref_Morning.index.month, df_P348_Ref_Morning.index.hour]).mean()

df_P348_Ref_Afternoon = df_P348_15m_Nuba_Afternoon['Radiacias'][df_P348_15m_Nuba_Afternoon['Rad_deriv']>0]
df_P348_Ref_Afternoon = df_P348_Ref_Afternoon.groupby([df_P348_Ref_Afternoon.index.month, df_P348_Ref_Afternoon.index.hour]).mean()

df_HourlySeasonalThrereshold_348_Nuba = pd.concat([df_P348_Ref_Morning, df_P348_Ref_Afternoon]).sort_index()
df_HourlyThrereshold_348_Nuba = df_HourlySeasonalThrereshold_348_Nuba.groupby(level=[1]).mean()

df_HourlySeasonalThrereshold_348_Nuba.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_SeasonalHourly_348_Nuba.csv')
df_HourlyThrereshold_348_Nuba.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Nuba.csv')

##-----------------------------------------350--------------------------------------##

df_P350_Ref_Morning = df_P350_15m_Nuba_Morning['Radiacias'][df_P350_15m_Nuba_Morning['Rad_deriv']<0]
df_P350_Ref_Morning = df_P350_Ref_Morning.groupby([df_P350_Ref_Morning.index.month, df_P350_Ref_Morning.index.hour]).mean()

df_P350_Ref_Afternoon = df_P350_15m_Nuba_Afternoon['Radiacias'][df_P350_15m_Nuba_Afternoon['Rad_deriv']>0]
df_P350_Ref_Afternoon = df_P350_Ref_Afternoon.groupby([df_P350_Ref_Afternoon.index.month, df_P350_Ref_Afternoon.index.hour]).mean()

df_HourlySeasonalThrereshold_350_Nuba = pd.concat([df_P350_Ref_Morning, df_P350_Ref_Afternoon]).sort_index()
df_HourlyThrereshold_350_Nuba = df_HourlySeasonalThrereshold_350_Nuba.groupby(level=[1]).mean()



df_HourlySeasonalThrereshold_350_Nuba.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_SeasonalHourly_350_Nuba.csv')
df_HourlyThrereshold_350_Nuba.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Nuba.csv')

##-----------------------------------------975--------------------------------------##

df_P975_Ref_Morning = df_P975_15m_Nuba_Morning['Radiacias'][df_P975_15m_Nuba_Morning['Rad_deriv']<0]
df_P975_Ref_Morning = df_P975_Ref_Morning.groupby([df_P975_Ref_Morning.index.month, df_P975_Ref_Morning.index.hour]).mean()

df_P975_Ref_Afternoon = df_P975_15m_Nuba_Afternoon['Radiacias'][df_P975_15m_Nuba_Afternoon['Rad_deriv']>0]
df_P975_Ref_Afternoon = df_P975_Ref_Afternoon.groupby([df_P975_Ref_Afternoon.index.month, df_P975_Ref_Afternoon.index.hour]).mean()

df_HourlySeasonalThrereshold_975_Nuba = pd.concat([df_P975_Ref_Morning, df_P975_Ref_Afternoon]).sort_index()
df_HourlyThrereshold_975_Nuba = df_HourlySeasonalThrereshold_975_Nuba.groupby(level=[1]).mean()

df_HourlySeasonalThrereshold_975_Nuba.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_SeasonalHourly_975_Nuba.csv')
df_HourlyThrereshold_975_Nuba.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Nuba.csv')

## ---- UMBRAL CASO DESPEJADO :

##-----------------------------------------348--------------------------------------##

df_P348_15m_Desp = df_result_348['Radiacias'][df_result_348['radiacion'] >= 0.99 * df_result_348['Radiacion']]
df_HourlySeasonalThrereshold_348_Desp = df_P348_15m_Desp.groupby([df_P348_15m_Desp.index.month, df_P348_15m_Desp.index.hour]).mean()
df_HourlyThrereshold_348_Desp = df_HourlySeasonalThrereshold_348_Desp.groupby(level=[1]).mean()

df_HourlySeasonalThrereshold_348_Desp.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_SeasonalHourly_348_Desp.csv')
df_HourlyThrereshold_348_Desp.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Desp.csv')

##-----------------------------------------350--------------------------------------##

df_P350_15m_Desp = df_result_350['Radiacias'][df_result_350['radiacion'] >= 0.99 * df_result_350['Radiacion']]
df_HourlySeasonalThrereshold_350_Desp = df_P350_15m_Desp.groupby([df_P350_15m_Desp.index.month, df_P350_15m_Desp.index.hour]).mean()
df_HourlyThrereshold_350_Desp = df_HourlySeasonalThrereshold_350_Desp.groupby(level=[1]).mean()

"-------------------------------------------------------------------------------------------------------"
##----------------------------------MACHETEEEEE PARA EL DEL CONSEJOO ---------------------------------##
"-------------------------------------------------------------------------------------------------------"
df_HourlyThrereshold_350_Desp.loc[df_HourlyThrereshold_350_Desp.values >40] =  38

df_HourlySeasonalThrereshold_350_Desp.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_SeasonalHourly_350_Desp.csv')
df_HourlyThrereshold_350_Desp.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Desp.csv')


##-----------------------------------------975--------------------------------------##

df_P975_15m_Desp = df_result_975['Radiacias'][df_result_975['radiacion'] >= 0.99 * df_result_975['Radiacion']]
df_HourlySeasonalThrereshold_975_Desp = df_P975_15m_Desp.groupby([df_P975_15m_Desp.index.month, df_P975_15m_Desp.index.hour]).mean()
df_HourlyThrereshold_975_Desp = df_HourlySeasonalThrereshold_975_Desp.groupby(level=[1]).mean()

df_HourlySeasonalThrereshold_975_Desp.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_SeasonalHourly_975_Desp.csv')
df_HourlyThrereshold_975_Desp.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Desp.csv')

## ---------------------------------GRAFICO DE LOS UMBRALES PARA CADA PUNTO POR HORA----------------------------------------- ##

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(df_HourlyThrereshold_350_Nuba.index, df_HourlyThrereshold_350_Nuba.values, color = '#09202E', label ='Nublado')
ax1.fill_between(df_HourlyThrereshold_350_Nuba.index, df_HourlyThrereshold_350_Nuba.values, 100, color = '#09202E', alpha = 0.5)
ax1.plot(df_HourlyThrereshold_350_Desp.index,df_HourlyThrereshold_350_Desp.values, color = '#98D1DD', label ='Despejado')
ax1.fill_between(df_HourlyThrereshold_350_Desp.index,0, df_HourlyThrereshold_350_Desp.values, color = '#98D1DD', alpha = 0.5)
ax1.set_xticks(range(6,18), minor=False)
ax1.set_xticklabels(df_HourlyThrereshold_350_Nuba.index, minor=False, rotation = 20)
ax1.set_ylabel(u'Reflectancias [%]', fontproperties=prop_1)
ax1.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax1.set_ylim(0, 100)
ax1.set_title('Umbrales de reflectancias \n para el Oeste',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(df_HourlyThrereshold_975_Nuba.index, df_HourlyThrereshold_975_Nuba.values, color = '#09202E', label ='Nublado')
ax2.fill_between(df_HourlyThrereshold_975_Nuba.index, df_HourlyThrereshold_975_Nuba.values, 100, color = '#09202E', alpha = 0.5)
ax2.plot(df_HourlyThrereshold_975_Desp.index,df_HourlyThrereshold_975_Desp.values, color = '#98D1DD', label ='Despejado')
ax2.fill_between(df_HourlyThrereshold_975_Desp.index,0, df_HourlyThrereshold_975_Desp.values, color = '#98D1DD', alpha = 0.5)
ax2.set_xticks(range(6,18), minor=False)
ax2.set_xticklabels(df_HourlyThrereshold_975_Nuba.index, minor=False, rotation = 20)
ax2.set_ylabel(u'Reflectancias [%]', fontproperties=prop_1)
ax2.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax2.set_ylim(0, 100)
ax2.set_title('Umbrales de reflectancias \n  para el Centro-Oeste',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.plot(df_HourlyThrereshold_348_Nuba.index, df_HourlyThrereshold_348_Nuba.values, color = '#09202E', label ='Nublado')
ax3.fill_between(df_HourlyThrereshold_348_Nuba.index, df_HourlyThrereshold_348_Nuba.values, 100, color = '#09202E', alpha = 0.5)
ax3.plot(df_HourlyThrereshold_348_Desp.index,df_HourlyThrereshold_348_Desp.values, color = '#98D1DD', label ='Despejado')
ax3.fill_between(df_HourlyThrereshold_348_Desp.index,0, df_HourlyThrereshold_348_Desp.values, color = '#98D1DD', alpha = 0.5)
ax3.set_xticks(range(6,18), minor=False)
ax3.set_xticklabels(df_HourlyThrereshold_348_Nuba.index, minor=False, rotation = 20)
ax3.set_ylabel(u'Reflectancias [%]', fontproperties=prop_1)
ax3.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax3.set_ylim(0, 100)
ax3.set_title('Umbrales de reflectancias \n  para el Este',   fontweight = "bold",  fontproperties = prop)

fontP = FontProperties()
fontP.set_size('small')
plt.legend(prop=fontP)
plt.subplots_adjust( wspace=0.3, hspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/TheresholsHourlyDistribution.pdf', format='pdf',  transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/TheresholsHourlyDistribution.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
