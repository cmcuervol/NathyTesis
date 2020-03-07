# -*- coding: utf-8 -*-
import datetime as dt
import os

path_directory = "/media/nacorreasa/NATHALIA/GOES_NC/"
Borrar_Nocturnas = 'no'                ## NOTA IMPORTANTE:  Para borrarlas debe ser: 'no'

atardecer = '18:20'
amanecer = '05:40'
#Banda = 02
resolucion = '0.5 Km'

'Este codigo es el primer paso para el orden de los archivos de GOES, ya que borra las imagenes'
'correspondiente a las horas nocturas, las cuales para el estudio de energia tofovoltaica no es'
'relevante. Luego de este, sigue el programa de Recorte de Archivos.'

# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
                                        # No cambiar nada en adelante
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*

def retorna_fecha_hora_info(ruta):
    fecha = ruta[ruta.find('c2019')+1:ruta.find('c2019')+12]
    fecha = dt.datetime.strptime(fecha, '%Y%j%H%M')
    fecha_utc = fecha.strftime('%Y/%m/%d/ %H:%M')
    fecha_local = fecha - dt.timedelta(hours=5)
    fecha_local = fecha_local.strftime('%Y/%m/%d %H:%M')
    fecha_path = fecha.strftime('%Y%m%d')
    fecha = fecha.strftime('%Y%m%d%H%M')
    return fecha_utc, fecha_path, fecha , fecha_local

def borrar_imagenes_nocturnas (path_directory, amanecer, atardecer):
    Folders = []
    for filename in os.listdir(path_directory):
        Folders.append(filename)
    for i in range(len(Folders)):
        for file in os.listdir(path_directory+Folders[i]):
            if file.endswith(".nc"):
                fecha_utc, fecha_path, fecha, fecha_local = retorna_fecha_hora_info(path_directory+Folders[i]+"/" + file)
                local_hour = dt.datetime.strptime(fecha_local[11:], '%H:%M').time()
                if local_hour > dt.datetime.strptime(atardecer, '%H:%M').time() or local_hour < dt.datetime.strptime(
                        amanecer, '%H:%M').time():
                    os.system('rm ' + path_directory+Folders[i]+"/" + file)
                    print ('Borrando todos los archivos nocturnos')
                else:
                    print ('No se econtraron archivos para borrar')

if Borrar_Nocturnas == 'no':
    borrar_imagenes_nocturnas(path_directory, amanecer, atardecer)    ## Ejecutando las dos funciones anteriores
else:
    pass
