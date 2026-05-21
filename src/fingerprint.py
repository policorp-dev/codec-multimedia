#!/usr/bin/python3
import subprocess
import re
import requests
import os
from time import sleep
import json

def verificar_focal_tech():
    # IDs de Vendor (VID) e Produto (PID) a serem verificados
    vid_focal_tech = "2808"
    pids_focal_tech = ["9338", "d979", "c652", "a959", "0579"]

    try:
        print("Executando 'lsusb' para verificar dispositivos...")
        resultado = subprocess.run(
            ["lsusb"],
            capture_output=True,
            text=True,
            check=True
        )
        saida_lsusb = resultado.stdout
        print("Saída do comando 'lsusb' obtida com sucesso.")

        pattern = re.compile(
            f"ID\\s+{vid_focal_tech}:({'|'.join(pids_focal_tech)})",
            re.IGNORECASE
        )

        matches = pattern.finditer(saida_lsusb)

        encontrado = False
        for match in matches:
            pid_encontrado = match.group(1).upper()
            print(f"Hardware Focal Tech encontrado! VID: {vid_focal_tech}, PID: {pid_encontrado}")
            encontrado = True

        if not encontrado:
            print("Nenhum hardware Focal Tech com os IDs especificados foi encontrado.")
            return False

        return True

    except FileNotFoundError:
        print("Erro: O comando 'lsusb' não foi encontrado. Certifique-se de que o pacote usbutils está instalado.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar 'lsusb': {e}")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return False


def verificar_libfprint(versao_alvo=None):
    if not versao_alvo:
        versao_alvo = "1:1.95.4+tod1-0ubuntu1~22.04.2+policorp"

    try:
        resultado = subprocess.check_output(["dpkg", "-l"], text=True)

        for linha in resultado.splitlines():
            if "libfprint-2-2" in linha and linha.startswith("ii"):
                partes = linha.split()
                nome_pacote_completo = partes[1]
                versao_instalada = partes[2]

                nome_pacote = nome_pacote_completo.split(":")[0]

                if versao_instalada == versao_alvo:
                    return nome_pacote  # Retorna "libfprint-2-2"
                else:
                    return None

        return None

    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar dpkg: {e}")
        return None


def baixar_arquivo(url, destino, tentativas=3, timeout=20):
    if os.path.isdir(destino):
        destino = os.path.join(destino, url.split("/")[-1])
    else:
        os.makedirs(os.path.dirname(destino), exist_ok=True)

    for tentativa in range(1, tentativas + 1):
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                tamanho_total = int(r.headers.get("content-length", 0))
                baixado = 0

                with open(destino, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            baixado += len(chunk)

                            if tamanho_total:
                                pct = (baixado / tamanho_total) * 100
                                print(
                                    f"\rBaixando: {pct:6.2f}% "
                                    f"({baixado/1024/1024:.2f}MB / {tamanho_total/1024/1024:.2f}MB)",
                                    end="",
                                    flush=True
                                )

            print(f"\nDownload concluído: {destino}")
            return destino

        except Exception as e:
            print(f"\nTentativa {tentativa} falhou: {e}")
            if tentativa < tentativas:
                print("Tentando novamente em 5s...")
                sleep(5)

    print("Falha no download após várias tentativas.")
    return None


def get_latest_package_info(package_name: str) -> dict:
    """
    Busca o arquivo packages.json remoto e retorna as informações do pacote solicitado.
    """
    url = "https://www.policorp.com.br/downloads/codec-multimedia-packages.json"
    #url = "http://localhost:8000/src/codec-multimedia-packages.json"
    try:
        print(f"INFO:Buscando informações atualizadas em {url}...", flush=True)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        info = data.get(package_name)
        if not info:
            print(f"AVISO:Pacote '{package_name}' não encontrado no JSON remoto.")
        return info
    except Exception as e:
        print(f"ERRO:Falha ao obter informações dos pacotes via JSON: {e}")
        return None


