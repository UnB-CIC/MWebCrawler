#  -*- coding: utf-8 -*-
#       @file: utils.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Utilidades.

from requests import get as busca
from requests.exceptions import RequestException as RequestException
from re import findall as encontra_padrao


# Construção de links para o Matrícula Web.
mweb = lambda nivel: 'https://matriculaweb.unb.br/' + str(nivel)
link = lambda pagina, cod: str(pagina) + '.aspx?cod=' + str(cod)
url_mweb = lambda nivel, pagina, cod: mweb(nivel) + '/' + link(pagina, cod)


# Códigos dos campi
DARCY_RIBEIRO = 1
PLANALTINA = 2
CEILANDIA = 3
GAMA = 4
