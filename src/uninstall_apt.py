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
    try:
        print("INFO: (Etapa 1/2) Verificando e corrigindo 'dpkg' (dpkg --configure -a)...", file=sys.stderr)

        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"

        result_dpkg = subprocess.run(
            ["dpkg", "--configure", "-a"],
            check=False,
            capture_output=True,
            text=True,
            env=env
        )

        if result_dpkg.returncode != 0:
            print(f"AVISO: 'dpkg --configure -a' reportou problemas (provavelmente dependências, o que é esperado).", file=sys.stderr)
            print(f"Detalhe: {result_dpkg.stderr}", file=sys.stderr)
        else:
            print("INFO: 'dpkg' verificado/corrigido.", file=sys.stderr)

    except Exception as e_fix:
        print(f"ERRO: Falha ao tentar executar 'dpkg --configure -a' via subprocess: {e_fix}", file=sys.stderr)
        return False

    try:
        with apt.Cache() as cache_fix:

            print("INFO: (Etapa 2/2) Atualizando cache para o 'fix-broken'...", file=sys.stderr)
            try:
                cache_fix.update(raise_on_error=True)
            except apt.cache.FetchFailedException as e_update:
                print(f"ERRO: Falha ao baixar listas para o 'fix-broken': {e_update}", file=sys.stderr)
                return False

            cache_fix.open(None)

            if cache_fix.broken_count > 0:
                print("INFO: (Etapa 2/2) Detectadas dependências quebradas. Corrigindo (apt --fix-broken)...", file=sys.stderr)

                cache_fix.fix_broken()

                try:
                    print("INFO: (Etapa 2/2) Aplicando as correções (commit)...", file=sys.stderr)
                    cache_fix.commit()
                except Exception as e_commit:
                    print(f"ERRO: Falha durante o 'commit' da correção: {e_commit}", file=sys.stderr)
                    return False

                cache_fix.open(None)

                if cache_fix.broken_count == 0:
                     print("INFO: Dependências corrigidas com sucesso.", file=sys.stderr)
                else:
                    print("ERRO: O 'fix_broken() + commit()' foi executado, mas o sistema ainda reporta pacotes quebrados. Abortando.", file=sys.stderr)
                    return False
            else:
                print("INFO: (Etapa 2/2) Nenhuma dependência quebrada encontrada.", file=sys.stderr)

    except apt.cache.LockFailedException as e:
        print(f"ERRO: O APT estava em uso ao tentar corrigir dependências (fix-broken): {e}", file=sys.stderr)
        return False
    except Exception as e_fix:
        print(f"ERRO: Falha crítica ao tentar executar 'fix_broken()': {e_fix}", file=sys.stderr)
        return False

    try:
        with apt.Cache() as cache:
            cache.open(None)

            print("INFO: (Etapa 3/3) Marcando pacotes para remoção...", file=sys.stderr)
            pacotes_a_remover = []

            for pkg_name in lista_de_pacotes:
                try:
                    pkg = cache[pkg_name]
                    if pkg.is_installed:
                        pkg.mark_delete()
                        pacotes_a_remover.append(pkg_name)
                except KeyError:
                    print(f"AVISO: Pacote '{pkg_name}' não encontrado, ignorando.", file=sys.stderr)
                    pass

            if not pacotes_a_remover:
                print("INFO: Nenhum dos pacotes estava instalado.", file=sys.stderr)
                return True

            print(f"INFO: (Etapa 3/3) Removendo pacotes APT: {pacotes_a_remover}", file=sys.stderr)

            cache.commit()
            return True

    except apt.cache.LockFailedException as e:
        print(f"ERRO: O APT já está em uso por outro processo (lock) durante a remoção. Tente novamente. Detalhe: {e}", file=sys.stderr)
        return False

    except Exception as e:
        print(f"ERRO: Falha inesperada na remoção APT (mesmo após correções): {e}", file=sys.stderr)
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
