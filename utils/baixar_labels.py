import requests
import json
import os
from pathlib import Path

from utils.func_BPS import autenticar_bps, obter_pdf_etiqueta_bps, listar_todos_parcels
    
# Fluxo principal
def main():
    with open('utils/api_google_driver/configs.json', 'r', encoding='utf-8') as file:
        dados = json.load(file)
    caminho_da_pasta = Path(dados['local_folder_path'])
    arquivos = [arquivo.name for arquivo in caminho_da_pasta.iterdir() if arquivo.is_file()]


    token = autenticar_bps()
    if token:
        lista_parcels_id = listar_todos_parcels(token, 'processed')
        for parcel in lista_parcels_id:

            if parcel['codigo_rastreio']:
                nome_arquivo = parcel['codigo_rastreio']
                if parcel['id'] in arquivos:
                    print(f'Etiqueta {parcel['id']}.pdf mudou para {nome_arquivo}.pdf')
                    os.remove(f'{dados['local_folder_path']}{parcel_id}.pdf')          
            else:
                nome_arquivo = parcel['id']

            if f'{nome_arquivo}.pdf' in arquivos:
                # print('etiqueta já baixada')
                continue

            arquivo = f"{dados['local_folder_path']}{nome_arquivo}.pdf"
            etiqueta = obter_pdf_etiqueta_bps(token, parcel_id=parcel['id'])  # ID do pacote real
            
            if etiqueta:
                print("etiqueta baixada", nome_arquivo)
                with open(arquivo, 'wb') as arq:
                    arq.write(etiqueta)
        
if __name__ == "__main__":
    # from func_BPS import autenticar_bps, obter_pdf_etiqueta_bps, listar_todos_parcels

    # main()
    with open('utils/api_google_driver/configs.json', 'r', encoding='utf-8') as file:
        dados = json.load(file)
    print(f"{dados['local_folder_path']}/wwww.pdf")
