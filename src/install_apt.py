#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# install_apt.py
# Helper de instalação (executado via pkexec)

import apt
import apt.debfile
import apt_pkg
import sys
import os
import subprocess

try:
    import fingerprint
except ImportError as e:
    print(f"ERRO:Falha ao importar o módulo 'fingerprint': {e}", file=sys.stderr)
    sys.exit(1)


def instalar_pacotes_apt(lista_de_pacotes: list) -> bool:
    try:
        cache = apt.Cache()
        print("INFO:Atualizando cache (apt update)...", file=sys.stderr)
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
        print("INFO:Pacotes APT já estão instalados.", file=sys.stderr)
        return True

    try:
        print(f"INFO:Instalando pacotes APT: {pacotes_a_instalar}", file=sys.stderr)
        cache.commit()
        return True
    except Exception as e:
        print(f"ERRO:Falha na instalação APT: {e}", file=sys.stderr)
        return False

def instalar_pacote_deb(deb_path: str) -> bool:
    try:
        print(f"INFO:Abrindo pacote .deb: {deb_path}", file=sys.stderr)
        deb = apt.debfile.DebPackage(deb_path)
        cache = apt.Cache()
        cache.open(None)

        if deb.pkgname in cache and cache[deb.pkgname].is_installed:
            apt_pkg.init_system()
            versao_instalada = cache[deb.pkgname].installed.version
            versao_deb = deb['Version']
            # Retorna: >0 (se A > B), <0 (se A < B), 0 (se A == B)
            comparacao = apt_pkg.version_compare(versao_deb, versao_instalada)
            if comparacao <= 0:
                print(f"INFO: Pacote {deb.pkgname} (v{versao_instalada}) já está instalado na versão correta ou mais nova.", file=sys.stderr)
                return True

            print(f"INFO: Atualizando {deb.pkgname} de {versao_instalada} para {versao_deb}...", file=sys.stderr)

        print("INFO:Verificando dependências...", file=sys.stderr)
        if not deb.check():
            print("ERRO:Dependências ausentes, tentando resolver com apt-get install -f", file=sys.stderr)
            subprocess.run(["apt-get", "-f", "install", "-y"], check=False)

        print("INFO:Instalando .deb...", file=sys.stderr)
        deb.install()

        print("INFO:Instalação do .deb concluída.", file=sys.stderr)
        return True

    except Exception as e:
        print(f"ERRO:Falha ao instalar o .deb: {e}", file=sys.stderr)
        return False

def download_lib_focal_tech() -> str:
    deb_name = "libfprint-2-2_1.95.4+tod1-0ubuntu1~22.04.2+policorp_amd64_20250714.deb"
    deb_path = f"/tmp/{deb_name}"

    if os.path.exists(deb_path):
        print("INFO:Arquivo .deb já existe em /tmp.", file=sys.stderr)
        return deb_path

    url = f"https://www.policorp.com.br/downloads/{deb_name}"

    try:
        print(f"INFO:Baixando {deb_name}...", file=sys.stderr)
        caminho_salvo = fingerprint.baixar_arquivo(url, "/tmp")

        if caminho_salvo and os.path.exists(caminho_salvo):
            return caminho_salvo
        else:
            print("ERRO:O download falhou (baixar_arquivo não retornou o caminho).", file=sys.stderr)
            return None
    except Exception as e:
        print(f"ERRO:Falha no download: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    if sys.version_info >= (3, 7):
        sys.stderr.reconfigure(line_buffering=True)
        sys.stdout.reconfigure(line_buffering=True)

    try:
        tem_hardware_focal = fingerprint.verificar_focal_tech()
        driver_instalado_correto = fingerprint.verificar_libfprint()
    except Exception as e:
        print(f"ERRO:Falha ao verificar hardware: {e}", file=sys.stderr)
        sys.exit(1)

    if tem_hardware_focal and not driver_instalado_correto:
        deb_path = download_lib_focal_tech()
        if not deb_path:
            print("ERRO:Falha ao baixar o driver Focal Tech.", file=sys.stderr)
            sys.exit(1)

        if not instalar_pacote_deb(deb_path):
            print("ERRO:Falha ao instalar o driver Focal Tech .deb.", file=sys.stderr)
            sys.exit(1)
        print("INFO:Driver Focal Tech .deb instalado com sucesso.", file=sys.stderr)

    elif tem_hardware_focal:
        print("INFO:Driver Focal Tech já está correto, pulando download.", file=sys.stderr)
    else:
        print("INFO:Hardware Focal Tech não detectado, pulando download.", file=sys.stderr)

    caminho_arquivo_codecs = "/usr/share/codec-multimedia/codec_multimedia/codecs.txt"
    try:
        with open(caminho_arquivo_codecs, "r") as f:
            pacotes_apt = [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        print(f"ERRO:{caminho_arquivo_codecs} não encontrado", file=sys.stderr)
        sys.exit(1)

    if not pacotes_apt:
        print("ERRO:codecs.txt está vazio", file=sys.stderr)
        sys.exit(1)

    if instalar_pacotes_apt(pacotes_apt):
        print("INFO:Instalação de codecs APT concluída.", file=sys.stderr)
        sys.exit(0) 
    else:
        print("ERRO:Falha ao instalar pacotes APT.", file=sys.stderr)
        sys.exit(1)
