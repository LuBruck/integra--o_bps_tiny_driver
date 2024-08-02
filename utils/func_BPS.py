import requests
from datetime import datetime
import json

import unicodedata
def remover_acentos(texto):
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sem_acento = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_sem_acento

# Credenciais e URLs
bps_api_url_auth = "https://bps.bringer.io/public/api/v2/auth/token.json"
bps_api_url_get_parcels = "https://bps.bringer.io/public/api/v2/get/parcels.json"
bps_api_pdf_labels = "https://bps.bringer.io/public/api/v2/get/parcel/labels.json"

# Credenciais de API
configs= json.load(open("utils/credenciais.json", "r", encoding='utf-8'))
bps_username = configs['bps_username']
bps_password = configs['bps_password']

class MeuErro(Exception):
    ...

# Função para autenticar na BPS
def autenticar_bps():
    payload = {
        "username": bps_username,
        "password": bps_password
    }
    response = requests.post(bps_api_url_auth, json=payload)
    if response.status_code == 201:
        return response.json()["accessToken"]
    else:
        raise MeuErro(f"Erro ao autenticar: {response.status_code}, {response.text}")
        


#Função para listar todos parcels
def listar_todos_parcels(token, status : ['assigned' 'processed', 'created', None] = None, 
    pagination_limit = "None", pagination_page = "None"):
    type_status = ['assigned', 'processed', 'created', None]
    headers = {
        "Authorization": f"Bearer {token}"
        }
    params = {
        "pagination[limit]": pagination_limit,
        "pagination[page]": pagination_page
    }
    response = requests.get(bps_api_url_get_parcels , headers = headers, params=params)
    if response.status_code == 200:
        pedidos = response.json()["data"]

        if not status in type_status:
            raise TypeError(f"Erro: O status {status} nao exite")

        lista = []
        data_str_fmt = '%Y-%m-%d'

        for pedido in pedidos:
            label = pedido['label']
            label = None if not label else label["external_tracking_number"]
            data_str_n_fmt = pedido['recipient']["created_at"].split("T")[0]
            data_pedido = datetime.strptime(data_str_n_fmt , data_str_fmt)
            primeiro_nome = pedido['recipient']['first_name']
            ultimo_nome = pedido['recipient']['last_name']

            nome_completo = primeiro_nome+" "+ultimo_nome if not primeiro_nome[-1] == ' ' \
                else primeiro_nome+ultimo_nome

            nome_completo = remover_acentos(nome_completo)

            if pedido['status'] == status or status == None:
                info_simplificado_parcels = {
                'id' : pedido['id'],
                'data_pedido': data_pedido,
                'nome' : nome_completo,
                'email': pedido['recipient']['email'],
                'cpf_cnpj' : pedido['recipient']['tax_id'], #TaxId = cpf/cnpj
                'celular' : pedido['recipient']['phone'],
                "codigo_rastreio": label
                }

                lista.append(info_simplificado_parcels)
        lista.reverse()
        return lista
    else:
        raise MeuErro(f"Erro : {response.status_code}, {response.text}")

def obter_pdf_etiqueta_bps(token, parcel_id):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"id": parcel_id}
    response = requests.get(bps_api_pdf_labels, headers=headers, params=params)
    if response.status_code == 200:
        try:
            return response.content  # Retorna o PDF
        except ValueError:  
            raise MeuErro(print("Erro ao decodificar JSON."))
    else:
        raise MeuErro(f"Erro ao obter etiquetas: {response.status_code}, {response.text}")
        



if __name__ == "__main__":
    token = autenticar_bps()
    if token:
        lista = listar_todos_parcels(token)
        p = obter_pdf_etiqueta_bps(token, lista[0]["id"])
        print(p)