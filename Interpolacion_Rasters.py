#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
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
import os
import rasterio
from scipy.interpolate import griddata

Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

"""
Codigo para la implementación del metodo de interpolacion en los raster y ncdfs
correspondientes a la información de raciacion solar en condiciones de cielo despejado,
de aspectos y de pendieentes.
"""

##############################################################################
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------
##############################################################################

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

################################################################################
##------------------LECTURA DEL NC DE RADIACION-------------------------------##
################################################################################

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Raster/Climatology_rad_clear_sky_Kumar.nc')
lat = ds.variables['lat'][:]
lat = lat[::-1]
lon = ds.variables['lon'][:]
Irra = ds.variables['Irradiancia'][:, :, :]
Irra = Irra[:,::-1, :]
tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas)):
    fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')
fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')
def hour_rounder(t):
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

fechas_horas = [hour_rounder(fechas_horas[i]) for i in range(len(fechas_horas))]
fechas_horas = np.array(fechas_horas)
################################################################################
##------------------LECTURA DE LOS DATOS DE GOES------------------------------##
################################################################################

"Las lats y lons de GOES serán la malla de referencia."

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
fechas_horas_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2__2018_2019.npy')
lat_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
lon_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')

################################################################################
##----------------------LECTURA DE LOS RASTERS--------------------------------##
################################################################################

with rasterio.open('/home/nacorreasa/Maestria/Datos_Tesis/DEMs/slope_amva_landsat.tif', 'r') as ds:
    slope = ds.read()  # read all raster values

with rasterio.open('/home/nacorreasa/Maestria/Datos_Tesis/DEMs/aspect_amva_landsat.tif', 'r') as ds:
    aspect = ds.read()  # read all raster values

################################################################################
##----------------------INTERPOLANDO LOS DATOS--------------------------------##
################################################################################
X, Y = np.meshgrid(lon, lat)

X_r = X.ravel()
Y_r = Y.ravel()

slope_r = slope.ravel()
slope_interpol = griddata((Y_r, X_r), slope_r, (lat_GOES, lon_GOES), method='linear')

aspect_r = aspect.ravel()
aspect_interpol = griddata((Y_r, X_r), aspect_r, (lat_GOES, lon_GOES), method='linear')

Irra_interpol=[]
for i in range(len(fechas_horas)):
    Irra_r = Irra[i, :, :].ravel()
    Irra_N = griddata((Y_r, X_r), Irra_r, (lat_GOES, lon_GOES), method='linear')
    Irra_interpol.append(Irra_N)

Irra_interpol = np.array(Irra_interpol)

X_r = X.ravel()
lon_interpol = griddata((Y_r, X_r), X_r, (lat_GOES, lon_GOES), method='linear')

Y_r = Y.ravel()
lat_interpol = griddata((Y_r, X_r), Y_r, (lat_GOES, lon_GOES), method='linear')

##----------------------------------------------------------------------------------------##

fechas_horas = [fechas_horas[i].strftime('%Y-%m-%d %H:%M') for i in range(len(fechas_horas))]
fechas_horas = np.array(fechas_horas)

############################################################################################
##--------------------------CORROBORANDO CON EL DIBUJO DE ALGUNO--------------------------##
############################################################################################

elegido=48
print(fechas_horas[elegido])

pruebaN = Irra_interpol[elegido, :, :]
prueba = Irra[elegido, :, :]

fig = plt.figure(figsize=[10, 8])
cax1= plt.imshow(prueba)
fig.subplots_adjust(right=0.8)
plt.title("Irradiancia original")
cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
fig.colorbar(cax1, label = u"Irradiance", cax=cbar_ax)
plt.subplots_adjust(wspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/IrradianciaOriginal_GIS.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/IrradianciaOriginal_GIS.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

fig = plt.figure(figsize=[10, 8])
cax1= plt.imshow(pruebaN)
fig.subplots_adjust(right=0.8)
plt.title("Irradiancia interpolada")
cbar_ax = fig.add_axes([0.85, 0.35, 0.05, 0.30])
fig.colorbar(cax1, label = u"Irradiance", cax=cbar_ax)
plt.subplots_adjust(wspace=0.3)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/IrradianciaInterpolada_GIS.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/IrradianciaInterpolada_GIS.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


############################################################################################
##----------------------------GUARDANDO EL ARRAY INTERPOLADO -----------------------------##
############################################################################################

nombre_Irra ='Array_Irradiance_Interpolate'
nombre_Slope ='Array_Slope_Interpolate'
nombre_Aspect ='Array_Aspect_Interpolate'
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
nombre_lat = 'Array_Lat_IrradianceInterpolate'
nombre_lon = 'Array_Lon_IrradianceInterpolate'
nombre_fechas_horas = 'Array_FechasHoras_IrradianceInterpolate'

np.save(Path_save[0:45]+nombre_Irra, Irra_interpol)
np.save(Path_save[0:45]+nombre_Slope, slope_interpol)
np.save(Path_save[0:45]+nombre_Aspect, aspect_interpol)
np.save(Path_save[0:45]+nombre_lat, lat_interpol)
np.save(Path_save[0:45]+nombre_lon, lon_interpol)
np.save(Path_save[0:45]+nombre_fechas_horas, fechas_horas)
