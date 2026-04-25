import streamlit as st
import sqlite3
from datetime import datetime
from streamlit_option_menu import option_menu

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Market Master",
    page_icon="🛒",
    layout="centered"
)

# ======================
# CSS PREMIUM
# ======================
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.block-container {
    padding-top: 1.5rem;
}
h1, h2, h3 {
    color: #f8fafc;
}
.card {
    background: #1e293b;
    padding: 16px;
    border-radius: 14px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.total-box {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    color: white;
    font-size: 24px;
    font-weight: bold;
}
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    font-weight: bold;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ======================
# BANCO
# ======================
conn = sqlite3.connect("feira.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS compras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT,
    preco REAL,
    quantidade INTEGER,
    mercado TEXT,
    data TEXT
)
""")
conn.commit()

# ======================
# HEADER + MENU
# ======================
st.title("🛒 Market Master")

selected = option_menu(
    menu_title=None,
    options=["Início", "Nova Feira", "Comparar"],
    icons=["house", "cart", "bar-chart"],
    default_index=0,
    orientation="horizontal",
)

# ======================
# INÍCIO
# ======================
if selected == "Início":

    from datetime import datetime

    # ======================
    # SAUDAÇÃO
    # ======================
    hora = datetime.now().hour

    if hora < 12:
        saudacao = "Bom dia ☀️"
    elif hora < 18:
        saudacao = "Boa tarde 🌤"
    else:
        saudacao = "Boa noite 🌙"

    st.markdown(f"## {saudacao}")
    st.markdown("### Bem-vindo ao Market Master")

    st.markdown("---")

    # ======================
    # BUSCAR ÚLTIMA COMPRA
    # ======================
    cursor.execute("""
        SELECT mercado, data 
        FROM compras
        ORDER BY id DESC
        LIMIT 1
    """)
    ultima = cursor.fetchone()

    if ultima:

        mercado, data = ultima

        cursor.execute("""
            SELECT produto, preco, quantidade 
            FROM compras
            WHERE mercado = ? AND data = ?
        """, (mercado, data))

        itens = cursor.fetchall()

        total = sum([float(i[1]) * i[2] for i in itens])

        st.markdown("### 🧾 Sua última feira")

        st.markdown(f"""
        <div class="card">
            🏪 <b>{mercado}</b><br>
            📅 {data}<br>
            💰 <b>Total:</b> R$ {total:.2f}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📦 Itens comprados")

        for i in itens:
            st.markdown(f"""
            <div class="card">
                <b>{i[0]}</b><br>
                {i[2]}x R$ {float(i[1]):.2f}
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("Você ainda não registrou nenhuma compra 🛒")

# ======================
# NOVA FEIRA
# ======================
elif selected == "Nova Feira":

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    # controle de limpeza (CORREÇÃO DO ERRO)
    if "limpar_campos" not in st.session_state:
        st.session_state.limpar_campos = False

    if st.session_state.limpar_campos:
        st.session_state.produto_input = ""
        st.session_state.preco_input = 0.0
        st.session_state.qtd_input = 1
        st.session_state.limpar_campos = False

    # inicializar campos
    if "produto_input" not in st.session_state:
        st.session_state.produto_input = ""
    if "preco_input" not in st.session_state:
        st.session_state.preco_input = 0.0
    if "qtd_input" not in st.session_state:
        st.session_state.qtd_input = 1

    st.subheader("Adicionar Produto")

    col1, col2 = st.columns(2)

    with col1:
        produto = st.text_input("Produto", key="produto_input")
        preco = st.number_input("Preço", min_value=0.0, key="preco_input")

    with col2:
        quantidade = st.number_input("Quantidade", min_value=1, key="qtd_input")

    if st.button("➕ Adicionar"):
        if produto:

            item_existente = next(
                (item for item in st.session_state.carrinho if item["produto"] == produto),
                None
            )

            if item_existente:
                item_existente["quantidade"] += quantidade
                st.toast("Quantidade atualizada 🔄")
            else:
                st.session_state.carrinho.append({
                    "produto": produto,
                    "preco": preco,
                    "quantidade": quantidade
                })
                st.toast("Produto adicionado 🛒")

            # ativa limpeza e recarrega
            st.session_state.limpar_campos = True
            st.rerun()

    st.markdown("### 🧾 Carrinho")

    total = 0

    for i, item in enumerate(st.session_state.carrinho):
        subtotal = item["preco"] * item["quantidade"]
        total += subtotal

        col1, col2 = st.columns([5,1])

        with col1:
            st.markdown(f"""
            <div class="card">
                <b>{item['produto']}</b><br>
                {item['quantidade']}x R$ {item['preco']:.2f}<br>
                <b>Subtotal:</b> R$ {subtotal:.2f}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("🗑", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()

    st.markdown(f"""
    <div class="total-box">
        💰 Total: R$ {total:.2f}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Finalizar Compra")

    mercado = st.text_input("Mercado")
    data = st.date_input("Data", value=datetime.today())

    if st.button("💾 Salvar Compra"):
        if st.session_state.carrinho and mercado:
            for item in st.session_state.carrinho:
                cursor.execute("""
                    INSERT INTO compras (produto, preco, quantidade, mercado, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item["produto"],
                    item["preco"],
                    item["quantidade"],
                    mercado,
                    str(data)
                ))

            conn.commit()
            st.session_state.carrinho = []
            st.success("Compra salva com sucesso!")
        else:
            st.warning("Preencha tudo antes de salvar.")

# ======================
# COMPARAR PREÇOS
# ======================
elif selected == "Comparar":

    st.subheader("Buscar Produto")

    produto_busca = st.text_input("Digite o produto")

    if st.button("🔍 Buscar"):
        cursor.execute("""
            SELECT produto, preco, quantidade, mercado, data 
            FROM compras
            WHERE produto LIKE ?
        """, ('%' + produto_busca + '%',))

        resultados = cursor.fetchall()

        if resultados:

            menor_preco = min([float(r[1]) for r in resultados])
            maior_preco = max([float(r[1]) for r in resultados])

            st.markdown("### 📊 Resultados")

            for r in resultados:

                preco_atual = float(r[1])
                economia = maior_preco - preco_atual

                destaque = ""
                cor = "#1e293b"

                if preco_atual == menor_preco:
                    destaque = "🏆 MELHOR PREÇO"
                    cor = "#065f46"

                st.markdown(f"""
                <div class="card" style="background:{cor}">
                    <b>{r[0]}</b><br>
                    💰 R$ {preco_atual:.2f} {destaque}<br>
                    💸 Economia: R$ {economia:.2f}<br>
                    📦 {r[2]}x<br>
                    🏪 {r[3]}<br>
                    📅 {r[4]}
                </div>
                """, unsafe_allow_html=True)

        else:
            st.warning("Nenhum resultado encontrado.")