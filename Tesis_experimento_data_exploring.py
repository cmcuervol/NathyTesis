# -*- coding: utf-8 -*-
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
from matplotlib import dates

plt.ioff()
##---INGRESAR LAS VARIABLES INICIALES ---##

fec_ini = '2018-10-12'
fec_fin = '2018-12-31'

#-----------------------------------------------------------------------------
fi = dt.datetime.strptime(fec_ini, '%Y-%m-%d')
ff = dt.datetime.strptime(fec_fin, '%Y-%m-%d')

#-----------------------------------------------------------------------------
# Rutas para acceder a las fuentes -------------------------------------------

prop   = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##---LECTURA DE LOS DATOS ---##
columnas_panel = ['fecha_hora', 'voltaje']
columnas_pira  = ['fecha_hora', 'radiacion']

df_pira    = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Datos_Rad_2018-10-11_2019-02-01.csv',  names=columnas_pira)
df_panel   = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Datos_Voltaje_2018-10-11_2019-02-01.csv', names=columnas_panel)
df_vaisala = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Datos_vaisala_201_2018-10-11_2019-01-20.csv')
df_thiess  = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Experimentos_Panel/Datos_thiess_1019_2018-10-11_2019-01-20.csv')

df_pira['fecha_hora'] = pd.to_datetime(df_pira['fecha_hora'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_panel['fecha_hora']  = pd.to_datetime(df_panel['fecha_hora'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_vaisala['fecha_hora'] = pd.to_datetime(df_vaisala['fecha_hora'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
df_thiess['fecha_hora']  = pd.to_datetime(df_thiess['fecha_hora'], format="%Y-%m-%d %H:%M:%S", errors='coerce')

df_pira = df_pira.set_index(["fecha_hora"])
df_panel  = df_panel.set_index(["fecha_hora"])
df_vaisala = df_vaisala.set_index(["fecha_hora"])
df_thiess  = df_thiess.set_index(["fecha_hora"])

##---RESAMPLEO DE LOS DATAFRAMES ---##

df_vaisala = df_vaisala.resample('1T').first()
df_thiess  = df_thiess.resample('1T').first()
df_panel   = df_panel.resample('1T').first()
df_pira    = df_pira.resample('1T').first()

##---OBTENIENDO UN SOLO DF CON LAS 3 VARIABLES ---##
df_result = pd.concat([df_panel, df_pira, df_vaisala], axis=1, sort=True)


##---FILTRANDO LA CALIDAD ---##
df_result = df_result[df_result['Calidad']<100]
df_result = df_result[df_result['radiacion']>0]
df_result = df_result[df_result['voltaje']>0]

##---FILTRANDO DATOS NOCTURNOS ---##
df_result = df_result.between_time('6:00', '18:00')


##---DIBUJO ---##

jet=plt.get_cmap('jet')
#fig = plt.figure(figsize=[14, 10])
plt.scatter(df_result['radiacion'], df_result['voltaje'], s=10, c=df_result['Temperatura'],  cmap=jet)
cbar = plt.colorbar()
cbar.ax.set_ylabel(u"Temperatura $[°C]$", rotation=270, fontsize=8, fontproperties=prop_1)
plt.xlabel(r"Intensidad de la radicion  $[W/m^{2}]$", fontsize=10, fontproperties=prop_1)
plt.ylabel("Voltaje $[V]$", fontsize=10, fontproperties=prop_1)
plt.title("Relacion entre las variables del experimento entre "+fec_ini+" y " + fec_fin, fontsize=11, fontweight = "bold",  fontproperties = prop)
plt.savefig('/home/nacorreasa/Escritorio/Bolitas.png')
plt.close()
