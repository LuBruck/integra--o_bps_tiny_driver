import requests
from datetime import datetime
import json


import unicodedata
def remover_acentos(texto):
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sem_acento = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_sem_acento

# Credenciais e URLs
tiny_api_url_alterar_rastreamento = "https://api.tiny.com.br/api2/cadastrar.codigo.rastreamento.pedido.php"
tiny_api_url_procurar_pedidos = "https://api.tiny.com.br/api2/pedidos.pesquisa.php"
tiny_api_url_pegar_pedidos = "https://api.tiny.com.br/api2/pedido.obter.php"
tiny_api_url_alterar_pedido = "https://api.tiny.com.br/api2/pedido.alterar.php"

# Credenciais de API
configs = json.load(open("utils/credenciais.json", "r", encoding='utf-8'))
tiny_api_token = configs['token_tiny']
class MeuErro(Exception):
    ...

#Função para colocar todos os pedidos em preparo do tiny em uma lista
def lista_pedidos_tiny(situacao = None, data_inicial = None):
    params = {
        "token" : tiny_api_token,
        "formato":'json',
        'situacao' : situacao,
        'dataInicial' : data_inicial
    }

    response = requests.get(tiny_api_url_procurar_pedidos, params=params)
    pedidos = response.json()
    consulta_de_retorno = True
    if pedidos["retorno"]["status"] == 'Erro' and pedidos['retorno']['codigo_erro'] == '20':
        print('A consulta nao retornou registros')
        consulta_de_retorno = False
    if response.status_code == 200 and consulta_de_retorno == True:
        if pedidos["retorno"]["status"] == 'Erro':
            raise MeuErro(f"Erro {pedidos["retorno"]["codigo_erro"]}, {pedidos["retorno"]["erros"]}")
        lista = []
        pedidos = pedidos['retorno']['pedidos']

        for pedido in pedidos:
            id_pedido = pedido['pedido']['id']
            pedido = pegar_pedido_tiny(id_pedido)

            data_str_fmt = '%d/%m/%Y'
            data_str_n_fmt = pedido["data_pedido"] #verifyExpires
            data_pedido = datetime.strptime(data_str_n_fmt , data_str_fmt)
            nome = pedido['cliente']['nome'] if not pedido['cliente']['nome'][-1] == " " \
                else pedido['cliente']['nome'][:-1]
            nome = remover_acentos(nome)

            info_simplificado_pedido = {
                'id' : pedido['id'],
                'data_pedido': data_pedido,
                'nome' : nome,
                'email': pedido['cliente']['email'],
                'cpf_cnpj' : pedido['cliente']['cpf_cnpj'], #TaxId
                'celular' : pedido['cliente']['fone']
            }
            lista.append(info_simplificado_pedido)
        return lista
    elif consulta_de_retorno == True:
        raise MeuErro(f'Erro ao pegar pedido: {response.status_code} {response.text}')

#Funação para pegar info de um pedido no tiny
def pegar_pedido_tiny(id):
    params = {
        "token" : tiny_api_token,
        "id" : id,
        "formato" : 'json',
    }
    response = requests.get(tiny_api_url_pegar_pedidos, params=params)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['retorno'].get('pedido', {})
    else:
        raise MeuErro(f"Deu erro em pegar este pedido:{response.status_code}, {response.text} ")

def alterar_rastreamento(id_pedido, codigo_rastreio):
    url_codigo_rastreio = f"https://bringerparcel.com/tracking/{codigo_rastreio}"
    params =  {
        'token' : tiny_api_token,
        'id' : id_pedido, 
        'codigoRastreamento' : codigo_rastreio,
        'urlRastreamento': url_codigo_rastreio
    }
    response = requests.post(tiny_api_url_alterar_rastreamento, params = params)
    if response.status_code == 200:
        if "<codigo_erro>32" in response.text:
            raise MeuErro(f"pedido:{params["id"]} nao encontrado")
        # print(response.text)
        print("Informacoes de rastreio enviado!")
    else:
        raise MeuErro(f'Erro ao enviado Informacoes: {response.status_code} {response.text}')

# Função para enviar a URL da etiqueta para o campo do pedido no TINYERP
def enviar_url_etiqueta_para_tiny(url_etiqueta, pedido_id):
    params = {
        "id" : pedido_id,
        'token' : tiny_api_token,
        }
    data = {
        "dados_pedido" : {
            "obs": f"Url da etiqueta: {url_etiqueta}",
            "obs_interna": ""
            }
        }
    
    response = requests.post(tiny_api_url_alterar_pedido, params = params , json=data )
    if response.status_code == 200:
        if "<codigo_erro>32" in response.text:
            raise MeuErro(f"pedido:{params["id"]} nao encontrado")
        print("URL da etiqueta enviada com sucesso!")
    else:
        raise MeuErro(f"Erro ao enviar URL da etiqueta: {response.status_code}, {response.text}")

if __name__ == "__main__":
    lista_pedidos_tiny()