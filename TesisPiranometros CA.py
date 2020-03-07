# -*- coding: utf-8 -*-
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist as AA
import matplotlib.ticker as tck
import matplotlib.font_manager as fm

#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')


df1_a = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6001.txt', parse_dates=[2])
df1_a = df1_a.set_index(["fecha_hora"])
df1_a.index = df1_a.index.tz_localize('UTC').tz_convert('America/Bogota')
df1_a.index = df1_a.index.tz_localize(None)

df1_b = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60012018_2019.txt', parse_dates=[2])
df1_b = df1_b.set_index(["fecha_hora"])
df1_b.index = df1_b.index.tz_localize('UTC').tz_convert('America/Bogota')
df1_b.index = df1_b.index.tz_localize(None)

df1 = df1_a.append(df1_b)

df2_a = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/6002.txt', parse_dates=[2])
df2_a = df2_a.set_index(["fecha_hora"])
df2_a.index = df2_a.index.tz_localize('UTC').tz_convert('America/Bogota')
df2_a.index = df2_a.index.tz_localize(None)

df2_b = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Piranometro/60022018_2019.txt', parse_dates=[2])
df2_b = df2_b.set_index(["fecha_hora"])
df2_b.index = df2_b.index.tz_localize('UTC').tz_convert('America/Bogota')
df2_b.index = df2_b.index.tz_localize(None)

df2 = df2_a.append(df2_b)

# Estableciendo las fechas a consultar de los datos DESPEJADOS EN ESTE CASO:
fec_ini = datetime.datetime.strptime('2016-03-10 19:01:00', "%Y-%m-%d %H:%M:%S")
fec_fin = datetime.datetime.strptime('2019-12-19 18:58:00', "%Y-%m-%d %H:%M:%S")
new_idx = pd.date_range(fec_ini.date(), fec_fin.date() + pd.Timedelta('1 day'), freq='T')

df1 = df1.loc[~df1.index.duplicated(keep='first')]
df2 = df2.loc[~df2.index.duplicated(keep='first')]

# df1 = df1[fec_ini:fec_fin]
# df2 = df2[fec_ini:fec_fin]

df1 = df1.reindex(new_idx)
df2 = df2.reindex(new_idx)

df = pd.DataFrame()
df['rad_1'] = list(df1['radiacion'].values)
df['rad_2'] = list(df2['radiacion'].values)
df = df.set_index(new_idx)
df = df[(df['rad_1'] > 0)  & (df['rad_2'] > 0)]
df['avg'] = df[['rad_1', 'rad_2']].mean(axis=1)
df = df.drop(df.index[len(df)-1])

df.replace(to_replace =[df['avg']<0], value =0.0)

#df = df.between_time('06:00', '17:59')

#df_dia = df.groupby(by=[df.index.day]).sum()

df_CA = df.groupby(by=[df.index.month]).mean()
df_CA =df_CA/2

# Amanecer0 = datetime.datetime.strptime('2016-10-29 05:30:00', "%Y-%m-%d %H:%M:%S")
# Amanecer1 = datetime.datetime.strptime('2016-10-29 06:00:00', "%Y-%m-%d %H:%M:%S")
# Atardecer = datetime.datetime.strptime('2016-10-29 00:00:00', "%Y-%m-%d %H:%M:%S")

IDEAM = [4382.6, 4409.5, 4295.7, 4165.2, 4050.5, 4321.6, 4668.1, 4605.7, 4595.1, 4419, 3958.3, 4149.4]
IDEAM = np.array(IDEAM)/24


# Para la gráfica
Mes = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Agos', 'Sep', 'Oct', 'Nov', 'Dic']
title = u" Insolación  promedio en el Valle de Aburrá"

fig = plt.figure(figsize=[13, 6])
plt.rc('axes', axisbelow=True)
plt.grid(which='major',  linestyle='--', linewidth=0.5, color='lightgray')
plt.bar(np.arange(len(Mes))+0.25, np.array(df_CA['avg']), width = 0.3,  color='#FFA500')
plt.xlim(-1, len(Mes))
plt.xlabel(u'$Mes$', fontsize=8)
plt.ylabel(r"Radiacion promedio $[W/m^{2}]$", fontsize=10)
plt.title(title, fontsize=13, fontweight="bold")
plt.xticks(np.arange(0.25, len(df_CA.index.values)+0.5, 1), Mes, size = 10, rotation = 15)

w = 0.3

fig = plt.figure(edgecolor='w', facecolor='w', figsize=[9, 6])
plt.rc('axes', edgecolor='gray')
ax=fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
S = plt.bar(np.arange(len(Mes)), np.array(df_CA['avg']), width=w,  color='#4682B4')
I = plt.bar(np.arange(len(Mes)) - w, IDEAM, width=w,  color='#FFA500')
plt.xlim(-1, len(Mes)-0.5)
plt.xlabel(u'$Mes$',  fontproperties=prop_1, fontsize=11)
plt.ylabel(r"Insolación promedio por mes $[W/m^{2}/dia]$",  fontproperties=prop_1, fontsize=11)
plt.title(title,  fontproperties=prop, fontsize=13)
plt.xticks(np.arange(0, len(Mes), 1), Mes, size=9, rotation=20)
plt.legend((S[0], I[0]), ('SIATA 2016-2019', 'IDEAM 1985-1997'))
plt.grid(which='major',  linestyle='--', linewidth=0.5, color='lightgray')
plt.show()
