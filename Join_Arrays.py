#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import netCDF4 as nc
from netCDF4 import Dataset
id
import datetime
import pytz
import pysolar
import scipy.interpolate as inter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"Codigo para unir dos arrays. Usado cuando los nc fueron muy grandes."

###############################################################################
##---------------------------LECTURA DE LOS ARRAYS---------------------------##
###############################################################################

Rad_1 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad2018CH2.npy')
fechas_horas_1 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_2018CH2.npy')
lat_1 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_2018CH2.npy')
lon_1 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_2018CH2.npy')

Rad_2 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2019CH2.npy')
fechas_horas_2 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2_2019.npy')
lat_2 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2019.npy')
lon_2 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2019.npy')

###############################################################################
##---------------------------UNION DE LOS ARRAYS-----------------------------##
###############################################################################

Rad_Full = np.vstack((Rad_2, Rad_1))
fechas_horas_Full = np.hstack((fechas_horas_1, fechas_horas_2)) ## -->C0n esta funcion el segundo array debe extenderse a q sea 2D y q se concatene con el axis =1
Lat_Full = np.vstack((lat_1, lat_2))
Lon_Full = np.vstack((lon_1, lon_2))

####################################################################################
##---------------------------VERIFICACION DE LOS ARRAYS---------------------------##
####################################################################################

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2018_2019.nc')

lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :]
Rad = ds.variables['Radiancias'][:, :, :]

tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
fechas_horas = pd.to_datetime(fechas_horas, errors='coerce')

nombre_rad ='Array_Rad_2018_2019CH2'
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
nombre_lat = 'Array_Lat_CH2_2018_2019'
nombre_lon = 'Array_Lon_CH2_2018_2019'
nombre_fechas_horas = 'Array_FechasHoras_CH2__2018_2019'

np.save(Path_save[0:45]+nombre_rad, Rad)
np.save(Path_save[0:45]+nombre_lat, lat)
np.save(Path_save[0:45]+nombre_lon, lon)
np.save(Path_save[0:45]+nombre_fechas_horas, fechas_horas)

##############################################################################
##---------------------------GUARDANDO LOS ARRAYS---------------------------##
##############################################################################
