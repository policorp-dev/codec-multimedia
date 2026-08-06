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

            print("INFO: (Etapa 3/3) Atualizando cache (apt update)...", file=sys.stderr)
            try:
                cache.update(raise_on_error=True)
            except apt.cache.FetchFailedException as e:
                print(f"ERRO: Falha ao baixar listas (apt update): {e}", file=sys.stderr)
                return False

            cache.open(None)
            pacotes_a_instalar = []

            for pkg_name in lista_de_pacotes:
                try:
                    pkg = cache[pkg_name]
                    if not pkg.is_installed:
                        pkg.mark_install()
                        pacotes_a_instalar.append(pkg_name)
                except KeyError:
                    print(f"ERRO: Pacote '{pkg_name}' não encontrado", file=sys.stderr)
                    return False

            if not pacotes_a_instalar:
                print("INFO: Pacotes APT já estão instalados.", file=sys.stderr)
                return True

            print(f"INFO: (Etapa 3/3) Instalando pacotes APT: {pacotes_a_instalar}", file=sys.stderr)

            cache.commit()
            return True

    except apt.cache.LockFailedException as e:
        print(f"ERRO: O APT já está em uso por outro processo (lock). Tente novamente. Detalhe: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERRO: Falha inesperada na instalação APT (mesmo após correções): {e}", file=sys.stderr)
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

def download_lib_focal_tech(pkg_info: dict) -> str:
    if not pkg_info:
        print("ERRO:Informações do pacote não fornecidas para download.", file=sys.stderr)
        return None

    deb_name = pkg_info.get("filename")
    url = pkg_info.get("url")

    if not deb_name or not url:
        print("ERRO:Informações do pacote incompletas no JSON (filename ou url ausente).", file=sys.stderr)
        return None

    deb_path = f"/tmp/{deb_name}"

    if os.path.exists(deb_path):
        print(f"INFO:Arquivo {deb_name} já existe em /tmp.", file=sys.stderr)
        return deb_path

    try:
        print(f"INFO:Baixando {deb_name} de {url}...", file=sys.stderr)
        caminho_salvo = fingerprint.baixar_arquivo(url, "/tmp")

        if caminho_salvo and os.path.exists(caminho_salvo):
            print(f"INFO:Pacote salvo em {caminho_salvo}", file=sys.stderr)
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
        pkg_info = fingerprint.get_latest_package_info("libfprint-2-2")
        versao_alvo = fingerprint.extrair_versao_do_filename(pkg_info.get("filename")) if pkg_info else None
        
        tem_hardware_focal = fingerprint.verificar_focal_tech()
        driver_instalado_correto = fingerprint.verificar_libfprint(versao_alvo)
    except Exception as e:
        print(f"ERRO:Falha ao verificar hardware ou obter informações do pacote: {e}", file=sys.stderr)
        sys.exit(1)

    if tem_hardware_focal and not driver_instalado_correto:
        if not pkg_info:
            print("ERRO:Hardware Focal Tech detectado, mas não foi possível obter informações do driver via JSON.", file=sys.stderr)
            sys.exit(1)
            
        deb_path = download_lib_focal_tech(pkg_info)
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
