from tkinter import *

root = Tk()
root.geometry("500x500")

class Aplicacao:
    def __init__(self, master=None):
        master.title("janela1")
        self.container1 = Frame(master)
        self.container1.pack(side=TOP)
        self.container1["width"]=200
        self.container1["height"]=200
        self.msg = Label(self.container1, text="container1")
        self.msg.pack()
        
        self.container2 = Frame(master)
        self.container2.pack(side=RIGHT)

        self.texto = Text(self.container2, height=5, width=40)

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

        self.botao1 = Button(self.container1, text= 'clique aqui', command = self.novaTela).pack()

        self.botao2 = Button(self.container2, text= "botao2", command = self.testarTexto).pack()

    def testarTexto(self):
        self.texto.insert(END, "aaa\n")
        self.texto.see("end")

    def novaTela(self):
        #esconder o root
        root.withdraw()

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
        self.botao1 = Button(self.container1, text= 'clique aqui', command = self.voltar).pack()

    def voltar(self):

        print("[voltar]clicou\n")
        #mostrar root
        root.deiconify()

        #destruir a nova tela
        self.master.destroy()

Aplicacao(root)
root.mainloop()