import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuração Inicial ---
st.set_page_config(
    page_title="Chef Assistente",
    page_icon="🍳",
    layout="centered"
)

# Tenta carregar a chave da API dos segredos do Streamlit
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("ERRO: A chave da API 'GEMINI_API_KEY' não foi encontrada nos Streamlit Secrets.")
    st.info("Por favor, verifique se a chave está configurada corretamente nas Configurações Avançadas do Streamlit Cloud.")
    st.stop()

# Inicialização do Cliente Gemini
client = genai.Client(api_key=API_KEY)

# --- Função de Geração de Receita (com Caching) ---
@st.cache_data(show_spinner="🍳 Criando sua receita deliciosa...")
def gerar_receita(ingredientes_input):
    """
    Gera uma receita usando o modelo Gemini 2.5 Flash, baseada em texto.
    """
    
    # 1. Definição da Persona/Instrução do Sistema
    system_prompt = """
    Você é um Chef Assistente profissional, criativo e amigável.
    Sua tarefa é criar uma receita completa e deliciosa baseada APENAS nos ingredientes fornecidos.

    **Regras:**
    1. A receita deve ser clara, passo a passo, e fácil de seguir.
    2. A saída DEVE ser formatada usando Markdown com títulos e subtítulos (Ex: '# Título', '## Ingredientes', '## Modo de Preparo').
    3. Inclua um tempo de preparo estimado no início da receita.
    4. Crie uma sugestão de nome criativo para o prato.
    """
    
    # 2. Definição do Conteúdo (Input de Texto)
    user_prompt_text = (
        f"Crie uma receita completa usando os seguintes ingredientes disponíveis:\n\n"
        f"Ingredientes: {ingredientes_input}\n\n"
    )
    
    # 3. Execução da Chamada à API com Tratamento de Erro
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_prompt_text],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return response.text
    except APIError as e:
        st.error(f"Erro na API Gemini: Falha ao gerar conteúdo. Detalhes: {e}")
        st.info("Se o erro for '503 UNAVAILABLE', o servidor está sobrecarregado. Tente novamente em 1 minuto.")
        return "Desculpe, não foi possível gerar a receita devido a um erro na comunicação com a API."
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        return "Ocorreu um erro desconhecido durante a geração da receita."


# --- Interface do Usuário (UI) ---

st.title("🍳 Chef Assistente")
st.markdown("---")

st.subheader("O que você tem na sua geladeira?")
st.markdown("Liste os ingredientes que você gostaria de usar para criarmos uma receita deliciosa.")


ingredientes_texto = st.text_input(
    "1. Digite seus Ingredientes:",
    placeholder="Ex: tomate, ovos, queijo, pão, cebola, azeite"
)

# Botão de Ação para Texto
if st.button("✨ Gerar Receita!", type="primary", use_container_width=True):
    if ingredientes_texto:
        # Chama a função de geração de receita
        receita = gerar_receita(ingredientes_input=ingredientes_texto)
        st.markdown("---")
        st.success("Receita Gerada!")
        st.markdown(receita)
    else:
        st.warning("Por favor, insira pelo menos um ingrediente para começar.")

# Gerenciamento de Cache
st.markdown("---")
if st.button("Limpar Cache e Recomeçar"):
    st.cache_data.clear()
    st.rerun()

# Rodapé
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        color: gray;
        text-align: center;
        padding: 10px;
        font-size: 0.8em;
    }
    </style>
    <div class="footer">
        Desenvolvido por  Ricardo Oliveira  Aplicação com API de IA em publicação no Streamlit.
    </div>
    """, 
    unsafe_allow_html=True
)