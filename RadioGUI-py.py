#!/usr/bin/python3.9

from tkinter import Button
from tkinter import Tk
from tkinter import Frame
from tkinter import Label
from tkinter import PhotoImage
from tkinter import Entry
from tkinter import StringVar
from tkinter import Scale
from tkinter import IntVar
from tkinter import messagebox
from tkinter.ttk import Combobox
import vlc
import radios



class Radio(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.salir) #  Que hacer al cerrar la ventana
        self.instance = vlc.Instance() #  Instancia el vlc
        self.player = self.instance.media_player_new()
        self.vista() 

    def vista(self):
        # Vista principal
        self.parent.title("RadioGUI-py") #  Titulo ventana
        self.parent.iconphoto(True, PhotoImage(file="icono.png")) # Icono
        vent_x = self.parent.winfo_screenwidth() // 2 - 200 // 2 # Tamaño
        vent_y = self.parent.winfo_screenheight() // 2 - 150 // 2 # Tamaño
        tam_y_pos = "200x" + "150+" + str(vent_x) + "+" + str(vent_y) # Posicion
        self.parent.geometry(tam_y_pos)  # Ancho, largo y posicion
        self.parent.resizable(False, False) # Redimensionable en ancho y largo, no
        self.parent.bind("<KeyPress-Escape>", self.salir) # Cerrar la ventana al precionar ESC
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
            values=(self.radios_()),
        )
        self.radio_selecionada.place(x=10, y=40)
        
        self.vol_muted = False # No muted
        self.vol_var = IntVar() 
        self.vol_var.set(100) # Set vol inicial
        # Volumen
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

        # Boton play / stop
        self.boton_play = Button(
            self.frame1,
            width = 8,
            text="Reproducir",
            command=self.play_,
        )
        self.boton_play.place(x=10, y=115)
        # Boton agregar
        self.boton_add = Button(self.frame1, text="Agregar", command=self.add_)
        self.boton_add.place(x=110, y=115)

    def play_(self):
        # Inicia o detiene la reproduccion
        if self.radio_selecionada.get():
            if self.play1:
                self.play1 = False
                self.boton_play.config(text="Parar") # Set text boton
                radio_s = self.radio_selecionada.get()
                media = self.instance.media_new(radios.radio[radio_s])
                self.player.set_media(media)
                self.player.play()
            else:
                self.play1 = True
                self.player.stop()
                self.boton_play.config(text="Reproducir") # Set text boton

    def add_(self):
        # Segunda vista, agregar o modificar radio
        if self.play1:

            def obtener(self, *args):
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
                width=22,
                values=(self.radios_()),
                textvariable=self.nombre,
            )
            self.r_selecionada.place(x=0, y=25)

            self.label2 = Label(self.frame2, text="Link de la radio:")
            self.label2.place(x=0, y=50)

            self.l_selecionada = Entry(
                self.frame2,
                width=22,
                textvariable=self.link,
            )
            self.l_selecionada.place(x=0, y=75)

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

            self.nombre.trace("w", obtener)

    def guardar_r(self):
        # Actualiza o guarda una entrada nueva en el dicionario
        if self.nombre.get() and self.link.get():
            # Actualiza el dicionario
            if self.nombre.get() in self.radios_():
                print("Actualizando")
                actu_dic = {self.nombre.get(): self.link.get()}
                radios.radio.update(actu_dic)
            # Crea una nueva entrada en el dicionario
            else:
                print("Guardando")
                radios.radio[self.nombre.get()] = self.link.get()
            # Guarda el dicionario
            rd = radios.radio
            file_dicty = open("radios.py", "wt")
            file_dicty.write("radio = " + str(rd))
            file_dicty.close()
        else:
            messagebox.showinfo(
                title="Campos incompletos",
                message="Debe ingresar el nombre la radio y su link",
            )
        self.frame2.destroy()
        self.vista()

    def eliminar_r(self):
        if self.nombre.get():
            # elimina el nombre selecionado del dicionario
            eli_cat = messagebox.askyesno(
                message=f"Eliminar a: {self.nombre.get()}?",
                title="Borrar radio",
            )
            if eli_cat:
                print("Eliminado")
                valor = self.nombre.get()
                rd = radios.radio
                rd.pop(valor)
                file_dicty = open("radios.py", "wt")
                file_dicty.write("radio = " + str(rd))
                file_dicty.close()
        else:
            messagebox.showinfo(
                title="Campos incompletos",
                message="Debe seleccionar la radio a eliminar",
            )
        self.frame2.destroy()
        self.vista()

    def radios_(self):
        # Devuelve una lista con las radios
        radio_lista = []
        valores = radios.radio.keys()
        for i in valores:
            radio_lista.append(i)
        return radio_lista

    def volumen(self, *args):
        # Configura el volumen
        vol = min(self.vol_var.get(), 100)
        v_m = "%d%s" % (vol, " Mute" if self.vol_muted else "")
        self.vol_cont.config(label="Volumen: " + v_m)
        self.player.audio_set_volume(vol)

    def salir(self, *args):
        # Que hacer al salir
        if not self.play1:
            self.player.stop()
        self.parent.quit()
        self.parent.destroy()
        print("Saliendo del programa")


if __name__ == "__main__":
    root = Tk()
    Radio(root)
    root.mainloop()

# final del camino
