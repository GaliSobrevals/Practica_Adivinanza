#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Juego de adivinanza mejorado — interfaz "rosita"
Guarda como: adivina_numero.py
Ejecutar: python3 adivina_numero.py
"""

from __future__ import annotations
import random
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Try to use colorama on Windows; if not available, fall back to ANSI codes.
try:
    from colorama import init as _colorama_init, Fore, Style
    _colorama_init(autoreset=True)
    PINK = Fore.MAGENTA
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL
except Exception:
    PINK = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

HIGHSCORE_PATH = Path.home() / ".adivina_numero_highscore.json"
DEFAULT_MIN = 1
DEFAULT_MAX = 100


def cargar_highscore() -> Optional[Dict[str, Any]]:
    """Carga el highscore desde un archivo JSON, si existe."""
    try:
        if HIGHSCORE_PATH.exists():
            with open(HIGHSCORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        # No fallar el juego por un error de IO
        pass
    return None


def guardar_highscore(record: Dict[str, Any]) -> None:
    """Guarda el highscore en un archivo JSON."""
    try:
        with open(HIGHSCORE_PATH, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    except Exception:
        # Si no pudo guardarse, silenciosamente no bloqueamos el juego
        pass


def imprimir_titulo() -> None:
    print(PINK + BOLD + "=" * 56 + RESET)
    print(PINK + BOLD + "   Bienvenido al juego: Adivina el número (1 - 100)   " + RESET)
    print(PINK + "          ¡Interfaz rosita y amigable! 💖" + RESET)
    print(PINK + BOLD + "=" * 56 + RESET)


def elegir_dificultad() -> Optional[int]:
    """
    Pide al usuario elegir un nivel de dificultad.
    Devuelve el número máximo de intentos permitido (None = ilimitado).
    """
    opciones = {
        "1": ("Fácil (ilimitado de intentos)", None),
        "2": ("Normal (10 intentos)", 10),
        "3": ("Difícil (5 intentos)", 5),
    }
    print()
    print(PINK + "Elige un nivel de dificultad:" + RESET)
    for k, (desc, _) in opciones.items():
        print(PINK + f"  {k}. {desc}" + RESET)

    while True:
        elec = input(PINK + "Tu elección (1/2/3): " + RESET).strip()
        if elec in opciones:
            return opciones[elec][1]
        print(PINK + "Por favor ingresa 1, 2 o 3." + RESET)


def pedir_entero(prompt: str) -> Optional[int]:
    """Pide un entero al usuario; devuelve None si el usuario cancela con Ctrl+C/EOF."""
    try:
        entrada = input(PINK + prompt + RESET + " ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return None
    if entrada == "":
        return None
    try:
        return int(entrada)
    except ValueError:
        print(PINK + "Entrada no válida. Escribe un número entero." + RESET)
        return None


def evaluar_pista(intento: int, secreto: int) -> str:
    """Devuelve una pista más descriptiva según la cercanía."""
    diff = abs(intento - secreto)
    if diff == 0:
        return "¡Exacto!"
    if diff <= 2:
        return "¡Muy cerca! 🔥"
    if diff <= 7:
        return "Cerca — sigue así."
    if diff <= 20:
        return "Algo lejos."
    return "Muy lejos."


def actualizar_highscore_si_corresponde(intentos: int, duracion: float) -> None:
    """Actualiza el highscore si la partida actual es mejor."""
    registro = cargar_highscore()
    mejor = None
    if registro:
        mejor = registro.get("mejor_intentos")
    mejorable = False
    if registro is None:
        mejorable = True
    elif intentos < registro.get("mejor_intentos", float("inf")):
        mejorable = True

    if mejorable:
        nuevo = {
            "mejor_intentos": intentos,
            "mejor_tiempo_segundos": round(duracion, 2),
            "timestamp": time.time(),
        }
        guardar_highscore(nuevo)
        print(PINK + BOLD + "¡Nuevo récord! 🎉 He guardado tu mejor marca." + RESET)
    else:
        if registro:
            print(PINK + f"Mejor marca actual: {registro.get('mejor_intentos')} intento(s) en {registro.get('mejor_tiempo_segundos')} s." + RESET)


def jugar_una_partida(max_intentos: Optional[int]) -> None:
    secreto = random.randint(DEFAULT_MIN, DEFAULT_MAX)
    intentos = 0
    inicio = time.time()
    rango_min, rango_max = DEFAULT_MIN, DEFAULT_MAX

    print()
    print(PINK + f"He elegido un número secreto entre {rango_min} y {rango_max}. ¡Suerte!" + RESET)
    if max_intentos is None:
        print(PINK + "Tienes intentos ilimitados." + RESET)
    else:
        print(PINK + f"Tienes como máximo {max_intentos} intentos." + RESET)

    while True:
        if max_intentos is not None and intentos >= max_intentos:
            print(PINK + BOLD + "Se han acabado los intentos. 😢 ¡Mejor suerte la próxima!" + RESET)
            print(PINK + f"El número secreto era: {secreto}" + RESET)
            break

        entrada = pedir_entero("Adivina el número secreto:")
        if entrada is None:
            # usuario canceló o dejó en blanco
            resp = input(PINK + "¿Quieres salir del juego? (s/n): " + RESET).strip().lower()
            if resp in ("s", "si", "y", "yes"):
                raise KeyboardInterrupt
            else:
                continue

        intento = entrada
        intentos += 1

        if intento < rango_min or intento > rango_max:
            print(PINK + f"Por favor, elige un número entre {rango_min} y {rango_max}." + RESET)
            continue

        if intento < secreto:
            pista = evaluar_pista(intento, secreto)
            print(PINK + "Demasiado bajo. " + pista + RESET)
        elif intento > secreto:
            pista = evaluar_pista(intento, secreto)
            print(PINK + "Demasiado alto. " + pista + RESET)
        else:
            dur = time.time() - inicio
            print()
            print(PINK + BOLD + f"¡Felicidades! 🎉 Has adivinado el número secreto: {secreto}" + RESET)
            print(PINK + f"Lo lograste en {intentos} intento{'s' if intentos != 1 else ''} y {round(dur,2)} segundos." + RESET)
            actualizar_highscore_si_corresponde(intentos, dur)
            break


def confirmar_repetir() -> bool:
    while True:
        r = input(PINK + "¿Quieres jugar otra vez? (s/n): " + RESET).strip().lower()
        if r in ("s", "si", "y", "yes"):
            return True
        if r in ("n", "no"):
            return False
        print(PINK + "Por favor responde s (sí) o n (no)." + RESET)


def main() -> None:
    imprimir_titulo()
    registro = cargar_highscore()
    if registro:
        print(PINK + f"Mejor marca guardada: {registro.get('mejor_intentos')} intento(s) en {registro.get('mejor_tiempo_segundos')} s." + RESET)
    try:
        while True:
            max_intentos = elegir_dificultad()
            try:
                jugar_una_partida(max_intentos)
            except KeyboardInterrupt:
                print()
                print(PINK + "Salida solicitada. Volviendo al menú principal..." + RESET)
            if not confirmar_repetir():
                print(PINK + "Gracias por jugar. ¡Hasta la próxima! 💕" + RESET)
                break
            print()  # espacio entre partidas
    except KeyboardInterrupt:
        print()
        print(PINK + "Adiós. ¡Cuídate! 💖" + RESET)


if __name__ == "__main__":
    main()
