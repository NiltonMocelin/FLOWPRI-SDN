from tkinter import *

root = Tk()
root.geometry("500x500")

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
        
        texto = """his is a multiline string.
We can write this in multiple lines too!
Hello from AskPython. This is the third line.
This is the fourth line. Although the length of the text is longer than
the width, we can use tkinter's scrollbar to solve this problem! """
        self.texto.insert(END, texto)
        self.texto.configure(state='disable')

        self.botoes = []
        self.botoes.append(Button(self.container1, text= 'Switch1', command = self.novaTela).pack())

        #self.botoes.append(Button(self.container1, text= "addTexto", command = self.testarTexto).pack())
        self.botoes.append(Button(self.container1, text= "addTexto", command = self.addButton).pack())

    def testarTexto(self):
        self.texto.configure(state='normal')
        self.texto.insert(END, "aaa\n")
        self.texto.see("end")
        self.texto.configure(state='disable')

    def addButton(self, texto='textoqq'):
        self.botoes.append(Button(self.container1, text=texto, command= self.testarTexto).pack())

    def novaTela(self):
        #esconder o root
        #root.withdraw()

        print("[novaTela]clicou\n")
        novaTela=Tk()

        novaTela.geometry("500x500")

        Janela2(novaTela)
        novaTela.mainloop()

class Janela2:
    def __init__(self, master=None):
        master.title("janela2")
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
        
        texto = """his is a multiline string.
We can write this in multiple lines too!
Hello from AskPython. This is the third line.
This is the fourth line. Although the length of the text is longer than
the width, we can use tkinter's scrollbar to solve this problem! """
        self.texto.insert(END, texto)
        self.texto.configure(state='disable')

    def voltar(self):

        print("[voltar]clicou\n")
        #mostrar root
        #root.deiconify()

        #destruir a nova tela
        self.master.destroy()

Aplicacao(root)
root.mainloop()