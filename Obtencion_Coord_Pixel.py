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
import pytz
import pysolar
import pvlib

################################################################################
## ----------------INGRESAR PARAMETROS INICIALES DEL  CODIGO------------------##
################################################################################

fi = '2018-01-01'
ff = '2019-01-01'

Altura = 'Ceilometro'  ##--> Para que sea con los datos, la palabra debe ser 'Ceilometro'
Horizonte = 'Anio'    ##-->Para que tome datos desde el 2018 ceilometro se pone 'Anio', para que tome solo lo del experimento se pone 'Exp'
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'

##############################################################################################
## ----------------------ÁNGULOS DE INCLINACIÓN EN GRADOS DECIMALES----------------------- ##
##############################################################################################

Inc_Betha_975 = 8
Inc_Betha_350 = 9
Inc_Betha_348 = 3

Surface_Azimuth_975 = 0
Surface_Azimuth_350 = 180
Surface_Azimuth_348 = 90

###############################################################################################
## ----------------OBTENIENDO INCIDENCIA, AZIMUTH Y ZENITH PARA CADA PUNTO------------------ ##
###############################################################################################

Latitudes = [6.259, 6.168, 6.255]        ## En orden: 6001, 6002, 6003
Longitudes = [-75.588, -75.644, -75.542] ## En orden: 6001, 6002, 6003

lat975, lon975 = Latitudes[0], Longitudes[0]
lat350, lon350 = Latitudes[1], Longitudes[1]
lat348, lon348 = Latitudes[2], Longitudes[2]

def daterange(start_date, end_date):
    'Ayuda a la abtencion de un rango de fechas. Revisar el parametro delta'
    import datetime
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(hours = 1)
    while start_date <= end_date:
        yield start_date
        start_date += delta

date_range = []
for i in daterange(fi, ff):
    date_range.append(i)

timezone = pytz.timezone("America/Bogota")
date_range_aware = [timezone.localize(date_range[i]) for i in range(len(date_range))]

##-----------------------------------------------------------------------------------##

azimuth975 = []
altitude_deg975 = []
for i in range(len(date_range_aware)):
    az,  al = pysolar.solar.get_position(lat975, lon975, date_range_aware[i])
    azimuth975.append(az)
    altitude_deg975.append(al)

zenith975 = [90 - altitude_deg975[i] for i in range(len(altitude_deg975))]

incidence975 = []
for i in range(len(azimuth975)):
    inc = pvlib.irradiance.aoi(Inc_Betha_975, Surface_Azimuth_975, zenith975[i], azimuth975[i])
    incidence975.append(inc)

df_angulos_975 = pd.DataFrame()
df_angulos_975['Incidencia'] = incidence975
df_angulos_975['Azimuth'] = azimuth975
df_angulos_975['Zenith'] = zenith975
df_angulos_975.index = date_range
df_angulos_975 = df_angulos_975.between_time('06:00', '18:00')

##-----------------------------------------------------------------------------------##

azimuth350 = []
altitude_deg350 = []
for i in range(len(date_range_aware)):
    az,  al = pysolar.solar.get_position(lat350, lon350, date_range_aware[i])
    azimuth350.append(az)
    altitude_deg350.append(al)

zenith350 = [90 - altitude_deg350[i] for i in range(len(altitude_deg350))]

incidence350 = []
for i in range(len(azimuth350)):
    inc = pvlib.irradiance.aoi(Inc_Betha_350, Surface_Azimuth_350, zenith350[i], azimuth350[i])
    incidence350.append(inc)

df_angulos_350 = pd.DataFrame()
df_angulos_350['Incidencia'] = incidence350
df_angulos_350['Azimuth'] = azimuth350
df_angulos_350['Zenith'] = zenith350
df_angulos_350.index = date_range
df_angulos_350 = df_angulos_350.between_time('06:00', '18:00')

##-----------------------------------------------------------------------------------##

azimuth348 = []
altitude_deg348 = []
for i in range(len(date_range_aware)):
    az,  al = pysolar.solar.get_position(lat348, lon348, date_range_aware[i])
    azimuth348.append(az)
    altitude_deg348.append(al)


zenith348 = [90 - altitude_deg348[i] for i in range(len(altitude_deg348))]

incidence348 = []
for i in range(len(azimuth348)):
    inc = pvlib.irradiance.aoi(Inc_Betha_348, Surface_Azimuth_348, zenith348[i], azimuth348[i])
    incidence348.append(inc)

df_angulos_348 = pd.DataFrame()
df_angulos_348['Incidencia'] = incidence348
df_angulos_348['Azimuth'] = azimuth348
df_angulos_348['Zenith'] = zenith348
df_angulos_348.index = date_range
df_angulos_348 = df_angulos_348.between_time('06:00', '18:00')

##############################################################################################
## ------------------OBTENIENDO EL PROMEDIO DE LAS ALTURAS APROXIMADOS--------------------- ##
##############################################################################################

if Altura == 'Ceilometro':

    'Los datos se obtienen de Miel Nuevo los datos de altura de nube del ceilómetro con la función cloud_higth'
    'que ya los entrega en hora local. La altura, tiene el label de 0. Estas alturas están en Metros.'

    Alturas_nubes_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudTSHora.csv',  sep=',', index_col =0)
    Alturas_nubes_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudCIHora.csv',  sep=',', index_col =0)
    Alturas_nubes_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudOrientalHora.csv',  sep=',', index_col =0)

    Alturas_nubes_348.index = pd.to_datetime(Alturas_nubes_348.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
    Alturas_nubes_350.index = pd.to_datetime(Alturas_nubes_350.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
    Alturas_nubes_975.index = pd.to_datetime(Alturas_nubes_975.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')


else:

    'Hay un parametro importante por definir apropiadamente y es el de la altura de las nubes. Con los datos, '
    'se espera obtener una altura promedio por hora, la cosa por definir son los pixeles de los q se tomaran '
    'la altura al tope de la nube. Por ahora se construirá un array considerando una altura de 10 Km que es'
    'lo concerniente a la troposfera. Se supone que habra un array por punto.'

    Alturas_nubes_975 = np.repeat(10000, len(df_angulos_975.Incidencia.values))  ## -- > en Km
    Alturas_nubes_350 = np.repeat(10000, len(df_angulos_350.Incidencia.values))  ## -- > en Km
    Alturas_nubes_348 = np.repeat(10000, len(df_angulos_348.Incidencia.values))  ## -- > en Km


result_348 = pd.concat([df_angulos_348,  Alturas_nubes_348], axis=1, join='inner')
result_350 = pd.concat([df_angulos_350,  Alturas_nubes_350], axis=1, join='inner')
result_975 = pd.concat([df_angulos_975,  Alturas_nubes_975], axis=1, join='inner')

df_angulos_975 = result_975
df_angulos_350 = result_350
df_angulos_348 = result_348

##############################################################################################
## -------------------OBTENIENDO EL SEGMENTO DE INCIDENCIA EN CADA PUNTO------------------- ##
##############################################################################################

'El normal va a ser el mismo en todas las observaciones de cada punto ya que solo depende de la altura y '
'del angulo de inclinacion.'

df_angulos_975 ['Normal'] = [df_angulos_975['0'].values[i]*np.cos(np.radians(Inc_Betha_975))  for i in range(len(df_angulos_975['0']))]
df_angulos_350 ['Normal'] = [df_angulos_350['0'].values[i]*np.cos(np.radians(Inc_Betha_350))  for i in range(len(df_angulos_350['0']))]
df_angulos_348 ['Normal'] = [df_angulos_348['0'].values[i]*np.cos(np.radians(Inc_Betha_348))  for i in range(len(df_angulos_348['0']))]

df_angulos_975 ['Segmento'] = [(np.sin(np.radians(df_angulos_975.Incidencia.values[i])))*(df_angulos_975.Normal.values[i]/np.sin(np.radians(90-Inc_Betha_975-df_angulos_975.Incidencia.values[i]))) for i in range(len(df_angulos_975.Incidencia.values))]
df_angulos_350 ['Segmento'] = [(np.sin(np.radians(df_angulos_350.Incidencia.values[i])))*(df_angulos_350.Normal.values[i]/np.sin(np.radians(90-Inc_Betha_350-df_angulos_350.Incidencia.values[i]))) for i in range(len(df_angulos_350.Incidencia.values))]
df_angulos_348 ['Segmento'] = [(np.sin(np.radians(df_angulos_348.Incidencia.values[i])))*(df_angulos_348.Normal.values[i]/np.sin(np.radians(90-Inc_Betha_348-df_angulos_348.Incidencia.values[i]))) for i in range(len(df_angulos_348.Incidencia.values))]

##############################################################################################
## ----------------------OBTENIENDO LA DESCOMPOSICIÓN DEL SEGMENTO ------------------------ ##
##############################################################################################

'Estos resultados son en metros, habria que sumarle estos puntos a cada coordenada para encontrarlas distancias finales.'
'Los valores negativos corresponderían a los del lado opuesto.'

df_angulos_975 ['Desc_Y_lat'] = df_angulos_975.Segmento.values*np.cos(np.radians(df_angulos_975.Azimuth.values))
df_angulos_350 ['Desc_Y_lat'] = df_angulos_350.Segmento.values*np.cos(np.radians(df_angulos_350.Azimuth.values))
df_angulos_348 ['Desc_Y_lat'] = df_angulos_348.Segmento.values*np.cos(np.radians(df_angulos_348.Azimuth.values))

df_angulos_975 ['Desc_X_lon'] = df_angulos_975.Segmento.values*np.sin(np.radians(df_angulos_975.Azimuth.values))
df_angulos_350 ['Desc_X_lon'] = df_angulos_350.Segmento.values*np.sin(np.radians(df_angulos_350.Azimuth.values))
df_angulos_348 ['Desc_X_lon'] = df_angulos_348.Segmento.values*np.sin(np.radians(df_angulos_348.Azimuth.values))

##############################################################################################
## ----------------------OBTENIENDO LAS COORDENADAS PARA CADA HORA ------------------------ ##
##############################################################################################

'A partir de la descomposicion anterior se suman los mentros que rrojan la descomposicion en X y Y considerando las equivalencias'
'de de un grado de las coordenadas geográficas decimales a metros en el Ecuador.'

Equiv_Lat = 110570 ## Equivalencia de un grado de latitud en metros cerca al Ecuador
Equiv_Lon = 111320 ## Equivalencia de un grado de longitud en metros cerca al Ecuador

Equi_Desc_Y_lat_975 = [df_angulos_975 ['Desc_Y_lat'].values[i]/Equiv_Lat for i in range(len(df_angulos_975 ['Desc_Y_lat'].values))]
Equi_Desc_X_lon_975 = [df_angulos_975 ['Desc_X_lon'].values[i] / Equiv_Lon for i in range(len(df_angulos_975 ['Desc_X_lon'].values)) ]
Hourly_Lats_TS = [Equi_Desc_Y_lat_975[i] + Latitudes[0] for i in range(len(Equi_Desc_Y_lat_975))]
Hourly_Lons_TS= [Equi_Desc_X_lon_975[i] + Longitudes[0] for i in range(len(Equi_Desc_X_lon_975))]

Equi_Desc_Y_lat_350 = [df_angulos_350 ['Desc_Y_lat'].values[i]/Equiv_Lat for i in range(len(df_angulos_350 ['Desc_Y_lat'].values))]
Equi_Desc_X_lon_350 = [df_angulos_350 ['Desc_X_lon'].values[i] / Equiv_Lon for i in range(len(df_angulos_350 ['Desc_X_lon'].values)) ]
Hourly_Lats_CI = [Equi_Desc_Y_lat_350[i] + Latitudes[1] for i in range(len(Equi_Desc_Y_lat_350))]
Hourly_Lons_CI= [Equi_Desc_X_lon_350[i] + Longitudes[1] for i in range(len(Equi_Desc_X_lon_350))]

Equi_Desc_Y_lat_348 = [df_angulos_348 ['Desc_Y_lat'].values[i]/Equiv_Lat for i in range(len(df_angulos_348 ['Desc_Y_lat'].values))]
Equi_Desc_X_lon_348 = [df_angulos_348 ['Desc_X_lon'].values[i] / Equiv_Lon for i in range(len(df_angulos_348 ['Desc_X_lon'].values)) ]
Hourly_Lats_JV = [Equi_Desc_Y_lat_348[i] + Latitudes[2] for i in range(len(Equi_Desc_Y_lat_348))]
Hourly_Lons_JV= [Equi_Desc_X_lon_348[i] + Longitudes[2] for i in range(len(Equi_Desc_X_lon_348))]

np.save(Path_save[0:45]+ Horizonte+'HourlyLat_TS', Hourly_Lats_TS)
np.save(Path_save[0:45]+ Horizonte+'HourlyLat_CI', Hourly_Lats_CI)
np.save(Path_save[0:45]+ Horizonte+'HourlyLat_JV', Hourly_Lats_JV)

np.save(Path_save[0:45]+ Horizonte+'HourlyLon_TS', Hourly_Lons_TS)
np.save(Path_save[0:45]+ Horizonte+'HourlyLon_CI', Hourly_Lons_CI)
np.save(Path_save[0:45]+ Horizonte+'HourlyLon_JV', Hourly_Lons_JV)

np.save(Path_save[0:45]+ Horizonte+'FechasHourlyCoords', df_angulos_975.index)

df_Lats_Lons_hourly_TS = pd.DataFrame({'Latitudes':Hourly_Lats_TS, 'Longitudes':Hourly_Lons_TS}, index = df_angulos_975.index)
df_Lats_Lons_hourly_CI = pd.DataFrame({'Latitudes':Hourly_Lats_CI, 'Longitudes':Hourly_Lons_CI}, index = df_angulos_350.index)
df_Lats_Lons_hourly_JV = pd.DataFrame({'Latitudes':Hourly_Lats_JV, 'Longitudes':Hourly_Lons_JV}, index = df_angulos_348.index)


df_Lats_Lons_hourly_TS.to_csv(Path_save[0:45]+ Horizonte+'_DFHourlyCoords_TS'+'.csv', sep=',')
df_Lats_Lons_hourly_CI.to_csv(Path_save[0:45]+ Horizonte+'_DFHourlyCoords_CI'+'.csv', sep=',')
df_Lats_Lons_hourly_JV.to_csv(Path_save[0:45]+ Horizonte+'_DFHourlyCoords_JV'+'.csv', sep=',')
