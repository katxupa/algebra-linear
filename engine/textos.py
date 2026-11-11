"""Every text the player can see, per language. Change IDIOMA to switch the whole game.

pt  = português
kea = kriolu (kabuverdianu): review/complete these; missing keys fall back to português.
"""

IDIOMA = "pt"

TEXTOS = {
    "pt": {
        "aula_com_erro": "erro",
        "sem_aulas": "Nenhuma aula encontrada",
    },
    "kea": {
        "aula_com_erro": "eru",
        "sem_aulas": "Ka ten nenhun aula",
    },
}


def t(chave: str) -> str:
    return TEXTOS.get(IDIOMA, {}).get(chave) or TEXTOS["pt"].get(chave, chave)
