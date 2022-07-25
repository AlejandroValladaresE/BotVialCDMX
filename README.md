# Repositorio de la aplicación  BotVialCDMX

## Antecedentes
Este proyecto nace de la necesidad de automatizar la documentación, registro y análisis  lo más cercano al tiempo real de  los siniestros de tránsito de la Ciudad de México, con el objetivo de visibilizar la violencia vial que viven los usuarios más vulnerables de la vía pública, y con ello evidenciar que las políticas de movilidad que se han implementado no estan enfocadas en la protección de los más vulnerables. Por #NiUnaMuerteVialMás

Para IAVM.
## Prerrequisitos:

Se sugiere la creación de un entorno virtual con Python 3.9+ para la ejecución de la aplicación. Una vez creado el entorno virtual, instalar a través del archivo requirements.txt las dependencias necesarias para el proyecto
- tweepy
- emoji
- python-dotenv
- pytz
- tzdata
- tzlocal

Ejecutar dentro del entorno virtual:
    > pip install requirements.txt
## Estructura de directorios de la aplicación:



La estructura de directorios de la aplicación es la siguiente:
bot-env/
|
|-- files
|-- config
- lastweet.txt
- last_mention.txt

|-logs
-  botvial.log

| .env
| analizador.py
| botvialbatch.py
| config.py
| mentions.py

## Descripción de  directorios y componentes
**Directorio files**

En este directorio se almacenan los archivos con los eventos recolectados por la aplicación.  La aplicación genera un archivo diario donde se almacenan los eventos, cuyo nombre tiene la siguiente estructura: logcdmxAAAA-MM-DD.csv donde AAAA es el año, MM es el mes y DD es el día en el cual se ejecuta la aplicación.

**Directorio config**

En este directorio se almacenan los archivos de configuración lasttweet.txt y last_mention.txt. El archivo last_tweet.txt sirve como pivote del script botvialbatch.py, almacenando el id del último evento extraido.  El archivo last_mention.txt tiene el mismo objetivo pero para el módulo mentions.py.

**Directorio logs**
Contiene el archivo botvial.log, el cual es el registro de eventos propios de la aplicación mediante el uso del módulo logging de python.

## Componentes
###  .env
Archivo con variables de ambientes para la aplicación, la cual contiene lo siguiente:
- Las claves de consumidor de la aplicación
- Los tokens de acceso de la aplicación.
- el ID de la lista que sirve como el insumo principal de tweets a monitorear por la aplicación.
- 8 listas para identificar los diferentes eventos. Cada lista contiene las diferentes variaciones de palabras que usan los usuarios para describir un evento:
 - fallecidos
 - peaton
 - bicicleta
 - motocicleta
 - atropellado
 - volcadura
 - exclusion
 - lista_accidentes
 - 1 Diccionario para relacionar la alcaldia/provincia donde se suscito el evento.
 		{nombre_alcaldia:cuenta_twitter}

**ejemplo**:
    consumerKey='clave_consumer_key' 
    consumerSecret='clave_consumer_secret' 
    accessToken='clave_access_token'
    accessTokenSecret=''clave_access_token_secret"
    fav='False'
    fallecidos='["muere","fallece","murio", "pierde la vida","perdio la vida"]'
    peaton='["peaton","transeunte","caminante","persona","individuo"]'
    bicicleta = '["ciclista","bicicleta","bici"]'
    motociclista='["motociclista","potro","motero","moto"]'
    atropellado='["atropellada","atropellado","atropellan","atropello","atropellar"]'
    volcadura='["volcadura","volcado","vuelca","volco","volcaron","volcados"]'
    exclusion='["robo","asesinados","asesinado","paf","arma de fuego","asalto","incendio"]'
    lista_accidente = '["choque","percance","impacto","impactado","choco","accidente","accidentado","accidentados","siniestro","incidente","derrapado","derrapo","pega","pego","pegaron"]'
    alcaldias='{ "azcapotzalco": "azcapotzalcomx","alvaro obregon":"alcaldiaao"}'


## config.py
Módulo que almacena las rutinas para:
1. Obtener fecha en formato %Y-%m-%d@%H:%M:%S
1. Crear un objeto API el cual servirá para el acceso a los endpoints de twitter, tomando como argumentos las claves de la aplicación.
1. Rutina para almacenar y obtener los últimos tweets procesados por la aplicación y alojados en los archivos lasttweet.txt y last_mention.txt


## analizador.py
Su función principal es análilzar el texto del status (tweet) para identificar si cumple con las caracteristicas de un siniestro de tránsito, almacenando el evento en el archivo files/logcdmxAAAA-MM-DD.csv corespondiente en caso de ser aceptado.  Sus principales argumentos son: el status (tweet a analizar) y las listas descriptivas de los eventos y sus valores, recuperados del archivo de configuración .env

Su principal salida es el status almacenado  en el archivo *files/logcdmxAAAA-MM-DD.csv* el cual separa con el pipeline ("|") los siguientes atributos:
1. 1.Tweet_ID: Id del tweet
2. Created_at: Fecha de creación en formato UTC local time
3. screen_name: Nombre del usuario que reporto el evento.
4. Texto: Texto del tweet.
5. Fecha_Extraccion: Fecha en la que se ejecuto la aplicación y validó el tweet
6. Hora_Extraccion: Hora en la que se ejecuto la aplicación y validó el tweet
7. atropellado: Indicador si existe un atropellado (1) o no (0)
8. volcadura: Indicador si existe una volcadura (1) o no (0)
9. fallecimiento:  Indicador si existe un fallecimiento (1) o no (0)
10. ciclista:  Indicador si involucro un ciclista (1) o no (0)
11. motociclista:  Indicador si involucro un motociclista (1) o no (0)
12. peaton: :  Indicador si involucro un peaton (1) o no (0)
13. Choque:  Indicador si involucró un choque (1) o no (0)
14. alcaldia: alcaldia/lugar donde se generó el evento.


## botvialbatch.py
Módulo principal de la aplicación.Hace uso del módulo config.py para la creación del objeto API que permitirá la conexión a los endpoints de Twitter, y del módulo analizador para el filtrado de los eventos. Su funcionalidad principal es:
1. Obtener de las variables de ambiente (.env) las claves de la aplicación y las listas con el vocabulario utilizador por el analizador.
1. Se obtiene el último status analizado del archivo lasttweet.txt. Si no existiese, almacena el más reciente que existe en la lista de Twitter.
1. Haciendo uso de la función de tweepy* list_timeline*, se obtienen los eventos más recientes de la lista de Twitter (sin incluir Retweets) a partir del último estatus analizado y almacenado en lasttweet.txt
1. Todos los status obtenidos se envian a analizar al módulo analizador.py


## mentions.py
Módulo secundario de la aplicación. Funciona de manera similar al módulo botvialbatch.py, obteniendo mediante la función* mentions_timeline* de Tweepy las menciones más recientes del timeline, a partir de la última mención almacenada en el archivo last_mention.txt. Se envia a analizar cada status/tweet al módulo analizador.py.