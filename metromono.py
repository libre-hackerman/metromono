# Copyright (C) 2017 Esteban López | gnu_stallman (at) protonmail (dot) ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pysine import sine
import time
import webbrowser
from threading import Thread

VERSION = "1.1.0"

# Ruta al archivo de configuración
ARCHIVO_CONFIG = ".config"

# Diccionario con las frecuencias (Hz) de las notas
FRECUENCIAS = {'A': 440, 'B': 494, 'C': 523,
               'D': 587, 'E': 659, 'F': 699, 'G': 784}

BPM_MINIMO = 1
BPM_MAXIMO = 300


class Tick:
    def __init__(self):
        self.duracion = 0.1  # Duración del tick
        self.compas = 0
        self.pulso = 1
        self.bpm = 1
        self.frecuencia = 0

    def tick(self):
        frecuencia = self.frecuencia
        if self.pulso == self.compas:
            frecuencia = 880  # acento (La agudo)
            self.pulso = 1
        elif self.compas != 0:
            self.pulso += 1

        # Evita que se vaya de madre
        if self.pulso > self.compas:
            self.pulso = 1

        sine(frequency=frecuencia, duration=self.duracion)
        # print("Pulso:", self.pulso)
        time.sleep((60.0/self.bpm)-self.duracion)  # pausa


class Archivo_config:
    def __init__(self, ruta):
        self.config = ruta

        # Valores por defecto
        self.bpm = 60
        self.compas = 0
        self.nota = 'A'

        self.leer_archivo()

    def leer_archivo(self):
        try:
            flujo_lectura = open(self.config, 'r', encoding="utf-8")
            self.bpm = int(flujo_lectura.readline())
            self.compas = int(flujo_lectura.readline())
            self.nota = flujo_lectura.readline()
            flujo_lectura.close()
        except FileNotFoundError:
            pass

    def escribir_archivo(self):
        flujo_escritura = open(self.config, 'w', encoding="utf-8")
        flujo_escritura.write(str(self.bpm) + '\n')
        flujo_escritura.write(str(self.compas) + '\n')
        flujo_escritura.write(self.nota)
        flujo_escritura.close()


class Gui:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Metrómono")

        self.bpm_seleccionado = tk.IntVar()  # BPMs recogidos de entrada_bpm
        self.nota_seleccionada = tk.StringVar()  # Nota elegida para el tono
        self.compas_seleccionado = tk.IntVar()  # Compás elegido

        # Carga de valores iniciales
        self.configuracion = Archivo_config(ARCHIVO_CONFIG)
        self.nota_seleccionada.set(self.configuracion.nota)
        self.bpm_seleccionado.set(self.configuracion.bpm)
        self.compas_seleccionado.set(self.configuracion.compas)
        self.sonando = False
        self.seguir_abierto = True

        self.boton_tap = tk.Button(
            self.ventana, text="TAP", command=self.tapping,
            activebackground="cyan")
        self.t1 = 0
        self.t2 = 0

        # Menú totalmente inncecesario pero que hago porque puedo
        self.barra_menu = tk.Menu(self.ventana)
        self.menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        self.menu_archivo.add_command(label="Salir", command=self.guardado)
        self.menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        self.menu_ayuda.add_command(label="Ayuda", command=self.ayuda)
        self.menu_ayuda.add_command(
            label="Atajos de teclado", command=self.ayuda_atajos)
        self.menu_ayuda.add_command(label="Licencia", command=self.licencia)
        self.menu_ayuda.add_separator()  # Barra horizontal
        self.menu_ayuda.add_command(
            label="Acerca de Metrómono", command=self.acerca_de)
        self.barra_menu.add_cascade(label="Archivo", menu=self.menu_archivo)
        self.barra_menu.add_cascade(label="Ayuda", menu=self.menu_ayuda)

        # Contiene el recolector de BPMs y el botón de inicio/pausa
        self.frame_superior = tk.Frame(self.ventana)

        self.deslizable_bpm = tk.Scale(
            self.frame_superior, variable=self.bpm_seleccionado,
            orient=tk.HORIZONTAL, from_=BPM_MINIMO, to=BPM_MAXIMO,
            activebackground="cyan", length=120)
        self.etiqueta_bpm = tk.Label(
            self.frame_superior, text="BPMs")  # Label indicando "bpms"

        self.boton = tk.Button(
            self.frame_superior, text="Iniciar", command=self.accion_boton,
            activebackground="cyan")

        self.desplegable_notas = ttk.Combobox(
            self.ventana, textvariable=self.nota_seleccionada, width=1,
            values=list(FRECUENCIAS.keys()))

        # Contiene el radiobutton con los compases
        self.frame_compas = tk.Frame(self.ventana)

        self.no_compas = tk.Radiobutton(
            self.frame_compas, text="Sin compás",
            variable=self.compas_seleccionado, value=0)
        self.compas_2_4 = tk.Radiobutton(
            self.frame_compas, text="2/4",
            variable=self.compas_seleccionado, value=2)
        self.compas_3_4 = tk.Radiobutton(
            self.frame_compas, text="3/4",
            variable=self.compas_seleccionado, value=3)
        self.compas_4_4 = tk.Radiobutton(
            self.frame_compas, text="4/4",
            variable=self.compas_seleccionado, value=4)

    def aparecer(self):
        self.ventana.config(menu=self.barra_menu)

        self.boton_tap.grid(row=0, column=0)
        self.frame_superior.grid(row=0, column=1)
        self.desplegable_notas.grid(row=1, column=0)
        self.frame_compas.grid(row=1, column=1)

        self.deslizable_bpm.pack(side=tk.LEFT)
        self.etiqueta_bpm.pack(side=tk.LEFT)
        self.boton.pack(side=tk.RIGHT)

        self.no_compas.pack(side=tk.LEFT)
        self.compas_2_4.pack(side=tk.LEFT)
        self.compas_3_4.pack(side=tk.LEFT)
        self.compas_4_4.pack(side=tk.LEFT)

        # Atajos de teclado
        self.ventana.bind("t", self.tapping)
        self.ventana.bind("<space>", self.accion_boton)
        self.ventana.bind("q", self.guardado)
        self.ventana.bind("<Left>", self.decrementar_bpm)
        self.ventana.bind("<Right>", self.incrementar_bpm)

        # En caso de que el usuario cierre el programa
        self.ventana.protocol("WM_DELETE_WINDOW", self.guardado)
        self.ventana.mainloop()

    def accion_boton(self, *args):
        if self.sonando:
            self.boton.config(text="Iniciar")
            self.boton_tap.config(state=tk.NORMAL)  # Restaura TAP
            self.ventana.bind("t", self.tapping)
            self.sonando = False
        else:
            self.boton.config(text="Parar")
            self.boton_tap.config(state=tk.DISABLED)  # Inhabilita TAP
            self.ventana.unbind("t")
            self.sonando = True

    def tapping(self, *args):
        if self.t1 == 0:
            self.t1 = time.time()
        else:
            self.t2 = time.time()
            self.bpm_seleccionado.set(int(60 / (self.t2 - self.t1)))
            self.t1 = 0
            self.t2 = 0

    def guardado(self, *args):
        self.configuracion.escribir_archivo()
        self.seguir_abierto = False
        self.ventana.destroy()

    def incrementar_bpm(self, *args):
        if self.bpm_seleccionado.get() + 1 <= BPM_MAXIMO:
            self.bpm_seleccionado.set(self.bpm_seleccionado.get()+1)

    def decrementar_bpm(self, *args):
        if self.bpm_seleccionado.get() - 1 >= BPM_MINIMO:
            self.bpm_seleccionado.set(self.bpm_seleccionado.get()-1)

    def ayuda(self):
        mensaje = """No es mi culpa si no
consigues seguir el tempo.
Haberte hecho vocalista."""
        messagebox.showinfo("Ayuda", mensaje)

    def ayuda_atajos(self):
        mensaje = """Atajos de teclado:

q -> Salir
t -> TAP
espacio -> Iniciar/Parar
flechas -> +/- BPMs"""
        messagebox.showinfo("Atajos de teclado", mensaje)

    def licencia(self):
        webbrowser.open("https://www.gnu.org/licenses/gpl.html")

    def acerca_de(self):
        messagebox.showinfo("Acerca de", "Metrómono v." + VERSION)


a = Gui()


def proceso_gui():
    a.aparecer()


def proceso_backend():
    backend = Tick()
    while(a.seguir_abierto):
        if (a.sonando):
            # Preparo el tick y guardo la configuración para caso de cierre
            backend.compas = a.configuracion.compas = a.compas_seleccionado.get()
            backend.bpm = a.configuracion.bpm = a.bpm_seleccionado.get()
            backend.frecuencia = FRECUENCIAS[a.nota_seleccionada.get()]
            a.configuracion.nota = a.nota_seleccionada.get()
            backend.tick()
        else:
            time.sleep(0.01)  # Para que al procesador no le de algo


hilo_backend = Thread(target=proceso_backend)
hilo_backend.start()

proceso_gui()
