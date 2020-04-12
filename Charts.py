import plotly.graph_objects as go
from APIServiceRS import APIServiceRS
import numpy as np
import pandas as pd
import matplotlib.pyplot as mp
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap


class Charts:
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

  def plot_matrix_color_code(self, file_name):
    #viridis = cm.get_cmap('viridis', 256)
    top = cm.get_cmap('Oranges_r', 128)
    bottom = cm.get_cmap('Blues', 128)

    newcolors = np.vstack(
      (top(np.linspace(0, 1, 128)), bottom(np.linspace(0, 1, 128))))
    #newcolors = viridis(np.linspace(0, 1, 256))
    newcmp = ListedColormap(newcolors)

    fig, plot = mp.subplots(1, 1, figsize=(10, 10), constrained_layout=True)

    data = pd.read_csv(file_name)
    data = data.drop('UID', axis=1)
    data = data.drop(data.index[0])

    psm = plot.pcolormesh(data, cmap=newcmp, rasterized=True)
    fig.colorbar(psm, ax=plot)
    mp.show()
    fig.savefig('vis.png', dpi=600)


# Exemplo de uso
# chart = Charts()
# chart.plot_historico_confirmados()
