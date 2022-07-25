import csv
import os
import re

from enum import Enum
from typing import Dict, Optional

class Alcaldía(Enum):
    Azcapotzalco       = "AZC"
    ÁlvaroObregón      = "AOB"
    BenitoJuárez       = "BJU"
    Coyoacán           = "COY"
    Cuajimalpa         = "CUJ"
    Cuauhtémoc         = "CUH"
    GustavoAMadero     = "GAM"
    Iztacalco          = "IZC"
    Iztapalapa         = "IZP"
    MagdalenaContreras = "MAC"
    MiguelHidalgo      = "MIH"
    MilpaAlta          = "MLP"
    Tláhuac            = "TLH"
    Tlalpan            = "TLP"
    VenustianoCarranza = "VCA"
    Xochimilco         = "XOC"

alcaldias: Dict[str, Alcaldía] = dict()

# Carga los datos de textos que representen alcladias
_csv_alcaldias_ubicacion: str = os.environ.get("CSV_ALCALDIAS", "recursos/alcaldias.csv")
with open(_csv_alcaldias_ubicacion) as archivo:
    lector = csv.DictReader(archivo)
    for fila in lector:
        alcaldias[fila["texto"].lower()] = Alcaldía(fila["alcaldía"])

def identifica_alcaldia(texto) -> Optional[Alcaldía]:
    '''
    Función para identificar si dentro del texto del tuit se reconoce la alcaldia
    donde se genero el evento.
    '''

    # Es posible que haya más de un texto de alcaldía
    posibles_alcaldias = set([ alcaldias[clave] for clave in alcaldias.keys() if re.search(clave, texto.lower()) ])

    # Solo regresa cuando hay una sola posible alcaldía
    if(len(posibles_alcaldias) == 1):
        return posibles_alcaldias.pop()
    else:
        return None
