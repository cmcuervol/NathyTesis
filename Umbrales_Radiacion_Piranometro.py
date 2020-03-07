#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
# from mpl_toolkits.axes_grid1 import host_subplot
# import mpl_toolkits.axisartist as AA
# import matplotlib
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

Theoric_Model = 'GIS'             ##-->> PARA QUE USE EL MODELO DE Gis DEBE SER 'GIS', DE OTRO MODO SERÍA 'Piranometro'
resolucion = 'diaria'             ##-->> LAS OPCIONES SON 'diaria' U 'horaria'
#-----------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

'Código desarrollado para encontrar el % de radiación en condiciones despejadas y nubladas'
'detectadas por el piranómetro, apartir de la información de las radiancias y de los umbrales'
'obtenidos en el código, Umbrales_Reflectancias.py'

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

###############################################################################
##----------------LECTURA Y AJUSTE DE LOS DATOS DE PIRANÓMETRO---------------##
###############################################################################
'Lectura de los datos de piranómetro en los tres puntos y ajuste de los valores de'
'medicion a rangos válidos.'
##------------------LECTURA DE LOS DATOS DEL EXPERIMENTO----------------------##
df_P975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel975.txt',  sep=',', index_col =0)
df_P350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel350.txt',  sep=',', index_col =0)
df_P348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel348.txt',  sep=',', index_col =0)

df_P975['Fecha_hora'] = df_P975.index
df_P350['Fecha_hora'] = df_P350.index
df_P348['Fecha_hora'] = df_P348.index

df_P975.index = pd.to_datetime(df_P975.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P350.index = pd.to_datetime(df_P350.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P348.index = pd.to_datetime(df_P348.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

## ----------------ACOTANDO LOS DATOS A VALORES VÁLIDOS---------------- ##

df_P975 = df_P975[(df_P975['NI'] > 0) & (df_P975['strength'] > 0)]
df_P350 = df_P350[(df_P350['NI'] > 0) & (df_P350['strength'] > 0)]
df_P348 = df_P348[(df_P348['NI'] > 0) & (df_P348['strength'] > 0)]

df_P975 = df_P975[df_P975['radiacion'] > 0]
df_P350 = df_P350[df_P350['radiacion'] > 0]
df_P348 = df_P348[df_P348['radiacion'] > 0]

df_P975_h = df_P975.groupby(pd.Grouper(freq="H")).mean()
df_P350_h = df_P350.groupby(pd.Grouper(freq="H")).mean()
df_P348_h = df_P348.groupby(pd.Grouper(freq="H")).mean()

df_P975_h = df_P975_h.between_time('06:00', '17:00')
df_P350_h = df_P350_h.between_time('06:00', '17:00')
df_P348_h = df_P348_h.between_time('06:00', '17:00')

##----AJUSTE DE LOS DATOS DE RADIACIÓN REAL AL RANGO DE FECHAS DESEADO-----##

def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada hora. Las fechas'
    'final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=60)
    while start_date <= end_date:
        yield start_date
        start_date += delta

fechas_975 = []
for i in daterange(df_P975.index[0].date().strftime("%Y-%m-%d"), (df_P975.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_975.append(i)

fechas_350 = []
for i in daterange(df_P350.index[0].date().strftime("%Y-%m-%d"), (df_P350.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_350.append(i)

fechas_348 = []
for i in daterange(df_P348.index[0].date().strftime("%Y-%m-%d"), (df_P348.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas_348.append(i)

fi_m = min(fechas_975[0].month, fechas_350[0].month, fechas_348[0].month)
fi_d = min(fechas_975[0].day, fechas_350[0].day, fechas_348[0].day)
ff_m = min(fechas_975[-1].month, fechas_350[-1].month, fechas_348[-1].month)
ff_d = min(fechas_975[-1].day, fechas_350[-1].day, fechas_348[-1].day)

##############################################################################
## ----------------LECTURA DE LOS DATOS DE RADIACION TEORICA--------------- ##
##############################################################################

if Theoric_Model == 'Piranometro':
    df_Theoric = pd.read_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_PIR.csv",  sep=',', index_col =0)
    df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

    df_Theoric = df_Theoric[(df_Theoric.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-'
                +str(fi_d)).date()) & (df_Theoric.index .date<= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

elif Theoric_Model == 'GIS':
    df_Theoric = pd.read_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_GIS.csv",  sep=',', index_col =0)
    df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

    df_Theoric = df_Theoric[(df_Theoric.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-'
                +str(fi_d)).date()) & (df_Theoric.index .date<= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]


df_Rad_P975 = pd.concat([df_Theoric, df_P975_h], axis = 1)
df_Rad_P350 = pd.concat([df_Theoric, df_P350_h], axis = 1)
df_Rad_P348 = pd.concat([df_Theoric, df_P348_h], axis = 1)

df_Rad_P975 =  df_Rad_P975.drop(['NI','strength'], axis=1)
df_Rad_P350 =  df_Rad_P350.drop(['NI','strength'], axis=1)
df_Rad_P348 =  df_Rad_P348.drop(['NI','strength'], axis=1)


###############################################################################
##---------ESTABLECIENDO EL PERCENTIL MINO DE DIA DESPEJADO O NUBLADO---------##
###############################################################################

'A manera de guia se proponen unos umbrales supuestos que ayudarána  refinar la informacion'
'que derive del resultado del análisis de los datos de CH2-GOES.'

##-------DISCRIMINACION ENTRE DIAS LLUVIOSOS Y SECOS POR PERCENTILES DE RADIACION--------##

'Se establecieron umbrales empiricamente para la seleccion de los dias marcadamente nubados y'
'marcadamente despejados dentro el periodo de registro, así: NUBADO = Sumas mayores o iguales'
'al 75% y DESPEJADO = Sumas menores o iguales al 25%.'

Sum_df_Rad_P975 = df_Rad_P975.groupby(pd.Grouper(freq='1D')).sum()
Sum_df_Rad_P350 = df_Rad_P350.groupby(pd.Grouper(freq='1D')).sum()
Sum_df_Rad_P348 = df_Rad_P348.groupby(pd.Grouper(freq='1D')).sum()

Sum_df_Rad_P975 = Sum_df_Rad_P975[Sum_df_Rad_P975['radiacion']>0]
Sum_df_Rad_P350 = Sum_df_Rad_P350[Sum_df_Rad_P350['radiacion']>0]
Sum_df_Rad_P348 = Sum_df_Rad_P348[Sum_df_Rad_P348['radiacion']>0]

Desp_Pira_975 = Sum_df_Rad_P975[Sum_df_Rad_P975.radiacion>=(Sum_df_Rad_P975.Rad_teo_975)*0.75]
Desp_Pira_350 = Sum_df_Rad_P350[Sum_df_Rad_P350.radiacion>=(Sum_df_Rad_P350.Rad_teo_350)*0.75]
Desp_Pira_348 = Sum_df_Rad_P348[Sum_df_Rad_P348.radiacion>=(Sum_df_Rad_P348.Rad_teo_348)*0.75]

Nuba_Pira_975 = Sum_df_Rad_P975[Sum_df_Rad_P975.radiacion<=(Sum_df_Rad_P975.Rad_teo_975)*0.25]
Nuba_Pira_350 = Sum_df_Rad_P350[Sum_df_Rad_P350.radiacion<=(Sum_df_Rad_P350.Rad_teo_350)*0.25]
Nuba_Pira_348 = Sum_df_Rad_P348[Sum_df_Rad_P348.radiacion<=(Sum_df_Rad_P348.Rad_teo_348)*0.25]

###############################################################################
##-----------------LECTURA Y AJUSTE DE LOS DATOS DE CH2-GOES-----------------##
###############################################################################

##-------DISCRIMINACION ENTRE DIAS LLUVIOSOS Y SECOS POR DATOS DE NUBOSIDAD CH2 GOES-------##

'En base a un planteamiento desarrollado anteriormente para la caracterización de nubes'
'con información del CH2-GOES 16, atravez de unos umbrales que se establecieron a partir'
'del artículo Rossow.WB & Garder.LC  de 1992 y desarrollado en Umbrales_Reflectancias.py'

ds = Dataset('/home/nacorreasa/Maestria/Datos_Tesis/GOES/GOES_nc_CREADOS/GOES_VA_C2_2019_0320_0610.nc')

Umbral_up_348   = 51.14326
Umbral_down_348 = 22.01725
Umbrales_348 = [Umbral_down_348, Umbral_up_348]

Umbral_up_350   = 53.5013
Umbral_down_350 = 25.9514
Umbrales_350 = [Umbral_down_350, Umbral_up_350]

Umbral_up_975   = 52.5605
Umbral_down_975 = 20.7504
Umbrales_975 = [Umbral_down_975, Umbral_up_975]

lat = ds.variables['lat'][:, :]
lon = ds.variables['lon'][:, :]
Rad = ds.variables['Radiancias'][:, :, :]

                   ## -- Obtener el tiempo para cada valor

tiempo = ds.variables['time']
fechas_horas = nc.num2date(tiempo[:], units=tiempo.units)
for i in range(len(fechas_horas)):
    fechas_horas[i] = fechas_horas[i].strftime('%Y-%m-%d %H:%M')

                   ## -- Selección del pixel de la TS y creación de DF
lat_index_975 = np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0]
lon_index_975 = np.where((lon[0, :] < -75.58) & (lon[0, :] > -75.59))[0][0]
Rad_pixel_975 = Rad[:, lat_index_975, lon_index_975]

Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)

                   ## -- Selección del pixel de la CI
lat_index_350 = np.where((lat[:, 0] > 6.16) & (lat[:, 0] < 6.17))[0][0]
lon_index_350 = np.where((lon[0, :] < -75.64) & (lon[0, :] > -75.65))[0][0]
Rad_pixel_350 = Rad[:, lat_index_350, lon_index_350]

Rad_df_350 = pd.DataFrame()
Rad_df_350['Fecha_Hora'] = fechas_horas
Rad_df_350['Radiacias'] = Rad_pixel_350
Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_350.index = Rad_df_350['Fecha_Hora']
Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)


                   ## -- Selección del pixel de la JV
lat_index_348 = np.where((lat[:, 0] > 6.25) & (lat[:, 0] < 6.26))[0][0]
lon_index_348 = np.where((lon[0, :] < -75.54) & (lon[0, :] > -75.55))[0][0]
Rad_pixel_348 = Rad[:, lat_index_348, lon_index_348]

Rad_df_348 = pd.DataFrame()
Rad_df_348['Fecha_Hora'] = fechas_horas
Rad_df_348['Radiacias'] = Rad_pixel_348
Rad_df_348['Fecha_Hora'] = pd.to_datetime(Rad_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_348.index = Rad_df_348['Fecha_Hora']
Rad_df_348 = Rad_df_348.drop(['Fecha_Hora'], axis=1)

'En este caso, como es por días, si se pueden promediar los valores de reflectancia, ya que se quieren encontrar los dias'
'primordiamente nublados y los primordiamente despejados. En otro caso, no se promedia oficialmente con la hora para no '
'perder la utilidad de la información cada 10 minutos al suavizar la serie.'

Rad_df_348_h =  Rad_df_348.groupby(pd.Grouper(freq="H")).mean()
Rad_df_350_h =  Rad_df_350.groupby(pd.Grouper(freq="H")).mean()
Rad_df_975_h =  Rad_df_975.groupby(pd.Grouper(freq="H")).mean()

df_348_desp_GOES = Rad_df_348_h[Rad_df_348_h['Radiacias'] < Umbral_down_348]
df_350_desp_GOES = Rad_df_350_h[Rad_df_350_h['Radiacias'] < Umbral_down_350]
df_975_desp_GOES = Rad_df_975_h[Rad_df_975_h['Radiacias'] < Umbral_down_975]

df_348_nuba_GOES = Rad_df_348_h[Rad_df_348_h['Radiacias'] > Umbral_up_348]
df_350_nuba_GOES = Rad_df_350_h[Rad_df_350_h['Radiacias'] > Umbral_up_350]
df_975_nuba_GOES = Rad_df_975_h[Rad_df_975_h['Radiacias'] > Umbral_up_975]

df_348_desp_GOES_count = df_348_desp_GOES.groupby(pd.Grouper(freq="D")).count()
df_350_desp_GOES_count = df_350_desp_GOES.groupby(pd.Grouper(freq="D")).count()
df_975_desp_GOES_count = df_975_desp_GOES.groupby(pd.Grouper(freq="D")).count()

df_348_nuba_GOES_count = df_348_nuba_GOES.groupby(pd.Grouper(freq="D")).count()
df_350_nuba_GOES_count = df_350_nuba_GOES.groupby(pd.Grouper(freq="D")).count()
df_975_nuba_GOES_count = df_975_nuba_GOES.groupby(pd.Grouper(freq="D")).count()

'Como se toman datos diurnos (12 horas), entonces el criterio será si en un dia se tuvieron por lo menos 6 '
'horas que excedan los umbrales de radiancias para cada caso, entonces, se considera ese dia como nubado o '
'despejado en cada caso.'

df_348_desp_GOES = df_348_desp_GOES_count[df_348_desp_GOES_count.Radiacias >=6]
df_350_desp_GOES = df_350_desp_GOES_count[df_350_desp_GOES_count.Radiacias >=6]
df_975_desp_GOES = df_975_desp_GOES_count[df_975_desp_GOES_count.Radiacias >=6]

df_348_nuba_GOES = df_348_nuba_GOES_count[df_348_nuba_GOES_count.Radiacias >=6]
df_350_nuba_GOES = df_350_nuba_GOES_count[df_350_nuba_GOES_count.Radiacias >=6]
df_975_nuba_GOES = df_975_nuba_GOES_count[df_975_nuba_GOES_count.Radiacias >=6]

'Realizando una interseccion de los dias que se consideraron despejados y nublados por los dos métodos'
'para luego evaluar que % de la radiación teorica de Gisel representan y pulir los porcentajes de la '
'suma de la radiacion medida por el piranometro.'

desp_result_975 = pd.concat([Desp_Pira_975, df_975_desp_GOES], axis=1, join='inner')
desp_result_350 = pd.concat([Desp_Pira_350, df_350_desp_GOES], axis=1, join='inner')
desp_result_348 = pd.concat([Desp_Pira_348, df_348_desp_GOES], axis=1, join='inner')

nuba_result_975 = pd.concat([Nuba_Pira_975, df_975_nuba_GOES], axis=1, join='inner')
nuba_result_350 = pd.concat([Nuba_Pira_350, df_350_nuba_GOES], axis=1, join='inner')
nuba_result_348 = pd.concat([Nuba_Pira_348, df_348_nuba_GOES], axis=1, join='inner')

desp_result_975['Relacion'] = (desp_result_975['radiacion']*100) /desp_result_975['Radiacion_Teo']
desp_result_350['Relacion'] = (desp_result_350['radiacion']*100) /desp_result_350['Radiacion_Teo']
desp_result_348['Relacion'] = (desp_result_348['radiacion']*100) /desp_result_348['Radiacion_Teo']

nuba_result_975['Relacion'] = (nuba_result_975['radiacion']*100) /nuba_result_975['Radiacion_Teo']
nuba_result_350['Relacion'] = (nuba_result_350['radiacion']*100) /nuba_result_350['Radiacion_Teo']
nuba_result_348['Relacion'] = (nuba_result_348['radiacion']*100) /nuba_result_348['Radiacion_Teo']

'Para hacerlo mas restrictivo, se tomaran los valores para los umbrales  más internos.'

Umbral_desp_pira_975 = np.nanmin(desp_result_975['Relacion'].values)-1
Umbral_desp_pira_350 = np.nanmin(desp_result_350['Relacion'].values)-1
Umbral_desp_pira_348 = np.nanmin(desp_result_348['Relacion'].values)-1

Umbral_nuba_pira_975 = np.nanmax(nuba_result_975['Relacion'].values)+1
Umbral_nuba_pira_350 = np.nanmax(nuba_result_350['Relacion'].values)+1
Umbral_nuba_pira_348 = np.nanmax(nuba_result_348['Relacion'].values)+1

'Todo depende del hallazgo de los umbrales del CH2-GOES, que es lo que sustenta, este procedimento, sin '
'embargo, debe tomarse en cuenta que deben realizarse para un rango mas amplio de pixeles, para un radio.'

print('Porcentaje de radiacion piranometro en TS despejada:'+ str(Umbral_desp_pira_975))
print('Porcentaje de radiacion piranometro en CI despejada:'+ str(Umbral_desp_pira_350))
print('Porcentaje de radiacion piranometro en JV despejada:'+ str(Umbral_desp_pira_348))

print('Porcentaje de radiacion piranometro en TS nublada:'+ str(Umbral_nuba_pira_975))
print('Porcentaje de radiacion piranometro en CI nublada:'+ str(Umbral_nuba_pira_350))
print('Porcentaje de radiacion piranometro en JV nublada:'+ str(Umbral_nuba_pira_348))
