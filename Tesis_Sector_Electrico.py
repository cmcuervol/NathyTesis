# -*- coding: utf-8 -*-
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
from matplotlib import dates


#-----------------------------------------------------------------------------
# Rutas para guardar ---------------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##---CALCULO DEL CRECIMEINTO DE LA CAPACIDAD INSTALDAA EN EL TIEMPO---##
df = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/PARATEC/CapacidadEfectivaGeneracionFuenteTipo20181017.csv')

for i in range(len(df['Fecha_entrada'].values)):
    df['Fecha_entrada'].loc[i] = str(df['Fecha_entrada'].loc[i])


df['Fecha_entrada'] = pd.to_datetime(df['Fecha_entrada'], format="%d/%m/%Y")
df.index = df['Fecha_entrada']
df.sort_index(inplace=True)
df['Capacidad_Efectiva'] = pd.to_numeric(df['Capacidad_Efectiva'], errors='coerce')

      ##---Distinguiendo los dataframes por fuente---##

df_Agua = df[df['Fuente'] == u'Agua']
df_Acpm = df[df['Fuente'] == u'Acpm']
df_Carbon = df[df['Fuente'] == u'Carbon']
df_Combustoleo = df[df['Fuente'] == u'Combustoleo']
df_Gas = df[df['Fuente'] == u'Gas']
df_JetA2 = df[df['Fuente'] == u'Jet-A2']
df_Mezcla = df[df['Fuente'] == u'Mezcla Gas - Jet-A2']
df_Biogas = df[df['Fuente'] == u'Biogas']
df_Bagazo = df[df['Fuente'] == u'Bagazo']
df_RadSolar = df[df['Fuente'] == u'Rad Solar']
df_Viento = df[df['Fuente'] == u'Viento']

      ##---Acumulando valores---##

Acum_df = df.groupby(pd.Grouper(freq="Y")).sum()
Acum_Agua = df_Agua.groupby(pd.Grouper(freq="Y")).sum()
Acum_Acpm = df_Acpm.groupby(pd.Grouper(freq="Y")).sum()
Acum_Carbon = df_Carbon.groupby(pd.Grouper(freq="Y")).sum()
Acum_Combustoleo = df_Combustoleo.groupby(pd.Grouper(freq="Y")).sum()
Acum_Gas = df_Gas.groupby(pd.Grouper(freq="Y")).sum()
Acum_JetA2 = df_JetA2.groupby(pd.Grouper(freq="Y")).sum()
Acum_Mezcla = df_Mezcla.groupby(pd.Grouper(freq="Y")).sum()
Acum_Biogas = df_Biogas.groupby(pd.Grouper(freq="Y")).sum()
Acum_Bagazo = df_Bagazo.groupby(pd.Grouper(freq="Y")).sum()
Acum_RadSolar = df_RadSolar.groupby(pd.Grouper(freq="Y")).sum()
Acum_Viento = df_Viento.groupby(pd.Grouper(freq="Y")).sum()

      ##---Ajustando los dataframes---##
Acum_Agua[u'Capacidad_Efectiva'] = Acum_Agua[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Acpm[u'Capacidad_Efectiva'] = Acum_Acpm[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Carbon[u'Capacidad_Efectiva'] = Acum_Carbon[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Combustoleo[u'Capacidad_Efectiva'] = Acum_Combustoleo[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Gas[u'Capacidad_Efectiva'] = Acum_Gas[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_JetA2[u'Capacidad_Efectiva'] = Acum_JetA2[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Mezcla[u'Capacidad_Efectiva'] = Acum_Mezcla[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Biogas[u'Capacidad_Efectiva'] = Acum_Biogas[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Bagazo[u'Capacidad_Efectiva'] = Acum_Bagazo[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_RadSolar[u'Capacidad_Efectiva'] = Acum_RadSolar[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})
Acum_Viento[u'Capacidad_Efectiva'] = Acum_Viento[u'Capacidad_Efectiva'].replace({0.0:np.nan, 0:np.nan})


new_idx = pd.date_range(df.index[0].date(), df.index[-1].date() + pd.Timedelta('365 days'), freq='Y')

Acum_Agua = Acum_Agua.reindex(new_idx)
Acum_Acpm = Acum_Acpm.reindex(new_idx)
Acum_Carbon = Acum_Carbon.reindex(new_idx)
Acum_Combustoleo = Acum_Combustoleo.reindex(new_idx)
Acum_Gas = Acum_Gas.reindex(new_idx)
Acum_JetA2 = Acum_JetA2.reindex(new_idx)
Acum_Mezcla = Acum_Mezcla.reindex(new_idx)
Acum_Biogas = Acum_Biogas.reindex(new_idx)
Acum_Bagazo = Acum_Bagazo.reindex(new_idx)
Acum_RadSolar = Acum_RadSolar.reindex(new_idx)
Acum_Viento = Acum_Viento.reindex(new_idx)

      ##---El total por fuente---##

df_fuente_total = df.groupby(['Fuente']).sum()


      ##---Gráfica serie de tiempo---##

fig = plt.figure(figsize=[10, 7])
ax = fig.add_subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.scatter(Acum_df.index, Acum_Agua['Capacidad_Efectiva'], color = '#4363d8', label='Agua', s = 30, marker = ".")
ax.scatter(Acum_df.index, Acum_Carbon['Capacidad_Efectiva'], color = '#3cb44b', label=u'Carbón', s = 30, marker = "v")
ax.scatter(Acum_df.index, Acum_Gas['Capacidad_Efectiva'], color = '#bfef45', label='Gas', s = 30, marker = "x")
ax.scatter(Acum_df.index, Acum_Bagazo['Capacidad_Efectiva'], color = '#9A6324', label='Bagazo', s = 30,  marker = "D")
ax.scatter(Acum_df.index, Acum_Acpm['Capacidad_Efectiva'], color = '#000000', label='Acpm', s = 30,  marker = "X")
ax.scatter(Acum_df.index, Acum_Biogas['Capacidad_Efectiva'], color = '#aaffc3', label='Biogas', s = 30,  marker = "o")
ax.scatter(Acum_df.index, Acum_Combustoleo['Capacidad_Efectiva'], color = '#f032e6', label='Combustoleo', s = 30,  marker = "s")
ax.scatter(Acum_df.index, Acum_JetA2['Capacidad_Efectiva'], color = '#a9a9a9', label='Jet-A2', s = 30,  marker = "$JA$")
ax.scatter(Acum_df.index, Acum_Mezcla['Capacidad_Efectiva'], color = '#fabebe', label='Mezcla', s = 30,  marker = "p")
ax.scatter(Acum_df.index, Acum_Viento['Capacidad_Efectiva'], color = '#42d4f4', label='Viento', s = 30,  marker = "1")
ax.scatter(Acum_df.index, Acum_RadSolar['Capacidad_Efectiva'], color = '#e6194B', label='Rad Solar', s = 30,  marker = "*")
plt.yscale('log')
ax.set_xlabel("Tiempo", fontproperties=prop, fontsize=14)
ax.set_ylabel("Capacidad Instalada $[MW]$", fontproperties=prop, fontsize=15)
ax.set_xlim(Acum_df.index[0].date() - pd.Timedelta('500 days'), Acum_df.index[-1].date() + pd.Timedelta('500 days'))
ax.legend(loc=2)
#ax.set_title(u'Histórico de la generación de energía electrica por fuente', fontsize=20, fontproperties=prop_2)
#ax.grid(which='major', linestyle='--', linewidth=0.5, color='lightgray')
plt.savefig('/home/nacorreasa/Maestria/Tesis/Introduccion/HistoricoCapacidadFuente.pdf', transparent=True)
plt.show()

      ##---Gráfica torta---##

plt.figure(1, figsize=(10, 10))
labels = 'Agua', 'Acpm', 'Bagazo',  'Biogas', 'Carbon', 'Combustoleo', 'Gas', 'Jet-A2', 'Mezcla', 'Viento', 'Rad Solar'
sizes = [11809.97, 766.00, 143.10, 5.55, 1653.30, 184.00, 2303.29, 44.00, 264.00, 18.42, 9.80]
colors = ['#4363d8', '#98D1DD', '#9A6324', '#aaffc3',  '#3cb44b', '#6f9f9c', '#bfef45', '#a9a9a9', '#fabebe', '#42d4f4', '#e6194B'  ]
explode = (0.1, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0)
total = str(int(np.sum(sizes)))

x = np.char.array(labels)
y = np.array(sizes)
porcent = 100.*y/y.sum()

patches, texts = plt.pie(y, colors=colors, startangle=90)
label = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(x, porcent)]

sort_legend = True
if sort_legend:
    patches, label, dummy =  zip(*sorted(zip(patches, label, y),
                                          key=lambda x: x[2],
                                          reverse=True))

#plt.legend(patches, label, bbox_to_anchor=(0.85, 0.1), ncol = 4, fontsize=9)
plt.legend(patches, label, bbox_to_anchor=(0.90,0.88), loc="upper left",ncol = 1, fontsize=14 )
plt.title(u'Distribución histórica de generación de energía por fuente', size = 23, fontweight = "bold",  fontproperties = prop, fontsize=15)
plt.text(1, 1, r'Total $[MW]$: '+ total,  fontweight = "bold", fontproperties = prop , fontsize = 20)
plt.savefig('/home/nacorreasa/Maestria/Tesis/Introduccion/CapacidadFuente.pdf', transparent=True)
plt.show()
