#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Este script é chamado pelo pkexec e deve rodar como root.
# Ele foi simplificado para NÃO reportar progresso (stdout),
# mas DEVE reportar erros (stderr).

import apt
import sys
import os

def instalar_pacotes_apt(lista_de_pacotes: list) -> bool:
    """
    Tenta instalar uma lista de pacotes.
    Retorna True em sucesso, False em falha.
    Imprime erros no stderr.
    """

    try:
        cache = apt.Cache()
        cache.update()
        cache.open(None)
    except Exception as e:
        print(f"ERRO:Falha ao abrir/atualizar cache: {e}", file=sys.stderr)
        return False

    pacotes_a_instalar = []
    
    for pkg_name in lista_de_pacotes:
        try:
            pkg = cache[pkg_name]
            if not pkg.is_installed:
                pkg.mark_install()
                pacotes_a_instalar.append(pkg_name)
        except KeyError:
            print(f"ERRO:Pacote '{pkg_name}' não encontrado", file=sys.stderr)
            return False

    if not pacotes_a_instalar:
        return True

    try:
        cache.commit()
        return True
    except Exception as e:
        print(f"ERRO:Falha na instalação: {e}", file=sys.stderr)
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

    if instalar_pacotes_apt(pacotes):
        sys.exit(0) 
    else:
        sys.exit(1) 
