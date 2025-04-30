import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from rembg import new_session, remove
import numpy as np
import cv2
import io
import os

# Sessão com modelo avançado
session = new_session("isnet-general-use")

# Variáveis globais
imagem_original = None
imagem_resultado = None

def escolher_imagem():
    caminho = filedialog.askopenfilename(
        title="Escolha uma imagem",
        filetypes=[("Imagens", "*.png *.jpg *.jpeg")]
    )
    if caminho:
        remover_fundo(caminho)

def suavizar_bordas(imagem_pil, intensidade=5):
    imagem_np = np.array(imagem_pil)
    alpha = imagem_np[:, :, 3]
    ksize = max(1, int(intensidade) // 2 * 2 + 1)  # Garante ímpar
    alpha = cv2.GaussianBlur(alpha, (ksize, ksize), 0)
    imagem_np[:, :, 3] = alpha
    return Image.fromarray(imagem_np)

def remover_fundo(caminho_imagem):
    global imagem_original, imagem_resultado
    try:
        with open(caminho_imagem, 'rb') as f:
            input_data = f.read()

        output_data = remove(input_data, session=session)
        imagem_original = Image.open(io.BytesIO(output_data)).convert("RGBA")
        imagem_resultado = imagem_original

        atualizar_imagem()
        salvar_btn.config(state=tk.NORMAL)
        slider.config(state=tk.NORMAL)
        mostrar_imagens_comparacao()

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def atualizar_imagem(event=None):
    intensidade = slider.get()
    imagem_editada = suavizar_bordas(imagem_resultado, intensidade=intensidade)
    imagem_editada.thumbnail((300, 300))
    imagem_tk = ImageTk.PhotoImage(imagem_editada)
    rotulo_imagem_resultado.config(image=imagem_tk)  # Corrigido aqui
    rotulo_imagem_resultado.image = imagem_tk  # Corrigido aqui


def mostrar_imagens_comparacao():
    if imagem_original and imagem_resultado:
        imagem_original.thumbnail((150, 150))
        imagem_resultado.thumbnail((150, 150))

        imagem_original_tk = ImageTk.PhotoImage(imagem_original)
        imagem_resultado_tk = ImageTk.PhotoImage(imagem_resultado)

        rotulo_imagem_original.config(image=imagem_original_tk)
        rotulo_imagem_original.image = imagem_original_tk
        rotulo_imagem_resultado.config(image=imagem_resultado_tk)
        rotulo_imagem_resultado.image = imagem_resultado_tk

def salvar_imagem():
    intensidade = slider.get()
    imagem_final = suavizar_bordas(imagem_resultado, intensidade=intensidade)

    salvar_como = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("Imagem PNG", "*.png")],
        title="Salvar imagem sem fundo"
    )

    if salvar_como:
        imagem_final.save(salvar_como)
        messagebox.showinfo("Sucesso", "Imagem salva com sucesso!")

def resetar_imagem():
    global imagem_resultado
    imagem_resultado = imagem_original
    atualizar_imagem()

def alternar_tema():
    global tema_escuro
    if tema_escuro:
        janela.config(bg='white')
        slider.config(bg='white', fg='black')
        rotulo_imagem_original.config(bg='white')
        rotulo_imagem_resultado.config(bg='white')
        salvar_btn.config(bg='lightgray')
        tema_escuro = False
    else:
        janela.config(bg='black')
        slider.config(bg='black', fg='white')
        rotulo_imagem_original.config(bg='black')
        rotulo_imagem_resultado.config(bg='black')
        salvar_btn.config(bg='darkgray')
        tema_escuro = True

def mostrar_tempo_processo(inicio, fim):
    tempo = fim - inicio
    tempo_label.config(text=f"Tempo de processamento: {tempo:.2f} segundos")

# Interface
janela = tk.Tk()
janela.title("Removedor de Fundo Aprimorado")
janela.geometry("700x550")

# Tema escuro ou claro
tema_escuro = False

# Botões
btn_escolher = tk.Button(janela, text="Escolher Imagem", command=escolher_imagem)
btn_escolher.pack(pady=10)

# Exibição de imagem comparativa
frame_comparacao = tk.Frame(janela)
frame_comparacao.pack(pady=10)

rotulo_imagem_original = tk.Label(frame_comparacao)
rotulo_imagem_original.grid(row=0, column=0, padx=10)

rotulo_imagem_resultado = tk.Label(frame_comparacao)
rotulo_imagem_resultado.grid(row=0, column=1, padx=10)

# Suavização
tk.Label(janela, text="Suavização das Bordas:").pack(pady=5)
slider = tk.Scale(janela, from_=0, to=20, orient=tk.HORIZONTAL, command=atualizar_imagem)
slider.set(5)
slider.config(state=tk.DISABLED)
slider.pack()

# Botão salvar
salvar_btn = tk.Button(janela, text="Salvar Imagem", command=salvar_imagem, state=tk.DISABLED)
salvar_btn.pack(pady=10)

# Botão resetar
resetar_btn = tk.Button(janela, text="Resetar Imagem", command=resetar_imagem)
resetar_btn.pack(pady=5)

# Botão alternar tema
alternar_tema_btn = tk.Button(janela, text="Alternar Tema", command=alternar_tema)
alternar_tema_btn.pack(pady=5)

# Exibir tempo de processamento
tempo_label = tk.Label(janela, text="Tempo de processamento: 0.00 segundos")
tempo_label.pack(pady=10)

# Iniciar a interface
janela.mainloop()