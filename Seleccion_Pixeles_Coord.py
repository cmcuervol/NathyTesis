#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA
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

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

'Se seleccionan los pixeles con el insumo de las coordenadas para un determinado periodo de tiempo, son guardadas como un np.array'

############################################################################################
## ----------------ACOTANDO LAS FECHAS POR DIA Y MES PARA TOMAR LOS DATOS---------------- ##
############################################################################################

fi_m = 1
fi_d = 1
ff_m = 12
ff_d = 20
Anio_datosGOES = 2019
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
Horizonte = 'Anio'    ##-->'Anio' para los datos del 2018 y 'EXP' para los datos a partir del experimento.

################################################################################################
##-------------------SELECCION DE LOS DATOS DE LAS COORDENADAS HORARIAS-----------------------##
################################################################################################
coord_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Anio_DFHourlyCoords_TS.csv',  sep=',')
coord_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Anio_DFHourlyCoords_CI.csv',  sep=',')
coord_JV = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Anio_DFHourlyCoords_JV.csv',  sep=',')
coord_JV['Longitudes'][coord_JV.index==0] = -75.510475   ##un pequeño "ajustillo"

coord_TS['Unnamed: 0'] = pd.to_datetime(coord_TS['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
coord_TS.index = coord_TS['Unnamed: 0']
coord_CI['Unnamed: 0'] = pd.to_datetime(coord_CI['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
coord_CI.index = coord_CI['Unnamed: 0']
coord_JV['Unnamed: 0'] = pd.to_datetime(coord_JV['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
coord_JV.index = coord_JV['Unnamed: 0']

if Horizonte == 'Anio':
    Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
    fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2__2018_2019.npy')
    lat = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
    lon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')

    ##-------------------------------------DUPLICANDO PARA Q SEAN DOS AÑOS-----------------------------##
    coord_TS_2 = coord_TS.copy()
    coord_TS_2.index = [coord_TS_2.index[i].replace(year=2019) for i in range(len(coord_TS_2.index))]
    df_result_TS = pd.concat([coord_TS, coord_TS_2])
    del coord_TS_2, coord_TS
    coord_TS = df_result_TS

    coord_CI_2 = coord_CI.copy()
    coord_CI_2.index = [coord_CI_2.index[i].replace(year=2019) for i in range(len(coord_CI_2.index))]
    df_result_CI = pd.concat([coord_CI, coord_CI_2])
    del coord_CI_2, coord_CI
    coord_CI = df_result_CI

    coord_JV_2 = coord_JV.copy()
    coord_JV_2.index = [coord_JV_2.index[i].replace(year=2019) for i in range(len(coord_JV_2.index))]
    df_result_JV = pd.concat([coord_JV, coord_JV_2])
    del coord_JV_2, coord_JV
    coord_JV = df_result_JV

    coord_TS = coord_TS[(coord_TS.index.date >= pd.to_datetime('2018-'+str(fi_m)+ '-'+str(fi_d)).date()) & (coord_TS.index.date  <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]
    coord_CI = coord_CI[(coord_CI.index.date >= pd.to_datetime('2018-'+str(fi_m)+ '-'+str(fi_d)).date()) & (coord_CI.index.date  <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]
    coord_JV = coord_JV[(coord_JV.index.date >= pd.to_datetime('2018-'+str(fi_m)+ '-'+str(fi_d)).date()) & (coord_JV.index.date  <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]



elif Horizonte == 'EXP':
    Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2019CH2.npy')
    fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CH2_2019.npy')
    lat = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2019.npy')
    lon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2019.npy')

    coord_TS.index = [coord_TS.index[i].replace(year=2019) for i in range(len(coord_TS.index))]
    coord_TS = coord_TS[(coord_TS.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d)).date()) & (coord_TS.index.date  <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

    coord_CI.index = [coord_CI.index[i].replace(year=2019) for i in range(len(coord_CI.index))]
    coord_CI = coord_CI[(coord_CI.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d)).date()) & (coord_CI.index.date  <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

    coord_JV.index = [coord_JV.index[i].replace(year=2019) for i in range(len(coord_JV.index))]
    coord_JV = coord_JV[(coord_JV.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d)).date()) & (coord_JV.index.date  <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

coord_TS.loc[coord_TS['Latitudes'] > round(float(lat[:, 0].max()), 2), 'Latitudes'] = round(float(lat[:, 0].max()), 2)
coord_TS.loc[coord_TS['Longitudes'] > round(float(lon[:, 0].max()), 2), 'Longitudes'] = round(float(lon[:, 0].max()), 2)
coord_TS.loc[coord_TS['Latitudes'] < round(float(lat[:, 0].min()), 2), 'Latitudes'] = round(float(lat[:, 0].min()), 2)
coord_TS.loc[coord_TS['Longitudes'] < round(float(lon[:, 0].min()), 2), 'Longitudes'] = round(float(lon[:, 0].min()), 2)

coord_JV.loc[coord_JV['Latitudes'] > round(float(lat[:, 0].max()), 2), 'Latitudes'] = round(float(lat[:, 0].max()), 2)
coord_JV.loc[coord_JV['Longitudes'] > round(float(lon[:, 0].max()), 2), 'Longitudes'] = round(float(lon[:, 0].max()), 2)
coord_JV.loc[coord_JV['Latitudes'] < round(float(lat[:, 0].min()), 2), 'Latitudes'] = round(float(lat[:, 0].min()), 2)
coord_JV.loc[coord_JV['Longitudes'] < round(float(lon[:, 0].min()), 2), 'Longitudes'] = round(float(lon[:, 0].min()), 2)

coord_CI.loc[coord_CI['Latitudes'] > round(float(lat[:, 0].max()), 2), 'Latitudes'] = round(float(lat[:, 0].max()), 2)
coord_CI.loc[coord_CI['Longitudes'] > round(float(lon[:, 0].max()), 2), 'Longitudes'] = round(float(lon[:, 0].max()), 2)
coord_CI.loc[coord_CI['Latitudes'] < round(float(lat[:, 0].min()), 2), 'Latitudes'] = round(float(lat[:, 0].min()), 2)
coord_CI.loc[coord_CI['Longitudes'] < round(float(lon[:, 0].min()), 2), 'Longitudes'] = round(float(lon[:, 0].min()), 2)


                   ## -- Selección del pixel de la TS
lat_index_975 = []
lon_index_975 = []

for i in range(len(coord_TS.Latitudes.values)):
    print(i)
    print(round(float(coord_TS.Latitudes.values[i]),6))
    print(round(float(coord_TS.Longitudes.values[i]),6))
    if coord_TS.Latitudes.values[i] >= 0:
        lat_index_975.append(np.where((lat[:, 0] >= (round(float(coord_TS.Latitudes.values[i]),6))-0.01) & (lat[:, 0] <= (round(float(coord_TS.Latitudes.values[i]),6)+0.01)))[0][0])
        lon_index_975.append(np.where((lon[0, :] >= (round(float(coord_TS.Longitudes.values[i]),6))-0.001) & (lon[0, :] <= (round(float(coord_TS.Longitudes.values[i]+0.01),6))))[0][0])
    else:
        lat_index_975.append(np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0])
        lon_index_975.append(np.where((lon[0, :] < -75.58) & (lon[0, :] > -75.59))[0][0])
    print('apendeo')

Rad_pixel_975 = []
fechas_horas_new =[]
for j in range(len(fechas_horas )):
    for i in range(len(lon_index_975)):
        if (pd.to_datetime(fechas_horas[j]).date() ==  coord_TS.index[i].date()) and (pd.to_datetime(fechas_horas[j]).hour ==  coord_TS.index[i].hour):
            Rad_pixel_975.append(Rad[j, lat_index_975[i], lon_index_975[i]])
            fechas_horas_new.append(fechas_horas[j])
            print('appendedo en Rad')
        else:
            pass
print('goleo TS')

                   ## -- Selección del pixel de CI
lat_index_350 = []
lon_index_350 = []

for i in range(len(coord_CI.Latitudes.values)):
    print(i)
    print(round(float(coord_CI.Latitudes.values[i]),6))
    print(round(float(coord_CI.Longitudes.values[i]),6))
    if coord_CI.Latitudes.values[i] >= 0:
        lat_index_350.append(np.where((lat[:, 0] >= (round(float(coord_CI.Latitudes.values[i]),6))-0.01) & (lat[:, 0] <= (round(float(coord_CI.Latitudes.values[i]),6)+0.01)))[0][0])
        lon_index_350.append(np.where((lon[0, :] >= (round(float(coord_CI.Longitudes.values[i]),6))-0.001) & (lon[0, :] <= (round(float(coord_CI.Longitudes.values[i]+0.01),6))))[0][0])
    else:
        lat_index_350.append(np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0])
        lon_index_350.append(np.where((lon[0, :] < -75.58) & (lon[0, :] > -75.59))[0][0])
    print('apendeo')

Rad_pixel_350 = []
for j in range(len(fechas_horas )):
    for i in range(len(lon_index_350)):
        if (pd.to_datetime(fechas_horas[j]).date() ==  coord_CI.index[i].date()) and (pd.to_datetime(fechas_horas[j]).hour ==  coord_CI.index[i].hour):
            Rad_pixel_350.append(Rad[j, lat_index_350[i], lon_index_350[i]])
            print('appendedo en Rad')
        else:
            pass
print('goleo CI')
                   ## -- Selección del pixel de la JV
lat_index_348 = []
lon_index_348 = []

for i in range(len(coord_JV.Latitudes.values)):
    print(i)
    print(round(float(coord_JV.Latitudes.values[i]),6))
    print(round(float(coord_JV.Longitudes.values[i]),6))
    if coord_JV.Latitudes.values[i] >= 0:
        lat_index_348.append(np.where((lat[:, 0] >= (round(float(coord_JV.Latitudes.values[i]),6))-0.01) & (lat[:, 0] <= (round(float(coord_JV.Latitudes.values[i]),6)+0.01)))[0][0])
        lon_index_348.append(np.where((lon[0, :] >= (round(float(coord_JV.Longitudes.values[i]),6))-0.001) & (lon[0, :] <= (round(float(coord_JV.Longitudes.values[i]+0.01),6))))[0][0])
    else:
        lat_index_348.append(np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0])
        lon_index_348.append(np.where((lon[0, :] < -75.58) & (lon[0, :] > -75.59))[0][0])
    print('apendeo')


lon_index_348 = lon_index_348[1:]   ##-->otro pequeño ajustillo
Rad_pixel_348 = []
for j in range(len(fechas_horas )):
    for i in range(len(lon_index_348)):
        if (pd.to_datetime(fechas_horas[j]).date() ==  coord_JV.index[i].date()) and (pd.to_datetime(fechas_horas[j]).hour ==  coord_JV.index[i].hour):
            Rad_pixel_348.append(Rad[j, lat_index_348[i], lon_index_348[i]])
            print('appendedo en Rad')
        else:
            pass
print('goleo JV')


Rad_pixel_348 = np.array(Rad_pixel_348)
Rad_pixel_350 = np.array(Rad_pixel_350)
Rad_pixel_975 = np.array(Rad_pixel_975)
fechas_horas_new = np.array(fechas_horas_new)

np.save(Path_save[0:45]+'Array_Rad_pix975_'+Horizonte, Rad_pixel_975)
np.save(Path_save[0:45]+'Array_Rad_pix350_'+Horizonte, Rad_pixel_350)
np.save(Path_save[0:45]+'Array_Rad_pix348_'+Horizonte, Rad_pixel_348)
np.save(Path_save[0:45]+'Array_FechasHoras_'+Horizonte, fechas_horas_new)

print('Hemos terminado con exito')
