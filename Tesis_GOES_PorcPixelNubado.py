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
# import netCDF4 as nc
# from netCDF4 import Dataset
# id
import itertools
import datetime
from scipy.stats import ks_2samp
import matplotlib.colors as colors
import os
#from pyPdf import PdfFileWriter, PdfFileReader

Pixeles = 'Originales'  ##---> 'Originales para qtome una malla con los pixeles ubicados donde deben
                         ##      ser originalmente o 'Seleccionados' q tome el array de la máscara.

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa para concocer el porcentaje de pixeles que superó el umbral de nubes a
cada hora de cada mes y por mes, tomando como referencia la cantidad de pixeles del
Valle de Aburrá. Como es sobre todo el registro, es un programa pesado.
"""

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

####################################################################################
## ---------------LECTURA DE LOS DATOS DE GOES CH2 Y DEMÁS INSUMOS--------------- ##
####################################################################################

if Pixeles == 'Seleccionados':
    ## -------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL ENMASCARADA -------##
    Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_Malla_MaskedClean.npy')
    fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Malla_MaskedClean.npy')
    fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')

    Rad = Rad [:,::-1, :]

    ##--LECTURA DE LOS DATOS DE IRRADIANCIA EN CONDICIONES DE CIELO DESPEJADO --##
    Irra = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Irradiance_Interpolate.npy')
    Total_Pix = np.count_nonzero(~np.isnan(Irra[12]))

elif Pixeles == 'Originales':
    ## ------------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL-------------- ##
    Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
    fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2__2018_2019.npy')
    fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')

    ## -----------------LECTURA DE LOS UMBRALES DE LAS REFLECTANCIAS----------- ##
    df_UmbralH_Nube_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Nuba.csv',  sep=',', index_col =0,  header = None)
    df_UmbralH_Nube_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Nuba.csv',  sep=',', index_col =0,  header = None)
    df_UmbralH_Nube_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Nuba.csv',  sep=',', index_col =0,  header = None)

    df_UmbralH_Nube = pd.concat([df_UmbralH_Nube_348, df_UmbralH_Nube_350, df_UmbralH_Nube_975], axis=1)
    df_UmbralH_Nube = df_UmbralH_Nube.mean(axis = 1, skipna = True)
    df_UmbralH_Nube = pd.DataFrame(df_UmbralH_Nube, columns=['Umbral'])

    ## ---------------------ENMASCARAMIENTO DE LAS IMAGENES-------------------##
    Rad_bina = []
    Rad_mask = []
    fechas_horas_new = []
    for i in range (len(fechas_horas)):
        for j in range(len(df_UmbralH_Nube.Umbral.index)):
            if df_UmbralH_Nube.Umbral.index[j] == fechas_horas[i].hour:
                umbral = df_UmbralH_Nube.Umbral[j+6]
                rad = Rad[i, :, :]
                radbi = (rad > umbral).astype(int)
                rad[rad<umbral]=np.nan
                Rad_bina.append(radbi)
                Rad_mask.append(rad)
                fechas_horas_new.append(fechas_horas[i])
                print('yes')
            else:
                pass

    Rad_bina = np.array(Rad_bina)
    Rad_mask = np.array(Rad_mask)

    del Rad
    Rad = Rad_mask

    Total_Pix = Rad.shape[1]*Rad.shape[2]

la = Rad .shape[1]
lo = Rad .shape[2]

#########################################################################
## ----------------PORCENTAJE DE PIXELES PARA CADA MES-----------------##
#########################################################################
"""
Con los calculos de esta sección se determina el porcentaje de pixeles nublados
durante un mes, con respecto al total de pixeles del mes.
"""
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

Porc=[Ene,Feb,Mar,Abr,May,Jun,Jul,Ago,Sep,Oct,Nov,Dic]
#Se creó la matriz del porcentaje mensual:
for i in range(0,12,1):
    Porc[i]=np.zeros((la,lo))
    Porc[i]=Porc[i].reshape(la,lo)
    for j in range(0,lo,1):
        for k in range(0,la,1):
            temporal = pd.DataFrame(Rad[:,k, j], index = fechas_horas_new, columns=['FR'] )
            temporal_month = temporal[temporal.index.month== s[i]]
            temporal_nuba = temporal_month[temporal_month['FR']>0]
            Porc[i][k][j] = (len(temporal_nuba)/ len(temporal_month))*100


Porc= np.array(Porc)
Porc[Porc==0] = np.nan

##------------------------------------------------GRAFICA------------------------------------------------##

shape = '/home/nacorreasa/Maestria/Semestre1/Analisis_Geoespacial/MuchosShapes/AMVA/AreaMetropolitana'
Path_Save = '/home/nacorreasa/Escritorio/Figuras/'
nombre_lat = 'Array_Lat_IrradianceInterpolate.npy'
nombre_lon = 'Array_Lon_IrradianceInterpolate.npy'
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
lat = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
lon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')
Lat = lat[:, 0]
Lon = lon[0,:]
levels = np.linspace(0, 100, 20)
lat_down = np.nanmin(Lat)
lat_up = np.nanmax(Lat)
lon_left = np.nanmin(Lon)
lon_right = np.nanmax(Lon)
times = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Agos', 'Sep', 'Oct', 'Nov','Dic']


def MapasCD_Imshow(data, lat, lon, lat_down, lat_up, lon_left, long_right,  name, titulo, cmap,  dt, dmes, levels='Nada'):
    plt.close('all')
    fig = plt.figure(figsize=(14,18))

    for i in range(0, 12):
        ax = fig.add_subplot(4, 3, i+1)
        ax.set_title(dmes[i], fontsize=18)
        m = Basemap(projection='merc', llcrnrlat=lat_down, urcrnrlat=lat_up,
                    llcrnrlon=lon_left, urcrnrlon=lon_right, resolution='i', lat_ts=20)
        m.readshapefile(shape, name='AreaMetropolitana', color='k', linewidth=1.5)
        cs = m.imshow(data[i], cmap =cmap)
        parallels = np.arange(lat_down, lat_up+1, 0.3)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
        meridians = np.arange(lon_left, long_right+1, 0.3)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)

    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.07)

    cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
    cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
    cbar.set_label(titulo,  fontproperties = prop, fontsize=20 )

    plt.savefig(Path_Save+name+'.png', format='png')
    os.system('scp '+ Path_Save+name+'.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

MapasCD_Imshow(Porc, Lat, Lon, min(Lat), max(Lat), min(Lon), max(Lon), 'PorcentajePixeles_CH2_mes', u'Porcentaje de pixeles nublados [%]',  'Greys', times, meses, levels = levels)

#########################################################################
## ----------------PORCENTAJE DE PIXELES PTotales-----------------##
#########################################################################
# Total_Pix_Complete = Rad.shape[0]*Rad.shape[1]*Rad.shape[2]
#
# Porc_Total=np.zeros((la,lo))
# Porc_Total=Porc_Total.reshape(la,lo)
# for j in range(0,lo,1):
#     for k in range(0,la,1):
#         temporal = pd.DataFrame(Rad[:,k, j], index = fechas_horas_new, columns=['FR'] )
#         temporal_nuba = temporal[temporal['FR']>0]
#         Porc_Total[k][j] = (len(temporal_nuba)/ len(temporal))*100
#
# def UnMapa_Imshow(data, lat, lon, lat_down, lat_up, lon_left, long_right,  name, titulo, cmap,  dt, dmes, levels='Nada'):
#     plt.close('all')
#     fig = plt.figure(figsize=(10,12))
#
#     ax = fig.add_subplot(111)
#     ax.set_title('Porcentaje de pixeles en todo el registro', fontsize=18)
#     m = Basemap(projection='merc', llcrnrlat=lat_down, urcrnrlat=lat_up,
#                 llcrnrlon=lon_left, urcrnrlon=lon_right, resolution='i', lat_ts=20)
#     m.readshapefile(shape, name='AreaMetropolitana', color='k', linewidth=1.5)
#     cs = m.imshow(data, cmap =cmap, alpha = 0.5)
#     parallels = np.arange(lat_down, lat_up+1, 0.3)
#     m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
#     meridians = np.arange(lon_left, long_right+1, 0.3)
#     m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
#
#     plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.07)
#
#     cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
#     cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
#     cbar.set_label(titulo,  fontproperties = prop, fontsize=20 )
#
#     plt.savefig(Path_Save+name+'.png', format='png')
#     os.system('scp '+ Path_Save+name+'.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
#
# UnMapa_Imshow(Porc_Total, Lat, Lon, min(Lat), max(Lat), min(Lon), max(Lon), 'PorcentajePixeles_CH2', u'Porcentaje de pixeles nublados [%]',  'Greys', times, meses, levels = levels)
#
#
# #########################################################################
# ## ----------------PORCENTAJE DE PIXELES ESTACIONAL-----------------##
# #########################################################################
# Horas = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
# Meses = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
#
# mes_index = []
# hora_index = []
# for i in range(len(Meses)):
#     for j in range(len(Horas)):
#         mes_index.append(Meses[i])
#         hora_index.append(Horas[j])
#
# Rad_PorcPix =[]
# for g in range(len(mes_index)):
#     for i in range(len(hora_index)):
#         Temporal_Porc = np.zeros((la,lo))
#         Temporal_Porc = Porc[i].reshape(la,lo)
#         for j in range(0,lo,1):
#             for k in range(0,la,1):
#                 temporal = pd.DataFrame(Rad[:,k, j], index = fechas_horas, columns=['FR'] )
#                 temporal_month = temporal[(temporal.index.month== mes_index[g]) & (temporal.index.hour == hora_index[i])]
#                 temporal_nuba = temporal_month[temporal_month['FR']>0]
#                 Temporal_Porc [k][j] = (len(temporal_nuba)/ Total_Pix)*100
#     Rad_PorcPix.append(Temporal_Porc)
# Rad_PorcPix = np.array(Rad_PorcPix)

##------------------------------------------------GRAFICA------------------------------------------------##

# Path_Save_pdf = '/home/nacorreasa/Escritorio/Figuras/'
# output = PdfFileWriter()
# for j in range(0,len(Meses)):
#
#     plt.close('all')
#     fig = plt.figure(figsize=(14,18))
#
#     for i in range(0, len(Horas)):
#         ax = fig.add_subplot(4, 3, i+1)
#         ax.set_title('Hora: '+str(Horas[i]), fontsize=18)
#         m = Basemap(projection='merc', llcrnrlat=lat_down, urcrnrlat=lat_up,
#                     llcrnrlon=lon_left, urcrnrlon=long_right, resolution='i', lat_ts=20)
#         m.readshapefile(shape, name='AreaMetropolitana', color='k', linewidth=1.5)
#         cs = m.imshow(Rad_PorcPix[i], cmap ='rainbow', alpha = 0.5)
#         parallels = np.arange(lat_down, lat_up+1, 0.3)
#         m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
#         meridians = np.arange(lon_left, long_right+1, 0.3)
#         m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
#
#     plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.07)
#
#     cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
#     cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
#     cbar.set_label('Porcentaje de pixeles nublados durante: ' + meses[i],  fontproperties = prop, fontsize=20 )
#
#
#
#     file_j = file(Path_Save_pdf + meses[i] '.pdf', 'rb')
#     page_j = PdfFileReader(file_j).getPage(0)
#     output.addPage(page_j)
#
#     os.system('rm ' + Path_Save_pdf + meses[i] '.pdf')
#
# output.write(file(Path_Save_pdf  + 'PorcentajePixeles_HoraMes.pdf', 'w'))
# os.system('scp '+ Path_Save_pdf +  'PorcentajePixeles_HoraMes.pdf  nacorreasa@192.168.1.74:/var/www/nacorreasa/Calidad_Meteo/Vaisala')
# os.system('rm '+ Path_Sal +  'PorcentajePixeles_HoraMes.pdf')
