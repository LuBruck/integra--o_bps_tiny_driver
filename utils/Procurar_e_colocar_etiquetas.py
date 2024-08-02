import requests
import json
from datetime import datetime
import sys
import os
# sys.path.append(os.path.join(os.path.dirname(__file__), 'api_google_driver/'))

from utils.api_google_driver.pegar_lista_driver import main as listar_e_enviar_driver
from utils.func_BPS import autenticar_bps, listar_todos_parcels
from utils.func_Tiny import enviar_url_etiqueta_para_tiny, lista_pedidos_tiny


#Fluxo principal 
def main():
    """Pega todos os pedidos do tiny que estão em 'preparando para envio', e
    coloca a url da etiqueta no campo de obs.
     """

    pedidos_preparando_tiny = []
    pedidos_parcel = []
    token = autenticar_bps()
    chaves_verificar = ['data_pedido', 'nome', 'cpf_cnpj']
    my_driver = listar_e_enviar_driver()
    lista_all = my_driver.list_files_driver()['all']
    lista_driver = []

    if token:
        pedidos_parcel = listar_todos_parcels(token, 'processed')
        pedidos_preparando_tiny = lista_pedidos_tiny(data_inicial='01/01/2024') #situacao="preparando_envio"


        for pedido_tiny in pedidos_preparando_tiny:
            itens_comum = {}
            # print(itens_comum)
            for pedido_parcel in pedidos_parcel:
                # print(pedido_parcel)
                for key, values in pedido_tiny.items() :
                    if key in pedido_tiny and pedido_parcel[key] == values:
                        itens_comum[key] = values
                        novos_itens = {
                            'id_parcel' : pedido_parcel['id'],
                            'id_tiny': pedido_tiny['id'],
                            'codigo_rastreio' : pedido_parcel['codigo_rastreio'] \
                                if pedido_parcel['codigo_rastreio'] else 'None'
                        }
                        itens_comum.update(novos_itens)
            # print(itens_comum)
            if all(chave in itens_comum for chave in chaves_verificar):
                for pdf in lista_all:
                    # print(pdf)
                    _dict = {
                        'id' : pdf['id'],
                        'nome_arquivo' : itens_comum['codigo_rastreio']
                    }
                    pdf = _dict
                    # print(pdf['nome_arquivo'], itens_comum['codigo_rastreio'], itens_comum['id_parcel'])
                    if pdf['nome_arquivo'] == f'{itens_comum['codigo_rastreio']}' or \
                        pdf['nome_arquivo'] == f'{itens_comum['id_parcel']}':
                        # print(pdf['nome_arquivo'], itens_comum['codigo_rastreio'], itens_comum['id_parcel'], itens_comum['nome'])
                        
                        url = f"https://drive.google.com/file/d/{pdf['nome_arquivo']}/view"
                        # enviar_url_etiqueta_para_tiny(url, itens_comum['id_tiny'])
                        

if __name__ == '__main__':
    from api_google_driver.pegar_lista_driver import main as listar_e_enviar_driver
    from func_BPS import autenticar_bps, listar_todos_parcels
    from func_Tiny import enviar_url_etiqueta_para_tiny, lista_pedidos_tiny

    my_driver = listar_e_enviar_driver()
    lista = my_driver.list_files_driver()['all']
    for pdf in lista:
        print(pdf['name'])
    # print(lista['all'])
    # main()
    # eita = listar_e_enviar_driver()
    # eita.upload_file_driver()
    # token = autenticar_bps()
    # if token:
    #     pedidos = listar_todos_parcels(token)
    #     print(pedidos)