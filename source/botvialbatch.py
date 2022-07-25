#Este módulo tiene el objetivo de obtener los tuits mas recinentes de la lista "AccidentesViales_CDMX". Usa el modulo analizador.py para
# evaluar y calificar el evento en el log de eventos
# Las principales actividades son: 
#       - Obtener del archivo .env las claves de acceso a la API de Twitter, el ID de la lista de twitter a dare seguimiento, asi las listas/diccionarios con los eventos que analizaran el texto del tuit.
#        -A partir del último ID que se encuentra alojado en el archivo config/lasttweet.txt, se extraen todos los tuis de la lista de tuiter con un ID >.

from cgitb import text
import tweepy
from dotenv import load_dotenv, find_dotenv
import os
from config import create_api, obten_fecha, obten_last_tweet, guarda_last_tweet
from analizador import analiza_evento, busca_evento
import logging
from time import sleep
import time
import json
logging.basicConfig(filename='Documentos/EntornoBot/logs/botvial.log',level=logging.INFO)
#logging.basicConfig(filename='~/Documentos/EntornoBot/logs/botvial.log',level=logging.INFO)
nombre_modulo = "botvialbatch.py"

def main():
    try:
        load_dotenv()
        cKey=os.environ.get('consumerKey')
        cSecret=os.environ.get('consumerSecret')
        aToken=os.environ.get('accessToken')
        aTokenSecret=os.environ.get('accessTokenSecret')
      #obtenemos el id de la lista de la cual vamos a recolectar eventos.
        lista=os.environ.get('list_id')
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
        fecha = obten_fecha()
        logging.info(fecha + " "  + nombre_modulo + " "+ "Inicia Botvial.py")
        try:
            logging.info(fecha + " "  + nombre_modulo + " "+ "inicia creación de API")
            api = create_api(cKey,cSecret,aToken,aTokenSecret)
            logging.info(fecha + " "  + nombre_modulo + " "+ "Termina creación de API")
            # Se recuperan todos los tuits desde el utlimo tuit guardado en el arhcivo ./config/lasttweet.txt hasta el momento de la ejecución.
            # en caso de no existir último tuit guardado (1er ejecución), se almace el más reciente de la lista.
            try:
                last_tweet_file = "lasttweet.txt"               
                id = obten_last_tweet(last_tweet_file)
                print("Ultimo tuit:", id)
                if id == 0:
                    print("Sin tuits previos, obtenemos el mas reciente:")                    
                    tweets_list = api.list_timeline(list_id=lista, count=1, include_entities=False, include_rts=False)
                    for tweet in tweets_list:
                        id = tweet.id                        
                        guarda_last_tweet(id,last_tweet_file)                    
                    logging.info(fecha + " " + "Sin tuits previos. Se inicia extracción a partir de ID:" + str(id) + " Screen Name:" + tweet.user.screen_name)
                # a partir del ultimo tuit, comenzamos la recolección de eventos.
                try:
                    tweets_list = api.list_timeline(list_id=lista,since_id = id, count=200 ,tweet_mode = 'extended', include_entities=False, include_rts=False)                    
                    contador_tweets = 1
                    aceptados = 0
                    logging.info(fecha + " " + "Inicio Extracción con ID > a: " + str(id))                    
                    for tweet in reversed(tweets_list):
                        id = tweet.id
                        # el primer tuit leido es el más reciente, por lo que es el que se almacena como el último procesado.
                        if contador_tweets == len(tweets_list):                        
                            guarda_last_tweet(id,last_tweet_file)
                            print("Ultimo estado:", str(tweet.id) + "user:" + str(tweet.user.screen_name))
                            logging.info(fecha + nombre_modulo + " " + "El ultimo estado extraido es: " + str(id) + str(tweet.user.screen_name))
                        contador_tweets+=1
                        # se valida el tuit en el módulo analiza.py para identificar si cumple con los criterios de procesamiento.
                        # Si cumple, la funcion responde con exitoso (1), si no,(0)
                        eventos_ok = analiza_evento(tweet,list_fallecidos,list_peaton,list_bicicleta,list_motocicleta,list_atropellado,list_volcadura,dict_alcaldia,list_accidente,list_exclusiones)
                        # Si el evento fue aceptado, se devuelve la lista con los eventos identificados para armar el texto del estatus
                        if len(eventos_ok) > 0:
                            aceptados+=1                        
                            status_text = " @muertevialcdmx #HechoVialCDMX "
                            if eventos_ok[6] == 1:
                                status_text += "#AtropelladoCDMX "
                            if eventos_ok[7] == 1:
                                status_text += "#VolcaduraCDMX "
                            if eventos_ok[8] == 1:
                                status_text += "#MuerteVialCDMX DEP"
                            print("Estado a actualizar: " + status_text)
                            logging.info(fecha + nombre_modulo +  " " + "Estado Aceptado:" + str(id))
                            # try:
                            #     fav = api.create_favorite(id = id, include_entities = False)
                            #     logging.info(fecha + " " + "Favorito creado exitosamente:" + str(fav.id))
                            #     try: 
                            #         new_status = api.update_status(status = status_text, in_reply_to_status_id = id, auto_populate_reply_metadata = True)
                            #         logging.info(fecha + " " + "Estatus creado exitosamente:" + str(new_status.id))
                            
                            #     except Exception as e:
                            #         logging.info(fecha + " " + "Error al generar leyenda para este tuit:" + str(id))
                            #         print(e)
                            # except Exception as e:
                            #     logging.info(fecha + " " + "Error al marcar como favorito este tuit:" + str(id))
                            #     print(e)                            
                    leidos = len(tweets_list)
                    logging.info(fecha + nombre_modulo + " Termino extraccion. Leidos:" + str(leidos) + ". Aceptados: " + str(aceptados))
                except Exception as e:
                    logging.error(fecha + " "  + nombre_modulo + " " + "Error al obtener ultimo evento." , exc_info=True)
                    print(e)       
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
