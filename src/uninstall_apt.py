#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# uninstall_apt.py

# Este script é chamado pelo pkexec e deve rodar como root.
# Ele REMOVE os pacotes listados em codecs.txt.

import apt
import sys
import os
import subprocess

try:
    import fingerprint
except ImportError as e:
    print(f"ERRO:Falha ao importar o módulo 'fingerprint': {e}", file=sys.stderr)
    sys.exit(1)

def remover_pacotes_apt(lista_de_pacotes: list) -> bool:
    
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


def obter_lista_modificada(filePath: str) -> list:
    try:
        with open(filePath, 'r') as file:
            packages = file.read().splitlines()
    except FileNotFoundError:
        print(f"ERRO: {filePath} não encontrado.", file=sys.stderr)
        return None

    if not packages:
        print("Arquivo de pacotes está vazio.")
        return []

    check_gnome_snapshot = subprocess.run(
        ["dpkg", "-s", "gnome-snapshot"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if check_gnome_snapshot.returncode == 0:
        packages = [pkg for pkg in packages if pkg != "gstreamer1.0-plugins-bad"]
        if not packages:
            print("Lista de pacotes vazia após remover gstreamer1.0-plugins-bad.")

    finger_print_package = fingerprint.verificar_libfprint()
    if finger_print_package:
        packages.append(finger_print_package)

    return packages

if __name__ == "__main__":
    if sys.version_info >= (3, 7):
        sys.stderr.reconfigure(line_buffering=True)

    file_path = "/usr/share/codec-multimedia/codec_multimedia/codecs.txt"

    pacotes_para_remover = obter_lista_modificada(file_path)

    if pacotes_para_remover is not None:
        if not pacotes_para_remover:
             print("ERRO:Lista de pacotes final está vazia.", file=sys.stderr)
             sys.exit(1)

        if remover_pacotes_apt(pacotes_para_remover):
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)
