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
from scipy.stats import pearsonr

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------

"Codigo para determinar en nivel de correlacion entre las variables  incidentes en la potencia de los paneles,"
"por lo cual se hace para el horizonte de tiempo de desde que se tengan datos del experimento de los paneles."
"Se hace con la correlación lineal de Pearson."

############################################################################################
## ----------------ACOTANDO LAS FECHAS POR DIA Y MES PARA TOMAR LOS DATOS---------------- ##
############################################################################################

fi_m = 3
fi_d = 23
ff_m = 12
ff_d = 20
Anio_datosGOES = 2019
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
Significancia = False ##--->Para que grafique los valores P y elimine las relaciones poco significantes debe ser True
Solo_Meteo = True    ##--->Para que tome solo los df con info meteorologica debe ser True

##############################################################################
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------
##############################################################################

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##############################################################################
## ----------------LECTURA DE LOS DATOS DE LOS EXPERIMENTOS---------------- ##
##############################################################################

df_P975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel975.txt',  sep=',', index_col =0)
df_P350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel350.txt',  sep=',', index_col =0)
df_P348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Panel348.txt',  sep=',', index_col =0)


df_P975.index = pd.to_datetime(df_P975.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P350.index = pd.to_datetime(df_P350.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P348.index = pd.to_datetime(df_P348.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

## ----------------ACOTANDO LOS DATOS A CALORES VÁLIDOS---------------- ##

df_P975 = df_P975[df_P975['radiacion'] > 0]
df_P350 = df_P350[df_P350['radiacion'] > 0]
df_P348 = df_P348[df_P348['radiacion'] > 0]

df_P975 = df_P975[(df_P975['NI'] >= 0) & (df_P975['strength'] >= 0) & (df_P975['strength'] <=100)]
df_P350 = df_P350[(df_P350['NI'] >= 0) & (df_P350['strength'] >= 0) & (df_P350['strength'] <=100)]
df_P348 = df_P348[(df_P348['NI'] >= 0) & (df_P348['strength'] >= 0) & (df_P348['strength'] <=100)]

df_P975 = df_P975[(df_P975['strength'] >= 0)]
df_P350 = df_P350[(df_P350['NI'] >= 0) & (df_P350['strength'] >= 0)]
df_P348 = df_P348[(df_P348['NI'] >= 0) & (df_P348['strength'] >= 0)]

df_P975_h = df_P975.groupby(pd.Grouper(freq="H")).mean()
df_P350_h = df_P350.groupby(pd.Grouper(freq="H")).mean()
df_P348_h = df_P348.groupby(pd.Grouper(freq="H")).mean()

df_P975_h = df_P975_h[(df_P975_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), errors='coerce')) & (df_P975_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), errors='coerce') )]

df_P350_h = df_P350_h[(df_P350_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), errors='coerce')) & (df_P350_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), errors='coerce') )]

df_P348_h = df_P348_h[(df_P348_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), errors='coerce')) & (df_P348_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), errors='coerce') )]

df_P975_h = df_P975_h.drop(['NI', 'radiacion'], axis=1)
df_P350_h = df_P350_h.drop(['NI', 'radiacion'], axis=1)
df_P348_h = df_P348_h.drop(['NI', 'radiacion'], axis=1)
##########################################################################################
## ----------------LECTURA DE LOS DATOS DE LAS ANOMALIAS DE LA RADIACION--------------- ##
##########################################################################################

Anomal_df_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/df_AnomalRad_pix975_2018_2019.csv',  sep=',')
Anomal_df_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/df_AnomalRad_pix348_2018_2019.csv',  sep=',')
Anomal_df_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/df_AnomalRad_pix350_2018_2019.csv',  sep=',')

Anomal_df_975['fecha_hora'] = pd.to_datetime(Anomal_df_975['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Anomal_df_975.index = Anomal_df_975['fecha_hora']
Anomal_df_975 = Anomal_df_975.drop(['fecha_hora'], axis=1)
Anomal_df_975 = Anomal_df_975.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
Anomal_df_975_h = Anomal_df_975.groupby(pd.Grouper(freq="H")).mean()

Anomal_df_350['fecha_hora'] = pd.to_datetime(Anomal_df_350['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Anomal_df_350.index = Anomal_df_350['fecha_hora']
Anomal_df_350 = Anomal_df_350.drop(['fecha_hora'], axis=1)
Anomal_df_350 = Anomal_df_350.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
Anomal_df_350_h = Anomal_df_350.groupby(pd.Grouper(freq="H")).mean()

Anomal_df_348['fecha_hora'] = pd.to_datetime(Anomal_df_348['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Anomal_df_348.index = Anomal_df_348['fecha_hora']
Anomal_df_348 = Anomal_df_348.drop(['fecha_hora'], axis=1)
Anomal_df_348 = Anomal_df_348.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
Anomal_df_348_h = Anomal_df_348.groupby(pd.Grouper(freq="H")).mean()

if Anio_datosGOES == 2018:
    Anomal_df_975_h.index = [Anomal_df_975_h.index[i].replace(year=2019) for i in range(len(Anomal_df_975_h.index))]
    Anomal_df_350_h.index = [Anomal_df_350_h.index[i].replace(year=2019) for i in range(len(Anomal_df_350_h.index))]
    Anomal_df_348_h.index = [Anomal_df_348_h.index[i].replace(year=2019) for i in range(len(Anomal_df_348_h.index))]

Anomal_df_975_h = Anomal_df_975_h[(Anomal_df_975_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d))) & (Anomal_df_975_h.index <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)))]
Anomal_df_350_h = Anomal_df_350_h[(Anomal_df_350_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d))) & (Anomal_df_350_h.index <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)))]
Anomal_df_348_h = Anomal_df_348_h[(Anomal_df_348_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d))) & (Anomal_df_348_h.index <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)))]

Anomal_df_348_h = Anomal_df_348_h.drop(['Radiacion_Med', 'radiacion',], axis=1)
Anomal_df_350_h = Anomal_df_350_h.drop(['Radiacion_Med', 'radiacion',], axis=1)
Anomal_df_975_h = Anomal_df_975_h.drop(['Radiacion_Med', 'radiacion',], axis=1)

Anomal_df_348_h = Anomal_df_348_h.loc[~Anomal_df_348_h.index.duplicated(keep='first')]
Anomal_df_350_h = Anomal_df_350_h.loc[~Anomal_df_350_h.index.duplicated(keep='first')]
Anomal_df_975_h = Anomal_df_975_h.loc[~Anomal_df_975_h.index.duplicated(keep='first')]

################################################################################
## ----------------LECTURA DE LOS DATOS DE LAS METEOROLÓGICAS---------------- ##
################################################################################

data_T_Torre = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad201.txt',  sep=',')
data_T_Conse = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad206.txt',  sep=',')
data_T_Joaqu = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad367.txt',  sep=',')

data_T_Torre.index = data_T_Torre['fecha_hora']
data_T_Torre = data_T_Torre.drop(['fecha_hora'], axis=1)
data_T_Torre.index = pd.to_datetime(data_T_Torre.index)
data_T_Torre = data_T_Torre.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
data_T_Torre = data_T_Torre[data_T_Torre[u'calidad'] < 100]
data_T_Torre = data_T_Torre[data_T_Torre['T'] > 0]
data_T_Torre_h = data_T_Torre.groupby(pd.Grouper(freq="H")).mean()

data_T_Conse.index = data_T_Conse['fecha_hora']
data_T_Conse = data_T_Conse.drop(['fecha_hora'], axis=1)
data_T_Conse.index = pd.to_datetime(data_T_Conse.index)
data_T_Conse = data_T_Conse.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
data_T_Conse = data_T_Conse[data_T_Conse[u'calidad'] < 100]
data_T_Conse = data_T_Conse[data_T_Conse['T'] > 0]
data_T_Conse_h = data_T_Conse.groupby(pd.Grouper(freq="H")).mean()

data_T_Joaqu.index = data_T_Joaqu['fecha_hora']
data_T_Joaqu = data_T_Joaqu.drop(['fecha_hora'], axis=1)
data_T_Joaqu.index = pd.to_datetime(data_T_Joaqu.index)
data_T_Joaqu = data_T_Joaqu.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
data_T_Joaqu = data_T_Joaqu[data_T_Joaqu[u'calidad'] < 100]
data_T_Joaqu = data_T_Joaqu[data_T_Joaqu['T'] > 0]
data_T_Joaqu_h = data_T_Joaqu.groupby(pd.Grouper(freq="H")).mean()

data_T_Torre_h = data_T_Torre_h[(data_T_Torre_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), errors='coerce')) & (data_T_Torre_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), errors='coerce') )]

data_T_Conse_h = data_T_Conse_h[(data_T_Conse_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), errors='coerce')) & (data_T_Conse_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), errors='coerce') )]

data_T_Joaqu_h = data_T_Joaqu_h[(data_T_Joaqu_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), errors='coerce')) & (data_T_Joaqu_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), errors='coerce') )]

data_T_Torre_h = data_T_Torre_h.drop(['codigo', 'calidad', 'H'], axis=1)
data_T_Conse_h = data_T_Conse_h.drop(['codigo', 'calidad', 'H'], axis=1)
data_T_Joaqu_h = data_T_Joaqu_h.drop(['codigo', 'calidad', 'H'], axis=1)

#########################################################################
## ----------------LECTURA DE LOS DATOS DEL RADIOMETRO---------------- ##
#########################################################################

data_Radi_WV = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/Integrated_VaporDensity_values.csv',  sep=',')
data_Radi_WV.index = data_Radi_WV[u'Unnamed: 0']
data_Radi_WV.index = pd.to_datetime(data_Radi_WV.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
data_Radi_WV = data_Radi_WV.between_time('06:00', '17:00')                      ##--> Seleccionar solo los datos de horas del dia
data_Radi_WV_h = data_Radi_WV[u'Integrate'].groupby(pd.Grouper(freq="H")).mean()

data_Radi_WV_h = data_Radi_WV_h[(data_Radi_WV_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d),  errors='coerce')) & (data_Radi_WV_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d),  errors='coerce') )]


#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
Rad_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix350_Anio.npy')
Rad_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix348_Anio.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')

# fechas_horas_anio = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')
# fechas_horas_anio = pd.to_datetime(fechas_horas_anio, format="%Y-%m-%d %H:%M", errors='coerce')
#
# fechas_horas_2019 = fechas_horas_anio[fechas_horas_anio.year==2019]
# fechas_horas_exp = fechas_horas_2019[fechas_horas_2019.date >= datetime.datetime('2019-03-20',format="%Y-%m-%d")]
#
# ##----------------------------------------------------------------------------------------##
#
# fechas_horas_new = [fechas_horas_new[i].strftime('%Y-%m-%d %H:%M') for i in range(len(fechas_horas_new))]
# fechas_horas_new = np.array(fechas_horas_new)

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

Rad_df_975_h = Rad_df_975.groupby(pd.Grouper(freq="H")).mean()
Rad_df_350_h = Rad_df_350.groupby(pd.Grouper(freq="H")).mean()
Rad_df_348_h = Rad_df_348.groupby(pd.Grouper(freq="H")).mean()

if Anio_datosGOES == 2018:
    Rad_df_975_h.index = [Rad_df_975_h.index[i].replace(year=2019) for i in range(len(Rad_df_975_h.index))]
    Rad_df_350_h.index = [Rad_df_350_h.index[i].replace(year=2019) for i in range(len(Rad_df_350_h.index))]
    Rad_df_348_h.index = [Rad_df_348_h.index[i].replace(year=2019) for i in range(len(Rad_df_348_h.index))]

Rad_df_975_h = Rad_df_975_h[(Rad_df_975_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d))) & (Rad_df_975_h.index <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)))]
Rad_df_350_h = Rad_df_350_h[(Rad_df_350_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d))) & (Rad_df_350_h.index <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)))]
Rad_df_348_h = Rad_df_348_h[(Rad_df_348_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'+str(fi_d))) & (Rad_df_348_h.index <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)))]

Rad_df_348_h = Rad_df_348_h.loc[~Rad_df_348_h.index.duplicated(keep='first')]
Rad_df_350_h = Rad_df_350_h.loc[~Rad_df_350_h.index.duplicated(keep='first')]
Rad_df_975_h = Rad_df_975_h.loc[~Rad_df_975_h.index.duplicated(keep='first')]

################################################################################
## ----------------LECTURA DE LOS DATOS DE EFICIENCIA NOMINAL---------------- ##
################################################################################

"Obtenidos del programa Tesis_Eficiencia_Panel.py"

df_nomEfi_975 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Efi_tiempo_nominal_P975.csv',  sep=',')
df_nomEfi_350 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Efi_tiempo_nominal_P350.csv',  sep=',')
df_nomEfi_348 = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Efi_tiempo_nominal_P348.csv',  sep=',')

df_nomEfi_975['fecha_hora'] = pd.to_datetime(df_nomEfi_975['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_nomEfi_975.index =  df_nomEfi_975['fecha_hora']

df_nomEfi_350['fecha_hora'] = pd.to_datetime(df_nomEfi_350['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_nomEfi_350.index =  df_nomEfi_350['fecha_hora']

df_nomEfi_348['fecha_hora'] = pd.to_datetime(df_nomEfi_348['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_nomEfi_348.index =  df_nomEfi_348['fecha_hora']

df_nomEfi_975 = df_nomEfi_975[(df_nomEfi_975.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d),  errors='coerce')) & (df_nomEfi_975.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d),  errors='coerce') )]

df_nomEfi_350 = df_nomEfi_350[(df_nomEfi_350.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d),  errors='coerce')) & (df_nomEfi_350.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d),  errors='coerce') )]

df_nomEfi_348 = df_nomEfi_348[(df_nomEfi_348.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d),  errors='coerce')) & (df_nomEfi_348.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d),  errors='coerce') )]

##------------------------ACOTANDOLO A VALORES VÁLIDOS--------------------------##
df_nomEfi_975 = df_nomEfi_975[df_nomEfi_975.Efi <=100]
df_nomEfi_350 = df_nomEfi_350[df_nomEfi_350.Efi <=100]
df_nomEfi_348 = df_nomEfi_975[df_nomEfi_975.Efi <=100]

df_nomEfi_975 = df_nomEfi_975.drop(['fecha_hora'], axis=1)
df_nomEfi_348 = df_nomEfi_348.drop(['fecha_hora'], axis=1)
df_nomEfi_350 = df_nomEfi_350.drop(['fecha_hora'], axis=1)

################################################################################
## -----------------------LECTURA DE LOS DATOS DE PM 2.5--------------------- ##
################################################################################
"Se toman los datos de PM 2.5 como indicados de las particulas que pueden dispersar la radiación solar."
"Los puntos a considerar son : la estacion 25 de UN Agronomia, la 80 en Villa Hermosa y la 38 en el Consejo"
"de Itagüí"

data_PM_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/PM_2con5/Total_Timeseries_PM25.csv',  sep=',')
data_PM_JV = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/PM_2con5/Total_Timeseries_PM80.csv',  sep=',')
data_PM_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/PM_2con5/Total_Timeseries_PM38.csv',  sep=',')

df_PM_TS = data_PM_TS[['Unnamed: 0', 'codigoSerial', 'pm25', 'calidad_pm25']]
df_PM_JV = data_PM_JV[['Unnamed: 0', 'codigoSerial', 'pm25', 'calidad_pm25']]
df_PM_CI = data_PM_CI[['Unnamed: 0', 'codigoSerial', 'pm25', 'calidad_pm25']]

df_PM_TS.columns = ['fecha_hora', 'codigoSerial', 'pm25', 'calidad_pm25']
df_PM_CI.columns = ['fecha_hora', 'codigoSerial', 'pm25', 'calidad_pm25']
df_PM_JV.columns = ['fecha_hora', 'codigoSerial', 'pm25', 'calidad_pm25']

df_PM_TS = df_PM_TS[df_PM_TS['calidad_pm25'] ==1]
df_PM_JV = df_PM_JV[df_PM_JV['calidad_pm25'] ==1]
df_PM_CI = df_PM_CI[df_PM_CI['calidad_pm25'] ==1]

df_PM_TS['fecha_hora'] = pd.to_datetime(df_PM_TS['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_PM_TS.index = df_PM_TS['fecha_hora']
df_PM_TS = df_PM_TS.drop(['fecha_hora', 'codigoSerial', 'calidad_pm25'], axis=1)

df_PM_CI['fecha_hora'] = pd.to_datetime(df_PM_CI['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_PM_CI.index = df_PM_CI['fecha_hora']
df_PM_CI = df_PM_CI.drop(['fecha_hora', 'codigoSerial', 'calidad_pm25'], axis=1)

df_PM_JV['fecha_hora'] = pd.to_datetime(df_PM_JV['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_PM_JV.index = df_PM_JV['fecha_hora']
df_PM_JV = df_PM_JV.drop(['fecha_hora', 'codigoSerial', 'calidad_pm25'], axis=1)

df_PM_JV =  df_PM_JV.loc[~df_PM_JV.index.duplicated(keep='first')]
df_PM_CI =  df_PM_CI.loc[~df_PM_CI.index.duplicated(keep='first')]
df_PM_TS =  df_PM_TS.loc[~df_PM_TS.index.duplicated(keep='first')]

df_PM_TS = df_PM_TS[(df_PM_TS.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d),  errors='coerce')) & (df_PM_TS.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d),  errors='coerce') )]

df_PM_JV = df_PM_JV[(df_PM_JV.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d),  errors='coerce')) & (df_PM_JV.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d),  errors='coerce') )]

df_PM_CI = df_PM_CI[(df_PM_CI.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d),  errors='coerce')) & (df_PM_CI.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d),  errors='coerce') )]

df_PM_TS = df_PM_TS.between_time('06:00', '17:59')
df_PM_CI = df_PM_CI.between_time('06:00', '17:59')
df_PM_JV = df_PM_JV.between_time('06:00', '17:59')


#################################################################################################
## -----------------------------SERIE DE ANOMALIAS DE LAS VARIABLES--------------------------- ##
#################################################################################################



df_result_975 =  pd.concat([df_P975_h ,  data_T_Torre_h ,data_Radi_WV_h , Rad_df_975_h, df_nomEfi_975, df_PM_TS], axis=1)
df_result_350 =  pd.concat([df_P350_h , data_T_Conse_h, data_Radi_WV_h , Rad_df_350_h, df_nomEfi_350, df_PM_CI], axis=1)
df_result_348 =  pd.concat([df_P348_h ,  data_T_Joaqu_h, data_Radi_WV_h , Rad_df_348_h, df_nomEfi_348, df_PM_JV], axis=1)

import datetime
def daterange(start_date, end_date):
    'Para el ajuste de las fechas en el modelo de Kumar cada hora. Las fechas'
    'final e inicial son en str: %Y-%m-%d'

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    delta = timedelta(minutes=60)
    while start_date <= end_date:
        yield start_date
        start_date += delta

fechas = []
for i in daterange(df_result_975.index[0].date().strftime("%Y-%m-%d"), (df_result_975.index[-1].date() + timedelta(days=1)).strftime("%Y-%m-%d")):
    fechas.append(i)

##--------------------------TEMPERATURA-------------------------------------##
df_result_975_Temp = df_result_975['T'][df_result_975['T']>0]
df_result_975_Temp_monthly_mean= df_result_975_Temp.groupby([df_result_975_Temp.index.month, df_result_975_Temp.index.hour]).mean()
punto_Temp_975 = df_result_975_Temp_monthly_mean.values

Temp_975 = []
fechas_new_Temp_975 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_975_Temp_monthly_mean.index.get_level_values(0))):
        if (df_result_975_Temp_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_975_Temp_monthly_mean.index.get_level_values(1)[j] == hora):
            Temp_975.append(punto_Temp_975[j])
            fechas_new_Temp_975.append(fechas[i])
        else:
            pass

df_Temp_975 = pd.DataFrame()
df_Temp_975['fecha_hora'] = fechas_new_Temp_975
df_Temp_975['Temp_Med'] = Temp_975
df_Temp_975.index = df_Temp_975['fecha_hora']
df_Temp_975 = df_Temp_975.drop(['fecha_hora'], axis=1)
df_Temp_975 = df_Temp_975.between_time('06:00', '17:59')

df_Anomal_Temp_975 = pd.concat([df_Temp_975, df_result_975_Temp], axis=1)
df_Anomal_Temp_975['Anomalia_T'] = df_Anomal_Temp_975['T']- df_Temp_975['Temp_Med']



df_result_350_Temp = df_result_350['T'][df_result_350['T']>0]
df_result_350_Temp_monthly_mean= df_result_350_Temp.groupby([df_result_350_Temp.index.month, df_result_350_Temp.index.hour]).mean()
punto_Temp_350 = df_result_350_Temp_monthly_mean.values

Temp_350 = []
fechas_new_Temp_350 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_350_Temp_monthly_mean.index.get_level_values(0))):
        if (df_result_350_Temp_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_350_Temp_monthly_mean.index.get_level_values(1)[j] == hora):
            Temp_350.append(punto_Temp_350[j])
            fechas_new_Temp_350.append(fechas[i])
        else:
            pass

df_Temp_350 = pd.DataFrame()
df_Temp_350['fecha_hora'] = fechas_new_Temp_350
df_Temp_350['Temp_Med'] = Temp_350
df_Temp_350.index = df_Temp_350['fecha_hora']
df_Temp_350 = df_Temp_350.drop(['fecha_hora'], axis=1)
df_Temp_350 = df_Temp_350.between_time('06:00', '17:59')

df_Anomal_Temp_350 = pd.concat([df_Temp_350, df_result_350_Temp], axis=1)
df_Anomal_Temp_350['Anomalia_T'] = df_Anomal_Temp_350['T']- df_Temp_350['Temp_Med']



df_result_348_Temp = df_result_348['T'][df_result_348['T']>0]
df_result_348_Temp_monthly_mean= df_result_348_Temp.groupby([df_result_348_Temp.index.month, df_result_348_Temp.index.hour]).mean()
punto_Temp_348 = df_result_348_Temp_monthly_mean.values

Temp_348 = []
fechas_new_Temp_348 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_348_Temp_monthly_mean.index.get_level_values(0))):
        if (df_result_348_Temp_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_348_Temp_monthly_mean.index.get_level_values(1)[j] == hora):
            Temp_348.append(punto_Temp_348[j])
            fechas_new_Temp_348.append(fechas[i])
        else:
            pass

df_Temp_348 = pd.DataFrame()
df_Temp_348['fecha_hora'] = fechas_new_Temp_348
df_Temp_348['Temp_Med'] = Temp_348
df_Temp_348.index = df_Temp_348['fecha_hora']
df_Temp_348 = df_Temp_348.drop(['fecha_hora'], axis=1)
df_Temp_348 = df_Temp_348.between_time('06:00', '17:59')

df_Anomal_Temp_348 = pd.concat([df_Temp_348, df_result_348_Temp], axis=1)
df_Anomal_Temp_348['Anomalia_T'] = df_Anomal_Temp_348['T']- df_Temp_348['Temp_Med']


##--------------------------DENSIDAD DEL VAPOR DE AGUA-------------------------------------##
df_result_975_WP = df_result_975['Integrate'][df_result_975['Integrate']>=0]
df_result_975_WP_monthly_mean= df_result_975_WP.groupby([df_result_975_WP.index.month, df_result_975_WP.index.hour]).mean()
punto_WP_975 = df_result_975_WP_monthly_mean.values

WP_975 = []
fechas_new_WP_975 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_975_WP_monthly_mean.index.get_level_values(0))):
        if (df_result_975_WP_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_975_WP_monthly_mean.index.get_level_values(1)[j] == hora):
            WP_975.append(punto_WP_975[j])
            fechas_new_WP_975.append(fechas[i])
        else:
            pass

df_WP_975 = pd.DataFrame()
df_WP_975['fecha_hora'] = fechas_new_WP_975
df_WP_975['WP_Med'] = WP_975
df_WP_975.index = df_WP_975['fecha_hora']
df_WP_975 = df_WP_975.drop(['fecha_hora'], axis=1)
df_WP_975 = df_WP_975.between_time('06:00', '17:59')

df_Anomal_WP_975 = pd.concat([df_WP_975, df_result_975_WP], axis=1)
df_Anomal_WP_975['Anomalia_WP'] = df_Anomal_WP_975['Integrate']- df_WP_975['WP_Med']



df_result_350_WP = df_result_350['Integrate'][df_result_350['Integrate']>0]
df_result_350_WP_monthly_mean= df_result_350_WP.groupby([df_result_350_WP.index.month, df_result_350_WP.index.hour]).mean()
punto_WP_350 = df_result_350_WP_monthly_mean.values

WP_350 = []
fechas_new_WP_350 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_350_WP_monthly_mean.index.get_level_values(0))):
        if (df_result_350_WP_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_350_WP_monthly_mean.index.get_level_values(1)[j] == hora):
            WP_350.append(punto_WP_350[j])
            fechas_new_WP_350.append(fechas[i])
        else:
            pass

df_WP_350 = pd.DataFrame()
df_WP_350['fecha_hora'] = fechas_new_WP_350
df_WP_350['WP_Med'] = WP_350
df_WP_350.index = df_WP_350['fecha_hora']
df_WP_350 = df_WP_350.drop(['fecha_hora'], axis=1)
df_WP_350 = df_WP_350.between_time('06:00', '17:59')

df_Anomal_WP_350 = pd.concat([df_WP_350, df_result_350_WP], axis=1)
df_Anomal_WP_350['Anomalia_WP'] = df_Anomal_WP_350['Integrate']- df_WP_350['WP_Med']



df_result_348_WP = df_result_348['Integrate'][df_result_348['Integrate']>0]
df_result_348_WP_monthly_mean= df_result_348_WP.groupby([df_result_348_WP.index.month, df_result_348_WP.index.hour]).mean()
punto_WP_348 = df_result_348_WP_monthly_mean.values

WP_348 = []
fechas_new_WP_348 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_348_WP_monthly_mean.index.get_level_values(0))):
        if (df_result_348_WP_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_348_WP_monthly_mean.index.get_level_values(1)[j] == hora):
            WP_348.append(punto_WP_348[j])
            fechas_new_WP_348.append(fechas[i])
        else:
            pass

df_WP_348 = pd.DataFrame()
df_WP_348['fecha_hora'] = fechas_new_WP_348
df_WP_348['WP_Med'] = WP_348
df_WP_348.index = df_WP_348['fecha_hora']
df_WP_348 = df_WP_348.drop(['fecha_hora'], axis=1)
df_WP_348 = df_WP_348.between_time('06:00', '17:59')

df_Anomal_WP_348 = pd.concat([df_WP_348, df_result_348_WP], axis=1)
df_Anomal_WP_348['Anomalia_WP'] = df_Anomal_WP_348['Integrate']- df_WP_348['WP_Med']


##--------------------------FACTOR DE RELFECTANCIA-------------------------------------##
df_result_975_FR = df_result_975['Radiacias'][df_result_975['Radiacias']>=0]
df_result_975_FR_monthly_mean= df_result_975_FR.groupby([df_result_975_FR.index.month, df_result_975_FR.index.hour]).mean()
punto_FR_975 = df_result_975_FR_monthly_mean.values

FR_975 = []
fechas_new_FR_975 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_975_FR_monthly_mean.index.get_level_values(0))):
        if (df_result_975_FR_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_975_FR_monthly_mean.index.get_level_values(1)[j] == hora):
            FR_975.append(punto_FR_975[j])
            fechas_new_FR_975.append(fechas[i])
        else:
            pass

df_FR_975 = pd.DataFrame()
df_FR_975['fecha_hora'] = fechas_new_FR_975
df_FR_975['FR_Med'] = FR_975
df_FR_975.index = df_FR_975['fecha_hora']
df_FR_975 = df_FR_975.drop(['fecha_hora'], axis=1)
df_FR_975 = df_FR_975.between_time('06:00', '17:59')

df_Anomal_FR_975 = pd.concat([df_FR_975, df_result_975_FR], axis=1)
df_Anomal_FR_975['Anomalia_FR'] = df_Anomal_FR_975['Radiacias']- df_FR_975['FR_Med']



df_result_350_FR = df_result_350['Radiacias'][df_result_350['Radiacias']>0]
df_result_350_FR_monthly_mean= df_result_350_FR.groupby([df_result_350_FR.index.month, df_result_350_FR.index.hour]).mean()
punto_FR_350 = df_result_350_FR_monthly_mean.values

FR_350 = []
fechas_new_FR_350 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_350_FR_monthly_mean.index.get_level_values(0))):
        if (df_result_350_FR_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_350_FR_monthly_mean.index.get_level_values(1)[j] == hora):
            FR_350.append(punto_FR_350[j])
            fechas_new_FR_350.append(fechas[i])
        else:
            pass

df_FR_350 = pd.DataFrame()
df_FR_350['fecha_hora'] = fechas_new_FR_350
df_FR_350['FR_Med'] = FR_350
df_FR_350.index = df_FR_350['fecha_hora']
df_FR_350 = df_FR_350.drop(['fecha_hora'], axis=1)
df_FR_350 = df_FR_350.between_time('06:00', '17:59')

df_Anomal_FR_350 = pd.concat([df_FR_350, df_result_350_FR], axis=1)
df_Anomal_FR_350['Anomalia_FR'] = df_Anomal_FR_350['Radiacias']- df_FR_350['FR_Med']



df_result_348_FR = df_result_348['Radiacias'][df_result_348['Radiacias']>0]
df_result_348_FR_monthly_mean= df_result_348_FR.groupby([df_result_348_FR.index.month, df_result_348_FR.index.hour]).mean()
punto_FR_348 = df_result_348_FR_monthly_mean.values

FR_348 = []
fechas_new_FR_348 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_348_FR_monthly_mean.index.get_level_values(0))):
        if (df_result_348_FR_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_348_FR_monthly_mean.index.get_level_values(1)[j] == hora):
            FR_348.append(punto_FR_348[j])
            fechas_new_FR_348.append(fechas[i])
        else:
            pass

df_FR_348 = pd.DataFrame()
df_FR_348['fecha_hora'] = fechas_new_FR_348
df_FR_348['FR_Med'] = FR_348
df_FR_348.index = df_FR_348['fecha_hora']
df_FR_348 = df_FR_348.drop(['fecha_hora'], axis=1)
df_FR_348 = df_FR_348.between_time('06:00', '17:59')

df_Anomal_FR_348 = pd.concat([df_FR_348, df_result_348_FR], axis=1)
df_Anomal_FR_348['Anomalia_FR'] = df_Anomal_FR_348['Radiacias']- df_FR_348['FR_Med']



##--------------------------PM 2.5-------------------------------------##
df_result_975_PM = df_result_975['pm25'][df_result_975['pm25']>=0]
df_result_975_PM_monthly_mean= df_result_975_PM.groupby([df_result_975_PM.index.month, df_result_975_PM.index.hour]).mean()
punto_PM_975 = df_result_975_PM_monthly_mean.values

PM_975 = []
fechas_new_PM_975 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_975_PM_monthly_mean.index.get_level_values(0))):
        if (df_result_975_PM_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_975_PM_monthly_mean.index.get_level_values(1)[j] == hora):
            PM_975.append(punto_PM_975[j])
            fechas_new_PM_975.append(fechas[i])
        else:
            pass

df_PM_975 = pd.DataFrame()
df_PM_975['fecha_hora'] = fechas_new_PM_975
df_PM_975['PM_Med'] = PM_975
df_PM_975.index = df_PM_975['fecha_hora']
df_PM_975 = df_PM_975.drop(['fecha_hora'], axis=1)
df_PM_975 = df_PM_975.between_time('06:00', '17:59')

df_Anomal_PM_975 = pd.concat([df_PM_975, df_result_975_PM], axis=1)
df_Anomal_PM_975['Anomalia_PM'] = df_Anomal_PM_975['pm25']- df_PM_975['PM_Med']



df_result_350_PM = df_result_350['pm25'][df_result_350['pm25']>0]
df_result_350_PM_monthly_mean= df_result_350_PM.groupby([df_result_350_PM.index.month, df_result_350_PM.index.hour]).mean()
punto_PM_350 = df_result_350_PM_monthly_mean.values

PM_350 = []
fechas_new_PM_350 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_350_PM_monthly_mean.index.get_level_values(0))):
        if (df_result_350_PM_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_350_PM_monthly_mean.index.get_level_values(1)[j] == hora):
            PM_350.append(punto_PM_350[j])
            fechas_new_PM_350.append(fechas[i])
        else:
            pass

df_PM_350 = pd.DataFrame()
df_PM_350['fecha_hora'] = fechas_new_PM_350
df_PM_350['PM_Med'] = PM_350
df_PM_350.index = df_PM_350['fecha_hora']
df_PM_350 = df_PM_350.drop(['fecha_hora'], axis=1)
df_PM_350 = df_PM_350.between_time('06:00', '17:59')

df_Anomal_PM_350 = pd.concat([df_PM_350, df_result_350_PM], axis=1)
df_Anomal_PM_350['Anomalia_PM'] = df_Anomal_PM_350['pm25']- df_PM_350['PM_Med']



df_result_348_PM = df_result_348['pm25'][df_result_348['pm25']>0]
df_result_348_PM_monthly_mean= df_result_348_PM.groupby([df_result_348_PM.index.month, df_result_348_PM.index.hour]).mean()
punto_PM_348 = df_result_348_PM_monthly_mean.values

PM_348 = []
fechas_new_PM_348 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_348_PM_monthly_mean.index.get_level_values(0))):
        if (df_result_348_PM_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_348_PM_monthly_mean.index.get_level_values(1)[j] == hora):
            PM_348.append(punto_PM_348[j])
            fechas_new_PM_348.append(fechas[i])
        else:
            pass

df_PM_348 = pd.DataFrame()
df_PM_348['fecha_hora'] = fechas_new_PM_348
df_PM_348['PM_Med'] = PM_348
df_PM_348.index = df_PM_348['fecha_hora']
df_PM_348 = df_PM_348.drop(['fecha_hora'], axis=1)
df_PM_348 = df_PM_348.between_time('06:00', '17:59')

df_Anomal_PM_348 = pd.concat([df_PM_348, df_result_348_PM], axis=1)
df_Anomal_PM_348['Anomalia_PM'] = df_Anomal_PM_348['pm25']- df_PM_348['PM_Med']

##--------------------------POTENCIA-------------------------------------##
df_result_975_Potencia = df_result_975['strength'][df_result_975['strength']>=0]
df_result_975_Potencia_monthly_mean= df_result_975_Potencia.groupby([df_result_975_Potencia.index.month, df_result_975_Potencia.index.hour]).mean()
punto_Potencia_975 = df_result_975_Potencia_monthly_mean.values

Potencia_975 = []
fechas_new_Potencia_975 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_975_Potencia_monthly_mean.index.get_level_values(0))):
        if (df_result_975_Potencia_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_975_Potencia_monthly_mean.index.get_level_values(1)[j] == hora):
            Potencia_975.append(punto_Potencia_975[j])
            fechas_new_Potencia_975.append(fechas[i])
        else:
            pass

df_Potencia_975 = pd.DataFrame()
df_Potencia_975['fecha_hora'] = fechas_new_Potencia_975
df_Potencia_975['Potencia_Med'] = Potencia_975
df_Potencia_975.index = df_Potencia_975['fecha_hora']
df_Potencia_975 = df_Potencia_975.drop(['fecha_hora'], axis=1)
df_Potencia_975 = df_Potencia_975.between_time('06:00', '17:59')

df_Anomal_Potencia_975 = pd.concat([df_Potencia_975, df_result_975_Potencia], axis=1)
df_Anomal_Potencia_975['Anomalia_Potencia'] = df_Anomal_Potencia_975['strength']- df_Potencia_975['Potencia_Med']



df_result_350_Potencia = df_result_350['strength'][df_result_350['strength']>0]
df_result_350_Potencia_monthly_mean= df_result_350_Potencia.groupby([df_result_350_Potencia.index.month, df_result_350_Potencia.index.hour]).mean()
punto_Potencia_350 = df_result_350_Potencia_monthly_mean.values

Potencia_350 = []
fechas_new_Potencia_350 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_350_Potencia_monthly_mean.index.get_level_values(0))):
        if (df_result_350_Potencia_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_350_Potencia_monthly_mean.index.get_level_values(1)[j] == hora):
            Potencia_350.append(punto_Potencia_350[j])
            fechas_new_Potencia_350.append(fechas[i])
        else:
            pass

df_Potencia_350 = pd.DataFrame()
df_Potencia_350['fecha_hora'] = fechas_new_Potencia_350
df_Potencia_350['Potencia_Med'] = Potencia_350
df_Potencia_350.index = df_Potencia_350['fecha_hora']
df_Potencia_350 = df_Potencia_350.drop(['fecha_hora'], axis=1)
df_Potencia_350 = df_Potencia_350.between_time('06:00', '17:59')

df_Anomal_Potencia_350 = pd.concat([df_Potencia_350, df_result_350_Potencia], axis=1)
df_Anomal_Potencia_350['Anomalia_Potencia'] = df_Anomal_Potencia_350['strength']- df_Potencia_350['Potencia_Med']



df_result_348_Potencia = df_result_348['strength'][df_result_348['strength']>0]
df_result_348_Potencia_monthly_mean= df_result_348_Potencia.groupby([df_result_348_Potencia.index.month, df_result_348_Potencia.index.hour]).mean()
punto_Potencia_348 = df_result_348_Potencia_monthly_mean.values

Potencia_348 = []
fechas_new_Potencia_348 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_348_Potencia_monthly_mean.index.get_level_values(0))):
        if (df_result_348_Potencia_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_348_Potencia_monthly_mean.index.get_level_values(1)[j] == hora):
            Potencia_348.append(punto_Potencia_348[j])
            fechas_new_Potencia_348.append(fechas[i])
        else:
            pass

df_Potencia_348 = pd.DataFrame()
df_Potencia_348['fecha_hora'] = fechas_new_Potencia_348
df_Potencia_348['Potencia_Med'] = Potencia_348
df_Potencia_348.index = df_Potencia_348['fecha_hora']
df_Potencia_348 = df_Potencia_348.drop(['fecha_hora'], axis=1)
df_Potencia_348 = df_Potencia_348.between_time('06:00', '17:59')

df_Anomal_Potencia_348 = pd.concat([df_Potencia_348, df_result_348_Potencia], axis=1)
df_Anomal_Potencia_348['Anomalia_Potencia'] = df_Anomal_Potencia_348['strength']- df_Potencia_348['Potencia_Med']


##--------------------------EFICIENCIA------------------------------------##
df_result_975_Eficiencia = df_result_975['Efi'][df_result_975['Efi']>=0]
df_result_975_Eficiencia_monthly_mean= df_result_975_Eficiencia.groupby([df_result_975_Eficiencia.index.month, df_result_975_Eficiencia.index.hour]).mean()
punto_Eficiencia_975 = df_result_975_Eficiencia_monthly_mean.values

Eficiencia_975 = []
fechas_new_Eficiencia_975 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_975_Eficiencia_monthly_mean.index.get_level_values(0))):
        if (df_result_975_Eficiencia_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_975_Eficiencia_monthly_mean.index.get_level_values(1)[j] == hora):
            Eficiencia_975.append(punto_Eficiencia_975[j])
            fechas_new_Eficiencia_975.append(fechas[i])
        else:
            pass

df_Eficiencia_975 = pd.DataFrame()
df_Eficiencia_975['fecha_hora'] = fechas_new_Eficiencia_975
df_Eficiencia_975['Eficiencia_Med'] = Eficiencia_975
df_Eficiencia_975.index = df_Eficiencia_975['fecha_hora']
df_Eficiencia_975 = df_Eficiencia_975.drop(['fecha_hora'], axis=1)
df_Eficiencia_975 = df_Eficiencia_975.between_time('06:00', '17:59')

df_Anomal_Eficiencia_975 = pd.concat([df_Eficiencia_975, df_result_975_Eficiencia], axis=1)
df_Anomal_Eficiencia_975['Anomalia_Eficiencia'] = df_Anomal_Eficiencia_975['Efi']- df_Eficiencia_975['Eficiencia_Med']



df_result_350_Eficiencia = df_result_350['Efi'][df_result_350['Efi']>0]
df_result_350_Eficiencia_monthly_mean= df_result_350_Eficiencia.groupby([df_result_350_Eficiencia.index.month, df_result_350_Eficiencia.index.hour]).mean()
punto_Eficiencia_350 = df_result_350_Eficiencia_monthly_mean.values

Eficiencia_350 = []
fechas_new_Eficiencia_350 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_350_Eficiencia_monthly_mean.index.get_level_values(0))):
        if (df_result_350_Eficiencia_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_350_Eficiencia_monthly_mean.index.get_level_values(1)[j] == hora):
            Eficiencia_350.append(punto_Eficiencia_350[j])
            fechas_new_Eficiencia_350.append(fechas[i])
        else:
            pass

df_Eficiencia_350 = pd.DataFrame()
df_Eficiencia_350['fecha_hora'] = fechas_new_Eficiencia_350
df_Eficiencia_350['Eficiencia_Med'] = Eficiencia_350
df_Eficiencia_350.index = df_Eficiencia_350['fecha_hora']
df_Eficiencia_350 = df_Eficiencia_350.drop(['fecha_hora'], axis=1)
df_Eficiencia_350 = df_Eficiencia_350.between_time('06:00', '17:59')

df_Anomal_Eficiencia_350 = pd.concat([df_Eficiencia_350, df_result_350_Eficiencia], axis=1)
df_Anomal_Eficiencia_350['Anomalia_Eficiencia'] = df_Anomal_Eficiencia_350['Efi']- df_Eficiencia_350['Eficiencia_Med']



df_result_348_Eficiencia = df_result_348['Efi'][df_result_348['Efi']>0]
df_result_348_Eficiencia_monthly_mean= df_result_348_Eficiencia.groupby([df_result_348_Eficiencia.index.month, df_result_348_Eficiencia.index.hour]).mean()
punto_Eficiencia_348 = df_result_348_Eficiencia_monthly_mean.values

Eficiencia_348 = []
fechas_new_Eficiencia_348 =[]
for i in range(len(fechas)):
    mes = fechas[i].month
    hora = fechas[i].hour
    for j in range(len(df_result_348_Eficiencia_monthly_mean.index.get_level_values(0))):
        if (df_result_348_Eficiencia_monthly_mean.index.get_level_values(0)[j] == mes) & (df_result_348_Eficiencia_monthly_mean.index.get_level_values(1)[j] == hora):
            Eficiencia_348.append(punto_Eficiencia_348[j])
            fechas_new_Eficiencia_348.append(fechas[i])
        else:
            pass

df_Eficiencia_348 = pd.DataFrame()
df_Eficiencia_348['fecha_hora'] = fechas_new_Eficiencia_348
df_Eficiencia_348['Eficiencia_Med'] = Eficiencia_348
df_Eficiencia_348.index = df_Eficiencia_348['fecha_hora']
df_Eficiencia_348 = df_Eficiencia_348.drop(['fecha_hora'], axis=1)
df_Eficiencia_348 = df_Eficiencia_348.between_time('06:00', '17:59')

df_Anomal_Eficiencia_348 = pd.concat([df_Eficiencia_348, df_result_348_Eficiencia], axis=1)
df_Anomal_Eficiencia_348['Anomalia_Eficiencia'] = df_Anomal_Eficiencia_348['Efi']- df_Eficiencia_348['Eficiencia_Med']


#################################################################################
## ----------------CORRELACION ENTRE LAS VARIABLES PRINCIPALES---------------- ##
#################################################################################
if Solo_Meteo == False:

    ##-----------------CONCATENANDO LOS DATAFRAMES DE LAS ANOMALÍAS------------------------------##
    nombre = 'ConPotencia'

    df_corr_975 =  pd.concat([Anomal_df_975_h, pd.DataFrame(df_Anomal_Potencia_975['Anomalia_Potencia']) , pd.DataFrame(df_Anomal_Temp_975['Anomalia_T']) ,pd.DataFrame(df_Anomal_WP_975['Anomalia_WP']) , pd.DataFrame(df_Anomal_FR_975['Anomalia_FR']), pd.DataFrame(df_Anomal_Eficiencia_975['Anomalia_Eficiencia']) , pd.DataFrame(df_Anomal_PM_975['Anomalia_PM'])], axis=1)
    df_corr_350 =  pd.concat([Anomal_df_350_h, pd.DataFrame(df_Anomal_Potencia_350['Anomalia_Potencia']) , pd.DataFrame(df_Anomal_Temp_350['Anomalia_T']) ,pd.DataFrame(df_Anomal_WP_350['Anomalia_WP']) , pd.DataFrame(df_Anomal_FR_350['Anomalia_FR']), pd.DataFrame(df_Anomal_Eficiencia_350['Anomalia_Eficiencia']) , pd.DataFrame(df_Anomal_PM_350['Anomalia_PM'])], axis=1)
    df_corr_348 =  pd.concat([Anomal_df_348_h,  pd.DataFrame(df_Anomal_Potencia_348['Anomalia_Potencia']) , pd.DataFrame(df_Anomal_Temp_348['Anomalia_T']) ,pd.DataFrame(df_Anomal_WP_348['Anomalia_WP']) , pd.DataFrame(df_Anomal_FR_348['Anomalia_FR']), pd.DataFrame(df_Anomal_Eficiencia_348['Anomalia_Eficiencia']) ,  pd.DataFrame(df_Anomal_PM_348['Anomalia_PM'])], axis=1)

    df_corr_975.to_csv(Path_save[0:45]+nombre+'_EXP_Anomalias_VariablesCondicionantes_975.csv', sep=',')
    df_corr_350.to_csv(Path_save[0:45]+nombre+ '_EXP_Anomalias_VariablesCondicionantes_350.csv', sep=',')
    df_corr_348.to_csv(Path_save[0:45]+nombre+'_EXP_Anomalias_VariablesCondicionantes_348.csv', sep=',')

    df_corr_975.columns = ['Irradiancia', 'Pot', 'Temp', u'Den VA', 'FR', u'$\eta$', u'PM 2.5']
    df_corr_350.columns = ['Irradiancia', 'Pot', 'Temp', u'Den VA', 'FR', u'$\eta$', u'PM 2.5']
    df_corr_348.columns = ['Irradiancia', 'Pot', 'Temp', u'Den VA', 'FR', u'$\eta$', u'PM 2.5']

    corr_975 = df_corr_975.corr(method = 'pearson')
    corr_350 = df_corr_350.corr(method = 'pearson')
    corr_348 = df_corr_348.corr(method = 'pearson')


elif Solo_Meteo == True:

    ##-----------------CONCATENANDO LOS DATAFRAMES DE LAS ANOMALÍAS------------------------------##

    nombre = 'SinPotencia'

    df_corr_975 =  pd.concat([Anomal_df_975_h,  pd.DataFrame(df_Anomal_Temp_975['Anomalia_T']) ,pd.DataFrame(df_Anomal_WP_975['Anomalia_WP']) , pd.DataFrame(df_Anomal_FR_975['Anomalia_FR']),  pd.DataFrame(df_Anomal_PM_975['Anomalia_PM'])], axis=1)
    df_corr_350 =  pd.concat([Anomal_df_350_h,  pd.DataFrame(df_Anomal_Temp_350['Anomalia_T']) ,pd.DataFrame(df_Anomal_WP_350['Anomalia_WP']) , pd.DataFrame(df_Anomal_FR_350['Anomalia_FR']),  pd.DataFrame(df_Anomal_PM_350['Anomalia_PM'])], axis=1)
    df_corr_348 =  pd.concat([Anomal_df_348_h,  pd.DataFrame(df_Anomal_Temp_348['Anomalia_T']) ,pd.DataFrame(df_Anomal_WP_348['Anomalia_WP']) , pd.DataFrame(df_Anomal_FR_348['Anomalia_FR']),  pd.DataFrame(df_Anomal_PM_348['Anomalia_PM'])], axis=1)

    df_corr_975.to_csv(Path_save[0:45]+nombre+'_EXP_Anomalias_VariablesCondicionantes_975.csv', sep=',')
    df_corr_350.to_csv(Path_save[0:45]+nombre+ '_EXP_Anomalias_VariablesCondicionantes_350.csv', sep=',')
    df_corr_348.to_csv(Path_save[0:45]+nombre+'_EXP_Anomalias_VariablesCondicionantes_348.csv', sep=',')


    df_corr_975.columns = ['Irradiancia',  'Temp', u'Den VA', 'Reflectancia',  u'PM 2.5']
    df_corr_350.columns = ['Irradiancia', 'Temp', u'Den VA', 'Reflectancia',  u'PM 2.5']
    df_corr_348.columns = ['Irradiancia', 'Temp', u'Den VA', 'Reflectancia',  u'PM 2.5']

    corr_975 = df_corr_975.corr(method = 'pearson')
    corr_350 = df_corr_350.corr(method = 'pearson')
    corr_348 = df_corr_348.corr(method = 'pearson')


################################################################################
##--------------------------VALOR P DE LA CORRELACIÓN-------------------------##
################################################################################

def calculate_pvalues(df):
    df = df.dropna()._get_numeric_data()
    dfcols = pd.DataFrame(columns=df.columns)
    pvalues = dfcols.transpose().join(dfcols, how='outer')
    for r in df.columns:
        for c in df.columns:
            pvalues[r][c] = round(pearsonr(df[r], df[c])[1], 4)
    return pvalues

pval_975 = calculate_pvalues(df_corr_975)
pval_350 = calculate_pvalues(df_corr_350)
pval_348 = calculate_pvalues(df_corr_348)

pval_975.to_csv('/home/nacorreasa/Escritorio/pval_975.csv')
pval_350.to_csv('/home/nacorreasa/Escritorio/pval_350.csv')
pval_348.to_csv('/home/nacorreasa/Escritorio/pval_348.csv')

###################################################################################################
##----------------------------------------BARRA DE COLORES A USAR--------------------------------##
###################################################################################################

def newjet():
    """función para crear un nuevo color bar con cero en la mitad, modeificando el color bar jet"""
    jetcmap = cm.get_cmap("jet", 11)  #generate a jet map with 11 values
    jet_vals = jetcmap(np.arange(11)) #extract those values as an array
    jet_vals[5] = [1, 1, 1, 1]        #change the middle value
    newcmap = colors.LinearSegmentedColormap.from_list("newjet", jet_vals)
    return newcmap

my_cbar=newjet()

###################################################################################################
origin_cmap = cm.get_cmap("bwr", 14)
origin_vals = origin_cmap(np.arange(14))
withe = np.array([1,1,1,1])
for i in range(3):
    origin_vals = np.insert(origin_vals, 7,withe, axis=0)

colrs=origin_vals
levels=np.arange(-1,1.1,0.1)
name='coqueto'
cmap_new       = colors.LinearSegmentedColormap.from_list(name,colrs)
levels_nuevos  = np.linspace(np.min(levels),np.max(levels),255)
#levels_nuevos  = np.linspace(-0.75,np.max(levels),255)
norm_new       = colors.BoundaryNorm(boundaries=levels_nuevos, ncolors=256)

############################################################
## ----------------GRÁFICA DE CORRELACIÓN---------------- ##
############################################################

fig = plt.figure(figsize=[10, 5])

ax1 = fig.add_subplot(131)
cax1 = ax1.imshow(corr_350,interpolation = 'none', cmap=cmap_new, norm=norm_new, vmin=-1, vmax=1)
ticks = np.arange(0, len(df_corr_350.columns), 1)
ax1.set_xticks(ticks)
plt.xticks(rotation=90)
ax1.set_title(u'Correlación de las \n anomalías en el Oeste', fontsize = 10, fontproperties = prop_1)
ax1.set_yticks(ticks)
ax1.set_xticklabels(df_corr_350.columns, rotation = 45, fontsize = 7)
ax1.set_yticklabels(df_corr_350.columns, rotation = 45, fontsize = 7)

ax2 = fig.add_subplot(132)
cax2 = ax2.imshow(corr_975,interpolation = 'none', cmap=cmap_new, norm=norm_new, vmin=-1, vmax=1)
ticks = np.arange(0, len(df_corr_975.columns), 1)
ax2.set_xticks(ticks)
plt.xticks(rotation=90)
ax2.set_title(u'Correlación de las \n anomalías en el Centro-Oeste', fontsize = 10, fontproperties = prop_1)
ax2.set_yticks(ticks)
ax2.set_xticklabels(df_corr_975.columns, rotation = 45, fontsize = 7)
ax2.set_yticklabels(df_corr_975.columns, rotation = 45, fontsize = 7)

ax3 = fig.add_subplot(133)
cax3 = ax3.imshow(corr_348,interpolation = 'none', cmap=cmap_new, norm=norm_new, vmin=-1, vmax=1)
ticks = np.arange(0, len(df_corr_348.columns), 1)
ax3.set_xticks(ticks)
plt.xticks(rotation=90)
ax3.set_title(u'Correlación de las \n anomalías en el Este', fontsize = 10, fontproperties = prop_1)
ax3.set_yticks(ticks)
ax3.set_xticklabels(df_corr_348.columns, rotation = 45, fontsize = 7)
ax3.set_yticklabels(df_corr_348.columns, rotation = 45, fontsize = 7)

fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.30, 0.015, 0.40 ])
cbar = fig.colorbar(cax3, label = u"Coeficiente de Correlación", cax=cbar_ax)
cbar.set_ticks([-1, -0.75, -0.5,-0.25,  0.0,0.25, 0.5, 0.75, 1])
cbar.set_ticklabels([str(i) for i in [-1, -0.75, -0.5,-0.25,  0.0,0.25, 0.5, 0.75, 1]])
plt.subplots_adjust(wspace=0.38)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Corr_imshowP_'+nombre+'_Anomaly.pdf', format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Corr_imshowP_'+nombre+'_Anomaly.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

###########################################################################################
## -------OBTENER LOS VALORES Y VECTORES PROPIOS DE LAS MATRICES DE CORRELACIÓN--------- ##
###########################################################################################

eig_va_348,eig_ve_348=np.linalg.eig(corr_348)
eig_va_348=np.real(eig_va_348)
eig_ve_348=np.real(eig_ve_348)
sum_evals_348 = np.sum(eig_va_348)

var_exp_348 = (eig_va_348/sum_evals_348) * 100
var_exp_348_sorted = np.sort(var_exp_348)[::-1]
var_exp_348_index = np.argsort(var_exp_348)[::-1]
eig_ve_348 = eig_ve_348[:,var_exp_348_index]

vector_propio_348_1 = eig_ve_348[:,0]
vector_propio_348_2 = eig_ve_348[:,1]
vector_propio_348_3 = eig_ve_348[:,2]
np.save(Path_save[0:45]+'VectorProp_1_348', vector_propio_348_1)
np.save(Path_save[0:45]+'VectorProp_2_348', vector_propio_348_2)
np.save(Path_save[0:45]+'VectorProp_3_348', vector_propio_348_3)



eig_va_350,eig_ve_350=np.linalg.eig(corr_350)
eig_va_350=np.real(eig_va_350)
eig_ve_350=np.real(eig_ve_350)
sum_evals_350 = np.sum(eig_va_350)

var_exp_350 = (eig_va_350/sum_evals_350) * 100
var_exp_350_sorted = np.sort(var_exp_350)[::-1]
var_exp_350_index = np.argsort(var_exp_350)[::-1]
eig_ve_350 = eig_ve_350[:,var_exp_350_index]

vector_propio_350_1 = eig_ve_350[:,0]
vector_propio_350_2 = eig_ve_350[:,1]
vector_propio_350_3 = eig_ve_350[:,2]

np.save(Path_save[0:45]+'VectorProp_1_350', vector_propio_350_1)
np.save(Path_save[0:45]+'VectorProp_2_350', vector_propio_350_2)
np.save(Path_save[0:45]+'VectorProp_3_350', vector_propio_350_3)


eig_va_975,eig_ve_975=np.linalg.eig(corr_975)
eig_va_975=np.real(eig_va_975)
eig_ve_975=np.real(eig_ve_975)
sum_evals_975 = np.sum(eig_va_975)

var_exp_975 = (eig_va_975/sum_evals_975) * 100
var_exp_975_sorted = np.sort(var_exp_975)[::-1]
var_exp_975_index = np.argsort(var_exp_975)[::-1]
eig_ve_975 = eig_ve_975[:,var_exp_975_index]

vector_propio_975_1 = eig_ve_975[:,0]
vector_propio_975_2 = eig_ve_975[:,1]
vector_propio_975_3 = eig_ve_975[:,2]

np.save(Path_save[0:45]+'VectorProp_1_975', vector_propio_975_1)
np.save(Path_save[0:45]+'VectorProp_2_975', vector_propio_975_2)
np.save(Path_save[0:45]+'VectorProp_3_975', vector_propio_975_3)











#################################################################################################
##------------------REEMPLAZANDO POR CERO LAS CORRELACIONES NO SIGNIFICATIVAS------------------##
#################################################################################################
if Significancia == True:
    p_975 = np.array(pval_975)
    p_348 = np.array(pval_348)
    p_350 = np.array(pval_350)

    alpha = 0.05
    w_348 = np.where(p_348>alpha)
    w_350 = np.where(p_350>alpha)
    w_975 = np.where(p_975>alpha)

    if len(w_975[0]) >0:
        for i in range(len(w_975[0])):
            a = w_975[0][i]
            b = w_975[1][i]
            corr_975.iloc[a, b] = 0.0
    else:
        pass

    if len(w_350[0]) >0:
        for i in range(len(w_350[0])):
            a = w_350[0][i]
            b = w_350[1][i]
            corr_350.iloc[a, b] = 0.0
    else:
        pass

    if len(w_348[0]) >0:
        for i in range(len(w_348[0])):
            a = w_348[0][i]
            b = w_348[1][i]
            corr_348.iloc[a, b] = 0.0
    else:
        pass

    ############################################################
    ## -------------------GRÁFICA DE VALOR P----------------- ##
    ############################################################

    fig = plt.figure(figsize=[10, 8])
    ax1 = fig.add_subplot(131)
    cax1 = ax1.imshow(np.array(pval_975), cmap='viridis')
    ticks = np.arange(0, len(pval_975.columns), 1)
    ax1.set_xticks(ticks)
    plt.xticks(rotation=90)
    ax1.set_title('Valor P en TS', fontsize = 10, fontproperties = prop_1)
    ax1.set_yticks(ticks)
    ax1.set_xticklabels(pval_975.columns, rotation = 45, fontsize = 7)
    ax1.set_yticklabels(pval_975.columns, rotation = 45, fontsize = 7)
    for i in range(len(pval_975)):
        for j in range(len(pval_975)):
            text = ax1.text(j, i, round(float(np.array(pval_975)[i, j]), 3),
                           ha="center", va="center", color="w")

    ax2 = fig.add_subplot(132)
    cax2 = ax2.imshow(pval_350, cmap='viridis')
    ticks = np.arange(0, len(pval_350.columns), 1)
    ax2.set_xticks(ticks)
    plt.xticks(rotation=90)
    ax2.set_title('Valor P en CI', fontsize = 10, fontproperties = prop_1)
    ax2.set_yticks(ticks)
    ax2.set_xticklabels(pval_350.columns, rotation = 45, fontsize = 7)
    ax2.set_yticklabels(pval_350.columns, rotation = 45, fontsize = 7)
    for i in range(len(pval_350)):
        for j in range(len(pval_350)):
            text = ax2.text(j, i, round(float(np.array(pval_350)[i, j]), 3),
                           ha="center", va="center", color="w")

    ax3 = fig.add_subplot(133)
    cax3 = ax3.imshow(pval_348, cmap='viridis')
    ticks = np.arange(0, len(pval_348.columns), 1)
    ax3.set_xticks(ticks)
    plt.xticks(rotation=90)
    ax3.set_title('Valor P en CI', fontsize = 10, fontproperties = prop_1)
    ax3.set_yticks(ticks)
    ax3.set_xticklabels(pval_348.columns, rotation = 45, fontsize = 7)
    ax3.set_yticklabels(pval_348.columns, rotation = 45, fontsize = 7)
    for i in range(len(pval_348)):
        for j in range(len(pval_348)):
            text = ax3.text(j, i, round(float(np.array(pval_348)[i, j]), 3),
                           ha="center", va="center", color="w")


    fig.subplots_adjust(right=0.8)
    plt.subplots_adjust(wspace=0.3)
    plt.savefig('/home/nacorreasa/Escritorio/Figuras/Valor_P_Correlacion.png')
    plt.close('all')
    os.system('scp /home/nacorreasa/Escritorio/Figuras/Valor_P_Correlacion.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')



















################################################################################
## --------------------------------DATOS NORMALZADOS------------------------- ##
################################################################################

df_corr_975_norm = (df_corr_975 - df_corr_975.mean()) / (df_corr_975.max() - df_corr_975.min())
df_corr_350_norm = (df_corr_350 - df_corr_350.mean()) / (df_corr_350.max() - df_corr_350.min())
df_corr_348_norm = (df_corr_348 - df_corr_348.mean()) / (df_corr_348.max() - df_corr_348.min())

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.plot(df_corr_975_norm.index, df_corr_975_norm.Rad.values, color = 'r', label ='Rad')
ax1.plot(df_corr_975_norm.index, df_corr_975_norm.Pot.values, color = 'blue', label= 'Pot')
ax1.plot(df_corr_975_norm.index, df_corr_975_norm.Temp.values, color = 'orange', label= 'Temp')
ax1.plot(df_corr_975_norm.index, df_corr_975_norm.HR.values, color = 'g', label ='HR')
ax1.plot(df_corr_975_norm.index, df_corr_975_norm['Den WV'].values, color = 'black', label= 'Den WV')
ax1.plot(df_corr_975_norm.index, df_corr_975_norm.FR.values, color = 'c', label = 'FR')
ax1.plot(df_corr_975_norm.index, df_corr_975_norm['$\eta$'].values, color = 'pink', label = '$\eta$')
ax1.set_ylabel(u"Variables en TS", fontsize=14, fontproperties=prop_1)
ax1.set_title(u"Comparacion entre variables relacionadas en el tiempo", fontsize=17,  fontweight = "bold",  fontproperties = prop)
ax1.set_ylim(np.nanmin(df_corr_975_norm.values), np.nanmax(df_corr_975_norm.values) * 1.2)
ax1.set_xlim(df_corr_975_norm.index[0], df_corr_975_norm.index[-1])
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax1.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
ax1.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
ax1.tick_params(axis='x', which='minor')
ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
ax1.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
ax1.tick_params(axis='x', which='major', pad=15)
ax1.legend()

ax2 = fig.add_subplot(3, 1, 2)
ax2.plot(df_corr_350_norm.index, df_corr_350_norm.Rad.values, color = 'r', label ='Rad')
ax2.plot(df_corr_350_norm.index, df_corr_350_norm.Pot.values, color = 'blue', label= 'Pot')
ax2.plot(df_corr_350_norm.index, df_corr_350_norm.Temp.values, color = 'orange', label= 'Temp')
ax2.plot(df_corr_350_norm.index, df_corr_350_norm.HR.values, color = 'g', label ='HR')
ax2.plot(df_corr_350_norm.index, df_corr_350_norm['Den WV'].values, color = 'black', label= 'Den WV')
ax2.plot(df_corr_350_norm.index, df_corr_350_norm.FR.values, color = 'c', label = 'FR')
ax2.plot(df_corr_350_norm.index, df_corr_350_norm['$\eta$'].values, color = 'pink', label = '$\eta$')
ax2.set_ylabel(u"Variables en CI", fontsize=14, fontproperties=prop_1)
ax2.set_ylim(np.nanmin(df_corr_350_norm.values), np.nanmax(df_corr_350_norm.values) * 1.2)
ax2.set_xlim(df_corr_350_norm.index[0], df_corr_350_norm.index[-1])
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax2.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
ax2.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
ax2.tick_params(axis='x', which='minor')
ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
ax2.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
ax2.tick_params(axis='x', which='major', pad=15)
ax2.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.plot(df_corr_348_norm.index, df_corr_348_norm.Rad.values, color = 'r', label ='Rad')
ax3.plot(df_corr_348_norm.index, df_corr_348_norm.Pot.values, color = 'blue', label= 'Pot')
ax3.plot(df_corr_348_norm.index, df_corr_348_norm.Temp.values, color = 'orange', label= 'Temp')
ax3.plot(df_corr_348_norm.index, df_corr_348_norm.HR.values, color = 'g', label ='HR')
ax3.plot(df_corr_348_norm.index, df_corr_348_norm['Den WV'].values, color = 'black', label= 'Den WV')
ax3.plot(df_corr_348_norm.index, df_corr_348_norm.FR.values, color = 'c', label = 'FR')
ax3.plot(df_corr_348_norm.index, df_corr_348_norm['$\eta$'].values, color = 'pink', label = '$\eta$')
ax3.set_ylabel(u"Variables en JV", fontsize=14, fontproperties=prop_1)
ax3.set_ylim(np.nanmin(df_corr_348_norm.values), np.nanmax(df_corr_348_norm.values) * 1.2)
ax3.set_xlim(df_corr_348_norm.index[0], df_corr_348_norm.index[-1])
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax3.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
ax3.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
ax3.tick_params(axis='x', which='minor')
ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
ax3.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
ax3.tick_params(axis='x', which='major', pad=15)
ax3.legend()

plt.savefig('/home/nacorreasa/Escritorio/Figuras/Corr_variables_plot.png')
#plt.show()
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Corr_variables_plot.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

################################################################################
## ----------------ANOMALÍAS DE LA RADIACIÓN Y LA TEMPERATURA---------------- ##
################################################################################

new_idx = np.arange(6, 18, 1)

df_All_P975 = df_All_P975.between_time('06:00', '17:00')              ##--> Seleccionar solo los datos de horas del dia
df_All_P350 = df_All_P350.between_time('06:00', '17:00')              ##--> Seleccionar solo los datos de horas del dia
df_All_P348 = df_All_P348.between_time('06:00', '17:00')              ##--> Seleccionar solo los datos de horas del dia


df_All_P975_Mean  = df_All_P975.groupby(by=[df_All_P975.index.hour]).mean()
df_All_P975_Mean  = df_All_P975_Mean.reindex(new_idx)
df_All_P975_Std  = df_All_P975.groupby(by=[df_All_P975.index.hour]).std()
df_All_P975_Std  = df_All_P975_Std.reindex(new_idx)
df_All_P975_Mean  = df_All_P975_Mean[['radiacion', 'T']]
df_All_P975_Std  = df_All_P975_Std[['radiacion', 'T']]
df_anomal_P975 = df_All_P975[['radiacion', 'T']]
#df_anomal_P975 = df_All_P975['T']
df_anomal_P975 = pd.DataFrame(df_anomal_P975)
df_anomal_P975 = df_anomal_P975[df_anomal_P975['T']>0]
df_anomal_P975['hour'] = df_anomal_P975.index.hour

Mean_T_P975 = []
Std_T_P975 = []
Mean_Rad_P975 = []
Std_Rad_P975 = []
for i in range(len(df_anomal_P975)):
    for j in range(len(df_All_P975_Mean)):
        if df_anomal_P975['hour'][i] == df_All_P975_Mean.index[j]:
            Mean_T_P975.append(df_All_P975_Mean['T'].values[j])
            Std_T_P975.append(df_All_P975_Std['T'].values[j])
            Mean_Rad_P975.append(df_All_P975_Mean['radiacion'].values[j])
            Std_Rad_P975.append(df_All_P975_Std['radiacion'].values[j])
        else:
            pass

df_anomal_P975['Mean_T'] = Mean_T_P975
df_anomal_P975['Std_T'] = Std_T_P975
df_anomal_P975['Anomal_T'] = (df_anomal_P975['T']-df_anomal_P975['Mean_T'])/df_anomal_P975['Std_T']

df_anomal_P975['Mean_Rad'] = Mean_Rad_P975
df_anomal_P975['Std_Rad'] = Std_Rad_P975
df_anomal_P975['Anomal_Rad'] = (df_anomal_P975['radiacion']-df_anomal_P975['Mean_Rad'])/df_anomal_P975['Std_Rad']


df_All_P350_Mean  = df_All_P350.groupby(by=[df_All_P350.index.hour]).mean()
df_All_P350_Mean  = df_All_P350_Mean.reindex(new_idx)
df_All_P350_Std  = df_All_P350.groupby(by=[df_All_P350.index.hour]).std()
df_All_P350_Std  = df_All_P350_Std.reindex(new_idx)
df_All_P350_Mean  = df_All_P350_Mean[['radiacion', 'T']]
df_All_P350_Std  = df_All_P350_Std[['radiacion', 'T']]
df_anomal_P350 = df_All_P350[['radiacion', 'T']]
#df_anomal_P350 = df_All_P350['T']
df_anomal_P350 = pd.DataFrame(df_anomal_P350)
df_anomal_P350 = df_anomal_P350[df_anomal_P350['T']>0]
df_anomal_P350['hour'] = df_anomal_P350.index.hour

Mean_T_P350 = []
Std_T_P350 = []
Mean_Rad_P350 = []
Std_Rad_P350 = []
for i in range(len(df_anomal_P350)):
    for j in range(len(df_All_P350_Mean)):
        if df_anomal_P350['hour'][i] == df_All_P350_Mean.index[j]:
            Mean_T_P350.append(df_All_P350_Mean['T'].values[j])
            Std_T_P350.append(df_All_P350_Std['T'].values[j])
            Mean_Rad_P350.append(df_All_P350_Mean['radiacion'].values[j])
            Std_Rad_P350.append(df_All_P350_Std['radiacion'].values[j])
        else:
            pass

df_anomal_P350['Mean_T'] = Mean_T_P350
df_anomal_P350['Std_T'] = Std_T_P350
df_anomal_P350['Anomal_T'] = (df_anomal_P350['T']-df_anomal_P350['Mean_T'])/df_anomal_P350['Std_T']

df_anomal_P350['Mean_Rad'] = Mean_Rad_P350
df_anomal_P350['Std_Rad'] = Std_Rad_P350
df_anomal_P350['Anomal_Rad'] = (df_anomal_P350['radiacion']-df_anomal_P350['Mean_Rad'])/df_anomal_P350['Std_Rad']


df_All_P348_Mean  = df_All_P348.groupby(by=[df_All_P348.index.hour]).mean()
df_All_P348_Mean  = df_All_P348_Mean.reindex(new_idx)
df_All_P348_Std  = df_All_P348.groupby(by=[df_All_P348.index.hour]).std()
df_All_P348_Std  = df_All_P348_Std.reindex(new_idx)
df_All_P348_Mean  = df_All_P348_Mean[['radiacion', 'T']]
df_All_P348_Std  = df_All_P348_Std[['radiacion', 'T']]
df_anomal_P348 = df_All_P348[['radiacion', 'T']]
#df_anomal_P348 = df_All_P348['T']
df_anomal_P348 = pd.DataFrame(df_anomal_P348)
df_anomal_P348 = df_anomal_P348[df_anomal_P348['T']>0]
df_anomal_P348['hour'] = df_anomal_P348.index.hour

Mean_T_P348 = []
Std_T_P348 = []
Mean_Rad_P348 = []
Std_Rad_P348 = []
for i in range(len(df_anomal_P348)):
    for j in range(len(df_All_P348_Mean)):
        if df_anomal_P348['hour'][i] == df_All_P348_Mean.index[j]:
            Mean_T_P348.append(df_All_P348_Mean['T'].values[j])
            Std_T_P348.append(df_All_P348_Std['T'].values[j])
            Mean_Rad_P348.append(df_All_P348_Mean['radiacion'].values[j])
            Std_Rad_P348.append(df_All_P348_Std['radiacion'].values[j])
        else:
            pass

df_anomal_P348['Mean_T'] = Mean_T_P348
df_anomal_P348['Std_T'] = Std_T_P348
df_anomal_P348['Anomal_T'] = (df_anomal_P348['T']-df_anomal_P348['Mean_T'])/df_anomal_P348['Std_T']

df_anomal_P348['Mean_Rad'] = Mean_Rad_P348
df_anomal_P348['Std_Rad'] = Std_Rad_P348
df_anomal_P348['Anomal_Rad'] = (df_anomal_P348['radiacion']-df_anomal_P348['Mean_Rad'])/df_anomal_P348['Std_Rad']

df_anomal_P975.index = pd.to_datetime(df_anomal_P975.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_anomal_P350.index = pd.to_datetime(df_anomal_P350.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_anomal_P348.index = pd.to_datetime(df_anomal_P348.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

## ----------------CD ANOMALÍAS DE LA RADIACIÓN Y LA TEMPERATURA---------------- ##

new_idx = np.arange(6, 18, 1)

df_anomal_P975_CD  = df_anomal_P975.groupby(by=[df_anomal_P975.index.hour]).mean()
df_anomal_P975_CD  = df_anomal_P975_CD.reindex(new_idx)

df_anomal_P350_CD  = df_anomal_P350.groupby(by=[df_anomal_P350.index.hour]).mean()
df_anomal_P350_CD  = df_anomal_P350_CD.reindex(new_idx)

df_anomal_P348_CD  = df_anomal_P348.groupby(by=[df_anomal_P348.index.hour]).mean()
df_anomal_P348_CD  = df_anomal_P348_CD.reindex(new_idx)

## ----------------CD DE LA RADIACIÓN Y LA TEMPERATURA---------------- ##

df_All_P975_CD  = df_All_P975.groupby(by=[df_All_P975.index.hour]).mean()
df_All_P975_CD  = df_All_P975_CD.reindex(new_idx)

df_All_P350_CD  = df_All_P350.groupby(by=[df_All_P350.index.hour]).mean()
df_All_P350_CD  = df_All_P350_CD.reindex(new_idx)

df_All_P348_CD  = df_All_P348.groupby(by=[df_All_P348.index.hour]).mean()
df_All_P348_CD  = df_All_P348_CD.reindex(new_idx)


## ----------------GRÁFICA DE LAS ANOMALÍAS DE LA RADIACIÓN Y LA TEMPERATURA---------------- ##

def two_scales(ax1, time, data1, data2, c1, c2, subplot_title):
    ax2 = ax1.twinx()
    ax1.plot(time, data1, color=c1)
    ax1.set_xlabel('Tiempo', fontproperties = prop_1)
    ax1.set_ylabel(r"Radiacion $[W/m^{2}]$", fontproperties = prop_1)
    ax2.plot(time, data2, color=c2)
    ax2.set_ylabel('Temperatura [°C]', fontproperties = prop_1)
    ax1.set_title(subplot_title, fontproperties = prop_2)
    ax1.set_xticklabels(time, rotation = 45, fontsize = 7)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    return ax1, ax2

t975 = df_anomal_P975.index
Rad975 = df_anomal_P975['Anomal_Rad']
Temp975 = df_anomal_P975['Anomal_T']

t350 = df_anomal_P350.index
Rad350 = df_anomal_P350['Anomal_Rad']
Temp350 = df_anomal_P350['Anomal_T']

t348 = df_anomal_P348.index
Rad348 = df_anomal_P348['Anomal_Rad']
Temp348 = df_anomal_P348['Anomal_T']

# Create axes
fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(10,4))
ax1, ax1a = two_scales(ax1, t975, Rad975, Temp975, 'gold', 'limegreen', u'Anomalías TS')
ax2, ax2a = two_scales(ax2, t350, Rad350, Temp350, 'gold', 'limegreen', u'Anomalías CI')
ax3, ax3a = two_scales(ax3, t348, Rad348, Temp348, 'gold', 'limegreen', u'Anomalías JV')

# Change color of each axis
def color_y_axis(ax, color):
    """Color your axes."""
    for t in ax.get_yticklabels():
        t.set_color(color)

color_y_axis(ax1, 'gold')
color_y_axis(ax1a, 'limegreen')
color_y_axis(ax2, 'gold')
color_y_axis(ax2a, 'limegreen')
color_y_axis(ax3, 'gold')
color_y_axis(ax3a, 'limegreen')

plt.tight_layout()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Serie_Anomalias.png')
plt.show()

## ----------------GRÁFICA CD DE LAS ANOMALÍAS DE LA RADIACIÓN Y LA TEMPERATURA---------------- ##

def two_scales_CD(ax1, time, data1, data2, c1, c2, subplot_title):
    x_pos = np.arange(len(time))

    ax2 = ax1.twinx()
    ax1.plot(x_pos, data1, color=c1)
    #ax1.bar(x_pos, data1, color=c1, align='center', alpha=0.5)
    ax1.set_xlabel(u'Horas del dia', fontproperties = prop_1)
    ax1.set_ylabel(r"Radiacion $[W/m^{2}]$", fontproperties = prop_1, colo)
    ax2.plot(x_pos, data2, color=c2)
    #ax2.bar(x_pos, data2, color=c2, align='center', alpha=0.5)
    ax2.set_ylabel('Temperatura [°C]', fontproperties = prop_1)
    ax1.set_title(subplot_title, fontproperties = prop_2)
    ax1.set_xticks(np.arange(0, 12, 1))
    ax1.set_xticklabels(time.values, rotation = 20)
    #ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    return ax1, ax2

t975_CD = df_anomal_P975_CD.index
Rad975_CD = df_anomal_P975_CD['Anomal_Rad']
Temp975_CD = df_anomal_P975_CD['Anomal_T']

t350_CD = df_anomal_P350_CD.index
Rad350_CD = df_anomal_P350_CD['Anomal_Rad']
Temp350_CD = df_anomal_P350_CD['Anomal_T']

t348_CD = df_anomal_P348_CD.index
Rad348_CD = df_anomal_P348_CD['Anomal_Rad']
Temp348_CD = df_anomal_P348_CD['Anomal_T']

fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(10,4))
ax1, ax1a = two_scales_CD(ax1, t975_CD, Rad975_CD , Temp975_CD , 'gold', 'limegreen', u'CD Anomalías TS')
ax2, ax2a = two_scales_CD(ax2, t350_CD, Rad350_CD , Temp350_CD , 'gold', 'limegreen', u'CD Anomalías CI')
ax3, ax3a = two_scales_CD(ax3, t348_CD, Rad348_CD , Temp348_CD , 'gold', 'limegreen', u'CD Anomalías JV')

def color_y_axis(ax, color):
    """Color your axes."""
    for t in ax.get_yticklabels():
        t.set_color(color)

color_y_axis(ax1, 'gold')
color_y_axis(ax1a, 'limegreen')
color_y_axis(ax2, 'gold')
color_y_axis(ax2a, 'limegreen')
color_y_axis(ax3, 'gold')
color_y_axis(ax3a, 'limegreen')

plt.tight_layout()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_Anomalias.png')
plt.show()

## ----------------GRÁFICA CD  DE LA RADIACIÓN Y LA TEMPERATURA---------------- ##

def two_scales_CD(ax1, time, data1, data2, c1, c2, subplot_title):
    x_pos = np.arange(len(time))

    ax2 = ax1.twinx()
    ax1.bar(x_pos, data1, color=c1, align='center', alpha=0.5)
    ax1.set_xlabel(u'Horas del dia', fontproperties = prop_1)
    ax1.set_ylabel(r"Radiacion $[W/m^{2}]$", fontproperties = prop_1, color = c1)
    ax2.bar(x_pos+0.75, data2, color=c2, align='center', alpha=0.5)
    ax2.set_ylabel('Temperatura [°C]', fontproperties = prop_1, color = c2)
    ax1.set_title(subplot_title, fontproperties = prop_2)
    ax1.set_xticks(np.arange(0, 12, 1))
    ax1.set_xticklabels(time.values, rotation = 20)
    #ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    return ax1, ax2

t975_CD = df_All_P975_CD.index
Rad975_CD = df_All_P975_CD['radiacion']
Temp975_CD = df_All_P975_CD['T']

t350_CD = df_All_P350_CD.index
Rad350_CD = df_All_P350_CD['radiacion']
Temp350_CD = df_All_P350_CD['T']

t348_CD = df_All_P350_CD.index
Rad348_CD = df_All_P350_CD['radiacion']
Temp348_CD = df_All_P350_CD['T']

fig, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=(10,4))
ax1, ax1a = two_scales_CD(ax1, t975_CD, Rad975_CD , Temp975_CD , 'gold', 'limegreen', u'CD Rad_Temp TS')
ax2, ax2a = two_scales_CD(ax2, t350_CD, Rad350_CD , Temp350_CD , 'gold', 'limegreen', u'CD Rad_Temp  CI')
ax3, ax3a = two_scales_CD(ax3, t348_CD, Rad348_CD , Temp348_CD , 'gold', 'limegreen', u'CD Rad_Temp  JV')

def color_y_axis(ax, color):
    """Color your axes."""
    for t in ax.get_yticklabels():
        t.set_color(color)

color_y_axis(ax1, 'gold')
color_y_axis(ax1a, 'limegreen')
color_y_axis(ax2, 'gold')
color_y_axis(ax2a, 'limegreen')
color_y_axis(ax3, 'gold')
color_y_axis(ax3a, 'limegreen')

plt.tight_layout()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_Rad_Temp.png')
plt.show()
