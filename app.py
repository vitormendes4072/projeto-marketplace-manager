# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from forms import RegistrationForm, LoginForm # <-- 1. IMPORTAR OS FORMULÁRIOS

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_super_segura' 

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() # <-- 2. INSTANCIAR O FORMULÁRIO DE LOGIN
    if form.validate_on_submit(): # <-- 3. USAR A VALIDAÇÃO DO WTFORMS
        # A validação passou! Acessamos os dados com form.campo.data
        email = form.email.data
        password = form.password.data
        print(f"Login com Email: {email}, Senha: {password}")
        
        # Lógica de autenticação...
        if email == "usuario@exemplo.com" and password == "12345":
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Login inválido. Verifique seu e-mail e senha.", "danger")
            return redirect(url_for('login'))

    # Se a validação falhar ou for um GET, renderiza o template com o formulário
    return render_template('login.html', form=form) # <-- 4. PASSAR O FORMULÁRIO PARA O TEMPLATE

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = RegistrationForm() # <-- 2. INSTANCIAR O FORMULÁRIO DE CADASTRO
    if form.validate_on_submit(): # <-- 3. VALIDAÇÃO AUTOMÁTICA!
        nome_completo = form.nome_completo.data
        email = form.email.data
        senha = form.senha.data
        print(f"Novo cadastro: Nome: {nome_completo}, Email: {email}")
        
        # Aqui viria a lógica para criar o hash da senha e salvar no banco
        
        flash(f'Conta criada para {form.nome_completo.data}!', 'success')
        return redirect(url_for('login'))
        
    return render_template('cadastro.html', form=form) # <-- 4. PASSAR O FORMULÁRIO PARA O TEMPLATE

@app.route('/dashboard')
def dashboard():
    return "<h1>Bem-vindo ao seu Painel!</h1>"

if __name__ == '__main__':
    app.run(debug=True)