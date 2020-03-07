#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
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
import matplotlib.cm as cm

Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
Horizonte = 'Anio'    ##-->'Anio' para los datos del 2018 y 2019y 'EXP' para los datos a partir del experimento.

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

'Codigo para guardar el array con los datos de las anomalías de la radiación y '
'Dibujar su relación con los datos de nubes con los umbrales establecidos. Se trabaja'
'con datos cada 15 minutos q es la mayor resolución de CH2 GOES.'

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


#################################################################################################
## -----------------------------SERIE DE ANOMALIAS DE LAS RADIACION--------------------------- ##
#################################################################################################
import datetime
def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada hora. Las fechas'
    'final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=15)
    while start_date <= end_date:
        yield start_date
        start_date += delta

fechas = []
for i in daterange(df_P975.index[0].date().strftime("%Y-%m-%d"), (df_P975.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas.append(i)

##------------------------------------------------------------------975-------------------------------------------------------------##
df_P975_15m = df_P975_15m.drop(['Unnamed: 0', 'idestacion',  'temperatura'], axis=1)
df_P975_15m = df_P975_15m.between_time('06:00', '17:59')
df_P975_15m_monthly_mean = df_P975_15m.groupby([df_P975_15m.index.month, df_P975_15m.index.hour, df_P975_15m.index.minute]).mean()
fechas_horas_CM = []
for i in range(len(df_P975_15m_monthly_mean.index)):
    fechas_horas_CM.append(pd.to_datetime('2018-'+str(df_P975_15m_monthly_mean.index[i][0])+' '+str(df_P975_15m_monthly_mean.index[i][1])+':'+str(df_P975_15m_monthly_mean.index[i][2]), format="%Y-%m %H:%M", errors='coerce'))

df_P975_15m_monthly_mean.index= fechas_horas_CM
df_P975_15m_monthly_mean = df_P975_15m_monthly_mean.sort_index()
df_P975_15m_monthly_mean['Month'] = np.array(df_P975_15m_monthly_mean.index.month)
df_P975_15m_monthly_mean = df_P975_15m_monthly_mean.sort_values(by="Month")
punto_975 = df_P975_15m_monthly_mean['radiacion']

Radiacion = []
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    mint = fechas[i].minute
    rad = np.where((df_P975_15m_monthly_mean.index.month == mes) & (df_P975_15m_monthly_mean.index.hour == hora) & (df_P975_15m_monthly_mean.index.minute == mint))[0]

    if len(rad) == 0:
        Radiacion.append(np.nan)
    else:
        Radiacion.append(punto_975.iloc[rad].values[0])
df_RadMed975 = pd.DataFrame()
df_RadMed975['fecha_hora'] = fechas
df_RadMed975['Radiacion_Med'] = Radiacion
df_RadMed975.index = df_RadMed975['fecha_hora']
df_RadMed975 = df_RadMed975.drop(['fecha_hora'], axis=1)
df_RadMed975 = df_RadMed975.between_time('06:00', '17:59')

df_Anomal_975 = pd.concat([df_RadMed975, df_P975_15m], axis=1)
df_Anomal_975['Anomalia'] = df_Anomal_975['radiacion']- df_Anomal_975['Radiacion_Med']
df_Anomal_975.to_csv(Path_save + 'df_AnomalRad_pix975_2018_2019.csv')

##------------------------------------------------------------------350-------------------------------------------------------------##
df_P350_15m = df_P350_15m.drop(['Unnamed: 0', 'idestacion',  'temperatura'], axis=1)
df_P350_15m = df_P350_15m.between_time('06:00', '17:59')
df_P350_15m_monthly_mean = df_P350_15m.groupby([df_P350_15m.index.month, df_P350_15m.index.hour, df_P350_15m.index.minute]).mean()
fechas_horas_CM = []
for i in range(len(df_P350_15m_monthly_mean.index)):
    fechas_horas_CM.append(pd.to_datetime('2018-'+str(df_P350_15m_monthly_mean.index[i][0])+' '+str(df_P350_15m_monthly_mean.index[i][1])+':'+str(df_P350_15m_monthly_mean.index[i][2]), format="%Y-%m %H:%M", errors='coerce'))

df_P350_15m_monthly_mean.index= fechas_horas_CM
df_P350_15m_monthly_mean = df_P350_15m_monthly_mean.sort_index()
df_P350_15m_monthly_mean['Month'] = np.array(df_P350_15m_monthly_mean.index.month)
df_P350_15m_monthly_mean = df_P350_15m_monthly_mean.sort_values(by="Month")
punto_350 = df_P350_15m_monthly_mean['radiacion']

Radiacion = []
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    mint = fechas[i].minute
    rad = np.where((df_P350_15m_monthly_mean.index.month == mes) & (df_P350_15m_monthly_mean.index.hour == hora) & (df_P350_15m_monthly_mean.index.minute == mint))[0]

    if len(rad) == 0:
        Radiacion.append(np.nan)
    else:
        Radiacion.append(punto_350.iloc[rad].values[0])
df_RadMed350 = pd.DataFrame()
df_RadMed350['fecha_hora'] = fechas
df_RadMed350['Radiacion_Med'] = Radiacion
df_RadMed350.index = df_RadMed350['fecha_hora']
df_RadMed350 = df_RadMed350.drop(['fecha_hora'], axis=1)
df_RadMed350 = df_RadMed350.between_time('06:00', '17:59')

df_Anomal_350 = pd.concat([df_RadMed350, df_P350_15m], axis=1)
df_Anomal_350['Anomalia'] = df_Anomal_350['radiacion']- df_Anomal_350['Radiacion_Med']
df_Anomal_350.to_csv(Path_save + 'df_AnomalRad_pix350_2018_2019.csv')

##------------------------------------------------------------------348-------------------------------------------------------------##
df_P348_15m = df_P348_15m.drop(['Unnamed: 0', 'idestacion',  'temperatura'], axis=1)
df_P348_15m = df_P348_15m.between_time('06:00', '17:59')
df_P348_15m_monthly_mean = df_P348_15m.groupby([df_P348_15m.index.month, df_P348_15m.index.hour, df_P348_15m.index.minute]).mean()
fechas_horas_CM = []
for i in range(len(df_P348_15m_monthly_mean.index)):
    fechas_horas_CM.append(pd.to_datetime('2018-'+str(df_P348_15m_monthly_mean.index[i][0])+' '+str(df_P348_15m_monthly_mean.index[i][1])+':'+str(df_P348_15m_monthly_mean.index[i][2]), format="%Y-%m %H:%M", errors='coerce'))

df_P348_15m_monthly_mean.index= fechas_horas_CM
df_P348_15m_monthly_mean = df_P348_15m_monthly_mean.sort_index()
df_P348_15m_monthly_mean['Month'] = np.array(df_P348_15m_monthly_mean.index.month)
df_P348_15m_monthly_mean = df_P348_15m_monthly_mean.sort_values(by="Month")
punto_348 = df_P348_15m_monthly_mean['radiacion']

Radiacion = []
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    mint = fechas[i].minute
    rad = np.where((df_P348_15m_monthly_mean.index.month == mes) & (df_P348_15m_monthly_mean.index.hour == hora) & (df_P348_15m_monthly_mean.index.minute == mint))[0]

    if len(rad) == 0:
        Radiacion.append(np.nan)
    else:
        Radiacion.append(punto_348.iloc[rad].values[0])
df_RadMed348 = pd.DataFrame()
df_RadMed348['fecha_hora'] = fechas
df_RadMed348['Radiacion_Med'] = Radiacion
df_RadMed348.index = df_RadMed348['fecha_hora']
df_RadMed348 = df_RadMed348.drop(['fecha_hora'], axis=1)
df_RadMed348 = df_RadMed348.between_time('06:00', '17:59')

df_Anomal_348 = pd.concat([df_RadMed348, df_P348_15m], axis=1)
df_Anomal_348['Anomalia'] = df_Anomal_348['radiacion']- df_Anomal_348['Radiacion_Med']
df_Anomal_348.to_csv(Path_save + 'df_AnomalRad_pix348_2018_2019.csv')
