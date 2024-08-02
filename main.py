#import padrao
import sys
import os
from datetime import datetime
from pathlib import Path
import json
import traceback

#Import variavel

#import de funçoes
from utils.baixar_labels import main as baixar_labels
from utils.api_google_driver.pegar_lista_driver import main as sincronizar_labels
from utils.Procurar_e_colocar_etiquetas import main as Proc_coloc_etiqueta_main
from utils.Colocar_Rastreio_no_tiny import main as Coloc_Rastreio_main 


data_agr = datetime.now()
# Coloc_Etiqueta_main()

def log_erro(erro, func):
    stack_trace = traceback.format_exc()
    print(f'Stack trace:\n{stack_trace}\nErro em {func}: {erro}')
    with open('log.txt', 'a') as arq:
        arq.write(f'Erro em {func}:{erro}  -- {data_agr}\n \
            traceback:{stack_trace}\n------------------------------------------\n')

if __name__ == '__main__':
    try:
        Coloc_Rastreio_main()
    except Exception as erro:
        log_erro(erro, 'Coloc_Rastreio')
        
    try:
        baixar_labels()
        
    except Exception as erro:
        log_erro(erro, 'baixar_labels')

    try:
        with open('utils/api_google_driver/configs.json', 'r', encoding='utf-8') as file:
            dados = json.load(file)
        caminho_da_pasta = Path(dados['local_folder_path'])
        arquivos = [arquivo.name for arquivo in caminho_da_pasta.iterdir() if arquivo.is_file()]

        eita = sincronizar_labels()
        lista = eita.list_files_driver()['all']
        for nome_arquivo in arquivos:
            pular = False
            for arquivo_driver in lista:
                if nome_arquivo == arquivo_driver['name'] and nome_arquivo != 'sync.log':
                    print('pulou')
                    pular = True
            if nome_arquivo.startswith(".") or pular:
                continue
            eita.upload_file_driver(nome_arquivo)
        
    except Exception as erro:
        log_erro(erro, 'upload_file_driver')

    try:
        Proc_coloc_etiqueta_main()
    except Exception as erro:
        log_erro(erro, 'Procurar_e_colocar_etiquetas')
