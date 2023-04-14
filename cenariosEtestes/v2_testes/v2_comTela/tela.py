from tkinter import *

class Aplicacao:
    def __init__(self, master=None):
        master.title("janela1")
        self.container1 = Frame(master)
        self.container1.pack(side=TOP)
        self.container1["width"]=200
        self.container1["height"]=50
        self.msg = Label(self.container1, text="Switches")
        self.msg.pack()
        
        self.container2 = Frame(master)
        self.container2.pack(side="bottom")
        self.container2["width"]=200
        self.container2["height"]=200

        self.texto = Text(self.container2, height=20, width=60)

        self.scroll_bar= Scrollbar(self.container2, orient="vertical", command=self.texto.yview)
        self.scroll_bar.pack(side=RIGHT)

        self.texto.configure(yscrollcommand=self.scroll_bar.set)
        self.texto.pack(side=LEFT)
        
        texto = """ - Inicio -"""
        self.texto.insert(END, texto)
        self.texto.configure(state='disable')

        self.botoes = []
        self.addButton('s1')

        #self.botoes.append(Button(self.container1, text= "addTexto", command = self.testarTexto).pack())
        self.botoes.append(Button(self.container1, text= "addTexto", command = self.addButton).pack())

        self.Janela2=None

    def testarTexto(self):
        self.texto.configure(state='normal')
        self.texto.insert(END, "aaa\n")
        self.texto.see("end")
        self.texto.configure(state='disable')

    def addButton(self, texto='textoqq'):
        self.botoes.append(Button(self.container1, text= texto, command = lambda m=texto:self.novaTela(m)).pack())

    def addTexto(self, texto=''):
        self.texto.configure(state='normal')
        self.texto.insert(END, texto)
        self.texto.see("end")
        self.texto.configure(state='disable')

    def novaTela(self, switch):
        #esconder o root
        #root.withdraw()

        print("[novaTela]clicou\n")
        novaTela=Tk()

        novaTela.geometry("500x500")

        Janela2(master=novaTela, switch=switch)
        novaTela.mainloop()

class Janela2:
    def __init__(self, master=None, switch=None):
        if switch == None:
            self.voltar()

        master.title(switch)
        self.master=master
        self.container1 = Frame(master)
        self.container1.pack(side=TOP)
        self.botao1 = Button(self.container1, text= 'Voltar', command = self.voltar).pack()
        self.container2 = Frame(master)
        self.container2.pack(side="bottom")
        self.container2["width"]=200
        self.container2["height"]=200

        self.texto = Text(self.container2, height=20, width=60)

        self.scroll_bar= Scrollbar(self.container2, orient="vertical", command=self.texto.yview)
        self.scroll_bar.pack(side=RIGHT)

        self.texto.configure(yscrollcommand=self.scroll_bar.set)
        self.texto.pack(side=LEFT)
        
        texto = """ - Inicio - """
        self.texto.insert(END, texto)
        self.texto.configure(state='disable')

    def addTexto(self, texto=''):
        self.texto.configure(state='normal')
        self.texto.insert(END, texto)
        self.texto.see("end")
        self.texto.configure(state='disable')

    def voltar(self):

        print("[voltar]clicou\n")
        #mostrar root
        #root.deiconify()

        #destruir a nova tela
        self.master.destroy()

root = Tk()
root.geometry("500x500")

Aplicacao(root)
root.mainloop()