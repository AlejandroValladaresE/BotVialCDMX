#Este módulo tiene el objetivo de analizar y calificar el texto recibido del stream en linea con la finalidad de calificar y almacenar 
#la información cuando se identifica una volcadura, un atropellado o un fallecimiento por incidentes viales.
# Las princilapes actividades son: 
#         - estandarización del texto convirtiendolo a minusculas
#         - Limpieza del texto
#         - busqueda de coincidencias para calificar el incidente vial
#
from cgitb import text
import re
import csv
import string
#import time
from config import obten_fecha
import logging
#from zoneinfo import ZoneInfo
import os
logging.basicConfig(filename='Documentos/EntornoBot/logs/botvial.log',level=logging.error)
#logging.basicConfig(filename='~/Documentos/EntornoBot/logs/botvial.log',level=logging.error)
import emoji
import pytz
import tzlocal
from datetime import datetime

from clasificadores.alcaldia import identifica_alcaldia

nombre_modulo = "analizador.py"

#función para identificar un evento. Se busca por cada una de las palabras que forman
# el evento dentro del texto del tuit. Se retorna lo siguiente:
#la funcion analiza eventos retorna una lista con los eventos identificados. 
# se descartan: Retweets, respuestas a eventos válidos o eventos en Zona Metropolitana de VDM
# Argumentos:
#    analiza_evento(status,lista_fallecido,lista_peaton,lista_bicis,lista_moto,lista_atropellado,lista_volcadura,dict_alcaldia,lista_accidente,lista_exclusiones)     
def analiza_evento(tweet,list_fall,list_peat,list_bic,list_moto,list_atrop,list_volc,list_accidente,list_exclusion):

    list_fallecimiento = list_fall
    list_peaton = list_peat
    list_bicicleta = list_bic
    list_motociclista = list_moto
    list_atropellado = list_atrop
    list_volcadura = list_volc
    lista_exclusiones = list_exclusion
    lista_accidente = list_accidente 
    file_name = 'Documentos/EntornoBot/files/logcdmx'   

    texto = tweet.full_text       
    evento = texto.lower()     
    resultado = []
    estado = 0

    #se eliminan los acentos
    cadena_limpia = limpia_texto(evento)
    # Se descarta evento si ocurrio en ZMVM o alguna exclusion general
    exclusion = busca_evento(lista_exclusiones,cadena_limpia)
    if exclusion:
        estado = 0
    else:
        # se buscan de manera detallada el tipo de evento, si se encuentra, la funcion busca_evento
        fallecimiento = busca_evento(list_fallecimiento, cadena_limpia)
        peaton = busca_evento(list_peaton,cadena_limpia)
        motociclista = busca_evento(list_motociclista,cadena_limpia)
        ciclista = busca_evento(list_bicicleta,cadena_limpia)        
        atropellado = busca_evento(list_atropellado,cadena_limpia)
        volcadura = busca_evento(list_volcadura,cadena_limpia)
        accidente = busca_evento(lista_accidente,cadena_limpia)
        alcaldia = identifica_alcaldia(cadena_limpia)
        
        if volcadura or atropellado or fallecimiento or accidente:
            # se descartan los fallecimientos no relacionados con eventos viales
            if fallecimiento and (atropellado or volcadura or accidente):
                estado = 1
            elif atropellado or volcadura or accidente:                    
                estado = 1
            else:                    
                estado = 0
            # si el evento califica correctamente, se registra en el log
            if estado == 1:
                resultado.append(tweet.id)               #[0
                resultado.append(convierte_utc_localtime(tweet.created_at))       #[1]
                resultado.append(tweet.user.screen_name) #[2]
                resultado.append(cadena_limpia)          #[3]
                fecha_hora = obten_fecha()               
                resultado.append(fecha_hora[0:10])       #[4]
                resultado.append(fecha_hora[11:20])      #[5]
                resultado.append(atropellado)            #[6]
                resultado.append(volcadura)              #[7]
                resultado.append(fallecimiento)          #[8]
                resultado.append(ciclista)               #[9]
                resultado.append(motociclista)           #[10]
                resultado.append(peaton)                 #[11]
                resultado.append(accidente)              #[12]
                resultado.append(alcaldia.value)         #[13]
                file_name += fecha_hora[0:10] + ".csv"
                estado = guarda_evento(resultado,file_name)
                if estado == 1:
                    print("Evento Aceptado",":", tweet.user.screen_name,":", cadena_limpia)
    return resultado         

#Función para identificar en el texto del tuit si existe alguna de las palabras que califiquen  
# dentro de los parámetros de analisis.
def busca_evento(palabras,texto):
    status_evento = 0    
    for palabra in palabras:
        patron = re.compile(r'\b{}\b'.format(palabra))
        if (re.search(patron,texto)):
            status_evento = 1
            break
    return status_evento

#Función para limpiar la cadena de caracteres del tuit recibido.
# una vez pasada a minusculas el texto, se realiza lo siguiente:
#   Elminar acentos, eliminar emojis con la libreria emoji,
# eliminar las nuevas lineas  con la función replace
def limpia_texto(texto):
    url = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    lista_acentos = ["\u00e1","\u00e9","\u00ed","\u00f3","\u00fa"]
    # el texto se pasa a minusculas
    texto_limpio = texto.lower()
    # se reemplazan los acentos por vocales sin acentos
    for acento in lista_acentos:
        if acento == "\u00e1":
            texto_limpio = texto_limpio.replace(acento,'a')
        elif acento == "\u00e9":
            texto_limpio = texto_limpio.replace(acento,'e')
        elif acento == "\u00ed":
            texto_limpio = texto_limpio.replace(acento,'i')
        elif acento == "\u00f3":
            texto_limpio = texto_limpio.replace(acento,'o')
        elif acento == "\u00fa":
            texto_limpio = texto_limpio.replace(acento,'u')
    # se eliminan los emojis
    texto_limpio = re.sub(emoji.get_emoji_regexp(),r"",texto_limpio)
    #se eliminan los caracteres de nueva linea
    texto_limpio = texto_limpio.replace('\n','')
    #se eliminan las url's
    texto_limpio = re.sub(url,'',texto_limpio)
    #se eliminan los carateres de puntuación
    punct = string.punctuation
    for char in punct:
        texto_limpio = texto_limpio.replace(char," ") 
    return texto_limpio
        
#función para almacenar el evento identificado  en el log de eventos
def guarda_evento(evento,file):
    respuesta = 0
    fecha = obten_fecha()
    try:
        with open(file, 'a',newline='',encoding="UTF-8") as log:
            writer = csv.writer(log,delimiter = '|',quoting=csv.QUOTE_ALL)
            writer.writerow(evento)  
            respuesta = 1             
    except Exception as e:
        logging.error(fecha + " "  + nombre_modulo + " " + "Error al guardar evento" , exc_info=True)
        print ("Error al escribir registro")
        respuesta = 0
    return respuesta
# Esta funcion permite convertir la fecha obtenida del campo created_at del tuit la cual se encuentra en 
# formato UTC a fecha local de MX, usando las librerias pytz y tzlocal.

def convierte_utc_localtime(fecha_utc):
    try:
        zona_horaria =tzlocal.get_localzone()
        localtime = fecha_utc.replace(tzinfo=pytz.utc).astimezone(zona_horaria)
        return str(localtime)        
    except:
        print("Error al convertir fecha.")
        return str(fecha_utc)
