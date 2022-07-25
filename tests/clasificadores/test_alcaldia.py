from clasificadores.alcaldia import Alcaldía, identifica_alcaldia

def test_ejemplo_sencillo_1():
    alcaldía = identifica_alcaldia("BJ")
    assert(alcaldía == Alcaldía.BenitoJuárez)

def test_ejemplo_sencillo_2():
    alcaldía = identifica_alcaldia("Benito Juárez")
    assert(alcaldía == Alcaldía.BenitoJuárez)

def test_ejemplo_sencillo_3():
    alcaldía = identifica_alcaldia("benito juarez")
    assert(alcaldía == Alcaldía.BenitoJuárez)

def test_ejemplo_enmedio_texto():
    alcaldía = identifica_alcaldia("Puede haber mucho texto BJ pero encontrar la alcaldía enmedio.")
    assert(alcaldía == Alcaldía.BenitoJuárez)
