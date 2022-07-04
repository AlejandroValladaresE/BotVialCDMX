# Bot para registro de incidentes viales
# Modulo para manejo y registro de menciones
#https://twitter.com/statuses/status/

from itertools import count
from sys import api_version
import tweepy
from dotenv import load_dotenv, find_dotenv
import os
import json
from config import create_api, obten_fecha, obten_last_tweet, guarda_last_tweet
from analizador import analiza_evento, busca_evento
import logging

logging.basicConfig(filename='Documentos/EntornoBot/logs/botvial.log',level=logging.INFO)
#logging.basicConfig(filename='~/Documentos/EntornoBot/logs/botvial.log',level=logging.INFO)
nombre_modulo = "mentions.py"

def main():
    try:
        load_dotenv()
        cKey=os.environ.get('consumerKey')
        cSecret=os.environ.get('consumerSecret')
        aToken=os.environ.get('accessToken')
        aTokenSecret=os.environ.get('accessTokenSecret')
        create_fav = os.environ.get('fav')
        #obtenemos las listas de nuestros diccionarios que serviran como filtro del módulo analizador.py. Se pasan como argumentos en la funcion analiza_evento()
        list_fallecidos = []
        list_peaton = []
        list_bicicleta= []
        list_motocicleta= []
        list_atropellado= []
        list_volcadura= []
        list_accidente= []
        list_exclusiones = []
        dict_alcaldia = {}
        list_fallecidos = json.loads(os.environ.get('fallecidos'))
        list_peaton = json.loads(os.environ.get('peaton'))
        list_bicicleta = json.loads(os.environ.get('bicicleta'))
        list_motocicleta = json.loads(os.environ.get('motociclista'))
        list_atropellado = json.loads(os.environ.get('atropellado'))
        list_volcadura = json.loads(os.environ.get('volcadura'))
        list_accidente = json.loads(os.environ.get('lista_accidente'))
        list_exclusiones = json.loads(os.environ.get('exclusion'))
        dict_alcaldia = json.loads(os.environ.get('alcaldias'))
        fecha = obten_fecha()
        logging.info(fecha + " "  + nombre_modulo + " "+ "Inicia mentions.py")
        try:
            logging.info(fecha + " "  + nombre_modulo + " "+ "inicia creación de API")
            api = create_api(cKey,cSecret,aToken,aTokenSecret)
            logging.info(fecha + " "  + nombre_modulo + " "+ "Termina creación de API")
            # Se recuperan todos los tuits desde el utlimo tuit guardado en el arhcivo ./config/last_mention.txt hasta el momento de la ejecución.
            # en caso de no existir último tuit guardado (1er ejecución), se almace el más reciente de la lista.
            try:
                archivo = 'last_mention.txt'                
                id = obten_last_tweet(archivo)
                logging.info(fecha + " " + nombre_modulo + " Inicio extraccion de menciones desde: " + str(id))
                if id == 0:
                    menciones = api.mentions_timeline(count=500,tweet_mode = 'extended', include_entities=False)
                else:
                    menciones = api.mentions_timeline(count=500,since_id = id, tweet_mode = 'extended', include_entities=False)
                total_menciones = len(menciones)
                contador_menciones = 0
                aceptados = 0
                fav_created = 0
                #Si existen menciones, se procesan.
                if total_menciones > 0:
                    for mencion in reversed(menciones):                    
                        contador_menciones +=1
                        id = mencion.id 
                        #Se identifica si se incluyo la referencia en un tweet citado o como parte de una respuesta
                        if mencion.is_quote_status:
                            id_origen = mencion.quoted_status_id
                        else:
                            id_origen = mencion.in_reply_to_status_id
                        #se obtiene el tweet original, el cual se analizara para identificar criterios de aceptacion
                        try:
                            tweet = api.get_status(id = id_origen, include_my_retweet = False, tweet_mode = 'extended')    
                            eventos_ok = analiza_evento(tweet,list_fallecidos,list_peaton,list_bicicleta,list_motocicleta,list_atropellado,list_volcadura,dict_alcaldia,list_accidente,list_exclusiones)
                            if len(eventos_ok) >0 :
                                aceptados+=1
                                logging.info(fecha + " " + nombre_modulo + " Estado Aceptado: " + str(id))
                                guarda_last_tweet(id,archivo)
                                if create_fav == 'True':
                                    try:
                                        print("Creando favorito")
                                        fav = api.create_favorite(id=tweet.id)
                                        print("ID del favorito", str(fav.id))
                                        logging.info(fecha + " " + nombre_modulo + " Favorito creado exitosamente: " + str(fav.id))
                                    except Exception as e:
                                        logging.error(fecha + " " + nombre_modulo + " Error al crear favorito. ",exc_info=True)
                                        print (e)
                        except Exception as e:
                            logging.error(fecha + " " + nombre_modulo + " Error recuperar el tuit solicitado... " + str(id_origen),exc_info=True)                    
                    logging.info(fecha + " " + nombre_modulo + " Ultima mencion guardada: " + str(id) ) 
                    logging.info(fecha + " " + nombre_modulo + " Favoritos Leidos: " + str(len(menciones)) + " Aceptados: " + str(aceptados))    
                else:
                    logging.info(fecha + " " + nombre_modulo + " Sin menciones o nuevas respuestas. ")
            except Exception as e:
                logging.info(fecha + " "  + nombre_modulo + " "+ "Error al acceder a los tuits de la lista")
                print(e)
        except Exception as e:
            fecha = obten_fecha()
            logging.error(fecha + " "  + nombre_modulo + " " + "Error al crear la API", exc_info=True)
            print(e)
    except Exception as e:
        logging.error(fecha + " "  + nombre_modulo + " "+ "Error al cargar variables de ambiente", exc_info=True)
        print(e)

if __name__ == "__main__":
    main()



