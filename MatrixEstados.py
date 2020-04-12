# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 12:23:43 2020

"""
import pandas as pd
import numpy as np
from APIServiceRS import APIServiceRS
from Charts import Charts
import matplotlib.pyplot as mp


class MatrixEstados:
  def __init__(self):
    self.api = APIServiceRS()
    self.charts = Charts()

  def __build_matrix(self, N, data, maxDate, to_plot, file_name):
    fig, plot = mp.subplots(1, 1, figsize=(10, 10), constrained_layout=True)
    dateCols = list(data.columns)
    if (maxDate == "last"):
      dateCols = dateCols[5:len(dateCols)]
    else:
      dateCols = dateCols[5:data.columns.get_loc(maxDate) + 1]

    # Ordena conforme os primeiros casos aparecem
    data = data.sort_values(by=dateCols,
                            ascending=np.zeros(len(dateCols), dtype=bool))

    # Encontra o primeiro dia em que o condado atinge N casos
    # e remove da analise os condados sem casos confirmados
    nfi = []
    uid = list(x for x in data['UID'])
    uidPositive = []
    for u in uid:
      infections = data.loc[data['UID'] == u, dateCols]
      nInfection = next(
        (i for i, x in enumerate(infections.values[0]) if x >= N), "None")
      if (nInfection != "None"):
        uidPositive.append(u)
      nfi.append(nInfection)

    size = len(uidPositive)
    print(str(size), "condados com teste positivo.")
    data.insert(4, "Day_First_N_Infections", nfi)

    # Histograma com a distribuicao de dias desde 22/01 para a infeccao N
    distribution = list(filter(("None").__ne__, nfi))
    plot.hist(distribution, bins=50)
    mp.xlabel("Dias até a infecção nº %d (desde %s)" % (N, dateCols[0]),
              fontsize=18)
    mp.ylabel("Frequência", fontsize=18)
    mp.title("Distribuição até " + dateCols[-1], fontsize=22)
    fig.savefig("hist_" + dateCols[-1].replace("/", "_") + ".png")

    newData = pd.DataFrame(data=uidPositive, columns=["UID"])

    # Calcula as diferencas de data
    count = 0
    progress = 0.0
    for i in uidPositive:
      di = data.loc[data['UID'] == i, "Day_First_N_Infections"]
      new_column = []
      for j in uidPositive:
        dj = data.loc[data['UID'] == j, "Day_First_N_Infections"]
        if ((not np.isnan(di.values[0])) and (not np.isnan(dj.values[0]))):
          new_column.append(di.values[0] - dj.values[0])
        else:
          new_column.append('NULL')
      count = count + 1
      # Exibe progresso para aliviar a impaciencia
      progress = (count / size) * 100
      print('\r%.2f%% completo.' % progress, end="\r")
      newData[i] = new_column

    csv_file_name = "%d_%s_%s.csv" % (N, maxDate.replace("/", "_"), file_name)

    # Salva o arquivo
    newData.to_csv(csv_file_name, index=False)

    if to_plot:
      self.charts.plot_matrix_color_code(csv_file_name)

  def get_matrix_estados(self,
                         N,
                         maxDate="last",
                         to_plot=False,
                         file_name="estados_RS"):
    data = self.api.get_historico_confirmados_municipio_pandas()
    self.__build_matrix(N, data, maxDate, to_plot, file_name)


# Exemplo de Uso
# mat = MatrixEstados()
# mat.get_matrix_estados(1, "04/12/2020", True)
