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
import netCDF4 as nc
from netCDF4 import Dataset
id
import itertools
import datetime
from scipy.stats import ks_2samp
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid
import matplotlib.cm as cm
import os
import statistics
'Programa para obtener los promedio y la varianza de cada mes de las nubes y dibujarlos. NO ES UN PROGRAMA LIVIANO, debido al set de datos.'

Horizonte = 'Anio'    ##-->Para que tome datos desde el 2018 de GOES se pone 'Anio', para que tome solo lo del experimento se pone 'Exp'

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

df_UmbralH_Nube = pd.concat([df_UmbralH_Nube_348, df_UmbralH_Nube_350, df_UmbralH_Nube_975], axis=1)
df_UmbralH_Nube = df_UmbralH_Nube.mean(axis = 1, skipna = True)
df_UmbralH_Nube = pd.DataFrame(df_UmbralH_Nube, columns=['Umbral'])

##---------------------------------------------------------------------------------------------------------##
#############################################################################################################
## ------------------LECTURA DE LOS DATOS DE GOES CH2 DURANTE EL REGISTRO DEL EXPERIMENTO------------------##
#############################################################################################################
##---------------------------------------------------------------------------------------------------------##

if Horizonte == 'Anio' :
    #ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C22018.nc')
    Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad2018CH2.npy')
    fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_2018CH2.npy')
    lat = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_2018CH2.npy')
    lon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_2018CH2.npy')

elif Horizonte == 'Exp' :
    Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_RadCH2_2019_0320_0822.npy')
    fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_2019_0320_0822_CH2.npy')
    lat = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_2019_0320_0822_CH2.npy')
    lon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_2019_0320_0822_CH2.npy')
# ################################################################################
# ## ----------------------LECTURA DE DATOS DE GOES CH02----------------------- ##
# ################################################################################
#
# ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C22018.nc')
# lat = ds.variables['lat'][:, :]
# lon = ds.variables['lon'][:, :]
# Rad = ds.variables['Radiancias'][:, :, :]
# tiempo = ds.variables['time']
# fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
# for i in range(len(fechas_horas)):
#     fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')
# fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')
#
#
# ################################################################################################
# ##-------------------INCORPORANDO EL ARRAY DEL ZENITH PARA CADA HORA--------------------------##
# ################################################################################################
#
# def Aclarado_visible(Path_Zenith, Path_Fechas, Rad, fechas_horas):
#     Z = np.load(Path_Zenith)
#     Fechas_Z = np.load(Path_Fechas)
#
#     daily_hours = np.arange(5, 19, 1)
#     Zenith = []
#     Fechas_Zenith = []
#     for i in range(len(Fechas_Z)):
#         if Fechas_Z[i].hour in daily_hours:
#             Zenith.append(Z[i, :, :])
#             Fechas_Zenith.append(Fechas_Z[i])
#         elif Fechas_Z[i].hour not in daily_hours:
#             pass
#     Zenith = np.array(Zenith)
#
#     Rad_clear = []
#     for i in range(len(Fechas_Zenith)):
#         for j in range(len(fechas_horas)):
#             if Fechas_Zenith[i].hour ==  fechas_horas[j].hour and Fechas_Zenith[i].day ==  fechas_horas[j].day:
#                 Rad_clear.append(Rad[j, :, :]/np.cos(Zenith[i, :, :]))
#             else:
#                 pass
#     Rad_clear = np.array(Rad_clear)
#     return Rad
#
# Rad_Z = Aclarado_visible('/home/nacorreasa/Maestria/Datos_Tesis/hourlyZenith2018.npy', '/home/nacorreasa/Maestria/Datos_Tesis/DatesZenith.npy', Rad, fechas_horas)
# del Rad
#
# Rad = Rad_Z

la = lat.shape[0]
lo = lat.shape[1]

Rad = Rad[1:-3, :, :]
fechas_horas = fechas_horas[1:-3]
##------------------------------------------------------------------------------------##
Rad_bina = []
Rad_mask = []

fechas_horas_new = []
for i in range (len(fechas_horas)):
    try:
        rad = Rad[i, :, :]
        umbral = df_UmbralH_Nube[df_UmbralH_Nube.Umbral.index == fechas_horas[i].hour].values[0][0]
        radm = np.ma.masked_where(rad < umbral, rad)
        radbi = (rad > umbral).astype(int)
        Rad_bina.append(radbi)
        Rad_mask.append(radm)
        fechas_horas_new.append(fechas_horas[i])
    except IndexError:
        pass
###################################################################################################################################################
##------------------------------------------------------SECCION 1 - REFLECTANCIA PROMEDIO--------------------------------------------------------##
###################################################################################################################################################
##------------------------------------------------------------------------------------------------------------------------------------------------##
s = np.arange(1, 13, 1)
Ene=[]
Feb=[]
Mar=[]
Abr=[]
May=[]
Jun=[]
Jul=[]
Ago=[]
Sep=[]
Oct=[]
Nov=[]
Dic=[]

Med=[Ene,Feb,Mar,Abr,May,Jun,Jul,Ago,Sep,Oct,Nov,Dic]
#Se creó la matriz de  la media mensual:
for i in range(0,12,1):
    Med[i]=np.zeros((la,lo))
    Med[i]=Med[i].reshape(la,lo)
    for j in range(0,lo,1):
        for k in range(0,la,1):
            temporal = pd.DataFrame(Rad[:,k, j], index = fechas_horas, columns=['FR'] )
            temporal_month = temporal[temporal.index.month== s[i]]
            Med[i][k][j]= temporal_month['FR'].mean()

##-------------------------------------------------------------------------------------------------------------------##

shape = '/home/nacorreasa/Maestria/Semestre1/Analisis_Geoespacial/MuchosShapes/AMVA/AreaMetropolitana'
Path_Save = '/home/nacorreasa/Escritorio/Figuras/'
Lat = lat[:, 0]
Lon = lon[0,:]
levels = np.linspace(0, 100, 20)

times = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Agos', 'Sep', 'Oct', 'Nov','Dic']

def MapasCD_Imshow(data, lat, lon, lat_down, lat_up, lon_left, long_right,  name, titulo, cmap,  dt, dmes, levels='Nada'):
    plt.close('all')
    fig = plt.figure(figsize=(14,18))

    for i in range(0, 12):
        ax = fig.add_subplot(4, 3, i+1)
        ax.set_title(dmes[i], fontsize=18)
        m = Basemap(projection='merc', llcrnrlat=lat_down, urcrnrlat=lat_up,
                    llcrnrlon=lon_left, urcrnrlon=long_right, resolution='i', lat_ts=20)
        m.readshapefile(shape, name='AreaMetropolitana', color='k', linewidth=1.5)
        cs = m.imshow(data[i], cmap =cmap, alpha = 0.5)
        parallels = np.arange(lat_down, lat_up+1, 0.3)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
        meridians = np.arange(lon_left, long_right+1, 0.3)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)

    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.01)

    cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
    cbar.set_label(titulo, fontproperties = prop, fontsize=20)

    plt.savefig(Path_Save+name+'.png', format='png')
    os.system('scp '+ Path_Save+name+'.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

MapasCD_Imshow(Med, Lat, Lon, min(Lat), max(Lat), min(Lon), max(Lon), 'Promedio_CH2_2018'+Horizonte, u'Factor Reflectancia',  'gist_rainbow', times, meses, levels = levels)

##########################################################################################################################################
##--------------------------------SECCION 2 -  PROMEDIO DE LOS DATOS ENMASCARADOS POR EL UMBRAL-----------------------------------------##
##########################################################################################################################################

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
        umbral = df_UmbralH_Nube[df_UmbralH_Nube.Umbral.index == fechas_horas[i].hour].values[0][0]
        radm = np.ma.masked_where(rad < umbral, rad)
        radbi = (rad > umbral).astype(int)
        Rad_bina.append(radbi)
        Rad_mask.append(radm)
        fechas_horas_new.append(fechas_horas[i])
    except IndexError:
        pass

Rad_bina = np.array(Rad_bina)
Rad_mask = np.array(Rad_mask)

# Umbral_up  = 49.00030
# Radm = np.ma.masked_where(Rad < Umbral_up, Rad)
Radm = Rad_mask
##-------------------------------------------------------------------------------------------------------------------##
Ene=[]
Feb=[]
Mar=[]
Abr=[]
May=[]
Jun=[]
Jul=[]
Ago=[]
Sep=[]
Oct=[]
Nov=[]
Dic=[]

Med=[Ene,Feb,Mar,Abr,May,Jun,Jul,Ago,Sep,Oct,Nov,Dic]
#Se creó la matriz de  la media mensual:
for i in range(0,12,1):
    Med[i]=np.zeros((la,lo))
    Med[i]=Med[i].reshape(la,lo)
    for j in range(0,lo,1):
        for k in range(0,la,1):
            temporal = pd.DataFrame(Radm[:,k, j], index = fechas_horas_new, columns=['FR'] )
            temporal_month = temporal[temporal.index.month== s[i]]
            Med[i][k][j]= temporal_month['FR'].mean()

##-------------------------------------------------------------------------------------------------------------------##

shape = '/home/nacorreasa/Maestria/Semestre1/Analisis_Geoespacial/MuchosShapes/AMVA/AreaMetropolitana'
Path_Save = '/home/nacorreasa/Escritorio/Figuras/'
Lat = lat[:, 0]
Lon = lon[0,:]
levels = np.linspace(0, 100, 20)

times = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Agos', 'Sep', 'Oct', 'Nov','Dic']

def MapasCD_Imshow(data, lat, lon, lat_down, lat_up, lon_left, long_right,  name, titulo, cmap,  dt, dmes, levels='Nada'):
    plt.close('all')
    fig = plt.figure(figsize=(14,18))

    for i in range(0, 12):
        ax = fig.add_subplot(4, 3, i+1)
        ax.set_title(dmes[i], fontsize=18)
        m = Basemap(projection='merc', llcrnrlat=lat_down, urcrnrlat=lat_up,
                    llcrnrlon=lon_left, urcrnrlon=long_right, resolution='i', lat_ts=20)
        m.readshapefile(shape, name='AreaMetropolitana', color='k', linewidth=1.5)
        cs = m.imshow(data[i], cmap =cmap, alpha = 0.5)
        parallels = np.arange(lat_down, lat_up+1, 0.3)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
        meridians = np.arange(lon_left, long_right+1, 0.3)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)

    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.01)

    cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
    cbar.set_label(titulo, fontproperties = prop, fontsize=20)

    plt.savefig(Path_Save+name+'.png', format='png')
    os.system('scp '+ Path_Save+name+'.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

MapasCD_Imshow(Med, Lat, Lon, min(Lat), max(Lat), min(Lon), max(Lon), 'PromedioMascara_CH2_2018'+Horizonte, u'Reflectancia nubes [%]',  'Greys', times, meses, levels = levels)

##########################################################################################################################################
##---------------------------------------------------------SECCION 3 - ENSAYOS----------------------------------------------------------##
##########################################################################################################################################

plt.imshow(Med[0])
plt.title('Med Enero')
plt.savefig(Path_Save+'Enero.png', format='png')
plt.close('all')
os.system('scp '+ Path_Save+'Enero.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


plt.imshow(Med[6])
plt.title('Med Julio')
plt.savefig(Path_Save+'Julio.png', format='png')
plt.close('all')
os.system('scp '+ Path_Save+'Julio.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


plt.imshow(Rad[45,:,:])
plt.title('Rad 45')
plt.savefig(Path_Save+'Rad45.png', format='png')
plt.close('all')
os.system('scp '+ Path_Save+'Rad45.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


##########################################################################################################################################
##---------------------------------SECCION 4-  VARIANZA DE LOS DATOS ENMASCARADOS POR EL UM--------------------------------------------##
##########################################################################################################################################

"Se hace con las sobre los datos normalizados para poder obtener el [%] de varianza"

##-------------------------------------------------------------------------------------------------------------------##
Ene=[]
Feb=[]
Mar=[]
Abr=[]
May=[]
Jun=[]
Jul=[]
Ago=[]
Sep=[]
Oct=[]
Nov=[]
Dic=[]

Var=[Ene,Feb,Mar,Abr,May,Jun,Jul,Ago,Sep,Oct,Nov,Dic]
#Se creó la matriz de  la varianza mensual:
for i in range(0,12,1):
    Var[i]=np.zeros((la,lo))
    Var[i]=Var[i].reshape(la,lo)
    for j in range(0,lo,1):
        for k in range(0,la,1):
            temporal = pd.DataFrame(Radm[:,k, j], index = fechas_horas_new, columns=['FR'] )
            temporal_month = temporal[temporal.index.month== s[i]]
            temporal_norm = (temporal_month['FR'] - temporal_month['FR'].mean()) / (temporal_month['FR'].max() - temporal_month['FR'].min())
            Var[i][k][j]= temporal_norm.var()

##-------------------------------------------------------------------------------------------------------------------##

shape = '/home/nacorreasa/Maestria/Semestre1/Analisis_Geoespacial/MuchosShapes/AMVA/AreaMetropolitana'
Path_Save = '/home/nacorreasa/Escritorio/Figuras/'
Lat = lat[:, 0]
Lon = lon[0,:]
levels = np.linspace(0, 100, 20)

times = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Agos', 'Sep', 'Oct', 'Nov','Dic']

def MapasCD_Imshow(data, lat, lon, lat_down, lat_up, lon_left, long_right,  name, titulo, cmap,  dt, dmes, levels='Nada'):
    plt.close('all')
    fig = plt.figure(figsize=(14,18))

    for i in range(0, 12):
        ax = fig.add_subplot(4, 3, i+1)
        ax.set_title(dmes[i], fontsize=18)
        m = Basemap(projection='merc', llcrnrlat=lat_down, urcrnrlat=lat_up,
                    llcrnrlon=lon_left, urcrnrlon=long_right, resolution='i', lat_ts=20)
        m.readshapefile(shape, name='AreaMetropolitana', color='k', linewidth=1.5)
        cs = m.imshow(data[i], cmap =cmap, alpha = 0.5)
        parallels = np.arange(lat_down, lat_up+1, 0.3)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
        meridians = np.arange(lon_left, long_right+1, 0.3)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)

    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.01)

    cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
    cbar.set_label(titulo,fontproperties = prop, fontsize=20)

    plt.savefig(Path_Save+name+'.png', format='png')
    os.system('scp '+ Path_Save+name+'.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

MapasCD_Imshow(Var, Lat, Lon, min(Lat), max(Lat), min(Lon), max(Lon), 'VarianzaMascara_CH2_2018'+Horizonte, u'Varianza normalizada [%]',  'Greys', times, meses, levels = levels)
