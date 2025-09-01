#!/usr/bin/python3.11

from tkinter import Button, Tk, Frame, Label, PhotoImage, Entry, StringVar, Scale, IntVar, messagebox, Toplevel
from tkinter.ttk import Combobox
from PIL import Image
from sys import exit
import os
import vlc
import radios
import pystray
import threading
import queue


class Radio(Frame):
    """Clase principal"""
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        # Llamo a la función para verificar la instancia única
        self.instancia_unica()
        # Mapeo la ruta absoluta de trabajo
        ruta_absoluta = os.path.split(os.path.abspath(__file__))[0]
        # Icono
        self.icono = ruta_absoluta + "/icono2.png"
        # Cerrar ventana
        self.parent.protocol("WM_DELETE_WINDOW", self.salir)
        self.instance = vlc.Instance("--no-video", "--aout=alsa")
        self.player = self.instance.media_player_new()
        # Crear una cola para manejar el cierre
        self.quit_queue = queue.Queue()
        # Iniciar el chequeo de la cola
        self.check_queue()
        self.vista()   

    def vista(self):
        """Vista principal, ubicacion de wwidget, configuracion de la ventana"""
        self.parent.title("RadioGUI-py")
        self.parent.iconphoto(True, PhotoImage(file=self.icono))
        vent_x = self.parent.winfo_screenwidth() // 2 - 200 // 2
        vent_y = self.parent.winfo_screenheight() // 2 - 150 // 2
        tam_y_pos = "200x" + "150+" + str(vent_x) + "+" + str(vent_y)
        self.parent.geometry(tam_y_pos)
        self.parent.resizable(False, False)
        # al presionar tecla Esc oculta la grafica
        self.parent.bind("<KeyPress-Escape>", self.ocultar)
        self.play1 = True

        # Frame 1
        self.frame1 = Frame(self.parent, height=200, width=200)
        self.frame1.place(x=0, y=0)
        self.label1 = Label(self.frame1, text="Elija su radio")
        self.label1.place(x=50, y=0)

        # Lista radios
        self.radio_selecionada = Combobox(
            self.frame1,
            width=20,
            state="readonly",
            values=self.radios_(),
        )
        self.radio_selecionada.bind("<<ComboboxSelected>>", lambda e: self.update_titulo())
        self.radio_selecionada.place(x=10, y=40)
        
        self.vol_muted = False
        self.vol_var = IntVar()
        self.vol_var.set(100)
        self.vol_cont = Scale(
            self.frame1,
            variable=self.vol_var,
            command=self.volumen,
            from_=0,
            to=100,
            orient="horizontal",
            length=170,
            showvalue=0,
            label="Volumen: 100",
        )
        self.vol_cont.place(x=10, y=60)

        self.boton_play = Button(
            self.frame1,
            width=8,
            text="Reproducir",
            command=self.play_,
        )
        self.boton_play.place(x=10, y=115)

        self.boton_add = Button(self.frame1, text="Agregar", command=self.add_)
        self.boton_add.place(x=110, y=115)

        # Crear el icono de la bandeja
        self.icon = pystray.Icon("RadioTrayIcon", Image.open(self.icono), "RadioGUI", menu=self.menu_icono_bandeja())
        threading.Thread(target=self.run_icon_bandeja).start()

    def update_titulo(self):
        """Actualizar el titulo del icono de la radio"""
        selected_radio = self.radio_selecionada.get()
        if selected_radio:
            self.icon.title = f"Radio Seleccionada: {selected_radio}"
        else:
            self.icon.title = "Selecciona una Radio"

    def play_(self):
        """Funcion de play/stop y actualizacion del nombre del boton"""
        if self.radio_selecionada.get():
            if self.play1:
                self.play1 = False
                self.boton_add.place_forget()
                self.boton_play.config(text="Parar")
                self.boton_play.config(width=19)
                radio_s = self.radio_selecionada.get()
                media = self.instance.media_new(radios.radio[radio_s])
                self.player.set_media(media)
                self.player.play()
            else:
                self.play1 = True
                self.player.stop()
                self.boton_play.config(text="Reproducir")
                self.boton_play.config(width=8)
                self.boton_add.place(x=110, y=115)
        else:
            messagebox.showwarning("Advertencia", "Seleccione una radio.")

    def add_(self):
        """Agregar una radio nueva, configuracion de la ventana agregar,
        widget de la ventana agregar, """
        if self.play1:
            def obtener(*args):
                try:
                    self.namae = radios.radio[self.nombre.get()]
                    self.link.set(self.namae)
                except KeyError:
                    pass
                except AttributeError:
                    pass

            self.link = StringVar()
            self.nombre = StringVar()

            self.frame2 = Frame(self.parent, height=200, width=200)
            self.frame2.place(x=0, y=0)

            self.label1 = Label(self.frame2, text="Nombre de la radio:")
            self.label1.place(x=0, y=0)

            self.r_selecionada = Combobox(
                self.frame2,
                width=21,
                values=self.radios_(),
                textvariable=self.nombre,
            )
            self.r_selecionada.place(x=5, y=25)

            self.label2 = Label(self.frame2, text="Link de la radio:")
            self.label2.place(x=0, y=50)

            self.l_selecionada = Entry(
                self.frame2,
                width=22,
                textvariable=self.link,
            )
            self.l_selecionada.place(x=5, y=75)

            self.boton_ag = Button(
                self.frame2,
                text="Agregar",
                command=self.guardar_r,
            )
            self.boton_ag.place(x=110, y=115)

            self.boton_rm = Button(
                self.frame2,
                text="Eliminar",
                command=self.eliminar_r,
            )
            self.boton_rm.place(x=10, y=115)

            self.nombre.trace_add("write", lambda *args: obtener())

    def guardar_r(self):
        """Guardar o editar una radio nueva"""
        if self.nombre.get() and self.link.get():
            if self.nombre.get() in self.radios_():
                print("Actualizando")
                actu_dic = {self.nombre.get(): self.link.get()}
                radios.radio.update(actu_dic)
            else:
                print("Guardando")
                radios.radio[self.nombre.get()] = self.link.get()
            rd = radios.radio
            with open("radios.py", "wt") as file_dicty:
                file_dicty.write("radio = " + str(rd))
        else:
            messagebox.showinfo(
                title="Campos incompletos",
                message="Debe ingresar el nombre la radio y su link",
            )
        self.frame2.destroy()

    def eliminar_r(self):
        """Eliminar una radio"""
        if self.nombre.get():
            eli_cat = messagebox.askyesno(
                message=f"Eliminar a: {self.nombre.get()}?",
                title="Borrar radio",
            )
            if eli_cat:
                print("Eliminado")
                valor = self.nombre.get()
                rd = radios.radio
                rd.pop(valor)
                with open("radios.py", "wt") as file_dicty:
                    file_dicty.write("radio = " + str(rd))
        else:
            messagebox.showinfo(
                title="Campos incompletos",
                message="Debe seleccionar la radio a eliminar",
            )
        self.frame2.destroy()

    def radios_(self):
        """Retorna las radios"""
        radio_lista = []
        valores = radios.radio.keys()
        for i in valores:
            radio_lista.append(i)
        return radio_lista

    def volumen(self, *args):
        """Volumen de la radio"""
        vol = min(self.vol_var.get(), 100)
        v_m = "%d%s" % (vol, " Mute" if self.vol_muted else "")
        self.vol_cont.config(label="Volumen: " + v_m)
        self.player.audio_set_volume(vol)

    def menu_icono_bandeja(self, mostrar_ocultar="Ocultar"):
        """Menu del icono de la bandeja de sistema"""
        return pystray.Menu(
            pystray.MenuItem("Play/Stop", self.play_),
            pystray.MenuItem("Acerca de", self.acerca),
            pystray.MenuItem(mostrar_ocultar, self.alternar_ventana),
            pystray.MenuItem("Salir", self.on_quit)
        )

    def run_icon_bandeja(self):
        """Correr icono"""
        self.icon.run()

    def alternar_ventana(self, icon, item):
        """Alternar entre mostrar y ocultar la ventana"""
        # Si la ventana está visible
        if self.parent.state() == "normal":
            self.ocultar()
            # Cambia el texto a "Mostrar"
            nuevo_texto = "Mostrar" 
        else:
            self.mostrar(icon, item)
            # Cambia el texto a "Ocultar"
            nuevo_texto = "Ocultar"

        # Actualizar el menú con el nuevo texto
        icon.menu = self.menu_icono_bandeja(mostrar_ocultar=nuevo_texto)

    def mostrar(self, icon, item):
        """Muestra la grafica"""
        self.parent.deiconify()
        self.parent.lift()
        self.update_titulo()

    def ocultar(self, *args):
        """Oculta la grafica"""
        # Oculta la ventana
        self.parent.withdraw()
        # Actualiza en texto en icono de la bandeja del sistema
        self.icon.menu = self.menu_icono_bandeja(mostrar_ocultar="Mostrar")

    def acerca(self, *args):
        """Muestra la ventana cerca de..."""
        # Crear una nueva ventana
        info_window = Toplevel(self.parent)
        info_window.title("Acerca de...")
        vent_x = self.parent.winfo_screenwidth() // 2 - 200 // 2
        vent_y = self.parent.winfo_screenheight() // 2 - 150 // 2
        tam_y_pos = "250x" + "260+" + str(vent_x) + "+" + str(vent_y)
        info_window.geometry(tam_y_pos)
        info_window.resizable(False, False)
        info_window.bind("<KeyPress-Escape>", lambda event: info_window.destroy())

        # Cargar un ícono o logo
        logo = PhotoImage(file=self.icono)

        # Etiqueta para mostrar el ícono
        logo_label = Label(info_window, image=logo)
        logo_label.image = logo
        logo_label.pack()

        # Etiqueta para mostrar el mensaje
        message_label = Label(info_window, anchor="w", text="Este es un programa que permite\nescuchar radios en línea.\nDesarrollado por due204\nContacto: due204@gmail.com")
        message_label.pack(pady=5)

        # Botón para cerrar la ventana
        close_button = Button(info_window, text="Cerrar", command=info_window.destroy)
        close_button.pack()

    
    def instancia_unica(self):
        """Verifica que se este ejecutando solamente una instancia del programa"""
        # Creo el archivo lock en el /tmp
        archivo_lock = '/tmp/radio_gui.lock'

        if os.path.exists(archivo_lock):
            print("RadioGUI-py ya está en ejecución.")
            # Salgo si el archivo lock ya existe
            exit(1)

        with open(archivo_lock, 'w') as f:
            # Escribo el PID en el archivo lock
            f.write(str(os.getpid()))

        def remuevo_archivo_lock():
            # Elimino el archivo lock
            os.remove(archivo_lock)

        # Me aseguro de que el archivo lock va a ser eliminado sin importar como se cierre la aplicacion
        import atexit
        atexit.register(remuevo_archivo_lock)

    def on_quit(self, icon, item):
        # Coloca un mensaje en la cola para salir
        self.quit_queue.put(True)

    def check_queue(self):
        try:
            while True:
                message = self.quit_queue.get_nowait()
                # Llama a la función de salida
                self.salir()  
        except queue.Empty:
            pass
        # Comprobar la cola de nuevo
        self.parent.after(100, self.check_queue) 

    def salir(self, *args):
        """Saliendo del programa"""
        if not self.play1:
            self.player.stop()
        self.icon.stop()
        # Usar after para asegurar que se llama en el hilo principal
        self.parent.after(0, self.parent.quit)
        self.parent.after(0, self.parent.destroy)
        print("Saliendo del programa")
        exit(0)


if __name__ == "__main__":
    root = Tk()
    Radio(root)
    root.mainloop()

# Final del camino. xD
