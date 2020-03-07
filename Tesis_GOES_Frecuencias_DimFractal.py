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
import matplotlib.cm as cm
import os

Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
Horizonte = 'Anio'    ##-->'Anio' para los datos del 2018 y 2019y 'EXP' para los datos a partir del experimento.

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
'Código para la derteminacion de la frecuencia y a demas de la dimension fractal (con el fin de revelar relaciones'
'entre ambos conceptos). En la entrada anteriore se define el horizonte de tiempo con el cual se quiere trabajar.'
'Además se obtiene el scatter q relaciona las reflectancias con las anomalías de la radiación.'

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

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

Anomal_df_348_h = Anomal_df_348_h.drop(['Radiacion_Med', 'radiacion',], axis=1)
Anomal_df_350_h = Anomal_df_350_h.drop(['Radiacion_Med', 'radiacion',], axis=1)
Anomal_df_975_h = Anomal_df_975_h.drop(['Radiacion_Med', 'radiacion',], axis=1)

Anomal_df_348_h = Anomal_df_348_h.loc[~Anomal_df_348_h.index.duplicated(keep='first')]
Anomal_df_350_h = Anomal_df_350_h.loc[~Anomal_df_350_h.index.duplicated(keep='first')]
Anomal_df_975_h = Anomal_df_975_h.loc[~Anomal_df_975_h.index.duplicated(keep='first')]

################################################################################################
## -------------------------------UMBRALES DE LAS REFLECTANCIAS------------------------------ ##
################################################################################################

Umbral_up_348   = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Nuba.csv',  sep=',',  header = None)
Umbral_down_348 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_348_Desp.csv',  sep=',',  header = None)
Umbral_up_348.columns=['Hora', 'Umbral']
Umbral_up_348.index = Umbral_up_348['Hora']
Umbral_up_348 = Umbral_up_348.drop(['Hora'], axis=1)
Umbral_down_348.columns=['Hora', 'Umbral']
Umbral_down_348.index = Umbral_down_348['Hora']
Umbral_down_348 = Umbral_down_348.drop(['Hora'], axis=1)

Umbral_up_350   = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Nuba.csv',  sep=',',  header = None)
Umbral_down_350 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_350_Desp.csv',  sep=',',  header = None)
Umbral_up_350.columns=['Hora', 'Umbral']
Umbral_up_350.index = Umbral_up_350['Hora']
Umbral_up_350 = Umbral_up_350.drop(['Hora'], axis=1)
Umbral_down_350.columns=['Hora', 'Umbral']
Umbral_down_350.index = Umbral_down_350['Hora']
Umbral_down_350 = Umbral_down_350.drop(['Hora'], axis=1)

Umbral_up_975   = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Nuba.csv',  sep=',',  header = None)
Umbral_down_975 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Desp.csv',  sep=',',  header = None)
Umbral_up_975.columns=['Hora', 'Umbral']
Umbral_up_975.index = Umbral_up_975['Hora']
Umbral_up_975 = Umbral_up_975.drop(['Hora'], axis=1)
Umbral_down_975.columns=['Hora', 'Umbral']
Umbral_down_975.index = Umbral_down_975['Hora']
Umbral_down_975 = Umbral_down_975.drop(['Hora'], axis=1)

##------------------------------------------------UMBRALES DE TODA LA REGIÓN------------------------------------------------------------##
'Se obtiene el dataframe promedio de umbrales para obtener los umbrales horarios y ser usados cuando se tome la región entera. '
df_concat_down = pd.concat((Umbral_down_348, Umbral_down_350, Umbral_down_975))
Umbral_down_Prom = df_concat_down.groupby(df_concat_down.index).mean()

df_concat_up = pd.concat((Umbral_up_348, Umbral_up_350, Umbral_up_975))
Umbral_up_Prom = df_concat_up.groupby(df_concat_up.index).mean()

####################################################################################
## ----------------LECTURA DE LOS DATOS DE GOES CH2 MALLA GENERAL---------------- ##
####################################################################################

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')

df_fh  = pd.DataFrame()
df_fh ['fecha_hora'] = fechas_horas
df_fh['fecha_hora'] = pd.to_datetime(df_fh['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_fh.index = df_fh['fecha_hora']
w = pd.date_range(df_fh.index.min(), df_fh.index.max()).difference(df_fh.index)
df_fh = df_fh[df_fh.index.hour != 5]

#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
Rad_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix350_Anio.npy')
Rad_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix348_Anio.npy')
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

#################################################################################################
##-------------------ENMASCARANDO LOS DATOS MENORES AL UMBRAL NUBLADO--------------------------##
#################################################################################################

Rad_nuba_348 = []
FH_Nuba_348 = []
for i in range(len(Rad_df_348)):
    for j in range(len(Umbral_up_348.index)):
        if (Rad_df_348.index[i].hour == Umbral_up_348.index[j]) & (Rad_df_348.Radiacias.values[i] >= Umbral_up_348.values[j]):
            Rad_nuba_348.append(Rad_df_348.Radiacias.values[i])
            FH_Nuba_348.append(Rad_df_348.index[i])
        elif (Rad_df_348.index[i].hour == Umbral_up_348.index[j]) & (Rad_df_348.Radiacias.values[i] < Umbral_up_348.values[j]):
            Rad_nuba_348.append(np.nan)
            FH_Nuba_348.append(Rad_df_348.index[i])

df_348_nuba = pd.DataFrame()
df_348_nuba['Radiacias'] = Rad_nuba_348
df_348_nuba['Fecha_Hora'] = FH_Nuba_348
df_348_nuba['Fecha_Hora'] = pd.to_datetime(df_348_nuba['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_348_nuba.index = df_348_nuba['Fecha_Hora']
df_348_nuba = df_348_nuba.drop(['Fecha_Hora'], axis=1)



Rad_nuba_350 = []
FH_Nuba_350 = []
for i in range(len(Rad_df_350)):
    for j in range(len(Umbral_up_350.index)):
        if (Rad_df_350.index[i].hour == Umbral_up_350.index[j]) & (Rad_df_350.Radiacias.values[i] >= Umbral_up_350.values[j]):
            Rad_nuba_350.append(Rad_df_350.Radiacias.values[i])
            FH_Nuba_350.append(Rad_df_350.index[i])
        elif (Rad_df_350.index[i].hour == Umbral_up_350.index[j]) & (Rad_df_350.Radiacias.values[i] < Umbral_up_350.values[j]):
            Rad_nuba_350.append(np.nan)
            FH_Nuba_350.append(Rad_df_350.index[i])

df_350_nuba = pd.DataFrame()
df_350_nuba['Radiacias'] = Rad_nuba_350
df_350_nuba['Fecha_Hora'] = FH_Nuba_350
df_350_nuba['Fecha_Hora'] = pd.to_datetime(df_350_nuba['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_350_nuba.index = df_350_nuba['Fecha_Hora']
df_350_nuba = df_350_nuba.drop(['Fecha_Hora'], axis=1)


Rad_nuba_975 = []
FH_Nuba_975 = []
for i in range(len(Rad_df_975)):
    for j in range(len(Umbral_up_975.index)):
        if (Rad_df_975.index[i].hour == Umbral_up_975.index[j]) & (Rad_df_975.Radiacias.values[i] >= Umbral_up_975.values[j]):
            Rad_nuba_975.append(Rad_df_975.Radiacias.values[i])
            FH_Nuba_975.append(Rad_df_975.index[i])
        elif (Rad_df_975.index[i].hour == Umbral_up_975.index[j]) & (Rad_df_975.Radiacias.values[i] < Umbral_up_975.values[j]):
            Rad_nuba_975.append(np.nan)
            FH_Nuba_975.append(Rad_df_975.index[i])

df_975_nuba = pd.DataFrame()
df_975_nuba['Radiacias'] = Rad_nuba_975
df_975_nuba['Fecha_Hora'] = FH_Nuba_975
df_975_nuba['Fecha_Hora'] = pd.to_datetime(df_975_nuba['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_975_nuba.index = df_975_nuba['Fecha_Hora']
df_975_nuba = df_975_nuba.drop(['Fecha_Hora'], axis=1)


def time_mod(time, delta, epoch=None):
    if epoch is None:
        epoch = datetime.datetime(1970, 1, 1, tzinfo=time.tzinfo)
    return (time - epoch) % delta

def time_round(time, delta, epoch=None):
    mod = time_mod(time, delta, epoch)
    if mod < (delta / 2):
       return time - mod
    return time + (delta - mod)


df_348_nuba.index = [time_round(df_348_nuba.index[i], datetime.timedelta(minutes=15)) for i in range(len(df_348_nuba.index))]
df_350_nuba.index = [time_round(df_350_nuba.index[i], datetime.timedelta(minutes=15)) for i in range(len(df_350_nuba.index))]
df_975_nuba.index = [time_round(df_975_nuba.index[i], datetime.timedelta(minutes=15)) for i in range(len(df_975_nuba.index))]

df_348_nuba =  df_348_nuba.loc[~df_348_nuba.index.duplicated(keep='first')]
df_350_nuba =  df_350_nuba.loc[~df_350_nuba.index.duplicated(keep='first')]
df_975_nuba =  df_975_nuba.loc[~df_975_nuba.index.duplicated(keep='first')]

df_975_nuba.to_csv(Path_save + Horizonte+'df_Nublados_pix975.csv')
df_350_nuba.to_csv(Path_save + Horizonte+'df_Nublados_pix350.csv')
df_348_nuba.to_csv(Path_save + Horizonte+'df_Nublados_pix348.csv')

#########################################################################
## -------------------ENMASCARAMIENTO DE LAS IMAGENES------------------##
#########################################################################

fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')
lat = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
lon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')

'Para este caso se tomarán solo los datos comprendidos entre las 6:00 y antes de las 18:00.'
'Esta es la razón del try except IndexError, para el ajuste de los datos y de las fechas. Se'
'toma cada paso de tiempo del array Rad para enmascararlo.'

Rad = Rad[1:-3, :, :]
fechas_horas = fechas_horas[1:-3]
fechas_horas =  pd.to_datetime(fechas_horas , format="%Y-%m-%d %H:%M", errors='coerce')
##------------------------------------------------------------------------------------##
Rad_bina = []
Rad_mask = []

fechas_horas_new = []
for i in range (len(fechas_horas)):
    try:
        rad = Rad[i, :, :]
        umbral = Umbral_up_Prom[Umbral_up_Prom.Umbral.index == fechas_horas[i].hour].values[0][0]
        radm = np.ma.masked_where(rad < umbral, rad)
        radbi = (rad > umbral).astype(int)
        Rad_bina.append(radbi)
        Rad_mask.append(radm)
        fechas_horas_new.append(fechas_horas[i])
    except IndexError:
        pass

Rad_bina = np.array(Rad_bina)
Rad_mask = np.array(Rad_mask)

#########################################################################
## ---------------DETERMINACIÓN DE LA DIMENSION FRACTAL----------------##
#########################################################################

def fractal_dimension(Z):
    assert(len(Z.shape) == 2)

    def boxcount(Z, k):
        S = np.add.reduceat(
            np.add.reduceat(Z, np.arange(0, Z.shape[0], k), axis=0),
                               np.arange(0, Z.shape[1], k), axis=1)
        return len(np.where((S > 0) & (S < k*k))[0])

    p = min(Z.shape)
    n = 2**np.floor(np.log(p)/np.log(2))
    n = int(np.log(n)/np.log(2))
    sizes = 2**np.arange(n, 1, -1)
    counts = []
    for size in sizes:
        counts.append(boxcount(Z, size))
    coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)
    return -coeffs[0]

Fractal_Dimension = []
for i in range(0, Rad_bina.shape[0]):
    Fractal_Dimension.append(fractal_dimension(Rad_bina[i, :, :]))

df_Fractal = pd.DataFrame(Fractal_Dimension, index = fechas_horas_new, columns = ['Dim_Fractal'])
df_Fractal = df_Fractal [df_Fractal ['Dim_Fractal']>1]

df_Fractal.index = [time_round(df_Fractal.index[i], datetime.timedelta(minutes=15)) for i in range(len(df_Fractal.index))]
df_Fractal =  df_Fractal.loc[~df_Fractal.index.duplicated(keep='first')]

df_Fractal_CD = df_Fractal.groupby(by=[df_Fractal.index.hour]).median()
df_Fractal_Month =  df_Fractal.groupby(by=[df_Fractal.index.month]).median()

#########################################################################################################
##---------------------------------OBTENIENDO EL DATAFRAME DE CADA MES --------------------------------##
#########################################################################################################
df_concat_nuba = pd.concat((df_348_nuba, df_350_nuba, df_975_nuba))
df_nuba_Prom = df_concat_nuba.groupby(df_concat_nuba.index).mean()

df_concat_Anomal = pd.concat((Anomal_df_348, Anomal_df_350, Anomal_df_975))
df_Anomal_Prom = df_concat_Anomal.groupby(df_concat_Anomal.index).mean()
df_Total =  pd.concat([df_Anomal_Prom, df_nuba_Prom, df_Fractal], axis=1)

x_month = np.arange(1, 13)

##--------------------------------GRAFICA  DIM FRACTAL MENSUAL------------------------------##
#Month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
Month = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

df_Fractal_Month_MintoMax = df_Fractal_Month.sort_values('Dim_Fractal', axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
colors = cm.plasma_r(np.linspace(0, 1, len(df_Fractal_Month)))
df_colors = pd.DataFrame(np.nan, columns =["Color"], index =np.arange(12))
df_colors = df_colors.astype(object)
for i in range(len(colors)):
    df_colors.at[i, 'Color'] = colors[i].tolist()
df_colors['Dim_Fractal'] = df_Fractal_Month_MintoMax['Dim_Fractal'].values
df_colors.index = df_Fractal_Month_MintoMax.index
mycmap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)

plt.close('all')
fig = plt.figure(figsize=(30,10))
for i in range(1, 13):
    ax = fig.add_subplot(2, 6, i)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.scatter(df_Total['Anomalia'][df_Total.index.month ==i].values, df_Total['Radiacias'][df_Total.index.month ==i].values, s=80, c= df_colors['Color'][i],  alpha=0.5, marker = ".")
    ax.set_ylabel(u"Reflectance factor", fontsize=12, fontproperties=prop_1)
    ax.set_xlabel(u"Irradiance anomaly $[W/m^{2}]$", fontsize=12, fontproperties=prop_1)
    ax.set_ylim(0, 100)
    ax.set_xlim(df_Anomal_Prom['Anomalia'].min()-1, df_Anomal_Prom['Anomalia'].max()+1)
    ax.set_title(Month[i-1], fontsize=20, fontproperties=prop)
    ax.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
xy = range(20)
z = xy
fake_ax = fig.add_axes([-1, 1,-1,1])
sc = plt.scatter(xy, xy, c=z,  vmin=df_colors['Dim_Fractal'].min(), vmax=df_colors['Dim_Fractal'].max(), s=35, cmap=mycmap)
#cbar2_ax = fig.add_axes([0.125, 0.99, 0.78, 0.015])
cbar2_ax = fig.add_axes([0.93, 0.15, 0.015, 0.75 ])
cbar = fig.colorbar(sc, cax=cbar2_ax, orientation='vertical', format="%.2f")
cbar.set_label('Monthly fractal dimension', fontsize=20, fontproperties=prop)
cbar.outline.set_edgecolor('gray')
plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterRefAnomalRad.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterRefAnomalRad.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##--------------------------------GRAFICA  DIM FRACTAL INTANTANEA------------------------------##

plt.close('all')
fig = plt.figure(figsize=(30,10))
for i in range(1, 13):
    ax = fig.add_subplot(2, 6, i)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    sc = ax.scatter(df_Total['Anomalia'][df_Total.index.month ==i].values, df_Total['Radiacias'][df_Total.index.month ==i].values, s=80, c= df_Total['Dim_Fractal'][df_Total.index.month ==i].values, cmap='viridis_r',  alpha=1, marker = ".")
    ax.set_ylabel(u"Reflectance factor", fontsize=12, fontproperties=prop_1)
    ax.set_xlabel(u"Irradiance anomaly $[W/m^{2}]$", fontsize=12, fontproperties=prop_1)
    ax.set_ylim(0, 100)
    ax.set_xlim(df_Anomal_Prom['Anomalia'].min()-1, df_Anomal_Prom['Anomalia'].max()+1)
    ax.set_title(Month[i-1], fontsize=20, fontproperties=prop)
    ax.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
cbar2_ax = fig.add_axes([0.93, 0.15, 0.015, 0.75 ])
cbar = fig.colorbar(sc, cax=cbar2_ax, orientation='vertical', format="%.2f")
cbar.set_label('Fractal dimension', fontsize=20, fontproperties=prop)
cbar.outline.set_edgecolor('gray')
plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterRefAnomalRad_INSTANT.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterRefAnomalRad_INSTANT.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##--------------------------------GRAFICA  DIM FRACTAL INTANTANEA HORARIA MENSUAL------------------------------##
df_Total = df_Total[df_Total['Radiacias']>0]

Hour = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
plt.close('all')
for j in range(len(Hour)):
    fig = plt.figure(figsize=(30,10))
    for i in range(1, 13):
        ax = fig.add_subplot(2, 6, i)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        sc = ax.scatter(df_Total['Anomalia'][(df_Total.index.month ==i)&(df_Total.index.hour ==Hour[j])].values,
         df_Total['Radiacias'][(df_Total.index.month ==i)&(df_Total.index.hour ==Hour[j])].values, s=80,
          c= df_Total['Dim_Fractal'][(df_Total.index.month ==i)&(df_Total.index.hour ==Hour[j])], cmap='viridis_r',  alpha=1, marker = ".")
        ax.set_ylabel(u"Reflectance factor", fontsize=12, fontproperties=prop_1)
        ax.set_xlabel(u"Irradiance anomaly $[W/m^{2}]$", fontsize=12, fontproperties=prop_1)
        ax.set_ylim(0, 100)
        ax.set_xlim(df_Anomal_Prom['Anomalia'].min()-1, df_Anomal_Prom['Anomalia'].max()+1)
        ax.set_title(Month[i-1], fontsize=20, fontproperties=prop)
        ax.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
    cbar2_ax = fig.add_axes([0.93, 0.15, 0.015, 0.75 ])
    cbar = fig.colorbar(sc, cax=cbar2_ax, orientation='vertical', format="%.2f")
    cbar.set_label('Fractal dimension', fontsize=20, fontproperties=prop)
    cbar.outline.set_edgecolor('gray')
    plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.25)
    plt.savefig('/home/nacorreasa/Escritorio/Figuras/ScatterRefAnomalRad_HORA'+str(Hour[j])+'.pdf', format='pdf', transparent=True)
    os.system('scp /home/nacorreasa/Escritorio/Figuras/ScatterRefAnomalRad_HORA'+str(Hour[j])+'.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio/Scatters_Month_Hourly')

##-------------------CD EN BOX PLOT HORARIO PARA CADA PUNTO----------------##
df_fractal_horas = {}
for i in range(1, 13):
    A = df_Fractal[df_Fractal.index.hour == (i + 5)]['Dim_Fractal']
    H = A.index.hour[0]
    print(H)
    df_fractal_horas[H] = A.values
    del H, A
df_fractal_horas = pd.DataFrame.from_dict(df_fractal_horas,orient='index').transpose()


fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
df_fractal_horas.boxplot(grid=False)
plt.title(u'Distribución de la Dim Fractal por horas', fontproperties=prop, fontsize = 8)
plt.ylabel(u'Dimension fractal', fontproperties=prop_1)
plt.xlabel(u'Horas', fontproperties=prop_1)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/DimFrac_BoxPlotHora.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/DimFrac_BoxPlotHora.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##-------------------CD EN BOX PLOT MENSUAL PARA CADA PUNTO----------------##
df_fractal_meses = {}
for i in range(1, 13):
    A = df_Fractal[df_Fractal.index.month == (i)]['Dim_Fractal']
    H = A.index.month[0]
    print(H)
    df_fractal_meses[H] = A.values
    del H, A
df_fractal_meses = pd.DataFrame.from_dict(df_fractal_meses,orient='index').transpose()


fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
df_fractal_meses.boxplot(grid=False)
plt.title(u'Distribución de la Dim Fractal por meses', fontproperties=prop, fontsize = 8)
plt.ylabel(u'Dimension fractal', fontproperties=prop_1)
plt.xlabel(u'Mes', fontproperties=prop_1)

plt.savefig('/home/nacorreasa/Escritorio/Figuras/DimFrac_BoxPlotMes.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/DimFrac_BoxPlotMes.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


#########################################################################################
## --------------------ENCONTRANDO LAS FRECUENCIAS DE CADA IMAGEN----------------------##
#########################################################################################

Total_pix = Rad_bina.shape[1] *  Rad_bina.shape[2]
Parcial_pix = []
for k in range(len(Rad_bina)):
    p = Rad_bina[k, :, :]
    list = []
    for i in range(0, p.shape[0]):
        for j in range(0, p.shape[1]):
            if p[i, j] > 0:
                list.append(p[i, j])
            else:
                pass
    Parcial_pix.append(len(list))

Frec = [(float(Parcial_pix[i])/Total_pix)*100 for i in range(len((Parcial_pix)))]

df_Frec = pd.DataFrame(Frec, index = fechas_horas_new, columns = ['Frec'])

df_Frec_CD =  df_Frec.groupby(by=[df_Frec.index.hour]).mean()
df_Frec_CD_season =  df_Frec.groupby([df_Frec.index.month, df_Frec.index.hour]).mean()
df_Frec_Month =  df_Frec.groupby(by=[df_Frec.index.month]).mean()

##------------------------GRAFICA CD  Y CA............................##

plt.close('all')
fig = plt.figure(figsize=(18,9))
ax1 = fig.add_subplot(1, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(df_Frec_Month.index.values,  df_Frec_Month.Frec.values, color = '#09202E', lw=1.5)
ax1.scatter(df_Frec_Month.index.values,  df_Frec_Month.Frec.values, marker='.', color = '#09202E', s=30)
ax1.set_xlabel('Meses', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"Frecuencia [%]", fontproperties = prop_1, fontsize=20)
ax1.set_xticks(range(1, 13), minor=False)
ax1.set_xticklabels(Month, minor=False, rotation = 20)
ax1.set_ylim(0, 100)
ax1.set_title(u'Frecuencia mensual de las nubes en Medellín', loc = 'center', fontproperties = prop, fontsize=25)

ax2 = fig.add_subplot(1, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(df_Frec_CD.index.values,  df_Frec_CD.Frec.values, color = '#09202E', lw=1.5)
ax2.scatter(df_Frec_CD.index.values,  df_Frec_CD.Frec.values, marker='.', color = '#09202E', s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"Frecuencia [%]", fontproperties = prop_1, fontsize=20)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(Hour, minor=False, rotation = 20)
ax2.set_ylim(0, 100)
ax2.set_title(u'Frecuencia horaria mensual de las nubes en Medellín', loc = 'center', fontproperties = prop, fontsize=25)

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/FreqClouds.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/FreqClouds.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


##------------------------GRAFICA CD SEASONAL  Y CA............................##

colors_list = ['#800000', '#e6194B', '#f58231', '#9A6324', '#bfef45', '#3cb44b', '#42d4f4', '#469990', '#000075', '#4363d8', '#911eb4', '#f032e6']
plt.close('all')
fig = plt.figure(figsize=(23,15))
ax1 = fig.add_subplot(1, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(df_Frec_Month.index.values,  df_Frec_Month.Frec.values, color = '#09202E', lw=1.5)
ax1.scatter(df_Frec_Month.index.values,  df_Frec_Month.Frec.values, marker='.', color = '#09202E', s=30)
ax1.set_xlabel('Meses', fontproperties = prop_1, fontsize=20)
ax1.set_ylabel(u"Frecuencia [%]", fontproperties = prop_1, fontsize=23)
ax1.set_xticks(range(1, 13), minor=False)
ax1.set_xticklabels(Month, minor=False, rotation = 20, fontsize=13)
ax1.set_ylim(0, 100)
ax1.set_title(u'Frecuencia mensual de nubes en Medellín', loc = 'center', fontproperties = prop, fontsize=25)

ax2 = fig.add_subplot(1, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
for i in range(len(Hour)):
    serie = df_Frec_CD_season.iloc[df_Frec_CD_season.index.get_level_values(0) == i+1].Frec.values
    ax2.plot(df_Frec_CD.index.values,  serie, color = colors_list[i], lw=1.5, label = Month[i])
    ax2.scatter(df_Frec_CD.index.values,  serie, marker='.', c = colors_list[i], s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=20)
ax2.set_ylabel(u"Frecuencia [%]", fontproperties = prop_1, fontsize=23)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(Hour, minor=False, rotation = 20, fontsize=13)
ax2.set_ylim(0, 100)
ax2.set_title(u'Frecuencia horaria de nubes  \n por mes en Medellín', loc = 'center', fontproperties = prop, fontsize=23)
plt.legend(fontsize=13)

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.25, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/FreqClouds.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/FreqClouds.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
