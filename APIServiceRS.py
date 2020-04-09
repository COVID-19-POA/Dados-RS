import requests
from datetime import date

class APIServiceRS:
  def __init__(self):
    self.base_url = "https://hsig.sema.rs.gov.br/arcgis/rest/services/COVID"
    self.data = None

  def __request_data(self):
    params = {"f": "json", "where": "1=1", "returnGeometry": "false", "outFields": "*"}
    response = requests.post(url="%s/Casos_hist/FeatureServer/0/query" %
                  (self.base_url), params=params)
    self.data = response.json()


  # Retorno: Dicionário de nomes dos municípios mapeado para dicionário com nome, data de atualização e histórico. Histórico é uma lista de dicionários com casos e data em formato date.
  # {
  #   [nome: str]: {
  #     nome: str,
  #     atualizado: date,
  #     historico: { casos: int, data: date }[]
  #   } 
  # }
  def __parse_historico_municipio(self, data):
    result = dict()

    for municipio in data["features"]:
      attributes = municipio["attributes"]
      historico = dict()
      # Data de atualização está em milisegundos, converter para date
      updated = date.fromtimestamp(int(str(attributes["data"])[0:10]))
      # Historico está em chaves do atributos, com chaves que começam por "casos_MES_DIA"
      for key, value in attributes.items():
        # Filtrando por chaves que possuem um valor associado
        if key.startswith("casos_") and value != None:
          data_caso = key.replace("casos_", "")
          data_caso = data_caso.split("_")
          parsed_data = "2020/%s/%s"%(data_caso[0], data_caso[1])
          data_caso = date(2020, int(data_caso[1]), int(data_caso[0]))
          historico[parsed_data] = { "casos": int(value), "data": data_caso }
      result[attributes["nm_municip"]] = { "nome": attributes["nm_municip"], "historico": historico, "atualizado": updated }

    return result

  # Retorna o histórico dos municípios. Dados ficam em cache para evitar requests desnecessárias, mas se precisar refazer, chamar com force_request como True
  def get_historico_municipio(self, force_request = False):
    if force_request:
      self.__request_data()
    elif self.data == None:
      self.__request_data()
    return self.__parse_historico_municipio(self.data)

# Exemplo de uso:
# api = APIServiceRS()
# historico = api.get_historico_municipio()
# historico_poa = historico["Porto Alegre"]["historico"]
# print(historico_poa)