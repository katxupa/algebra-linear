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
        "em_breve": "em breve",
        "matriz": "Matriz",
        "m_linha": "Linha",
        "m_coluna": "Coluna",
        "m_quadrada": "Quadrada",
        "m_retangular": "Retangular",
        "diagonal_principal": "Diagonal Principal",
        "tri_sup": "Triangular Superior",
        "tri_inf": "Triangular Inferior",
        "m_diagonal": "Diagonal",
        "m_escalar": "Escalar",
        "m_identidade": "Identidade",
        "m_nula": "Nula",
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
        "em_breve": "ka ta tarda",
    },
}


def t(chave: str) -> str:
    return TEXTOS.get(IDIOMA, {}).get(chave) or TEXTOS["pt"].get(chave, chave)
