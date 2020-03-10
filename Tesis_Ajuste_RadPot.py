#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib
#matplotlib.use('Agg')
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

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Relacion y juate de sta de los datos de potencia y de radiacion solar
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

df_P975_h = df_P975_h[df_P975_h['strength'] <= 80]

df_P975_h = df_P975_h[(df_P975_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P975_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]
df_P350_h = df_P350_h[(df_P350_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P350_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]
df_P348_h = df_P348_h[(df_P348_h.index.date >= pd.to_datetime('2019-'+str(fi_m)+ '-' +str(fi_d)).date()) & (df_P348_h.index.date <= pd.to_datetime('2019-'+str(ff_m)+ '-'+str(ff_d)).date())]

df_P975_h.drop(df_P975_h[(df_P975_h['strength']>20) & (df_P975_h['radiacion']<350)].index, axis=0, inplace=True)
df_P350_h.drop(df_P350_h[(df_P350_h['strength']>20) & (df_P350_h['radiacion']<350)].index, axis=0, inplace=True)
df_P348_h.drop(df_P348_h[(df_P348_h['strength']>20) & (df_P348_h['radiacion']<350)].index, axis=0, inplace=True)

################################################################################
##-------------------REGRESION LINEAL METODO STATS MODEL----------------------##
################################################################################
import statsmodels.api as sm
import statsmodels.formula.api as smf

df_P975 = df_P975.dropna()
df_P975['intercept']=1

##---------Robust linear Model
huber_t_975 = sm.RLM(df_P975['strength'],df_P975[['intercept','radiacion']], M=sm.robust.norms.HuberT())
hub_results_975 = huber_t_975.fit()
slope_975 = hub_results_975.params [1]
intercept_975 = hub_results_975.params [0]
hub_results_975.summary()
hub_results_975.fittedvalues

xm_975 = list(df_P975.radiacion.values)
################################################################################
df_P350 = df_P350.dropna()
df_P350['intercept']=1

##---------Robust linear Model
huber_t_350 = sm.RLM(df_P350['strength'],df_P350[['intercept','radiacion']], M=sm.robust.norms.HuberT())
hub_results_350 = huber_t_350.fit()
slope_350 = hub_results_350.params [1]
intercept_350 = hub_results_350.params [0]
hub_results_350.summary()
hub_results_350.fittedvalues

xm_350 = list(df_P350.radiacion.values)
################################################################################
df_P348 = df_P348.dropna()
df_P348['intercept']=1

##---------Robust linear Model
huber_t_348 = sm.RLM(df_P348['strength'],df_P348[['intercept','radiacion']], M=sm.robust.norms.HuberT())
hub_results_348 = huber_t_348.fit()
slope_348 = hub_results_348.params [1]
intercept_348 = hub_results_348.params [0]
hub_results_348.fittedvalues

xm_348 = list(df_P348.radiacion.values)

################################################################################
##------------------------CALCULO DE LOS ESTADISTICOS-------------------------##
################################################################################

import scipy, scipy.stats.chisquare

esta_val_chi_res975 = scipy.stats.chisquare(df_anomal_975.Anomalia_Potencia.values, f_exp=res_975.fittedvalues.values)[0]
esta_val_chi_hub_results_975 = scipy.stats.chisquare(df_anomal_975.Anomalia_Potencia.values, f_exp=hub_results_975.fittedvalues.values)[0]
esta_val_chi_slr_results_975 = scipy.stats.chisquare(df_anomal_975.Anomalia_Potencia.values, f_exp=slr_results_975.fittedvalues.values)[0]

esta_val_chi_res350 = scipy.stats.chisquare(df_anomal_350.Anomalia_Potencia.values, f_exp=res_350.fittedvalues.values)[0]
esta_val_chi_hub_results_350 = scipy.stats.chisquare(df_anomal_350.Anomalia_Potencia.values, f_exp=hub_results_350.fittedvalues.values)[0]
esta_val_chi_slr_results_350 = scipy.stats.chisquare(df_anomal_350.Anomalia_Potencia.values, f_exp=slr_results_350.fittedvalues.values)[0]

esta_val_chi_res348 = scipy.stats.chisquare(df_anomal_348.Anomalia_Potencia.values, f_exp=res_348.fittedvalues.values)[0]
esta_val_chi_hub_results_348 = scipy.stats.chisquare(df_anomal_348.Anomalia_Potencia.values, f_exp=hub_results_348.fittedvalues.values)[0]
esta_val_chi_slr_results_348 = scipy.stats.chisquare(df_anomal_348.Anomalia_Potencia.values, f_exp=slr_results_348.fittedvalues.values)[0]


################################################################################
##--------------------------CALCULO DE LOS VALORES P--------------------------##
################################################################################
##----Chi2
p_val_chi_res975 = scipy.stats.chisquare(df_P975.strength.values, f_exp=res_975.fittedvalues.values)[1]
p_val_chi_hub_results_975 = scipy.stats.chisquare(df_P975.strength.values, f_exp=hub_results_975.fittedvalues.values)[1]
p_val_chi_slr_results_975 = scipy.stats.chisquare(df_P975.strength.values, f_exp=slr_results_975.fittedvalues.values)[1]

p_val_chi_res350 = scipy.stats.chisquare(df_P350.strength.values, f_exp=res_350.fittedvalues.values)[1]
p_val_chi_hub_results_350 = scipy.stats.chisquare(df_P350.strength.values, f_exp=hub_results_350.fittedvalues.values)[1]
p_val_chi_slr_results_350 = scipy.stats.chisquare(df_P350.strength.values, f_exp=slr_results_350.fittedvalues.values)[1]

p_val_chi_res348 = scipy.stats.chisquare(df_P348.strength.values, f_exp=res_348.fittedvalues.values)[1]
p_val_chi_hub_results_348 = scipy.stats.chisquare(df_P348.strength.values, f_exp=hub_results_348.fittedvalues.values)[1]
p_val_chi_slr_results_348 = scipy.stats.chisquare(df_P348.strength.values, f_exp=slr_results_348.fittedvalues.values)[1]


##----T_Student
p_val_tst_res_975 = st.ttest_ind(df_P975.strength.values, res_975.fittedvalues.values)[1]
p_val_tst_hub_results_975 = st.ttest_ind(df_P975.strength.values, hub_results_975.fittedvalues.values)[1]
p_val_tst_slr_results_975 = st.ttest_ind(df_P975.strength.values, slr_results_975.fittedvalues.values)[1]

p_val_tst_res_350 = st.ttest_ind(df_P350.strength.values, res_350.fittedvalues.values)[1]
p_val_tst_hub_results_350 = st.ttest_ind(df_P350.strength.values, hub_results_350.fittedvalues.values)[1]
p_val_tst_slr_results_350 = st.ttest_ind(df_P350.strength.values, slr_results_350.fittedvalues.values)[1]

p_val_tst_res_348 = st.ttest_ind(df_P348.strength.values, res_348.fittedvalues.values)[1]
p_val_tst_hub_results_348 = st.ttest_ind(df_P348.strength.values, hub_results_348.fittedvalues.values)[1]
p_val_tst_slr_results_348 = st.ttest_ind(df_P348.strength.values, slr_results_348.fittedvalues.values)[1]

from scipy.stats import ks_2samp
##----Smirnov Kolmogorov
p_val_Kv_res_975 = st.ks_2samp(df_P975.strength.values, res_975.fittedvalues.values)[1]
p_val_Kv_hub_results_975 = st.ks_2samp(df_P975.strength.values, hub_results_975.fittedvalues.values)[1]
p_val_Kv_slr_results_975 = st.ks_2samp(df_P975.strength.values, slr_results_975.fittedvalues.values)[1]

p_val_Kv_res_350 = st.ks_2samp(df_P350.strength.values, res_350.fittedvalues.values)[1]
p_val_Kv_hub_results_350 = st.ks_2samp(df_P350.strength.values, hub_results_350.fittedvalues.values)[1]
p_val_Kv_slr_results_350 = st.ks_2samp(df_P350.strength.values, slr_results_350.fittedvalues.values)[1]

p_val_Kv_res_348 = st.ks_2samp(df_P348.strength.values, res_348.fittedvalues.values)[1]
p_val_Kv_hub_results_348 = st.ks_2samp(df_P348.strength.values, hub_results_348.fittedvalues.values)[1]
p_val_Kv_slr_results_348 = st.ks_2samp(df_P348.strength.values, slr_results_348.fittedvalues.values)[1]

################################################################################
##-------------------------------AJUSTE CUADRATICO----------------------------##
################################################################################

z_348    = np.polyfit(df_P348['radiacion'].values, df_P348['strength'].values, 1)
p_348    = np.poly1d(z_348)
df_P348['radiacion'].values.sort()
yfit_348 = np.array([p_348(i) for i in df_P348['radiacion'].values ])
xm_348   = df_P348.radiacion.values
#p_348(1200)

df_P350['radiacion'].values.sort()
z_350    = np.polyfit(df_P350['radiacion'].values, df_P350['strength'].values, 2)
p_350    = np.poly1d(z_350)
yfit_350 = [p_350(i) for i in df_P350['radiacion'].values]
xm_350   = list(df_P350.radiacion.values)

df_P975['radiacion'].values.sort()
z_975    = np.polyfit(df_P975['radiacion'].values, df_P975['strength'].values, 2)
p_975    = np.poly1d(z_975)
yfit_975 = [p_975(i) for i in df_P975['radiacion'].values]
xm_975   = list(df_P975.radiacion.values)

################################################################################
##----------GRAFICO DE LA RELACIÓN ANOMALIAS POT Y REFLECTANCIA --------------##
################################################################################

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(np.log(df_P350_h.radiacion.values), np.log(df_P350_h.strength.values), s=50, c='#b2df8a', alpha=0.5, marker = ".")
#ax1. plot(xm_350,  yfit_350,  color='#1f78b4', linewidth = 1.1, label = 'Poli' )

#ax1. plot(xm_350,  hub_results_350.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'Ajuste por RLM' )
#ax1. plot(xm_350,  slr_results_350.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax1.set_ylabel(u"Potencia $[W]$", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relación en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
#ax1.text(0.2, 25, r'y = ' + str(slope_350.round(3))+'x  '+ str(intercept_350.round(3))  , fontsize=10, fontproperties=prop_1)
ax1.set_ylim(0,100)
ax1.set_xlim(0, 1300)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
# plt.yscale('log')
# plt.xscale('log')
plt.legend()


ax2 = fig.add_subplot(3, 1, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(np.log(df_P975_h.radiacion.values), np.log(df_P975_h.strength.values), s=50, c='#b2df8a', alpha=0.5, marker = ".")
ax2. plot(xm_975,  yfit_975,  color='#1f78b4', linewidth = 1.1, label = 'Poli' )

#ax2. plot(xm_975,  hub_results_975.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'Ajuste por RLM' )
#ax2. plot(xm_975,  slr_results_975.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax2.set_ylabel(u"Potencia $[W]$", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Relación en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.xaxis.set_ticks_position('bottom')
ax2.yaxis.set_ticks_position('left')
#ax2.text(0.2, 25, r'y = ' + str(slope_975.round(3))+'x  '+ str(intercept_975.round(3))  , fontsize=10, fontproperties=prop_1)
ax2.set_ylim(0,100)
ax2.set_xlim(0, 1300)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.yscale('log')
plt.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(np.log(df_P348_h.radiacion.values), np.log(df_P348_h.strength.values), s=50, c='#b2df8a', alpha=0.5, marker = ".")
ax3. plot(xm_348,  yfit_348,  color='#1f78b4', linewidth = 1.1, label = 'Poli' )

#ax3. plot(xm_348,  hub_results_348.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'Ajuste por RLM' )
#ax3. plot(xm_348,  slr_results_348.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax3.set_ylabel(u"Potencia $[W]$", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Relación en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.xaxis.set_ticks_position('bottom')
ax3.yaxis.set_ticks_position('left')
#ax3.text(0.2, 25, r'y = ' + str(slope_348.round(3))+'x  '+ str(intercept_348.round(3))  , fontsize=10, fontproperties=prop_1)
ax3.set_ylim(0,100)
ax3.set_xlim(0, 1300)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.yscale('log')
plt.legend()

plt.subplots_adjust( wspace=0.4, hspace=0.45)
plt.show()








fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_P350_h.radiacion.values, df_P350_h.strength.values, s=50, c='#b2df8a', alpha=0.5, marker = ".")
#ax1. plot(xm_350,  yfit_350,  color='#1f78b4', linewidth = 1.1, label = 'Poli' )
ax1. plot(xm_350,  hub_results_350.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'Ajuste por RLM' )
#ax1. plot(xm_350,  slr_results_350.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax1.set_ylabel(u"Potencia $[W]$", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relación en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
ax1.text(0.2, 25, r'y = ' + str(slope_350.round(3))+'x  '+ str(intercept_350.round(3))  , fontsize=10, fontproperties=prop_1)
ax1.set_ylim(0,100)
ax1.set_xlim(0, 1300)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()


ax2 = fig.add_subplot(3, 1, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(df_P975_h.radiacion.values, df_P975_h.strength.values, s=50, c='#b2df8a', alpha=0.5, marker = ".")
#ax2. plot(xm_975,  yfit_975,  color='#1f78b4', linewidth = 1.1, label = 'Poli' )
ax2. plot(xm_975,  hub_results_975.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'Ajuste por RLM' )
#ax2. plot(xm_975,  slr_results_975.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax2.set_ylabel(u"Potencia $[W]$", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Relación en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.xaxis.set_ticks_position('bottom')
ax2.yaxis.set_ticks_position('left')
ax2.text(0.2, 25, r'y = ' + str(slope_975.round(3))+'x  '+ str(intercept_975.round(3))  , fontsize=10, fontproperties=prop_1)
ax2.set_ylim(0,100)
ax2.set_xlim(0, 1300)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(df_P348_h.radiacion.values, df_P348_h.strength.values, s=50, c='#b2df8a', alpha=0.5, marker = ".")
#ax3. plot(xm_348,  yfit_348,  color='#1f78b4', linewidth = 1.1, label = 'Poli' )
ax3. plot(xm_348,  hub_results_348.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'Ajuste por RLM' )
#ax3. plot(xm_348,  slr_results_348.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax3.set_ylabel(u"Potencia $[W]$", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Irradiancia $[W/m^{2}]$", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Relación en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.xaxis.set_ticks_position('bottom')
ax3.yaxis.set_ticks_position('left')
ax3.text(0.2, 25, r'y = ' + str(slope_348.round(3))+'x  '+ str(intercept_348.round(3))  , fontsize=10, fontproperties=prop_1)
ax3.set_ylim(0,100)
ax3.set_xlim(0, 1300)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

plt.subplots_adjust( wspace=0.4, hspace=0.45)
plt.show()
