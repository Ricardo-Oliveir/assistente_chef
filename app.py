import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError
from PIL import Image

# --- Configuração Inicial ---
st.set_page_config(
    page_title="Chef Assistente Multimodal",
    page_icon="📸",
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

# --- Função de Caching (Otimização de Performance) ---
@st.cache_data(show_spinner="📸 Analisando a imagem e criando a receita (pode levar alguns segundos)...")
def gerar_receita(ingredientes_input, uploaded_image=None):
    """
    Gera uma receita usando o modelo Gemini 2.5 Flash, aceitando imagem ou texto.
    """
    
    # 1. Definição da Persona/Instrução do Sistema
    system_prompt = """
    Você é um Chef Assistente profissional, criativo e amigável.
    Sua tarefa é criar uma receita completa e deliciosa baseada APENAS nos ingredientes que você identificar no INPUT.

    **Regras:**
    1. Se uma IMAGEM for fornecida, IDENTIFIQUE todos os ingredientes comestíveis e use-os. Ignore caixas, embalagens ou texto não comestível.
    2. Se apenas TEXTO for fornecido, use o texto.
    3. A receita deve ser clara, passo a passo, e fácil de seguir.
    4. A saída DEVE ser formatada usando Markdown com títulos e subtítulos (Ex: '# Título', '## Ingredientes', '## Modo de Preparo').
    5. Inclua um tempo de preparo estimado no início da receita.
    6. Crie uma sugestão de nome criativo para o prato.
    """
    
    # 2. Definição do Conteúdo (Input Multimodal)
    contents = []
    
    if uploaded_image:
        contents.append(uploaded_image)
        user_prompt_text = (
            "Analise esta imagem. Crie uma receita completa usando APENAS os ingredientes comestíveis identificados."
        )
    else:
        user_prompt_text = (
            f"Crie uma receita completa usando os seguintes ingredientes disponíveis:\n\n"
            f"Ingredientes: {ingredientes_input}\n\n"
        )
    
    contents.append(user_prompt_text)
    
    # 3. Execução da Chamada à API com Tratamento de Erro
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            ),
        )
        return response.text
    except APIError as e:
        st.error(f"Erro na API Gemini: Falha ao gerar conteúdo. Verifique se o modelo 'gemini-2.5-flash' está disponível e a chave está correta. Detalhes: {e}")
        return "Desculpe, não foi possível gerar a receita devido a um erro na comunicação com a API."
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        return "Ocorreu um erro desconhecido durante a geração da receita."


# --- Interface do Usuário (UI) ---

st.title("📸 Chef Assistente Multimodal")
st.markdown("---")

st.subheader("Como você quer gerar a receita?")
st.markdown("Escolha a opção mais fácil para você:")

# Opção 1: Upload de Imagem/Foto (Prioritário)
uploaded_file = st.file_uploader(
    "1. Tire ou Envie uma Foto da sua Geladeira/Despensa:",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False,
    help="DICA: No celular, este botão permite abrir a câmera para tirar uma foto na hora!"
)

image = None
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption='Sua foto de ingredientes.', use_column_width=True)
    except Exception as e:
        st.error(f"Não foi possível processar a imagem. Erro: {e}")

    # Botão de Ação para Imagem
    if st.button("✨ Gerar Receita com Base na Foto!", type="primary", use_container_width=True):
        if image:
            receita = gerar_receita(ingredientes_input="", uploaded_image=image)
            st.markdown("---")
            st.success("Receita Gerada por Análise de Imagem!")
            st.markdown(receita)
        else:
             st.warning("Imagem inválida ou não carregada.")


# Opção 2: Entrada de Texto (Fallback)
st.markdown("---")
st.markdown("**OU**")

ingredientes_texto = st.text_input(
    "2. Digite os Ingredientes (Se não quiser enviar foto):",
    placeholder="Ex: tomate, ovos, queijo, pão, cebola, azeite"
)

# Botão de Ação para Texto
if st.button("✨ Gerar Receita por Texto!", type="secondary", use_container_width=True):
    if ingredientes_texto:
        receita = gerar_receita(ingredientes_input=ingredientes_texto, uploaded_image=None)
        st.markdown("---")
        st.success("Receita Gerada por Texto!")
        st.markdown(receita)
    else:
        st.warning("Por favor, insira pelo menos um ingrediente ou envie uma foto para começar.")

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
        Desenvolvido  por Ricardo Oliveira usando Google Gemini API e Streamlit 
                </div>
    """, 
    unsafe_allow_html=True
)