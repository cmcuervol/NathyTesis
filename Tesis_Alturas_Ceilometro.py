#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

#------------------------------------------------------------------------------
# Motivación codigo -----------------------------------------------------------
'Código para lacreación de dataframes con la minima altura de nubes a resolución horaria'
'a partir de la información de ceilómetro. De acuerdo a su horizonte temporal se debe '
'ajustar la reuta de consulta y de guardar archivos.'

####################################################################################
##--------------------FUNCION PARA CONSULTA DE ARCHIVOS---------------------------##
####################################################################################

def cloud_higth(Fecha_Inicio,Fecha_Fin, ceilometro):

        Fecha_Inicio = datetime.strftime(datetime.strptime(Fecha_Inicio, "%Y%m%d %H:%M") + timedelta(hours = 5),"%Y%m%d %H:%M")
        Fecha_Fin    = datetime.strftime(datetime.strptime(Fecha_Fin, "%Y%m%d %H:%M") + timedelta(hours = 5),"%Y%m%d %H:%M")

        File_List = pd.date_range(Fecha_Inicio[:8], Fecha_Fin[:8], freq='1D')
        Fechas   = []
        Cloud1   = []
        Cloud2   = []
        Cloud3   = []
        for idd, Fecha in enumerate(File_List):
                try:
                        year  = datetime.strftime(Fecha, '%Y')
                        month = datetime.strftime(Fecha, '%b')
                        day   = datetime.strftime(Fecha, '%d')

                        hisname  = '/mnt/ALMACENAMIENTO/ceilometro/datos/ceilometro'+str(ceilometro) \
                              +'/'+year+'/' + month+'/CEILOMETER_1_LEVEL_3_DEFAULT_' +day+'.his'
                        print (hisname)
                        Lista=np.genfromtxt(hisname,delimiter=', ',dtype=object,usecols=(0,-2,-4,-3),skip_header=1)

                        for j in range(1,len(Lista)):
                                Fechas.append(Lista[j][0])
                                Cloud1.append(np.float(Lista[j][1]))
                                Cloud2.append(np.float(Lista[j][2]))
                                Cloud3.append(np.float(Lista[j][3]))
                except:
                        pass
                fechas=pd.to_datetime(Fechas)- timedelta(hours=5)
                Data = pd.DataFrame(index=fechas)
                Data["Cloud1"]=Cloud1
                Data["Cloud2"]=Cloud2
                Data["Cloud3"]=Cloud3
        Data[Data<0]=np.nan
        Data1=Data.min(axis=1)
        #Data.index=pd.to_datetime(Data['0'])
        return Data1


####################################################################################
##--------------------------LECTURA DE LOS DATOS----------------------------------##
####################################################################################
"Los datos q se leen ya se entregan con la funcion de cloud_higth ya están a la hora local. Entrega la altura en Metros."

df_TS = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/siataCloudEne2018Dic2019.csv',  sep=',', index_col =0)
df_CI = pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/itaguiCloudEne2018Dic2019.csv',  sep=',', index_col =0)
df_AMVA= pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/amvaCloudEne2018Dic2019.csv',  sep=',', index_col =0)
df_FC= pd.read_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/federicocarrasquillaCloudEne2018Dic2019.csv',  sep=',', index_col =0)

df_TS.index = pd.to_datetime(df_TS.index)
df_TS = df_TS.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
df_TS_h = df_TS.groupby(pd.Grouper(freq="H")).mean()

df_CI.index = pd.to_datetime(df_CI.index)
df_CI = df_CI.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
df_CI_h = df_CI.groupby(pd.Grouper(freq="H")).mean()

df_AMVA.index = pd.to_datetime(df_AMVA.index)
df_AMVA = df_AMVA.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
df_AMVA_h = df_AMVA.groupby(pd.Grouper(freq="H")).mean()

df_FC.index = pd.to_datetime(df_FC.index)
df_FC = df_FC.between_time('06:00', '18:00')                      ##--> Seleccionar solo los datos de horas del dia
df_FC_h = df_FC.groupby(pd.Grouper(freq="H")).mean()

####################################################################################
##----------------------CONCATENACIÓN DEL DF ORIENTAL-----------------------------##
####################################################################################

frames = [df_AMVA, df_FC]
df_oriental = pd.concat(frames)

####################################################################################
##----------------------SELECCION DE LA NUBE MAS BAJA-----------------------------##
####################################################################################

df_oriental_min = pd.DataFrame( df_oriental.min(axis=1))
df_TS_min = pd.DataFrame( df_TS.min(axis=1))
df_CI_min =pd.DataFrame(  df_CI.min(axis=1))
df_AMVA_min = pd.DataFrame( df_AMVA.min(axis=1))
df_FC_min = pd.DataFrame( df_FC.min(axis=1))

####################################################################################
##----------------------HACIENDO UN PROMEDIO HORARIO------------------------------##
####################################################################################

df_oriental_min_h = df_oriental_min.groupby(pd.Grouper(freq="H")).mean()
df_TS_min_h = df_TS_min.groupby(pd.Grouper(freq="H")).mean()
df_CI_min_h = df_CI_min.groupby(pd.Grouper(freq="H")).mean()
df_AMVA_min_h = df_AMVA_min.groupby(pd.Grouper(freq="H")).mean()
df_FC_min_h = df_FC_min.groupby(pd.Grouper(freq="H")).mean()

####################################################################################
##--------------------------GUARDANDO LOS DATAFRAMES------------------------------##
####################################################################################

df_oriental_min_h.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudOrientalHora.csv')
df_TS_min_h.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudTSHora.csv')
df_CI_min_h.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudCIHora.csv')
df_AMVA_min_h.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudAMVAHora.csv')
df_FC_min_h.to_csv('/home/nacorreasa/Maestria/Datos_Tesis/Ceilometro/Ceilometro2018_2019/MinCloudFCHora.csv')
