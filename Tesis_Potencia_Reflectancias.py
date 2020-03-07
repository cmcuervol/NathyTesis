#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
import matplotlib
# matplotlib.use('Agg')
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
import statistics
from scipy.stats import pearsonr
from scipy import stats
import scipy.stats as st
import scipy.special as sp


#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

################################################################################
##-----------------LECTURA DE LOS DATOS DE LAS ANOMALIAS ---------------------##
################################################################################
Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
df_anomal_975 = pd.read_csv(Path_save+'ConPotencia_EXP_Anomalias_VariablesCondicionantes_975.csv',  sep=',', index_col =0)
df_anomal_350 = pd.read_csv(Path_save+'ConPotencia_EXP_Anomalias_VariablesCondicionantes_350.csv',  sep=',', index_col =0)
df_anomal_348 = pd.read_csv(Path_save+'ConPotencia_EXP_Anomalias_VariablesCondicionantes_348.csv',  sep=',', index_col =0)

df_anomal_975.index = pd.to_datetime(df_anomal_975.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_anomal_350.index = pd.to_datetime(df_anomal_350.index, format="%Y-%m-%d %H:%M", errors='coerce')
df_anomal_348.index = pd.to_datetime(df_anomal_348.index, format="%Y-%m-%d %H:%M", errors='coerce')


################################################################################
##-------------------REGRESION LINEAL METODO STATS MODEL----------------------##
################################################################################
import statsmodels.api as sm
import statsmodels.formula.api as smf

df_anomal_975 = df_anomal_975.dropna()
df_anomal_975['intercept']=1

##--------Lineal Mínimos cuadrados
lm_975 =sm.OLS(df_anomal_975['Anomalia_Potencia'],df_anomal_975[['intercept','Anomalia_FR']])
slr_results_975 = lm_975.fit()
slr_results_975.summary()
slr_results_975.fittedvalues

##--------LAD special case of quantile regression where q=0.5
mod_975 = smf.quantreg('Anomalia_Potencia ~ Anomalia_FR', df_anomal_975)
res_975 = mod_975.fit(q=.5)
res_975.summary()
res_975.fittedvalues

##---------Robust linear Model
huber_t_975 = sm.RLM(df_anomal_975['Anomalia_Potencia'],df_anomal_975[['intercept','Anomalia_FR']], M=sm.robust.norms.HuberT())
hub_results_975 = huber_t_975.fit()
hub_results_975.summary()
hub_results_975.fittedvalues

xm_975 = list(df_anomal_975.Anomalia_FR.values)
################################################################################
df_anomal_350 = df_anomal_350.dropna()
df_anomal_350['intercept']=1

##--------Lineal Mínimos cuadrados
lm_350 =sm.OLS(df_anomal_350['Anomalia_Potencia'],df_anomal_350[['intercept','Anomalia_FR']])
slr_results_350 = lm_350.fit()
slr_results_350.summary()
slr_results_350.fittedvalues

##--------LAD special case of quantile regression where q=0.5
mod_350 = smf.quantreg('Anomalia_Potencia ~ Anomalia_FR', df_anomal_350)
res_350 = mod_350.fit(q=.5)
res_350.summary()
res_350.fittedvalues

##---------Robust linear Model
huber_t_350 = sm.RLM(df_anomal_350['Anomalia_Potencia'],df_anomal_350[['intercept','Anomalia_FR']], M=sm.robust.norms.HuberT())
hub_results_350 = huber_t_350.fit()
hub_results_350.summary()
hub_results_350.fittedvalues

xm_350 = list(df_anomal_350.Anomalia_FR.values)
################################################################################
df_anomal_348 = df_anomal_348.dropna()
df_anomal_348['intercept']=1

##--------Lineal Mínimos cuadrados
lm_348 =sm.OLS(df_anomal_348['Anomalia_Potencia'],df_anomal_348[['intercept','Anomalia_FR']])
slr_results_348 = lm_348.fit()
slr_results_348.summary()
slr_results_348.fittedvalues

##--------LAD special case of quantile regression where q=0.5
mod_348 = smf.quantreg('Anomalia_Potencia ~ Anomalia_FR', df_anomal_348)
res_348 = mod_348.fit(q=.5)
res_348.summary()
res_348.fittedvalues

##---------Robust linear Model
huber_t_348 = sm.RLM(df_anomal_348['Anomalia_Potencia'],df_anomal_348[['intercept','Anomalia_FR']], M=sm.robust.norms.HuberT())
hub_results_348 = huber_t_348.fit()
v
hub_results_348.fittedvalues

xm_348 = list(df_anomal_348.Anomalia_FR.values)

################################################################################
##--------------------------CALCULO DE LOS VALORES P--------------------------##
################################################################################
import scipy, scipy.stats.chisquare
##----Chi2
p_val_chi_res975 = scipy.stats.chisquare(df_anomal_975.Anomalia_Potencia.values, f_exp=res_975.fittedvalues.values)[1]
p_val_chi_hub_results_975 = scipy.stats.chisquare(df_anomal_975.Anomalia_Potencia.values, f_exp=hub_results_975.fittedvalues.values)[1]
p_val_chi_slr_results_975 = scipy.stats.chisquare(df_anomal_975.Anomalia_Potencia.values, f_exp=slr_results_975.fittedvalues.values)[1]

p_val_chi_res350 = scipy.stats.chisquare(df_anomal_350.Anomalia_Potencia.values, f_exp=res_350.fittedvalues.values)[1]
p_val_chi_hub_results_350 = scipy.stats.chisquare(df_anomal_350.Anomalia_Potencia.values, f_exp=hub_results_350.fittedvalues.values)[1]
p_val_chi_slr_results_350 = scipy.stats.chisquare(df_anomal_350.Anomalia_Potencia.values, f_exp=slr_results_350.fittedvalues.values)[1]

p_val_chi_res348 = scipy.stats.chisquare(df_anomal_348.Anomalia_Potencia.values, f_exp=res_348.fittedvalues.values)[1]
p_val_chi_hub_results_348 = scipy.stats.chisquare(df_anomal_348.Anomalia_Potencia.values, f_exp=hub_results_348.fittedvalues.values)[1]
p_val_chi_slr_results_348 = scipy.stats.chisquare(df_anomal_348.Anomalia_Potencia.values, f_exp=slr_results_348.fittedvalues.values)[1]

##----T_Student
p_val_tst_res_975 = st.ttest_ind(df_anomal_975.Anomalia_Potencia.values, res_975.fittedvalues.values)[1]
p_val_tst_hub_results_975 = st.ttest_ind(df_anomal_975.Anomalia_Potencia.values, hub_results_975.fittedvalues.values)[1]
p_val_tst_slr_results_975 = st.ttest_ind(df_anomal_975.Anomalia_Potencia.values, slr_results_975.fittedvalues.values)[1]

p_val_tst_res_350 = st.ttest_ind(df_anomal_350.Anomalia_Potencia.values, res_350.fittedvalues.values)[1]
p_val_tst_hub_results_350 = st.ttest_ind(df_anomal_350.Anomalia_Potencia.values, hub_results_350.fittedvalues.values)[1]
p_val_tst_slr_results_350 = st.ttest_ind(df_anomal_350.Anomalia_Potencia.values, slr_results_350.fittedvalues.values)[1]

p_val_tst_res_348 = st.ttest_ind(df_anomal_348.Anomalia_Potencia.values, res_348.fittedvalues.values)[1]
p_val_tst_hub_results_348 = st.ttest_ind(df_anomal_348.Anomalia_Potencia.values, hub_results_348.fittedvalues.values)[1]
p_val_tst_slr_results_348 = st.ttest_ind(df_anomal_348.Anomalia_Potencia.values, slr_results_348.fittedvalues.values)[1]

################################################################################
##----------GRAFICO DE LA RELACIÓN ANOMALIAS POT Y REFLECTANCIA --------------##
################################################################################

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_anomal_350.Anomalia_FR.values, df_anomal_350.Anomalia_Potencia.values, s=50, c='#b2df8a', alpha=0.5, marker = ".")
ax1. plot(xm_350,  res_350.fittedvalues.values,  color='#1f78b4', linewidth = 1.1, label = 'LAD' )
ax1. plot(xm_350,  hub_results_350.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'RLM' )
ax1. plot(xm_350,  slr_results_350.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax1.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relacion en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
#ax1.text(-69, 25, r'Y = ' + str(slope_350.round(3))+'x  '+ str(intercept_350.round(3))  , fontsize=10, fontproperties=prop_1)
ax1.set_ylim(-60, 60)
ax1.set_xlim(-70, 70)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()


ax2 = fig.add_subplot(3, 1, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(df_anomal_975.Anomalia_FR.values, df_anomal_975.Anomalia_Potencia.values, s=50, c='#b2df8a', alpha=0.5, marker = ".")
ax2. plot(xm_975,  res_975.fittedvalues.values,  color='#1f78b4', linewidth = 1.1, label = 'LAD' )
ax2. plot(xm_975,  hub_results_975.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'RLM' )
ax2. plot(xm_975,  slr_results_975.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax2.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Relacion en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.xaxis.set_ticks_position('bottom')
ax2.yaxis.set_ticks_position('left')
#ax2.text(-69, 25, r'Y = ' + str(slope_975.round(3))+'x  '+ str(intercept_975.round(3))  , fontsize=10, fontproperties=prop_1)
ax2.set_ylim(-60, 60)
ax2.set_xlim(-70, 70)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(df_anomal_348.Anomalia_FR.values, df_anomal_348.Anomalia_Potencia.values, s=50, c='#b2df8a', alpha=0.5, marker = ".")
ax3. plot(xm_348,  res_348.fittedvalues.values,  color='#1f78b4', linewidth = 1.1, label = 'LAD' )
ax3. plot(xm_348,  hub_results_348.fittedvalues.values,  color = '#fc8d62',  linewidth = 1.1, label = 'RLM' )
ax3. plot(xm_348,  slr_results_348.fittedvalues.values,  color = '#33a02c',  linewidth = 1.1, label = 'OLS' )
ax3.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Relacion en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.xaxis.set_ticks_position('bottom')
ax3.yaxis.set_ticks_position('left')
#ax3.text(-69, 25, r'Y = ' + str(slope_348.round(3))+'x  '+ str(intercept_348.round(3))  , fontsize=10, fontproperties=prop_1)
ax3.set_ylim(-60, 60)
ax3.set_xlim(-70, 70)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

plt.subplots_adjust( wspace=0.4, hspace=0.45)
plt.show()









































################################################################################
##----------------------STD DE LAS VARIABLES POR HORAS  ----------------------##
################################################################################
df_anomal_975_CDstd = df_anomal_975.groupby(by=[df_anomal_975.index.hour]).std()
df_anomal_350_CDstd = df_anomal_350.groupby(by=[df_anomal_350.index.hour]).std()
df_anomal_348_CDstd = df_anomal_348.groupby(by=[df_anomal_348.index.hour]).std()

df_anomal_975_CDstd = df_anomal_975_CDstd[df_anomal_975_CDstd.Anomalia>0]
df_anomal_350_CDstd = df_anomal_350_CDstd[df_anomal_350_CDstd.Anomalia>0]
df_anomal_348_CDstd = df_anomal_348_CDstd[df_anomal_348_CDstd.Anomalia>0]



##-------------------------------GRAFICA STD CA----------------------------##
plt.close('all')
fig = plt.figure(figsize=(18,9))
ax1 = fig.add_subplot(1, 2, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.plot(df_anomal_350_CDstd.index.values,  df_anomal_350_CDstd.Anomalia_FR.values, color = '#52C1BA', lw=1.5, label = 'Oeste')
ax1.scatter(df_anomal_350_CDstd.index.values,  df_anomal_350_CDstd.Anomalia_FR.values, marker='.', color = '#52C1BA', s=30)
ax1.plot(df_anomal_975_CDstd.index.values,  df_anomal_975_CDstd.Anomalia_FR.values, color = '#09202E', lw=1.5, label = 'Centro-Oeste')
ax1.scatter(df_anomal_975_CDstd.index.values,  df_anomal_975_CDstd.Anomalia_FR.values, marker='.', color = '#09202E', s=30)
ax1.plot(df_anomal_348_CDstd.index.values,  df_anomal_348_CDstd.Anomalia_FR.values, color = '#0b6623', lw=1.5, label = 'Este')
ax1.scatter(df_anomal_348_CDstd.index.values,  df_anomal_348_CDstd.Anomalia_FR.values, marker='.', color = '#0b6623', s=30)
ax1.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax1.set_ylabel(u"[%]", fontproperties = prop_1, fontsize=20)
ax1.set_xticks(range(6, 18), minor=False)
ax1.set_xticklabels(df_anomal_350_CDstd.index, minor=False, rotation = 20)
ax1.set_ylim(0, 30)
ax1.set_title(u'Desviasión estándar horaria de reflectancia ', loc = 'center', fontproperties = prop, fontsize=23)
plt.legend()

ax2 = fig.add_subplot(1, 2, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.plot(df_anomal_350_CDstd.index.values,  df_anomal_350_CDstd.Anomalia_Potencia.values, color = '#52C1BA', lw=1.5, label = 'Oeste')
ax2.scatter(df_anomal_350_CDstd.index.values,  df_anomal_350_CDstd.Anomalia_Potencia.values, marker='.', color = '#52C1BA', s=30)
ax2.plot(df_anomal_975_CDstd.index.values,  df_anomal_975_CDstd.Anomalia_Potencia.values, color = '#09202E', lw=1.5, label = 'Centro-Oeste')
ax2.scatter(df_anomal_975_CDstd.index.values,  df_anomal_975_CDstd.Anomalia_Potencia.values, marker='.', color = '#09202E', s=30)
ax2.plot(df_anomal_348_CDstd.index.values,  df_anomal_348_CDstd.Anomalia_Potencia.values, color = '#0b6623', lw=1.5, label = 'Este')
ax2.scatter(df_anomal_348_CDstd.index.values,  df_anomal_348_CDstd.Anomalia_Potencia.values, marker='.', color = '#0b6623', s=30)
ax2.set_xlabel('Horas del dia', fontproperties = prop_1, fontsize=17)
ax2.set_ylabel(u"[W]", fontproperties = prop_1, fontsize=20)
ax2.set_xticks(range(6, 18), minor=False)
ax2.set_xticklabels(df_anomal_350_CDstd.index, minor=False, rotation = 20)
ax2.set_ylim(0, 50)
ax2.set_title(u'Desviasión estándar horaria de potencia ', loc = 'center', fontproperties = prop, fontsize=23)
plt.legend()

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.2, hspace=0.25)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/STD_Duirna_FR_Pot.pdf', format='pdf', transparent=True)
os.system('scp /home/nacorreasa/Escritorio/Figuras/STD_Duirna_FR_Pot.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


################################################################################
##------------REGRESION LINEAL DE LOS DATOS DE LAS DOS ANOMALIAS -------------##
################################################################################

df_anomal_975 = df_anomal_975.dropna()
xm_975 = list(df_anomal_975.Anomalia_FR.values)
ym_975 = list(df_anomal_975.Anomalia_Potencia.values)
slope_975, intercept_975, r_value, p_value, std_err_975 = stats.linregress(xm_975, ym_975)
xm_975.sort()
yfit_975 = [intercept_975 + slope_975 * xi for xi in xm_975]

df_anomal_350 = df_anomal_350.dropna()
xm_350 = list(df_anomal_350.Anomalia_FR.values)
ym_350 = list(df_anomal_350.Anomalia_Potencia.values)
slope_350, intercept_350, r_value, p_value, std_err_350 = stats.linregress(xm_350, ym_350)
xm_350.sort()
yfit_350 = [intercept_350 + slope_350 * xi for xi in xm_350]


df_anomal_348 = df_anomal_348.dropna()
xm_348 = list(df_anomal_348.Anomalia_FR.values)
ym_348 = list(df_anomal_348.Anomalia_Potencia.values)
slope_348, intercept_348, r_value, p_value, std_err_348 = stats.linregress(xm_348, ym_348)
xm_348.sort()
yfit_348 = [intercept_348 + slope_348 * xi for xi in xm_348]

################################################################################
##----------GRAFICO DE LA RELACIÓN ANOMALIAS POT Y REFLECTANCIA --------------##
################################################################################

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_anomal_350.Anomalia_FR.values, df_anomal_350.Anomalia_Potencia.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax1. plot(xm_350,  yfit_350,  color='#09202E', linewidth = 1.1, label = 'Linea de ajuste' )
ax1.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relacion en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
ax1.text(-69, 25, r'Y = ' + str(slope_350.round(3))+'x  '+ str(intercept_350.round(3))  , fontsize=10, fontproperties=prop_1)
ax1.set_ylim(-60, 60)
ax1.set_xlim(-70, 70)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()


ax2 = fig.add_subplot(3, 1, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(df_anomal_975.Anomalia_FR.values, df_anomal_975.Anomalia_Potencia.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax2. plot(xm_975, yfit_975,  color='#09202E', linewidth = 1.1, label = 'Linea de ajuste' )
ax2.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Relacion en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.xaxis.set_ticks_position('bottom')
ax2.yaxis.set_ticks_position('left')
ax2.text(-69, 25, r'Y = ' + str(slope_975.round(3))+'x  '+ str(intercept_975.round(3))  , fontsize=10, fontproperties=prop_1)
ax2.set_ylim(-60, 60)
ax2.set_xlim(-70, 70)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(df_anomal_348.Anomalia_FR.values, df_anomal_348.Anomalia_Potencia.values, s=50, c='#004D56', alpha=0.5, marker = ".")
ax3. plot(xm_348, yfit_348,  color='#09202E', linewidth = 1.1, label = 'Linea de ajuste' )
ax3.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Relacion en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.xaxis.set_ticks_position('bottom')
ax3.yaxis.set_ticks_position('left')
ax3.text(-69, 25, r'Y = ' + str(slope_348.round(3))+'x  '+ str(intercept_348.round(3))  , fontsize=10, fontproperties=prop_1)
ax3.set_ylim(-60, 60)
ax3.set_xlim(-70, 70)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()


plt.subplots_adjust( wspace=0.4, hspace=0.45)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_Anomal_Pot_vs_Anomalia_FR.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_Anomal_Pot_vs_Anomalia_FR.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')








df_anomal_350['Hora'] = list(df_anomal_350.index.hour)
df_anomal_975['Hora'] = list(df_anomal_975.index.hour)
df_anomal_348['Hora'] = list(df_anomal_348.index.hour)

colors = {6:'#800000', 7:'#e6194B', 8:'#f58231', 9:'#9A6324', 10:'#bfef45', 11:'#3cb44b', 12:'#42d4f4', 13:'#469990', 14:'#000075', 15:'#4363d8', 16:'#911eb4', 17:'#f032e6'}

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_anomal_350.Anomalia_FR.values, df_anomal_350.Anomalia_Potencia.values, s=50, c=df_anomal_350['Hora'].apply(lambda x: colors[x]), alpha=0.5, marker = ".")
ax1. plot(xm_350,  yfit_350,  color='#09202E', linewidth = 1.1, label = 'Linea de ajuste' )
ax1.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax1.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax1.set_title(u'Relacion en el Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax1.xaxis.set_ticks_position('bottom')
ax1.yaxis.set_ticks_position('left')
ax1.text(-69, 25, r'Y = ' + str(slope_350.round(3))+'x  '+ str(intercept_350.round(3))  , fontsize=10, fontproperties=prop_1)
ax1.set_ylim(-60, 60)
ax1.set_xlim(-70, 70)
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()


ax2 = fig.add_subplot(3, 1, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter(df_anomal_975.Anomalia_FR.values, df_anomal_975.Anomalia_Potencia.values, s=50, c=df_anomal_975['Hora'].apply(lambda x: colors[x]), alpha=0.5, marker = ".")
ax2. plot(xm_975, yfit_975,  color='#09202E', linewidth = 1.1, label = 'Linea de ajuste' )
ax2.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax2.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax2.set_title(u'Relacion en el Centro-Oeste' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax2.xaxis.set_ticks_position('bottom')
ax2.yaxis.set_ticks_position('left')
ax2.text(-69, 25, r'Y = ' + str(slope_975.round(3))+'x  '+ str(intercept_975.round(3))  , fontsize=10, fontproperties=prop_1)
ax2.set_ylim(-60, 60)
ax2.set_xlim(-70, 70)
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter(df_anomal_348.Anomalia_FR.values, df_anomal_348.Anomalia_Potencia.values, s=50, c=df_anomal_348['Hora'].apply(lambda x: colors[x]), alpha=0.5, marker = ".")
ax3. plot(xm_348, yfit_348,  color='#09202E', linewidth = 1.1, label = 'Linea de ajuste' )
ax3.set_ylabel(u"Anomalia de \n Potencia $[Wh]$", fontsize=14, fontproperties=prop_1)
ax3.set_xlabel(u"Anomalía Reflectancia [%]", fontsize=14, fontproperties=prop_1)
ax3.set_title(u'Relacion en el Este' ,  fontsize=10,  fontweight = "bold",  fontproperties = prop)
ax3.xaxis.set_ticks_position('bottom')
ax3.yaxis.set_ticks_position('left')
ax3.text(-69, 25, r'Y = ' + str(slope_348.round(3))+'x  '+ str(intercept_348.round(3))  , fontsize=10, fontproperties=prop_1)
ax3.set_ylim(-60, 60)
ax3.set_xlim(-70, 70)
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
plt.legend()


plt.subplots_adjust( wspace=0.4, hspace=0.45)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_Anomal_Pot_vs_Anomalia_FR.pdf',  format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_Anomal_Pot_vs_Anomalia_FR.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
