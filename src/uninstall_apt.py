#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Este script é chamado pelo pkexec e deve rodar como root.
# Ele REMOVE os pacotes listados em codecs.txt.

import apt
import sys
import os

def remover_pacotes_apt(lista_de_pacotes: list) -> bool:
    """
    Tenta remover uma lista de pacotes usando python-apt.
    Retorna True em sucesso, False em falha.
    Imprime erros no stderr.
    """
    
    if os.geteuid() != 0:
        print("ERRO:Este script deve ser executado como root", file=sys.stderr)
        return False

    try:
        cache = apt.Cache()
        cache.open(None)
    except Exception as e:
        print(f"ERRO:Falha ao abrir o cache: {e}", file=sys.stderr)
        return False

    pacotes_a_remover = []
    
    for pkg_name in lista_de_pacotes:
        try:
            pkg = cache[pkg_name]
            if pkg.is_installed:
                pkg.mark_delete()
                pacotes_a_remover.append(pkg_name)
        except KeyError:
            print(f"AVISO:Pacote '{pkg_name}' não encontrado, ignorando.", file=sys.stderr)
            pass 

    if not pacotes_a_remover:
        print("INFO:Nenhum dos pacotes estava instalado.", file=sys.stderr)
        return True

    try:
        cache.commit()
        return True
    except Exception as e:
        print(f"ERRO:Falha na remoção: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if sys.version_info >= (3, 7):
        sys.stderr.reconfigure(line_buffering=True)

    caminho_arquivo = "/usr/share/codec-multimedia/codec_multimedia/codecs.txt"

    try:
        with open(caminho_arquivo, "r") as f:
            pacotes = [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        print(f"ERRO:{caminho_arquivo} não encontrado", file=sys.stderr)
        sys.exit(1)

    if not pacotes:
        print("ERRO:codecs.txt está vazio", file=sys.stderr)
        sys.exit(1)

    if remover_pacotes_apt(pacotes):
        sys.exit(0) 
    else:
        sys.exit(1)
