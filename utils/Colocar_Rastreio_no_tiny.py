import requests
from utils.func_BPS import autenticar_bps, listar_todos_parcels
from utils.func_Tiny import alterar_rastreamento, lista_pedidos_tiny
from datetime import date , timedelta

def main():

    token = autenticar_bps()
    _data = date.today() - timedelta(days=1)
    _data.strftime("%d%m%Y")
    lista_tiny = lista_pedidos_tiny(data_inicial=_data)

    if token and lista_tiny:
        lista_parcel = listar_todos_parcels(token, 'processed')
        chaves_verificar = ['nome', 'cpf_cnpj'] #se achar uma maneira em que tenha a mesma data pra um pedido q não foi pago no dia, colocar

        for pedido_tiny in lista_tiny:
            itens_comum = {}
            for pedido_parcel in lista_parcel:
                if not pedido_parcel['codigo_rastreio']:
                    continue
                for key, values in pedido_tiny.items() :
                    if key in pedido_tiny and pedido_parcel[key] == values:
                        
                        itens_comum[key] = values
                        itens_comum["id_parcel"] = pedido_parcel["id"]
                        itens_comum["id_tiny"] = pedido_tiny["id"]
                        itens_comum['codigo_rastreio'] = pedido_parcel['codigo_rastreio']

            if all(chave in itens_comum for chave in chaves_verificar):
                # print(itens_comum)
                alterar_rastreamento(itens_comum["id_tiny"], itens_comum['codigo_rastreio'])

if __name__ == '__main__':
    main()
    # token = autenticar_bps()
    # lista_parcel = listar_todos_parcels(token)
    # lista_tiny = lista_pedidos_tiny(data_inicial='01/01/2024')

    # for pedidp_tiny in lista_tiny:
    #     for pedido_parcel in lista_parcel:
    #         print(pedidp_tiny["nome"], pedido_parcel["nome"])
    #         print(pedidp_tiny["nome"]==pedido_parcel["nome"])
    #         print(pedidp_tiny["data_pedido"], pedido_parcel["data_pedido"])
    #         print(pedidp_tiny["data_pedido"]==pedido_parcel["data_pedido"])
    #         print(pedidp_tiny["cpf_cnpj"], pedido_parcel["cpf_cnpj"])
    #         print(pedidp_tiny["cpf_cnpj"] == pedido_parcel["cpf_cnpj"])
    #         print("____________________________")

