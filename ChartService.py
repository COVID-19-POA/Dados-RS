import plotly.graph_objects as go
import pandas as pd
from APIServiceRS import APIServiceRS


class ChartService:
  def __init__(self):
    self.__api = APIServiceRS()
    self.__data_confirmados = None

  def __get_casos_data(self, data, historico, municipio):
    if data in historico[municipio]["historico"]:
      return historico[municipio]["historico"][data]["casos"]
    else:
      return 0

  def plot_historico_confirmados(self, forceRequest=False):
    if forceRequest or self.__data_confirmados == None:
      self.__data_confirmados = self.__api.get_historico_confirmados_municipio(
      )
    historico_confirmados_poa = self.__data_confirmados["Porto Alegre"]
    datas = list(historico_confirmados_poa["historico"].keys())
    sorted(
      datas,
      key=lambda data: historico_confirmados_poa["historico"][data]["data"])
    fig = go.Figure()
    for municipio, _ in self.__data_confirmados.items():
      casos = list(
        map(
          lambda data: self.__get_casos_data(data, self.__data_confirmados,
                                             municipio), datas))
      fig.add_trace(go.Scatter(x=datas, y=casos, mode='lines', name=municipio))

    fig.update_layout(title='Histórico de Casos Confirmados no RS',
                      xaxis_title='Data',
                      yaxis_title='Casos')

    fig.show()


# Exemplo de uso
# chart = ChartService()
# chart.plot_historico_confirmados()
