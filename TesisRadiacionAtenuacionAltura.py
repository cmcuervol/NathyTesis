#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.font_manager as fm
import math as m
import itertools
from matplotlib import dates
import itertools
import datetime

#-----------------------------------------------------------------------------
# Rutas para guardar ---------------------------------------------------------

prop = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

##----------------------------------------Método 1 radiación al tope de la atmosfera-----------------------------------------##
##---CALCULO DE LA DECLINACION SOLAR---##
J = np.arange(1, 366, 1)
g = 2*m.pi*(J-1)/365

d = (0.006918 - 0.399912*np.cos(g) + 0.070257*np.sin(g) - 0.006758*np.cos(2*g) + 0.000907*np.sin(2*g) - 0.002697*np.cos(3*g) + 0.00148*np.sin(3*g)+ 0.000907*np.sin(2*g) - 0.002697*np.cos(3*g) + 0.00148*np.sin(3*g))

dd = list(itertools.chain.from_iterable(itertools.repeat(x, 24) for x in d))


##---CALCULO DEL ANGULO HORARIO---##

def daterange(start_date, end_date):
    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta

    ##---Ecuación del tiempo---##

B = 2*m.pi*(J-81)/365
ET = 9.87*np.sin(2*B)-7.53*np.cos(B)-1.5*np.cos(B)

    ##---Tiempo solar---##

Ls = -75.                       #Meridiano estándar en grados decimales
# Ls = -75*m.pi/180.            #Meridiano estándar en radianes
Ll = -75.56359                  #Meridiano local en grados decimales
# Ll = -75.56359 *m.pi/180.     #Meridiano local en radianes
L = (Ls-Ll)/15
LT = []                          #Local standar time como datetime
start_date = datetime.datetime(2013, 1, 1, 00, 00)
end_date = datetime.datetime(2013, 1, 1, 23, 00)
for single_date in daterange(start_date, end_date):
    LT.append(single_date.time())

LT = np.arange(0, 24, 1)          #Local standar time como decimal

TS = []
for j in range(len(ET)):         #Variar en el tiempo solar de cada dia
    for i in range(len(LT)):     #Variar en las horas
        TS.append(LT[i]+(ET[j]/60)+L)


    ##---Angulo horario---##

w = []
for i in range(len(TS)):
    w.append(15*(12-TS[i]))       #En grados decimales

w = np.array(w)*m.pi/180          #Pasar a radianes

##---CALCULO DE LA RADIACION AL TOPE DE LA ATMOSFERA---##

    ##---Excentricidad---##

Eo = 1+(0.0033*np.cos((2*np.pi*J)/365))

d_h = list(itertools.chain.from_iterable(itertools.repeat(x, 24) for x in list(d))) # Declinacion a resolucion horaria

Eo_h = list(itertools.chain.from_iterable(itertools.repeat(x, 24) for x in Eo))      # Excentricidad a resolucion horaria

    ##---Radiacion al tope de la atmosfera---##

Cte = ((12*3.6)/m.pi)*1367
Lat = 6.217                        # En grados decimales
Io = []
for i in range(len(w)-1):
    Io.append(Cte*Eo_h[i]*(((m.sin(Lat*m.pi/180)*m.cos(d_h[i]))*(m.sin(w[i])-m.sin(w[i+1])))+(w[1]-w[2])*(m.sin(Lat*m.pi/180)*m.sin(d_h[i]))))  ##OJOesta iteracion produce un desfase de una hora

Io = np.array(Io)

Io[Io < 0] = np.nan

##----------------------------------------Método 2 radiación al tope de la atmosfera-----------------------------------------##

Lat = 6.217*m.pi/180.                             # Radianes

      ##---Distancia de la tierra al sol para cada día---##
dist = 1 - 0.01672*(np.cos(0.985*(J-4)))
dist = dist*10E10
distM = 1.5*10E11                                # Verificar unidades
So = 1367                                        # W/m2

# Ya la declinacion esta en radianes  d = d*np.pi/180

      ##---Ángulo horario por día (amanecer)---##
ho = np.arccos(-1*(np.tan(Lat)*np.tan(d)))      # En radianes
ho = ho*180/np.pi

      ##---Tiempo en horas de amanecida a partir del ángulo horario---##
to = 12 - ho/15                                  # En horas decimales
to_m = np.mean(to)

time_o = []
for i in range(len(to)):
    a = (str(datetime.timedelta(seconds = to[i]*3600))[0:7])
    time_o.append(datetime.datetime.strptime(a, '%H:%M:%S').time())

       ##---Ángulo horario por día (atardecer)---##

hf = -1*ho                                       # En grados

      ##---Tiempo en horas de atardecer a partir del ángulo horario---##
tf = 12 - hf/15                                  # En horas decimales
tf_m = np.mean(tf)

time_f = []
for i in range(len(tf)):
    a = (str(datetime.timedelta(seconds = tf[i]*3600))[0:7])
    time_f.append(datetime.datetime.strptime(a, '%H:%M:%S').time())

      ##---Insolación promedio por día al tope de la atmosfera---##

Qd = So/np.pi*((distM/dist)**2)*(ho*np.sin(Lat)*np.sin(d) + np.cos(Lat)*np.cos(d)*np.sin(ho))

      ##---Radiación al tope de la atmósfera horario---##
Io = []
#for i in range(len(d)):
#    for j in range(0, len(w), 24):
#        Io.append(So*Eo[i]*(np.sin(d[i])*np.sin(Lat) + np.cos(d[i])*np.cos(Lat)*np.cos(w[j:j+24])))

Io = []
for i in range(len(dd)):
    Io.append(So*Eo_h[i]*(np.sin(dd[i])*np.sin(Lat) + np.cos(dd[i])*np.cos(Lat)*np.cos(w[i])))

##--------------------------------------------------------------------------------------------------------------------##

##---CALCULO DE LA DURACIÓN DEL DÍA---##

Nd = 2./15.*ho                                    # En horas decimales

Nd_m = np.mean(Nd)

time_Nd = []
for i in range(len(Nd)):
    a = (str(datetime.timedelta(seconds = Nd[i]*3600))[0:7])
    time_Nd.append(datetime.datetime.strptime(a, '%H:%M:%S').time())

##---CALCULO DE LA ALTURA SOLAR ALPHA---##

Alpha = []
for i in range(len(d)):
    for j in range(0, len(w), 24):
        Alpha.append(np.arcsin(np.sin(Lat)*np.sin(d[i])+np.cos(Lat)*np.cos(d[i])*np.cos(w[j:j+24])))


##---CALCULO DE LA RADIACION INCIDENTE---##
df = pd.read_table('/home/nacorreasa/SIATA/Investigacion/Consultas6001.txt', parse_dates=[2])
df = df.set_index(["fecha_hora"])
df.index = df.index.tz_localize('UTC').tz_convert('America/Bogota')
df.index = df.index.tz_localize(None)


df_h = pd.DataFrame()
df_h['radiacion'] = df.radiacion.resample('H').mean()
df_h['temperatura'] = df.temperatura.resample('H').mean()

##----------------------------------------Acotando el df a la muestra deseada-----------------------------------------##
df_h = df_h.truncate(before='2016-03-10 00:00:00', after='2016-12-31 23:00:00')

new_idx = pd.date_range(df_h.index[0].date(), df_h.index[-1].date() + pd.Timedelta('1 day'), freq='H')
df_h = df_h.reindex(new_idx)
df_h = df_h.drop(df_h.index[len(df_h)-1])

Io = Io[(68*24)-1:]
##--------------------------------------------------------------------------------------------------------------------##

df_h['Io'] = Io

##---CALCULO DEL COEFICIENTE DE CLARIDAD---##

df_h['Mt'] = list(df_h['radiacion'].values/df_h['Io'].values)

##---ATENUACION ESPECTRAL CONTINUA---##

m = 2                                # Adimensional
l = np.arange(0.2, 2.2, 0.2)         # Micrometros

Trl = []
for i in range(len(l)):
    Trl.append(np.exp(-0.008735*(l[i]**-4.08))*2)

Tal = []
for i in range(len(l)):
    Tal.append(np.exp(-0.1*(l[i]**-1.3))*2)

Tcl = []
for i in range(len(l)):
    Tcl.append(Tal[i]+Trl[i])

##--------------------------------------------------------------------------------------------------------------------##

##---INDEX ANUAL---##

date1 = '2017-01-01'
date2 = '2017-12-31'
start = datetime.datetime.strptime(date1, '%Y-%m-%d')
end = datetime.datetime.strptime(date2, '%Y-%m-%d')
step = datetime.timedelta(days=1)
dates_index = []
while start <= end:
    print (start.date())
    dates_index.append(start.date())
    start += step

##--------------------------------------------------------------------------------------------------------------------##

##---GRAFICAS---##

##-ÁNGULO HORARIO-##
fig = plt.figure(edgecolor='gray', figsize=[10, 8], facecolor='w')
plt.rc('axes', axisbelow=True, edgecolor='gray')
ax = fig.add_subplot(111)
ax.plot(w[0:48], label = u'Grados decimales',   color='#52C1BA')
ax.set_xlabel(u'Horas del año', fontsize=16, fontweight="bold", fontproperties=prop_2, color = 'black')
ax.set_ylabel(u'Ánguo horario-Grados decimal', fontsize=17, fontweight="bold", fontproperties=prop_2, color = 'black')
ax.set_title(u'Ángulo horario para las primeras 48 horas del año', fontsize=20, fontweight="bold", fontproperties=prop, color = 'black')
plt.show()


##-Metodo1 DURACION DEL DIA-##

fig = plt.figure(edgecolor='gray', figsize=[18, 13], facecolor='w')
plt.rc('axes', axisbelow=True, edgecolor='gray')
ax = fig.add_subplot(111)
ax.plot(dates_index, Nd, label = u'Duracion del día',   color='#52C1BA')
ax.plot(dates_index, tf, label = 'Hora de atardecer', color='#ffa040')
ax.plot(dates_index, to, label = 'Hora de amanecer', color='#0b6623')
ax.set_xlabel(u'Meses', fontsize=16, fontweight="bold", fontproperties=prop_2, color = 'black')
ax.set_ylabel('Hora decimal', fontsize=17, fontweight="bold", fontproperties=prop_2, color = 'black')
ax.set_title(u'Horas de amanecer, atardecer y duración del día para Medellín', fontsize=20, fontweight="bold", fontproperties=prop, color = 'black')
ax.set_ylim(np.min(to)-1, np.max(tf)*1.1)
ax.set_xlim(dates_index[0], dates_index[-1])
# ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%d:%m"))
# ax.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
#ax.tick_params(axis='x', which='minor')
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b"))
ax.xaxis.set_major_locator(tck.MaxNLocator(nbins=12))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
ax.tick_params(axis='x', which='major', pad=1)
ax.grid(which='major',  linestyle='--', linewidth=0.5, color='lightgray')
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.13), fancybox=True, ncol=3, prop={'size': 13})
plt.tick_params(color='black', labelcolor='black')
plt.tight_layout()
plt.show()

##-Metodo2 DURACION DEL DIA-##

Meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May','Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

# # GRAFICA

fig, host = plt.subplots()
fig.subplots_adjust(right=0.75)
par1 = host.twinx()
par2 = host.twinx()
# Move the spine of the second axes outwards
par2.spines["right"].set_position(("axes", 1.2))

p1, = host.plot(np.arange(0, len(dates_index),1),  Nd, label = u'Duración del día',   color='#52C1BA')
p2, = par1.plot(np.arange(0, len(dates_index),1),  tf, label = 'Hora de atardecer', color='#ffa040')
p3, = par2.plot(np.arange(0, len(dates_index),1),  to, label = 'Hora de amanecer', color='#0b6623')


host.set_ylim(np.nanmin(Nd)*0.90, np.nanmax(Nd)*1.1)
par1.set_ylim(np.nanmin(tf)*0.90, np.nanmax(tf)*1.1)
par2.set_ylim(np.nanmin(to)*0.90, np.nanmax(to)*1.1)


host.set_xlabel(u'Meses', fontsize=16, fontweight="bold", fontproperties=prop_2)
host.set_ylabel(u'Duración del día $[h]$', fontweight="bold", fontproperties=prop_2)
par1.set_ylabel('Hora de atardecer', fontweight="bold", fontproperties=prop_2)
par2.set_ylabel('Hora de amanecer', fontweight="bold", fontproperties=prop_2)


lines = [p1, p2, p3]
host.legend(lines, [l.get_label() for l in lines])

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

host.set_xticks(np.arange(15, len(dates_index)+15, 30.5))
host.set_xticklabels(Meses, size=9, rotation=0)
host.set_title(u'Horas de amanecer, atardecer y duración del día para Medellín',  fontweight="bold", fontproperties=prop, color = 'black')

plt.draw()
plt.show()

































def grafica_triple_anual(index, lista1, lista2, lista3, title, ylabel, xlabel, ylimsup, yliminf, label1, label2, label3):
    fig = plt.figure(edgecolor='gray', figsize=[18, 13], facecolor='w')
    plt.rc('axes', axisbelow=True, edgecolor='gray')
    ax = fig.add_subplot(111)
    ax.plot(index, lista1, label=label1, color='#52C1BA')
    ax.plot(index, lista2, label=label2, color='#ffa040')
    ax.plot(index, lista3, label=label3, color='#0b6623')
    ax.set_xlabel(xlabel, fontsize=16, fontweight="bold", fontproperties=prop_2, color='black')
    ax.set_ylabel(ylabel, fontsize=17, fontweight="bold", fontproperties=prop_2, color='black')
    ax.set_title(title, fontsize=20, fontweight="bold",
                 fontproperties=prop, color='black')
    ax.set_ylim(yliminf, ylimsup * 1.1)
    ax.set_xlim(index[0], index[-1])
    ax.tick_params(axis='x', which='major')
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b"))
    ax.xaxis.set_major_locator(tck.MaxNLocator(nbins=12))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    ax.tick_params(axis='x', which='major', pad=1)
    ax.grid(which='major', linestyle='--', linewidth=0.5, color='lightgray')
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.13), fancybox=True, ncol=3, prop={'size': 13})
    plt.tick_params(color='black', labelcolor='black')
    plt.show()


def grafica_radiacion(index, lista, title, ylabel, xlabel, ylimsup, yliminf):
    fig = plt.figure(edgecolor='gray', figsize=[10, 8], facecolor='w')
    plt.rc('axes', axisbelow=True, edgecolor='gray')
    ax = fig.add_subplot(111)
    ax.plot(index, lista,  color='#52C1BA')
    ax.set_xlabel(xlabel, fontsize=14, fontweight="bold", fontproperties=prop_2, color = 'gray')
    ax.set_ylabel(ylabel, fontsize=14, fontweight="bold", fontproperties=prop_2, color = 'gray')
    ax.set_title(title, fontsize=18, fontweight="bold", fontproperties=prop, color = 'gray')
    ax.set_ylim(yliminf, ylimsup*1.1)
    ax.legend()
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
    ax.tick_params(axis='x', which='minor')
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
    ax.tick_params(axis='x', which='major', pad=15)
    ax.grid(which='major',  linestyle='--', linewidth=0.5, color='lightgray')
    plt.tick_params(color='gray', labelcolor='gray')
    plt.show()
    plt.rc('axes', axisbelow=True, edgecolor='gray')
    ax = fig.add_subplot(111)
    ax.plot(index, lista,  color='#52C1BA')
    ax.set_xlabel(xlabel, fontsize=14, fontweight="bold", fontproperties=prop_2, color = 'gray')
    ax.set_ylabel(ylabel, fontsize=14, fontweight="bold", fontproperties=prop_2, color = 'gray')
    ax.set_title(title, fontsize=18, fontweight="bold", fontproperties=prop, color = 'gray')
    ax.set_ylim(yliminf*1.1, ylimsup*1.1)
    ax.legend()
    ax.tick_params(axis='x', which='minor')
    ax.tick_params(axis='x', which='major', pad=15)
    ax.grid(which='major',  linestyle='--', linewidth=0.5, color='lightgray')
    plt.tick_params(color='gray', labelcolor='gray')
    plt.show()

def grafica_radiacion_doble(index1, lista1, index2, lista2, title, ylabel, xlabel, ylimsup, yliminf):
    fig = plt.figure(edgecolor='gray', figsize=[10, 8], facecolor='w')
    plt.rc('axes', axisbelow=True, edgecolor='gray')
    ax = fig.add_subplot(111)
    ax.plot(index1, lista1,  color='#52C1BA', label = 'Extraterrestre')
    ax.plot(index2, lista2, color='#ffa040', label = 'Global')
    ax.set_xlabel(xlabel, fontsize=14, fontweight="bold", fontproperties=prop_2, color = 'gray')
    ax.set_ylabel(ylabel, fontsize=14, fontweight="bold", fontproperties=prop_2, color = 'gray')
    ax.set_title(title, fontsize=18, fontweight="bold", fontproperties=prop, color = 'gray')
    ax.set_ylim(yliminf, ylimsup*1.1)
    ax.legend()
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_locator(tck.MaxNLocator(nbins=5))
    ax.tick_params(axis='x', which='minor')
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(tck.MaxNLocator(nbins=5))
    ax.tick_params(axis='x', which='major', pad=15)
    ax.grid(which='major',  linestyle='--', linewidth=0.5, color='lightgray')
    plt.tick_params(color='gray', labelcolor='gray')
    plt.show()

grafica_radiacion(df_h.index[0:24], list(df_h['Io'][0:24].values), "Intensidad de la radiacion por unidad de area",
                  r"Intensidad de la radicion $[W/m^{2}]$", "Tiempo", np.nanmax(df_h['Io'][0:24]), np.nanmin(df_h['Io'][0:24]))

grafica_radiacion(J, d, u"Declinación terrestre por dia del año",
                  u"Declinación $[rad]$","Dia juliano", 0.6, -0.6)

grafica_radiacion(J, ET, u"Ecuación del tiempo",
                  u"Minutos","Dia juliano",  18, -18)

grafica_radiacion_doble(df_h.index[0:24], list(df_h['Io'][0:24].values),df_h.index[0:24], list(df_h['radiacion'][0:24].values), "Intensidad de la radiacion  por unidad de area",
                  r"Intensidad de la radicion  $[W/m^{2}]$", "Tiempo", np.nanmax(df_h['radiacion'][0:24]), np.nanmin(df_h['radiacion'][0:24]))
