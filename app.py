from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from dotenv import load_dotenv
from supabase_client import supabase
from supabase_client import get_table_rows


load_dotenv()


app = Flask(__name__)

# CONFIG BÁSICA
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troca-por-uma-chave-secreta")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# "Banco de dados" fake de pedidos só para demonstração
ORDERS = {
    "12345": {
        "id": "12345",
        "marketplace": "Shopee",
        "status": "Enviado",
        "customer_name": "Sophia Clark",
        "total_value": 55.00,
        "address": "123 Main Street, Apt 4B, Anytown, CA 91234",
        "items": [
            {"product": "Cotton T-Shirt", "quantity": 2, "sku": "TSHIRT-001", "unit_price": 20.00},
            {"product": "Denim Jeans", "quantity": 1, "sku": "JEANS-002", "unit_price": 15.00},
        ],
        "history": [
            {"title": "Pedido Recebido", "datetime": "2024-01-15 10:00 AM"},
            {"title": "Etiqueta Gerada", "datetime": "2024-01-15 12:00 PM"},
            {"title": "Item Enviado", "datetime": "2024-01-16 09:00 AM"},
        ],
    },
    # se quiser, depois você adiciona mais pedidos aqui (67890, 11223, etc.)
}


# ----- MODEL -----
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


# ----- HELPER: login_required -----
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para acessar essa página.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


# ----- ROTAS BÁSICAS -----

@app.route("/")
def index():
    # Redireciona direto para login por enquanto
    return redirect(url_for("login"))


# Register / Cadastro
@app.route("/register", methods=["GET", "POST"])
@app.route("/cadastro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # nomes dos campos vindos do register.html
        nome_completo = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("confirm_password")

        # Validações simples
        if not nome_completo or not email or not password or not password_confirm:
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("register"))

        if password != password_confirm:
            flash("As senhas não conferem.", "danger")
            return redirect(url_for("register"))

        # Verifica se email já existe
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Já existe um usuário com esse e-mail.", "danger")
            return redirect(url_for("register"))

        # Cria usuário
        user = User(nome_completo=nome_completo, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    # usa o seu arquivo de layout de cadastro
    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # nomes dos campos do login.html
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_email"] = user.email
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("E-mail ou senha inválidos.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("login"))


# ----- ROTAS DE NAVEGAÇÃO DA APLICAÇÃO -----

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user_email=session.get("user_email"))


@app.route("/orders")
@login_required
def orders():
    # página de gerenciamento de pedidos
    # ajuste o nome do arquivo se o seu estiver escrito diferente
    return render_template("gerenciamentoPedidos.html")

@app.route("/orders/<order_id>")
@login_required
def order_details(order_id):
    order = ORDERS.get(order_id)
    if not order:
        flash("Pedido não encontrado.", "warning")
        return redirect(url_for("orders"))
    return render_template("detalhesPedido.html", order=order)


@app.route("/shipping")
@login_required
def shipping():
    # sua página processamentoEnvio.html
    return render_template("processamentoEnvio.html")


@app.route("/reports")
@login_required
def reports():
    # sua página relatorioAnalises.html
    return render_template("relatorioAnalises.html")


@app.route("/processamentoEnvio")
@login_required
def processamentoEnvio():
    # placeholder – crie um products.html depois se quiser
    return render_template("processamentoEnvio.html")


@app.route("/settings")
@login_required
def settings():
    # placeholder – crie um settings.html depois se quiser
    return render_template("configuracoes.html")

from supabase_client import supabase   # lá em cima, junto com os imports


@app.route("/supabase-clientes")
@login_required
def supabase_clientes():
    try:
        # Busca da tabela "clientes"
        response = supabase.table("clientes").select("*").limit(100).execute()
        rows = response.data or []
        print("ROWS DO SUPABASE:", rows)  # só pra debug no terminal
    except Exception as e:
        print("Erro ao consultar Supabase:", e)
        rows = []

    # Mapeia os campos do Supabase para nomes que vamos usar no HTML
    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_cliente"),
                "nome": r.get("nome"),
                "endereco": r.get("endereco"),
                "telefone": r.get("telefone"),
                "email": r.get("email"),
            }
        )

    return render_template("supabaseDados.html", registros=registros)

@app.route("/supabase-produtos")
@login_required
def supabase_produtos():
    tabela = "produtos"

    try:
        # Busca até 200 produtos
        response = supabase.table(tabela).select("*").limit(200).execute()
        rows = response.data or []
        print("ROWS PRODUTOS:", rows)  # só pra debug no terminal
    except Exception as e:
        print("Erro ao consultar produtos:", e)
        rows = []

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_produto"),
                "nome": r.get("nome"),
                "descricao": r.get("descricao"),
                "preco": r.get("preco") or 0,
                "estoque": r.get("estoque") or 0,
                "peso_kg": r.get("kg_produto") or 0,
            }
        )

    return render_template("supabaseProdutos.html", registros=registros)

@app.route("/supabase-veiculos")
@login_required
def supabase_veiculos():
    tabela = "veiculos"

    try:
        response = supabase.table(tabela).select("*").limit(200).execute()
        rows = response.data or []
        print("ROWS VEICULOS:", rows)  # debug
    except Exception as e:
        print("Erro ao consultar veiculos:", e)
        rows = []

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_veiculo") or r.get("id") or r.get("id_veiculos"),
                "modelo": r.get("modelo"),
                "placa": r.get("placa"),
                "capacidade_kg": r.get("capacidade_kg") or 0,
                "consumo_km_litro": r.get("consumo_km_litro") or 0,
            }
        )

    return render_template("supabaseVeiculos.html", registros=registros)


@app.route("/clientes")
@login_required
def clientes():
    rows = get_table_rows("clientes")

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_cliente"),
                "cols": [
                    r.get("nome"),
                    r.get("endereco"),
                    r.get("telefone"),
                    r.get("email"),
                ],
            }
        )

    return render_template(
        "supabaseDados.html",
        titulo="Clientes",
        descricao="Lista de clientes cadastrados no Supabase.",
        colunas=["Nome", "Endereço", "Telefone", "E-mail"],
        registros=registros,
    )


@app.route("/produtos")
@login_required
def produtos():
    rows = get_table_rows("produtos")

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_produto"),
                "cols": [
                    r.get("nome"),
                    r.get("descricao"),
                    r.get("preco"),
                    r.get("estoque"),
                    r.get("kg_produto"),
                ],
            }
        )

    return render_template(
        "supabaseDados.html",
        titulo="Produtos",
        descricao="Lista de produtos disponíveis no Supabase.",
        colunas=["Nome", "Descrição", "Preço", "Estoque", "Kg/Produto"],
        registros=registros,
    )


@app.route("/motoristas")
@login_required
def motoristas():
    rows = get_table_rows("motoristas")

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_motorista"),
                "cols": [
                    r.get("nome"),
                    r.get("telefone"),
                    r.get("email"),
                    r.get("regiao"),
                    r.get("cnh_numero"),
                ],
            }
        )

    return render_template(
        "supabaseDados.html",
        titulo="Motoristas",
        descricao="Motoristas cadastrados para as entregas.",
        colunas=["Nome", "Telefone", "E-mail", "Região", "CNH"],
        registros=registros,
    )


@app.route("/veiculos")
@login_required
def veiculos():
    rows = get_table_rows("veiculos")

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_veiculo"),
                "cols": [
                    r.get("modelo"),
                    r.get("placa"),
                    r.get("capacidade_kg"),
                    r.get("consumo_km_litro"),
                ],
            }
        )

    return render_template(
        "supabaseDados.html",
        titulo="Veículos",
        descricao="Veículos disponíveis para roteirização das entregas.",
        colunas=["Modelo", "Placa", "Capacidade (kg)", "Consumo (km/l)"],
        registros=registros,
    )

@app.route("/supabase-motoristas")
@login_required
def supabase_motoristas():
    tabela = "motoristas"

    try:
        response = supabase.table(tabela).select("*").limit(200).execute()
        rows = response.data or []
        print("ROWS MOTORISTAS:", rows)  # debug
    except Exception as e:
        print("Erro ao consultar motoristas:", e)
        rows = []

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_motorista") or r.get("id") or r.get("id_motoristas"),
                "nome": r.get("nome"),
                "telefone": r.get("telefone"),
                "email": r.get("email"),
                "regiao": r.get("regiao"),
                "cnh_numero": r.get("cnh_numero"),
            }
        )

    return render_template("supabaseMotoristas.html", registros=registros)

@app.route("/supabase-entregas")
@login_required
def supabase_entregas():
    tabela = "entregas"

    try:
        response = supabase.table(tabela).select("*").limit(200).execute()
        rows = response.data or []
        print("ROWS ENTREGAS:", rows)  # debug pra ver as colunas reais no console
    except Exception as e:
        print("Erro ao consultar entregas:", e)
        rows = []

    registros = []
    for r in rows:
        registros.append(
            {
                "id": r.get("id_entrega") or r.get("id"),
                "id_cliente": r.get("id_cliente"),
                "id_motorista": r.get("id_motorista"),
                "data": r.get("data_entrega") or r.get("data") or "",
                "status": r.get("status") or r.get("situacao") or "-",
            }
        )

    return render_template("supabaseEntregas.html", registros=registros)

@app.route("/supabase-entregas-produtos")
@login_required
def supabase_entregas_produtos():
    tabela = "entregas_produtos"

    try:
        resp = supabase.table(tabela).select("*").limit(200).execute()
        rows = resp.data or []
        print("ROWS ENTREGAS_PRODUTOS:", rows)
    except Exception as e:
        print("Erro ao consultar entregas_produtos:", e)
        rows = []

    itens = []
    for r in rows:
        itens.append(
            {
                # tenta vários nomes possíveis de ID, pra não quebrar
                "id": r.get("id_entrega_produto")
                or r.get("id")
                or r.get("id_entrega_prod"),

                "id_entrega": r.get("id_entrega"),
                "id_produto": r.get("id_produto"),

                # quantidade pode estar com nome diferente, deixei seguro
                "quantidade": r.get("quantidade")
                or r.get("qtd")
                or r.get("qtd_produto"),

                # campo opcional, se não existir mostra "-"
                "kg_total": r.get("kg_total") or r.get("peso_total") or "-",
            }
        )

    return render_template("supabaseEntregasProdutos.html", itens=itens)


# ----- MAIN -----
if __name__ == "__main__":
    # criar as tabelas *depois* que o modelo User foi definido
    with app.app_context():
        db.create_all()
    app.run(debug=True)
