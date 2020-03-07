#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import math as m
id
import itertools
import datetime
from scipy.stats import ks_2samp
import os
import statistics
from pysolar.solar import *
from scipy.stats import pearsonr
from scipy import stats
import scipy.stats as st
import scipy.special as sp

################################################################################
## ---------------------CALCULO DE LA RADIACIÓN TEORICA---------------------- ##
################################################################################

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

    data_Model = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_Totales/Total_Timeseries_Rad_2018.csv', sep=',')

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
