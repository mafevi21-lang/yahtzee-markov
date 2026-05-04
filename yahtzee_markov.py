"""
=======================================================
  YAHTZEE con MODELO DE MARKOV
  Materia: Simulación / Inteligencia Artificial
  Descripción: Juego de Yahtzee con cadena de Markov
               para predecir y recomendar estrategias.
=======================================================
"""

import random

# ──────────────────────────────────────────
#  DEFINICIÓN DE ESTADOS DE MARKOV
# ──────────────────────────────────────────
ESTADOS = ['Nada', 'Par', 'DosPares', 'Trio',
           'Cuarteto', 'FullHouse', 'EscPeq', 'EscLar', 'Yahtzee']
NUM_ESTADOS = len(ESTADOS)

# Matriz de transición (conteos inicializados en 1 → suavizado de Laplace)
matriz_transicion = [[1] * NUM_ESTADOS for _ in range(NUM_ESTADOS)]


# ──────────────────────────────────────────
#  FUNCIONES DE DADO
# ──────────────────────────────────────────
def fncResDado():
    """Regresa el resultado de un dado (1-6)."""
    return random.randint(1, 6)


# ──────────────────────────────────────────
#  FUNCIONES DE EVALUACIÓN DE MANO
# ──────────────────────────────────────────
def fncPunYahtzee(lstRes):
    """Regresa 50 si todos los dados son iguales (Yahtzee), si no 0."""
    return 50 if len(set(lstRes)) == 1 else 0


def fncLS(lstRes):
    """Regresa 40 si hay escalera larga (Large Straight), si no 0."""
    ordenada = sorted(lstRes)
    if ordenada == [1, 2, 3, 4, 5] or ordenada == [2, 3, 4, 5, 6]:
        return 40
    return 0


def fncSmallS(lstRes):
    """Regresa 30 si hay escalera pequeña (4 consecutivos), si no 0."""
    conjunto = set(lstRes)
    patrones = [{1,2,3,4}, {2,3,4,5}, {3,4,5,6}]
    for patron in patrones:
        if patron.issubset(conjunto):
            return 30
    return 0


def fncFullHouse(lstRes):
    """Regresa 25 si hay full house (3+2), si no 0."""
    conteos = sorted([lstRes.count(v) for v in set(lstRes)])
    if conteos == [2, 3]:
        return 25
    return 0


def fncCuarteto(lstRes):
    """Regresa la suma si hay cuatro del mismo valor, si no 0."""
    for v in set(lstRes):
        if lstRes.count(v) >= 4:
            return sum(lstRes)
    return 0


def fncTrio(lstRes):
    """Regresa la suma si hay tres del mismo valor, si no 0."""
    for v in set(lstRes):
        if lstRes.count(v) >= 3:
            return sum(lstRes)
    return 0


def fncPuntos(lstRes):
    """Regresa el puntaje de una mano según la mejor combinación."""
    pun = fncPunYahtzee(lstRes)
    if pun > 0:
        print("  → ¡YAHTZEE! (+50)")
        return pun

    pun = fncLS(lstRes)
    if pun > 0:
        print("  → Escalera Larga (+40)")
        return pun

    pun = fncSmallS(lstRes)
    if pun > 0:
        print("  → Escalera Pequeña (+30)")
        return pun

    pun = fncFullHouse(lstRes)
    if pun > 0:
        print("  → Full House (+25)")
        return pun

    pun = fncCuarteto(lstRes)
    if pun > 0:
        print("  → Cuarteto (suma)")
        return pun

    pun = fncTrio(lstRes)
    if pun > 0:
        print("  → Trío (suma)")
        return pun

    pun = sum(lstRes)
    print("  → Sin combinación (suma bruta)")
    return pun


# ──────────────────────────────────────────
#  MODELO DE MARKOV
# ──────────────────────────────────────────
def obtener_estado(lstRes):
    """
    Clasifica una mano en uno de los ESTADOS de Markov.
    Retorna el índice del estado correspondiente.
    """
    ordenada = sorted(lstRes)
    conjunto  = set(lstRes)

    if len(conjunto) == 1:
        return ESTADOS.index('Yahtzee')
    if ordenada in ([1,2,3,4,5], [2,3,4,5,6]):
        return ESTADOS.index('EscLar')
    for patron in [{1,2,3,4},{2,3,4,5},{3,4,5,6}]:
        if patron.issubset(conjunto):
            return ESTADOS.index('EscPeq')

    conteos = sorted([lstRes.count(v) for v in conjunto])
    if conteos == [2, 3]:
        return ESTADOS.index('FullHouse')
    if 4 in conteos:
        return ESTADOS.index('Cuarteto')
    if 3 in conteos:
        return ESTADOS.index('Trio')
    if conteos.count(2) >= 2:
        return ESTADOS.index('DosPares')
    if 2 in conteos:
        return ESTADOS.index('Par')

    return ESTADOS.index('Nada')


def actualizar_transicion(estado_desde, estado_hacia):
    """Registra una transición observada en la matriz de Markov."""
    matriz_transicion[estado_desde][estado_hacia] += 1


def probabilidades_transicion(estado_desde):
    """
    Normaliza la fila de la matriz y retorna las probabilidades
    de pasar a cada estado desde el estado dado.
    """
    fila = matriz_transicion[estado_desde]
    total = sum(fila)
    return [v / total for v in fila]


def recomendar_estrategia(estado_idx):
    """
    Dado el estado actual, imprime la recomendación de Markov
    (hacia qué estado conviene moverse y con qué probabilidad).
    """
    probs = probabilidades_transicion(estado_idx)
    mejor_siguiente = probs.index(max(probs))
    nombre_estado   = ESTADOS[estado_idx]
    nombre_siguiente = ESTADOS[mejor_siguiente]

    print(f"\n  📊 [MARKOV] Estado actual: {nombre_estado}")
    print(f"  📈 Estado más probable siguiente: {nombre_siguiente} "
          f"({probs[mejor_siguiente]*100:.1f}%)")

    recomendaciones = {
        'Nada':      "  💡 Relanza todos los dados.",
        'Par':       "  💡 Conserva el par, relanza los 3 restantes.",
        'DosPares':  "  💡 Conserva ambos pares, busca Full House.",
        'Trio':      "  💡 Conserva el trío, relanza los 2 sobrantes.",
        'Cuarteto':  "  💡 Conserva el cuarteto, busca Yahtzee.",
        'FullHouse': "  💡 ¡Full House completo! Considera anotar.",
        'EscPeq':    "  💡 Escalera pequeña lista. Anota o busca la larga.",
        'EscLar':    "  💡 ¡Escalera larga! Anota de inmediato.",
        'Yahtzee':   "  💡 ¡YAHTZEE! Anota los 50 puntos.",
    }
    print(recomendaciones.get(nombre_estado, "  💡 Evalúa la mejor jugada."))
    return mejor_siguiente


def imprimir_matriz():
    """Imprime la matriz de transición normalizada (en %)."""
    print("\n  ═══ MATRIZ DE TRANSICIÓN DE MARKOV (%) ═══")
    header = "        " + "".join(f"{e[:5]:>7}" for e in ESTADOS)
    print(header)
    for i, fila_nombre in enumerate(ESTADOS):
        probs = probabilidades_transicion(i)
        fila_str = f"  {fila_nombre[:7]:<8}" + "".join(f"{p*100:>6.1f}%" for p in probs)
        print(fila_str)
    print()


# ──────────────────────────────────────────
#  SIMULACIÓN DEL JUEGO
# ──────────────────────────────────────────
def simular_turno(jugador_num):
    """
    Simula un turno completo (hasta 3 tiradas) de un jugador,
    aplicando el modelo de Markov en cada tirada.
    Retorna el puntaje final del turno.
    """
    print(f"\n{'═'*50}")
    print(f"  TURNO JUGADOR {jugador_num}")
    print(f"{'═'*50}")

    dados = [fncResDado() for _ in range(5)]
    estado_previo = None

    for tirada in range(1, 4):  # máximo 3 tiradas
        estado_actual_idx = obtener_estado(dados)
        estado_actual_nom = ESTADOS[estado_actual_idx]

        print(f"\n  Tirada {tirada}: {dados}")
        print(f"  Estado Markov: {estado_actual_nom}")

        # Actualizar matriz de transición
        if estado_previo is not None:
            actualizar_transicion(estado_previo, estado_actual_idx)

        # Recomendar
        mejor_sig = recomendar_estrategia(estado_actual_idx)

        # Criterio de parada: si ya tenemos una buena combinación, paramos
        if estado_actual_nom in ('Yahtzee', 'EscLar', 'FullHouse', 'EscPeq', 'Cuarteto'):
            print(f"  ✅ Combinación óptima encontrada. No se relanza.")
            break

        # Relanzar dados que no convienen conservar
        if tirada < 3:
            # Estrategia simple: conservar el valor más frecuente
            freq = {}
            for d in dados:
                freq[d] = freq.get(d, 0) + 1
            max_freq = max(freq.values())
            conservar_val = [v for v,c in freq.items() if c == max_freq][0]
            dados = [d if d == conservar_val else fncResDado() for d in dados]

        estado_previo = estado_actual_idx

    puntaje = fncPuntos(dados)
    print(f"\n  🎯 Puntaje del turno: {puntaje}")
    return puntaje, estado_actual_idx


# ──────────────────────────────────────────
#  BLOQUE PRINCIPAL
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║   YAHTZEE  —  MODELO DE MARKOV               ║")
    print("╚══════════════════════════════════════════════╝")

    NUM_RONDAS = 13  # partida estándar de Yahtzee

    puntajes_j1 = []
    puntajes_j2 = []
    ganadores   = []
    historial_estados_j1 = []
    historial_estados_j2 = []

    for ronda in range(1, NUM_RONDAS + 1):
        print(f"\n\n{'★'*20}  RONDA {ronda}/{NUM_RONDAS}  {'★'*20}")

        pun1, est1 = simular_turno(1)
        pun2, est2 = simular_turno(2)

        puntajes_j1.append(pun1)
        puntajes_j2.append(pun2)
        historial_estados_j1.append(est1)
        historial_estados_j2.append(est2)

        if pun1 > pun2:
            ganadores.append(1)
        elif pun2 > pun1:
            ganadores.append(2)
        else:
            ganadores.append(0)  # empate

    # ── Resultados finales ──
    print("\n\n" + "═"*50)
    print("  RESULTADOS FINALES")
    print("═"*50)
    print(f"  Puntajes Jugador 1: {puntajes_j1}")
    print(f"  Total Jugador 1:    {sum(puntajes_j1)}")
    print(f"\n  Puntajes Jugador 2: {puntajes_j2}")
    print(f"  Total Jugador 2:    {sum(puntajes_j2)}")

    victorias_j1 = ganadores.count(1)
    victorias_j2 = ganadores.count(2)
    empates      = ganadores.count(0)
    print(f"\n  Victorias por ronda → J1: {victorias_j1}  J2: {victorias_j2}  Empates: {empates}")

    if sum(puntajes_j1) > sum(puntajes_j2):
        print("\n  🏆 GANADOR TOTAL: Jugador 1")
    elif sum(puntajes_j2) > sum(puntajes_j1):
        print("\n  🏆 GANADOR TOTAL: Jugador 2")
    else:
        print("\n  🤝 EMPATE TOTAL")

    # ── Matriz de Markov final ──
    imprimir_matriz()

    print("  Historial de estados J1:", [ESTADOS[e] for e in historial_estados_j1])
    print("  Historial de estados J2:", [ESTADOS[e] for e in historial_estados_j2])
    print("\n  Fin del programa.")
