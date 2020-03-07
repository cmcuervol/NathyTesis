#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import netCDF4 as nc
from netCDF4 import Dataset
import os
import rasterio
from scipy.interpolate import griddata
from scipy import interpolate

Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

"""
Codigo para la interpolacion de las latitudes y las longiutes, a usar como medida
extrema cuando se dañen los arrays de latitudes y de las Longitudes.
"""

################################################################################
##------------------LECTURA DE LOS DATOS DE GOES CH2--------------------------##
################################################################################

"Las lats y lons de GOES serán la malla de referencia."

lat_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
lon_GOES = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')

################################################################################
##----------------------INTERPOLANDO LOS DATOS--------------------------------##
################################################################################


x = np.arange(0, lat_GOES.shape[1], 1)
y = np.arange(0, lat_GOES.shape[0], 1)
f = interpolate.interp2d(x, y, lat_GOES[:,:])
xnew = np.arange(0, lat_GOES.shape[1], 3.9)
ynew = np.arange(0, lat_GOES.shape[0], 4)
Lat_new = f(xnew, ynew)
Lat_new=np.array(Lat_new)

del x, y, f, xnew, ynew

x = np.arange(0, lon_GOES.shape[1], 1)
y = np.arange(0, lon_GOES.shape[0], 1)
f = interpolate.interp2d(x, y, lon_GOES[:,:])
xnew = np.arange(0, lon_GOES.shape[1], 3.9)
ynew = np.arange(0, lon_GOES.shape[0], 4)
Lon_new = f(xnew, ynew)
Lon_new=np.array(Lon_new)

############################################################################################
##----------------------------GUARDANDO EL ARRAY INTERPOLADO -----------------------------##
############################################################################################

np.save(Path_save+'Array_Lat_COD_Junio', Lat_new)
np.save(Path_save+'Array_Lon_COD_Junio', Lon_new)
