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
id
import itertools
import datetime
from scipy.stats import ks_2samp
import matplotlib.colors as colors
import pytz
import pysolar
import pvlib
from datetime import datetime, timedelta

"""
Codigo para la creación de dos 3D array con la información de la latitud y la
logitud relevante para cada pixel de cada hora, considerando la altura promedio
de la nube, el angulo de incidencia, la pendiente y el aspecto de la superficie.

"""

##############################################################################################
## ------------------OBTENIENDO EL PROMEDIO DE LAS ALTURAS APROXIMADOS--------------------- ##
##############################################################################################

'Los datos se obtienen de Miel Nuevo los datos de altura de nube del ceilómetro con la función cloud_higth'
'que ya los entrega en hora local. La altura, tiene el label de 0. Estas alturas están en Metros.'

Alturas_nubes_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudTSHora.csv',  sep=',', index_col =0)
Alturas_nubes_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudCIHora.csv',  sep=',', index_col =0)
Alturas_nubes_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudOrientalHora.csv',  sep=',', index_col =0)

df_Total_Altura_Nubes =  pd.concat((Alturas_nubes_975, Alturas_nubes_350, Alturas_nubes_348), axis=1).mean(axis=1)
df_Total_Altura_Nubes.index = pd.to_datetime(df_Total_Altura_Nubes.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_Total_Altura_Nubes = df_Total_Altura_Nubes.between_time('06:00', '18:00')
df_Altura_Nubes_season =  df_Total_Altura_Nubes.groupby([df_Total_Altura_Nubes.index.month, df_Total_Altura_Nubes.index.hour]).mean()

##############################################################################################
## ------------------LECTURA DE LOS DATOS PROVENIENTES DE LOS RASTERS---------------------- ##
##############################################################################################

Aspect = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Aspect_Interpolate.npy')
Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Irradiance_Interpolate.npy')
Slope = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Slope_Interpolate.npy')
Lon_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_IrradianceInterpolate.npy')
Lat_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_IrradianceInterpolate.npy')
fechas_horas_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_IrradianceInterpolate.npy')
fechas_horas_Irra = pd.to_datetime(fechas_horas_Irra, format="%Y-%m-%d %H:%M", errors='coerce')
def hour_rounder(t):
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

fechas_horas_Irra = [hour_rounder(fechas_horas[i]) for i in range(len(fechas_horas))]
fechas_horas_Irra = np.array(fechas_horas_Irra)

timezone = pytz.timezone("America/Bogota")
fechas_horas_Irra_aware = [timezone.localize(pd.to_datetime(fechas_horas_Irra[i], format="%Y-%m-%d %H:%M", errors='coerce')) for i in range(len(fechas_horas_Irra))]

Irra[Irra < 0] = np.nan

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2__2018_2019.npy')
Lat_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
Lon_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')

##############################################################################################
## ------------------------CALCULO DE LAS COORDENADAS INCIDENTES--------------------------- ##
##############################################################################################

Equiv_Lat = 110570 ## Equivalencia de un grado de latitud en metros cerca al Ecuador
Equiv_Lon = 111320 ## Equivalencia de un grado de longitud en metros cerca al Ecuador

la = Irra.shape[1]
lo = Irra.shape[2]
Lats = []
Lons = []

for z in range(len(fechas_horas_Irra )):
    print(z)
    la_t = np.zeros((la, lo))
    lo_t = np.zeros((la, lo))
    for i in range(la):
        for j in range(lo):
            if m.isnan(Irra[z, i, j]) == False:
                print('Si lo hace')

                lat = Lat_Irra[i, j]
                lon = Lon_Irra[i, j]
                Inc_Betha = Slope[ i, j]
                Surface_Azimuth = Aspect[ i, j]

                azimuth,  altura = pysolar.solar.get_position(lat, lon, fechas_horas_Irra_aware[z])
                zenith = 90 - altura
                incidencia = pvlib.irradiance.aoi(Inc_Betha, Surface_Azimuth, zenith, azimuth)

                Altura_nube = df_Altura_Nubes_season[(df_Altura_Nubes_season.index.get_level_values(0)==fechas_horas_Irra_aware[z].month)&((df_Altura_Nubes_season.index.get_level_values(1)==fechas_horas_Irra_aware[z].hour))].values[0]

                normal = Altura_nube*np.cos(np.radians(Inc_Betha))
                segmento = (np.sin(np.radians(incidencia)))*(normal/np.sin(np.radians(90-Inc_Betha-incidencia)))
                Desc_Y_lat = segmento*np.cos(np.radians(Surface_Azimuth))
                Desc_X_lon = segmento*np.sin(np.radians(Surface_Azimuth))
                Equi_Desc_Y_lat = Desc_Y_lat/Equiv_Lat
                Equi_Desc_X_lon = Desc_X_lon / Equiv_Lon

                Hourly_Lats_TS = Equi_Desc_Y_lat + lat
                Hourly_Lons_TS = Equi_Desc_X_lon + lon

                la_t[i, j] = Hourly_Lats_TS
                lo_t[i, j] = Hourly_Lons_TS

            elif m.isnan(Irra[z, i, j]) == True:
                print('Es nan')
                la_t[i, j] = np.nan
                lo_t[i, j] = np.nan
    print(z)
    Lats.append(la_t)
    Lons.append(lo_t)
    print('APENDEO')
Lats = np.array(Lats)
Lons = np.array(Lons)

#################################################################################################
##----------------------------GUARDANDO LOS ARRAYS DE COORDENADAS -----------------------------##
#################################################################################################
nombre_fechas_horas = 'Array_FechasHoras_IrradianceInterpolate'
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
np.save(Path_save[0:45]+ 'HourlyLat_Malla', Lats)
np.save(Path_save[0:45]+ 'HourlyLon_Malla', Lons)
np.save(Path_save[0:45]+nombre_fechas_horas, fechas_horas_Irra)
