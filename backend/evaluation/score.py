import numpy as np

def media_modelo(resultados, modelo):
    keys = ["correcao", "completude", "clareza", "fidelidade", "nota_final"]

    medias = {}

    for k in keys:
        valores = [
            r[modelo][k]
            for r in resultados
            if r[modelo] is not None
        ]

        medias[k] = np.mean(valores)

    return medias