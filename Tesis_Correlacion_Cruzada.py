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

Horizonte = 'Anio'    ##-->Para que tome datos desde el 2018 de GOES se pone 'Anio', para que tome solo lo del experimento se pone 'Exp'
Pluvio = 'si'         ##--> Para que promedie la lluvia de los dos pluviometros debe ser 'si'
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop   = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Código para realizar el análisis de correlación temporal de variables incidentes en el la generación de energía solar.
Es pensado para el horizonte del año o mayor, de manera que se tenga una estadística robusta. Tambien se hace la correlacion
lineal de Pearson para los datos entre la nubosidad del CH2 de GOES y los acumulados de lluvia de 2018. Todos los sets de
datos son normalizados y revisados en calidad de datos, a demás de ser remuestreados a resolución horaria entre las 06:00 y
las 17:59 para tomar 12 horas.
"""
##########################################################################################################
##-----------------------------------LECTURA DE LOS DATOS  DE PIRANOMETRO-------------------------------##
##########################################################################################################

def ReadPrianometro(Path, NameFile):
    df_pira = pd.read_table(os.path.join(Path, NameFile), parse_dates=[2])
    df_pira = df_pira.set_index(["fecha_hora"])
    df_pira.index = df_pira.index.tz_localize('UTC').tz_convert('America/Bogota')
    df_pira.index = df_pira.index.tz_localize(None)
    df_pira = df_pira[df_pira['radiacion'] >=0]

    return df_pira

Path_pira = '/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/'
df_pira_TS = ReadPrianometro(Path_pira,'60012018.txt')
df_pira_CI = ReadPrianometro(Path_pira,'60022018.txt')
df_pira_JV = ReadPrianometro(Path_pira,'60032018.txt')
## ------------------------------------DATOS HORARIOS DE RADIACON----------------------------- ##

df_pira_JV_h =  df_pira_JV.groupby(pd.Grouper(freq="H")).mean()
df_pira_CI_h =  df_pira_CI.groupby(pd.Grouper(freq="H")).mean()
df_pira_TS_h =  df_pira_TS.groupby(pd.Grouper(freq="H")).mean()

df_pira_JV_h = df_pira_JV_h.between_time('06:00', '17:59')
df_pira_CI_h = df_pira_CI_h.between_time('06:00', '17:59')
df_pira_TS_h = df_pira_TS_h.between_time('06:00', '17:59')
##########################################################################################
## ----------------LECTURA DE LOS DATOS DE LAS ANOMALIAS DE LA RADIACION--------------- ##
##########################################################################################
def ReadAnomalRad(Path, NameFile):
    Anomal_df= pd.read_csv(os.path.join(Path, NameFile),  sep=',')
    Anomal_df['fecha_hora'] = pd.to_datetime(Anomal_df['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
    Anomal_df.index = Anomal_df['fecha_hora']
    Anomal_df = Anomal_df.drop(['fecha_hora'], axis=1)
    Anomal_df = Anomal_df.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
    Anomal_df_h = Anomal_df.groupby(pd.Grouper(freq="H")).mean()
    Anomal_df_h = Anomal_df_h.drop(['Radiacion_Med', 'radiacion',], axis=1)
    Anomal_df_h = Anomal_df_h.loc[~Anomal_df_h.index.duplicated(keep='first')]

    return Anomal_df_h

Path_AnomalRad = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
Anomal_df_975_h = ReadAnomalRad(Path_AnomalRad, 'df_AnomalRad_pix975_2018_2019.csv')
Anomal_df_348_h = ReadAnomalRad(Path_AnomalRad, 'df_AnomalRad_pix348_2018_2019.csv')
Anomal_df_350_h = ReadAnomalRad(Path_AnomalRad, 'df_AnomalRad_pix350_2018_2019.csv')


###########################################################################################################
##---------------------------------LECTURA DE LA MALLA DE DATOS CH2 GOES---------------------------------##
###########################################################################################################

Rad = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_2018_2019CH2.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')
lat = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lat_CH2_2018_2019.npy')
lon = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Lon_CH2_2018_2019.npy')

df_fh  = pd.DataFrame()
df_fh ['fecha_hora'] = fechas_horas
df_fh['fecha_hora'] = pd.to_datetime(df_fh['fecha_hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_fh.index = df_fh['fecha_hora']
w = pd.date_range(df_fh.index.min(), df_fh.index.max()).difference(df_fh.index)

#################################################################################################
##-------------------LECTURA DE LOS DATOS DE CH2 GOES PARA CADA PIXEL--------------------------##
#################################################################################################

Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
Rad_pixel_350 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix350_Anio.npy')
Rad_pixel_348 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix348_Anio.npy')
fechas_horas = df_fh['fecha_hora'].values

Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975['Fecha_Hora'] = pd.to_datetime(Rad_df_975['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)


Rad_df_350 = pd.DataFrame()
Rad_df_350['Fecha_Hora'] = fechas_horas
Rad_df_350['Radiacias'] = Rad_pixel_350
Rad_df_350['Fecha_Hora'] = pd.to_datetime(Rad_df_350['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_350.index = Rad_df_350['Fecha_Hora']
Rad_df_350 = Rad_df_350.drop(['Fecha_Hora'], axis=1)


Rad_df_348 = pd.DataFrame()
Rad_df_348['Fecha_Hora'] = fechas_horas
Rad_df_348['Radiacias'] = Rad_pixel_348
Rad_df_348['Fecha_Hora'] = pd.to_datetime(Rad_df_348['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
Rad_df_348.index = Rad_df_348['Fecha_Hora']
Rad_df_348 = Rad_df_348.drop(['Fecha_Hora'], axis=1)

## ------------------------------------DATOS HORARIOS DE REFLECTANCIAS------------------------- ##

Rad_df_348_h =  Rad_df_348.groupby(pd.Grouper(freq="H")).mean()
Rad_df_350_h =  Rad_df_350.groupby(pd.Grouper(freq="H")).mean()
Rad_df_975_h =  Rad_df_975.groupby(pd.Grouper(freq="H")).mean()

Rad_df_348_h = Rad_df_348_h.between_time('06:00', '17:59')
Rad_df_350_h = Rad_df_350_h.between_time('06:00', '17:59')
Rad_df_975_h = Rad_df_975_h.between_time('06:00', '17:59')

########################################################################################################
## -------------------------------SELECCIONARLAS REFLECTANCIAS NUBLADAS------------------------------ ##
########################################################################################################

df_975_nuba = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Aniodf_Nublados_pix975.csv',  sep=',')
df_350_nuba = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Aniodf_Nublados_pix350.csv',  sep=',')
df_348_nuba = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Aniodf_Nublados_pix348.csv',  sep=',')

df_975_nuba['Unnamed: 0'] = pd.to_datetime(df_975_nuba['Unnamed: 0'], format="%Y-%m-%d %H:%M", errors='coerce')
df_975_nuba.index = df_975_nuba['Unnamed: 0']
df_975_nuba = df_975_nuba.drop(['Unnamed: 0'], axis=1)

df_350_nuba['Unnamed: 0'] = pd.to_datetime(df_350_nuba['Unnamed: 0'], format="%Y-%m-%d %H:%M", errors='coerce')
df_350_nuba.index = df_350_nuba['Unnamed: 0']
df_350_nuba = df_350_nuba.drop(['Unnamed: 0'], axis=1)

df_348_nuba['Unnamed: 0'] = pd.to_datetime(df_348_nuba['Unnamed: 0'], format="%Y-%m-%d %H:%M", errors='coerce')
df_348_nuba.index = df_348_nuba['Unnamed: 0']
df_348_nuba = df_348_nuba.drop(['Unnamed: 0'], axis=1)


df_348_nuba_h =  df_348_nuba.groupby(pd.Grouper(freq="H")).mean()
df_350_nuba_h =  df_350_nuba.groupby(pd.Grouper(freq="H")).mean()
df_975_nuba_h =  df_975_nuba.groupby(pd.Grouper(freq="H")).mean()

df_348_nuba_h = df_348_nuba_h.between_time('06:00', '17:59')
df_350_nuba_h = df_350_nuba_h.between_time('06:00', '17:59')
df_975_nuba_h = df_975_nuba_h.between_time('06:00', '17:59')

################################################################################################################
## -------------------------LECTURA DE LOS DATOS DE COBERTURA DE NUBES FISH EYE-------------------------------##
################################################################################################################

df_cloud_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_TS.csv',  sep=',')
df_cloud_TS.columns = ['fecha_hora', 'Porcentaje']
df_cloud_TS.index = df_cloud_TS['fecha_hora']
df_cloud_TS = df_cloud_TS.drop(['fecha_hora'], axis =1)
df_cloud_TS.index = pd.to_datetime(df_cloud_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_TS.index = [df_cloud_TS.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_TS.index))]
df_cloud_TS.index = pd.to_datetime(df_cloud_TS.index, format="%Y-%m-%d %H:%M", errors='coerce')


df_cloud_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_CI.csv',  sep=',')
df_cloud_CI.columns = ['fecha_hora', 'Porcentaje']
df_cloud_CI.index = df_cloud_CI['fecha_hora']
df_cloud_CI = df_cloud_CI.drop(['fecha_hora'], axis =1)
df_cloud_CI.index = pd.to_datetime(df_cloud_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_CI.index = [df_cloud_CI.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_CI.index))]
df_cloud_CI.index = pd.to_datetime(df_cloud_CI.index, format="%Y-%m-%d %H:%M", errors='coerce')


df_cloud_AMVA = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_AMVA.csv',  sep=',')
df_cloud_AMVA.columns = ['fecha_hora', 'Porcentaje']
df_cloud_AMVA.index = df_cloud_AMVA['fecha_hora']
df_cloud_AMVA = df_cloud_AMVA.drop(['fecha_hora'], axis =1)
df_cloud_AMVA.index = pd.to_datetime(df_cloud_AMVA.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_cloud_AMVA.index = [df_cloud_AMVA.index[i].strftime("%Y-%m-%d %H:%M:00 ") for i in range(len(df_cloud_AMVA.index))]
df_cloud_AMVA.index = pd.to_datetime(df_cloud_AMVA.index, format="%Y-%m-%d %H:%M", errors='coerce')


##----------------------------------ACOTANDOLO A LOS DATOS DE SOLO EL 2018---------------------------------##

# Rad_df_975 = Rad_df_975[Rad_df_975.index.year==2018]
# Rad_df_350 = Rad_df_350[Rad_df_350.index.year==2018]
# Rad_df_348 = Rad_df_348[Rad_df_348.index.year==2018]


## ------------------------------------DATOS HORARIOS DE % DE NUBES------------------------- ##

df_cloud_AMVA_h =  df_cloud_AMVA.groupby(pd.Grouper(freq="H")).mean()
df_cloud_CI_h =  df_cloud_CI.groupby(pd.Grouper(freq="H")).mean()
df_cloud_TS_h =  df_cloud_TS.groupby(pd.Grouper(freq="H")).mean()

df_cloud_TS_h = df_cloud_TS_h.between_time('06:00', '17:59')
df_cloud_CI_h = df_cloud_CI_h.between_time('06:00', '17:59')
df_cloud_AMVA_h = df_cloud_AMVA_h.between_time('06:00', '17:59')

##########################################################################################################
##-------------------------------UNIENDO LOS DOS DATAFRAMES POR LOS INDICES-----------------------------##
##########################################################################################################

df_complete_348_h = pd.concat([df_348_nuba_h, df_pira_JV_h,  df_cloud_AMVA_h, Anomal_df_348_h], axis=1)
df_complete_350_h = pd.concat([df_350_nuba_h, df_pira_CI_h,  df_cloud_CI_h, Anomal_df_350_h], axis=1)
df_complete_975_h = pd.concat([df_975_nuba_h, df_pira_TS_h,  df_cloud_TS_h, Anomal_df_975_h ], axis=1)

df_complete_348_h = df_complete_348_h.drop(['Unnamed: 0', 'idestacion'], axis=1)
df_complete_350_h = df_complete_350_h.drop(['Unnamed: 0', 'idestacion'], axis=1)
df_complete_975_h = df_complete_975_h.drop(['Unnamed: 0', 'idestacion'], axis=1)


##------------------------------------------------------------------------------------------------------------------##
df_complete_348_h_norm = (df_complete_348_h - df_complete_348_h.mean()) / (df_complete_348_h.max() - df_complete_348_h.min())
df_complete_350_h_norm = (df_complete_350_h - df_complete_350_h.mean()) / (df_complete_350_h.max() - df_complete_350_h.min())
df_complete_975_h_norm = (df_complete_975_h - df_complete_975_h.mean()) / (df_complete_975_h.max() - df_complete_975_h.min())

df_complete_348_h_norm = df_complete_348_h_norm[df_complete_348_h_norm.index.year == 2018]
df_complete_350_h_norm = df_complete_350_h_norm[df_complete_350_h_norm.index.year == 2018]
df_complete_975_h_norm = df_complete_975_h_norm[df_complete_975_h_norm.index.year == 2018]


##---------------------------SCATTER RELACION ENTRE % NUBES Y ANOMALIAS DE LA RADIACION---------------------------------------##

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.scatter(df_complete_975_h.Anomalia.values, df_complete_975_h.Radiacias.values, s=40, c='orange', label='P_TS', alpha=0.3, marker = ".")
ax.scatter(df_complete_350_h.Anomalia.values, df_complete_350_h.Radiacias.values, s=40, c='green', label='P_CI', alpha=0.3, marker = "*")
ax.scatter(df_complete_348_h.Anomalia.values, df_complete_348_h.Radiacias.values, s=40, c='red', label='P_JV', alpha=0.3, marker = "p")
ax.set_ylabel(u"Anomalia Rad",  fontproperties=prop_1, fontsize=20)
ax.set_xlabel(u"Reflectancias", fontproperties=prop_1, fontsize=20)
ax.set_ylim(0, 100 )
plt.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend(loc = 2)
plt.title(u'Scatter Ref- Anomalias Rad', fontsize=18,  fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_AnomaliasReflec.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_AnomaliasReflec.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##########################################################################################################
##------------------------EJECUTANDO LA CORRELACION CRUZADA SOBRE CADA DATAFRAME------------------------##
##########################################################################################################


def crosscorr(datax, datay, lag=0, wrap=False):
    """ Lag-N cross correlation.
    Shifted data filled with NaNs

    Parameters
    ----------
    lag :  bint, default 0
    datax, datay : pandas.Series objects of equal length
    Returns
    ----------
    crosscorr : float
    """
    if wrap:
        shiftedy = datay.shift(lag)
        shiftedy.iloc[:lag] = datay.iloc[-lag:].values
        return datax.corr(shiftedy)
    else:
        return datax.corr(datay.shift(lag))

lag = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

##------------------------CROSS COR ENTRE RADIACION Y REFLECTANCIA--------------------------##
d1_348_rr = df_complete_348_h_norm['Radiacias']
d2_348_rr = df_complete_348_h_norm['Anomalia']
rs_348_rr = [crosscorr(d1_348_rr,d2_348_rr, i) for i in range(-11, 12)]

d1_350_rr = df_complete_350_h_norm['Radiacias']
d2_350_rr = df_complete_350_h_norm['Anomalia']
rs_350_rr = [crosscorr(d1_350_rr,d2_350_rr, i) for i in range(-11, 12)]

d1_975_rr = df_complete_975_h_norm['Radiacias']
d2_975_rr = df_complete_975_h_norm['Anomalia']
rs_975_rr = [crosscorr(d1_975_rr,d2_975_rr, i) for i in range(-11, 12)]

y_min = min(np.nanmin(rs_348_rr)  , np.nanmin(rs_350_rr), np.nanmin(rs_975_rr))-0.01
y_max = max(np.nanmax(rs_348_rr)   , np.nanmax(rs_350_rr), np.nanmax(rs_975_rr))+0.01

Fig = plt.figure(figsize=(14,10))
ax1 = Fig.add_subplot(311)
ax1.plot(list(np.arange(-11, 12)),rs_350_rr)
ax1.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_350_rr)), rs_350_rr, where=rs_350_rr >= np.repeat(0, len(rs_350_rr)), facecolor='green', interpolate=True, alpha = 0.3)
ax1.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_350_rr)), rs_350_rr, where=rs_350_rr <= np.repeat(0, len(rs_350_rr)), facecolor='red', interpolate=True, alpha = 0.3)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.axvline(np.mean(np.arange(-11, 12)),color='k',linestyle='--',label='Center')
ax1.axvline(list(np.arange(-11, 12))[np.argmax(abs(np.array(rs_350_rr)))],color='r',linestyle='--',label='Peak synchrony')
ax1.set_title(u'Reflectance vs Radiation anomalies Correlation in the West', fontsize=20,  fontweight = "bold",  fontproperties = prop)
ax1.set_xlabel('Offset',  fontproperties=prop_1, fontsize=16)
ax1.set_ylabel('Pearson r',  fontproperties=prop_1, fontsize=16)
ax1.set_xticks( np.arange(-11, 12))
ax1.set_xticklabels(list(np.arange(-11, 12)))
ax1.set_ylim(y_min, y_max)
plt.legend()


ax2 = Fig.add_subplot(312)
ax2.plot(np.arange(-11, 12), rs_975_rr)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_975_rr)), rs_975_rr, where=rs_975_rr >= np.repeat(0, len(rs_975_rr)), facecolor='green', interpolate=True, alpha = 0.3)
ax2.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_975_rr)), rs_975_rr, where=rs_975_rr <= np.repeat(0, len(rs_975_rr)), facecolor='red', interpolate=True, alpha = 0.3)
ax2.axvline(np.mean(np.arange(-11, 12)),color='k',linestyle='--',label='Center')
ax2.axvline(list(np.arange(-11, 12))[np.argmax(abs(np.array(rs_975_rr)))],color='r',linestyle='--',label='Peak synchrony')
ax2.set_title(u'Reflectance vs Radiation anomalies Correlation in the West Center', fontsize=20,  fontweight = "bold",  fontproperties = prop)
ax2.set_xlabel('Offset',  fontproperties=prop_1, fontsize=16)
ax2.set_ylabel('Pearson r',  fontproperties=prop_1, fontsize=16)
ax2.set_xticks( np.arange(-11, 12))
ax2.set_xticklabels(list(np.arange(-11, 12)))
ax2.set_ylim(y_min, y_max)
plt.legend()


ax3 = Fig.add_subplot(313)
ax3.plot(list(np.arange(-11, 12)), rs_348_rr)
ax3.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_348_rr)), rs_348_rr, where=rs_348_rr >= np.repeat(0, len(rs_348_rr)), facecolor='green', interpolate=True, alpha = 0.3)
ax3.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_348_rr)), rs_348_rr, where=rs_348_rr <= np.repeat(0, len(rs_348_rr)), facecolor='red', interpolate=True, alpha = 0.3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.axvline(np.mean(np.arange(-11, 12)),color='k',linestyle='--',label='Center')
ax3.axvline(list(np.arange(-11, 12))[np.argmax(abs(np.array(rs_348_rr)))],color='r',linestyle='--',label='Peak synchrony')
ax3.set_title(u'Reflectance vs Radiation anomalies Correlation in the East', fontsize=20,  fontweight = "bold",  fontproperties = prop)
ax3.set_xlabel('Offset',  fontproperties=prop_1, fontsize=16)
ax3.set_ylabel('Pearson r',  fontproperties=prop_1, fontsize=16)
ax3.set_xticks( np.arange(-11, 12))
ax3.set_xticklabels(list(np.arange(-11, 12)))
ax3.set_ylim(y_min, y_max)
plt.legend()

plt.subplots_adjust(hspace=0.45)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CorrelacionReflecRad.png')
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CorrelacionReflecRad.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CorrelacionReflecRad.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

##------------------------CROSS COR ENTRE RADIACION Y %NUBE FISHEYE--------------------------##

d1_348_rp = df_complete_348_h_norm['Porcentaje']
d2_348_rp = df_complete_348_h_norm['Anomalia']
rs_348_rp = [crosscorr(d1_348_rp,d2_348_rp, i) for i in range(-11, 12)]

d1_350_rp = df_complete_350_h_norm['Porcentaje']
d2_350_rp = df_complete_350_h_norm['Anomalia']
rs_350_rp = [crosscorr(d1_350_rp,d2_350_rp, i) for i in range(-11, 12)]

d1_975_rp = df_complete_975_h_norm['Porcentaje']
d2_975_rp = df_complete_975_h_norm['Anomalia']
rs_975_rp = [crosscorr(d1_975_rp,d2_975_rp, i) for i in range(-11, 12)]

y_min = min(np.nanmin(rs_348_rp)  , np.nanmin(rs_350_rp), np.nanmin(rs_975_rp))-0.01
y_max = max(np.nanmax(rs_348_rp)   , np.nanmax(rs_350_rp), np.nanmax(rs_975_rp))+0.01

Fig = plt.figure(figsize=(14,10))
ax1 = Fig.add_subplot(311)
ax1.plot(list(np.arange(-11, 12)),rs_350_rp)
ax1.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_350_rp)), rs_350_rp, where=rs_350_rp >= np.repeat(0, len(rs_350_rp)), facecolor='green', interpolate=True, alpha = 0.3)
ax1.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_350_rp)), rs_350_rp, where=rs_350_rp <= np.repeat(0, len(rs_350_rp)), facecolor='red', interpolate=True, alpha = 0.3)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.axvline(np.mean(np.arange(-11, 12)),color='k',linestyle='--',label='Center')
ax1.axvline(list(np.arange(-11, 12))[np.argmax(abs(np.array(rs_350_rp)))],color='r',linestyle='--',label='Peak synchrony')
ax1.set_title(u' % Clouds coverage vs Radiation anomalies Correlation in the West', fontsize=20,  fontweight = "bold",  fontproperties = prop)
ax1.set_xlabel('Offset',  fontproperties=prop_1, fontsize=16)
ax1.set_ylabel('Pearson r',  fontproperties=prop_1, fontsize=16)
ax1.set_xticks( np.arange(-11, 12))
ax1.set_xticklabels(list(np.arange(-11, 12)))
ax1.set_ylim(y_min, y_max)
plt.legend()

ax2 = Fig.add_subplot(312)
ax2.plot(np.arange(-11, 12), rs_975_rp)
ax2.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_975_rp)), rs_975_rp, where=rs_975_rp >= np.repeat(0, len(rs_975_rp)), facecolor='green', interpolate=True, alpha = 0.3)
ax2.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_975_rp)), rs_975_rp, where=rs_975_rp <= np.repeat(0, len(rs_975_rp)), facecolor='red', interpolate=True, alpha = 0.3)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.axvline(np.mean(np.arange(-11, 12)),color='k',linestyle='--',label='Center')
ax2.axvline(list(np.arange(-11, 12))[np.argmax(abs(np.array(rs_975_rp)))],color='r',linestyle='--',label='Peak synchrony')
ax2.set_title(u' % Clouds coverage vs Radiation anomalies Correlation in the Center', fontsize=20,  fontweight = "bold",  fontproperties = prop)
ax2.set_xlabel('Offset',  fontproperties=prop_1, fontsize=16)
ax2.set_ylabel('Pearson r',  fontproperties=prop_1, fontsize=16)
ax2.set_xticks( np.arange(-11, 12))
ax2.set_xticklabels(list(np.arange(-11, 12)))
ax2.set_ylim(y_min, y_max)
plt.legend()

ax3 = Fig.add_subplot(313)
ax3.plot(list(np.arange(-11, 12)), rs_348_rp)
ax3.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_348_rp)), rs_348_rp, where=rs_348_rp >= np.repeat(0, len(rs_348_rp)), facecolor='green', interpolate=True, alpha = 0.3)
ax3.fill_between(list(np.arange(-11, 12)), np.repeat(0, len(rs_348_rp)), rs_348_rp, where=rs_348_rp <= np.repeat(0, len(rs_348_rp)), facecolor='red', interpolate=True, alpha = 0.3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.axvline(np.mean(np.arange(-11, 12)),color='k',linestyle='--',label='Center')
ax3.axvline(list(np.arange(-11, 12))[np.argmax(abs(np.array(rs_348_rp)))],color='r',linestyle='--',label='Peak synchrony')
ax3.set_title(u' % Clouds coverage vs Radiation anomalies Correlation in the East', fontsize=20,  fontweight = "bold",  fontproperties = prop)
ax3.set_xlabel('Offset',  fontproperties=prop_1, fontsize=16)
ax3.set_ylabel('Pearson r',  fontproperties=prop_1, fontsize=16)
ax3.set_xticks( np.arange(-11, 12))
ax3.set_xticklabels(list(np.arange(-11, 12)))
ax3.set_ylim(y_min, y_max)
plt.legend()

plt.subplots_adjust(hspace=0.4)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CorrelacionRadPorc.png')
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CorrelacionRadPorc.pdf', format='pdf', transparent=True)
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CorrelacionRadPorc.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
