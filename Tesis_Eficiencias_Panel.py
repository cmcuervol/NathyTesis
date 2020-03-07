#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import pearsonr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.transforms as transforms

#-----------------------------------------------------------------------------
# Motivación del Codigo ------------------------------------------------------

"""
Codigo para el análisis de la potencia de los paneles , y las eficiencias de acuerdo
a las características de los paneles y los datos meteorológicos y de radaición.
"""

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##########################################################################################
## ----------------LECTURA DE LOS DATOS DE LOS EXPERIMENTOS Y RADIACION---------------- ##
##########################################################################################

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

df_P975 = df_P975[df_P975['strength'] <=100]
df_P350 = df_P350[df_P350['strength'] <=100]
df_P348 = df_P348[df_P348['strength'] <=100]

df_P975_h = df_P975.groupby(pd.Grouper(freq="H")).mean()
df_P350_h = df_P350.groupby(pd.Grouper(freq="H")).mean()
df_P348_h = df_P348.groupby(pd.Grouper(freq="H")).mean()

##########################################################################################
## ---------------LECTURA DE LOS DATOS DE TEMPERATURA Y HUMEDAD RELATIVA--------------- ##
##########################################################################################

data_T_Torre = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad201.txt',  sep=',')
data_T_Conse = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad206.txt',  sep=',')
data_T_Joaqu = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Meteorologicas/Entrega_TH_CuRad367.txt',  sep=',')

data_T_Torre.index = data_T_Torre['fecha_hora']
data_T_Torre = data_T_Torre.drop(['fecha_hora'], axis=1)
data_T_Torre.index = pd.to_datetime(data_T_Torre.index)
data_T_Torre = data_T_Torre.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
data_T_Torre = data_T_Torre[data_T_Torre['T']>0]
data_T_Torre_h = data_T_Torre.groupby(pd.Grouper(freq="H")).mean()

data_T_Conse.index = data_T_Conse['fecha_hora']
data_T_Conse = data_T_Conse.drop(['fecha_hora'], axis=1)
data_T_Conse.index = pd.to_datetime(data_T_Conse.index)
data_T_Conse = data_T_Conse.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
data_T_Conse = data_T_Conse[data_T_Conse['T']>0]
data_T_Conse_h = data_T_Conse.groupby(pd.Grouper(freq="H")).mean()

data_T_Joaqu.index = data_T_Joaqu['fecha_hora']
data_T_Joaqu = data_T_Joaqu.drop(['fecha_hora'], axis=1)
data_T_Joaqu.index = pd.to_datetime(data_T_Joaqu.index)
data_T_Joaqu = data_T_Joaqu.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
data_T_Joaqu = data_T_Joaqu[data_T_Joaqu['T']>0]
data_T_Joaqu_h = data_T_Joaqu.groupby(pd.Grouper(freq="H")).mean()


################################################################################
## -----------------------CARACTERISTICAS DEL PANEL-------------------------- ##
################################################################################
Voc = 22.68    ## --> En V
Isc = 8.62     ## --> En A
Area_TS = 0.66    ## --> En m2
Area_Laderas = 0.60    ## --> En m2

################################################################################
## -------------------OBTENER EL PUNTO DE MÁXIMA POTENCIA-------------------- ##
################################################################################

df_P975['Max_Strength'] = df_P975.groupby(df_P975.index.date)['strength'].transform('max')
df_P975_max = df_P975[df_P975['Max_Strength'] == df_P975["strength"]]
# df_P975_max = df_P975_max.groupby(pd.Grouper(freq='D')).first()

df_P350['Max_Strength'] = df_P350.groupby(df_P350.index.date)['strength'].transform('max')
df_P350_max = df_P350[df_P350['Max_Strength'] == df_P350["strength"]]
# df_P350_max = df_P350.groupby(pd.Grouper(freq='D')).first()

df_P348['Max_Strength'] = df_P348.groupby(df_P348.index.date)['strength'].transform('max')
df_P348_max = df_P348[df_P348['Max_Strength'] == df_P348["strength"]]
# df_P348_max = df_P348.groupby(pd.Grouper(freq='D')).first()

#######################################################################################
## ----------------OBTENER LA EFICIENCIA EN LA CONVERSION DE ENERGÍA---------------- ##
#######################################################################################

df_P975_max['E_ConvE'] = df_P975_max['Max_Strength']/(df_P975_max['radiacion']*Area_TS)
df_P350_max['E_ConvE'] = df_P350_max['Max_Strength']/(df_P350_max['radiacion']*Area_Laderas)
df_P348_max['E_ConvE'] = df_P348_max['Max_Strength']/(df_P348_max['radiacion']*Area_Laderas)

###############################################################################################################
## ----------------OBTERNER EFICIENCIA ANTE CONDICIONES VARIANTES DE RADIACION Y TEMPERATURA---------------- ##
###############################################################################################################

df_All_P975 = pd.concat([df_P975_h, data_T_Torre_h], axis = 1)
df_All_P348 = pd.concat([df_P348_h, data_T_Joaqu_h], axis = 1)
df_All_P350 = pd.concat([df_P350_h, data_T_Conse_h], axis = 1)

df_All_P975 = df_All_P975.between_time('06:00', '18:00')              ##--> Seleccionar solo los datos de horas del dia
df_All_P350 = df_All_P350.between_time('06:00', '18:00')              ##--> Seleccionar solo los datos de horas del dia
df_All_P348 = df_All_P348.between_time('06:00', '18:00')              ##--> Seleccionar solo los datos de horas del dia

T_noct = 48         ## --> Temperatura nominal operativa en °C

Tm_P975 = (T_noct - 20)*(df_All_P975['radiacion'].values / 800)+df_All_P975['T'].values
Tm_P350 = (T_noct - 20)*(df_All_P350['radiacion'].values / 800)+df_All_P350['T'].values
Tm_P348 = (T_noct - 20)*(df_All_P348['radiacion'].values / 800)+df_All_P348['T'].values

Go = 1000           ## --> Condicion de radiacion estandar de la prueba en W/m2
To = 25             ## --> Condicion de temperatura estandar de la prueba en °C
no = 10.12          ## --> Eficiencia de todo el panel a condicioines estandar en %
a  = 1.20E-3        ## --> Parámetro empirico en °C^-1
b  = -4.60E-3       ## --> Parámetro empirico en °C^-1
c1 = 0.033          ## --> Parámetro empirico
c2 = -0.0092        ## --> Parámetro empirico

n_975 = no*(1+a*(Tm_P975-To))*(1+c1*np.log(df_All_P975['radiacion'].values/Go)+c2*(np.log(df_All_P975['radiacion'].values/Go))**2+b*(Tm_P975-To))
n_350 = no*(1+a*(Tm_P350-To))*(1+c1*np.log(df_All_P350['radiacion'].values/Go)+c2*(np.log(df_All_P350['radiacion'].values/Go))**2+b*(Tm_P350-To))
n_348 = no*(1+a*(Tm_P348-To))*(1+c1*np.log(df_All_P348['radiacion'].values/Go)+c2*(np.log(df_All_P348['radiacion'].values/Go))**2+b*(Tm_P348-To))

df_n_975 = pd.DataFrame()
df_n_975['Desemp'] = n_975
df_n_975.index = df_All_P975.index

df_n_350 = pd.DataFrame()
df_n_350['Desemp'] = n_350
df_n_350.index = df_All_P350.index

df_n_348 = pd.DataFrame()
df_n_348['Desemp'] = n_348
df_n_348.index = df_All_P348.index

########################################################################################
## ----------------OBTENER LA EFICIENCIA NOMINAL EN TODOS LOS TIEMPOS---------------- ##
########################################################################################
Potencia_Ideal = Area_TS*1000

df_P348_h_Efi = ((df_P348_h[u'strength']/Potencia_Ideal) * 100).to_frame()
df_P350_h_Efi = ((df_P350_h[u'strength']/Potencia_Ideal) * 100).to_frame()
df_P975_h_Efi = ((df_P975_h[u'strength']/Potencia_Ideal) * 100).to_frame()


df_P348_h_Efi.columns = [ 'Efi']
df_P350_h_Efi.columns = [ 'Efi']
df_P975_h_Efi.columns = [ 'Efi']

df_P348_h_Efi.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Efi_tiempo_nominal_P348.csv')
df_P350_h_Efi.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Efi_tiempo_nominal_P350.csv')
df_P975_h_Efi.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Efi_tiempo_nominal_P975.csv')

##########################################################################################################################
## ---------------CICLOS DIURNOS DE LA EFICIENCIA ANTE CONDICIONES VARIANTES DE RADIACION Y TEMPERATURA---------------- ##
##########################################################################################################################

new_idx = np.arange(6, 18, 1)

df_n_975_CD  = df_n_975.groupby(by=[df_n_975.index.hour]).mean()
df_n_975_CD  = df_n_975_CD.reindex(new_idx)

df_n_350_CD  = df_n_350.groupby(by=[df_n_350.index.hour]).mean()
df_n_350_CD  = df_n_350_CD.reindex(new_idx)

df_n_348_CD  = df_n_348.groupby(by=[df_n_348.index.hour]).mean()
df_n_348_CD  = df_n_348_CD.reindex(new_idx)

#########################################################################################################################
## ----------------DIFERENCIAS EN LAS EFICIENCIA ANTE CONDICIONES VARIANTES DE RADIACION Y TEMPERATURA---------------- ##
#########################################################################################################################
dif_n_CD_P348_P350 = df_n_348_CD['Desemp'].values - df_n_350_CD['Desemp'].values

dif_n_CD_P348_P975 = df_n_348_CD['Desemp'].values - df_n_975_CD['Desemp'].values

dif_n_CD_P350_P975 = df_n_350_CD['Desemp'].values - df_n_975_CD['Desemp'].values

################################################################################################################################
## ----------------OBTENER EL PUNTO DE MÁXIMA EFICIENCIA ANTE CONDICIONES VARIANTES DE RADIACION Y TEMPERATURA--------------- ##
################################################################################################################################

df_n_975['Max_Performance'] = df_n_975.groupby(df_n_975.index.date)['Desemp'].transform('max')
df_n_975_max = df_n_975[df_n_975['Max_Performance'] == df_n_975['Desemp']]

df_n_350['Max_Performance'] = df_n_350.groupby(df_n_350.index.date)['Desemp'].transform('max')
df_n_350_max = df_n_350[df_n_350['Max_Performance'] == df_n_350['Desemp']]

df_n_348['Max_Performance'] = df_n_348.groupby(df_n_348.index.date)['Desemp'].transform('max')
df_n_348_max = df_n_348[df_n_348['Max_Performance'] == df_n_348['Desemp']]

##------------------------------------------------------------------------------------------##

df_n_348_max.index = df_n_348_max.index.date
df_n_350_max.index = df_n_350_max.index.date
df_n_975_max.index = df_n_975_max.index.date

df_n_348_max_serie = df_n_348_max.reindex(df_n_975_max.index)
df_n_350_max_serie = df_n_350_max.reindex(df_n_975_max.index)
df_n_975_max_serie = df_n_975_max.reindex(df_n_975_max.index)

################################################################################
## ----------------CICLO DIURNO DE LA POTENCIA DE LOS PANELES---------------- ##
################################################################################

df_P975 = df_P975[df_P975["strength"] > 0]
df_P350 = df_P350[df_P350["strength"] > 0]
df_P348 = df_P348[df_P348["strength"] > 0]

df_P975_CD  = df_P975.groupby(by=[df_P975.index.hour]).mean()
df_P975_CD  = df_P975_CD.reindex(new_idx)

df_P350_CD  = df_P350.groupby(by=[df_P350.index.hour]).mean()
df_P350_CD  = df_P350_CD.reindex(new_idx)

df_P348_CD  = df_P348.groupby(by=[df_P348.index.hour]).mean()
df_P348_CD  = df_P348_CD.reindex(new_idx)

####################################################################################
## ----------------PROMEDIO MENSUAL DE LA POTENCIA DE LOS PANELES---------------- ##
####################################################################################

df_P975_PM  = df_P975.groupby(by=[df_P975.index.month]).mean()
df_P350_PM  = df_P350.groupby(by=[df_P350.index.month]).mean()
df_P348_PM  = df_P348.groupby(by=[df_P348.index.month]).mean()

################################################################################
## ----------------DIFERENCIAS DE LA POTENCIA DE LOS PANELES---------------- ##
################################################################################

dif_CD_P348_P350 = df_P348_CD['strength'].values - df_P350_CD['strength'].values

dif_CD_P348_P975 = df_P348_CD['strength'].values - df_P975_CD['strength'].values

dif_CD_P350_P975 = df_P350_CD['strength'].values - df_P975_CD['strength'].values

###############################################################
## ----------------TITULOS SCATTER Y PARASIT---------------- ##
###############################################################

title_Scatter = "Dispersion de los datos de potencia de cada panel en el tiempo"
title_Parasit = u"Eficiencia en la conversion de energía, radiación y punto de máximas potencias"

########################################################################################
## ----------------GRÁFICOS DE LA DISPERSION DE LOS DATOS DE POTENCIA---------------- ##
########################################################################################

fig = plt.figure(figsize=[10, 8])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(3, 1, 1)
ax1.scatter(df_P975.index, df_P975["strength"].values, s=80, c='#2980B9', label='P_Torre', alpha=0.5, marker = ".")
ax1.set_ylabel(u"W", fontsize=14, fontproperties=prop_1)
ax1.set_title(title_Scatter, fontsize=17,  fontweight = "bold",  fontproperties = prop)
ax1.set_ylim(0, np.nanmax(df_P975["strength"]) * 1.2)
ax1.set_xlim(df_P975.index[0], df_P975.index[-1])
ax1.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax1.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
ax1.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
ax1.tick_params(axis='x', which='minor')
ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
ax1.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
ax1.tick_params(axis='x', which='major', pad=15)
ax1.legend()

ax2 = fig.add_subplot(3, 1, 2)
ax2.scatter(df_P350.index, df_P350["strength"].values, s=80, c='#2980B9', label='P_Consejo', alpha=0.5, marker = ".")
ax2.set_ylabel(u"W", fontsize=14, fontproperties=prop_1)
ax2.set_ylim(0, np.nanmax(df_P975["strength"]) * 1.2)
ax2.set_xlim(df_P350.index[0], df_P350.index[-1])
ax2.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax2.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
ax2.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
ax2.tick_params(axis='x', which='minor')
ax2.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
ax2.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
ax2.tick_params(axis='x', which='major', pad=15)
ax2.legend()

ax3 = fig.add_subplot(3, 1, 3)
ax3.scatter(df_P348.index, df_P348["strength"].values, s=80, c='#2980B9', label='P_JoaquinV', alpha=0.5, marker = ".")
ax3.set_ylabel(u"W", fontsize=14, fontproperties=prop_1)
ax3.set_ylim(0, np.nanmax(df_P975["strength"]) * 1.2)
ax3.set_xlim(df_P348.index[0], df_P348.index[-1])
ax3.grid(which='major', linestyle=':', linewidth=0.5, alpha=0.7)
ax3.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
ax3.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
ax3.tick_params(axis='x', which='minor')
ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
ax3.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
ax3.tick_params(axis='x', which='major', pad=15)
ax3.legend()

plt.subplots_adjust( wspace=0.3, hspace=0.3)
plt.show()

##############################################################################
## ----------------GRÁFICOS DEL CICLO DIURNO DE LA POTENCIA---------------- ##
##############################################################################

x_pos = np.arange(len(df_P348_CD.index))

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.bar(x_pos, df_P975_CD['strength'], align='center', alpha=0.5)
ax1.set_ylim(0, 50)
ax1.set_xticks(np.arange(0, 12))
ax1.set_xticklabels(df_P975_CD.index.values)
ax1.set_ylabel(u'[W]', fontproperties=prop_1)
ax1.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax1.set_title('CD potencia en Torre SIATA',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.bar(x_pos, df_P350_CD['strength'], align='center', alpha=0.5)
ax2.set_ylim(0, 50)
ax2.set_xticks(np.arange(0, 12))
ax2.set_xticklabels(df_P975_CD.index.values)
ax2.set_ylabel(u'[W]', fontproperties=prop_1)
ax2.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax2.set_title(r'CD potencia en Consejo Itagüí',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.bar(x_pos, df_P348_CD['strength'], align='center', alpha=0.5)
ax3.set_ylim(0, 50)
ax3.set_xticks(np.arange(0, 12))
ax3.set_xticklabels(df_P975_CD.index.values)
ax3.set_ylabel(u'[W]', fontproperties=prop_1)
ax3.set_xlabel(u'Horas del dia', fontproperties=prop_1)
ax3.set_title(u'CD potencia en Joaquín V',   fontweight = "bold",  fontproperties = prop)

plt.subplots_adjust( wspace=0.3, hspace=0.3)


plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_Potencia.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CD_Potencia.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

###################################################################################
## ----------------GRÁFICOS DEL PROMEDIO MENSUAL DE LA POTENCIA---------------- ##
###################################################################################

x_pos = np.arange(len(df_P348_PM.index))

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.bar(x_pos, df_P975_PM['strength'], align='center', alpha=0.5)
ax1.set_ylim(0, 50)
ax1.set_xticks(np.arange(0, (len(df_P975_PM.index.values))))
ax1.set_xticklabels(df_P975_PM.index.values)
ax1.set_ylabel(u'[W]', fontproperties=prop_1)
ax1.set_xlabel(u'Mes de registro', fontproperties=prop_1)
ax1.set_title('PM potencia en Torre SIATA',   fontweight = "bold",  fontproperties = prop)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.bar(x_pos, df_P350_PM['strength'], align='center', alpha=0.5)
ax2.set_ylim(0, 50)
ax2.set_xticks(np.arange(0, (len(df_P975_PM.index.values))))
ax2.set_xticklabels(df_P975_PM.index.values)
ax2.set_ylabel(u'[W]', fontproperties=prop_1)
ax2.set_xlabel(u'Mes de registro', fontproperties=prop_1)
ax2.set_title(r'PM potencia en Consejo Itagüí',   fontweight = "bold",  fontproperties = prop)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.bar(x_pos, df_P348_PM['strength'], align='center', alpha=0.5)
ax3.set_ylim(0, 50)
ax3.set_xticks(np.arange(0, (len(df_P975_PM.index.values))))
ax3.set_xticklabels(df_P975_PM.index.values)
ax3.set_ylabel(u'[W]', fontproperties=prop_1)
ax3.set_xlabel(u'Mes de registro', fontproperties=prop_1)
ax3.set_title(u'PM potencia en Joaquín Vallejo',   fontweight = "bold",  fontproperties = prop)

plt.subplots_adjust( wspace=0.3, hspace=0.3)


plt.savefig('/home/nacorreasa/Escritorio/Figuras/PM_Potencia.png')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/PM_Potencia.png nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')



###########################################################################################################
#-----------------------------------GRAFICO DE LA POTENCIA 3 EN 1------------------------------------------#
###########################################################################################################

x_pos = np.arange(len(df_P348_CD.index))
x_pos1 = np.arange(0.75, len(df_P348_CD.index) + 0.75, 1)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax=fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.plot(df_P975_CD.index.values,df_P350_CD['strength'].values, color= '#70AFBA', label='CD_West',  lw = 1.2)
plt.plot(df_P975_CD.index.values,df_P975_CD['strength'].values, color='#004D56', label='CD_West Center',  lw = 1.2)
plt.plot(df_P975_CD.index.values,df_P348_CD['strength'].values, color='#C7D15D', label='CD_East',  lw = 1.2)
plt.fill_between(df_P975_CD.index.values, 0, df_P350_CD['strength'].values, color= '#70AFBA', alpha = 0.5)
plt.fill_between(df_P975_CD.index.values, 0, df_P975_CD['strength'].values, color= '#004D56', alpha = 0.5)
plt.fill_between(df_P975_CD.index.values, 0, df_P348_CD['strength'].values, color= '#C7D15D', alpha = 0.5)
plt.xticks(df_P348_CD.index, (df_P975_CD.index.values), fontsize=10, fontproperties=prop, rotation=20 )
plt.xlabel(u'Hours', fontsize = 18, fontproperties=prop_1)
plt.ylabel(u'[W/h]', fontproperties=prop_1, fontsize = 18)
plt.ylim(0, 100)
plt.title(u'Power CD at the three measurement points',   fontweight = "bold",  fontproperties = prop, fontsize = 20)
plt.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_Potencia_3en1.pdf', formar = 'pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CD_Potencia_3en1.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')







fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax=fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.bar(np.arange(len(df_P975_CD.index.values))+0.5, np.array(df_P350_CD['strength'].values), color= '#70AFBA', label='CD_West',  width = 0.25)
plt.bar(np.arange(len(df_P975_CD.index.values))+0.75, np.array(df_P975_CD['strength'].values), color='#004D56', label='CD_West Center',  width = 0.25)
plt.bar(np.arange(len(df_P975_CD.index.values))+1., np.array(df_P348_CD['strength'].values), color='#C7D15D', label='CD_East',  width = 0.25)
plt.xticks(x_pos1, (df_P975_CD.index.values), fontsize=10, fontproperties=prop, rotation=20 )
plt.xlabel(u'Hours', fontsize = 18, fontproperties=prop_1)
plt.ylabel(u'[W/h]', fontproperties=prop_1, fontsize = 18)
plt.title(u'Power CD at the three measurement points',   fontweight = "bold",  fontproperties = prop, fontsize = 20)
plt.legend()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/CD_Potencia_3en1.pdf', formar = 'pdf')
plt.close('all')
os.system('scp /home/nacorreasa/Escritorio/Figuras/CD_Potencia_3en1.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')

######################################################################################################################################
## ----------------GRÁFICOS DEL CICLO DIURNO DE LA EFICIENCIA ANTE CONDICIONES VARIANTES DE RADIACION Y TEMPERATURA---------------- ##
######################################################################################################################################

x_pos = np.arange(len(df_n_348_CD.index))
x_pos1 = np.arange(0.75, len(df_n_348_CD.index) + 0.75, 1)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
plt.bar(np.arange(len(df_n_348_CD.index.values))+0.5, np.array(df_n_975_CD['Desemp'].values), color= '#2ECC71', label='CD_TS',  width = 0.25)
plt.bar(np.arange(len(df_n_348_CD.index.values))+0.75, np.array(df_n_350_CD['Desemp'].values), color='#F7DC6F', label='CD_CI',  width = 0.25)
plt.bar(np.arange(len(df_n_348_CD.index.values))+1., np.array(df_n_348_CD['Desemp'].values), color='#F39C12', label='CD_JV',  width = 0.25)
plt.axhline(y = float(no), color = '#2471A3', linewidth = 3 )
plt.xticks(x_pos1, (df_n_348_CD.index.values), fontsize=10, fontproperties=prop, rotation=20 )
plt.xlabel(u'Horas del dia', fontproperties=prop_1)
plt.ylabel(u'$\eta$ [%]', fontproperties=prop_1)
plt.title(u'CD eficiencia de los paneles en los puntos de medición',   fontweight = "bold",  fontproperties = prop)
plt.legend()
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/Entrega_2/CD_Potencia_3en1.png')
plt.show()

## ----------------GRÁFICOS DE LAS DIFERENCIAS DEL CD  DE POTENCIA -------------------- ##

x_pos = np.arange(len(df_n_348_CD.index))
x_pos1 = np.arange(0.75, len(df_n_348_CD.index) + 0.75, 1)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
plt.bar(np.arange(len(df_n_348_CD.index.values))+0.5, dif_CD_P350_P975, color= '#2ECC71', label='CD_CI - CD_TS',  width = 0.25)
plt.bar(np.arange(len(df_n_348_CD.index.values))+0.75, dif_CD_P348_P975, color='#F7DC6F', label='CD_JV - CD_TS',  width = 0.25)
plt.bar(np.arange(len(df_n_348_CD.index.values))+1., dif_CD_P348_P350, color='#F39C12', label='CD_JV - CD_CI',  width = 0.25)
plt.xticks(x_pos1, (df_n_348_CD.index.values), fontsize=10, fontproperties=prop, rotation=20 )
plt.xlabel(u'Horas del dia', fontproperties=prop_1)
plt.ylabel(u'Diferencias', fontproperties=prop_1)
plt.title(u'Diferencias CD de las potencias en los puntos de medición',   fontweight = "bold",  fontproperties = prop)
plt.legend()
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/Entrega_2/Diferencias_CD_POT_3en1.png')
plt.show()

#######################################################################################################################################
## ----------------GRÁFICOS DE LAS DIFERENCIAS DE LA EFICIENCIA ANTE CONDICIONES VARIANTES DE RADIACION Y TEMPERATURA---------------- ##
#######################################################################################################################################

x_pos = np.arange(len(df_n_348_CD.index))
x_pos1 = np.arange(0.75, len(df_n_348_CD.index) + 0.75, 1)

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
plt.bar(np.arange(len(df_n_348_CD.index.values))+0.5, dif_n_CD_P350_P975, color= '#2ECC71', label='CD_CI - CD_TS',  width = 0.25)
plt.bar(np.arange(len(df_n_348_CD.index.values))+0.75, dif_n_CD_P348_P975, color='#F7DC6F', label='CD_JV - CD_TS',  width = 0.25)
plt.bar(np.arange(len(df_n_348_CD.index.values))+1., dif_n_CD_P348_P350, color='#F39C12', label='CD_JV - CD_CI',  width = 0.25)
plt.xticks(x_pos1, (df_n_348_CD.index.values), fontsize=10, fontproperties=prop, rotation=20 )
plt.xlabel(u'Horas del dia', fontproperties=prop_1)
plt.ylabel(u'Diferencias', fontproperties=prop_1)
plt.title(u'Diferencias CD de los desempeños de paneles en los puntos de medición',   fontweight = "bold",  fontproperties = prop)
plt.legend()
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/Entrega_2/Diferencias_CD_DESEMP_3en1.png')
plt.show()

########################################################################################################################################
## ----------------GRÁFICOS DE LAS DIFERENCIAS DE LA EFICIENCIA ANTE CONDICIONES VARIANTES DE RADIACION Y TEMPERATURA---------------- ##
########################################################################################################################################

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax = fig.add_subplot(111)
ax.plot(df_n_975_max_serie.index, df_n_975_max_serie['Desemp'].values, color= '#2ECC71', label='Desemp TS', linewidth = 3, linestyle='dashed')
ax.plot(df_n_350_max_serie.index, df_n_350_max_serie['Desemp'].values, color='#F7DC6F', label='Desemp CI', linewidth = 3)
ax.plot(df_n_348_max_serie.index, df_n_348_max_serie['Desemp'].values, color='#F39C12', label='Desemp JV', linewidth = 3, linestyle =  '-.')
ax.axhline(y = float(no), color = '#2471A3', linewidth = 3 )
plt.text(0, float(no),  'Efi_panel', ha='right', va='center')
# trans = transforms.blended_transform_factory(ax.get_yticklabels()[0].get_transform(), ax.transData)
# ax.text(0, float(no), "{:.0f}".format(float(no)), color="#2471A3", transform=trans,  ha="right", va="center")
hfmt = mdates.DateFormatter('%m-%d')
ax.xaxis.set_major_formatter(hfmt)
fig.autofmt_xdate()
plt.xlabel(u'Periodo de medición (días)', fontproperties=prop_1)
plt.ylabel(u'Eficiencias relativas [%]', fontproperties=prop_1)
plt.title(u'Eficiencias relativas de paneles en los puntos de medición',   fontweight = "bold",  fontproperties = prop)
plt.legend()
plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/Entrega_2/Plot_eficiancias_relativas_3en1.png')
plt.show()

## ----------------GRÁFICOS DE LA TEMPERATURA DEL MODULO---------------- ##

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
plt.plot(Tm_P975[0:36], color= '#2ECC71', label='Tm_TS', linewidth = 3)
plt.xlabel(u'Horas', fontproperties=prop_1)
plt.ylabel(u'Temperatura del módulo PV [°C]', fontproperties=prop_1)
plt.title(u'Primeras 36 horas de $Tm$ en TS',   fontweight = "bold",  fontproperties = prop)
plt.legend()
#plt.savefig('/home/nacorreasa/Maestria/Semestre2/Curso_Rad/Entrega_2/Plot_eficiancias_relativas_3en1.png')
plt.show()


## ----------------GRÁFICOS DE LA POTENCIA PICO, RADIACIÓN Y LA EFICIANCIA EN LA CONVERSION DE ENERGÍA DEL PANEL---------------- ##
jet = plt.get_cmap('jet')

##-->Torre SIATA
df_P975_max['Horas_Dec'] = np.array(df_P975_max.index.hour+df_P975_max.index.minute/60)

fig = plt.figure(figsize=(9, 7))
host = plt.subplot(111)
fig.subplots_adjust(right=0.75)

par1 = host.twinx()
par2 = host.twinx()
par2.spines["right"].set_position(("axes", 1.2))

p1, = host.plot(df_P975_max.index.date, df_P975_max['E_ConvE'].values, label='Eficiencia', color='#52C1BA')
p2, = par1.plot(df_P975_max.index.date, df_P975_max['radiacion'].values, color='orange', label=u'Radiación')
p3, = par2.plot(df_P975_max.index.date, df_P975_max['Max_Strength'].values, color='#202248', label=u'Potencia Max', alpha=0.5)

cs = par2.scatter(df_P975_max.index.date, df_P975_max['Max_Strength'].values, s=25, c=df_P975_max['Horas_Dec'],  cmap=jet)

host.set_ylim(0, np.nanmax(df_P975_max['E_ConvE'].values) * 1.10, 2)
par1.set_ylim(0, np.nanmax(df_P975_max['radiacion'].values) * 1.02)
par2.set_ylim(0, np.nanmax(df_P975_max['Max_Strength'].values) * 1.5)

host.set_xlabel("Tiempo", fontsize=8, fontproperties=prop)
host.set_ylabel(r"Eficiencia $\eta$")
par1.set_ylabel(r"$[W/m^{2}]$")
par2.set_ylabel(u"[W]")

for ax in [par1, par2]:
    ax.set_frame_on(True)
    ax.patch.set_visible(False)

    plt.setp(ax.spines.values(), visible=False)
    ax.spines["right"].set_visible(True)

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
par2.yaxis.label.set_color(p3.get_color())

par1.spines["right"].set_edgecolor(p2.get_color())
par2.spines["right"].set_edgecolor(p3.get_color())

host.tick_params(axis='y', colors=p1.get_color())
par1.tick_params(axis='y', colors=p2.get_color())
par2.tick_params(axis='y', colors=p3.get_color())

# host.set_xticks(np.arange(0, len(Nd), 12))
# host.set_xticklabels(Meses, size=11, rotation=45)
host.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b%d"))
host.set_title(title_Parasit + "\n-Torre SIATA", fontsize=10, fontweight="bold", fontproperties=prop)

cbar_ax = fig.add_axes([0.05, 0.04, 0.78, 0.008])
cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Horas de $Pmp$", fontsize=8, fontproperties=prop)

l, b, w, h = host.get_position().bounds
# ll, bb, ww, hh = cbar_ax.host.get_position().bounds
cbar_ax.ax.set_position([ll, b + 0.2*h, ww, h*0.8])

plt.subplots_adjust(left  = 0.10, right = 0.9 , bottom = 0.1 , top = 0.9 , hspace = 0.3  )
plt.tight_layout()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Parasit_Torre.png')
plt.draw()
plt.show()

##-->Consejo Itagüí

df_P350_max['Horas_Dec'] = np.array(df_P350_max.index.hour+df_P350_max.index.minute/60)

fig = plt.figure(figsize=(9, 7))
host = plt.subplot(111)
fig.subplots_adjust(right=0.75)

par1 = host.twinx()
par2 = host.twinx()
par2.spines["right"].set_position(("axes", 1.2))

p1, = host.plot(df_P350_max.index.date, df_P350_max['E_ConvE'].values, label='Eficiencia', color='#52C1BA')
p2, = par1.plot(df_P350_max.index.date, df_P350_max['radiacion'].values, color='orange', label=u'Radiación')
p3, = par2.plot(df_P350_max.index.date, df_P350_max['Max_Strength'].values, color='#202248', label=u'Potencia Max', alpha=0.5)

cs = par2.scatter(df_P350_max.index.date, df_P350_max['Max_Strength'].values, s=25, c=df_P350_max['Horas_Dec'],  cmap=jet)

host.set_ylim(0, np.nanmax(df_P350_max['E_ConvE'].values) * 1.10, 2)
par1.set_ylim(0, np.nanmax(df_P350_max['radiacion'].values) * 1.02)
par2.set_ylim(0, np.nanmax(df_P350_max['Max_Strength'].values) * 1.5)

host.set_xlabel("Tiempo", fontsize=8, fontproperties=prop)
host.set_ylabel(r"Eficiencia $\eta$")
par1.set_ylabel(r"$[W/m^{2}]$")
par2.set_ylabel(u"[W]")

for ax in [par1, par2]:
    ax.set_frame_on(True)
    ax.patch.set_visible(False)

    plt.setp(ax.spines.values(), visible=False)
    ax.spines["right"].set_visible(True)

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
par2.yaxis.label.set_color(p3.get_color())

par1.spines["right"].set_edgecolor(p2.get_color())
par2.spines["right"].set_edgecolor(p3.get_color())

host.tick_params(axis='y', colors=p1.get_color())
par1.tick_params(axis='y', colors=p2.get_color())
par2.tick_params(axis='y', colors=p3.get_color())

# host.set_xticks(np.arange(0, len(Nd), 12))
# host.set_xticklabels(Meses, size=11, rotation=45)
host.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b%d"))
host.set_title(title_Parasit + u"\n-Consejo Itagüí", fontsize=10, fontweight="bold", fontproperties=prop)

cbar_ax = fig.add_axes([0.05, 0.04, 0.78, 0.008])
cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Horas de $Pmp$", fontsize=8, fontproperties=prop)

l, b, w, h = host.get_position().bounds
#ll, bb, ww, hh = cbar_ax.host.get_position().bounds
cbar_ax.ax.set_position([ll, b + 0.2*h, ww, h*0.8])


plt.subplots_adjust(left  = 0.10, right = 0.9 , bottom = 0.1 , top = 0.9 , hspace = 0.3  )
plt.tight_layout()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Parasit_Consejo.png')
plt.draw()
plt.show()

##-->Joaquín Vallejo

df_P348_max['Horas_Dec'] = np.array(df_P348_max.index.hour+df_P348_max.index.minute/60)

fig = plt.figure(figsize=(9, 7))
host = plt.subplot(111)
fig.subplots_adjust(right=0.75)

par1 = host.twinx()
par2 = host.twinx()
par2.spines["right"].set_position(("axes", 1.2))

p1, = host.plot(df_P348_max.index.date, df_P348_max['E_ConvE'].values, label='Eficiencia', color='#52C1BA')
p2, = par1.plot(df_P348_max.index.date, df_P348_max['radiacion'].values, color='orange', label=u'Radiación')
p3, = par2.plot(df_P348_max.index.date, df_P348_max['Max_Strength'].values, color='#202248', label=u'Potencia Max', alpha=0.5)

cs = par2.scatter(df_P348_max.index.date, df_P348_max['Max_Strength'].values, s=25, c=df_P348_max['Horas_Dec'],  cmap=jet)

host.set_ylim(0, np.nanmax(df_P348_max['E_ConvE'].values) * 1.10, 2)
par1.set_ylim(0, np.nanmax(df_P348_max['radiacion'].values) * 1.02)
par2.set_ylim(0, np.nanmax(df_P348_max['Max_Strength'].values) * 1.5)

host.set_xlabel("Tiempo", fontsize=8, fontproperties=prop)
host.set_ylabel(r"Eficiencia $\eta$")
par1.set_ylabel(r"$[W/m^{2}]$")
par2.set_ylabel(u"[W]")

for ax in [par1, par2]:
    ax.set_frame_on(True)
    ax.patch.set_visible(False)

    plt.setp(ax.spines.values(), visible=False)
    ax.spines["right"].set_visible(True)

host.yaxis.label.set_color(p1.get_color())
par1.yaxis.label.set_color(p2.get_color())
par2.yaxis.label.set_color(p3.get_color())

par1.spines["right"].set_edgecolor(p2.get_color())
par2.spines["right"].set_edgecolor(p3.get_color())

host.tick_params(axis='y', colors=p1.get_color())
par1.tick_params(axis='y', colors=p2.get_color())
par2.tick_params(axis='y', colors=p3.get_color())

# host.set_xticks(np.arange(0, len(Nd), 12))
# host.set_xticklabels(Meses, size=11, rotation=45)
host.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b%d"))
host.set_title(title_Parasit + u"\n-Joaquín Vallejo", fontsize=10, fontweight="bold", fontproperties=prop)

cbar_ax = fig.add_axes([0.05, 0.04, 0.78, 0.008])
cbar = fig.colorbar(cs, cax=cbar_ax, orientation='horizontal', format="%.2f")
cbar.set_label(u"Horas de $Pmp$", fontsize=8, fontproperties=prop)

l, b, w, h = host.get_position().bounds
ll, bb, ww, hh = cbar_ax.host.get_position().bounds
cbar_ax.ax.set_position([ll, b + 0.2*h, ww, h*0.8])

plt.subplots_adjust(left  = 0.10, right = 0.9 , bottom = 0.1 , top = 0.9 , hspace = 0.3  )
plt.tight_layout()
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Parasit_Joaquin.png')
plt.draw()
plt.show()

## ----------------HISTOGRAMA DE LAS HORAS DE MÁXIMA POTENCIA---------------- ##

fig = plt.figure(figsize=[10, 6])
plt.rc('axes', edgecolor='gray')
ax1 = fig.add_subplot(1, 3, 1)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.hist(df_P348_max.index.hour, bins='auto', alpha = 0.5)
ax1.set_title(u'Distribución de las HSP en JV', fontproperties=prop, fontsize = 13)
ax1.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax1.set_xlabel(u'Horas Solares Pico', fontproperties=prop_1)

ax2 = fig.add_subplot(1, 3, 2)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.hist(df_P350_max.index.hour, bins='auto', alpha = 0.5)
ax2.set_title(u'Distribución de las HSP en CI', fontproperties=prop, fontsize = 13)
ax2.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax2.set_xlabel(u'Horas Solares Pico', fontproperties=prop_1)

ax3 = fig.add_subplot(1, 3, 3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.hist(df_P975_max.index.hour, bins='auto', alpha = 0.5)
ax3.set_title(u'Distribución de las HSP en TS', fontproperties=prop, fontsize = 13)
ax3.set_ylabel(u'Frecuencia', fontproperties=prop_1)
ax3.set_xlabel(u'Horas Solares Pico', fontproperties=prop_1)
plt.savefig('/home/nacorreasa/Escritorio/Figuras/Hist_HSP.png')
plt.show()

## ----------------GRÁFICOS DE DISPERSION DE LA POTENCIA DEL PANEL EN FUNCIÓN DE LA RAD Y LA TEMP---------------- ##

jet = plt.get_cmap('jet')
fig = plt.figure(figsize=[11, 10])

ax1 = fig.add_subplot(1, 3, 1)
sc1 = ax1.scatter(df_P975_h['radiacion'], df_P975_h['strength'], s=10, c=data_T_Torre_h['T'],  cmap=jet)
cbar1 = ax1.figure.colorbar(sc1)
cbar1.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar1.ax.tick_params(pad=-15, labelsize=6)
ax1.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax1.set_ylabel("Potencia $[W]$", fontsize=10, fontproperties=prop_1)
ax1.set_title("Torre SIATA" , fontsize=10)

ax2 = fig.add_subplot(1, 3, 2)
sc2 = ax2.scatter(df_P350_h['radiacion'], df_P350_h['strength'], s=10, c=data_T_Conse_h['T'],  cmap=jet)
cbar2 = plt.colorbar(sc2)
cbar2.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar2.ax.tick_params(pad=-15, labelsize=6)
ax2.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax2.set_ylabel("Potencia $[W]$", fontsize=10, fontproperties=prop_1)
ax2.set_title(u"Consejo Itagüí" , fontsize=10, fontproperties=prop_1)

ax3 = fig.add_subplot(1, 3, 3)
sc3 = ax3.scatter(df_P348_h['radiacion'], df_P348_h['strength'], s=10, c=data_T_Joaqu_h['T'],  cmap=jet)
cbar3 = plt.colorbar(sc3)
cbar3.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=6, fontproperties=prop_1, labelpad=15)
cbar3.ax.tick_params(pad=-15, labelsize=6)
ax3.set_xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
ax3.set_ylabel("Potencia $[W]$", fontsize=10, fontproperties=prop_1)
ax3.set_title(u"Joaquín Vallejo", fontsize=10, fontproperties=prop_1)

plt.subplots_adjust( wspace=0.3, hspace=1)
fig.suptitle(u"Relación de la potencia, radiación y temperatura", fontsize=15, fontweight = "bold",  fontproperties = prop)
plt.show()
