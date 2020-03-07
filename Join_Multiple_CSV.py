# -*- coding: utf-8 -*-
import os

"Programa para la unin de los archivos mensuales del modelo de radiación de GIS o de las Fisheye, la carpeta donde se va a guardar el archivo"
"completo, debe ser diferente a la carpeta donde están los archivos porque de lo contrario sacaria error."

## PONER LA PALABRA CLAVE DE LOS ARCHIVOS DE TEXTO ##
Key_Word = '.csv'

## LA RUTA DONDE SE VA A GUARDAR EL ARCHIVO COMPLETO ##
#fout = open("/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_Totales/Total_Timeseries_Rad_2018.csv", "a")
fout = open("/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/Totales/Total_Timeseries_FishEye_AMVA.csv", "a")
#fout = open("/home/nacorreasa/Maestria/Datos_Tesis/PM_2con5/Total_Timeseries_PM80.csv", "a")

## LA RUTA DEL PRIMERO DE LOS ARCHIVOS PARA ESCRIBIR EL ENCABEZADO ##
# for line in open("/home/nacorreasa/Maestria/Datos_Tesis/PM_2con5/80/estacion_data_calidadaire_80_20190301_20190331.csv"):
#     fout.write(line)
# for line in open("/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/AMVA_Dia/1_serie_dia_2018-03-06.csv"):
#     fout.write(line)
for line in open("/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_2018_nuevos/2018-01-15_Timeseries_sup_horizontal.csv"):
    fout.write(line)

## LA RUTA DONDE ESTÁN LOS ARCHIVOS DE TEXTO A UNIR ##
#Folder = '/home/nacorreasa/Maestria/Datos_Tesis/PM_2con5/80/'
#Folder = '/home/nacorreasa/Maestria/Datos_Tesis/Fish_Eye/AMVA_Dia/'
Folder = '/home/nacorreasa/Maestria/Datos_Tesis/Radiacion_GIS/Teoricos_2018_nuevos/'
lista = os.listdir(Folder)

Erroneos = []

## ESCRITURA SOBRE EL ARCHIVO VACÍO CREADO ##
for i in range(len(lista)):
    if  lista[i].endswith(Key_Word):
        try:
            f = open(Folder +lista[i])
            print(lista[i])
            next(f)
            for line in f:
                fout.write(line)
            f.close()
        except:
            print ('fallo en ' + lista[i])
            Erroneos.append(lista[i])
fout.close()
