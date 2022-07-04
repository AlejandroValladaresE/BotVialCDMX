import tweepy
from dotenv import load_dotenv
from datetime import datetime
import logging

logging.basicConfig(filename='Documentos/EntornoBot/logs/botvial.log',level=logging.INFO)
#logging.basicConfig(filename='~/Documentos/EntornoBot/logs/botvial.log',level=logging.INFO)
nombre_modulo = "config.py"
def obten_fecha():
    fecha = datetime.today().strftime('%Y-%m-%d@%H:%M:%S')
    return fecha

#función create_api: utilizando las llaves cargas de variables de ambiente,
#se crea un objeto API utilizando la api de twitter para poder realizar
#solicitudes
def create_api(cons_key,cons_secret,access_tkn, access_tkn_secret):
    ## obtenemos las llaves de acceso de variables de ambiente
    
    cKey= cons_key
    cSecret=cons_secret
    aToken=access_tkn
    aTokenSecret=access_tkn_secret
    # se crea objetoos para autenticarse con la API de twitter
    auth = tweepy.OAuthHandler(cKey,cSecret)
    auth.set_access_token(aToken,aTokenSecret)
    # se crea el objeto API de twitter
    api = tweepy.API(auth,wait_on_rate_limit = True,)
    try:
        api.verify_credentials()
    except Exception as e:
        fec_format = obten_fecha()
        logging.error(fec_format + " " + nombre_modulo + " " + "Error al crear la API", exc_info=True)
        raise e
    fec_format = obten_fecha()
    logging.info(fec_format + " " + nombre_modulo + " " + "API creada exitosamente!")
    return api

# Esta funcion se encarga de obtener el ultimo tuit registrado en la corrida previa del programa
def obten_last_tweet(file):
    ruta = 'Documentos/EntornoBot/config/' + file
    try:
        with open(ruta,'r') as ltfile:
            last_tweet = ltfile.read()
            if len(last_tweet) == 0:
                last_tweet = 0
    except Exception as e:
        last_tweet = 0
        print(e)     
    return last_tweet
#esta funcion se encarga de almacenar el ultimo tuit del timenline de la lista de trabajo que será
#  el pivote para la recolección de los eventos
def guarda_last_tweet(tuit_id,file):
    datos = str(tuit_id)
    ruta = 'Documentos/EntornoBot/config/' + file
    try:
        #print("Tuit a gurdar:", tuit_id)
        with open(ruta,'w') as ltfile:
            ltfile.write(datos)
        resultado = 1
    except Exception as e:
        resultado = 0
        print(e)    
    return resultado

