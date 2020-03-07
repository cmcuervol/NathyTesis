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
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import math as m
import matplotlib.dates as mdates
import netCDF4 as nc
from netCDF4 import Dataset
id
import itertools
import datetime
from pylab import *
from scipy.ndimage import measurements
import matplotlib.colors as colors
import os

fec_ini ='2019-05-15'
fec_fin ='2019-12-31'
Recorte_Rad = 'no' ##---> Será 'si' para que recorte el set de Reflectancias original a las fechas de COD y los enmascare.
                   ##      En 'si consume mucha ram y debe correrse este programa por partes'
fi = datetime.datetime.strptime(fec_ini,"%Y-%m-%d")
ff =datetime. datetime.strptime(fec_fin,"%Y-%m-%d")
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##--------------------SECCION UNO: RELACION AREAS Y COD-----------------------##
#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa para analizar la relacion entre la COD y las refelctancias, asi como el
area de las nubes y las COD. En amos casos se grafica el scatter.
"""
###############################################################################
##---------------LECTURA DEL NETCDF CON LOS DATOS GOES COD-------------------##
###############################################################################

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_COD_05-2019-12-2019.nc')

COD = ds.variables['COD'][:, :, :]
tiempo = ds.variables['time']
fechas_horas_COD = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas_COD)):
    fechas_horas_COD[i] = fechas_horas_COD[i].strftime('%Y-%m-%d %H:%M')
fechas_horas_COD = pd.to_datetime(fechas_horas_COD, format="%Y-%m-%d %H:%M", errors='coerce')
lat_COD = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_COD_Junio.npy')
lon_COD = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_COD_Junio.npy')

COD = np.ma.filled(COD, fill_value=0.)
COD[COD ==0.] =np.nan

Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
np.save(Path_save[0:45]+'Array_COD_05-2019-12-2019', COD)
np.save(Path_save[0:45]+'Array_FechasHoras_COD_05-2019-12-2019',fechas_horas_COD )

if Recorte_Rad == 'si':
    ###############################################################################
    ## -------------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL-------------- ##
    ###############################################################################

    Rad_origin = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
    fechas_horas_Rad_origin = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2__2018_2019.npy')
    fechas_horas_Rad_origin = pd.to_datetime(fechas_horas_Rad_origin, format="%Y-%m-%d %H:%M", errors='coerce')

    Rad = Rad_origin[(fechas_horas_Rad_origin>= fi)&(fechas_horas_Rad_origin<=ff)]
    fechas_horas_Rad =  fechas_horas_Rad_origin[(fechas_horas_Rad_origin>= fi)&(fechas_horas_Rad_origin<=ff)]
    ################################################################################
    ## -----------------LECTURA DE LOS UMBRALES DE LAS REFLECTANCIAS------------- ##
    ################################################################################
    df_UmbralH_Nube_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Nuba.csv',  sep=',', index_col =0,  header = None)
    df_UmbralH_Nube_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Nuba.csv',  sep=',', index_col =0,  header = None)
    df_UmbralH_Nube_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Nuba.csv',  sep=',', index_col =0,  header = None)

    df_UmbralH_Nube = pd.concat([df_UmbralH_Nube_348, df_UmbralH_Nube_350, df_UmbralH_Nube_975], axis=1)
    df_UmbralH_Nube = df_UmbralH_Nube.mean(axis = 1, skipna = True)
    df_UmbralH_Nube = pd.DataFrame(df_UmbralH_Nube, columns=['Umbral'])

    ################################################################################
    ## -----------------------ENMASCARAMIENTO DE LAS IMAGENES---------------------##
    ################################################################################
    Rad_bina = []
    Rad_mask = []
    fechas_horas_new = []
    for i in range (len(fechas_horas_Rad)):
        for j in range(len(df_UmbralH_Nube.Umbral.index)):
            if df_UmbralH_Nube.Umbral.index[j] == fechas_horas_Rad[i].hour:
                umbral = df_UmbralH_Nube.Umbral[j+6]
                rad = Rad[i, :, :]
                radbi = (rad > umbral).astype(int)
                rad[rad<umbral]=np.nan
                Rad_bina.append(radbi)
                Rad_mask.append(rad)
                fechas_horas_new.append(fechas_horas_Rad[i])
                print('yes')
            else:
                pass

    Rad_bina = np.array(Rad_bina)
    Rad_mask = np.array(Rad_mask)

    ##----------------------------------------------------------------------------------------##

    fechas_horas_new = [fechas_horas_new[i].strftime('%Y-%m-%d %H:%M') for i in range(len(fechas_horas_new))]
    fechas_horas_new = np.array(fechas_horas_new)
    Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
    np.save(Path_save[0:45]+'Array_Rad_bina_05-2019-12-2019', Rad_bina)
    np.save(Path_save[0:45]+'Array_Rad_mask_05-2019-12-2019', Rad_mask)
    np.save(Path_save[0:45]+'Array_Fechas_Horas_Rad_05-2019-12-2019', fechas_horas_new)
else:
    Rad_bina = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_bina_05-2019-12-2019.npy')
    Rad_mask = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_mask_05-2019-12-2019.npy')
    fechas_horas_new = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Fechas_Horas_Rad_05-2019-12-2019.npy')
    fechas_horas_new = pd.to_datetime(fechas_horas_new, format="%Y-%m-%d %H:%M", errors='coerce')
    pass
################################################################################
## -------------LEYENDO LAS AREAS DE LAS IMAGENES ENMASCARADAS----------------##
################################################################################
"""
El procedimiendo para obtener las areas es muy pesado entonces toca hacerlo
por partes, es decir, para longitudes aproximadas de 5mil elementos.
"""
# save np.load
np_load_old = np.load
# modify the default parameters of np.load
np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)

Area_1 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_AREA1Rad_bina_05-2019-12-2019.npy')
Area_2 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_AREA2Rad_bina_05-2019-12-2019.npy')
Area_3 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_AREA3Rad_bina_05-2019-12-2019.npy')

np.load = np_load_old

Area_complete = np.concatenate((Area_1, Area_2, Area_3))
#Area_complete = (Area_complete [Area_complete >=4]).all()

################################################################################
## --------------CREANDO DF CON LOS DATOS DE AREAS DE INTERES-----------------##
################################################################################
Area=[]
for i in range(len(fechas_horas_new)):
    a = Area_complete[i]
    a[a<4.]=np.nan
    Area.append(a)
Area = np.array(Area)

Area_max=[]
for i in range(len(fechas_horas_new)):
    a_max = np.nanmax(Area[i])
    Area_max.append(a_max)
Area_max = np.array(Area_max)

Area_min=[]
for i in range(len(fechas_horas_new)):
    a_min = np.nanmin(Area[i])
    Area_min.append(a_min)
Area_min = np.array(Area_min)

Area_mean=[]
for i in range(len(fechas_horas_new)):
    a_mean = np.nanmean(Area[i])
    Area_mean.append(a_mean)
Area_mean = np.array(Area_mean)

df_areas = pd.DataFrame({'Area':Area, 'Area_max':Area_max, 'Area_min':Area_min, 'Area_mean':Area_mean}, index= fechas_horas_new)

################################################################################
## ---------------CREANDO DF CON LOS DATOS DE COD DE INTERÉS------------------##
################################################################################

COD_max=[]
for i in range(len(fechas_horas_COD)):
    a_max = np.nanmax(COD[i])
    COD_max.append(a_max)
COD_max = np.array(COD_max)

COD_min=[]
for i in range(len(fechas_horas_COD)):
    a_min = np.nanmin(COD[i])
    COD_min.append(a_min)
COD_min = np.array(COD_min)

COD_mean=[]
for i in range(len(fechas_horas_COD)):
    a_mean = np.nanmean(COD[i])
    COD_mean.append(a_mean)
COD_mean = np.array(COD_mean)

df_COD = pd.DataFrame({'COD_max':COD_max, 'COD_min':COD_min, 'COD_mean':COD_mean}, index= fechas_horas_COD)

################################################################################
## --------------CONCATENANDO LOS DOS DATAFRAMES PARA DIBUJAR-----------------##
################################################################################

df_complete = pd.concat([df_COD,  df_areas], axis=1)
df_complete = df_complete.between_time('06:00', '17:59')

################################################################################
## ------------------------------GRAFICA MAXIMOS------------------------------##
################################################################################

fig = plt.figure(figsize=[8, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_complete.COD_max.values, df_complete.Area_max.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax1.set_ylabel(u"Tamaño", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relacion Tamaño vs. COD maximos' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.set_ylim(0, np.nanmax(df_complete.Area_max.values))
ax1.set_xlim(0, 160)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_Size_vs_COD_max.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_Size_vs_COD_max.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


################################################################################
## ------------------------------GRAFICA PROMEDIO-----------------------------##
################################################################################

fig = plt.figure(figsize=[8, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_complete.COD_mean.values, df_complete.Area_mean.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax1.set_ylabel(u"Tamaño", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relacion Tamaño vs. COD promedios' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.set_ylim(0, np.nanmax(df_complete.Area_mean.values)+1)
ax1.set_xlim(0, 160)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_Size_vs_COD_mean.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_Size_vs_COD_mean.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##---------------SECCION DOS: RELACION REFLECTANCIAS Y COD--------------------##
#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa par ala relacionar las COD y los valores de reflecyancia entre los tres
punto de interes.
"""
#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

COD_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix975_EXP.npy')
COD_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix350_EXP.npy')
COD_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix348_EXP.npy')
fechas_horas_COD = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CODEXP.npy')

                   ## -- Selección del pixel de la TS
COD_df_975 = pd.DataFrame()
COD_df_975['Fecha_Hora'] = fechas_horas_COD
COD_df_975['COD'] = COD_pixel_975
COD_df_975['Fecha_Hora'] = pd.to_datetime(COD_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_975.index = COD_df_975['Fecha_Hora']
COD_df_975 = COD_df_975.drop(['Fecha_Hora'], axis=1)

                   ## -- Selección del pixel de la CI

COD_df_350 = pd.DataFrame()
COD_df_350['Fecha_Hora'] = fechas_horas_COD
COD_df_350['COD'] = COD_pixel_350
COD_df_350['Fecha_Hora'] = pd.to_datetime(COD_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_350.index = COD_df_350['Fecha_Hora']
COD_df_350 = COD_df_350.drop(['Fecha_Hora'], axis=1)


                   ## -- Selección del pixel de la JV

COD_df_348 = pd.DataFrame()
COD_df_348['Fecha_Hora'] = fechas_horas_COD[6:]
COD_df_348['COD'] = COD_pixel_348
COD_df_348['Fecha_Hora'] = pd.to_datetime(COD_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_348.index = COD_df_348['Fecha_Hora']
COD_df_348 = COD_df_348.drop(['Fecha_Hora'], axis=1)

#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
Rad_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix350_Anio.npy')
Rad_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix348_Anio.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')

df_fh  = pd.DataFrame()
df_fh ['fecha_hora'] = fechas_horas
df_fh['fecha_hora'] = pd.to_datetime(df_fh['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_fh.index = df_fh['fecha_hora']
w = pd.date_range(df_fh.index.min(), df_fh.index.max()).difference(df_fh.index)
df_fh = df_fh[df_fh.index.hour != 5]
fechas_horas = df_fh['fecha_hora'].values


                   ## -- Selección del pixel de la TS
Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)

                   ## -- Selección del pixel de la CI

Rad_df_350 = pd.DataFrame()
Rad_df_350['Fecha_Hora'] = fechas_horas
Rad_df_350['Radiacias'] = Rad_pixel_350
Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_350.index = Rad_df_350['Fecha_Hora']
Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)


                   ## -- Selección del pixel de la JV

Rad_df_348 = pd.DataFrame()
Rad_df_348['Fecha_Hora'] = fechas_horas
Rad_df_348['Radiacias'] = Rad_pixel_348
Rad_df_348['Fecha_Hora'] = pd.to_datetime(Rad_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_348.index = Rad_df_348['Fecha_Hora']
Rad_df_348 = Rad_df_348.drop(['Fecha_Hora'], axis=1)

## ----------------ACOTANDO LOS DATOS A FECHAS DESEADAS---------------- ##
Rad_df_348 = Rad_df_348.loc[(Rad_df_348.index >= fi) & (Rad_df_348.index <=ff) ]
Rad_df_350 = Rad_df_350.loc[(Rad_df_350.index >= fi) & (Rad_df_350.index <=ff) ]
Rad_df_975 = Rad_df_975.loc[(Rad_df_975.index >= fi) & (Rad_df_975.index <=ff) ]

################################################################################
## --------------CONCATENANDO LOS DOS DATAFRAMES PARA RELACIONAR--------------##
################################################################################

df_comple_CODRef_348 = pd.concat([Rad_df_348,  COD_df_348], axis=1)
df_comple_CODRef_348 = df_comple_CODRef_348.between_time('06:00', '17:59')

df_comple_CODRef_350 = pd.concat([Rad_df_350,  COD_df_350], axis=1)
df_comple_CODRef_350 = df_comple_CODRef_350.between_time('06:00', '17:59')

df_comple_CODRef_975 = pd.concat([Rad_df_975,  COD_df_975], axis=1)
df_comple_CODRef_975 = df_comple_CODRef_975.between_time('06:00', '17:59')

################################################################################
## -------------------------RELACIONEN CADA PUNTO-----------------------------##
################################################################################

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_comple_CODRef_350.COD.values, df_comple_CODRef_350.Radiacias.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax1.set_ylabel(u"Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relacion en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.set_ylim(0, 100)
ax1.set_xlim(0, 160)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)


ax2 = fig.add_subplot(3, 1, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(df_comple_CODRef_975.COD.values, df_comple_CODRef_975.Radiacias.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax2.set_ylabel(u"Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Relacion en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.set_ylim(0, 100)
ax2.set_xlim(0, 160)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)

ax3 = fig.add_subplot(3, 1, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(df_comple_CODRef_348.COD.values, df_comple_CODRef_348.Radiacias.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax3.set_ylabel(u"Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Relacion en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.set_ylim(0, 100)
ax3.set_xlim(0, 160)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)


plt.subplots_adjust( wspace=0.4, hspace=0.45)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_Reflectancia_vs_COD.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_Reflectancia_vs_COD.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


# Rad_bina_1 = Rad_bina[0:int(len(Rad_bina)/3), :, :]
# Rad_bina_2 = Rad_bina[int(len(Rad_bina)/3):int(len(Rad_bina)/3)+int(len(Rad_bina)/3), :, :]
# Rad_bina_3 = Rad_bina[int(len(Rad_bina)/3)+int(len(Rad_bina)/3):, :, :]
#
# fechas_horas_new_1 = fechas_horas_new[0:int(len(fechas_horas_new)/3)]
# fechas_horas_new_2 = fechas_horas_new[int(len(fechas_horas_new)/3):int(len(fechas_horas_new)/3)+int(len(fechas_horas_new)/3)]
# fechas_horas_new_3 = fechas_horas_new[int(len(fechas_horas_new)/3)+int(len(fechas_horas_new)/3):]
#
#
# Rad_bina_names_1, num_1 = measurements.label(Rad_bina_1)
# Area_1 = []
# for i in range(len(fechas_horas_new_1)):
#     Area_1.append(measurements.sum(Rad_bina_1[i], Rad_bina_names_1[i], index=arange(Rad_bina_names_1[i].max() + 1)) )
#     print(i)
# Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
# Area_1 = np.array(Area_1)
# np.save(Path_save+'Array_AREA1Rad_bina_05-2019-12-2019', Area_1)

# Rad_bina_names_2, num_2 = measurements.label(Rad_bina_2)
# Area_2 = []
# for i in range(len(fechas_horas_new_2)):
#     Area_2.append(measurements.sum(Rad_bina_2[i], Rad_bina_names_2[i], index=arange(Rad_bina_names_2[i].max() + 1)) )
#     print(i)
# Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
# Area_2 = np.array(Area_2)
# np.save(Path_save+'Array_AREA2Rad_bina_05-2019-12-2019', Area_2)

# Rad_bina_names_3, num_3 = measurements.label(Rad_bina_3)
# Area_3 = []
# for i in range(len(fechas_horas_new_3)):
#     Area_3.append(measurements.sum(Rad_bina_3[i], Rad_bina_names_3[i], index=arange(Rad_bina_names_3[i].max() + 1)) )
#     print(i)
# Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
# Area_3 = np.array(Area_3)
# np.save(Path_save+'Array_AREA3Rad_bina_05-2019-12-2019', Area_3)
