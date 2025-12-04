#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adivina el número — Interfaz Tkinter (tema rosita)
Guardar como: adivina_numero_tk.py
Ejecutar: python3 adivina_numero_tk.py
"""

from __future__ import annotations
import random
import time
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

HIGHSCORE_PATH = Path.home() / ".adivina_numero_highscore.json"
DEFAULT_MIN = 1
DEFAULT_MAX = 100

# Colores
BG_PINK = "#ffe6f2"
PANEL_PINK = "#ffd6ea"
BUTTON_PINK = "#ff9ccf"
TEXT_PINK = "#c7257a"
ACCENT_PINK = "#ff4d9a"
WHITE = "#ffffff"
DARK = "#3b0a2a"


def cargar_highscore() -> dict | None:
    try:
        if HIGHSCORE_PATH.exists():
            with open(HIGHSCORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def guardar_highscore(record: dict) -> None:
    try:
        with open(HIGHSCORE_PATH, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def evaluar_pista(intento: int, secreto: int) -> str:
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


class AdivinaGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Adivina el número — Rosita 💖")
        master.configure(bg=BG_PINK)
        master.resizable(False, False)

        # Estado del juego
        self.secreto: int | None = None
        self.intentos: int = 0
        self.max_intentos: int | None = None
        self.inicio_tiempo: float | None = None
        self.timer_job = None

        # Cargar highscore
        self.highscore = cargar_highscore()

        # Layout
        self._crear_widgets()
        self._colocar_widgets()
        self._actualizar_highscore_label()

    def _crear_widgets(self):
        # Encabezado
        self.title_lbl = tk.Label(self.master, text="Adivina el número (1 - 100)", bg=BG_PINK,
                                  fg=ACCENT_PINK, font=("Helvetica", 16, "bold"))
        self.subtitle_lbl = tk.Label(self.master, text="¡Interfaz rosita para adivinar y divertirte! 💕",
                                     bg=BG_PINK, fg=TEXT_PINK, font=("Helvetica", 10))

        # Panel principal
        self.panel = tk.Frame(self.master, bg=PANEL_PINK, bd=2, relief="ridge", padx=12, pady=12)

        # Dificultad
        self.dif_lbl = tk.Label(self.panel, text="Dificultad:", bg=PANEL_PINK, fg=DARK, font=("Helvetica", 10, "bold"))
        self.dificultad_var = tk.StringVar(value="2")
        self.rb_easy = tk.Radiobutton(self.panel, text="Fácil (ilimitado)", variable=self.dificultad_var,
                                      value="1", bg=PANEL_PINK, fg=DARK, selectcolor=BUTTON_PINK, anchor="w")
        self.rb_normal = tk.Radiobutton(self.panel, text="Normal (10 intentos)", variable=self.dificultad_var,
                                        value="2", bg=PANEL_PINK, fg=DARK, selectcolor=BUTTON_PINK, anchor="w")
        self.rb_hard = tk.Radiobutton(self.panel, text="Difícil (5 intentos)", variable=self.dificultad_var,
                                      value="3", bg=PANEL_PINK, fg=DARK, selectcolor=BUTTON_PINK, anchor="w")

        # Botones de control
        self.new_btn = tk.Button(self.panel, text="Nueva partida", bg=BUTTON_PINK, fg=DARK,
                                 command=self.nueva_partida, width=14)
        self.quit_btn = tk.Button(self.panel, text="Salir", bg=WHITE, fg=DARK, command=self.master.quit, width=8)

        # Input de intento
        self.guess_lbl = tk.Label(self.panel, text="Tu intento:", bg=PANEL_PINK, fg=DARK, font=("Helvetica", 10))
        self.guess_entry = tk.Entry(self.panel, width=10, justify="center", font=("Helvetica", 12, "bold"))
        self.guess_entry.bind("<Return>", lambda e: self.enviar_intento())

        self.send_btn = tk.Button(self.panel, text="Probar", bg=ACCENT_PINK, fg=WHITE, command=self.enviar_intento, width=8)

        # Pistas y estado
        self.hint_lbl = tk.Label(self.panel, text="Pulsa 'Nueva partida' para comenzar.", bg=PANEL_PINK, fg=TEXT_PINK,
                                 font=("Helvetica", 11), wraplength=300, justify="center")
        self.attempts_lbl = tk.Label(self.panel, text="Intentos: 0", bg=PANEL_PINK, fg=DARK, font=("Helvetica", 10))
        self.timer_lbl = tk.Label(self.panel, text="Tiempo: 0.0 s", bg=PANEL_PINK, fg=DARK, font=("Helvetica", 10))

        # Highscore
        self.hs_frame = tk.Frame(self.master, bg=BG_PINK)
        self.hs_lbl = tk.Label(self.hs_frame, text="Mejor marca: —", bg=BG_PINK, fg=TEXT_PINK, font=("Helvetica", 10))

    def _colocar_widgets(self):
        self.title_lbl.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="n")
        self.subtitle_lbl.grid(row=1, column=0, pady=(0, 10), padx=10, sticky="n")
        self.panel.grid(row=2, column=0, padx=12, pady=(0, 12))

        # Panel layout
        self.dif_lbl.grid(row=0, column=0, columnspan=2, sticky="w")
        self.rb_easy.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))
        self.rb_normal.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))
        self.rb_hard.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 8))

        self.new_btn.grid(row=4, column=0, sticky="w", pady=(0, 8))
        self.quit_btn.grid(row=4, column=1, sticky="e", pady=(0, 8))

        self.guess_lbl.grid(row=5, column=0, pady=(4, 0))
        self.guess_entry.grid(row=5, column=1, pady=(4, 0))
        self.send_btn.grid(row=6, column=0, columnspan=2, pady=(8, 6))

        self.hint_lbl.grid(row=7, column=0, columnspan=2, pady=(6, 4))
        self.attempts_lbl.grid(row=8, column=0, sticky="w", pady=(4, 0))
        self.timer_lbl.grid(row=8, column=1, sticky="e", pady=(4, 0))

        self.hs_frame.grid(row=3, column=0, sticky="ew", padx=10)
        self.hs_lbl.pack(pady=(0, 8))

    def _actualizar_highscore_label(self):
        if self.highscore:
            mi = self.highscore.get("mejor_intentos")
            mt = self.highscore.get("mejor_tiempo_segundos")
            self.hs_lbl.config(text=f"Mejor marca: {mi} intento(s) en {mt} s")
        else:
            self.hs_lbl.config(text="Mejor marca: —")

    def nueva_partida(self):
        # Determinar límite de intentos
        dif = self.dificultad_var.get()
        if dif == "1":
            self.max_intentos = None
        elif dif == "2":
            self.max_intentos = 10
        else:
            self.max_intentos = 5

        self.secreto = random.randint(DEFAULT_MIN, DEFAULT_MAX)
        self.intentos = 0
        self.inicio_tiempo = time.time()
        self.hint_lbl.config(text=f"He elegido un número entre {DEFAULT_MIN} y {DEFAULT_MAX}. ¡Buena suerte!", fg=TEXT_PINK)
        self.attempts_lbl.config(text="Intentos: 0")
        self.timer_lbl.config(text="Tiempo: 0.0 s")
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus_set()
        # Desactivar cambios de dificultad mientras haya partida? Aquí permitimos cambiar (crea nueva partida si se hace)
        self._cancel_timer()
        self._update_timer()

    def _update_timer(self):
        if self.inicio_tiempo is None:
            return
        elapsed = time.time() - self.inicio_tiempo
        self.timer_lbl.config(text=f"Tiempo: {elapsed:.1f} s")
        # Actualizar cada 100 ms
        self.timer_job = self.master.after(100, self._update_timer)

    def _cancel_timer(self):
        if self.timer_job:
            try:
                self.master.after_cancel(self.timer_job)
            except Exception:
                pass
            self.timer_job = None

    def enviar_intento(self):
        if self.secreto is None:
            messagebox.showinfo("Comienza primero", "Pulsa 'Nueva partida' para comenzar a jugar.")
            return

        texto = self.guess_entry.get().strip()
        if texto == "":
            self.hint_lbl.config(text="Escribe un número entre 1 y 100.", fg=ACCENT_PINK)
            return
        try:
            intento = int(texto)
        except ValueError:
            self.hint_lbl.config(text="Entrada no válida. Escribe un número entero.", fg=ACCENT_PINK)
            return

        if intento < DEFAULT_MIN or intento > DEFAULT_MAX:
            self.hint_lbl.config(text=f"El número debe estar entre {DEFAULT_MIN} y {DEFAULT_MAX}.", fg=ACCENT_PINK)
            return

        self.intentos += 1
        self.attempts_lbl.config(text=f"Intentos: {self.intentos}")
        pista_cercania = evaluar_pista(intento, self.secreto)

        if intento < self.secreto:
            self.hint_lbl.config(text=f"Demasiado bajo. {pista_cercania}", fg=TEXT_PINK)
        elif intento > self.secreto:
            self.hint_lbl.config(text=f"Demasiado alto. {pista_cercania}", fg=TEXT_PINK)
        else:
            # Gana
            dur = time.time() - (self.inicio_tiempo or time.time())
            self._cancel_timer()
            self.hint_lbl.config(text=f"¡Felicidades! Has adivinado: {self.secreto}", fg=ACCENT_PINK)
            self._on_victory(duracion=dur)
            return

        # Comprobar límite de intentos si aplica
        if self.max_intentos is not None and self.intentos >= self.max_intentos:
            self._cancel_timer()
            self.hint_lbl.config(text=f"Se acabaron los intentos. El número era {self.secreto}.", fg=ACCENT_PINK)
            messagebox.showinfo("Fin de la partida", f"Has agotado los intentos.\nEl número secreto era: {self.secreto}")
            # Reiniciar secreto para prevenir más intentos hasta nueva partida
            self.secreto = None

        # Preparar siguiente intento
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus_set()

    def _on_victory(self, duracion: float):
        msg = f"¡Has ganado en {self.intentos} intento(s) en {duracion:.2f} segundos! 🎉"
        messagebox.showinfo("¡Ganaste!", msg)
        # Actualizar highscore si corresponde: menor intentos es mejor; si no hay registro se guarda.
        guardar = False
        if not self.highscore:
            guardar = True
        else:
            mejor_intentos = self.highscore.get("mejor_intentos", float("inf"))
            if self.intentos < mejor_intentos:
                guardar = True

        if guardar:
            nuevo = {
                "mejor_intentos": self.intentos,
                "mejor_tiempo_segundos": round(duracion, 2),
                "timestamp": time.time(),
            }
            guardar_highscore(nuevo)
            self.highscore = nuevo
            self._actualizar_highscore_label()
            messagebox.showinfo("¡Récord!", "¡Nuevo récord guardado! 🎉")

        # Marcar partida como finalizada
        self.secreto = None

    def on_close(self):
        # Asegurarse de cancelar temporizador
        self._cancel_timer()
        self.master.destroy()


def main():
    root = tk.Tk()
    app = AdivinaGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
