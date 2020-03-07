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


#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Codigo para establecer si la radiacion en superficie de los piranometros guarda una relacion directa
con la profundidad optica de la nube. Se hace pixel a pixel con los pixeles seleccionados de COD para cada punto
"""
fec_ini = '2019-10-01'
fec_fin = '2019-10-31'
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
Anomalies = 'si'         ##---> Para que dibuje con las anomalias de la radiacion debe ser  'si'.
Promedio_3puntos = 'no'  ##---> Para que promedie la radiacion de los 3 puntos debe ser 'si'

##-----------------------------AJUSTE DE RANGO DE FECHAS----------------------------------##
import datetime as dt
fi  = dt.datetime.strptime(fec_ini, '%Y-%m-%d')
ff  = dt.datetime.strptime(fec_fin, '%Y-%m-%d')
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop   = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

COD_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix975_EXP.npy')
COD_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix350_EXP.npy')
COD_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_COD_pix348_EXP.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_CODEXP.npy')


# COD_pixel_975 = COD_pixel_975.astype('int32')
# COD_pixel_975 [COD_pixel_975 <0]=np.nan
#
# COD_pixel_350 = COD_pixel_350.astype('int32')
# COD_pixel_350 [COD_pixel_350 <0]=np.nan
#
# COD_pixel_975 = COD_pixel_975.astype('int32')
# COD_pixel_975 [COD_pixel_975 <0]=np.nan

                   ## -- Selección del pixel de la TS
COD_df_975 = pd.DataFrame()
COD_df_975['Fecha_Hora'] = fechas_horas
COD_df_975['COD'] = COD_pixel_975
COD_df_975['Fecha_Hora'] = pd.to_datetime(COD_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_975.index = COD_df_975['Fecha_Hora']
COD_df_975 = COD_df_975.drop(['Fecha_Hora'], axis=1)

                   ## -- Selección del pixel de la CI

COD_df_350 = pd.DataFrame()
COD_df_350['Fecha_Hora'] = fechas_horas
COD_df_350['COD'] = COD_pixel_350
COD_df_350['Fecha_Hora'] = pd.to_datetime(COD_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_350.index = COD_df_350['Fecha_Hora']
COD_df_350 = COD_df_350.drop(['Fecha_Hora'], axis=1)


                   ## -- Selección del pixel de la JV

COD_df_348 = pd.DataFrame()
COD_df_348['Fecha_Hora'] = fechas_horas[6:]
COD_df_348['COD'] = COD_pixel_348
COD_df_348['Fecha_Hora'] = pd.to_datetime(COD_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
COD_df_348.index = COD_df_348['Fecha_Hora']
COD_df_348 = COD_df_348.drop(['Fecha_Hora'], axis=1)


#################################################################################################
## --------------INCORPORANDO LOS DATOS DE RADIACIÓN PARA LOS DOS AÑOS DE DATOS--------------- ##
#################################################################################################


df_P975 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60012018_2019.txt', parse_dates=[2])
df_P350 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60022018_2019.txt', parse_dates=[2])
df_P348 = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60032018_2019.txt', parse_dates=[2])

df_P975 = df_P975.set_index(["fecha_hora"])
df_P975.index = df_P975.index.tz_localize('UTC').tz_convert('America/Bogota')
df_P975.index = df_P975.index.tz_localize(None)

df_P350 = df_P350.set_index(["fecha_hora"])
df_P350.index = df_P350.index.tz_localize('UTC').tz_convert('America/Bogota')
df_P350.index = df_P350.index.tz_localize(None)

df_P348 = df_P348.set_index(["fecha_hora"])
df_P348.index = df_P348.index.tz_localize('UTC').tz_convert('America/Bogota')
df_P348.index = df_P348.index.tz_localize(None)

df_P975.index = pd.to_datetime(df_P975.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P350.index = pd.to_datetime(df_P350.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_P348.index = pd.to_datetime(df_P348.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

## ----------------ACOTANDO LOS DATOS A VALORES VÁLIDOS---------------- ##

'Como en este caso lo que interesa es la radiacion, para la filtración de los datos, se'
'considerarán los datos de radiacion mayores a 0.'

df_P975 = df_P975[(df_P975['radiacion'] > 0) ]
df_P350 = df_P350[(df_P350['radiacion'] > 0) ]
df_P348 = df_P348[(df_P348['radiacion'] > 0) ]

df_P975_h = df_P975.groupby(pd.Grouper(freq="H")).mean()
df_P350_h = df_P350.groupby(pd.Grouper(freq="H")).mean()
df_P348_h = df_P348.groupby(pd.Grouper(freq="H")).mean()

df_P975 = df_P975.between_time('06:00', '17:59')
df_P350 = df_P350.between_time('06:00', '17:59')
df_P348 = df_P348.between_time('06:00', '17:59')

df_P975 =  df_P975.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)
df_P350 =  df_P350.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)
df_P348 =  df_P348.drop(['Unnamed: 0', 'idestacion', 'temperatura'], axis=1)

if Promedio_3puntos == 'si':
    ## ----------------UNIENDO LOS DATOS DE LOS 3 PUNTOS POR EL PROMEDIO---------------- ##
    df_Radiacion_Pira = pd.concat([df_P348, df_P350, df_P975], axis=1)
    df_Radiacion_Pira = df_Radiacion_Pira.mean(axis = 1, skipna = True)
    df_Radiacion_Pira = pd.DataFrame(df_Radiacion_Pira, columns=['Radiacion'])

    ## ----------------ACOTANDO LOS DATOS A FECHAS DESEADAS---------------- ##
    df_Radiacion_Pira = df_Radiacion_Pira.loc[(df_Radiacion_Pira.index >= fi) & (df_Radiacion_Pira.index <=ff) ]

    ## ----------------AGRUPANDOLOS POR RESOLUCIÓN TEMPORAL DE GOES---------------- ##
    df_Radiacion_Pira_10m = df_Radiacion_Pira.groupby(pd.Grouper(freq="15min")).mean()
else:
    pass

##########################################################################################
## ----------------LECTURA DE LOS DATOS DE LAS ANOMALIAS DE LA RADIACION--------------- ##
##########################################################################################
"""
Estos datos están cada 15 min
"""

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
Anomal_df_348 = Anomal_df_348.between_time('06:00', '18:00')

Anomal_df_348 = Anomal_df_348.drop(['Radiacion_Med', 'radiacion',], axis=1)
Anomal_df_350 = Anomal_df_350.drop(['Radiacion_Med', 'radiacion',], axis=1)
Anomal_df_975 = Anomal_df_975.drop(['Radiacion_Med', 'radiacion',], axis=1)

Anomal_df_348_h = Anomal_df_348.groupby(pd.Grouper(freq="H")).mean()
                      ##--> Seleccionar solo los datos de horas del dia
Anomal_df_348_h = Anomal_df_348_h.loc[~Anomal_df_348_h.index.duplicated(keep='first')]
Anomal_df_350_h = Anomal_df_350_h.loc[~Anomal_df_350_h.index.duplicated(keep='first')]
Anomal_df_975_h = Anomal_df_975_h.loc[~Anomal_df_975_h.index.duplicated(keep='first')]

############################################################################################
##--------------------------CONSTRUYENDO UN DATAFRAME COMPLETO ---------------------------##
############################################################################################

df_complete_975 = pd.concat([df_P975,  COD_df_975, Anomal_df_975], axis=1)
df_complete_975 = df_complete_975.between_time('06:00', '17:59')

df_complete_350 = pd.concat([df_P350,  COD_df_350, Anomal_df_350], axis=1)
df_complete_350 = df_complete_350.between_time('06:00', '17:59')

df_complete_348 = pd.concat([df_P348,  COD_df_348, Anomal_df_348], axis=1)
df_complete_348 = df_complete_348.between_time('06:00', '17:59')

############################################################################################
##---------------ACOTANDO EL DATAFRAME COMPLETO A LAS FECHAS DE INTERES-------------------##
############################################################################################

df_complete_975_muestra = df_complete_975.loc[(df_complete_975.index >= fi) & (df_complete_975.index <=ff) ]
df_complete_350_muestra = df_complete_350.loc[(df_complete_350.index >= fi) & (df_complete_350.index <=ff) ]
df_complete_348_muestra = df_complete_348.loc[(df_complete_348.index >= fi) & (df_complete_348.index <=ff) ]

#################################################################################################
## -------------------------GRAFICANDO A RELACION CONSIDERANDO LA HORA------------------------ ##
#################################################################################################


if Anomalies == 'si' :
    fig = plt.figure(figsize=[10, 8])
    plt.rc('axes', edgecolor='gray')
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    # ax1.spines['left'].set_position('center')
    # ax1.spines['bottom'].set_position('center')
    ax1.scatter(df_complete_350_muestra.COD.values, df_complete_350_muestra.Anomalia.values, s=50, c='#004D56', alpha=0.5, marker = ".")
    ax1.set_ylabel(u"Anomalia de \n Irradiancia  $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
    ax1.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
    ax1.set_title(u'Relacion en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    ax1.set_ylim(-600, 600)
    ax1.set_xlim(0, 160)
    ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)


    ax2 = fig.add_subplot(3, 1, 2)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    # ax2.spines['left'].set_position('center')
    # ax2.spines['bottom'].set_position('center')
    ax2.scatter(df_complete_975_muestra.COD.values, df_complete_975_muestra.Anomalia.values, s=50, c='#004D56', alpha=0.5, marker = ".")
    ax2.set_ylabel(u"Anomalia de \n Irradiancia  $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
    ax2.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
    ax2.set_title(u'Relacion en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
    ax2.xaxis.set_ticks_position('bottom')
    ax2.yaxis.set_ticks_position('left')
    ax2.set_ylim(-600, 600)
    ax2.set_xlim(0, 160)
    ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)

    ax3 = fig.add_subplot(3, 1, 3)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    # ax3.spines['left'].set_position('center')
    # ax3.spines['bottom'].set_position('center')
    ax3.scatter(df_complete_348_muestra.COD.values, df_complete_348_muestra.Anomalia.values, s=50, c='#004D56', alpha=0.5, marker = ".")
    ax3.set_ylabel(u"Anomalia de \n Irradiancia  $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
    ax3.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
    ax3.set_title(u'Relacion en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
    ax3.xaxis.set_ticks_position('bottom')
    ax3.yaxis.set_ticks_position('left')
    ax3.set_ylim(-600, 600)
    ax3.set_xlim(0, 160)
    ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)


    plt.subplots_adjust( wspace=0.4, hspace=0.45)
    plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_Anomal_vs_COD.pdf',  format='pdf')
    plt.close('all')
    os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_Anomal_vs_COD.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

else:
    fig = plt.figure(figsize=[10, 8])
    plt.rc('axes', edgecolor='gray')
    ax1 = fig.add_subplot(3, 1, 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.scatter(df_complete_350_muestra.COD.values, df_complete_350_muestra.radiacion.values, s=50, c='#004D56', alpha=0.5, marker = ".")
    ax1.set_ylabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
    ax1.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
    ax1.set_title(u'Relacion en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
    ax1.set_ylim(0, 1300)
    ax1.set_xlim(0, 160)
    ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)


    ax2 = fig.add_subplot(3, 1, 2)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.scatter(df_complete_975_muestra.COD.values, df_complete_975_muestra.radiacion.values, s=50, c='#004D56', alpha=0.5, marker = ".")
    ax2.set_ylabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
    ax2.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
    ax2.set_title(u'Relacion en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
    ax2.set_ylim(0, 1300)
    ax2.set_xlim(0, 160)
    ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)

    ax3 = fig.add_subplot(3, 1, 3)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.scatter(df_complete_348_muestra.COD.values, df_complete_348_muestra.radiacion.values, s=50, c='#004D56', alpha=0.5, marker = ".")
    ax3.set_ylabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
    ax3.set_xlabel(u"Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
    ax3.set_title(u'Relacion en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
    ax3.set_ylim(0, 1300)
    ax3.set_xlim(0, 160)
    ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)


    plt.subplots_adjust( wspace=0.4, hspace=0.45)
    plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_Radiacion_vs_COD.pdf',  format='pdf')
    plt.close('all')
    os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_Radiacion_vs_COD.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

############################################################################################
##--------------FIJANDO UNA COD Y ENCONTRANDO LAS IRRADIANCIAS ASOCIADAS------------------##
############################################################################################

COD_fija = [0, 10,  20, 30,   40, 50,  60, 70,  80,  90,  100, 110,  120, 130,  140, 150 , 160]


df_complete_975_fija = pd.DataFrame()
means_975 = []
std_975 = []
index_975 = []
for i in range (1, len(COD_fija)):
    df_complete_975_temporal = df_complete_975[(df_complete_975.COD>= COD_fija[i-1])&(df_complete_975.COD < COD_fija[i])]
    print(COD_fija[i])
    if len(df_complete_975_temporal)>1:
        df_complete_975_fija = df_complete_975_fija.append(df_complete_975_temporal)
        means_975.append(np.nanmean(df_complete_975_temporal.radiacion.values))
        std_975.append(np.nanstd(df_complete_975_temporal.radiacion.values))
        index_975.append(COD_fija[i])
    else:
        pass



df_complete_350_fija = pd.DataFrame()
means_350 = []
std_350 = []
index_350 = []
for i in range (1, len(COD_fija)):
    df_complete_350_temporal = df_complete_350[(df_complete_350.COD>= COD_fija[i-1])&(df_complete_350.COD < COD_fija[i])]
    print(COD_fija[i])
    if len(df_complete_350_temporal)>1:
        df_complete_350_fija = df_complete_350_fija.append(df_complete_350_temporal)
        means_350.append(np.nanmean(df_complete_350_temporal.radiacion.values))
        std_350.append(np.nanstd(df_complete_350_temporal.radiacion.values))
        index_350.append(COD_fija[i])
    else:
        pass



df_complete_348_fija = pd.DataFrame()
means_348 = []
std_348 = []
index_348 = []
for i in range (1, len(COD_fija)):
    df_complete_348_temporal = df_complete_348[(df_complete_348.COD>= COD_fija[i-1])&(df_complete_348.COD < COD_fija[i])]
    print(COD_fija[i])
    if len(df_complete_348_temporal)>1:
        df_complete_348_fija = df_complete_348_fija.append(df_complete_348_temporal)
        means_348.append(np.nanmean(df_complete_348_temporal.radiacion.values))
        std_348.append(np.nanstd(df_complete_348_temporal.radiacion.values))
        index_348.append(COD_fija[i])
    else:
        pass

#################################################################################################
## --------------GRAFICANDO LAS DESCIASIONES DE RADIACION POR INTERVALOS DE COD--------------- ##
#################################################################################################
index_350_labels = ['0-10', '10-20', '20-30', '30-40', '40-50','50-60', '60-70',
'70-80', '80-90', '90-100','100-110', '110-120', '120-130', '130-140', '140-150']
index_975_labels = ['0-10', '10-20', '20-30', '30-40', '40-50','50-60', '60-70',
'70-80', '80-90', '90-100','100-110', '110-120', '120-130', '130-140', '140-150']
index_348_labels = ['0-10', '10-20', '20-30', '30-40', '40-50','50-60', '60-70',
'70-80', '80-90', '90-100','100-110', '110-120', '120-130', '130-140', '140-150']

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3,1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(index_350, means_350, color= '#fdae61', label = 'Media')
ax1.scatter(index_350, means_350, s=50, c='#fdae61', marker = ".")
ax1.plot(index_350, std_350, color= '#2b83ba', label = u'Desviación estándar')
ax1.scatter(index_350, std_350, s=50, c='#2b83ba', marker = ".")
ax1.set_ylabel(u"$[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Intervalo Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Estadísticos en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.set_xticks(np.array(index_350), minor=False)
ax1.set_xticklabels(np.array(index_350_labels), minor=False, rotation = 20)
ax1.set_ylim(0, max(np.max(means_350), np.max(std_350)) +8)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

ax2 = fig.add_subplot(3, 1, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(index_975, means_975, color= '#fdae61', label = 'Media')
ax2.scatter(index_975, means_975, s=50, c='#fdae61', marker = ".")
ax2.plot(index_975, std_975, color= '#2b83ba', label = u'Desviación estándar')
ax2.scatter(index_975, std_975, s=50, c='#2b83ba', marker = ".")
ax2.set_ylabel(u"$[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Intervalo Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Estadísticos en el Centro Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.set_xticks(np.array(index_975), minor=False)
ax2.set_xticklabels(np.array(index_975_labels), minor=False, rotation = 20)
ax2.set_ylim(0, max(np.max(means_975), np.max(std_975)) +8)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.plot(index_348, means_348, color= '#fdae61', label = 'Media')
ax3.scatter(index_348, means_348, s=50, c='#fdae61', marker = ".")
ax3.plot(index_348, std_348, color= '#2b83ba', label = u'Desviación estándar')
ax3.scatter(index_348, std_348, s=50, c='#2b83ba', marker = ".")
ax3.set_ylabel(u"$[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Intervalo Profundidad Optica de Nubes", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Estadísticos en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.set_xticks(np.array(index_348), minor=False)
ax3.set_xticklabels(np.array(index_348_labels), minor=False, rotation = 20)
ax3.set_ylim(0, max(np.max(means_348),np.max(std_348)) +8)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)

plt.legend()
plt.subplots_adjust( wspace=0.4, hspace=0.65)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Irra_stdmean_interval_COD.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Irra_stdmean_interval_COD.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


############################################################################################
##--------------------COD CRITICA Y FDP DE  LAS IRRADIANCIAS ASOCIADAS--------------------##
############################################################################################

COD_cririca = 15
df_complete_975_critica = pd.DataFrame()

df_complete_975_temporal = df_complete_975[(df_complete_975.COD>= COD_cririca)&(df_complete_975.COD < COD_cririca+1)]
df_complete_975_temporal = df_complete_975_temporal[df_complete_975_temporal.Anomalia<0]
"""
Solo se escoge una muestras aleatoriamente.
"""
df_complete_975_temporal_aleatory = df_complete_975_temporal.sample(6)

"""
Solo se escoge una muestras aleatoriamente.
"""

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
for i in range(len(df_complete_975_temporal_aleatory.index )):
    df_radiation = df_complete_975['radiacion'][(df_complete_975.index > df_complete_975_temporal_aleatory.index[i]) & (df_complete_975.index <= df_complete_975_temporal_aleatory.index[i] +timedelta(minutes=15))]
    ax = fig.add_subplot(2, 3, i+1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.hist(df_radiation.values, bins='auto', alpha = 0.5)
    ax.set_title(u'Histograma radiacion muestra \n aleatoria: '+str(df_complete_975_temporal_aleatory.index[i]), fontproperties=prop, fontsize = 12)
    ax.set_ylabel(u'Frecuencia', fontproperties=prop_1, fontsize = 10)
    ax.set_xlabel(u'Radiacion', fontproperties=prop_1, fontsize = 10)
plt.subplots_adjust( wspace=0.4, hspace=0.65)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistogramaAleatorio.pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/HistogramaAleatorio.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
