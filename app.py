import streamlit as st
import sqlite3
from datetime import datetime

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Market Master",
    page_icon="🛒",
    layout="centered"
)

# ======================
# ESTILO PROFISSIONAL
# ======================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.4);
}
.total-box {
    background-color: #ff4b4b;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
    font-size: 22px;
    font-weight: bold;
}
.stButton>button {
    border-radius: 10px;
    background-color: #ff4b4b;
    color: white;
    font-weight: bold;
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
# MENU
# ======================
st.title("🛒 Market Master")

menu = st.sidebar.radio("Menu", [
    "🏠 Início",
    "🛒 Nova Feira",
    "📊 Comparar Preços"
])

# ======================
# INÍCIO
# ======================
if menu == "🏠 Início":
    st.markdown("""
    ## 👋 Bem-vindo ao Market Master

    Controle sua feira, compare preços e economize dinheiro 💰
    """)

# ======================
# NOVA FEIRA
# ======================
elif menu == "🛒 Nova Feira":

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    st.subheader("Adicionar Produto")

    produto = st.text_input("Nome do produto")
    preco = st.number_input("Preço", min_value=0.0)
    quantidade = st.number_input("Quantidade", min_value=1)

    if st.button("Adicionar"):
        if produto:
            st.session_state.carrinho.append({
                "produto": produto,
                "preco": preco,
                "quantidade": quantidade
            })
            st.success("Produto adicionado!")

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
                Subtotal: R$ {subtotal:.2f}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("❌", key=f"remover_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()

    # TOTAL
    st.markdown(f"""
    <div class="total-box">
        Total: R$ {total:.2f}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Finalizar Compra")

    mercado = st.text_input("Mercado")
    data = st.date_input("Data", value=datetime.today())

    if st.button("Salvar Compra"):
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
            st.warning("Adicione produtos e informe o mercado.")

# ======================
# COMPARAR PREÇOS
# ======================
elif menu == "📊 Comparar Preços":

    st.subheader("Buscar Produto")

    produto_busca = st.text_input("Digite o nome do produto")

    if st.button("Buscar"):
        cursor.execute("""
            SELECT produto, preco, quantidade, mercado, data 
            FROM compras
            WHERE produto LIKE ?
        """, ('%' + produto_busca + '%',))

        resultados = cursor.fetchall()

        if resultados:

            menor_preco = min([float(r[1]) for r in resultados])

            st.markdown("### Resultados")

            for r in resultados:
                destaque = "🟢 MAIS BARATO" if float(r[1]) == menor_preco else ""

                st.markdown(f"""
                <div class="card">
                    <b>{r[0]}</b><br>
                    💰 R$ {float(r[1]):.2f} {destaque}<br>
                    📦 {r[2]}x<br>
                    🏪 {r[3]}<br>
                    📅 {r[4]}
                </div>
                """, unsafe_allow_html=True)

        else:
            st.warning("Nenhum resultado encontrado.")