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
##-----------------LECTURA DE LOS DATOS DE LOS MAPAS -------------------------##
################################################################################
df_chuscal = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Mapas_Cap4/BosqueChuscal_data.txt', sep=";", header = 0, index_col =0, decimal=',')
df_calasanz = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Mapas_Cap4/Calasanz_data.txt', sep=";", header = 0, index_col =0, decimal=',')
df_campoval = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Mapas_Cap4/Campo_data.txt', sep=";", header = 0, index_col =0, decimal=',')
df_eafit = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Mapas_Cap4/Eafit_data.txt', sep=";", header = 0, index_col =0, decimal=',')
df_jesusmaria = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Mapas_Cap4/JesusMaria_data.txt', sep=";", header = 0, index_col =0, decimal=',')
df_santacruz = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Mapas_Cap4/SataCruz_data.txt', sep=";", header = 0, index_col =0, decimal=',')


################################################################################
##--------------------HISTOGRAMAS DE AREAS POR SECTOR-------------------------##
################################################################################

plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(df_calasanz['AREA'].values, bins=10, alpha = 0.5)
ax1.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax1.set_ylabel(r"Frecuencia absoluta", fontproperties = prop_1)
ax1.set_title(u'Distribución de áreas en el Oeste \n edificaciones altas', loc = 'center', fontproperties = prop, fontsize=10)

ax2=fig.add_subplot(2,3,2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(df_eafit['AREA'].values, bins=10, alpha = 0.5)
ax2.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax2.set_ylabel(r"Frecuencia absoluta", fontproperties = prop_1)
ax2.set_title(u'Distribución de áreas en el Centro \n edificaciones altas', loc = 'center', fontproperties = prop, fontsize=10)

ax3 = fig.add_subplot(2,3,3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(df_chuscal['AREA'].values, bins=10, alpha = 0.5)
ax3.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax3.set_ylabel(r"Frecuencia absoluta", fontproperties = prop_1)
ax3.set_title(u'Distribución de áreas en el Este \n edificaciones altas', loc = 'center', fontproperties = prop, fontsize=10)

ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.hist(df_jesusmaria['AREA'].values, bins=10, color = 'orange',  alpha = 0.8)
ax4.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax4.set_ylabel(r"Frecuencia absoluta", fontproperties = prop_1)
ax4.set_title(u'Distribución de áreas en el Oeste \n edificaciones bajas', loc = 'center', fontproperties = prop, fontsize=10)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.hist(df_santacruz['AREA'].values, bins=10, color = 'orange',  alpha = 0.8)
ax5.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax5.set_ylabel(r"Frecuencia absoluta", fontproperties = prop_1)
ax5.set_title(u'Distribución de áreas en el Centro \n edificaciones bajas', loc = 'center', fontproperties = prop, fontsize=10)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.hist(df_campoval['AREA'].values, bins=10, color = 'orange',  alpha = 0.8)
ax6.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax6.set_ylabel(r"Frecuencia absoluta", fontproperties = prop_1)
ax6.set_title(u'Distribución de áreas en el Este \n edificaciones bajas', loc = 'center', fontproperties = prop, fontsize=10)

plt.subplots_adjust(wspace=0.3, hspace=0.38)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Histo_Areas_ZonasUrb.pdf', format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Histo_Areas_ZonasUrb.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


################################################################################
##--------------------SCATTERS ÁREA VS ENERGÍA GENERADA-----------------------##
################################################################################

plt.close("all")
fig = plt.figure(figsize=(10., 8.),facecolor='w',edgecolor='w')
ax1=fig.add_subplot(2,3,1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.scatter(df_calasanz['AREA'].values,df_calasanz['Elec_Prod_'].values,  s=50, c='#2980B9', alpha=0.5, marker = ".")
ax1.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax1.set_ylabel(r"Energia  al año $[MWh]$", fontproperties = prop_1)
ax1.set_title(u'Relación energía y áreas en el Oeste \n edificaciones altas', loc = 'center', fontproperties = prop, fontsize=10)

ax2=fig.add_subplot(2,3,2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.scatter( df_eafit['AREA'].values, df_eafit['Elec_Prod_'].values, s=50, c='#2980B9', alpha=0.5, marker = ".")
ax2.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax2.set_ylabel(r"Energia  al año $[MWh]$", fontproperties = prop_1)
ax2.set_title(u'Relación energía y áreas en el Centro \n edificaciones altas', loc = 'center', fontproperties = prop, fontsize=10)

ax3 = fig.add_subplot(2,3,3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.scatter( df_chuscal['AREA'].values, df_chuscal['Elec_Prod_'].values, s=50, c='#2980B9', alpha=0.5, marker = ".")
ax3.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax3.set_ylabel(r"Energia  al año $[MWh]$", fontproperties = prop_1)
ax3.set_title(u'Relación energía y áreas en el Este \n edificaciones altas', loc = 'center', fontproperties = prop, fontsize=10)

ax4 = fig.add_subplot(2,3,4)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.scatter( df_jesusmaria['AREA'].values, df_jesusmaria['Elec_Prod_'].values, s=50, c='orange', alpha=0.8, marker = ".")
ax4.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax4.set_ylabel(r"Energia  al año $[MWh]$", fontproperties = prop_1)
ax4.set_title(u'Relación energía y áreas en el Oeste \n edificaciones bajas', loc = 'center', fontproperties = prop, fontsize=10)

ax5 = fig.add_subplot(2,3,5)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.scatter( df_santacruz['AREA'].values, df_santacruz['Elec_Prod_'].values, s=50, c='orange', alpha=0.8, marker = ".")
ax5.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax5.set_ylabel(r"Energia  al año $[MWh]$", fontproperties = prop_1)
ax5.set_title(u'Relación energía y áreas en el Centro \n edificaciones bajas', loc = 'center', fontproperties = prop, fontsize=10)

ax6 = fig.add_subplot(2,3,6)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)
ax6.scatter(df_campoval['AREA'].values,df_campoval['Elec_Prod_'].values,  s=50, c='orange', alpha=0.8, marker = ".")
ax6.set_xlabel(u'Área $[m^{2}]$', fontproperties = prop_1)
ax6.set_ylabel(r"Energia  al año $[MWh]$", fontproperties = prop_1)
ax6.set_title(u'Relación energía y áreas en el Este \n edificaciones bajas', loc = 'center', fontproperties = prop, fontsize=10)

plt.subplots_adjust(wspace=0.3, hspace=0.38)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Scatter_EnergyAreas_ZonasUrb.pdf', format='pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/Scatter_EnergyAreas_ZonasUrb.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')
