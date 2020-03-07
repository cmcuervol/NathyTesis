#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA
import matplotlib
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


#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

#########################################################################
## ----------------LECTURA DE LOS ARCHIVOS DE UMBRALES-----------------##
#########################################################################

df_UmbralH_Nube_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/UmbralH_Nube_348.csv',  sep=',', index_col =0)
df_UmbralH_Nube_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/UmbralH_Nube_350.csv',  sep=',', index_col =0)
df_UmbralH_Nube_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/UmbralH_Nube_975.csv',  sep=',', index_col =0)

df_UmbralH_Nube = pd.concat([df_UmbralH_Nube_348, df_UmbralH_Nube_350, df_UmbralH_Nube_975], axis=1, sort=False)
df_UmbralH_Nube = df_UmbralH_Nube.mean(axis = 1, skipna = True)
df_UmbralH_Nube = pd.DataFrame(df_UmbralH_Nube, columns=['Umbral'])

#########################################################################
## ---------------DETERMINACIÓN DE LA DIMENSION FRACTAL----------------##
#########################################################################

def fractal_dimension(Z):
    assert(len(Z.shape) == 2)

    'https://gist.github.com/viveksck/1110dfca01e4ec2c608515f0d5a5b1d1'
    # From https://github.com/rougier/numpy-100 (#87)
    def boxcount(Z, k):
        S = np.add.reduceat(
            np.add.reduceat(Z, np.arange(0, Z.shape[0], k), axis=0),
                               np.arange(0, Z.shape[1], k), axis=1)
        return len(np.where((S > 0) & (S < k*k))[0])

    # Minimal dimension of image
    p = min(Z.shape)
    # Greatest power of 2 less than or equal to p
    n = 2**np.floor(np.log(p)/np.log(2))
    # Extract the exponent
    n = int(np.log(n)/np.log(2))
    # Build successive box sizes (from 2**n down to 2**1)
    sizes = 2**np.arange(n, 1, -1)
    # Actual box counting with decreasing size
    counts = []
    for size in sizes:
        counts.append(boxcount(Z, size))
    # Fit the successive log(sizes) with log (counts)
    coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)
    return -coeffs[0]

##---------------------------------------------------------------------------------------------------------##
#############################################################################################################
## ------------------LECTURA DE LOS DATOS DE GOES CH2 DURANTE EL REGISTRO DEL EXPERIMENTO------------------##
#############################################################################################################
##---------------------------------------------------------------------------------------------------------##

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2019_0320_0610.nc')


lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :]
Rad = ds.variables['Radiancias'][:, :, :]

                   ## -- Obtener el tiempo para cada valor

tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas)):
    fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')

fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')
fechas_horas = fechas_horas.round('10Min')

#########################################################################
## -------------------ENMASCARAMIENTO DE LAS IMAGENES------------------##
#########################################################################
'Para este caso se tomarán solo los datos comprendidos entre las 6:00 y antes de las 18:00.'
'Esta es la razón del try except IndexError, para el ajuste de los datos y de las fechas. Se'
'toma cada paso de tiempo del array Rad para enmascararlo.'

Rad = Rad[1:-3, :, :]
fechas_horas = fechas_horas[1:-3]
##------------------------------------------------------------------------------------##
Rad_bina = []
Rad_mask = []
fechas_horas_new = []
for i in range (len(fechas_horas)):
    try:
        rad = Rad[i, :, :]
        umbral = df_UmbralH_Nube[df_UmbralH_Nube.Umbral.index == fechas_horas.hour[i]].values[0][0]
        radm = np.ma.masked_where(rad < umbral, rad)
        radbi = (rad > umbral).astype(int)
        Rad_bina.append(radbi)
        Rad_mask.append(radm)
        fechas_horas_new.append(fechas_horas[i])
    except IndexError:
        pass

Rad_bina = np.array(Rad_bina)
Rad_mask = np.array(Rad_mask)

Ci = plt.imshow(Rad_bina[23, :, :])

#########################################################################
## ---------------CICLO DIURNO DE LA DIMENSIÓN FRACTAL-----------------##
#########################################################################

Fractal_Dimension = []
for i in range(0, Rad_bina.shape[0]):
    Fractal_Dimension.append(fractal_dimension(Rad_bina[i, :, :]))

df_Fractal = pd.DataFrame(Fractal_Dimension, index = fechas_horas_new, columns = ['Dim_Fractal'])
df_Fractal_CD = df_Fractal.groupby(by=[df_Fractal.index.hour]).mean()

x_pos = np.array([ 6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17])

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.bar(np.arange(len(x_pos))+0, np.array(df_Fractal_CD.Dim_Fractal.values), align='center', alpha=0.5, label='Desp')
ax.set_xticks(np.arange(0, 12))
ax.set_xticklabels(x_pos)
ax.set_ylabel(u'[W]', fontproperties=prop_1)
ax.set_xlabel(u'Horas del dia', fontproperties=prop_1)
plt.title(u'CD de la dimensión fractal para el experimento',   fontweight = "bold",  fontproperties = prop)
ax.tick_params(color='gray', labelcolor='gray')
for spine in ax.spines.values():
    spine.set_edgecolor('gray')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_fdimention_experimentrecord.png')
plt.show()

##---------------------------------------------------------------------------------------------------------##
#############################################################################################################
## -------------------------LECTURA DE LOS DATOS DE GOES CH2 DURANTE EL 2018-------------------------------##
#############################################################################################################
##---------------------------------------------------------------------------------------------------------##


ds_2018 = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C22018_11_18.nc')


lat_2018 = ds_2018.variables['lat'][:, :]
lon_2018 = ds_2018.variables['lon'][:, :]
Rad_2018 = ds_2018.variables['Radiancias'][:, :, :]

                   ## -- Obtener el tiempo para cada valor

tiempo_2018 = ds_2018.variables['time']
fechas_horas_2018 = nc.num2date(tiempo_2018[:], units=tiempo_2018.units)
for i in range(len(fechas_horas_2018)):
    fechas_horas_2018[i] = fechas_horas_2018[i].strftime('%Y-%m-%d %H:%M')

fechas_horas_2018 = pd.to_datetime(fechas_horas_2018, format="%Y-%m-%d %H:%M", errors='coerce')
fechas_horas_2018 = fechas_horas_2018.round('15Min')

#########################################################################
## -------------------ENMASCARAMIENTO DE LAS IMAGENES------------------##
#########################################################################
'Para este caso se tomarán solo los datos comprendidos entre las 6:00 y antes de las 18:00.'
'Esta es la razón del try except IndexError, para el ajuste de los datos y de las fechas. Se'
'toma cada paso de tiempo del array Rad para enmascararlo.'

Rad_2018 = Rad_2018[1:-2, :, :]
fechas_horas_2018 = fechas_horas_2018[1:-2]
##------------------------------------------------------------------------------------##
Rad_bina_2018 = []
Rad_mask_2018 = []
fechas_horas_new_2018 = []
for i in range (len(fechas_horas_2018)):
    try:
        rad = Rad_2018[i, :, :]
        umbral = df_UmbralH_Nube[df_UmbralH_Nube.Umbral.index == fechas_horas_2018.hour[i]].values[0][0]
        radm = np.ma.masked_where(rad < umbral, rad)
        radbi = (rad > umbral).astype(int)
        Rad_bina_2018.append(radbi)
        Rad_mask_2018.append(radm)
        fechas_horas_new_2018.append(fechas_horas_2018[i])
    except IndexError:
        pass

Rad_bina_2018 = np.array(Rad_bina_2018)
Rad_mask_2018 = np.array(Rad_mask_2018)

############################################################################
## ---------------CICLO DIURNO DE LA DIMENSIÓN FRACTAL 2018---------------##
############################################################################

Fractal_Dimension_2018 = []
for i in range(0, Rad_bina_2018.shape[0]):
    Fractal_Dimension_2018.append(fractal_dimension(Rad_bina_2018[i, :, :]))

df_Fractal_2018 = pd.DataFrame(Fractal_Dimension_2018, index = fechas_horas_new_2018, columns = ['Dim_Fractal'])

df_Fractal_CD_2018 = df_Fractal_2018.groupby(by=[df_Fractal_2018.index.hour]).mean()

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.bar(np.arange(len(x_pos))+0, np.array(df_Fractal_CD_2018.Dim_Fractal.values), align='center', alpha=0.5, label='Desp')
ax.set_xticks(np.arange(0, 12))
ax.set_xticklabels(x_pos)
ax.set_ylabel(u'[W]', fontproperties=prop_1)
ax.set_xlabel(u'Horas del dia', fontproperties=prop_1)
plt.title(u'CD de la dimensión fractal para el 2018',   fontweight = "bold",  fontproperties = prop)
ax.tick_params(color='gray', labelcolor='gray')
for spine in ax.spines.values():
    spine.set_edgecolor('gray')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_fdimention_2018.png')
plt.show()

#######################################################################################################
## ---------------CICLO DIURNO DE LA DIMENSIÓN FRACTAL POR MESES DEL CICLO HIDROLOGICO---------------##
#######################################################################################################

#df_Fractal_2018_DEF = df_Fractal_2018[(df_Fractal_2018.index.month == 1) | (df_Fractal_2018.index.month == 12) | (df_Fractal_2018.index.month == 2)]
df_Fractal_2018_DEF = df_Fractal_2018[(df_Fractal_2018.index.month == 1) | (df_Fractal_2018.index.month == 2)]
df_Fractal_2018_MAM = df_Fractal_2018[(df_Fractal_2018.index.month == 3) | (df_Fractal_2018.index.month == 4) | (df_Fractal_2018.index.month == 5)]
df_Fractal_2018_JJA = df_Fractal_2018[(df_Fractal_2018.index.month == 6) | (df_Fractal_2018.index.month == 7) | (df_Fractal_2018.index.month == 8)]
df_Fractal_2018_SON = df_Fractal_2018[(df_Fractal_2018.index.month == 9) | (df_Fractal_2018.index.month == 10) | (df_Fractal_2018.index.month == 11)]


                                 ## -- Ciclo diurno horario de cada trimestre

df_Fractal_2018_DEF_CD  = df_Fractal_2018_DEF.groupby(by=[df_Fractal_2018_DEF.index.hour]).mean()
df_Fractal_2018_MAM_CD  = df_Fractal_2018_MAM.groupby(by=[df_Fractal_2018_MAM.index.hour]).mean()
df_Fractal_2018_JJA_CD  = df_Fractal_2018_JJA.groupby(by=[df_Fractal_2018_JJA.index.hour]).mean()
df_Fractal_2018_SON_CD  = df_Fractal_2018_SON.groupby(by=[df_Fractal_2018_SON.index.hour]).mean()

##--Grafico CD horario de cada trimestre
x_pos = np.arange(len(df_Fractal_2018_DEF_CD.index))

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(2, 2, 1)
ax1.bar(x_pos, df_Fractal_2018_DEF_CD['Dim_Fractal'], align='center', alpha=0.5)
ax1.set_xticks(np.arange(0, 13))
ax1.set_xticklabels(df_Fractal_2018_DEF_CD.index.values)
ax1.set_ylabel(u'Dimension Fractal', fontproperties=prop_1)
ax1.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax1.set_title('DEF',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(2, 2, 2)
ax2.bar(x_pos, df_Fractal_2018_MAM_CD['Dim_Fractal'], align='center', alpha=0.5)
ax2.set_xticks(np.arange(0, 13))
ax2.set_xticklabels(df_Fractal_2018_MAM_CD.index.values)
ax2.set_ylabel(u'Dimension Fractal', fontproperties=prop_1)
ax2.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax2.set_title(r'MAM',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(2, 2, 3)
ax3.bar(x_pos, df_Fractal_2018_JJA_CD['Dim_Fractal'], align='center', alpha=0.5)
ax3.set_xticks(np.arange(0, 13))
ax3.set_xticklabels(df_Fractal_2018_JJA_CD.index.values)
ax3.set_ylabel(u'Dimension Fractal', fontproperties=prop_1)
ax3.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax3.set_title(u'JJA',   fontweight = "bold",  fontproperties = prop)

ax4 = fig.add_subplot(2, 2, 4)
ax4.bar(x_pos, df_Fractal_2018_SON_CD['Dim_Fractal'], align='center', alpha=0.5)
ax4.set_xticks(np.arange(0, 13))
ax4.set_xticklabels(df_Fractal_2018_SON_CD.index.values)
ax4.set_ylabel(u'Dimension Fractal', fontproperties=prop_1)
ax4.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax4.set_title(u'SON',   fontweight = "bold",  fontproperties = prop)

plt.subplots_adjust( wspace=0.3, hspace=0.4)
fig.suptitle(u"CD Trimestral", fontsize=15, fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_TRIMESTRALfdimention_2018.png')
plt.show()
