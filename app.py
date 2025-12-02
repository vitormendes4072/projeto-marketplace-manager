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


# ----- MAIN -----
if __name__ == "__main__":
    # criar as tabelas *depois* que o modelo User foi definido
    with app.app_context():
        db.create_all()
    app.run(debug=True)
