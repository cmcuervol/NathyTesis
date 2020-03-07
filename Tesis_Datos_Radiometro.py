#!/usr/bin/env python

import datetime as dt
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("template")
import matplotlib.font_manager as fm

## --------------------------------------------------------------------------------------- ##
## Consulta archivos con los datos de de radiometro que se alojan en home de Cuervo en Atlas ##
## --------------------------------------------------------------------------------------- ##

## RUTAS PARA CONSULTAR Y GUARDAR LOS PRODUCTOS ##

Path = '/home/cmcuervol/Desktop/radiometro/datos/'     ## de donde va a sacar los datos
ruta = '/home/nacorreasa/Maestria/Datos_Tesis/Radiometro/Radiometro_Panel/'                     ## donde se van a guardar los productos-Atlas
path_read = '/home/cmcuervol/Desktop/RWP/'             ## datos del radar de vientos

Path_fig = '/home/cmcuervol/Desktop/Salgar/Figuras/'   ## Atlas
Path_fuentes = '/home/cmcuervol/Fuentes/'              ## SAL

## SELECCION DE LAS FECHAS DE INTERES ##

# today = dt.datetime.now() + dt.timedelta(hours=5)
# start = today -dt.timedelta(hours=48)
start = dt.datetime(2019, 3, 20 , 0, 0)
# start = dt.datetime(2017, 10, 22 , 0, 0)
today = dt.datetime(2019, 12, 20, 23, 0)


## PARA LOS COLORES ##

# Colors for graphics SIATA style
gris70 = (112/255., 111/255., 111/255.)

ColorInfo1 = (82 /255., 183/255.,196/255.)
ColorInfo2 = (55 /255., 123/255.,148/255.)
ColorInfo3 = (43 /255.,  72/255.,105/255.)
ColorInfo4 = (32 /255.,  34/255., 72/255.)
ColorInfo5 = (34 /255.,  71/255., 94/255.)
ColorInfo6 = (31 /255., 115/255.,116/255.)
ColorInfo7 = (39 /255., 165/255.,132/255.)
ColorInfo8 = (139/255., 187/255.,116/255.)
ColorInfo9 = (200/255., 209/255., 93/255.)
ColorInfo10 =(249/255., 230/255., 57/255.)

# Types of fonts Avenir
AvenirHeavy = fm.FontProperties(fname=Path_fuentes+'AvenirLTStd-Heavy.otf')
AvenirBook  = fm.FontProperties(fname=Path_fuentes+'AvenirLTStd-Book.otf')
AvenirBlack = fm.FontProperties(fname=Path_fuentes+'AvenirLTStd-Black.otf')
AvenirRoman = fm.FontProperties(fname=Path_fuentes+'AvenirLTStd-Roman.ttf')


def listador(directorio, inicio, final):
    lf = []
    lista = os.listdir(directorio)
    for i in lista:
        if i.startswith(inicio) and i.endswith(final):
            lf.append(i)
    return lf

def listadorLV2(directorio, inicio):
    lf = []
    lista = os.listdir(directorio)
    for i in lista:
        if i.startswith(inicio) and i.endswith('lv2.csv'):
            lf.append(i)
    return lf


Inicio = start
Final = today


dias = []
day = start
i = 0
try:
    while day.date() <= today.date():
        dias.append(day)
        i += 1
        day = start + dt.timedelta(days=i)
except:
    while day.date() <= today:
        dias.append(day)
        i += 1
        day = start + dt.timedelta(days=i)

## LECTURA ##


lv2 =[0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80, 0.90,
1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00, 2.25, 2.50, 2.75, 3.00, 3.25,
3.50, 3.75, 4.00, 4.25, 4.50, 4.75, 5.00, 5.25, 5.50, 5.75, 6.00, 6.25, 6.50, 6.75, 7.00, 7.25,
7.50, 7.75, 8.00, 8.25, 8.50, 8.75, 9.00, 9.25, 9.50, 9.75, 10.00]


record = []
date   = []
GPS    = []
ground = []
cloud  = []
time   = []

Temperature_Zenit = []
Temperature_15N   = []
Temperature_15S   = []
Temperature_15A   = []

VaporDensity_Zenit = []
VaporDensity_15N   = []
VaporDensity_15S   = []
VaporDensity_15A   = []

Liquid_Zenit = []
Liquid_15N   = []
Liquid_15S   = []
Liquid_15A   = []

RelativeHumidity_Zenit = []
RelativeHumidity_15N   = []
RelativeHumidity_15S   = []
RelativeHumidity_15A   = []

#Tiempos
t_Temperature_Zenit = []
t_Temperature_15N   = []
t_Temperature_15S   = []
t_Temperature_15A   = []

t_VaporDensity_Zenit = []
t_VaporDensity_15N   = []
t_VaporDensity_15S   = []
t_VaporDensity_15A   = []

t_Liquid_Zenit = []
t_Liquid_15N   = []
t_Liquid_15S   = []
t_Liquid_15A   = []

t_RelativeHumidity_Zenit = []
t_RelativeHumidity_15N   = []
t_RelativeHumidity_15S   = []
t_RelativeHumidity_15A   = []


def Read_CSV(filename):

    f = open(filename, "r" )

    for line in f:
        #cortar caracteres
        c = line.split('\r\n')
        #separar en las primeras 3 entradas separadas por ','
        a = c[0].split(',', 3)

        record.append(a[0])
        date.append(a[1])

        if a[2] == '31':
            GPS.append(a[3].split(','))

            #organizar la fecha de cada trama de datos
            t = a [1]
            time.append(dt.datetime(2000+int(t[6:8]), int(t[0:2]), int(t[3:5]), int(t[9:11]), int(t[12:14]),
                                    int(t[15:17]))-dt.timedelta(hours=5))


        elif a[2] == '201':
            ground.append(a[3].split(','))

        elif a[2] == '301':
            cloud.append(a[3].split(',')[:-1])

        elif a[2] == '401':

            if a[3].startswith('Angle15KV(A)'):
                b = a[3].split(',', 1)
                try:
                    Temperature_15A.append(np.array(b[1].split(',')[:-1]).astype(float))
                except:
                    Temperature_15A.append([np.nan]*58)

                t = a [1]
                t_Temperature_15A.append(dt.datetime(2000+int(t[6:8]), int(t[0:2]), int(t[3:5]),
                      int(t[9:11]), int(t[12:14]))-dt.timedelta(hours=5))

        elif a[2] == '402':

            if a[3].startswith('Angle15KV(A)'):
                b = a[3].split(',', 1)
                try:
                    VaporDensity_15A.append(np.array(b[1].split(',')[:-1]).astype(float))
                except:
                    VaporDensity_15A.append([np.nan]*58)

                t = a [1]
                t_VaporDensity_15A.append(dt.datetime(2000+int(t[6:8]), int(t[0:2]), int(t[3:5]),
                      int(t[9:11]), int(t[12:14]))-dt.timedelta(hours=5))

        elif a[2] == '403':
            if a[3].startswith('Angle15KV(A)'):
                b = a[3].split(',', 1)
                try:
                    Liquid_15A.append(np.array(b[1].split(',')[:-1]).astype(float))
                except:
                    Liquid_15A.append([np.nan]*58)

                t = a [1]
                t_Liquid_15A.append(dt.datetime(2000+int(t[6:8]), int(t[0:2]), int(t[3:5]),
                      int(t[9:11]), int(t[12:14]))-dt.timedelta(hours=5))

        elif a[2] == '404':

            if a[3].startswith('Angle15KV(A)'):
                b = a[3].split(',', 1)
                try:
                    RelativeHumidity_15A.append(np.array(b[1].split(',')[:-1]).astype(float))
                except:
                    RelativeHumidity_15A.append([np.nan]*58)

                t = a [1]
                t_RelativeHumidity_15A.append(dt.datetime(2000+int(t[6:8]), int(t[0:2]), int(t[3:5]),
                      int(t[9:11]), int(t[12:14]))-dt.timedelta(hours=5))

    #borrar los tiempos de los headers de inicio y final
    del time[0]
    del time[-1]

def Read_bad():
    a=np.zeros(58)
    a[a==0]=np.nan

    time.append (day)

    Temperature_Zenit.append(a)
    Temperature_15N.append(a)
    Temperature_15S.append(a)
    Temperature_15A.append(a)

    VaporDensity_Zenit.append(a)
    VaporDensity_15N.append(a)
    VaporDensity_15S.append(a)
    VaporDensity_15A.append(a)

    Liquid_Zenit.append(a)
    Liquid_15N.append(a)
    Liquid_15S.append(a)
    Liquid_15A.append(a)

    RelativeHumidity_Zenit.append(a)
    RelativeHumidity_15N.append(a)
    RelativeHumidity_15S.append(a)
    RelativeHumidity_15A.append(a)

    #Tiempos
    t_Temperature_Zenit.append(day)
    t_Temperature_15N.append(day)
    t_Temperature_15S.append(day)
    t_Temperature_15A.append(day)

    t_VaporDensity_Zenit.append(day)
    t_VaporDensity_15N.append(day)
    t_VaporDensity_15S.append(day)
    t_VaporDensity_15A.append(day)

    t_Liquid_Zenit.append(day)
    t_Liquid_15N.append(day)
    t_Liquid_15S.append(day)
    t_Liquid_15A.append(day)

    t_RelativeHumidity_Zenit.append(day)
    t_RelativeHumidity_15N.append(day)
    t_RelativeHumidity_15S.append(day)
    t_RelativeHumidity_15A.append(day)



# ==========================================================================
#                       Lectura de todos los archivos
# ==========================================================================

missed = []
corruted = []

# Lectura recursiva si hay fechas sin archivos o con archivos malos

for day in dias:
    print ('******************************' + day.strftime('%Y-%m-%d') + '******************************')
    try:
        # existencia de archivos
        # os.system("scp "+RemoteHost+":"+RemotePath+day.strftime('%Y-%m-%d')+"*lv2.csv "+Path)
        # print "copy files done"
        lista = listadorLV2(Path, day.strftime('%Y-%m-%d'))
        print (lista)
        a = lista[0]
        lista = np.array(lista)
        lista.sort()
        for archivo in lista:
            try:
                # lectura de cada archivo
                Read_CSV(Path + archivo)
                print ('Readed ' + archivo)
            except:
                Read_bad()
                corruted.append(archivo)
                print ('file corruted', archivo)
        # os.system('rm '+Path+day.strftime('%Y-%m-%d')+"*lv2.csv ")
        #os.system('rm '+Path+file2)
        print ('lv2 file deleted')
    except:
        Read_bad()
        print ('Day without flies')
        missed.append(day)

print ('************************* lv2 files readed **************************')

print (missed)

print (corruted)



# Limpiar Variables

del Temperature_Zenit
del Temperature_15N
del Temperature_15S
# del Temperature_15A

del VaporDensity_Zenit
del VaporDensity_15N
del VaporDensity_15S
# del VaporDensity_15A

del Liquid_Zenit
del Liquid_15N
del Liquid_15S
# del Liquid_15A

del RelativeHumidity_Zenit
del RelativeHumidity_15N
del RelativeHumidity_15S
# del RelativeHumidity_15A

# Tiempos
del t_Temperature_Zenit
del t_Temperature_15N
del t_Temperature_15S
# del t_Temperature_15A

del t_VaporDensity_Zenit
del t_VaporDensity_15N
del t_VaporDensity_15S
# del t_VaporDensity_15A

del t_Liquid_Zenit
del t_Liquid_15N
del t_Liquid_15S
# del t_Liquid_15A

del t_RelativeHumidity_Zenit
del t_RelativeHumidity_15N
del t_RelativeHumidity_15S
# del t_RelativeHumidity_15A



print ("variables cleared")


# =============================================================================
# CONVERTIR LOS DATOS EN MATRICES

def Matriciador(X):
    M = np.zeros((len(X), 58), dtype=float)

    for i in range(len(X)):
        for j in range(58):
            try:
                M[i, j] = float(X[i][j])
            except:
                M[i, j] = np.nan
                print (i, t_VaporDensity_15A[i])

    return M

ground = np.array(ground, dtype=float)
cloud = np.array(cloud, dtype=float)


Temperature_15A = np.array(Temperature_15A, dtype=float)
print ('Temperature')


Liquid_15A = np.array(Liquid_15A, dtype=float)
print ('Liquid')


RelativeHumidity_15A = np.array(RelativeHumidity_15A, dtype=float)
print ('RelativeHumidity')


VaporDensity_15A = Matriciador(VaporDensity_15A)

print ('VaporDensity')

# Enmascarar datos malos
Temperature_15A = np.ma.masked_outside(Temperature_15A, 100, 350)
Temperature_15A = np.ma.array(Temperature_15A, mask=np.isnan(Temperature_15A))
Temperature_15A = np.ma.mask_rows(Temperature_15A)

RelativeHumidity_15A = np.ma.masked_outside(RelativeHumidity_15A, 0, 100)
RelativeHumidity_15A = np.ma.array(RelativeHumidity_15A, mask=np.isnan(RelativeHumidity_15A))
RelativeHumidity_15A = np.ma.mask_rows(RelativeHumidity_15A)

Liquid_15A = np.ma.masked_outside(Liquid_15A, 0, 10)
Liquid_15A = np.ma.array(Liquid_15A, mask=np.isnan(Liquid_15A))
Liquid_15A = np.ma.mask_rows(Liquid_15A)

print ('Masked')

T_A = pd.DataFrame(Temperature_15A, index=t_Temperature_15A, columns=lv2)
print ('Pandas Temperature')

V_A = pd.DataFrame(VaporDensity_15A, index=t_VaporDensity_15A, columns=lv2)
print ('Pandas Vapor')

L_A = pd.DataFrame(Liquid_15A, index=t_Liquid_15A, columns=lv2)
print ('Pandas Liquid')


H_A = pd.DataFrame(RelativeHumidity_15A, index=t_RelativeHumidity_15A, columns=lv2)
print ('Pandas Humedad')




# Recortar fechas humanas
T_A = T_A[(T_A.index>=Inicio)&(T_A.index<=Final)]
V_A = V_A[(V_A.index>=Inicio)&(V_A.index<=Final)]
L_A = L_A[(L_A.index>=Inicio)&(L_A.index<=Final)]
H_A = H_A[(H_A.index>=Inicio)&(H_A.index<=Final)]



# Guardar en txt
T_A.to_csv(ruta+'Temperature-'     +Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.txt', sep='\t')
V_A.to_csv(ruta+'VaporDensity-'    +Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.txt', sep='\t')
L_A.to_csv(ruta+'Liquid-'          +Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.txt', sep='\t')
H_A.to_csv(ruta+'RelativeHumidity-'+Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.txt', sep='\t')

T_A.to_csv(ruta+'Temperature-'     +Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.csv', sep=',')
V_A.to_csv(ruta+'VaporDensity-'    +Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.csv', sep=',')
L_A.to_csv(ruta+'Liquid-'          +Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.csv', sep=',')
H_A.to_csv(ruta+'RelativeHumidity-'+Inicio.strftime('%Y-%m-%d')+'_'+Final.strftime('%Y-%m-%d')+'.csv', sep=',')
