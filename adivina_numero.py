#!/usr/bin/env python3
# Juego de adivinanza con interfaz "rosita"
# Guardar como adivina_numero.py y ejecutar: python3 adivina_numero.py

import random

# Colores ANSI (rosita / magenta claro)
PINK = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

def imprimir_titulo():
    print(PINK + BOLD + "=" * 44)
    print("   Bienvenido al juego de Adivina el Número (1 - 100)")
    print("          ¡Todo en tonos rosita para ti! 💖")
    print("=" * 44 + RESET)

def pedir_entero(prompt: str) -> int:
    while True:
        try:
            entrada = input(PINK + prompt + RESET + " ")
            valor = int(entrada.strip())
            return valor
        except ValueError:
            print(PINK + "Entrada no válida. Por favor escribe un número entero." + RESET)

def jugar():
    secreto = random.randint(1, 100)
    intentos = 0
    imprimir_titulo()

    while True:
        intento = pedir_entero("Adivina el número secreto:")
        intentos += 1

        if intento < 1 or intento > 100:
            print(PINK + "Por favor, elige un número entre 1 y 100." + RESET)
            continue

        if intento < secreto:
            print(PINK + "Demasiado bajo. Intenta un número más grande. ▲" + RESET)
        elif intento > secreto:
            print(PINK + "Demasiado alto. Prueba con un número más pequeño. ▼" + RESET)
        else:
            print()
            print(PINK + BOLD + "¡Felicidades! 🎉 Has adivinado el número secreto: " + str(secreto) + RESET)
            print(PINK + f"Lo lograste en {intentos} intento{'s' if intentos != 1 else ''}." + RESET)
            break

def main():
    while True:
        jugar()
        respuesta = input(PINK + "¿Quieres jugar otra vez? (s/n): " + RESET).strip().lower()
        if respuesta not in ("s", "si", "y", "yes"):
            print(PINK + "Gracias por jugar. ¡Hasta la próxima! 💕" + RESET)
            break
        print()  # línea en blanco antes de la siguiente partida

if __name__ == "__main__":
    main()
