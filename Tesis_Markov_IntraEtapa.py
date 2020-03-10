#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import datetime
import os

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
"""
Programa para obtener las cadenas de markov intra etapa dentro del dia.
"""
#-----------------------------------------------------------------------------
# Rutas para las fuentes -----------------------------------------------------

prop   = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Heavy.otf' )
prop_1 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Book.otf')
prop_2 = fm.FontProperties(fname='/home/nacorreasa/SIATA/Cod_Califi/AvenirLTStd-Black.otf')

####################################################################################
## -----------LECTURA DE LOS DATOS DE GOES CH2 PARA EL PIXEL DE INTERES---------- ##
####################################################################################
Rad_pixel_975 = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_Rad_pix975_Anio.npy')
fechas_horas = np.load('/home/nacorreasa/Maestria/Datos_Tesis/Arrays/Array_FechasHoras_Anio.npy')
fechas_horas = pd.to_datetime(fechas_horas, format="%Y-%m-%d %H:%M", errors='coerce')


                   ## -- Selección del pixel de la TS
Rad_df_975 = pd.DataFrame()
Rad_df_975['Fecha_Hora'] = fechas_horas
Rad_df_975['Radiacias'] = Rad_pixel_975
Rad_df_975.index = Rad_df_975['Fecha_Hora']
Rad_df_975 = Rad_df_975.drop(['Fecha_Hora'], axis=1)

"""
Se hace sobre los datos filtrados de nubosidad para el pixel
"""

Umbral_up_975   = pd.read_table('/home/nacorreasa/Maestria/Datos_Tesis/Umbrales_Horarios/Umbral_Hourly_975_Nuba.csv',  sep=',',  header = None)
Umbral_up_975.columns=['Hora', 'Umbral']
Umbral_up_975.index = Umbral_up_975['Hora']
Umbral_up_975 = Umbral_up_975.drop(['Hora'], axis=1)


Rad_nuba_975 = []
FH_Nuba_975 = []
for i in range(len(Rad_df_975)):
    for j in range(len(Umbral_up_975.index)):
        if (Rad_df_975.index[i].hour == Umbral_up_975.index[j]) & (Rad_df_975.Radiacias.values[i] >= Umbral_up_975.values[j][0]):
            Rad_nuba_975.append(Rad_df_975.Radiacias.values[i])
            FH_Nuba_975.append(Rad_df_975.index[i])
            print(Rad_df_975.Radiacias.values[i])
        elif (Rad_df_975.index[i].hour == Umbral_up_975.index[j]) & (Rad_df_975.Radiacias.values[i] < Umbral_up_975.values[j][0]):
            #Rad_nuba_975.append(np.nan)
            Rad_nuba_975.append(0.)
            FH_Nuba_975.append(Rad_df_975.index[i])
            print('nan')


df_975_nuba = pd.DataFrame()
df_975_nuba['Radiacias'] = Rad_nuba_975
df_975_nuba['Fecha_Hora'] = FH_Nuba_975
df_975_nuba['Fecha_Hora'] = pd.to_datetime(df_975_nuba['Fecha_Hora'], format="%Y-%m-%d %H:%M", errors='coerce')
df_975_nuba.index = df_975_nuba['Fecha_Hora']
df_975_nuba = df_975_nuba.drop(['Fecha_Hora'], axis=1)

#df_975_nuba = df_975_nuba[df_975_nuba.Radiacias>0]

####################################################################################
## ---------------DEFICINICIÓN DE ESTADOS CON LA FDP DE LOS ESTADOS-------------- ##
####################################################################################
Histograma, Bins = np.histogram(df_975_nuba['Radiacias'][np.isfinite(df_975_nuba['Radiacias'])] , bins=[0, Umbral_up_975.Umbral.values.min(), 40, 60, 80, 100 ], density = False)
####################################################################################
## -----------------------GENERACION DE LA LISTA DE ESTADOS---------------------- ##
####################################################################################

Estado_ini = [df_975_nuba [(df_975_nuba.Radiacias.values >= round(Bins[i],2)) & (df_975_nuba.Radiacias.values <=round(Bins[i+1],2))] for i in range(5)]

df_975_nuba['Estado_ini'] = np.zeros(len(df_975_nuba))

for i in range(len(df_975_nuba.index)):
    for e in range(1,6):
        if df_975_nuba.index[i] in Estado_ini[e-1].index:
            print(e)
            df_975_nuba['Estado_ini'].iloc[i] = e

####################################################################################
## --------------GENRACION DE LA CADENA DE MARKOV DE TARDE-MANIANA-------------- ##
####################################################################################

# # Para los ensayos de la función considere:
# df_nub = df_975_nuba
# horas_emp = 17
# horas_sig = 6

def weird_division(n, d):
    return n / d if d else 0

def Prob_Transicion(df_nub, horas_emp, horas_sig , Estado_ini, Name, trimestre ):
    """
    Calcula la probabilidad marginal y condicional de pasar de estados entre los periodos definidos
    INPUTS
    df_nub    : DataFrame with radiances and initial state
    horas_emp : least limit hour of the initial period (int)
    horas_sig : first limit hour of the end period (int)
    Estado_ini: list with DataFrames of every state
    Name      : Name to save the file with Prob_Marginal
    trimestre : strcon los indicativos de cada trimestre JJA, SON, DEF, MAM

    OUTPUTS
    Prob_Marginal    : nxn array with the marginal probabily  of states transitions
    Prob_Condicional : nxn array with the conditional probabily of states transitions  based on the initial state
    """
    Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
    delta = datetime.timedelta(hours = 9)
    n = len(Estado_ini)

    if trimestre == 'JJA':
        mes = [6, 7, 8]
    elif trimestre == 'SON':
        mes = [9, 10, 11]
    elif trimestre == 'DEF':
        mes = [12, 1, 2]
    elif trimestre == 'MAM':
        mes = [3, 4, 5]

    df_nub = df_nub[(df_nub.index.month  == mes[0])|(df_nub.index.month  == mes[1])|(df_nub.index.month  == mes[2])]

    df_emp = df_nub[df_nub.index.hour == horas_emp]
    df_sig = df_nub[df_nub.index.hour == horas_sig]
    df_emp = df_emp.groupby(df_emp.index.map(lambda t: datetime.datetime(t.year, t.month, t.day, t.hour))).last()
    df_sig = df_sig.groupby(df_sig .index.map(lambda t: datetime.datetime(t.year, t.month, t.day, t.hour))).first()

    s=0
    Count = np.zeros((n,n), dtype=int)
    for i in range(1, len(df_emp.index)):
        if (df_emp.index[i-1]+delta).date()  in df_sig.index.date:
            df_fecha_emp = df_emp[df_emp.index.date == (df_emp.index[i-1]).date()]
            df_fecha_sig = df_sig[df_sig.index.date == (df_emp.index[i-1]+delta).date()]
            for begin in range(n):
                for end in range(n):
                    if df_fecha_emp.Estado_ini.values[-1] == begin+1  and df_fecha_sig.Estado_ini.values[0] == end+1 :
                        s = s+1
                        Count[begin, end] = Count[begin, end]+1
                        # Count[begin, end] +=1

    total_Estado_ini = Count.sum(axis=1)
    total_Estado_fin = Count.sum(axis=0)

    Total_General = total_Estado_ini.sum()

    Prob_Condicional = np.zeros((n,n), dtype=float)
    for i in range(len(total_Estado_fin)):
        Prob_Condicional[i,:] = weird_division(Count[i,:],total_Estado_ini[i]) * 100


    Array_total = np.repeat(Total_General, n)
    Prob_Marginal = np.zeros((n,n), dtype=float)
    for i in range(len(Array_total)):
        Prob_Marginal[i,:] = Count[i,:]/Array_total[i] * 100


    np.save(Path_save+Name+trimestre, Prob_Marginal)

    print('Guardando '+ Name+trimestre)
    return Prob_Marginal, Prob_Condicional


Prob_Marginal_tarde_morning_JJA, Prob_Condicional_tarde_morning_JJA = Prob_Transicion(df_975_nuba, 17,  6, Estado_ini, 'Array_Mark_Trans_TardeMorning', 'JJA')
Prob_Marginal_morning_noon_JJA , Prob_Condicional_morning_noon_JJA  = Prob_Transicion(df_975_nuba, 9,  10, Estado_ini, 'Array_Mark_Trans_MorningNoon',  'JJA')
Prob_Marginal_noon_tarde_JJA   , Prob_Condicional_noon_tarde_JJA    = Prob_Transicion(df_975_nuba, 14, 15, Estado_ini, 'Array_Mark_Trans_NoonTarde',    'JJA')

Prob_Marginal_tarde_morning_SON, Prob_Condicional_tarde_morning_SON = Prob_Transicion(df_975_nuba, 17,  6, Estado_ini, 'Array_Mark_Trans_TardeMorning', 'SON')
Prob_Marginal_morning_noon_SON , Prob_Condicional_morning_noon_SON  = Prob_Transicion(df_975_nuba, 9,  10, Estado_ini, 'Array_Mark_Trans_MorningNoon',  'SON')
Prob_Marginal_noon_tarde_SON   , Prob_Condicional_noon_tarde_SON    = Prob_Transicion(df_975_nuba, 14, 15, Estado_ini, 'Array_Mark_Trans_NoonTarde',    'SON')

Prob_Marginal_tarde_morning_DEF, Prob_Condicional_tarde_morning_DEF = Prob_Transicion(df_975_nuba, 17,  6, Estado_ini, 'Array_Mark_Trans_TardeMorning', 'DEF')
Prob_Marginal_morning_noon_DEF , Prob_Condicional_morning_noon_DEF  = Prob_Transicion(df_975_nuba, 9,  10, Estado_ini, 'Array_Mark_Trans_MorningNoon',  'DEF')
Prob_Marginal_noon_tarde_DEF   , Prob_Condicional_noon_tarde_DEF    = Prob_Transicion(df_975_nuba, 14, 15, Estado_ini, 'Array_Mark_Trans_NoonTarde',    'DEF')

Prob_Marginal_tarde_morning_MAM, Prob_Condicional_tarde_morning_MAM = Prob_Transicion(df_975_nuba, 17,  6, Estado_ini, 'Array_Mark_Trans_TardeMorning', 'MAM')
Prob_Marginal_morning_noon_MAM , Prob_Condicional_morning_noon_MAM  = Prob_Transicion(df_975_nuba, 9,  10, Estado_ini, 'Array_Mark_Trans_MorningNoon',  'MAM')
Prob_Marginal_noon_tarde_MAM   , Prob_Condicional_noon_tarde_MAM    = Prob_Transicion(df_975_nuba, 14, 15, Estado_ini, 'Array_Mark_Trans_NoonTarde',    'MAM')


##########NOMBRES###########
"""
Guardando Array_Mark_Trans_TardeMorningJJA
Guardando Array_Mark_Trans_MorningNoonJJA
Guardando Array_Mark_Trans_NoonTardeJJA
Guardando Array_Mark_Trans_TardeMorningSON
Guardando Array_Mark_Trans_MorningNoonSON
Guardando Array_Mark_Trans_NoonTardeSON
Guardando Array_Mark_Trans_TardeMorningDEF
Guardando Array_Mark_Trans_MorningNoonDEF
Guardando Array_Mark_Trans_NoonTardeDEF
Guardando Array_Mark_Trans_TardeMorningMAM
Guardando Array_Mark_Trans_MorningNoonMAM
Guardando Array_Mark_Trans_NoonTardeMAM
"""
############################

################################################################################
## -----------------------------------GRAFICA-------------------------------- ##
################################################################################

MAM_resha_tarde_morning_m = np.reshape(Prob_Marginal_tarde_morning_MAM, (-1, 5))
MAM_resha_morning_noon_m  = np.reshape(Prob_Marginal_morning_noon_MAM,  (-1, 5))
MAM_resha_noon_tarde_m    = np.reshape(Prob_Marginal_noon_tarde_MAM,    (-1, 5))

DEF_resha_tarde_morning_m = np.reshape(Prob_Marginal_tarde_morning_DEF, (-1, 5))
DEF_resha_morning_noon_m  = np.reshape(Prob_Marginal_morning_noon_DEF,  (-1, 5))
DEF_resha_noon_tarde_m    = np.reshape(Prob_Marginal_noon_tarde_DEF,    (-1, 5))

JJA_resha_tarde_morning_m = np.reshape(Prob_Marginal_tarde_morning_JJA, (-1, 5))
JJA_resha_morning_noon_m  = np.reshape(Prob_Marginal_morning_noon_JJA,  (-1, 5))
JJA_resha_noon_tarde_m    = np.reshape(Prob_Marginal_noon_tarde_JJA,    (-1, 5))

SON_resha_tarde_morning_m = np.reshape(Prob_Marginal_tarde_morning_SON, (-1, 5))
SON_resha_morning_noon_m  = np.reshape(Prob_Marginal_morning_noon_SON,  (-1, 5))
SON_resha_noon_tarde_m    = np.reshape(Prob_Marginal_noon_tarde_SON,    (-1, 5))


MAM_resha_tarde_morning_c = np.reshape(Prob_Condicional_tarde_morning_MAM, (-1, 5))
MAM_resha_morning_noon_c  = np.reshape(Prob_Condicional_morning_noon_MAM,  (-1, 5))
MAM_resha_noon_tarde_c    = np.reshape(Prob_Condicional_noon_tarde_MAM,    (-1, 5))

DEF_resha_tarde_morning_c = np.reshape(Prob_Condicional_tarde_morning_DEF, (-1, 5))
DEF_resha_morning_noon_c  = np.reshape(Prob_Condicional_morning_noon_DEF,  (-1, 5))
DEF_resha_noon_tarde_c    = np.reshape(Prob_Condicional_noon_tarde_DEF,    (-1, 5))

JJA_resha_tarde_morning_c = np.reshape(Prob_Condicional_tarde_morning_JJA, (-1, 5))
JJA_resha_morning_noon_c  = np.reshape(Prob_Condicional_morning_noon_JJA,  (-1, 5))
JJA_resha_noon_tarde_c    = np.reshape(Prob_Condicional_noon_tarde_JJA,    (-1, 5))

SON_resha_tarde_morning_c = np.reshape(Prob_Condicional_tarde_morning_SON, (-1, 5))
SON_resha_morning_noon_c  = np.reshape(Prob_Condicional_morning_noon_SON,  (-1, 5))
SON_resha_noon_tarde_c    = np.reshape(Prob_Condicional_noon_tarde_SON,    (-1, 5))


data_marg = np.array([DEF_resha_tarde_morning_m, MAM_resha_tarde_morning_m, JJA_resha_tarde_morning_m, SON_resha_tarde_morning_m, DEF_resha_morning_noon_m, MAM_resha_morning_noon_m, JJA_resha_morning_noon_m, SON_resha_morning_noon_m,  DEF_resha_noon_tarde_m, MAM_resha_noon_tarde_m, JJA_resha_noon_tarde_m, SON_resha_noon_tarde_m])
data_cond = np.array([DEF_resha_tarde_morning_c, MAM_resha_tarde_morning_c, JJA_resha_tarde_morning_c, SON_resha_tarde_morning_c, DEF_resha_morning_noon_c, MAM_resha_morning_noon_c, JJA_resha_morning_noon_c, SON_resha_morning_noon_c,  DEF_resha_noon_tarde_c, MAM_resha_noon_tarde_c, JJA_resha_noon_tarde_c, SON_resha_noon_tarde_c])

titles =[ u'DEF Tarde a Mañana', u'MAM Tarde a Mañana', u'JJA Tarde a Mañana',u'SON Tarde a Mañana', 'DEF Mañana a Medio dia', 'MAM Mañana a Medio dia', 'JJA Mañana a Medio dia','SON Mañana a Medio dia', 'DEF Medio dia a Tarde', 'MAM Medio dia a Tarde', 'JJA Medio dia a Tarde','SON Medio dia a Tarde']

cmap1 = plt.cm.viridis_r
cmap1.set_bad('white',1.)
plt.close('all')
fig = plt.figure(figsize=(17,13))
for i in range(0, 12):
    ax = fig.add_subplot(3, 4, i+1)
    cs = ax.imshow(data_marg[i], cmap=cmap1)
    ax.set_ylabel('Estado Inicial', fontproperties = prop_1, fontsize =14)
    ax.set_xlabel('Estado Final', fontproperties = prop_1, fontsize =14)
    ax.set_title(titles[i], fontproperties = prop, fontsize =15)
    data_marg[i][data_marg[i]==0]=None
    for k in range(0,5):
        for j in range(0,5):
            text = ax.text(j, k, round(data_marg[i][k, j], 2),  ha="center", va="center", color="w")
    ax.set_xticklabels(np.array(['0','1', '2', '3', '4', '5']))
    ax.set_yticklabels(np.array(['0', '1', '2', '3', '4', '5']))

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.01)
cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
cbar.set_label(u'Probabilidad [%]',  fontproperties = prop, fontsize=20 )

plt.savefig('/home/nacorreasa/Escritorio/Figuras/MarkovChain_InterEtapa_marg.pdf', format='pdf', transparent=True)


cmap2 = plt.cm.viridis_r
cmap2.set_bad('white',1.)
plt.close('all')
fig = plt.figure(figsize=(17,13))
for i in range(0, 12):
    ax = fig.add_subplot(3, 4, i+1)
    cs = ax.imshow(data_cond[i], cmap=cmap2)
    ax.set_ylabel('Estado Inicial', fontproperties = prop_1, fontsize =14)
    ax.set_xlabel('Estado Final', fontproperties = prop_1, fontsize =14)
    ax.set_title(titles[i], fontproperties = prop, fontsize =15)
    data_cond[i][data_cond[i]==0]=None
    for k in range(0,5):
        for j in range(0,5):
            text = ax.text(j, k, round(data_cond[i][k, j], 2),  ha="center", va="center", color="w")
    ax.set_xticklabels(np.array(['0','1', '2', '3', '4', '5']))
    ax.set_yticklabels(np.array(['0', '1', '2', '3', '4', '5']))

plt.subplots_adjust(left=0.125, bottom=0.085, right=0.9, top=0.95, wspace=0.35, hspace=0.01)
cbar_ax = fig.add_axes([0.125, 0.05, 0.78, 0.015])
cbar = fig.colorbar(cs, cax=cbar_ax,  orientation='horizontal', format="%.2f")
cbar.set_label(u'Probabilidad [%]',  fontproperties = prop, fontsize=20 )

plt.savefig('/home/nacorreasa/Escritorio/Figuras/MarkovChain_InterEtapa_cond.pdf', format='pdf', transparent=True)

os.system('scp /home/nacorreasa/Escritorio/Figuras/MarkovChain_InterEtapa*.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')












# def Prob(df_nub, horas_emp, horas_sig , Estado_ini, Name ):
#     """
#     Calcula la probabilidad de pasar de estados entre los periodos definidos
#     INPUTS
#     df_nub    : DataFrame with radiances and initial state
#     horas_emp : list of hours of the initial period
#     horas_sig : list of hours of the end period
#     Estado_ini: list with DataFrames of every state
#     Name      : Name to save the file
#     """
#     Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
#     n = len(Estado_ini)
#     Count = np.zeros((n,n), dtype=int)
#     for i in range(1, len(df_nub.index)):
#         if (df_nub.index[i-1].hour in  horas_emp) & (df_nub.index[i].hour in  horas_sig):
#             print(df_nub.index[i-1])
#             for begin in range(n):
#                 for end in range(n):
#                     if df_nub.Estado_ini.values[i-1] == begin+1  and df_nub.Estado_ini.values[i] == end+1 :
#                         Count[begin, end] +=1
#
#     n_Estado_ini = [len(Estado_ini[i]) for i in range(n)]
#     n_Estado_ini = np.array(n_Estado_ini).astype(float)
#     Prob = np.zeros((n,n), dtype=float)
#     for i in range(len(n_Estado_ini)):
#         Prob[i,:] = Count[i, :]/n_Estado_ini[i] * 100
#
#
#     np.save(Path_save+Name, Prob)
#
#     print('Guardando '+ Name)
#
# Prob(df_975_nuba,horas_tarde,   horas_maniana, Estado_ini, 'Array_Markov_TardeMorning')
# Prob(df_975_nuba,horas_maniana, horas_noon,    Estado_ini, 'Array_Markov_MorningNoon')
# Prob(df_975_nuba,horas_noon,    horas_tarde,   Estado_ini, 'Array_Markov_NoonTarde')
# De acá en adelante son lineas perdidas
