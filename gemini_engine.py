# -*- coding: utf-8 -*-

import os
from google import genai


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def gerar_analise_economica(self, titulo, resumo, categoria):

        prompt = f"""
Atue como um Economista Sênior (PhD) com foco em análise de dados e estratégia macroeconômica.

Objetivo: Realize uma varredura nos principais portais de notícias e bancos de dados financeiros
(como Bloomberg, Reuters, Financial Times, Valor Econômico e sites de Bancos Centrais) para extrair 
os fatos mais relevantes das últimas 24 horas.

Informações base:

Título da resenha: {titulo}

Resumo da resenha:
{resumo}

Categoria: {categoria}

Diretrizes Obrigatórias:

Tom e Estilo: Imparcial, técnico e analítico. Use linguagem clara, objetiva e evite adjetivos desnecessários ou termos sensacionalistas.

Extensão: Mínimo de 700 palavras. Desenvolva os parágrafos com profundidade.

Originalidade: O texto deve ser inédito, processando as informações e reescrevendo-as com uma narrativa própria (sem plágio).

Isenção: Proibido emitir opinião pessoal ou usar primeira pessoa. Se houver controvérsias, apresente os dois lados de forma equilibrada.

Estrutura do Texto:

Título: Chamativo, porém informativo e sóbrio.

Lide (Lead): O primeiro parágrafo deve responder: Quem? O quê? Onde? Quando? Por quê? e Como?

Subtítulos: Utilize pelo menos dois subtítulos para organizar a progressão temática do texto.

Corpo: Desenvolva os fatos de forma cronológica ou por relevância de impacto.

Conclusão Analítica: Encerre com uma análise técnica sobre as implicações futuras ou o desdobramento esperado dos fatos, sem cair no opinativo subjetivo.

Importante:
- Não escreva explicações externas.
- Não inclua observações adicionais.
- Entregue apenas o texto final já estruturado.
"""


        response = self.client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()
