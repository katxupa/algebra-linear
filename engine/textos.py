"""Every text the player can see, per language. Change IDIOMA to switch the whole game.

pt  = português
kea = kriolu (kabuverdianu): review/complete these; missing keys fall back to português.
"""

IDIOMA = "pt"

TEXTOS = {
    "pt": {
        "aula_com_erro": "erro",
        "sem_aulas": "Nenhuma aula encontrada",
        "objetivo_escalonada": "Forma Escalonada",
        "objetivo_reduzida": "Forma Escalonada Reduzida",
        "desfazer": "desfazer",
        "ver_sistema": "sistema",
        "ver_matriz": "matriz",
        "monta_operacao": "monta a operação, ex:",
        "novo": "novo",
    },
    "kea": {
        "aula_com_erro": "eru",
        "sem_aulas": "Ka ten nenhun aula",
        "objetivo_escalonada": "Forma Skalonadu",
        "objetivo_reduzida": "Forma Skalonadu Riduzidu",
        "desfazer": "disfaze",
        "ver_sistema": "sistéma",
        "ver_matriz": "matris",
        "monta_operacao": "monta operason, ex:",
        "novo": "nobu",
    },
}


def t(chave: str) -> str:
    return TEXTOS.get(IDIOMA, {}).get(chave) or TEXTOS["pt"].get(chave, chave)
