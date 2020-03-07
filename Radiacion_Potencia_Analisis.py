#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
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
import os

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##-----------------SECCION UNO: PROMEDIOS HORARIOS Y MENSUALES----------------##
#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Porgrama par aobterner los promedios horarios y mensuales de la radacion y la
potencia, dentro del periodo de registro de los paneles.
"""
################################################################################
## ----------ACOTANDO LAS FECHAS POR DIA Y MES PARA TOMAR LOS DATOS---------- ##
################################################################################

fi_m = 3
fi_d = 23
ff_m = 12
ff_d = 20
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
    df = df[(df['NI'] >= 0) & (df['strength'] >= 0)& (df['strength'] <= 100)]
    ## --------------------ACOTANDO LOS DATOS POR CALIDAD-------------------- ##
    if 'calidad' in df.columns:
        df = df[df['calidad']<100]
    df = df.between_time('06:00', '17:00')
    ## ---------------------AGRUPANDO LOS DATOS A HORAS---------------------- ##
    df_h = df.groupby(pd.Grouper(freq="H")).mean()
    df_h = df_h.between_time('06:00', '17:00')
    return df_h, df

df_P975_h, df_P975 = lectura_datos_piranometro(df_P975)
df_P350_h, df_P350 = lectura_datos_piranometro(df_P350)
df_P348_h, df_P348 = lectura_datos_piranometro(df_P348)

df_P975_h = df_P975_h[(df_P975_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P975_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

df_P350_h = df_P350_h[(df_P350_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P350_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

df_P348_h = df_P348_h[(df_P348_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P348_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

##############################################################################
## --------------------DESVIASIONES Y PROMEDIOS TEMPORALES----------------- ##
##############################################################################
df_P975_season_mean =  df_P975.groupby([df_P975.index.month, df_P975.index.hour]).mean()
df_P350_season_mean =  df_P350.groupby([df_P350.index.month, df_P350.index.hour]).mean()
df_P348_season_mean =  df_P348.groupby([df_P348.index.month, df_P348.index.hour]).mean()

df_P975_season_std =  df_P975.groupby([df_P975.index.month, df_P975.index.hour]).std()
df_P350_season_std =  df_P350.groupby([df_P350.index.month, df_P350.index.hour]).std()
df_P348_season_std =  df_P348.groupby([df_P348.index.month, df_P348.index.hour]).std()

##############################################################################
## ----------GRAFICA DE LAS DESVIASIONES Y PROMEDIOS TEMPORALES ----------- ##
##############################################################################

Hour = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
Month = [ 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
colors_list = ['#800000', '#e6194B', '#f58231', '#9A6324', '#bfef45', '#3cb44b', '#42d4f4', '#469990', '#000075', '#4363d8', '#911eb4', '#f032e6']

plt.close('all')
fig = plt.figure(figsize=(13,23))
ax1 = fig.add_subplot(3, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P350_season_mean.iloc[df_P350_season_mean.index.get_level_values(0) == i].radiacion.values
    ax1.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax1.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax1.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=20)
ax1.set_xticks(range(6, 18), minor=False)
ax1.set_xticklabels(Hour, minor=False, rotation = 20)
ax1.set_ylim(0, 1000)
ax1.set_title(u'Promedios horarios de radiacion \n por cada mes en el Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax2 = fig.add_subplot(3, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P350_season_std.iloc[df_P350_season_std.index.get_level_values(0) == i].radiacion.values
    ax2.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax2.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=20)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(Hour, minor=False, rotation = 20)
ax2.set_ylim(0, 600)
ax2.set_title(u'Desviasiones estándar de radiacion \n por cada mes en el Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax3 = fig.add_subplot(3, 2, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P975_season_mean.iloc[df_P975_season_mean.index.get_level_values(0) == i].radiacion.values
    ax3.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax3.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax3.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax3.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=20)
ax3.set_xticks(range(6, 18), minor=False)
ax3.set_xticklabels(Hour, minor=False, rotation = 20)
ax3.set_ylim(0, 1000)
ax3.set_title(u'Promedios horarios de radiacion \n por cada mes en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax4 = fig.add_subplot(3, 2, 4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P975_season_std.iloc[df_P975_season_std.index.get_level_values(0) == i].radiacion.values
    ax4.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax4.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax4.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax4.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=20)
ax4.set_xticks(range(6, 18), minor=False)
ax4.set_xticklabels(Hour, minor=False, rotation = 20)
ax4.set_ylim(0, 600)
ax4.set_title(u'Desviasiones estándar de radiacion \n por cada mes en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax5 = fig.add_subplot(3, 2, 5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P348_season_mean.iloc[df_P348_season_mean.index.get_level_values(0) == i].radiacion.values
    ax5.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax5.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax5.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax5.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=20)
ax5.set_xticks(range(6, 18), minor=False)
ax5.set_xticklabels(Hour, minor=False, rotation = 20)
ax5.set_ylim(0, 1000)
ax5.set_title(u'Promedios horarios de radiacion \n por cada mes en el Este', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax6 = fig.add_subplot(3, 2, 6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P348_season_std.iloc[df_P348_season_std.index.get_level_values(0) == i].radiacion.values
    ax6.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax6.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax6.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax6.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=20)
ax6.set_xticks(range(6, 18), minor=False)
ax6.set_xticklabels(Hour, minor=False, rotation = 20)
ax6.set_ylim(0, 600)
ax6.set_title(u'Desviasiones estándar de radiacion \n por cada mes en el Este', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/PromDesv_radiacion.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/PromDesv_radiacion.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')





Hour = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
Month = [ 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
colors_list = ['#800000', '#e6194B', '#f58231', '#9A6324', '#bfef45', '#3cb44b', '#42d4f4', '#469990', '#000075', '#4363d8', '#911eb4', '#f032e6']

plt.close('all')
fig = plt.figure(figsize=(13,23))
ax1 = fig.add_subplot(3, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P350_season_mean.iloc[df_P350_season_mean.index.get_level_values(0) == i].strength.values
    ax1.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax1.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax1.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=20)
ax1.set_xticks(range(6, 18), minor=False)
ax1.set_xticklabels(Hour, minor=False, rotation = 20)
ax1.set_ylim(0, 80)
ax1.set_title(u'Promedios horarios de potencia \n por cada mes en el Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax2 = fig.add_subplot(3, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P350_season_std.iloc[df_P350_season_std.index.get_level_values(0) == i].strength.values
    ax2.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax2.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=20)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(Hour, minor=False, rotation = 20)
ax2.set_ylim(0, 50)
ax2.set_title(u'Desviasiones estándar de potencia \n por cada mes en el Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax3 = fig.add_subplot(3, 2, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P975_season_mean.iloc[df_P975_season_mean.index.get_level_values(0) == i].strength.values
    ax3.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax3.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax3.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax3.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=20)
ax3.set_xticks(range(6, 18), minor=False)
ax3.set_xticklabels(Hour, minor=False, rotation = 20)
ax3.set_ylim(0, 80)
ax3.set_title(u'Promedios horarios de potencia \n por cada mes en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax4 = fig.add_subplot(3, 2, 4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P975_season_std.iloc[df_P975_season_std.index.get_level_values(0) == i].strength.values
    ax4.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax4.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax4.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax4.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=20)
ax4.set_xticks(range(6, 18), minor=False)
ax4.set_xticklabels(Hour, minor=False, rotation = 20)
ax4.set_ylim(0, 50)
ax4.set_title(u'Desviasiones estándar de potencia \n por cada mes en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax5 = fig.add_subplot(3, 2, 5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P348_season_mean.iloc[df_P348_season_mean.index.get_level_values(0) == i].strength.values
    ax5.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax5.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax5.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax5.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=20)
ax5.set_xticks(range(6, 18), minor=False)
ax5.set_xticklabels(Hour, minor=False, rotation = 20)
ax5.set_ylim(0, 80)
ax5.set_title(u'Promedios horarios de potencia \n por cada mes en el Este', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

ax6 = fig.add_subplot(3, 2, 6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
for i in range(3,len(Hour)+1):
    serie = df_P348_season_std.iloc[df_P348_season_std.index.get_level_values(0) == i].strength.values
    ax6.plot(Hour,  serie, color = colors_list[i-1], lw=1.5, label = Month[i-1])
    ax6.scatter(Hour,  serie, marker='.', c = colors_list[i-1], s=30)
ax6.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax6.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=20)
ax6.set_xticks(range(6, 18), minor=False)
ax6.set_xticklabels(Hour, minor=False, rotation = 20)
ax6.set_ylim(0, 50)
ax6.set_title(u'Desviasiones estándar de potencia \n por cada mes en el Este', loc = 'center', fontproperties = prop, fontsize=18)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/PromDesv_potencia.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/PromDesv_potencia.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


##-------------SECCION DOS: PROMEDIOS CASOS DEPEJADOS Y NUBLADOS-------------##
#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Porgrama para el establecimeinto de los promedios de potencia y radiacion bajo
condiciones despejadas y nubladas.
"""
###############################################################################
## ------------------LECTURA DE LOS DATOS RADIAION TEORICA------------------ ##
###############################################################################
df_Theoric = pd.read_csv("/home/nacorreasa/Maestria/Datos_Tesis/RadiacionTeorica_DataFrames/df_GIS.csv",  sep=',', index_col =0)
df_Theoric.index = pd.to_datetime(df_Theoric.index, format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_Theoric = df_Theoric[(df_Theoric.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_Theoric.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

"""
Se hace para los 15 minutos en los que se considedaron condiciones estables de radiacion
"""
df_P348_15m = df_P348.groupby(pd.Grouper(freq="15Min")).mean()
df_P350_15m = df_P350.groupby(pd.Grouper(freq="15Min")).mean()
df_P975_15m = df_P975.groupby(pd.Grouper(freq="15Min")).mean()

df_P348_15m  = df_P348_15m .between_time('06:00', '17:59')
df_P350_15m  = df_P350_15m .between_time('06:00', '17:59')
df_P975_15m  = df_P975_15m .between_time('06:00', '17:59')

df_result_348 = pd.concat([df_P348_15m, df_Theoric['Rad_teo_348']], axis=1)
df_result_350 = pd.concat([df_P350_15m, df_Theoric['Rad_teo_350']], axis=1)
df_result_975 = pd.concat([df_P975_15m, df_Theoric['Rad_teo_975']], axis=1)

"""
Se definen los escenarios para los los cuales trabajar
"""
horas_maniana = [6, 7, 8, 9]
horas_noon = [10, 11, 12, 13, 14]
horas_tarde = [15, 16, 17, 18]

DEF = [1, 2, 12]
MAM = [3, 4, 5]
JJA = [6, 7, 8]
SON = [9, 10, 11]

################################################################################
##----------------------------------------------------------------------------##
## ---- CASO NUBOSO :
################################################################################

df_result_348['Rad_deriv'] = np.gradient(df_result_348['radiacion'].values)
df_result_350['Rad_deriv'] = np.gradient(df_result_350['radiacion'].values)
df_result_975['Rad_deriv'] = np.gradient(df_result_975['radiacion'].values)


df_P348_15m_Nuba_Morning = df_result_348.between_time('06:00','11:59')
df_P348_15m_Nuba_Afternoon = df_result_348.between_time('12:00','17:59')
df_P350_15m_Nuba_Morning = df_result_350.between_time('06:00','11:59')
df_P350_15m_Nuba_Afternoon = df_result_350.between_time('12:00','17:59')
df_P975_15m_Nuba_Morning = df_result_975.between_time('06:00','11:59')
df_P975_15m_Nuba_Afternoon = df_result_975.between_time('12:00','17:59')

################################################################################
##--------------------------------------348-----------------------------------##
################################################################################
df_P348_Ref_Morning = df_P348_15m_Nuba_Morning[df_P348_15m_Nuba_Morning['Rad_deriv']<0]
df_P348_Ref_Afternoon = df_P348_15m_Nuba_Afternoon[df_P348_15m_Nuba_Afternoon['Rad_deriv']>0]
df_348_Ref = pd.concat([df_P348_Ref_Morning, df_P348_Ref_Afternoon]).sort_index()

df_348_Nuba =pd.DataFrame()
for i in range(len(df_348_Ref.index )):
    df_348_Nuba = df_348_Nuba.append(df_P348[(df_P348.index>=df_348_Ref.index[i]) & (df_P348.index<=df_348_Ref.index[i] +timedelta(minutes=15))])

##------------>>> MANIANA
df_348_Nuba_m = df_348_Nuba[(df_348_Nuba.index.hour == horas_maniana[0])| (df_348_Nuba.index.hour == horas_maniana[1])| (df_348_Nuba.index.hour == horas_maniana[2])|(df_348_Nuba.index.hour == horas_maniana[3]) ]
df_348_Nuba_m_DEF =df_348_Nuba_m[(df_348_Nuba_m.index.month == DEF[0])| (df_348_Nuba_m.index.month == DEF[1])| (df_348_Nuba_m.index.month == DEF[2])]
df_348_Nuba_m_MAM =df_348_Nuba_m[(df_348_Nuba_m.index.month == MAM[0])| (df_348_Nuba_m.index.month == MAM[1])| (df_348_Nuba_m.index.month == MAM[2])]
df_348_Nuba_m_JJA =df_348_Nuba_m[(df_348_Nuba_m.index.month == JJA[0])| (df_348_Nuba_m.index.month == JJA[1])| (df_348_Nuba_m.index.month == JJA[2])]
df_348_Nuba_m_SON =df_348_Nuba_m[(df_348_Nuba_m.index.month == SON[0])| (df_348_Nuba_m.index.month == SON[1])| (df_348_Nuba_m.index.month == SON[2])]

mean_radiacion_Nuba_348_m = [np.nanmean(df_348_Nuba_m_DEF.radiacion.values), np.nanmean(df_348_Nuba_m_MAM.radiacion.values), np.nanmean(df_348_Nuba_m_JJA.radiacion.values), np.nanmean(df_348_Nuba_m_SON.radiacion.values)]
std_radiacion_Nuba_348_m = [np.nanstd(df_348_Nuba_m_DEF.radiacion.values), np.nanstd(df_348_Nuba_m_MAM.radiacion.values), np.nanstd(df_348_Nuba_m_JJA.radiacion.values), np.nanstd(df_348_Nuba_m_SON.radiacion.values)]

mean_strength_Nuba_348_m = [np.nanmean(df_348_Nuba_m_DEF.strength.values), np.nanmean(df_348_Nuba_m_MAM.strength.values), np.nanmean(df_348_Nuba_m_JJA.strength.values), np.nanmean(df_348_Nuba_m_SON.strength.values)]
std_strength_Nuba_348_m = [np.nanstd(df_348_Nuba_m_DEF.strength.values), np.nanstd(df_348_Nuba_m_MAM.strength.values), np.nanstd(df_348_Nuba_m_JJA.strength.values), np.nanstd(df_348_Nuba_m_SON.strength.values)]

##------------>>> MEDIO DIA
df_348_Nuba_n = df_348_Nuba[(df_348_Nuba.index.hour == horas_noon[0])| (df_348_Nuba.index.hour == horas_noon[1])| (df_348_Nuba.index.hour == horas_noon[2])|(df_348_Nuba.index.hour == horas_noon[3]) |(df_348_Nuba.index.hour == horas_noon[4])]
df_348_Nuba_n_DEF =df_348_Nuba_n[(df_348_Nuba_n.index.month == DEF[0])| (df_348_Nuba_n.index.month == DEF[1])| (df_348_Nuba_n.index.month == DEF[2])]
df_348_Nuba_n_MAM =df_348_Nuba_n[(df_348_Nuba_n.index.month == MAM[0])| (df_348_Nuba_n.index.month == MAM[1])| (df_348_Nuba_n.index.month == MAM[2])]
df_348_Nuba_n_JJA =df_348_Nuba_n[(df_348_Nuba_n.index.month == JJA[0])| (df_348_Nuba_n.index.month == JJA[1])| (df_348_Nuba_n.index.month == JJA[2])]
df_348_Nuba_n_SON =df_348_Nuba_n[(df_348_Nuba_n.index.month == SON[0])| (df_348_Nuba_n.index.month == SON[1])| (df_348_Nuba_n.index.month == SON[2])]

mean_radiacion_Nuba_348_n = [np.nanmean(df_348_Nuba_n_DEF.radiacion.values), np.nanmean(df_348_Nuba_n_MAM.radiacion.values), np.nanmean(df_348_Nuba_n_JJA.radiacion.values), np.nanmean(df_348_Nuba_n_SON.radiacion.values)]
std_radiacion_Nuba_348_n = [np.nanstd(df_348_Nuba_n_DEF.radiacion.values), np.nanstd(df_348_Nuba_n_MAM.radiacion.values), np.nanstd(df_348_Nuba_n_JJA.radiacion.values), np.nanstd(df_348_Nuba_n_SON.radiacion.values)]

mean_strength_Nuba_348_n = [np.nanmean(df_348_Nuba_n_DEF.strength.values), np.nanmean(df_348_Nuba_n_MAM.strength.values), np.nanmean(df_348_Nuba_n_JJA.strength.values), np.nanmean(df_348_Nuba_n_SON.strength.values)]
std_strength_Nuba_348_n = [np.nanstd(df_348_Nuba_n_DEF.strength.values), np.nanstd(df_348_Nuba_n_MAM.strength.values), np.nanstd(df_348_Nuba_n_JJA.strength.values), np.nanstd(df_348_Nuba_n_SON.strength.values)]

##------------>>> TARDE
df_348_Nuba_t = df_348_Nuba[(df_348_Nuba.index.hour == horas_tarde[0])| (df_348_Nuba.index.hour == horas_tarde[1])| (df_348_Nuba.index.hour == horas_tarde[2])|(df_348_Nuba.index.hour == horas_tarde[3]) ]
df_348_Nuba_t_DEF =df_348_Nuba_t[(df_348_Nuba_t.index.month == DEF[0])| (df_348_Nuba_t.index.month == DEF[1])| (df_348_Nuba_t.index.month == DEF[2])]
df_348_Nuba_t_MAM =df_348_Nuba_t[(df_348_Nuba_t.index.month == MAM[0])| (df_348_Nuba_t.index.month == MAM[1])| (df_348_Nuba_t.index.month == MAM[2])]
df_348_Nuba_t_JJA =df_348_Nuba_t[(df_348_Nuba_t.index.month == JJA[0])| (df_348_Nuba_t.index.month == JJA[1])| (df_348_Nuba_t.index.month == JJA[2])]
df_348_Nuba_t_SON =df_348_Nuba_t[(df_348_Nuba_t.index.month == SON[0])| (df_348_Nuba_t.index.month == SON[1])| (df_348_Nuba_t.index.month == SON[2])]

mean_radiacion_Nuba_348_t = [np.nanmean(df_348_Nuba_t_DEF.radiacion.values), np.nanmean(df_348_Nuba_t_MAM.radiacion.values), np.nanmean(df_348_Nuba_t_JJA.radiacion.values), np.nanmean(df_348_Nuba_t_SON.radiacion.values)]
std_radiacion_Nuba_348_t = [np.nanstd(df_348_Nuba_t_DEF.radiacion.values), np.nanstd(df_348_Nuba_t_MAM.radiacion.values), np.nanstd(df_348_Nuba_t_JJA.radiacion.values), np.nanstd(df_348_Nuba_t_SON.radiacion.values)]

mean_strength_Nuba_348_t = [np.nanmean(df_348_Nuba_t_DEF.strength.values), np.nanmean(df_348_Nuba_t_MAM.strength.values), np.nanmean(df_348_Nuba_t_JJA.strength.values), np.nanmean(df_348_Nuba_t_SON.strength.values)]
std_strength_Nuba_348_t = [np.nanstd(df_348_Nuba_t_DEF.strength.values), np.nanstd(df_348_Nuba_t_MAM.strength.values), np.nanstd(df_348_Nuba_t_JJA.strength.values), np.nanstd(df_348_Nuba_t_SON.strength.values)]

################################################################################
##--------------------------------------350-----------------------------------##
################################################################################
df_P350_Ref_Morning = df_P350_15m_Nuba_Morning[df_P350_15m_Nuba_Morning['Rad_deriv']<0]
df_P350_Ref_Afternoon = df_P350_15m_Nuba_Afternoon[df_P350_15m_Nuba_Afternoon['Rad_deriv']>0]
df_350_Ref = pd.concat([df_P350_Ref_Morning, df_P350_Ref_Afternoon]).sort_index()

df_350_Nuba =pd.DataFrame()
for i in range(len(df_350_Ref.index )):
    df_350_Nuba = df_350_Nuba.append(df_P350[(df_P350.index>=df_350_Ref.index[i]) & (df_P350.index<=df_350_Ref.index[i] +timedelta(minutes=15))])

##------------>>> MANIANA
df_350_Nuba_m = df_350_Nuba[(df_350_Nuba.index.hour == horas_maniana[0])| (df_350_Nuba.index.hour == horas_maniana[1])| (df_350_Nuba.index.hour == horas_maniana[2])|(df_350_Nuba.index.hour == horas_maniana[3]) ]
df_350_Nuba_m_DEF =df_350_Nuba_m[(df_350_Nuba_m.index.month == DEF[0])| (df_350_Nuba_m.index.month == DEF[1])| (df_350_Nuba_m.index.month == DEF[2])]
df_350_Nuba_m_MAM =df_350_Nuba_m[(df_350_Nuba_m.index.month == MAM[0])| (df_350_Nuba_m.index.month == MAM[1])| (df_350_Nuba_m.index.month == MAM[2])]
df_350_Nuba_m_JJA =df_350_Nuba_m[(df_350_Nuba_m.index.month == JJA[0])| (df_350_Nuba_m.index.month == JJA[1])| (df_350_Nuba_m.index.month == JJA[2])]
df_350_Nuba_m_SON =df_350_Nuba_m[(df_350_Nuba_m.index.month == SON[0])| (df_350_Nuba_m.index.month == SON[1])| (df_350_Nuba_m.index.month == SON[2])]

mean_radiacion_Nuba_350_m = [np.nanmean(df_350_Nuba_m_DEF.radiacion.values), np.nanmean(df_350_Nuba_m_MAM.radiacion.values), np.nanmean(df_350_Nuba_m_JJA.radiacion.values), np.nanmean(df_350_Nuba_m_SON.radiacion.values)]
std_radiacion_Nuba_350_m = [np.nanstd(df_350_Nuba_m_DEF.radiacion.values), np.nanstd(df_350_Nuba_m_MAM.radiacion.values), np.nanstd(df_350_Nuba_m_JJA.radiacion.values), np.nanstd(df_350_Nuba_m_SON.radiacion.values)]

mean_strength_Nuba_350_m = [np.nanmean(df_350_Nuba_m_DEF.strength.values), np.nanmean(df_350_Nuba_m_MAM.strength.values), np.nanmean(df_350_Nuba_m_JJA.strength.values), np.nanmean(df_350_Nuba_m_SON.strength.values)]
std_strength_Nuba_350_m = [np.nanstd(df_350_Nuba_m_DEF.strength.values), np.nanstd(df_350_Nuba_m_MAM.strength.values), np.nanstd(df_350_Nuba_m_JJA.strength.values), np.nanstd(df_350_Nuba_m_SON.strength.values)]

##------------>>> MEDIO DIA
df_350_Nuba_n = df_350_Nuba[(df_350_Nuba.index.hour == horas_noon[0])| (df_350_Nuba.index.hour == horas_noon[1])| (df_350_Nuba.index.hour == horas_noon[2])|(df_350_Nuba.index.hour == horas_noon[3]) |(df_350_Nuba.index.hour == horas_noon[4])]
df_350_Nuba_n_DEF =df_350_Nuba_n[(df_350_Nuba_n.index.month == DEF[0])| (df_350_Nuba_n.index.month == DEF[1])| (df_350_Nuba_n.index.month == DEF[2])]
df_350_Nuba_n_MAM =df_350_Nuba_n[(df_350_Nuba_n.index.month == MAM[0])| (df_350_Nuba_n.index.month == MAM[1])| (df_350_Nuba_n.index.month == MAM[2])]
df_350_Nuba_n_JJA =df_350_Nuba_n[(df_350_Nuba_n.index.month == JJA[0])| (df_350_Nuba_n.index.month == JJA[1])| (df_350_Nuba_n.index.month == JJA[2])]
df_350_Nuba_n_SON =df_350_Nuba_n[(df_350_Nuba_n.index.month == SON[0])| (df_350_Nuba_n.index.month == SON[1])| (df_350_Nuba_n.index.month == SON[2])]

mean_radiacion_Nuba_350_n = [np.nanmean(df_350_Nuba_n_DEF.radiacion.values), np.nanmean(df_350_Nuba_n_MAM.radiacion.values), np.nanmean(df_350_Nuba_n_JJA.radiacion.values), np.nanmean(df_350_Nuba_n_SON.radiacion.values)]
std_radiacion_Nuba_350_n = [np.nanstd(df_350_Nuba_n_DEF.radiacion.values), np.nanstd(df_350_Nuba_n_MAM.radiacion.values), np.nanstd(df_350_Nuba_n_JJA.radiacion.values), np.nanstd(df_350_Nuba_n_SON.radiacion.values)]

mean_strength_Nuba_350_n = [np.nanmean(df_350_Nuba_n_DEF.strength.values), np.nanmean(df_350_Nuba_n_MAM.strength.values), np.nanmean(df_350_Nuba_n_JJA.strength.values), np.nanmean(df_350_Nuba_n_SON.strength.values)]
std_strength_Nuba_350_n = [np.nanstd(df_350_Nuba_n_DEF.strength.values), np.nanstd(df_350_Nuba_n_MAM.strength.values), np.nanstd(df_350_Nuba_n_JJA.strength.values), np.nanstd(df_350_Nuba_n_SON.strength.values)]

##------------>>> TARDE
df_350_Nuba_t = df_350_Nuba[(df_350_Nuba.index.hour == horas_tarde[0])| (df_350_Nuba.index.hour == horas_tarde[1])| (df_350_Nuba.index.hour == horas_tarde[2])|(df_350_Nuba.index.hour == horas_tarde[3]) ]
df_350_Nuba_t_DEF =df_350_Nuba_t[(df_350_Nuba_t.index.month == DEF[0])| (df_350_Nuba_t.index.month == DEF[1])| (df_350_Nuba_t.index.month == DEF[2])]
df_350_Nuba_t_MAM =df_350_Nuba_t[(df_350_Nuba_t.index.month == MAM[0])| (df_350_Nuba_t.index.month == MAM[1])| (df_350_Nuba_t.index.month == MAM[2])]
df_350_Nuba_t_JJA =df_350_Nuba_t[(df_350_Nuba_t.index.month == JJA[0])| (df_350_Nuba_t.index.month == JJA[1])| (df_350_Nuba_t.index.month == JJA[2])]
df_350_Nuba_t_SON =df_350_Nuba_t[(df_350_Nuba_t.index.month == SON[0])| (df_350_Nuba_t.index.month == SON[1])| (df_350_Nuba_t.index.month == SON[2])]

mean_radiacion_Nuba_350_t = [np.nanmean(df_350_Nuba_t_DEF.radiacion.values), np.nanmean(df_350_Nuba_t_MAM.radiacion.values), np.nanmean(df_350_Nuba_t_JJA.radiacion.values), np.nanmean(df_350_Nuba_t_SON.radiacion.values)]
std_radiacion_Nuba_350_t = [np.nanstd(df_350_Nuba_t_DEF.radiacion.values), np.nanstd(df_350_Nuba_t_MAM.radiacion.values), np.nanstd(df_350_Nuba_t_JJA.radiacion.values), np.nanstd(df_350_Nuba_t_SON.radiacion.values)]

mean_strength_Nuba_350_t = [np.nanmean(df_350_Nuba_t_DEF.strength.values), np.nanmean(df_350_Nuba_t_MAM.strength.values), np.nanmean(df_350_Nuba_t_JJA.strength.values), np.nanmean(df_350_Nuba_t_SON.strength.values)]
std_strength_Nuba_350_t = [np.nanstd(df_350_Nuba_t_DEF.strength.values), np.nanstd(df_350_Nuba_t_MAM.strength.values), np.nanstd(df_350_Nuba_t_JJA.strength.values), np.nanstd(df_350_Nuba_t_SON.strength.values)]

################################################################################
##--------------------------------------975-----------------------------------##
################################################################################
df_P975_Ref_Morning = df_P975_15m_Nuba_Morning[df_P975_15m_Nuba_Morning['Rad_deriv']<0]
df_P975_Ref_Afternoon = df_P975_15m_Nuba_Afternoon[df_P975_15m_Nuba_Afternoon['Rad_deriv']>0]
df_975_Ref = pd.concat([df_P975_Ref_Morning, df_P975_Ref_Afternoon]).sort_index()

df_975_Nuba =pd.DataFrame()
for i in range(len(df_975_Ref.index )):
    df_975_Nuba = df_975_Nuba.append(df_P975[(df_P975.index>=df_975_Ref.index[i]) & (df_P975.index<=df_975_Ref.index[i] +timedelta(minutes=15))])

##------------>>> MANIANA
df_975_Nuba_m = df_975_Nuba[(df_975_Nuba.index.hour == horas_maniana[0])| (df_975_Nuba.index.hour == horas_maniana[1])| (df_975_Nuba.index.hour == horas_maniana[2])|(df_975_Nuba.index.hour == horas_maniana[3]) ]
df_975_Nuba_m_DEF =df_975_Nuba_m[(df_975_Nuba_m.index.month == DEF[0])| (df_975_Nuba_m.index.month == DEF[1])| (df_975_Nuba_m.index.month == DEF[2])]
df_975_Nuba_m_MAM =df_975_Nuba_m[(df_975_Nuba_m.index.month == MAM[0])| (df_975_Nuba_m.index.month == MAM[1])| (df_975_Nuba_m.index.month == MAM[2])]
df_975_Nuba_m_JJA =df_975_Nuba_m[(df_975_Nuba_m.index.month == JJA[0])| (df_975_Nuba_m.index.month == JJA[1])| (df_975_Nuba_m.index.month == JJA[2])]
df_975_Nuba_m_SON =df_975_Nuba_m[(df_975_Nuba_m.index.month == SON[0])| (df_975_Nuba_m.index.month == SON[1])| (df_975_Nuba_m.index.month == SON[2])]

mean_radiacion_Nuba_975_m = [np.nanmean(df_975_Nuba_m_DEF.radiacion.values), np.nanmean(df_975_Nuba_m_MAM.radiacion.values), np.nanmean(df_975_Nuba_m_JJA.radiacion.values), np.nanmean(df_975_Nuba_m_SON.radiacion.values)]
std_radiacion_Nuba_975_m = [np.nanstd(df_975_Nuba_m_DEF.radiacion.values), np.nanstd(df_975_Nuba_m_MAM.radiacion.values), np.nanstd(df_975_Nuba_m_JJA.radiacion.values), np.nanstd(df_975_Nuba_m_SON.radiacion.values)]

mean_strength_Nuba_975_m = [np.nanmean(df_975_Nuba_m_DEF.strength.values), np.nanmean(df_975_Nuba_m_MAM.strength.values), np.nanmean(df_975_Nuba_m_JJA.strength.values), np.nanmean(df_975_Nuba_m_SON.strength.values)]
std_strength_Nuba_975_m = [np.nanstd(df_975_Nuba_m_DEF.strength.values), np.nanstd(df_975_Nuba_m_MAM.strength.values), np.nanstd(df_975_Nuba_m_JJA.strength.values), np.nanstd(df_975_Nuba_m_SON.strength.values)]

##------------>>> MEDIO DIA
df_975_Nuba_n = df_975_Nuba[(df_975_Nuba.index.hour == horas_noon[0])| (df_975_Nuba.index.hour == horas_noon[1])| (df_975_Nuba.index.hour == horas_noon[2])|(df_975_Nuba.index.hour == horas_noon[3]) |(df_975_Nuba.index.hour == horas_noon[4])]
df_975_Nuba_n_DEF =df_975_Nuba_n[(df_975_Nuba_n.index.month == DEF[0])| (df_975_Nuba_n.index.month == DEF[1])| (df_975_Nuba_n.index.month == DEF[2])]
df_975_Nuba_n_MAM =df_975_Nuba_n[(df_975_Nuba_n.index.month == MAM[0])| (df_975_Nuba_n.index.month == MAM[1])| (df_975_Nuba_n.index.month == MAM[2])]
df_975_Nuba_n_JJA =df_975_Nuba_n[(df_975_Nuba_n.index.month == JJA[0])| (df_975_Nuba_n.index.month == JJA[1])| (df_975_Nuba_n.index.month == JJA[2])]
df_975_Nuba_n_SON =df_975_Nuba_n[(df_975_Nuba_n.index.month == SON[0])| (df_975_Nuba_n.index.month == SON[1])| (df_975_Nuba_n.index.month == SON[2])]

mean_radiacion_Nuba_975_n = [np.nanmean(df_975_Nuba_n_DEF.radiacion.values), np.nanmean(df_975_Nuba_n_MAM.radiacion.values), np.nanmean(df_975_Nuba_n_JJA.radiacion.values), np.nanmean(df_975_Nuba_n_SON.radiacion.values)]
std_radiacion_Nuba_975_n = [np.nanstd(df_975_Nuba_n_DEF.radiacion.values), np.nanstd(df_975_Nuba_n_MAM.radiacion.values), np.nanstd(df_975_Nuba_n_JJA.radiacion.values), np.nanstd(df_975_Nuba_n_SON.radiacion.values)]

mean_strength_Nuba_975_n = [np.nanmean(df_975_Nuba_n_DEF.strength.values), np.nanmean(df_975_Nuba_n_MAM.strength.values), np.nanmean(df_975_Nuba_n_JJA.strength.values), np.nanmean(df_975_Nuba_n_SON.strength.values)]
std_strength_Nuba_975_n = [np.nanstd(df_975_Nuba_n_DEF.strength.values), np.nanstd(df_975_Nuba_n_MAM.strength.values), np.nanstd(df_975_Nuba_n_JJA.strength.values), np.nanstd(df_975_Nuba_n_SON.strength.values)]

##------------>>> TARDE
df_975_Nuba_t = df_975_Nuba[(df_975_Nuba.index.hour == horas_tarde[0])| (df_975_Nuba.index.hour == horas_tarde[1])| (df_975_Nuba.index.hour == horas_tarde[2])|(df_975_Nuba.index.hour == horas_tarde[3]) ]
df_975_Nuba_t_DEF =df_975_Nuba_t[(df_975_Nuba_t.index.month == DEF[0])| (df_975_Nuba_t.index.month == DEF[1])| (df_975_Nuba_t.index.month == DEF[2])]
df_975_Nuba_t_MAM =df_975_Nuba_t[(df_975_Nuba_t.index.month == MAM[0])| (df_975_Nuba_t.index.month == MAM[1])| (df_975_Nuba_t.index.month == MAM[2])]
df_975_Nuba_t_JJA =df_975_Nuba_t[(df_975_Nuba_t.index.month == JJA[0])| (df_975_Nuba_t.index.month == JJA[1])| (df_975_Nuba_t.index.month == JJA[2])]
df_975_Nuba_t_SON =df_975_Nuba_t[(df_975_Nuba_t.index.month == SON[0])| (df_975_Nuba_t.index.month == SON[1])| (df_975_Nuba_t.index.month == SON[2])]

mean_radiacion_Nuba_975_t = [np.nanmean(df_975_Nuba_t_DEF.radiacion.values), np.nanmean(df_975_Nuba_t_MAM.radiacion.values), np.nanmean(df_975_Nuba_t_JJA.radiacion.values), np.nanmean(df_975_Nuba_t_SON.radiacion.values)]
std_radiacion_Nuba_975_t = [np.nanstd(df_975_Nuba_t_DEF.radiacion.values), np.nanstd(df_975_Nuba_t_MAM.radiacion.values), np.nanstd(df_975_Nuba_t_JJA.radiacion.values), np.nanstd(df_975_Nuba_t_SON.radiacion.values)]

mean_strength_Nuba_975_t = [np.nanmean(df_975_Nuba_t_DEF.strength.values), np.nanmean(df_975_Nuba_t_MAM.strength.values), np.nanmean(df_975_Nuba_t_JJA.strength.values), np.nanmean(df_975_Nuba_t_SON.strength.values)]
std_strength_Nuba_975_t = [np.nanstd(df_975_Nuba_t_DEF.strength.values), np.nanstd(df_975_Nuba_t_MAM.strength.values), np.nanstd(df_975_Nuba_t_JJA.strength.values), np.nanstd(df_975_Nuba_t_SON.strength.values)]

################################################################################
##----------------------------------------------------------------------------##
## ---- CASO DESPEJADO:
################################################################################

################################################################################
##-------------------------------------348------------------------------------##
################################################################################
df_P348_15m_Desp = pd.DataFrame()
for i in range(len(df_result_348)):
    for j in range(len( df_Theoric['Rad_teo_348'].index)):
        if (df_result_348['radiacion'].index[i].month == df_Theoric['Rad_teo_348'].index[j].month) and (df_result_348['radiacion'].index[i].hour == df_Theoric['Rad_teo_348'].index[j].hour):
            if (df_result_348['radiacion'].iloc[i] >= 0.99 * df_Theoric['Rad_teo_348'].iloc[j]):
                df_P348_15m_Desp = df_P348_15m_Desp.append(pd.DataFrame(df_result_348.iloc[[i]]))
            else:
                pass
        else:
            pass

df_P348_15m_Desp =  df_P348_15m_Desp.loc[~df_P348_15m_Desp.index.duplicated(keep='first')]

df_348_Desp =pd.DataFrame()
for i in range(len(df_P348_15m_Desp.index )):
        df_348_Desp = df_348_Desp.append(df_P348[(df_P348.index>=df_P348_15m_Desp.index[i]) & (df_P348.index<=df_P348_15m_Desp.index[i] +timedelta(minutes=15))])

##------------>>> MANIANA

df_348_Desp_m = df_348_Desp[(df_348_Desp.index.hour == horas_maniana[0])| (df_348_Desp.index.hour == horas_maniana[1])| (df_348_Desp.index.hour == horas_maniana[2])|(df_348_Desp.index.hour == horas_maniana[3]) ]
df_348_Desp_m_DEF =df_348_Desp_m[(df_348_Desp_m.index.month == DEF[0])| (df_348_Desp_m.index.month == DEF[1])| (df_348_Desp_m.index.month == DEF[2])]
df_348_Desp_m_MAM =df_348_Desp_m[(df_348_Desp_m.index.month == MAM[0])| (df_348_Desp_m.index.month == MAM[1])| (df_348_Desp_m.index.month == MAM[2])]
df_348_Desp_m_JJA =df_348_Desp_m[(df_348_Desp_m.index.month == JJA[0])| (df_348_Desp_m.index.month == JJA[1])| (df_348_Desp_m.index.month == JJA[2])]
df_348_Desp_m_SON =df_348_Desp_m[(df_348_Desp_m.index.month == SON[0])| (df_348_Desp_m.index.month == SON[1])| (df_348_Desp_m.index.month == SON[2])]

mean_radiacion_Desp_348_m = [np.nanmean(df_348_Desp_m_DEF.radiacion.values), np.nanmean(df_348_Desp_m_MAM.radiacion.values), np.nanmean(df_348_Desp_m_JJA.radiacion.values), np.nanmean(df_348_Desp_m_SON.radiacion.values)]
std_radiacion_Desp_348_m = [np.nanstd(df_348_Desp_m_DEF.radiacion.values), np.nanstd(df_348_Desp_m_MAM.radiacion.values), np.nanstd(df_348_Desp_m_JJA.radiacion.values), np.nanstd(df_348_Desp_m_SON.radiacion.values)]

mean_strength_Desp_348_m = [np.nanmean(df_348_Desp_m_DEF.strength.values), np.nanmean(df_348_Desp_m_MAM.strength.values), np.nanmean(df_348_Desp_m_JJA.strength.values), np.nanmean(df_348_Desp_m_SON.strength.values)]
std_strength_Desp_348_m = [np.nanstd(df_348_Desp_m_DEF.strength.values), np.nanstd(df_348_Desp_m_MAM.strength.values), np.nanstd(df_348_Desp_m_JJA.strength.values), np.nanstd(df_348_Desp_m_SON.strength.values)]

##------------>>> MEDIO DIA

df_348_Desp_n = df_348_Desp[(df_348_Desp.index.hour == horas_noon[0])| (df_348_Desp.index.hour == horas_noon[1])| (df_348_Desp.index.hour == horas_noon[2])|(df_348_Desp.index.hour == horas_noon[3])|(df_348_Desp.index.hour == horas_noon[4]) ]
df_348_Desp_n_DEF =df_348_Desp_n[(df_348_Desp_n.index.month == DEF[0])| (df_348_Desp_n.index.month == DEF[1])| (df_348_Desp_n.index.month == DEF[2])]
df_348_Desp_n_MAM =df_348_Desp_n[(df_348_Desp_n.index.month == MAM[0])| (df_348_Desp_n.index.month == MAM[1])| (df_348_Desp_n.index.month == MAM[2])]
df_348_Desp_n_JJA =df_348_Desp_n[(df_348_Desp_n.index.month == JJA[0])| (df_348_Desp_n.index.month == JJA[1])| (df_348_Desp_n.index.month == JJA[2])]
df_348_Desp_n_SON =df_348_Desp_n[(df_348_Desp_n.index.month == SON[0])| (df_348_Desp_n.index.month == SON[1])| (df_348_Desp_n.index.month == SON[2])]

mean_radiacion_Desp_348_n = [np.nanmean(df_348_Desp_n_DEF.radiacion.values), np.nanmean(df_348_Desp_n_MAM.radiacion.values), np.nanmean(df_348_Desp_n_JJA.radiacion.values), np.nanmean(df_348_Desp_n_SON.radiacion.values)]
std_radiacion_Desp_348_n = [np.nanstd(df_348_Desp_n_DEF.radiacion.values), np.nanstd(df_348_Desp_n_MAM.radiacion.values), np.nanstd(df_348_Desp_n_JJA.radiacion.values), np.nanstd(df_348_Desp_n_SON.radiacion.values)]

mean_strength_Desp_348_n = [np.nanmean(df_348_Desp_n_DEF.strength.values), np.nanmean(df_348_Desp_n_MAM.strength.values), np.nanmean(df_348_Desp_n_JJA.strength.values), np.nanmean(df_348_Desp_n_SON.strength.values)]
std_strength_Desp_348_n = [np.nanstd(df_348_Desp_n_DEF.strength.values), np.nanstd(df_348_Desp_n_MAM.strength.values), np.nanstd(df_348_Desp_n_JJA.strength.values), np.nanstd(df_348_Desp_n_SON.strength.values)]

##------------>>> TARDE

df_348_Desp_t = df_348_Desp[(df_348_Desp.index.hour == horas_tarde[0])| (df_348_Desp.index.hour == horas_tarde[1])| (df_348_Desp.index.hour == horas_tarde[2])|(df_348_Desp.index.hour == horas_tarde[3]) ]
df_348_Desp_t_DEF =df_348_Desp_t[(df_348_Desp_t.index.month == DEF[0])| (df_348_Desp_t.index.month == DEF[1])| (df_348_Desp_t.index.month == DEF[2])]
df_348_Desp_t_MAM =df_348_Desp_t[(df_348_Desp_t.index.month == MAM[0])| (df_348_Desp_t.index.month == MAM[1])| (df_348_Desp_t.index.month == MAM[2])]
df_348_Desp_t_JJA =df_348_Desp_t[(df_348_Desp_t.index.month == JJA[0])| (df_348_Desp_t.index.month == JJA[1])| (df_348_Desp_t.index.month == JJA[2])]
df_348_Desp_t_SON =df_348_Desp_t[(df_348_Desp_t.index.month == SON[0])| (df_348_Desp_t.index.month == SON[1])| (df_348_Desp_t.index.month == SON[2])]

mean_radiacion_Desp_348_t = [np.nanmean(df_348_Desp_t_DEF.radiacion.values), np.nanmean(df_348_Desp_t_MAM.radiacion.values), np.nanmean(df_348_Desp_t_JJA.radiacion.values), np.nanmean(df_348_Desp_t_SON.radiacion.values)]
std_radiacion_Desp_348_t = [np.nanstd(df_348_Desp_t_DEF.radiacion.values), np.nanstd(df_348_Desp_t_MAM.radiacion.values), np.nanstd(df_348_Desp_t_JJA.radiacion.values), np.nanstd(df_348_Desp_t_SON.radiacion.values)]

mean_strength_Desp_348_t = [np.nanmean(df_348_Desp_t_DEF.strength.values), np.nanmean(df_348_Desp_t_MAM.strength.values), np.nanmean(df_348_Desp_t_JJA.strength.values), np.nanmean(df_348_Desp_t_SON.strength.values)]
std_strength_Desp_348_t = [np.nanstd(df_348_Desp_t_DEF.strength.values), np.nanstd(df_348_Desp_t_MAM.strength.values), np.nanstd(df_348_Desp_t_JJA.strength.values), np.nanstd(df_348_Desp_t_SON.strength.values)]


################################################################################
##-------------------------------------350------------------------------------##
################################################################################
df_P350_15m_Desp = pd.DataFrame()
for i in range(len(df_result_350)):
    for j in range(len( df_Theoric['Rad_teo_350'].index)):
        if (df_result_350['radiacion'].index[i].month == df_Theoric['Rad_teo_350'].index[j].month) and (df_result_350['radiacion'].index[i].hour == df_Theoric['Rad_teo_350'].index[j].hour):
            if (df_result_350['radiacion'].iloc[i] >= 0.99 * df_Theoric['Rad_teo_350'].iloc[j]):
                df_P350_15m_Desp = df_P350_15m_Desp.append(pd.DataFrame(df_result_350.iloc[[i]]))
            else:
                pass
        else:
            pass

df_P350_15m_Desp =  df_P350_15m_Desp.loc[~df_P350_15m_Desp.index.duplicated(keep='first')]

df_350_Desp =pd.DataFrame()
for i in range(len(df_P350_15m_Desp.index )):
    df_350_Desp = df_350_Desp.append(df_P350[(df_P350.index>=df_P350_15m_Desp.index[i]) & (df_P350.index<=df_P350_15m_Desp.index[i] +timedelta(minutes=15))])

##------------>>> MANIANA

df_350_Desp_m = df_350_Desp[(df_350_Desp.index.hour == horas_maniana[0])| (df_350_Desp.index.hour == horas_maniana[1])| (df_350_Desp.index.hour == horas_maniana[2])|(df_350_Desp.index.hour == horas_maniana[3]) ]
df_350_Desp_m_DEF =df_350_Desp_m[(df_350_Desp_m.index.month == DEF[0])| (df_350_Desp_m.index.month == DEF[1])| (df_350_Desp_m.index.month == DEF[2])]
df_350_Desp_m_MAM =df_350_Desp_m[(df_350_Desp_m.index.month == MAM[0])| (df_350_Desp_m.index.month == MAM[1])| (df_350_Desp_m.index.month == MAM[2])]
df_350_Desp_m_JJA =df_350_Desp_m[(df_350_Desp_m.index.month == JJA[0])| (df_350_Desp_m.index.month == JJA[1])| (df_350_Desp_m.index.month == JJA[2])]
df_350_Desp_m_SON =df_350_Desp_m[(df_350_Desp_m.index.month == SON[0])| (df_350_Desp_m.index.month == SON[1])| (df_350_Desp_m.index.month == SON[2])]

mean_radiacion_Desp_350_m = [np.nanmean(df_350_Desp_m_DEF.radiacion.values), np.nanmean(df_350_Desp_m_MAM.radiacion.values), np.nanmean(df_350_Desp_m_JJA.radiacion.values), np.nanmean(df_350_Desp_m_SON.radiacion.values)]
std_radiacion_Desp_350_m = [np.nanstd(df_350_Desp_m_DEF.radiacion.values), np.nanstd(df_350_Desp_m_MAM.radiacion.values), np.nanstd(df_350_Desp_m_JJA.radiacion.values), np.nanstd(df_350_Desp_m_SON.radiacion.values)]

mean_strength_Desp_350_m = [np.nanmean(df_350_Desp_m_DEF.strength.values), np.nanmean(df_350_Desp_m_MAM.strength.values), np.nanmean(df_350_Desp_m_JJA.strength.values), np.nanmean(df_350_Desp_m_SON.strength.values)]
std_strength_Desp_350_m = [np.nanstd(df_350_Desp_m_DEF.strength.values), np.nanstd(df_350_Desp_m_MAM.strength.values), np.nanstd(df_350_Desp_m_JJA.strength.values), np.nanstd(df_350_Desp_m_SON.strength.values)]

##------------>>> MEDIO DIA

df_350_Desp_n = df_350_Desp[(df_350_Desp.index.hour == horas_noon[0])| (df_350_Desp.index.hour == horas_noon[1])| (df_350_Desp.index.hour == horas_noon[2])|(df_350_Desp.index.hour == horas_noon[3])|(df_350_Desp.index.hour == horas_noon[4]) ]
df_350_Desp_n_DEF =df_350_Desp_n[(df_350_Desp_n.index.month == DEF[0])| (df_350_Desp_n.index.month == DEF[1])| (df_350_Desp_n.index.month == DEF[2])]
df_350_Desp_n_MAM =df_350_Desp_n[(df_350_Desp_n.index.month == MAM[0])| (df_350_Desp_n.index.month == MAM[1])| (df_350_Desp_n.index.month == MAM[2])]
df_350_Desp_n_JJA =df_350_Desp_n[(df_350_Desp_n.index.month == JJA[0])| (df_350_Desp_n.index.month == JJA[1])| (df_350_Desp_n.index.month == JJA[2])]
df_350_Desp_n_SON =df_350_Desp_n[(df_350_Desp_n.index.month == SON[0])| (df_350_Desp_n.index.month == SON[1])| (df_350_Desp_n.index.month == SON[2])]

mean_radiacion_Desp_350_n = [np.nanmean(df_350_Desp_n_DEF.radiacion.values), np.nanmean(df_350_Desp_n_MAM.radiacion.values), np.nanmean(df_350_Desp_n_JJA.radiacion.values), np.nanmean(df_350_Desp_n_SON.radiacion.values)]
std_radiacion_Desp_350_n = [np.nanstd(df_350_Desp_n_DEF.radiacion.values), np.nanstd(df_350_Desp_n_MAM.radiacion.values), np.nanstd(df_350_Desp_n_JJA.radiacion.values), np.nanstd(df_350_Desp_n_SON.radiacion.values)]

mean_strength_Desp_350_n = [np.nanmean(df_350_Desp_n_DEF.strength.values), np.nanmean(df_350_Desp_n_MAM.strength.values), np.nanmean(df_350_Desp_n_JJA.strength.values), np.nanmean(df_350_Desp_n_SON.strength.values)]
std_strength_Desp_350_n = [np.nanstd(df_350_Desp_n_DEF.strength.values), np.nanstd(df_350_Desp_n_MAM.strength.values), np.nanstd(df_350_Desp_n_JJA.strength.values), np.nanstd(df_350_Desp_n_SON.strength.values)]

##------------>>> TARDE

df_350_Desp_t = df_350_Desp[(df_350_Desp.index.hour == horas_tarde[0])| (df_350_Desp.index.hour == horas_tarde[1])| (df_350_Desp.index.hour == horas_tarde[2])|(df_350_Desp.index.hour == horas_tarde[3]) ]
df_350_Desp_t_DEF =df_350_Desp_t[(df_350_Desp_t.index.month == DEF[0])| (df_350_Desp_t.index.month == DEF[1])| (df_350_Desp_t.index.month == DEF[2])]
df_350_Desp_t_MAM =df_350_Desp_t[(df_350_Desp_t.index.month == MAM[0])| (df_350_Desp_t.index.month == MAM[1])| (df_350_Desp_t.index.month == MAM[2])]
df_350_Desp_t_JJA =df_350_Desp_t[(df_350_Desp_t.index.month == JJA[0])| (df_350_Desp_t.index.month == JJA[1])| (df_350_Desp_t.index.month == JJA[2])]
df_350_Desp_t_SON =df_350_Desp_t[(df_350_Desp_t.index.month == SON[0])| (df_350_Desp_t.index.month == SON[1])| (df_350_Desp_t.index.month == SON[2])]

mean_radiacion_Desp_350_t = [np.nanmean(df_350_Desp_t_DEF.radiacion.values), np.nanmean(df_350_Desp_t_MAM.radiacion.values), np.nanmean(df_350_Desp_t_JJA.radiacion.values), np.nanmean(df_350_Desp_t_SON.radiacion.values)]
std_radiacion_Desp_350_t = [np.nanstd(df_350_Desp_t_DEF.radiacion.values), np.nanstd(df_350_Desp_t_MAM.radiacion.values), np.nanstd(df_350_Desp_t_JJA.radiacion.values), np.nanstd(df_350_Desp_t_SON.radiacion.values)]

mean_strength_Desp_350_t = [np.nanmean(df_350_Desp_t_DEF.strength.values), np.nanmean(df_350_Desp_t_MAM.strength.values), np.nanmean(df_350_Desp_t_JJA.strength.values), np.nanmean(df_350_Desp_t_SON.strength.values)]
std_strength_Desp_350_t = [np.nanstd(df_350_Desp_t_DEF.strength.values), np.nanstd(df_350_Desp_t_MAM.strength.values), np.nanstd(df_350_Desp_t_JJA.strength.values), np.nanstd(df_350_Desp_t_SON.strength.values)]


################################################################################
##-------------------------------------975------------------------------------##
################################################################################
df_P975_15m_Desp = pd.DataFrame()
for i in range(len(df_result_975)):
    for j in range(len( df_Theoric['Rad_teo_975'].index)):
        if (df_result_975['radiacion'].index[i].month == df_Theoric['Rad_teo_975'].index[j].month) and (df_result_975['radiacion'].index[i].hour == df_Theoric['Rad_teo_975'].index[j].hour):
            if (df_result_975['radiacion'].iloc[i] >= 0.99 * df_Theoric['Rad_teo_975'].iloc[j]):
                df_P975_15m_Desp = df_P975_15m_Desp.append(pd.DataFrame(df_result_975.iloc[[i]]))
            else:
                pass
        else:
            pass

df_P975_15m_Desp =  df_P975_15m_Desp.loc[~df_P975_15m_Desp.index.duplicated(keep='first')]

df_975_Desp =pd.DataFrame()
for i in range(len(df_P975_15m_Desp.index )):
    df_975_Desp = df_975_Desp.append(df_P975[(df_P975.index>=df_P975_15m_Desp.index[i]) & (df_P975.index<=df_P975_15m_Desp.index[i] +timedelta(minutes=15))])

##------------>>> MANIANA

df_975_Desp_m = df_975_Desp[(df_975_Desp.index.hour == horas_maniana[0])| (df_975_Desp.index.hour == horas_maniana[1])| (df_975_Desp.index.hour == horas_maniana[2])|(df_975_Desp.index.hour == horas_maniana[3]) ]
df_975_Desp_m_DEF =df_975_Desp_m[(df_975_Desp_m.index.month == DEF[0])| (df_975_Desp_m.index.month == DEF[1])| (df_975_Desp_m.index.month == DEF[2])]
df_975_Desp_m_MAM =df_975_Desp_m[(df_975_Desp_m.index.month == MAM[0])| (df_975_Desp_m.index.month == MAM[1])| (df_975_Desp_m.index.month == MAM[2])]
df_975_Desp_m_JJA =df_975_Desp_m[(df_975_Desp_m.index.month == JJA[0])| (df_975_Desp_m.index.month == JJA[1])| (df_975_Desp_m.index.month == JJA[2])]
df_975_Desp_m_SON =df_975_Desp_m[(df_975_Desp_m.index.month == SON[0])| (df_975_Desp_m.index.month == SON[1])| (df_975_Desp_m.index.month == SON[2])]

mean_radiacion_Desp_975_m = [np.nanmean(df_975_Desp_m_DEF.radiacion.values), np.nanmean(df_975_Desp_m_MAM.radiacion.values), np.nanmean(df_975_Desp_m_JJA.radiacion.values), np.nanmean(df_975_Desp_m_SON.radiacion.values)]
std_radiacion_Desp_975_m = [np.nanstd(df_975_Desp_m_DEF.radiacion.values), np.nanstd(df_975_Desp_m_MAM.radiacion.values), np.nanstd(df_975_Desp_m_JJA.radiacion.values), np.nanstd(df_975_Desp_m_SON.radiacion.values)]

mean_strength_Desp_975_m = [np.nanmean(df_975_Desp_m_DEF.strength.values), np.nanmean(df_975_Desp_m_MAM.strength.values), np.nanmean(df_975_Desp_m_JJA.strength.values), np.nanmean(df_975_Desp_m_SON.strength.values)]
std_strength_Desp_975_m = [np.nanstd(df_975_Desp_m_DEF.strength.values), np.nanstd(df_975_Desp_m_MAM.strength.values), np.nanstd(df_975_Desp_m_JJA.strength.values), np.nanstd(df_975_Desp_m_SON.strength.values)]

##------------>>> MEDIO DIA

df_975_Desp_n = df_975_Desp[(df_975_Desp.index.hour == horas_noon[0])| (df_975_Desp.index.hour == horas_noon[1])| (df_975_Desp.index.hour == horas_noon[2])|(df_975_Desp.index.hour == horas_noon[3])|(df_975_Desp.index.hour == horas_noon[4]) ]
df_975_Desp_n_DEF =df_975_Desp_n[(df_975_Desp_n.index.month == DEF[0])| (df_975_Desp_n.index.month == DEF[1])| (df_975_Desp_n.index.month == DEF[2])]
df_975_Desp_n_MAM =df_975_Desp_n[(df_975_Desp_n.index.month == MAM[0])| (df_975_Desp_n.index.month == MAM[1])| (df_975_Desp_n.index.month == MAM[2])]
df_975_Desp_n_JJA =df_975_Desp_n[(df_975_Desp_n.index.month == JJA[0])| (df_975_Desp_n.index.month == JJA[1])| (df_975_Desp_n.index.month == JJA[2])]
df_975_Desp_n_SON =df_975_Desp_n[(df_975_Desp_n.index.month == SON[0])| (df_975_Desp_n.index.month == SON[1])| (df_975_Desp_n.index.month == SON[2])]

mean_radiacion_Desp_975_n = [np.nanmean(df_975_Desp_n_DEF.radiacion.values), np.nanmean(df_975_Desp_n_MAM.radiacion.values), np.nanmean(df_975_Desp_n_JJA.radiacion.values), np.nanmean(df_975_Desp_n_SON.radiacion.values)]
std_radiacion_Desp_975_n = [np.nanstd(df_975_Desp_n_DEF.radiacion.values), np.nanstd(df_975_Desp_n_MAM.radiacion.values), np.nanstd(df_975_Desp_n_JJA.radiacion.values), np.nanstd(df_975_Desp_n_SON.radiacion.values)]

mean_strength_Desp_975_n = [np.nanmean(df_975_Desp_n_DEF.strength.values), np.nanmean(df_975_Desp_n_MAM.strength.values), np.nanmean(df_975_Desp_n_JJA.strength.values), np.nanmean(df_975_Desp_n_SON.strength.values)]
std_strength_Desp_975_n = [np.nanstd(df_975_Desp_n_DEF.strength.values), np.nanstd(df_975_Desp_n_MAM.strength.values), np.nanstd(df_975_Desp_n_JJA.strength.values), np.nanstd(df_975_Desp_n_SON.strength.values)]

##------------>>> TARDE

df_975_Desp_t = df_975_Desp[(df_975_Desp.index.hour == horas_tarde[0])| (df_975_Desp.index.hour == horas_tarde[1])| (df_975_Desp.index.hour == horas_tarde[2])|(df_975_Desp.index.hour == horas_tarde[3]) ]
df_975_Desp_t_DEF =df_975_Desp_t[(df_975_Desp_t.index.month == DEF[0])| (df_975_Desp_t.index.month == DEF[1])| (df_975_Desp_t.index.month == DEF[2])]
df_975_Desp_t_MAM =df_975_Desp_t[(df_975_Desp_t.index.month == MAM[0])| (df_975_Desp_t.index.month == MAM[1])| (df_975_Desp_t.index.month == MAM[2])]
df_975_Desp_t_JJA =df_975_Desp_t[(df_975_Desp_t.index.month == JJA[0])| (df_975_Desp_t.index.month == JJA[1])| (df_975_Desp_t.index.month == JJA[2])]
df_975_Desp_t_SON =df_975_Desp_t[(df_975_Desp_t.index.month == SON[0])| (df_975_Desp_t.index.month == SON[1])| (df_975_Desp_t.index.month == SON[2])]

mean_radiacion_Desp_975_t = [np.nanmean(df_975_Desp_t_DEF.radiacion.values), np.nanmean(df_975_Desp_t_MAM.radiacion.values), np.nanmean(df_975_Desp_t_JJA.radiacion.values), np.nanmean(df_975_Desp_t_SON.radiacion.values)]
std_radiacion_Desp_975_t = [np.nanstd(df_975_Desp_t_DEF.radiacion.values), np.nanstd(df_975_Desp_t_MAM.radiacion.values), np.nanstd(df_975_Desp_t_JJA.radiacion.values), np.nanstd(df_975_Desp_t_SON.radiacion.values)]

mean_strength_Desp_975_t = [np.nanmean(df_975_Desp_t_DEF.strength.values), np.nanmean(df_975_Desp_t_MAM.strength.values), np.nanmean(df_975_Desp_t_JJA.strength.values), np.nanmean(df_975_Desp_t_SON.strength.values)]
std_strength_Desp_975_t = [np.nanstd(df_975_Desp_t_DEF.strength.values), np.nanstd(df_975_Desp_t_MAM.strength.values), np.nanstd(df_975_Desp_t_JJA.strength.values), np.nanstd(df_975_Desp_t_SON.strength.values)]

################################################################################
##-----------------------------------GRAFICAS---------------------------------##
################################################################################

x_labels = ['DEF', 'MAM', 'JJA', 'SON']

plt.close('all')
fig = plt.figure(figsize=(16,23))
ax1 = fig.add_subplot(3, 4, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(x_labels,  mean_radiacion_Nuba_975_m, color = '#abdda4', lw=1.5, label = 'Nublado')
ax1.scatter(x_labels,  mean_radiacion_Nuba_975_m, marker='.', c = '#abdda4', s=30)
ax1.plot(x_labels,  mean_radiacion_Desp_975_m, color = '#d7191c', lw=1.5, label = 'Despejado')
ax1.scatter(x_labels,  mean_radiacion_Desp_975_m, marker='.', c = '#d7191c', s=30)
ax1.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax1.set_xticks(range(0, 4), minor=False)
ax1.set_xticklabels(x_labels, minor=False, rotation = 20)
ax1.set_ylim(0, 1300)
ax1.set_title(u'Promedio de la radiación en la \n mañana en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax2 = fig.add_subplot(3, 4, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(x_labels,  std_radiacion_Nuba_975_m, color = '#abdda4', lw=1.5, label = 'Nublado')
ax2.scatter(x_labels,  std_radiacion_Nuba_975_m, marker='.', c = '#abdda4', s=30)
ax2.plot(x_labels,  std_radiacion_Desp_975_m, color = '#d7191c', lw=1.5, label = 'Despejado')
ax2.scatter(x_labels,  std_radiacion_Desp_975_m, marker='.', c = '#d7191c', s=30)
ax2.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax2.set_xticks(range(0, 4), minor=False)
ax2.set_xticklabels(x_labels, minor=False, rotation = 20)
ax2.set_ylim(0, 600)
ax2.set_title(u'Desviación de la radiación en la \n mañana en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax3 = fig.add_subplot(3, 4, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.plot(x_labels,  mean_strength_Nuba_975_m, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax3.scatter(x_labels,  mean_strength_Nuba_975_m, marker='.', c = '#2b83ba', s=30)
ax3.plot(x_labels,  mean_strength_Desp_975_m, color = '#fdae61', lw=1.5, label = 'Despejado')
ax3.scatter(x_labels,  mean_strength_Desp_975_m, marker='.', c = '#fdae61', s=30)
ax3.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax3.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax3.set_xticks(range(0, 4), minor=False)
ax3.set_xticklabels(x_labels, minor=False, rotation = 20)
ax3.set_ylim(0, 80)
ax3.set_title(u'Promedio de la potencia en la \n mañana en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax4 = fig.add_subplot(3, 4, 4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.plot(x_labels,  std_strength_Nuba_975_m, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax4.scatter(x_labels,  std_strength_Nuba_975_m, marker='.', c = '#2b83ba', s=30)
ax4.plot(x_labels,  std_strength_Desp_975_m, color = '#fdae61', lw=1.5, label = 'Despejado')
ax4.scatter(x_labels,  std_strength_Desp_975_m, marker='.', c = '#fdae61', s=30)
ax4.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax4.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax4.set_xticks(range(0, 4), minor=False)
ax4.set_xticklabels(x_labels, minor=False, rotation = 20)
ax4.set_ylim(0, 50)
ax4.set_title(u'Desviación de la potencia en la \n mañana en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()


ax5 = fig.add_subplot(3, 4, 5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.plot(x_labels,  mean_radiacion_Nuba_975_n, color = '#abdda4', lw=1.5, label = 'Nublado')
ax5.scatter(x_labels,  mean_radiacion_Nuba_975_n, marker='.', c = '#abdda4', s=30)
ax5.plot(x_labels,  mean_radiacion_Desp_975_n, color = '#d7191c', lw=1.5, label = 'Despejado')
ax5.scatter(x_labels,  mean_radiacion_Desp_975_n, marker='.', c = '#d7191c', s=30)
ax5.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax5.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax5.set_xticks(range(0, 4), minor=False)
ax5.set_xticklabels(x_labels, minor=False, rotation = 20)
ax5.set_ylim(0, 1300)
ax5.set_title(u'Promedio de la radiación al \n medio dia en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax6 = fig.add_subplot(3, 4, 6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.plot(x_labels,  std_radiacion_Nuba_975_n, color = '#abdda4', lw=1.5, label = 'Nublado')
ax6.scatter(x_labels,  std_radiacion_Nuba_975_n, marker='.', c = '#abdda4', s=30)
ax6.plot(x_labels,  std_radiacion_Desp_975_n, color = '#d7191c', lw=1.5, label = 'Despejado')
ax6.scatter(x_labels,  std_radiacion_Desp_975_n, marker='.', c = '#d7191c', s=30)
ax6.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax6.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax6.set_xticks(range(0, 4), minor=False)
ax6.set_xticklabels(x_labels, minor=False, rotation = 20)
ax6.set_ylim(0, 600)
ax6.set_title(u'Desviación de la radiación al \n medio dia en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax7 = fig.add_subplot(3, 4, 7)
ax7.spines['top'].set_visible(False)
ax7.spines['right'].set_visible(False)
ax7.plot(x_labels,  mean_strength_Nuba_975_n, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax7.scatter(x_labels,  mean_strength_Nuba_975_n, marker='.', c = '#2b83ba', s=30)
ax7.plot(x_labels,  mean_strength_Desp_975_n, color = '#fdae61', lw=1.5, label = 'Despejado')
ax7.scatter(x_labels,  mean_strength_Desp_975_n, marker='.', c = '#fdae61', s=30)
ax7.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax7.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax7.set_xticks(range(0, 4), minor=False)
ax7.set_xticklabels(x_labels, minor=False, rotation = 20)
ax7.set_ylim(0, 80)
ax7.set_title(u'Promedio de la potencia al \n medio dia en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax8 = fig.add_subplot(3, 4, 8)
ax8.spines['top'].set_visible(False)
ax8.spines['right'].set_visible(False)
ax8.plot(x_labels,  std_strength_Nuba_975_n, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax8.scatter(x_labels,  std_strength_Nuba_975_n, marker='.', c = '#2b83ba', s=30)
ax8.plot(x_labels,  std_strength_Desp_975_n, color = '#fdae61', lw=1.5, label = 'Despejado')
ax8.scatter(x_labels,  std_strength_Desp_975_n, marker='.', c = '#fdae61', s=30)
ax8.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax8.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax8.set_xticks(range(0, 4), minor=False)
ax8.set_xticklabels(x_labels, minor=False, rotation = 20)
ax8.set_ylim(0, 50)
ax8.set_title(u'Desviación de la potencia al \n medio dia en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax9 = fig.add_subplot(3, 4, 9)
ax9.spines['top'].set_visible(False)
ax9.spines['right'].set_visible(False)
ax9.plot(x_labels,  mean_radiacion_Nuba_975_t, color = '#abdda4', lw=1.5, label = 'Nublado')
ax9.scatter(x_labels,  mean_radiacion_Nuba_975_t, marker='.', c = '#abdda4', s=30)
ax9.plot(x_labels,  mean_radiacion_Desp_975_t, color = '#d7191c', lw=1.5, label = 'Despejado')
ax9.scatter(x_labels,  mean_radiacion_Desp_975_t, marker='.', c = '#d7191c', s=30)
ax9.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax9.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax9.set_xticks(range(0, 4), minor=False)
ax9.set_xticklabels(x_labels, minor=False, rotation = 20)
ax9.set_ylim(0, 1300)
ax9.set_title(u'Promedio de la radiación en la \n tarde en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax10 = fig.add_subplot(3, 4, 10)
ax10.spines['top'].set_visible(False)
ax10.spines['right'].set_visible(False)
ax10.plot(x_labels,  std_radiacion_Nuba_975_t, color = '#abdda4', lw=1.5, label = 'Nublado')
ax10.scatter(x_labels,  std_radiacion_Nuba_975_t, marker='.', c = '#abdda4', s=30)
ax10.plot(x_labels,  std_radiacion_Desp_975_t, color = '#d7191c', lw=1.5, label = 'Despejado')
ax10.scatter(x_labels,  std_radiacion_Desp_975_t, marker='.', c = '#d7191c', s=30)
ax10.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax10.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax10.set_xticks(range(0, 4), minor=False)
ax10.set_xticklabels(x_labels, minor=False, rotation = 20)
ax10.set_ylim(0, 600)
ax10.set_title(u'Desviación de la radiación en la \n tarde en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax11 = fig.add_subplot(3, 4, 11)
ax11.spines['top'].set_visible(False)
ax11.spines['right'].set_visible(False)
ax11.plot(x_labels,  mean_strength_Nuba_975_t, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax11.scatter(x_labels,  mean_strength_Nuba_975_t, marker='.', c = '#2b83ba', s=30)
ax11.plot(x_labels,  mean_strength_Desp_975_t, color = '#fdae61', lw=1.5, label = 'Despejado')
ax11.scatter(x_labels,  mean_strength_Desp_975_t, marker='.', c = '#fdae61', s=30)
ax11.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax11.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax11.set_xticks(range(0, 4), minor=False)
ax11.set_xticklabels(x_labels, minor=False, rotation = 20)
ax11.set_ylim(0, 80)
ax11.set_title(u'Promedio de la potencia en la \n tarde en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax12 = fig.add_subplot(3, 4, 12)
ax12.spines['top'].set_visible(False)
ax12.spines['right'].set_visible(False)
ax12.plot(x_labels,  std_strength_Nuba_975_t, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax12.scatter(x_labels,  std_strength_Nuba_975_t, marker='.', c = '#2b83ba', s=30)
ax12.plot(x_labels,  std_strength_Desp_975_t, color = '#fdae61', lw=1.5, label = 'Despejado')
ax12.scatter(x_labels,  std_strength_Desp_975_t, marker='.', c = '#fdae61', s=30)
ax12.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax12.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax12.set_xticks(range(0, 4), minor=False)
ax12.set_xticklabels(x_labels, minor=False, rotation = 20)
ax12.set_ylim(0, 50)
ax12.set_title(u'Desviación de la potencia en la \n tarde en el Centro-Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.3, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/MeanStd_RadPower_NubaDesp_CentroOeste.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/MeanStd_RadPower_NubaDesp_CentroOeste.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


plt.close('all')
fig = plt.figure(figsize=(16,23))
ax1 = fig.add_subplot(3, 4, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(x_labels,  mean_radiacion_Nuba_350_m, color = '#abdda4', lw=1.5, label = 'Nublado')
ax1.scatter(x_labels,  mean_radiacion_Nuba_350_m, marker='.', c = '#abdda4', s=30)
ax1.plot(x_labels,  mean_radiacion_Desp_350_m, color = '#d7191c', lw=1.5, label = 'Despejado')
ax1.scatter(x_labels,  mean_radiacion_Desp_350_m, marker='.', c = '#d7191c', s=30)
ax1.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax1.set_xticks(range(0, 4), minor=False)
ax1.set_xticklabels(x_labels, minor=False, rotation = 20)
ax1.set_ylim(0, 1300)
ax1.set_title(u'Promedio de la radiación en la \n mañana en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax2 = fig.add_subplot(3, 4, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(x_labels,  std_radiacion_Nuba_350_m, color = '#abdda4', lw=1.5, label = 'Nublado')
ax2.scatter(x_labels,  std_radiacion_Nuba_350_m, marker='.', c = '#abdda4', s=30)
ax2.plot(x_labels,  std_radiacion_Desp_350_m, color = '#d7191c', lw=1.5, label = 'Despejado')
ax2.scatter(x_labels,  std_radiacion_Desp_350_m, marker='.', c = '#d7191c', s=30)
ax2.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax2.set_xticks(range(0, 4), minor=False)
ax2.set_xticklabels(x_labels, minor=False, rotation = 20)
ax2.set_ylim(0, 600)
ax2.set_title(u'Desviación de la radiación en la \n mañana en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax3 = fig.add_subplot(3, 4, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.plot(x_labels,  mean_strength_Nuba_350_m, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax3.scatter(x_labels,  mean_strength_Nuba_350_m, marker='.', c = '#2b83ba', s=30)
ax3.plot(x_labels,  mean_strength_Desp_350_m, color = '#fdae61', lw=1.5, label = 'Despejado')
ax3.scatter(x_labels,  mean_strength_Desp_350_m, marker='.', c = '#fdae61', s=30)
ax3.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax3.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax3.set_xticks(range(0, 4), minor=False)
ax3.set_xticklabels(x_labels, minor=False, rotation = 20)
ax3.set_ylim(0, 80)
ax3.set_title(u'Promedio de la potencia en la \n mañana en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax4 = fig.add_subplot(3, 4, 4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.plot(x_labels,  std_strength_Nuba_350_m, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax4.scatter(x_labels,  std_strength_Nuba_350_m, marker='.', c = '#2b83ba', s=30)
ax4.plot(x_labels,  std_strength_Desp_350_m, color = '#fdae61', lw=1.5, label = 'Despejado')
ax4.scatter(x_labels,  std_strength_Desp_350_m, marker='.', c = '#fdae61', s=30)
ax4.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax4.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax4.set_xticks(range(0, 4), minor=False)
ax4.set_xticklabels(x_labels, minor=False, rotation = 20)
ax4.set_ylim(0, 50)
ax4.set_title(u'Desviación de la potencia en la \n mañana en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()


ax5 = fig.add_subplot(3, 4, 5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.plot(x_labels,  mean_radiacion_Nuba_350_n, color = '#abdda4', lw=1.5, label = 'Nublado')
ax5.scatter(x_labels,  mean_radiacion_Nuba_350_n, marker='.', c = '#abdda4', s=30)
ax5.plot(x_labels,  mean_radiacion_Desp_350_n, color = '#d7191c', lw=1.5, label = 'Despejado')
ax5.scatter(x_labels,  mean_radiacion_Desp_350_n, marker='.', c = '#d7191c', s=30)
ax5.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax5.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax5.set_xticks(range(0, 4), minor=False)
ax5.set_xticklabels(x_labels, minor=False, rotation = 20)
ax5.set_ylim(0, 1300)
ax5.set_title(u'Promedio de la radiación al \n medio dia en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax6 = fig.add_subplot(3, 4, 6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.plot(x_labels,  std_radiacion_Nuba_350_n, color = '#abdda4', lw=1.5, label = 'Nublado')
ax6.scatter(x_labels,  std_radiacion_Nuba_350_n, marker='.', c = '#abdda4', s=30)
ax6.plot(x_labels,  std_radiacion_Desp_350_n, color = '#d7191c', lw=1.5, label = 'Despejado')
ax6.scatter(x_labels,  std_radiacion_Desp_350_n, marker='.', c = '#d7191c', s=30)
ax6.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax6.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax6.set_xticks(range(0, 4), minor=False)
ax6.set_xticklabels(x_labels, minor=False, rotation = 20)
ax6.set_ylim(0, 600)
ax6.set_title(u'Desviación de la radiación al \n medio dia en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax7 = fig.add_subplot(3, 4, 7)
ax7.spines['top'].set_visible(False)
ax7.spines['right'].set_visible(False)
ax7.plot(x_labels,  mean_strength_Nuba_350_n, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax7.scatter(x_labels,  mean_strength_Nuba_350_n, marker='.', c = '#2b83ba', s=30)
ax7.plot(x_labels,  mean_strength_Desp_350_n, color = '#fdae61', lw=1.5, label = 'Despejado')
ax7.scatter(x_labels,  mean_strength_Desp_350_n, marker='.', c = '#fdae61', s=30)
ax7.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax7.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax7.set_xticks(range(0, 4), minor=False)
ax7.set_xticklabels(x_labels, minor=False, rotation = 20)
ax7.set_ylim(0, 80)
ax7.set_title(u'Promedio de la potencia al \n medio dia en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax8 = fig.add_subplot(3, 4, 8)
ax8.spines['top'].set_visible(False)
ax8.spines['right'].set_visible(False)
ax8.plot(x_labels,  std_strength_Nuba_350_n, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax8.scatter(x_labels,  std_strength_Nuba_350_n, marker='.', c = '#2b83ba', s=30)
ax8.plot(x_labels,  std_strength_Desp_350_n, color = '#fdae61', lw=1.5, label = 'Despejado')
ax8.scatter(x_labels,  std_strength_Desp_350_n, marker='.', c = '#fdae61', s=30)
ax8.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax8.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax8.set_xticks(range(0, 4), minor=False)
ax8.set_xticklabels(x_labels, minor=False, rotation = 20)
ax8.set_ylim(0, 50)
ax8.set_title(u'Desviación de la potencia al \n medio dia en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax9 = fig.add_subplot(3, 4, 9)
ax9.spines['top'].set_visible(False)
ax9.spines['right'].set_visible(False)
ax9.plot(x_labels,  mean_radiacion_Nuba_350_t, color = '#abdda4', lw=1.5, label = 'Nublado')
ax9.scatter(x_labels,  mean_radiacion_Nuba_350_t, marker='.', c = '#abdda4', s=30)
ax9.plot(x_labels,  mean_radiacion_Desp_350_t, color = '#d7191c', lw=1.5, label = 'Despejado')
ax9.scatter(x_labels,  mean_radiacion_Desp_350_t, marker='.', c = '#d7191c', s=30)
ax9.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax9.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax9.set_xticks(range(0, 4), minor=False)
ax9.set_xticklabels(x_labels, minor=False, rotation = 20)
ax9.set_ylim(0, 1300)
ax9.set_title(u'Promedio de la radiación en la \n tarde en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax10 = fig.add_subplot(3, 4, 10)
ax10.spines['top'].set_visible(False)
ax10.spines['right'].set_visible(False)
ax10.plot(x_labels,  std_radiacion_Nuba_350_t, color = '#abdda4', lw=1.5, label = 'Nublado')
ax10.scatter(x_labels,  std_radiacion_Nuba_350_t, marker='.', c = '#abdda4', s=30)
ax10.plot(x_labels,  std_radiacion_Desp_350_t, color = '#d7191c', lw=1.5, label = 'Despejado')
ax10.scatter(x_labels,  std_radiacion_Desp_350_t, marker='.', c = '#d7191c', s=30)
ax10.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax10.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax10.set_xticks(range(0, 4), minor=False)
ax10.set_xticklabels(x_labels, minor=False, rotation = 20)
ax10.set_ylim(0, 600)
ax10.set_title(u'Desviación de la radiación en la \n tarde en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax11 = fig.add_subplot(3, 4, 11)
ax11.spines['top'].set_visible(False)
ax11.spines['right'].set_visible(False)
ax11.plot(x_labels,  mean_strength_Nuba_350_t, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax11.scatter(x_labels,  mean_strength_Nuba_350_t, marker='.', c = '#2b83ba', s=30)
ax11.plot(x_labels,  mean_strength_Desp_350_t, color = '#fdae61', lw=1.5, label = 'Despejado')
ax11.scatter(x_labels,  mean_strength_Desp_350_t, marker='.', c = '#fdae61', s=30)
ax11.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax11.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax11.set_xticks(range(0, 4), minor=False)
ax11.set_xticklabels(x_labels, minor=False, rotation = 20)
ax11.set_ylim(0, 80)
ax11.set_title(u'Promedio de la potencia en la \n tarde en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax12 = fig.add_subplot(3, 4, 12)
ax12.spines['top'].set_visible(False)
ax12.spines['right'].set_visible(False)
ax12.plot(x_labels,  std_strength_Nuba_350_t, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax12.scatter(x_labels,  std_strength_Nuba_350_t, marker='.', c = '#2b83ba', s=30)
ax12.plot(x_labels,  std_strength_Desp_350_t, color = '#fdae61', lw=1.5, label = 'Despejado')
ax12.scatter(x_labels,  std_strength_Desp_350_t, marker='.', c = '#fdae61', s=30)
ax12.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax12.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax12.set_xticks(range(0, 4), minor=False)
ax12.set_xticklabels(x_labels, minor=False, rotation = 20)
ax12.set_ylim(0, 50)
ax12.set_title(u'Desviación de la potencia en la \n tarde en el Oeste', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.3, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/MeanStd_RadPower_NubaDesp_Oeste.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/MeanStd_RadPower_NubaDesp_Oeste.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')






plt.close('all')
fig = plt.figure(figsize=(16,23))
ax1 = fig.add_subplot(3, 4, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(x_labels,  mean_radiacion_Nuba_348_m, color = '#abdda4', lw=1.5, label = 'Nublado')
ax1.scatter(x_labels,  mean_radiacion_Nuba_348_m, marker='.', c = '#abdda4', s=30)
ax1.plot(x_labels,  mean_radiacion_Desp_348_m, color = '#d7191c', lw=1.5, label = 'Despejado')
ax1.scatter(x_labels,  mean_radiacion_Desp_348_m, marker='.', c = '#d7191c', s=30)
ax1.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax1.set_xticks(range(0, 4), minor=False)
ax1.set_xticklabels(x_labels, minor=False, rotation = 20)
ax1.set_ylim(0, 1300)
ax1.set_title(u'Promedio de la radiación en la \n mañana en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax2 = fig.add_subplot(3, 4, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(x_labels,  std_radiacion_Nuba_348_m, color = '#abdda4', lw=1.5, label = 'Nublado')
ax2.scatter(x_labels,  std_radiacion_Nuba_348_m, marker='.', c = '#abdda4', s=30)
ax2.plot(x_labels,  std_radiacion_Desp_348_m, color = '#d7191c', lw=1.5, label = 'Despejado')
ax2.scatter(x_labels,  std_radiacion_Desp_348_m, marker='.', c = '#d7191c', s=30)
ax2.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax2.set_xticks(range(0, 4), minor=False)
ax2.set_xticklabels(x_labels, minor=False, rotation = 20)
ax2.set_ylim(0, 600)
ax2.set_title(u'Desviación de la radiación en la \n mañana en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax3 = fig.add_subplot(3, 4, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.plot(x_labels,  mean_strength_Nuba_348_m, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax3.scatter(x_labels,  mean_strength_Nuba_348_m, marker='.', c = '#2b83ba', s=30)
ax3.plot(x_labels,  mean_strength_Desp_348_m, color = '#fdae61', lw=1.5, label = 'Despejado')
ax3.scatter(x_labels,  mean_strength_Desp_348_m, marker='.', c = '#fdae61', s=30)
ax3.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax3.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax3.set_xticks(range(0, 4), minor=False)
ax3.set_xticklabels(x_labels, minor=False, rotation = 20)
ax3.set_ylim(0, 80)
ax3.set_title(u'Promedio de la potencia en la \n mañana en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax4 = fig.add_subplot(3, 4, 4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.plot(x_labels,  std_strength_Nuba_348_m, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax4.scatter(x_labels,  std_strength_Nuba_348_m, marker='.', c = '#2b83ba', s=30)
ax4.plot(x_labels,  std_strength_Desp_348_m, color = '#fdae61', lw=1.5, label = 'Despejado')
ax4.scatter(x_labels,  std_strength_Desp_348_m, marker='.', c = '#fdae61', s=30)
ax4.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax4.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax4.set_xticks(range(0, 4), minor=False)
ax4.set_xticklabels(x_labels, minor=False, rotation = 20)
ax4.set_ylim(0, 50)
ax4.set_title(u'Desviación de la potencia en la \n mañana en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()


ax5 = fig.add_subplot(3, 4, 5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.plot(x_labels,  mean_radiacion_Nuba_348_n, color = '#abdda4', lw=1.5, label = 'Nublado')
ax5.scatter(x_labels,  mean_radiacion_Nuba_348_n, marker='.', c = '#abdda4', s=30)
ax5.plot(x_labels,  mean_radiacion_Desp_348_n, color = '#d7191c', lw=1.5, label = 'Despejado')
ax5.scatter(x_labels,  mean_radiacion_Desp_348_n, marker='.', c = '#d7191c', s=30)
ax5.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax5.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax5.set_xticks(range(0, 4), minor=False)
ax5.set_xticklabels(x_labels, minor=False, rotation = 20)
ax5.set_ylim(0, 1300)
ax5.set_title(u'Promedio de la radiación al \n medio dia en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax6 = fig.add_subplot(3, 4, 6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.plot(x_labels,  std_radiacion_Nuba_348_n, color = '#abdda4', lw=1.5, label = 'Nublado')
ax6.scatter(x_labels,  std_radiacion_Nuba_348_n, marker='.', c = '#abdda4', s=30)
ax6.plot(x_labels,  std_radiacion_Desp_348_n, color = '#d7191c', lw=1.5, label = 'Despejado')
ax6.scatter(x_labels,  std_radiacion_Desp_348_n, marker='.', c = '#d7191c', s=30)
ax6.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax6.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax6.set_xticks(range(0, 4), minor=False)
ax6.set_xticklabels(x_labels, minor=False, rotation = 20)
ax6.set_ylim(0, 600)
ax6.set_title(u'Desviación de la radiación al \n medio dia en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax7 = fig.add_subplot(3, 4, 7)
ax7.spines['top'].set_visible(False)
ax7.spines['right'].set_visible(False)
ax7.plot(x_labels,  mean_strength_Nuba_348_n, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax7.scatter(x_labels,  mean_strength_Nuba_348_n, marker='.', c = '#2b83ba', s=30)
ax7.plot(x_labels,  mean_strength_Desp_348_n, color = '#fdae61', lw=1.5, label = 'Despejado')
ax7.scatter(x_labels,  mean_strength_Desp_348_n, marker='.', c = '#fdae61', s=30)
ax7.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax7.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax7.set_xticks(range(0, 4), minor=False)
ax7.set_xticklabels(x_labels, minor=False, rotation = 20)
ax7.set_ylim(0, 80)
ax7.set_title(u'Promedio de la potencia al \n medio dia en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax8 = fig.add_subplot(3, 4, 8)
ax8.spines['top'].set_visible(False)
ax8.spines['right'].set_visible(False)
ax8.plot(x_labels,  std_strength_Nuba_348_n, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax8.scatter(x_labels,  std_strength_Nuba_348_n, marker='.', c = '#2b83ba', s=30)
ax8.plot(x_labels,  std_strength_Desp_348_n, color = '#fdae61', lw=1.5, label = 'Despejado')
ax8.scatter(x_labels,  std_strength_Desp_348_n, marker='.', c = '#fdae61', s=30)
ax8.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax8.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax8.set_xticks(range(0, 4), minor=False)
ax8.set_xticklabels(x_labels, minor=False, rotation = 20)
ax8.set_ylim(0, 50)
ax8.set_title(u'Desviación de la potencia al \n medio dia en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax9 = fig.add_subplot(3, 4, 9)
ax9.spines['top'].set_visible(False)
ax9.spines['right'].set_visible(False)
ax9.plot(x_labels,  mean_radiacion_Nuba_348_t, color = '#abdda4', lw=1.5, label = 'Nublado')
ax9.scatter(x_labels,  mean_radiacion_Nuba_348_t, marker='.', c = '#abdda4', s=30)
ax9.plot(x_labels,  mean_radiacion_Desp_348_t, color = '#d7191c', lw=1.5, label = 'Despejado')
ax9.scatter(x_labels,  mean_radiacion_Desp_348_t, marker='.', c = '#d7191c', s=30)
ax9.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax9.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax9.set_xticks(range(0, 4), minor=False)
ax9.set_xticklabels(x_labels, minor=False, rotation = 20)
ax9.set_ylim(0, 1300)
ax9.set_title(u'Promedio de la radiación en la \n tarde en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax10 = fig.add_subplot(3, 4, 10)
ax10.spines['top'].set_visible(False)
ax10.spines['right'].set_visible(False)
ax10.plot(x_labels,  std_radiacion_Nuba_348_t, color = '#abdda4', lw=1.5, label = 'Nublado')
ax10.scatter(x_labels,  std_radiacion_Nuba_348_t, marker='.', c = '#abdda4', s=30)
ax10.plot(x_labels,  std_radiacion_Desp_348_t, color = '#d7191c', lw=1.5, label = 'Despejado')
ax10.scatter(x_labels,  std_radiacion_Desp_348_t, marker='.', c = '#d7191c', s=30)
ax10.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax10.set_ylabel(u"$[W/m^{2}]$", fontproperties = prop_1, fontsize=16)
ax10.set_xticks(range(0, 4), minor=False)
ax10.set_xticklabels(x_labels, minor=False, rotation = 20)
ax10.set_ylim(0, 600)
ax10.set_title(u'Desviación de la radiación en la \n tarde en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax11 = fig.add_subplot(3, 4, 11)
ax11.spines['top'].set_visible(False)
ax11.spines['right'].set_visible(False)
ax11.plot(x_labels,  mean_strength_Nuba_348_t, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax11.scatter(x_labels,  mean_strength_Nuba_348_t, marker='.', c = '#2b83ba', s=30)
ax11.plot(x_labels,  mean_strength_Desp_348_t, color = '#fdae61', lw=1.5, label = 'Despejado')
ax11.scatter(x_labels,  mean_strength_Desp_348_t, marker='.', c = '#fdae61', s=30)
ax11.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax11.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax11.set_xticks(range(0, 4), minor=False)
ax11.set_xticklabels(x_labels, minor=False, rotation = 20)
ax11.set_ylim(0, 80)
ax11.set_title(u'Promedio de la potencia en la \n tarde en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

ax12 = fig.add_subplot(3, 4, 12)
ax12.spines['top'].set_visible(False)
ax12.spines['right'].set_visible(False)
ax12.plot(x_labels,  std_strength_Nuba_348_t, color = '#2b83ba', lw=1.5, label = 'Nublado')
ax12.scatter(x_labels,  std_strength_Nuba_348_t, marker='.', c = '#2b83ba', s=30)
ax12.plot(x_labels,  std_strength_Desp_348_t, color = '#fdae61', lw=1.5, label = 'Despejado')
ax12.scatter(x_labels,  std_strength_Desp_348_t, marker='.', c = '#fdae61', s=30)
ax12.set_xlabel('Trimestre', fontproperties = prop_1, fontsize=17)
ax12.set_ylabel(u"$[W]$", fontproperties = prop_1, fontsize=16)
ax12.set_xticks(range(0, 4), minor=False)
ax12.set_xticklabels(x_labels, minor=False, rotation = 20)
ax12.set_ylim(0, 50)
ax12.set_title(u'Desviación de la potencia en la \n tarde en el Este', loc = 'center', fontproperties = prop, fontsize=14)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.3, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/MeanStd_RadPower_NubaDesp_Este.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/MeanStd_RadPower_NubaDesp_Este.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
