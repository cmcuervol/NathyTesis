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
Programa para obtener las cadenas de markov por etapa dentro del dia.
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
df_nub = df_975_nuba
trimestre = 'JJA'
etapa = 'tarde'

def weird_division(n, d):
    return n / d if d else 0

def Prob_Etapa(df_nub, etapa, Estado_ini, Name, trimestre ):
    """
    Calcula la probabilidad marginal y condicional de pasar de estados entre los periodos definidos
    INPUTS
    df_nub    : DataFrame with radiances and initial state
    etapa     : str indicando las etapas maniana, noon, tarde
    Estado_ini: list with DataFrames of every state
    Name      : Name to save the file with Prob_Marginal
    trimestre : str con los indicativos de cada trimestre JJA, SON, DEF, MAM

    OUTPUTS
    Prob_Marginal    : nxn array with the marginal probabily  of states transitions
    Prob_Condicional : nxn array with the conditional probabily of states transitions  based on the initial state
    """
    Path_save = '/home/nacorreasa/Maestria/Datos_Tesis/Arrays/'
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

    if etapa == 'maniana':
        df_nub = df_nub[(df_nub.index.hour == 6)|(df_nub.index.hour == 7)|(df_nub.index.hour == 8)|(df_nub.index.hour == 9)]
    elif etapa == 'noon':
        df_nub = df_nub[(df_nub.index.hour == 10)|(df_nub.index.hour == 11)|(df_nub.index.hour == 12)|(df_nub.index.hour == 13)|(df_nub.index.hour == 14)]
    elif etapa == 'tarde':
        df_nub = df_nub[(df_nub.index.hour == 15)|(df_nub.index.hour == 14)|(df_nub.index.hour == 13)|(df_nub.index.hour == 12)]

    Count = np.zeros((n,n), dtype=int)
    for i in range(1, len(df_nub.index)):
        for begin in range(n):
            for end in range(n):
                if df_nub.Estado_ini.values[i-1] == begin+1  and df_nub.Estado_ini.values[i] == end+1 :
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


    np.save(Path_save+Name+trimestre+etapa, Prob_Marginal)

    print('Guardando '+ Name+trimestre+etapa)
    return Prob_Marginal, Prob_Condicional


Prob_Marginal_morning_JJA,Prob_Condicional_morning_JJA = Prob_Etapa(df_975_nuba, 'maniana', Estado_ini, 'Array_Mark_Trans_Morning', 'JJA')
Prob_Marginal_noon_JJA   ,Prob_Condicional_noon_JJA    = Prob_Etapa(df_975_nuba, 'noon', Estado_ini, 'Array_Mark_Trans_Noon', 'JJA')
Prob_Marginal_tarde_JJA  ,Prob_Condicional_tarde_JJA   = Prob_Etapa(df_975_nuba, 'tarde', Estado_ini, 'Array_Mark_Trans_Tarde', 'JJA')

Prob_Marginal_morning_SON,Prob_Condicional_morning_SON = Prob_Etapa(df_975_nuba, 'maniana', Estado_ini, 'Array_Mark_Trans_Morning', 'SON')
Prob_Marginal_noon_SON   ,Prob_Condicional_noon_SON    = Prob_Etapa(df_975_nuba, 'noon', Estado_ini, 'Array_Mark_Trans_Noon', 'SON')
Prob_Marginal_tarde_SON  ,Prob_Condicional_tarde_SON   = Prob_Etapa(df_975_nuba, 'tarde', Estado_ini, 'Array_Mark_Trans_Tarde', 'SON')

Prob_Marginal_morning_DEF,Prob_Condicional_morning_DEF = Prob_Etapa(df_975_nuba, 'maniana', Estado_ini, 'Array_Mark_Trans_Morning', 'DEF')
Prob_Marginal_noon_DEF   ,Prob_Condicional_noon_DEF    = Prob_Etapa(df_975_nuba, 'noon', Estado_ini, 'Array_Mark_Trans_Noon', 'DEF')
Prob_Marginal_tarde_DEF  ,Prob_Condicional_tarde_DEF   = Prob_Etapa(df_975_nuba, 'tarde', Estado_ini, 'Array_Mark_Trans_Tarde', 'DEF')

Prob_Marginal_morning_MAM,Prob_Condicional_morning_MAM = Prob_Etapa(df_975_nuba, 'maniana', Estado_ini, 'Array_Mark_Trans_Morning', 'MAM')
Prob_Marginal_noon_MAM   ,Prob_Condicional_noon_MAM    = Prob_Etapa(df_975_nuba, 'noon', Estado_ini, 'Array_Mark_Trans_Noon', 'MAM')
Prob_Marginal_tarde_MAM  ,Prob_Condicional_tarde_MAM   = Prob_Etapa(df_975_nuba, 'tarde', Estado_ini, 'Array_Mark_Trans_Tarde', 'MAM')


##########NOMBRES###########
"""
Guardando Array_Mark_Trans_MorningJJAmaniana
Guardando Array_Mark_Trans_NoonJJAnoon
Guardando Array_Mark_Trans_TardeJJAtarde
Guardando Array_Mark_Trans_MorningSONmaniana
Guardando Array_Mark_Trans_NoonSONnoon
Guardando Array_Mark_Trans_TardeSONtarde
Guardando Array_Mark_Trans_MorningDEFmaniana
Guardando Array_Mark_Trans_NoonDEFnoon
Guardando Array_Mark_Trans_TardeDEFtarde
Guardando Array_Mark_Trans_MorningMAMmaniana
Guardando Array_Mark_Trans_NoonMAMnoon
Guardando Array_Mark_Trans_TardeMAMtarde
"""
############################

################################################################################
## -----------------------------------GRAFICA-------------------------------- ##
################################################################################

MAM_resha_morning_m = np.reshape(Prob_Marginal_morning_MAM, (-1, 5))
MAM_resha_noon_m    = np.reshape(Prob_Marginal_noon_MAM,    (-1, 5))
MAM_resha_tarde_m   = np.reshape(Prob_Marginal_tarde_MAM,   (-1, 5))

DEF_resha_morning_m = np.reshape(Prob_Marginal_morning_DEF, (-1, 5))
DEF_resha_noon_m    = np.reshape(Prob_Marginal_noon_DEF,    (-1, 5))
DEF_resha_tarde_m   = np.reshape(Prob_Marginal_tarde_DEF,   (-1, 5))

SON_resha_morning_m = np.reshape(Prob_Marginal_morning_SON, (-1, 5))
SON_resha_noon_m    = np.reshape(Prob_Marginal_noon_SON,    (-1, 5))
SON_resha_tarde_m   = np.reshape(Prob_Marginal_tarde_SON,   (-1, 5))

JJA_resha_morning_m = np.reshape(Prob_Marginal_morning_JJA, (-1, 5))
JJA_resha_noon_m    = np.reshape(Prob_Marginal_noon_JJA,    (-1, 5))
JJA_resha_tarde_m   = np.reshape(Prob_Marginal_tarde_JJA,   (-1, 5))

MAM_resha_morning_c = np.reshape(Prob_Condicional_morning_MAM, (-1, 5))
MAM_resha_noon_c    = np.reshape(Prob_Condicional_noon_MAM,    (-1, 5))
MAM_resha_tarde_c   = np.reshape(Prob_Condicional_tarde_MAM,   (-1, 5))

DEF_resha_morning_c = np.reshape(Prob_Condicional_morning_DEF, (-1, 5))
DEF_resha_noon_c    = np.reshape(Prob_Condicional_noon_DEF,    (-1, 5))
DEF_resha_tarde_c   = np.reshape(Prob_Condicional_tarde_DEF,   (-1, 5))

SON_resha_morning_c = np.reshape(Prob_Condicional_morning_SON, (-1, 5))
SON_resha_noon_c    = np.reshape(Prob_Condicional_noon_SON,    (-1, 5))
SON_resha_tarde_c   = np.reshape(Prob_Condicional_tarde_SON,   (-1, 5))

JJA_resha_morning_c = np.reshape(Prob_Condicional_morning_JJA, (-1, 5))
JJA_resha_noon_c    = np.reshape(Prob_Condicional_noon_JJA,    (-1, 5))
JJA_resha_tarde_c   = np.reshape(Prob_Condicional_tarde_JJA,   (-1, 5))



data_marg = np.array([DEF_resha_morning_m, MAM_resha_morning_m, JJA_resha_morning_m, SON_resha_morning_m, DEF_resha_noon_m, MAM_resha_noon_m, JJA_resha_noon_m, SON_resha_noon_m,  DEF_resha_tarde_m, MAM_resha_tarde_m, JJA_resha_tarde_m, SON_resha_tarde_m])
data_cond = np.array([DEF_resha_morning_c, MAM_resha_morning_c, JJA_resha_morning_c, SON_resha_morning_c, DEF_resha_noon_c, MAM_resha_noon_c, JJA_resha_noon_c, SON_resha_noon_c,  DEF_resha_tarde_c, MAM_resha_tarde_c, JJA_resha_tarde_c, SON_resha_tarde_c])

titles =[ u'DEF Mañana', u'MAM Mañana', u'JJA Mañana',u'SON Mañana', 'DEF Medio dia', 'MAM Medio dia', 'JJA Medio dia','SON Medio dia', 'DEF Tarde', 'MAM Tarde', 'JJA Tarde','SON Tarde']

cmap1 = plt.cm.viridis_r
cmap1.set_bad('white',1.)
plt.close('all')
fig = plt.figure(figsize=(17,13))
for i in range(0, 12):
    ax = fig.add_subplot(3, 4, i+1)
    cs = ax.imshow(data_marg[i], cmap =cmap1)
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

plt.savefig('/home/nacorreasa/Escritorio/Figuras/MarkovChain_Anual_marg.pdf', format='pdf', transparent=True)


cmap2 = plt.cm.viridis_r
cmap2.set_bad('white',1.)
plt.close('all')
fig = plt.figure(figsize=(17,13))
for i in range(0, 12):
    ax = fig.add_subplot(3, 4, i+1)
    cs = ax.imshow(data_cond[i], cmap =cmap2)
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

plt.savefig('/home/nacorreasa/Escritorio/Figuras/MarkovChain_Anual_cond.pdf', format='pdf', transparent=True)

os.system('scp /home/nacorreasa/Escritorio/Figuras/MarkovChain_Anual_*.pdf nacorreasa@192.168.1.74:/var/www/nacorreasa/Graficas_Resultados/Estudio')


#'YlGnBu'
