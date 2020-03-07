#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
# import netCDF4 as nc
# from netCDF4 import Dataset
id
import itertools
import datetime
from scipy.stats import ks_2samp
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import matplotlib.cm as cm
import os
import statistics
from scipy import stats
import scipy.stats as st

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa par aa creación de un 3D array con la información de reflectancia incidente para cada pixeles
en cada paso de tiempo. El resultado será para cada de tiempo  de las imagenes de GOES.
"""
##############################################################################################
## ------------------LECTURA DE LOS DATOS PROVENIENTES DE LOS RASTERS---------------------- ##
##############################################################################################
Lon_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_IrradianceInterpolate.npy')
Lat_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_IrradianceInterpolate.npy')
fechas_horas_Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_IrradianceInterpolate.npy')
fechas_horas_Irra = pd.to_datetime(fechas_horas_Irra, format="%Y-%m-%d %H:%M", errors='coerce')
Hourly_Lats = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/HourlyLat_Malla.npy')
Hourly_Lons = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/HourlyLon_Malla.npy')


Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')
fechas_horas_GOES = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')
Lat_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
Lon_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')

Hourly_Lats[Hourly_Lats>=np.nanmax(Lat_GOES)] = np.nan
Hourly_Lats[Hourly_Lats<=np.nanmin(Lat_GOES)] = np.nan
Hourly_Lons[Hourly_Lons>=np.nanmax(Lon_GOES)] = np.nan
Hourly_Lons[Hourly_Lons<=np.nanmin(Lon_GOES)] = np.nan

##############################################################################################
## --------------DEFINICION DE LAS FUNCIONES PARA LA SELECCIOND DE DATOS------------------- ##
##############################################################################################

lat_irra=Hourly_Lats
lon_irra=Hourly_Lons
lat_GOES=Lat_GOES
lon_GOES= Lon_GOES

prec = 6
delta = 0.01

lat_index = np.zeros(lat_irra.shape)
lon_index = np.zeros(lon_irra.shape)

for k in range(lat_irra.shape[0]): # time
    for i in range(lat_irra.shape[1]): # lat
        for j in range(lat_irra.shape[2]): # lon
            if m.isnan(lat_irra[k, i, j]) == False and m.isnan(lon_irra[k, i, j]) == False:
                print('Si lo hace')
                lat_index[k,i,j] = np.where((lat_GOES[:, 0] >= (round(float(lat_irra[k,i,j]),prec))-delta) & (lat_GOES[:, 0] <= (round(float(lat_irra[k,i,j]),prec)+delta)))[0][0]
                lon_index[k,i,j] = np.where((lon_GOES[0, :] >= (round(float(lon_irra[k,i,j]),prec))-delta) & (lon_GOES[0, :] <= (round(float(lon_irra[k,i,j]),prec)+delta)))[0][0]
            elif m.isnan(lat_irra[k, i, j]) == True or m.isnan(lon_irra[k, i, j]) == True:
                print('Es nan')
                lat_index[k,i,j] = np.nan
                lon_index[k,i,j] = np.nan

Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
np.save(Path_save[0:45]+'Array_Lat_index_Malla', lat_index)
np.save(Path_save[0:45]+'Array_Lon_index_Malla', lon_index)
print('Arrays de indices generados y guardados')
