#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
from scipy import stats
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
from pysolar.solar import *
import scipy.stats as st
import scipy.special as sp


'Programas para la selección de días despejados, en los horizontes de tiempo deseados'
##############################################################################
## ------------------------------ENTRADAS INICIALES------------------------ ##
##############################################################################
Horizonte_Tiempo = 'Experimento'  ##---> Puede ser experimento o histórico
fi_m = 3
fi_d = 23
ff_m = 8
ff_d = 22
Theoric_Model = 'GIS'   ##---> 'GIS' para que coja el de Gis o 'Piranometro' para que tome el de el piranometro

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

def lectura_datos_piranometro(df):
    df['Fecha_hora'] = df.index
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
    ## -----------------ACOTANDO LOS DATOS A VALORES VÁLIDOS----------------- ##
    df = df[df['radiacion'] > 0]
    df = df[(df['NI'] >= 0) & (df['strength'] >= 0)]
    ## --------------------ACOTANDO LOS DATOS POR CALIDAD-------------------- ##
    if 'calidad' in df.columns:
        df = df[df['calidad']<100]
    ## ---------------------AGRUPANDO LOS DATOS A HORAS---------------------- ##
    df_h = df.groupby(pd.Grouper(freq="H")).mean()
    df_h = df_h.between_time('06:00', '17:00')
    return df_h, df

df_P975_h, df_P975 = lectura_datos_piranometro(df_P975)
df_P350_h, df_P350 = lectura_datos_piranometro(df_P350)
df_P348_h, df_P348 = lectura_datos_piranometro(df_P348)

df_P975_h = df_P975_h[(df_P975_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_P975_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

df_P350_h = df_P350_h[(df_P350_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_P350_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

df_P348_h = df_P348_h[(df_P348_h.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
            +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_P348_h.index
            <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

##############################################################################
## ----------------LECTURA DE LOS DATOS DE RADIACION TEORICA--------------- ##
##############################################################################

if Theoric_Model == 'Piranometro':
    df_Theoric = pd.read_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_PIR.csv",  sep=',', index_col =0)
    df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

    df_Theoric = df_Theoric[(df_Theoric.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
                +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_Theoric.index
                <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

elif Theoric_Model == 'GIS':
    df_Theoric = pd.read_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_GIS.csv",  sep=',', index_col =0)
    df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')

    df_Theoric = df_Theoric[(df_Theoric.index >= pd.to_datetime('2019-'+str(fi_m)+ '-'
                +str(fi_d), format="%Y-%m-%d", errors='coerce')) & (df_Theoric.index
                <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d), format="%Y-%m-%d", errors='coerce') )]

###############################################################################
##---------ESTABLECIENDO EL PERCENTIL MINO DE DIA DESPEJADO O NUBLADO---------##
###############################################################################

'El acumulado diario de la radiación teórica'

df_Theoric_sum = df_Theoric.groupby(pd.Grouper(freq='1D')).sum()

Hist_df_Theoric_sum = np.histogram(df_Theoric_sum.values[~np.isnan(df_Theoric_sum.values)])

##-------DISCRIMINACION ENTRE DIAS LLUVIOSOS Y SECOS POR PERCENTILES DE RADIACION--------##

'Contraste de la distribución de las frecuencias de las radiación acumulada por cada dia con los datos de registro'
'y con los de los registros de cada punto.'

Sum_df_P975 = df_P975_h.groupby(pd.Grouper(freq='1D')).sum()
Sum_df_P350 = df_P350_h.groupby(pd.Grouper(freq='1D')).sum()
Sum_df_P348 = df_P348_h.groupby(pd.Grouper(freq='1D')).sum()

Hist_df_P975_sum = np.histogram(Sum_df_P975['radiacion'].values[~np.isnan(Sum_df_P975['radiacion'].values)])
Hist_df_P350_sum = np.histogram(Sum_df_P350['radiacion'].values[~np.isnan(Sum_df_P350['radiacion'].values)])
Hist_df_P348_sum = np.histogram(Sum_df_P348['radiacion'].values[~np.isnan(Sum_df_P348['radiacion'].values)])

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(df_Theoric_sum['Rad_teo_348'].values[~np.isnan(df_Theoric_sum['Rad_teo_348'].values)], bins='auto', alpha = 0.5, color = 'orange')
ax1.hist(Sum_df_P348['radiacion'].values[~np.isnan(Sum_df_P348['radiacion'].values)], bins='auto', alpha = 0.5)
ax1.set_title(u'Distribución de la radiación \n diaria en JV', fontproperties=prop, fontsize = 13)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Acumulado diario de radiación', fontproperties=prop_1)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(df_Theoric_sum['Rad_teo_350'].values[~np.isnan(df_Theoric_sum['Rad_teo_350'].values)], bins='auto', alpha = 0.5, color = 'orange')
ax2.hist(Sum_df_P350['radiacion'].values[~np.isnan(Sum_df_P350['radiacion'].values)], bins='auto', alpha = 0.5)
ax2.set_title(u'Distribución de la radiación \n diaria en CI', fontproperties=prop, fontsize = 13)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Acumulado diario de radiación', fontproperties=prop_1)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(df_Theoric_sum['Rad_teo_975'].values[~np.isnan(df_Theoric_sum['Rad_teo_975'].values)], bins='auto', alpha = 0.5, color = 'orange')
ax3.hist(Sum_df_P975['radiacion'].values[~np.isnan(Sum_df_P975['radiacion'].values)], bins='auto', alpha = 0.5)
ax3.set_title(u'Distribución de la radiación \n diaria en TS', fontproperties=prop, fontsize = 13)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Acumulado diario de radiación', fontproperties=prop_1)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/HistoRadAcumDia.png')
plt.show()

#####################################################################################################################################
##-------------ENCONTRAR LA FRACCIÓN QUE REPRESENTAN DE ACUERDO A LOS CASOS SELECCIONADOS DENTRO DEL PERIODO DE REGISTRO-----------##
#####################################################################################################################################

'Se pretenden encontrar algunos días extras a partir de los días de ejemplo, que deben estar dentro del horizonte de registro'
##-------------------------------NUBLADOS-------------------------------------##

Desp_dia = [ 18]
Desp_mes = [ 8]

Sum_df_P975_desp = pd.DataFrame()
for i in range(len(Desp_mes)):
    a = Sum_df_P975.loc[(Sum_df_P975.index.month == Desp_mes[i]) & (Sum_df_P975.index.day== Desp_dia[i])]
    Sum_df_P975_desp = pd.concat([Sum_df_P975_desp, a])
    print(a.index)

Sum_df_P350_desp = pd.DataFrame()
for i in range(len(Desp_mes)):
    a = Sum_df_P350.loc[(Sum_df_P350.index.month == Desp_mes[i]) & (Sum_df_P350.index.day== Desp_dia[i])]
    Sum_df_P350_desp = pd.concat([Sum_df_P350_desp, a])
    print(a.index)

Sum_df_P348_desp = pd.DataFrame()
for i in range(len(Desp_mes)):
    a = Sum_df_P348.loc[(Sum_df_P348.index.month == Desp_mes[i]) & (Sum_df_P348.index.day== Desp_dia[i])]
    Sum_df_P348_desp = pd.concat([Sum_df_P348_desp, a])
    print(a.index)

Theo_desp_975 = []
for i in range(len(Desp_mes)):
    Theo_desp_975.append(df_Theoric_sum['Rad_teo_348'].loc[(df_Theoric_sum.index.month == Desp_mes[i]) & (df_Theoric_sum.index.day== Desp_dia[i])].values[0])
Sum_df_P975_desp['Rad_Teoric'] = Theo_desp_975
Sum_df_P975_desp['Prop'] = (Sum_df_P975_desp['radiacion'] * 100)/Sum_df_P975_desp['Rad_Teoric']

Theo_desp_350 = []
for i in range(len(Desp_mes)):
    Theo_desp_350.append(df_Theoric_sum['Rad_teo_348'].loc[(df_Theoric_sum.index.month == Desp_mes[i]) & (df_Theoric_sum.index.day== Desp_dia[i])].values[0])
Sum_df_P350_desp['Rad_Teoric'] = Theo_desp_350
Sum_df_P350_desp['Prop'] = (Sum_df_P350_desp['radiacion'] * 100)/Sum_df_P350_desp['Rad_Teoric']

Theo_desp_348 = []
for i in range(len(Desp_mes)):
    Theo_desp_348.append(df_Theoric_sum['Rad_teo_348'].loc[(df_Theoric_sum.index.month == Desp_mes[i]) & (df_Theoric_sum.index.day== Desp_dia[i])].values[0])
Sum_df_P348_desp['Rad_Teoric'] = Theo_desp_348
Sum_df_P348_desp['Prop'] = (Sum_df_P348_desp['radiacion'] * 100)/Sum_df_P348_desp['Rad_Teoric']

List_prop_desp = []
if Sum_df_P348_desp['Prop'].values > 0:
    List_prop_desp.append(Sum_df_P348_desp['Prop'].values[0])
if Sum_df_P350_desp['Prop'].values > 0:
    List_prop_desp.append(Sum_df_P350_desp['Prop'].values[0])
if Sum_df_P975_desp['Prop'].values > 0:
    List_prop_desp.append(Sum_df_P975_desp['Prop'].values[0])

if len(List_prop_desp) > 1:
    Prop_umbral_desp = np.nanmean(List_prop_desp)
elif len(List_prop_desp) == 1:
    Prop_umbral_desp = List_prop_desp [0]

print('Porcentaje para despejado = '+ str(Prop_umbral_desp.round(2)))

##-------------------------------NUBLADOS-------------------------------------##

Nubla_dia = [ 20]
Nubla_mes = [ 4 ]

Sum_df_P975_nubla = pd.DataFrame()
for i in range(len(Nubla_mes)):
    a = Sum_df_P975.loc[(Sum_df_P975.index.month == Nubla_mes[i]) & (Sum_df_P975.index.day== Nubla_dia[i])]
    Sum_df_P975_nubla = pd.concat([Sum_df_P975_nubla, a])
    print(a.index)

Sum_df_P350_nubla = pd.DataFrame()
for i in range(len(Nubla_mes)):
    a = Sum_df_P350.loc[(Sum_df_P350.index.month == Nubla_mes[i]) & (Sum_df_P350.index.day== Nubla_dia[i])]
    Sum_df_P350_nubla = pd.concat([Sum_df_P350_nubla, a])
    print(a.index)

Sum_df_P348_nubla = pd.DataFrame()
for i in range(len(Nubla_mes)):
    a = Sum_df_P348.loc[(Sum_df_P348.index.month == Nubla_mes[i]) & (Sum_df_P348.index.day== Nubla_dia[i])]
    Sum_df_P348_nubla = pd.concat([Sum_df_P348_nubla, a])
    print(a.index)

Theo_nubla_975 = []
for i in range(len(Nubla_mes)):
    Theo_nubla_975.append(df_Theoric_sum['Rad_teo_348'].loc[(df_Theoric_sum.index.month == Nubla_mes[i]) & (df_Theoric_sum.index.day== Nubla_dia[i])].values[0])
Sum_df_P975_nubla['Rad_Teoric'] = Theo_nubla_975
Sum_df_P975_nubla['Prop'] = (Sum_df_P975_nubla['radiacion'] * 100)/Sum_df_P975_nubla['Rad_Teoric']

Theo_nubla_350 = []
for i in range(len(Nubla_mes)):
    Theo_nubla_350.append(df_Theoric_sum['Rad_teo_348'].loc[(df_Theoric_sum.index.month == Nubla_mes[i]) & (df_Theoric_sum.index.day== Nubla_dia[i])].values[0])
Sum_df_P350_nubla['Rad_Teoric'] = Theo_nubla_350
Sum_df_P350_nubla['Prop'] = (Sum_df_P350_nubla['radiacion'] * 100)/Sum_df_P350_nubla['Rad_Teoric']

Theo_nubla_348 = []
for i in range(len(Nubla_mes)):
    Theo_nubla_348.append(df_Theoric_sum['Rad_teo_348'].loc[(df_Theoric_sum.index.month == Nubla_mes[i]) & (df_Theoric_sum.index.day== Nubla_dia[i])].values[0])
Sum_df_P348_nubla['Rad_Teoric'] = Theo_nubla_348
Sum_df_P348_nubla['Prop'] = (Sum_df_P348_nubla['radiacion'] * 100)/Sum_df_P348_nubla['Rad_Teoric']

List_prop_nubla = []
if Sum_df_P348_nubla['Prop'].values > 0:
    List_prop_nubla.append(Sum_df_P348_nubla['Prop'].values[0])
if Sum_df_P350_nubla['Prop'].values > 0:
    List_prop_nubla.append(Sum_df_P350_nubla['Prop'].values[0])
if Sum_df_P975_nubla['Prop'].values > 0:
    List_prop_nubla.append(Sum_df_P975_nubla['Prop'].values[0])

if len(List_prop_nubla) > 1:
    Prop_umbral_nubla = np.nanmean(List_prop_nubla)
elif len(List_prop_nubla) == 1:
    Prop_umbral_nubla = List_prop_nubla [0]

print('Porcentaje para nublado = '+ str(Prop_umbral_nubla.round(2)))
