# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 15:55:10 2017

@author: Asus
"""
'''Radiation Model '''

'''Modelo de Radiación Kumar,1997 1 Celda
Filosofía:
La ROC que alcanza la tierra puede ser: directa, difusa o reflejada.

La radiación global de onda corta que recibe la tierra es casi proporcional a la
directa y varía con la geometría del terreno. la difusa responde más a variaciones
del gradiente del terreno. Para cielos despejados esta variación con respecto a la
topografía se comparte entre la difusa y la directa, lo cual hace que se conserve
la variabilidad espacial de la radiación percibida.

Radiación difusa:
    Isotropica: condiciones de cielo despejado
    Anisotropica: condiciones de cielo nublado o parcialmente nublado

Objetivo: Computing potential solar radiation (the amount of shortwave radiation
received under clear-sky conditions), over a large area using only digital elevation
and latitude data and to study the variation in radiation at different aspects and slopes.


El modelo calcula radiación de onda corta directa, sobre una superficie de la tierra
en un periodo de tiempo dado. Para un día dado, calcula los tiempos de amanecida y de 
atardecer, e integra la radiación solar desde el amanecer al atardecer de cada día.
Tiene en cuenta la radiación difusa de manera simplificada


PRIMER ENSAYO
Ensayo partiendo de que la pendiente = 0° y el aspecto es -1, por ser una celda plana

An understanding of the nature of extraterrestrial radiation, the effects of orientation
of a receiving surface, and the theoretically possible radiation at the earth’s surface is
important in understanding and using solar radiation data (libro de energía solar)

DUDAS:
Unidades del hillshade, Angulo Horario
Si tuvo en cuenta la radiación difusa
Solar time? 

- por el tiempo que hay.. la idea es hallar la irradiación en W/m2 y multiplicarla por el numero de
segundos que tiene el delta t...para integrarla y así hallar la irradiancia de ese delta t?

CONCEPTOS (solar Enginnering of thermal processes):
Irradiance, W/m2 The rate at which radiant energy is incident on a surface per unit
area of surface. The symbol G is used for solar irradiance, with appropriate subscripts for
beam, diffuse, or spectral radiation.

Irradiation or Radiant Exposure, J/m2 The incident energy per unit area on a
surface, found by integration of irradiance over a specified time, usually an hour or a day.
Insolation is a term applying specifically to solar energy irradiation. The symbol H is used
for insolation for a day. The symbol I is used for insolation for an hour (or other period if
specified).
....    
    '''

#paquetes requeridos

import matplotlib as mpl #Recordar esto para que no muestre las imagenes
mpl.use ("Agg")

import numpy as np
import datetime as dt
import pysolar.solar as ps
import pandas as pd
from dateutil.relativedelta import relativedelta
import pylab as plt
from osgeo import gdal
import os
import matplotlib.gridspec as gridspec
from mpl_toolkits.basemap import Basemap
from matplotlib import rcParams
import matplotlib.dates as mdates

import psycopg2



rcParams['legend.frameon']= False 
rcParams['legend.markerscale']=2.
rcParams['legend.fontsize']=14.
rcParams['axes.edgecolor']='0.8'
rcParams['axes.labelcolor']='0.4'
rcParams['axes.linewidth']='0.8'
rcParams['axes.labelsize']=17
rcParams['axes.titlesize']=20
rcParams[u'text.color']= u'.35'
rcParams[u'xtick.direction']= u'in'
rcParams[u'xtick.major.width']= 0.5
rcParams[u'ytick.color']=u'.15'
rcParams[u'ytick.direction']=u'in'
rcParams[ u'font.sans-serif']=[u'Arial',
                               u'Liberation Sans',
                               u'Bitstream Vera Sans',
                               u'sans-serif']
rcParams[u'patch.facecolor'] = (0.2980392156862745, 0.4470588235294118,0.6901960784313725)


#==============================================================================
'''Funciones del modelo'''
#==============================================================================

# __________  Angulos Universales _____________________________________________

def sun_elevation(latitude,longitude,date_time,elevacion_msnm):
    '''Origen: Pysolar 
    Altitude is reckoned with zero at the horizon. The altitude
is positive when the sun is above the horizon.'''
    #GetAltitude(latitude_deg, longitude_deg, utc_datetime, elevation = 0, temperature_celsius = 25, pressure_millibars = 1013.25)
    ele =  ps.get_altitude(latitude,longitude,date_time,elevation = elevacion_msnm)
    return ele
    
def sun_azimuth(latitude,longitude,date_time,elevacion_msnm):
    '''Origen: Pysolar 
    Azimuth is reckoned with zero corresponding to south. Positive azimuth
    estimates correspond to estimates east of south; negative estimates are west of south.'''
    azi = ps.get_azimuth(latitude,longitude,date_time,elevation = elevacion_msnm)
    #GetAzimuth(latitude_deg, longitude_deg, utc_datetime, elevation = 0)
    return azi

def date_to_hour_angle_radianes(date_time):
    '''The hour angle describes how far east or west the Sun is from the local meridian.
    It is zero when the Sun is on the meridian and decreases at a rate of 15° per hour
    Negativo: desde la medianoche cuando -12 (-180°), 0: al mediodía
    Positivo: desde el mediodía a la media noche (180°)'''
    hour_local = date_time.hour + (date_time.minute/60.) + (date_time.second/3600.)
    hs = 180 - (15* hour_local)
    DR = (2*np.pi/360.)
    hs = hs*DR #Angulo solar en radianes
    return hs

def Hour_angle_radianes_to_date(hs,date_time):
    '''The hour angle describes how far east or west the Sun is from the local meridian.
    It is zero when the Sun is on the meridian and decreases at a rate of 15° per hour
    Negativo: desde la medianoche cuando -12 (-180°), 0: al mediodía
    Positivo: desde el mediodía a la media noche (180°)'''
    
    DR = (2*np.pi/360.)
    hsD = hs/DR
    hour_local = (-hsD + 180.)/15.
    hour = int(hour_local)
    minutes = int(((hour_local - hour)*60.))
    return dt.datetime(date_time.year,date_time.month,date_time.day,hour,minutes)


def altitud_radianes(LR,ds,hs):
    '''Origen: Kumar
    Esta función calcula el angulo de elevación del sol (en radianes) sobre una superficie plana
    en función de L: latitud del sitio, ds: Ángulo de declinación solar, hs: Ángulo horario
    TODOS EN RADIANES'''
    sin_a = (np.sin(LR)*np.sin(ds)) + (np.cos(LR)*np.cos(ds)*np.cos(hs))
    a = np.arcsin(sin_a)
    return a

def azimuth_radianes(ds,hs,a,LR):    
    '''Origen: Kumar
    the angular displacement from south of the projection of beam radiation
    on the horizontal plane. Displacements east of south are negative and west of
    south are positive.
    Esta función calcula el angulo de azimuth del sol (en radianes) sobre una superficie plana
    en función de L: latitud del sitio, ds: Ángulo de declinación solar, hs: Ángulo horario
    TODOS EN RADIANES'''
    sin_az = (np.cos(ds)*np.sin(hs))/np.cos(a)
    az = np.arcsin(sin_az)

    '''Porque el condicional'''
    #To find the azimuth angle, it is important to distinguish the case where the Sun
    #is in the northern half of the sky from the case where it is in the southern half.
    #If cos hs is greater ( less) than tan ds /tan L then the Sun is in the northern
    #(southern) half of the sky and its azimuth angle is in the range - 90° to 90° (90° to 270°).
    
    TEST = np.tan(ds)/np.tan(LR)
    Y = np.cos(hs)
    if Y > TEST: az = az
    elif Y < TEST:  az = np.pi - az
    elif Y == TEST and hs>=0: az = np.pi/2.
    elif Y == TEST  and hs <0: az = - np.pi/2.
    else: 
        print ('El calculo de azimuth esta raro')
    return az

def sunrise_sunset_kumar(LR,ds):
    '''Ajuste para latitudes exceeding 66.5 N/S, verificar que x  no es mayor a 1 para acos(x)'''
    if  -1 * np.tan(np.nanmean(LR)) * np.tan(ds) < -1.0: #less than (lt)
        SR = np.arccos(-1.0)                                              
    elif -1 *np.tan(np.nanmean(LR)) * np.tan(ds) >  1.0: #greater than (gt)           
        SR = np.arccos(1.0)                                               
    else:    # PARA EL RESTO DE LATITUDES                                                                      "
        SR = np.arccos(-1*np.tan(np.nanmean(LR))*np.tan(ds)) #Amanecer en radianes (para -66.5°,66.5°)        
    SS = -SR #Atardecer  en radianes
    return SR,SS

def elevation_azimuth_day(date_str,TI,UTC,LAT,LON,ELEVACION):
    '''Esta función haya todos las posiciones del sol para un día dado y un paso de tiempo dado
    INPUT: date str - fecha del día en string y TI - paso de tiempo en formato numérico
    OUTPUT: DataFrame con índices de las horas del día y con values azimuths y elevaciones correspondientes'''
    index_horas = pd.date_range(date_str+' 00:00',date_str+' 23:59',freq=str(int(TI))+'min')   
    Elevations = pd.DataFrame(index = index_horas, columns = ['Elevations'])
    Azimuths = pd.DataFrame(index = index_horas, columns = ['Azimuths'])   
    dates_utc = [dtime + relativedelta(hours=(UTC*-1)) for dtime in index_horas]  
               
    Eleva =  [sun_elevation(LAT,LON,d,np.nanmean(ELEVACION)) for d in dates_utc]
    Azimu = [sun_azimuth(LON,LON,d,np.nanmean(ELEVACION)) for d in dates_utc]      
    Elevations ['Elevations'] = Eleva
    Azimuths['Azimuths'] = Azimu
    return Elevations, Azimuths 
         
def sunrise_sunset_ps(Elevation_day,Azimuth_day):
    #Se define amanecer y atardecer cuando hay un cambio de signo en la elevación 
    aux = np.where(Elevation_day.values>0)
    #Amanecer
    time_sunrise = Elevation_day.index[aux[0][0]]
    #Atardecer    
    time_sunset =  Elevation_day.index[aux[0][-1]]
    return  time_sunrise, time_sunset


def Day_number(date_time):
    #para conocer el día juliano se usa el atributo día del año de la función timetuple
    N =  date_time.timetuple().tm_yday
    return N

def Declination_angle(N):
    '''Devuelve el angulo de inclinaciónd e la tierra en Radianes y se calcula con el día Juliano'''
    DR = (2*np.pi/360.)
    ds = 23.45*DR*np.sin((360.*DR)*(284.+N)/365.)
    return ds

def Cos_angle_of_incidence(LR,B,aW,ds,hs):
    '''Origen: Kumar (ojo todos los inputs son en radianes)
    Angle of incidence, the angle between the beam radiation on a surface and the normal
    to that surface. 0°, es que el angulo del sol y el normal es el mismo osea la rad es directa
    y mayor a 90 es que el sol esta por debajo de la superficie
    i is the angle between the normal to the surface and the direction to the Sun
    B y aW están en radianes aquí :'''
    cos_i= (np.sin(ds)*(np.sin(LR)*np.cos(B) - (np.cos(LR)*np.sin(B)*np.cos(aW))))+ \
                  (np.cos(ds)*np.cos(hs))*(np.cos(LR)*np.cos(B) + np.sin(LR)*np.sin(B)*np.cos(aW))+\
                  (np.cos(ds)*np.sin(B)*np.sin(aW)*np.sin(hs))
    return cos_i




#___ PROPIO DE KUMAR __________________________________________________________
def Solar_flux_out_atmosphere(N):
    '''Origen: Kumar
    Estima la radiación incidente a tope de atmósfera en W/m2, con la ecuación de 
    Kreith and Kreider (1978) and Duffie and Beckman (1991)
    
    Esto considera la variación de la distancia entre la tierra y el sol durante el año
    debido a la excentricidad de la orbita de la tierra'''
    
    So = 1367. #Constante solar (W/m2)
    Io = So*(1+(0.0344*np.cos((360.*DR*N/365.))))
    return Io
    
def Air_mass_ratio(a):
    '''Origen: Kumar
    The air mass ratio is the relative mass of air through which solar radiation
    must pass to reach the surface of the Earth.
    It varies from M=1 when the Sun is overhead to about 30 when the Sun is at the horizon.
    The two main factors a ecting the air mass ratio are the direction of the path and
    the local altitude.
     Input: altitud en radiaciones'''
    M = np.sqrt(1229. + ((614.*np.sin(a))**2.)) - (614.*np.sin(a))
    return M         
            
def transmittance(M):
    '''Origen: Kumar
    Kreith and Kreider (1978 ) have described the atmospheric transmittance for
    beam radiation by the empirical relationship given in equation.'''
    tb = 0.56*(np.exp(-0.65* M)+ np.exp(-0.095*M))
    
    return tb 
    
def diffuse_radiation_kumar(B,a,tb,Io):
    '''Origen: Kumar ( tomado de Liu and Jordan)
    Diffuse solar radiation (Id ) was calculated using the method suggested by Gates (1980),
    Principle:  the smaller the transmittance to scattered skylight
    td is the radiation difusion coefficient. td can be related to tb by equation (Liu and Jordan 1960) 
    which applies to clear sky conditions, and shows that the greater the direct solar beam transmittance'''
    td= 0.271 - (0.294*tb)
    Id= Io*td*(np.cos(B/2.)**2.)*np.sin(a)
    td[a<=0] = 0 #Este condicional es para cuando no sea de día no ponga rad difusa

    return Id
def reflected_radiation_kumar(B,a,tb,Io):
    '''Origen: Kumar    
    The magnitude of reflected radiation depends on the slope of the surface and the
    ground reflectance coefficient. The reflected radiation here is the ground reflected
    radiation, both direct sunlight and diffuse skylight, impinging on the slope after
    being reflected from other surfaces visible above the slope’s local horizon. The
    reflecting surfaces are considered to be Lambertian. Here reflected radiation (Ir ) was
    calculated based on equation (19) (Gates 1980):
    where r is the ground reflectance coefficient and tr is the reflectance transmittivity'''
    r =  0.2 # A value of 0.20 was used for the reflectance coeficient of vegetation
    tr = 0.271 + (0.706*tb)
    Ir = r*Io*tr*(np.sin(B/2.)**2.)*np.sin(a)
    tr[a<=0] = 0 #Este condicional es para cuando no sea de día no ponga rad difusa
    
    return Ir      
#__ GDAL ______________________________________________________________________        
def read_map_raster(ruta_map, proyecto=None):
    # type: (object, object) -> object
    'Funcion: read_map\n' \
    'Descripcion: Lee un mapa raster soportado por GDAL.\n' \
    'Parametros Obligatorios:.\n' \
    ' -ruta_map: Ruta donde se encuentra el mapa.\n' \
    'Parametros Opcionales:.\n' \
    ' -proyecto: Si se especifica un proyecto importado como: from fwm.modealcion import cuencas as cu.\n' \
    ' como proyecto=cu, entonces cu copiara todas las propiedades del header del proyecto, exepcto dxp.\n' \
    'Retorno:.\n' \
    ' Si se especifica el proyecto: actualiza el proyecto y devuelve la matriz del mapa.\n' \
    ' Si no se especifica: devuelve la matriz del mapa y una lista con las caracteristicas:.\n' \
    ' En el siguiente orden: ncols,nrows,xll,yll,dx,nodata.\n' \
        # Abre el mapa
    direction = gdal.Open(ruta_map)
    # lee la informacion del mapa
    ncols = direction.RasterXSize
    nrows = direction.RasterYSize
    banda = direction.GetRasterBand(1)
    noData = banda.GetNoDataValue()
    geoT = direction.GetGeoTransform()
    dx = geoT[1]
    xll = geoT[0];
    yll = geoT[3] - nrows * dx
    # lee el mapa
    Mapa = direction.ReadAsArray().astype(np.float32)
    Mapa[Mapa == noData] = np.nan #es -3000
    #Adicionalmente los 0 también son nan: asociado alfillvalue
    Mapa[Mapa == 0] = np.nan #es -3000
    
    Mapa = Mapa[::-1]
    direction.FlushCache()
    del direction
    if proyecto != None:
        return Mapa
    else:
        return Mapa, [ncols, nrows, xll, yll, dx, noData]

def hill_shaded(azD_norte,aD,name,path_dem,path_hill):
    os.system('gdaldem hillshade -az '+str(azD_norte)+' -alt '+str(aD)+' '+path_dem+'dem_amva_landsat.tif '+path_hill+''+name+'_HillShade.tif')
#    https://gis.stackexchange.com/questions/54348/making-shaded-area-polygon-from-hillshade-raster-in-arcgis-desktop
    #Read generated raster and threshold to 100 (1 es el valor de sombra absoluta pero hasta 100 es bien)
    hillshade, [ncols, nrows, xll, yll, dx, noData] = read_map_raster(path_hill+name+'_HillShade.tif', proyecto=None)
    return hillshade

'''  Otra opción de Hillhade a explorar '''
#    https://matplotlib.org/api/colors_api.html
#    from matplotlib.colors import LightSource
#    ls = LightSource(azdeg=azD_norte, altdeg= aD.mean())
#    shadow2 = ls.hillshade(ELEVACION, vert_exag=1)

#    plt.imshow(shadow2-shadow);plt.colorbar()
#    plt.imshow(shadow2[::-1]);plt.colorbar()

#_____________________Consultas Piranometro ___________________________________
def Consulta_Piranometros(workdir,estacion,fecha_inicial,fecha_final):
    '''Las fechas se ingresan como datetime por la conversión en utc'''
    host   = "192.168.1.74"
    user   = "torresiata"
    passwd = "qJNXf%A);"
    dbname = "newsiata"
    
    #Se consulta en horas UTC
    fecha_inicial = fecha_inicial + relativedelta(hours = +5)
    fecha_final = fecha_final + relativedelta(hours = +5)
    
    fecha_inicial = fecha_inicial.strftime('%Y-%m-%d %H:%M:%S')
    fecha_final = fecha_final.strftime('%Y-%m-%d %H:%M:%S')
    query1 = "SELECT fecha_hora, radiacion FROM dato_piranometro WHERE idestacion = "+estacion+" AND fecha_hora BETWEEN '"+fecha_inicial+"' AND '"+fecha_final+"' ORDER BY idestacion, fecha_hora";
    
    print (query1)
    
    conn_db = psycopg2.connect("dbname='" + dbname + "' user='" + user +"' host='" + host + "' password='" + passwd + "'")
    db_cursor = conn_db.cursor ()
    db_cursor.execute (query1)
    data_db = db_cursor.fetchall ()
    #print data_db
    print ("****************************************")
    df_data_db = pd.read_sql (query1, conn_db)
    conn_db.close ()
    df_data_db.to_csv(workdir+ fecha_inicial[:10]+'_'+estacion+'_radiacion.csv', sep=',')

        
def read_piranometro_csv(date_str,codigo,workdir):
    #Datos medidos
    piranometro = pd.read_csv(workdir+date_str+'_'+codigo+'_radiacion.csv', header = 0,sep=',',index_col=1)
    R_ind  = pd.to_datetime(pd.DatetimeIndex(piranometro.index))
    R_index=[dat+relativedelta(hours=-5) for dat in R_ind]
    
    piranometro.index=R_index        
    fecha_completaG = pd.date_range(piranometro.index[0],piranometro.index[-1],freq="1min")
    piranometro = piranometro.reindex(index = fecha_completaG)  
    piranometro = piranometro.replace(to_replace=-999.,value=np.nan)
    radiacion = piranometro['radiacion']
    return radiacion



#==============================================================================
#Calculos por paso de tiempo
#==============================================================================
def time_step(hour,ds,LR,Io,path_raster,path_hill,path_save):  
    print (hour)
    hs = date_to_hour_angle_radianes(hour)       
    a = altitud_radianes(LR,ds,hs)
    
    #Conversión de ángulos de radianes a grados para poner como input en hillshade
    aD = a/DR

    az = np.zeros(LR.shape)    
    azD = np.zeros(LR.shape)    
    for lat_i in range(LR.shape[0]):
        for lon_j in range(LR.shape[1]):
            az_aux = azimuth_radianes(ds,hs,a[lat_i,lon_j],LR[lat_i,lon_j])
            az[lat_i,lon_j] = az_aux
            #Conversión de ángulos de radianes a grados para poner como input en hillshade
    
            if az_aux >= 0:
                azD[lat_i,lon_j] = az_aux/DR
            else: 
                azD[lat_i,lon_j] = 360 - (np.abs(az_aux)/DR) 

    #Construccion Hillshade
    azD_norte = (180.0 - azD.mean())%360.0
    name_hill = hour.strftime('%Y-%m-%d_%H_%M')
    shadow = hill_shaded(azD_norte,aD.mean(),name_hill,path_raster,path_hill) 

    shadow [shadow <= 20] = 0 #Sombra
    shadow [shadow > 20] = 1 #Celda iluminada
    #______________________________________________________________________________
    ''' shortwave solar radiation striking a surface normal to the Sun’s rays (Is )'''
    M =  Air_mass_ratio(a)
    tb = transmittance(M)  #FUNCIONA PARA 0.4-0.8 According to Gates (1980) at very high elevations with extremely clear air t may be as high as 0´8, while for a clear sky with high turbidity it may be as low as 0´4
    Is = Io * tb  
    #______________________________________________________________________________
    '''Solar radiation on a tilted surface (Ip ) '''
    cos_i = Cos_angle_of_incidence(LR,B,aW,ds,hs)
    Ip = Is * cos_i
    #______________________________________________________________________________
    '''Radiación difusa y reflejada'''
    Id = diffuse_radiation_kumar(B,a,tb,Io)   
    Ir = reflected_radiation_kumar(B,a,tb,Io)
    #______________________________________________________________________________
    '''Obtención de la radiación incidente global'''
    W2 = ((Ip* shadow)+Id+Ir) * 60. * TI *1.e-6  # (Acum ese tiempo MJ/W2) supongo que es TI es para saber los segundos del intervalo de tiempo
        
    '''Resume'''
    Direct =  Ip* shadow 
    Difusse = Id 
    Reflected =  Ir 
    return W2, shadow, cos_i, Direct, Difusse, Reflected
    
 
    
#==============================================================================
# Ejecución diaria 
#==============================================================================

def daily_model(date_str,TI,ELEVACION,LR,path_raster,save_data):
    print (date_str)
    '''NOTA A ESTO HAY QUE PONERLE TODAS LAS VARIABLES DEPENDIENTES PERO OTRO DIA JAJAJA'''
    
    
    date_time = dt.datetime.strptime(date_str,'%Y-%m-%d') 
    try:
        os.mkdir(workdir+'/'+date_str)
        os.mkdir(workdir+'/'+date_str+'/hillshade')
    except:
        print ('Ya había carpeta o no se pudo crear :P')
    
    path_save = workdir+'/'+date_str+'/'
    path_hill = path_save+'hillshade/'
    
    #==============================================================================
    #  Calculos DIURNOS - 1 vez al día
    #==============================================================================
    N = Day_number(date_time) #Dia juliano del año
    ds = Declination_angle(N)
    Io = Solar_flux_out_atmosphere(N)
    index_day = pd.date_range(start = date_str+' 05:00',end = date_str+' 19:00',freq=str(int(TI))+'min')
    index_save = pd.date_range(start = date_str+' 06:00',end = date_str+' 19:00',freq='1H')
    
    
    '''Esto es SOLO para amanecer y atardecer en los graficos (SIN TOPOGRAFIA)'''
    ''' AMANECER Y ATARDECER: Pysolar es más preciso pero se usa kumar...'''
    Elevations_day,Azimuths_day = elevation_azimuth_day(date_str,TI,UTC,LAT,LON,1600)    
    index_sunrise_ps, index_sunset_ps  = sunrise_sunset_ps(Elevations_day,Azimuths_day)
    
    '''Acumulador :)  W0 Es el resultado final'''
    W0 = np.zeros(ELEVACION.shape)
    time_rad = np.zeros(ELEVACION.shape)
    
    Torre_SIATA ={'lat':6.25932,'lon': -75.58855, 'cod':'6001'}
    Concejo_Itagui = {'lat':6.16815,'lon': -75.64421, 'cod':'6002'}
    Joaquin_vallejo = {'lat':6.25511, 'lon':-75.54268, 'cod':'6003'}
    Parque_de_aguas= {'lat':6.40626,'lon': -75.41947}
    
    #Dataframe para guardar los resultados del modelo
    Series_val = pd.DataFrame(index = index_day,columns=['TS_kumar','TS_kumar_directa','TS_kumar_difusa',
                                                          'CI_kumar','CI_kumar_directa','CI_kumar_difusa',
                                                          'JV_kumar','JV_kumar_directa','JV_kumar_difusa',
                                                          'TS_piranometro','CI_piranometro','JV_piranometro',
                                                          'TS_Shadow','CI_Shadow','JV_Shadow'])
    #==============================================================================
    # iterador
    #==============================================================================
    
    time_rad_all = np.ones((len(index_save),LR.shape[0], LR.shape[1]))*np.nan
    W0_flux_all = np.ones((len(index_save), LR.shape[0], LR.shape[1]))*np.nan
    for paso_tiempo, hour in enumerate(index_day):   
        W2_t, shadow_t, cos_i_t , Direct_t, Difusse_t, Reflected_t = time_step(hour,ds,LR,Io,path_raster,path_hill,path_save)
        
        #Acumulados
        W0 = W0 + W2_t #Radaiación global
        time_rad = time_rad + (shadow_t*(TI/60.)) #tiempo de sol en horas
        W0_flux = Direct_t + Difusse_t + Reflected_t
        
        if hour in index_save:
            paso_index_save = pd.Series(index = index_save,data = range(len(index_save)))
            paso_save = paso_index_save.ix[hour]
            W0_flux_all[paso_save,:,:] = Direct_t + Difusse_t + Reflected_t 
            time_rad_all[paso_save,:,:] = time_rad
            #______________________________________________________________________________
            '''Grafico de la radiación y sus componentes'''
            plt.figure(figsize=(14,8))
            gs=gridspec.GridSpec(2,3) #dos filas: instantaneo y acumulado, 2 columnas: 
            rcParams['figure.subplot.hspace'] = 0.2 # more height between subplots
            rcParams['figure.subplot.wspace'] = 0.2 # more width between subplots
            
            ax=plt.subplot(gs[0])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(W0_flux,interpolation='nearest',cmap= 'plasma', norm = norm_flux)
            plt.title(u'Irradiancia global (paso de tiempo)',fontsize = 15)
            cbar = plt.colorbar(cs,pad=0.04,fraction=0.046,values=bounds_flux,boundaries=bounds_flux)
            cbar.ax.tick_params(labelsize=12)
            cbar.ax.tick_params(labelsize=13)
            cbar.set_ticks(bounds_flux[::4])
            cbar.set_ticklabels(bounds_flux[::4])
            cbar.set_label(u'Flujo energía W/m2', fontsize=16)
            #Titulo de la grafica
            plt.text(1.1,1.23,u'Irradiación - Hora: '+hour.strftime('%Y-%m-%d %H:%M'),fontsize = 21,transform = ax.transAxes)
            
            ax=plt.subplot(gs[1])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(W0,interpolation='nearest',cmap= 'jet', norm = norm_W)
            plt.title(u'Irradiación Global \n (Acum. Directa, Difusa y Reflejada)',fontsize = 15)
            cbar = plt.colorbar(cs,pad=0.04,fraction=0.046,values=bounds_W,boundaries=bounds_W)
            cbar.ax.tick_params(labelsize=12)
            cbar.ax.tick_params(labelsize=13)
            cbar.set_ticks(bounds_W[::4])
            cbar.set_ticklabels(bounds_W[::4])
            cbar.set_label(u'Irradiación MJ/m2', fontsize=16)
        
            ax=plt.subplot(gs[2])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(time_rad,interpolation='nearest',cmap= 'viridis', norm = norm_sunshine)
            plt.title(u'Número de horas con \n radiación al momento',fontsize = 15)
            cbar = plt.colorbar(cs,pad=0.04,fraction=0.046,values=bounds_sunshine,boundaries=bounds_sunshine)
            cbar.ax.tick_params(labelsize=13)
            cbar.set_ticks(bounds_sunshine[::4])
            cbar.set_ticklabels(bounds_sunshine[::4])
            cbar.set_label(u'Horas', fontsize=16)
            
            ax=plt.subplot(gs[3])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(Direct_t,interpolation='nearest',cmap= 'plasma', norm = norm_flux)
            plt.title(u'Irradiacion directa (paso de tiempo)',fontsize = 15)
            cbar = plt.colorbar(cs,pad=0.04,fraction=0.046,values=bounds_flux,boundaries=bounds_flux)
            cbar.ax.tick_params(labelsize=12)
            cbar.ax.tick_params(labelsize=13)
            cbar.set_ticks(bounds_flux[::4])
            cbar.set_ticklabels(bounds_flux[::4])
            cbar.set_label(u'Flujo energía W/m2', fontsize=16)
            
            ax=plt.subplot(gs[4])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(Difusse_t,interpolation='nearest',cmap= 'plasma', norm = norm_flux)
            plt.title(u'Irradiación difusa (paso de tiempo)',fontsize = 15)
            cbar = plt.colorbar(cs,pad=0.04,fraction=0.046,values=bounds_flux,boundaries=bounds_flux)
            cbar.ax.tick_params(labelsize=12)
            cbar.ax.tick_params(labelsize=13)
            cbar.set_ticks(bounds_flux[::4])
            cbar.set_ticklabels(bounds_flux[::4])
            cbar.set_label(u'Flujo energía W/m2', fontsize=16)
            
            ax=plt.subplot(gs[5])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(Reflected_t,interpolation='nearest',cmap= 'plasma', norm = norm_flux)
            plt.title(u'Irradiación reflejada (paso de tiempo)',fontsize = 15)
            cbar = plt.colorbar(cs,pad=0.04,fraction=0.046,values=bounds_flux,boundaries=bounds_flux)
            cbar.ax.tick_params(labelsize=12)
            cbar.ax.tick_params(labelsize=13)
            cbar.set_ticks(bounds_flux[::4])
            cbar.set_ticklabels(bounds_flux[::4])
            cbar.set_label(u'Flujo energía W/m2', fontsize=16)
            
            
            plt.savefig(path_save+'/Irradiacion'+hour.strftime('%Y-%m-%d_%H_%M')+'.png',dpi=150,transparent=False,bbox_inches='tight')
            
            plt.show();plt.close()
            #______________________________________________________________________________
            '''Grafico del tiempo con radiación'''
            plt.figure(figsize=(12,7))
            gs=gridspec.GridSpec(1,2) #dos filas: instantaneo y acumulado, 2 columnas: 
            rcParams['figure.subplot.hspace'] = 0.2 # more height between subplots
            rcParams['figure.subplot.wspace'] = 0.2 # more width between subplots
            plt.suptitle(u'Tiempo con radiación - Hora: '+hour.strftime('%Y-%m-%d %H:%M'),fontsize = 18)
            #Graficando los datos:
            
            ax=plt.subplot(gs[0])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(shadow_t*(TI/60.),interpolation='nearest',cmap= 'magma')
            cbar=plt.colorbar(cs, cmap= 'magma', boundaries=[-1,0.5,1], ticks=[0,0.5,1],orientation = 'horizontal')
            tick_locs   = [0.25,0.75]
            tick_labels = ['Sombra','Luz']
            cbar.locator     = mpl.ticker.FixedLocator(tick_locs)
            cbar.formatter   = mpl.ticker.FixedFormatter(tick_labels)
            cbar.ax.tick_params(labelsize = 14)
            cbar.update_ticks()
            plt.title(u'Pixeles iluminados vs sombra',fontsize = 15)
            
            ax=plt.subplot(gs[1])   
            m = Basemap(llcrnrlon=min_lon,llcrnrlat=min_lat,urcrnrlon=max_lon,urcrnrlat=max_lat,projection='cyl', resolution='i') 
            cs = m.imshow(time_rad,interpolation='nearest',cmap= 'viridis', norm = norm_sunshine)
            plt.title(u'Acumulado al momento',fontsize = 15)
            
            cbar = plt.colorbar(cs,pad=0.04,fraction=0.046,values=bounds_sunshine,boundaries=bounds_sunshine)
            cbar.ax.tick_params(labelsize=13)
            cbar.set_ticks(bounds_sunshine[::4])
            cbar.set_ticklabels(bounds_sunshine[::4])
            cbar.set_label(u'Horas con radiación directa', fontsize=16)
            try:
                plt.savefig(path_save+'/Sunshine'+hour.strftime('%Y-%m-%d_%H_%M')+'.png',dpi=150,transparent=False,bbox_inches='tight')
            except:
                print ('forma de la matriz de hillshade: '+ str((shadow_t*(TI/60.)).shape))
                print ('forma de la matriz de hillshade: '+ str((time_rad).shape))
                plt.savefig(path_save+'/Sunshine'+hour.strftime('%Y-%m-%d_%H_%M')+'.png',dpi=150,transparent=False)
            
            plt.show();plt.close()
    
    
        #==============================================================================
        '''Extracción y guardada de series de radiación en un punto dado''' 
        #==============================================================================
        
        Series_val.ix[hour]['TS_kumar']  = find_value(W0_flux,lat_tile,lon_tile, Torre_SIATA)
        Series_val.ix[hour]['CI_kumar']  = find_value(W0_flux,lat_tile,lon_tile, Concejo_Itagui)
        Series_val.ix[hour]['JV_kumar']  = find_value(W0_flux,lat_tile,lon_tile, Joaquin_vallejo)
    
        Series_val.ix[hour]['TS_kumar_directa']  = find_value(Direct_t,lat_tile,lon_tile, Torre_SIATA)
        Series_val.ix[hour]['CI_kumar_directa']  = find_value(Direct_t,lat_tile,lon_tile, Concejo_Itagui)
        Series_val.ix[hour]['JV_kumar_directa']  = find_value(Direct_t,lat_tile,lon_tile, Joaquin_vallejo)
    
        Series_val.ix[hour]['TS_kumar_difusa']  = find_value(Difusse_t,lat_tile,lon_tile, Torre_SIATA)
        Series_val.ix[hour]['CI_kumar_difusa']  = find_value(Difusse_t,lat_tile,lon_tile, Concejo_Itagui)
        Series_val.ix[hour]['JV_kumar_difusa']  = find_value(Difusse_t,lat_tile,lon_tile, Joaquin_vallejo)
    
        Series_val.ix[hour]['TS_Shadow']  = find_value(shadow_t,lat_tile,lon_tile, Torre_SIATA)
        Series_val.ix[hour]['CI_Shadow']  = find_value(shadow_t,lat_tile,lon_tile, Concejo_Itagui)
        Series_val.ix[hour]['JV_Shadow']  = find_value(shadow_t,lat_tile,lon_tile, Joaquin_vallejo)
        
    # _____ Consecución datos del piranometro  ________________________________________________
    
    
    for estacion in ['6001','6002','6003']:
        fecha_inicial = dt.datetime.strptime(date_str+' 05:00:00','%Y-%m-%d %H:%M:%S') 
        fecha_final = dt.datetime.strptime(date_str+' 19:00:00','%Y-%m-%d %H:%M:%S') 
        Consulta_Piranometros(path_save,estacion,fecha_inicial,fecha_final)
    
    
    Series_piranometro = pd.DataFrame()
    try:
        Series_piranometro['TS_piranometro'] = read_piranometro_csv(date_str,Torre_SIATA['cod'],path_save)
    except:
        Series_piranometro['TS_piranometro'] = pd.Series(index = index_day, data = np.ones(len(index_day))*np.nan)
    
    try:
        Series_piranometro['JV_piranometro'] = read_piranometro_csv(date_str,Joaquin_vallejo['cod'],path_save)
    except:
        Series_piranometro['JV_piranometro'] = pd.Series(index = index_day, data = np.ones(len(index_day))*np.nan)
    
    try:
        Series_piranometro['CI_piranometro'] = read_piranometro_csv(date_str,Concejo_Itagui['cod'],path_save)
    except:
        Series_piranometro['CI_piranometro'] = pd.Series(index = index_day, data = np.ones(len(index_day))*np.nan)
        
    
    Series_val['TS_piranometro'] = Series_piranometro['TS_piranometro'].ix[index_day]
    Series_val['CI_piranometro'] = Series_piranometro['CI_piranometro'].ix[index_day]
    Series_val['JV_piranometro'] = Series_piranometro['JV_piranometro'].ix[index_day]
    
    Series_piranometro = Series_piranometro.ix[index_day[0]:index_day[-1]]
    
    # _____ Grafico de comparación :Radiación Global  ________________________________________________    
    plt.figure(figsize=(12,8))
    gs=gridspec.GridSpec(2,2) #dos filas: ctrl y asimilacion, 6 columnas: obs + 5 corridas
    rcParams['figure.subplot.hspace'] = 0.65# more height between subplots
    rcParams['figure.subplot.wspace'] = 0.15 # more width between subplots
    
    ax=plt.subplot(gs[0])   
    plt.plot(Series_piranometro['TS_piranometro'] ,color = 'Indigo',lw =2, alpha = 0.4,label = u'Piranómetro')
    plt.plot(Series_val['TS_kumar'] ,color = 'DarkOrchid',lw =2, label = u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.ylabel('Irradiancia - Flujo (W/m2)',fontsize = 15)
    plt.text(0.32,1.05, u'Torre SIATA', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    #Este es el titulo
    plt.text(1.1,1.2,u'Series de tiempo en ubicaciones de piranómetros \n (Radiación Global): '+hour.strftime('%Y-%m-%d'),fontsize = 21,transform = ax.transAxes, horizontalalignment='center')
    
    ax=plt.subplot(gs[1])   
    plt.plot(Series_piranometro['CI_piranometro'],color = 'MediumBlue',lw =2,alpha = 0.4, label =  u'Piranómetro')
    plt.plot(Series_val['CI_kumar_directa'],color = 'RoyalBlue',lw =2, label =   u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.text(0.2,1.05, u'Concejo de Itagüí', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    
    ax=plt.subplot(gs[2])   
    plt.plot(Series_piranometro['JV_piranometro'],color = 'Teal',lw =2,alpha = 0.4,label =  u'Piranómetro')
    plt.plot(Series_val['JV_kumar'],color = 'LightSeaGreen',lw =2, label =  u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.text(0.25,1.05, u'Joaquín Vallejo', transform = ax.transAxes,fontsize = 16)
    plt.ylabel('Irradiancia - Flujo (W/m2)',fontsize = 15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    
    ax=plt.subplot(gs[3])   
    plt.plot(Series_val['TS_kumar'] ,color = 'DarkOrchid',lw =2, label = u'Torre SIATA (modelo)')
    plt.plot(Series_val['CI_kumar'],color = 'RoyalBlue',lw =2, label =   u'Concejo de Itagüí (modelo)')
    plt.plot(Series_val['JV_kumar'],color = 'LightSeaGreen',lw =2, label =  u'Joaquín Vallejo (modelo)')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.),label = 'Amanecer y atardecer')
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.text(0.1,1.05, u'Comparación entre lugares', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.85,-0.1),fontsize = 14, ncol = 1)
    
    plt.savefig(path_save+'/TimeSeriePiranometros_Global_'+hour.strftime('%Y-%m-%d')+'.png',dpi=300,transparent=False,bbox_inches='tight')
    plt.show();plt.close()
    
    # _____ Grafico de comparación :Radiación Directa  ________________________________________________
    plt.figure(figsize=(12,8))
    gs=gridspec.GridSpec(2,2) #dos filas: ctrl y asimilacion, 6 columnas: obs + 5 corridas
    rcParams['figure.subplot.hspace'] = 0.65# more height between subplots
    rcParams['figure.subplot.wspace'] = 0.15 # more width between subplots
    
    ax=plt.subplot(gs[0])   
    plt.plot(Series_piranometro['TS_piranometro'] ,color = 'Indigo',lw =2, alpha = 0.4,label = u'Piranómetro')
    plt.plot(Series_val['TS_kumar_directa'] ,color = 'DarkOrchid',lw =2, label = u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.ylabel('Irradiancia - Flujo (W/m2)',fontsize = 15)
    plt.text(0.32,1.05, u'Torre SIATA', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    #Este es el titulo
    plt.text(1.1,1.2,u'Series de tiempo en ubicaciones de piranómetros \n (Radiación Directa): '+hour.strftime('%Y-%m-%d'),fontsize = 21,transform = ax.transAxes, horizontalalignment='center')
    
    ax=plt.subplot(gs[1])   
    plt.plot(Series_piranometro['CI_piranometro'],color = 'MediumBlue',lw =2,alpha = 0.4, label =  u'Piranómetro')
    plt.plot(Series_val['CI_kumar_directa'],color = 'RoyalBlue',lw =2, label =   u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.text(0.2,1.05, u'Concejo de Itagüí', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    
    ax=plt.subplot(gs[2])   
    plt.plot(Series_piranometro['JV_piranometro'],color = 'Teal',lw =2,alpha = 0.4,label =  u'Piranómetro')
    plt.plot(Series_val['JV_kumar_directa'],color = 'LightSeaGreen',lw =2, label =  u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.text(0.25,1.05, u'Joaquín Vallejo', transform = ax.transAxes,fontsize = 16)
    plt.ylabel('Irradiancia - Flujo (W/m2)',fontsize = 15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    
    ax=plt.subplot(gs[3])   
    plt.plot(Series_val['TS_kumar_directa'] ,color = 'DarkOrchid',lw =2, label = u'Torre SIATA (modelo)')
    plt.plot(Series_val['CI_kumar_directa'],color = 'RoyalBlue',lw =2, label =   u'Concejo de Itagüí (modelo)')
    plt.plot(Series_val['JV_kumar_directa'],color = 'LightSeaGreen',lw =2, label =  u'Joaquín Vallejo (modelo)')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.),label = 'Amanecer y atardecer')
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.text(0.1,1.05, u'Comparación entre lugares', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.85,-0.1),fontsize = 14, ncol = 1)
    
    plt.savefig(path_save+'/TimeSeriePiranometros_Directa_'+hour.strftime('%Y-%m-%d')+'.png',dpi=300,transparent=False,bbox_inches='tight')
    plt.show();plt.close()
    
    # _____ Grafico de comparación :Radiación Difusa  ________________________________________________
    plt.figure(figsize=(12,8))
    gs=gridspec.GridSpec(2,2) #dos filas: ctrl y asimilacion, 6 columnas: obs + 5 corridas
    rcParams['figure.subplot.hspace'] = 0.85# more height between subplots
    rcParams['figure.subplot.wspace'] = 0.15 # more width between subplots
    
    ax=plt.subplot(gs[0])   
    plt.plot(Series_piranometro['TS_piranometro'] ,color = 'Indigo',lw =2, alpha = 0.4,label = u'Piranómetro')
    plt.plot(Series_val['TS_kumar_difusa'] ,color = 'DarkOrchid',lw =2, label = u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.ylabel('Irradiancia - Flujo (W/m2)',fontsize = 15)
    plt.text(0.32,1.05, u'Torre SIATA', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    #Este es el titulo
    plt.text(1.1,1.2,u'Series de tiempo en ubicaciones de piranómetros \n (Radiación Difusa): '+hour.strftime('%Y-%m-%d'),fontsize = 21,transform = ax.transAxes, horizontalalignment='center')
    
    ax=plt.subplot(gs[1])   
    plt.plot(Series_piranometro['CI_piranometro'],color = 'MediumBlue',lw =2,alpha = 0.4, label =  u'Piranómetro')
    plt.plot(Series_val['CI_kumar_difusa'],color = 'RoyalBlue',lw =2, label =   u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.text(0.2,1.05, u'Concejo de Itagüí', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    
    ax=plt.subplot(gs[2])   
    plt.plot(Series_piranometro['JV_piranometro'],color = 'Teal',lw =2,alpha = 0.4,label =  u'Piranómetro')
    plt.plot(Series_val['JV_kumar_difusa'],color = 'LightSeaGreen',lw =2, label =  u'Modelo')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    plt.text(0.25,1.05, u'Joaquín Vallejo', transform = ax.transAxes,fontsize = 16)
    plt.ylabel('Irradiancia - Flujo (W/m2)',fontsize = 15)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.legend(bbox_to_anchor=(0.65,-0.1),fontsize = 14, ncol = 1)
    
    ax=plt.subplot(gs[3])   
    plt.plot(Series_val['TS_kumar_difusa'] ,color = 'DarkOrchid',lw =2, label = u'Torre SIATA (modelo)')
    plt.plot(Series_val['CI_kumar_difusa'],color = 'RoyalBlue',lw =2, label =   u'Concejo de Itagüí (modelo)')
    plt.plot(Series_val['JV_kumar_difusa'],color = 'LightSeaGreen',lw =2, label =  u'Joaquín Vallejo (modelo)')
    plt.axvline(x= index_sunrise_ps,lw = 4 , color = (19/255.,77/255.,111/255.),label = 'Amanecer y atardecer')
    plt.axvline(x= index_sunset_ps, lw = 4 , color = (19/255.,77/255.,111/255.))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.text(0.1,1.05, u'Comparación entre lugares', transform = ax.transAxes,fontsize = 16)
    plt.legend(bbox_to_anchor=(0.85,-0.1),fontsize = 14, ncol = 1)
    
    plt.savefig(path_save+'/TimeSeriePiranometros_Difusa_'+hour.strftime('%Y-%m-%d')+'.png',dpi=300,transparent=False,bbox_inches='tight')
    plt.show();plt.close()    
    #_____________________    Guardar datos    ________________________________
    if save_data == True:
        '''Guardar series en CSV'''
        Series_val.to_csv(path_save+date_str+'_Timeseries.csv',sep=',')
    
    
        '''Guardar Datos en pickle: ABORTADO MATA EL PC, repito MATA el PC'''
        Data_rad = {'Radglobal_Flux':W0_flux_all,
            'Timestep':TI,
            'Indices':index_save,
            'Indices_originales': index_day,
            'Irradiacion_dia':W0,
            'Time_rad_dia':time_rad}
        Data_time = {'Time_solar':time_rad_all,
            'Timestep':TI,
            'Indices':index_save,
            'Indices_originales': index_day,
            'Time_rad_dia':time_rad}
        
        import pickle
        output1 = open(path_save+date_str+'_Resultados_Radiacion.pkl', 'wb')
        pickle.dump(Data_rad, output1)
        output1.close()
        del Data_rad
    
        output2 = open(path_save+date_str+'_Resultados_TiempoRadiacion.pkl', 'wb')
        pickle.dump(Data_time, output2)
        output2.close()
        
        del Data_time

    if save_data == False:
        '''BORRAR_HILLSHADES'''
        os.system('rm -rf '+path_hill)

''' Herramientas series de tiempo''' 
def find_value(matriz,lat,lon, ubicacion):
    valuelat = ubicacion['lat']
    valuelon = ubicacion['lon']
    latx = (np.abs(lat-valuelat)).argmin()
    lonx = (np.abs(lon-valuelon)).argmin()
    value = matriz[latx,lonx]
    return value
#==============================================================================
#  #Valores Fijos y asociados al DEM
#==============================================================================

workdir = '/home/gguzmane/Rad_model/'
path_raster= workdir+'/AncillaryData/'

#
#workdir = 'C:/Users/gizel/Dropbox/UrbanHeatIsland/Modelo_Radiacion/results/'
#path_raster= 'C:/Users/gizel/Documents/UHI/Raster/'
#
#Conversiones
DR = ((2.*np.pi)/360.)  # factor de conversion de grados a radianes

'''Elevacion'''
ELEVACION, [ncols, nrows, xll, yll, dx, noData] = read_map_raster(path_raster+'dem_amva_landsat.tif', proyecto=None)
'''pendiente'''
B_d, [ncols, nrows, xll, yll, dx, noData] = read_map_raster(path_raster+'slope_amva_landsat.tif', proyecto=None)
#B_d = 0 #Es la pendiente que se obtiene del DEM
B = B_d*DR # Pendiente en radianes
'''Aspecto en grados con 0 grados al norte (orientado al norte)'''
aW_n, [ncols, nrows, xll, yll, dx, noData] = read_map_raster(path_raster+'aspect_amva_landsat.tif', proyecto=None)
'''Aspecto en grados con 0 grados al sur (orientado al sue)'''
#Cambio de aspecto porque el azimuth es cero en el sur (ESTO ES SI EL ASPECTO VA DE 0 - 360)
#LO RARO ES QUE SE PONE PARA QUE SEA EN SENTIDO ANTI HORARIO PERO BUEEEH
aW_s = np.ones(aW_n.shape)*np.nan    
aW_s[aW_n == -1] = 0
aW_s[aW_n <= 180] = (180 - aW_n[aW_n <= 180]) # si se ubica entre N-E-S,  (le less or equal)
aW_s[aW_n > 180] = (540- aW_n[aW_n > 180]) # si se ubica entre S-W_E, 

aW = aW_s*DR # aspecto en radianes

'''Limites del shape en coordenadas geográficas'''
min_lat = 5.978178; min_lon = -75.719430 
max_lat = 6.512488; max_lon = -75.222057

lat_tile = np.linspace(min_lat,max_lat,ELEVACION.shape[0])
lon_tile = np.linspace(min_lon,max_lon,ELEVACION.shape[1])

LonD, LatD = np.meshgrid(lon_tile, lat_tile)

'''Latitud que le entra al modelo'''
LR = LatD*DR #Latitud en radianes
'''Se hace la suposicion que siempre hay el mismo angulo del sol para todo el valle de Aburrá,
en Hillshade el angulo que se usa es fijo y los tiempos de integración tambienv ( elevacion no varia, azimuth 1 grado)'''
#punto en el centro de Medellín
LAT = lat_tile.mean()  #(positivo al norte, ngativo al sur del ecuador)
LON =  lon_tile.mean()

'''Cosas para las colorbar'''
import matplotlib.colors as colors
bounds_cosi  = np.round(np.linspace(-1,1,20),2)
norm_cosi = colors.BoundaryNorm(boundaries=bounds_cosi, ncolors=256) 

bounds_W  = np.round(np.linspace(0,42,43),2)
norm_W = colors.BoundaryNorm(boundaries=bounds_W, ncolors=256) 

bounds_flux  = np.round(np.linspace(0,1200,41),2)
norm_flux = colors.BoundaryNorm(boundaries=bounds_flux, ncolors=256) 

bounds_sunshine  = np.round(np.linspace(0,14,28),2)
norm_sunshine = colors.BoundaryNorm(boundaries=bounds_sunshine, ncolors=256) 


#==============================================================================
# AHORA SI SUPER EJECUCION!!!!   
#==============================================================================

# Día
#date_str = '2016-11-21'
TI = 10. #Tiempo de intervalo en minutos, entre los calculos de flujo
UTC = -5.
Dias = ['2016-11-22','2017-01-23','2017-02-05','2016-03-25','2016-04-15','2016-05-17','2017-06-12',
        '2016-07-09','2016-08-15','2016-09-15','2016-10-15','2016-11,21','2016-12-15']

#Ejecucion lenta guardando todo (hillshades + datos)
for dia_mes in Dias:
    daily_model(dia_mes, TI, ELEVACION, LR, path_raster,save_data = True)

#==============================================================================
#def open_pklfiles(path_pkldata):
#    import  pickle
#    open_pkl = open(path_pkldata, 'rb')
#    data = pickle.load(open_pkl)
#    open_pkl.close()
#    return data  

