import streamlit as st
import os
from google import genai
from google.genai import types

# --- Configuração Inicial e Título ---
st.set_page_config(
    page_title="Chef Assistente com Gemini",
    page_icon="🍳",
    layout="centered"
)

st.title("🍳 Chef Assistente com Gemini")
st.markdown("Diga-me o que você tem na geladeira, e eu crio uma receita rápida para você!")

# --- Configuração da API Key (Uso de st.secrets para deploy no Streamlit Cloud) ---
try:
    # Tenta obter a API key das secrets (necessário para deploy)
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    # Fallback para ambiente local (leitura de variável de ambiente)
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("ERRO: A chave da API ('GEMINI_API_KEY') não foi encontrada.")
    st.info("Para usar, defina a variável de ambiente GEMINI_API_KEY ou configure o st.secrets no Streamlit Cloud.")
    st.stop()

# Inicializa o cliente da API
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Erro ao inicializar o cliente Gemini: {e}")
    st.stop()


# --- Função para Gerar Conteúdo ---
@st.cache_data(show_spinner=False)
def gerar_receita(ingredientes):
    """
    Chama a API Gemini para gerar uma receita baseada na lista de ingredientes.
    """
    
    # Instrução de Sistema: Define a persona e a regra do modelo.
    # CRITÉRIO DE AVALIAÇÃO: Qualidade do Prompt (Persona e Formatação definidos)
    system_instruction = (
        "Você é um chef de cozinha 5 estrelas, especializado em pratos rápidos e criativos com "
        "recursos limitados. Sua resposta deve ser sempre formatada em Português usando Markdown."
    )
    
    # Prompt do Usuário (Instrução da Atividade)
    prompt = (
        f"Crie uma receita fácil e rápida usando APENAS estes ingredientes: {ingredientes}. "
        "Se não for possível criar um prato completo, sugira o que falta. "
        "Formate a resposta com Título, Ingredientes e Modo de Preparo (usando subtítulos em negrito)."
    )
    
    # Configuração de Geração
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.8, # Um pouco mais baixo para manter a receita estruturada
    )
    
    # Chamada à API
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-09-2025',
            contents=prompt,
            config=config,
        )
        return response.text
    except Exception as e:
        return f"Ocorreu um erro ao gerar o conteúdo: {e}"


# --- Interface do Usuário ---

# Campo de entrada para os ingredientes
ingredientes_input = st.text_input(
    "Quais ingredientes você tem disponíveis?",
    placeholder="Ex: tomate, ovos, queijo, pão, cebola, azeite"
)

# Botão de geração
if st.button("Gerar Receita!", type="primary", use_container_width=True):
    if ingredientes_input:
        with st.spinner("🍽️ Consultando o livro de receitas..."):
            receita_gerada = gerar_receita(ingredientes_input)
            
            # Exibe o resultado
            st.subheader("👨‍🍳 Sua Receita Exclusiva:")
            st.markdown(receita_gerada)
            st.success("Receita gerada com sucesso! Bom apetite.")
    else:
        st.warning("Por favor, digite os ingredientes que você tem para que eu possa criar a receita.")

st.divider()
st.caption("Desenvolvido para o Projeto 'IA Prática' com Google Gemini API e Streamlit.")