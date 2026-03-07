# -*- coding: utf-8 -*-

import os
import re
import time
from google import genai
from google.api_core import exceptions
from configuracoes import MODELO_GEMINI, MIN_PALAVRAS, MAX_PALAVRAS

class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        # Estratégia de Fallback solicitada: 3 Modelos em 3 Ciclos
        self.modelos_fallback = [
            "gemini-3-flash-preview",
            "gemini-2.5-pro", 
            "gemini-2.5-flash"
        ]

    def gerar_analise_economica(self, titulo, resumo, tema):
        """
        Interface principal chamada pelo run_bot.py.
        Prepara o prompt e executa a lógica de resiliência.
        """
        prompt = f"""
        Aja como um analista sênior de {tema}. 
        Escreva um artigo profundo e profissional sobre: {titulo}.
        Use como base as seguintes informações: {resumo}.
        Regras obrigatórias:
        - Mínimo de {MIN_PALAVRAS} palavras e máximo de {MAX_PALAVRAS}.
        - NÃO repita o título da notícia no início do texto.
        - Use Markdown apenas para separar seções com subtítulos.
        - O tom deve ser informativo e analítico.
        """
        
        texto_gerado = self._executar_com_resiliencia(prompt)
        
        if texto_gerado:
            return self._limpar_e_formatar_markdown(texto_gerado)
        return "Erro: Não foi possível gerar o conteúdo após 9 tentativas."

    def _limpar_e_formatar_markdown(self, texto):
        """
        Transforma negritos Markdown em HTML <strong> e remove marcadores de título e lista.
        """
        if not texto:
            return ""
            
        # 1. Transforma **texto** em <strong>texto</strong>
        texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
        
        # 2. Suprime os marcadores de título #, ##, ###, etc.
        texto = re.sub(r'#+\s?', '', texto)
        
        # 3. Suprime asteriscos isolados (marcadores de lista ou itálico simples)
        texto = re.sub(r'^\s*\*\s?', '', texto, flags=re.MULTILINE)
        texto = texto.replace('*', '')
        
        return texto.strip()

    def _executar_com_resiliencia(self, prompt):
        """
        Lógica de 9 tentativas (3 ciclos x 3 modelos) conforme solicitado.
        """
        tentativa_total = 1
        for ciclo in range(1, 4):  # 3 passagens completas
            for modelo in self.modelos_fallback:
                try:
                    print(f"Tentativa {tentativa_total}/9 | Ciclo {ciclo} | Usando: {modelo}")
                    
                    response = self.client.models.generate_content(
                        model=modelo,
                        contents=prompt
                    )

                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                
                except Exception as e:
                    erro_msg = str(e).upper()
                    if any(x in erro_msg for x in ["503", "UNAVAILABLE", "DEADLINE", "429", "QUOTA"]):
                        print(f"⚠️ Modelo {modelo} indisponível ou lotado. Tentando próximo...")
                        time.sleep(5) 
                    else:
                        print(f"❌ Erro no modelo {modelo}: {e}")
                
                tentativa_total += 1
        
        return None

# ==========================================================
# FUNÇÕES DE FORMATAÇÃO (PADRÃO OURO)
# ==========================================================

def formatar_texto(texto, titulo_principal):
    """
    Processa o corpo do texto: H2 para subtítulos e P para parágrafos.
    Remove repetições do título principal dentro do corpo do texto.
    """
    if not texto:
        return ""
        
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    COR_MD = "rgb(7, 55, 99)"
    titulo_norm = titulo_principal.strip().lower()

    for linha in linhas:
        linha_limpa = linha.strip("#* ").strip()
        
        # Pula a linha se for repetição do título (limpeza inteligente)
        if linha_limpa.lower() == titulo_norm:
            continue

        # Ordem 5: Subtítulo H2 - Arial 20, Bold, Cor MD, Maiúsculas
        if linha.startswith("#") or (len(linha_limpa.split()) <= 15 and not linha_limpa.endswith(".")):
            html_final += f"""
            <h2 style="text-align:left !important; font-family:Arial !important; color:{COR_MD} !important; 
                       font-size:20px !important; font-weight:bold !important; text-transform:uppercase !important; 
                       margin-top:25px !important; margin-bottom:10px !important; display:block !important;">
                {linha_limpa}
            </h2>
            """
        else:
            # Ordem 6: Texto - Fonte 18, Justificado, Cor MD
            html_final += f"""
            <p style="text-align:justify !important; font-family:Arial !important; color:{COR_MD} !important; 
                      font-size:18px !important; line-height:1.7 !important; margin-bottom:15px !important;">
                {linha_limpa}
            </p>
            """
    return html_final

def obter_esqueleto_html(dados):
    """
    Gera o HTML final seguindo a Ordem 2 (Título via CSS) e Ordem 4 (Imagem 16:9).
    """
    titulo = dados.get("titulo", "").strip()
    imagem = dados.get("imagem", "").strip()
    texto_bruto = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    conteudo_formatado = formatar_texto(texto_bruto, titulo)
    COR_MD = "rgb(7, 55, 99)"

    return f"""
<style>
    /* Ordem 2: Controle do Título do Blogger via CSS */
    h1.post-title, h1.entry-title, h2.post-title, h3.post-title, .post-title {{
        text-align:center !important; 
        font-family:Arial, sans-serif !important; 
        font-size:28px !important; 
        font-weight:bold !important; 
        color:{COR_MD} !important; 
        text-transform:uppercase !important;
        margin-bottom:20px !important;
        display: block !important;
    }}
</style>

<div style="max-width:900px !important; margin:auto !important; font-family:Arial, sans-serif !important;">

    <div style="text-align:center !important; margin-bottom:25px !important;">
        <img src="{imagem}" style="width:100% !important; height:auto !important; aspect-ratio:16/9 !important; object-fit:cover !important; border-radius:8px !important; display:block !important; margin:auto !important;">
    </div>

    <div class="conteudo-post">
        {conteudo_formatado}
    </div>

    <div style="margin-top:40px !important; padding-top:20px !important; border-top:1px solid #eee !important;">
        {assinatura}
    </div>

</div>
"""
