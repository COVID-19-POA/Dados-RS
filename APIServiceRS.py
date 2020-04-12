import requests
from datetime import date
import pandas as pd


class APIServiceRS:
  def __init__(self):
    self.__base_url = "https://hsig.sema.rs.gov.br/arcgis/rest/services/COVID"
    self.__confirmed_data = None
    self.__mortes_data = None

  def __request_historico_confirmados(self):
    params = {
      "f": "json",
      "where": "1=1",
      "returnGeometry": "false",
      "outFields": "*"
    }
    response = requests.post(url="%s/Casos_hist/FeatureServer/0/query" %
                             (self.__base_url),
                             params=params)
    self.__confirmed_data = response.json()

  def __request_historico_mortes(self):
    params = {
      "f": "json",
      "where": "1=1",
      "returnGeometry": "false",
      "outFields": "*"
    }
    response = requests.post(url="%s/Mortes_hist/FeatureServer/0/query" %
                             (self.__base_url),
                             params=params)
    self.__mortes_data = response.json()

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
          parsed_data = "2020/%s/%s" % (data_caso[0], data_caso[1])
          data_caso = date(2020, int(data_caso[1]), int(data_caso[0]))
          historico[parsed_data] = {"casos": int(value), "data": data_caso}
      result[attributes["nm_municip"]] = {
        "nome": attributes["nm_municip"],
        "historico": historico,
        "atualizado": updated
      }

    return result

  def __parse_date(self, date):
    date = date.split("/")
    date = "%s/%s/%s" % (date[2], date[1], date[0])
    return date

  def __parse_data_pandas(self, data):
    res = {
      "UID": [],
      "Admin2": [],
      "Province_State": [],
      "Country_Region": [],
      "Combined_Key": []
    }
    rs = "Rio Grande do Sul"
    dates_row = []
    count = 0
    for municipio, value in data.items():
      count += 1
      res["UID"].append(count)
      res["Admin2"].append(municipio)
      res["Province_State"].append(rs)
      res["Country_Region"].append("BR")
      res["Combined_Key"].append("%s, %s, BR" % (municipio, rs))
      for date in dates_row:
        if date not in value["historico"].keys():
          res[self.__parse_date(date)].append(0)
      for date, cases in value["historico"].items():
        parsed_date = self.__parse_date(date)
        if parsed_date in res:
          res[parsed_date].append(cases["casos"])
        else:
          dates_row.append(date)
          res[parsed_date] = [cases["casos"]]
    return pd.DataFrame.from_dict(res)

  # Retorna o histórico de casos confirmados dos municípios. Dados ficam em cache para evitar requests desnecessárias, mas se precisar refazer, chamar com force_request como True
  def get_historico_confirmados_municipio(self, force_request=False):
    if force_request or self.__confirmed_data == None:
      self.__request_historico_confirmados()
    return self.__parse_historico_municipio(self.__confirmed_data)

  # Retorna o histórico de casos de morte dos municípios. Dados ficam em cache para evitar requests desnecessárias, mas se precisar refazer, chamar com force_request como True
  def get_historico_mortes_municipio(self, force_request=False):
    if force_request or self.__mortes_data == None:
      self.__request_historico_mortes()
    return self.__parse_historico_municipio(self.__mortes_data)

  def get_historico_confirmados_municipio_pandas(self, force_request=False):
    return self.__parse_data_pandas(
      self.get_historico_confirmados_municipio(force_request))

  def get_historico_mortes_municipio_pandas(self, force_request=False):
    return self.__parse_data_pandas(
      self.get_historico_mortes_municipio(force_request))

  # Retorna dicionario com historico de confirmados e mortes
  def get_historico_completo(self, force_request=False):
    if force_request:
      self.__request_historico_confirmados()
      self.__request_historico_mortes()
    return {
      "confirmados": self.get_historico_confirmados_municipio(),
      "mortes": self.get_historico_mortes_municipio()
    }


# Exemplo de uso:
# api = APIServiceRS()
# historico = api.get_historico_confirmados_municipio()
# historico_poa = historico["Porto Alegre"]["historico"]
# print(historico_poa)
