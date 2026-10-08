from datetime import datetime
from flask import Flask, render_template, url_for, request, flash, redirect

app = Flask(__name__)
app.secret_key = 'chave-secreta-fatec-2026'

CIDADES = ['Jaú', 'Bauru', 'Botucatu', 'Marília', 'Outra']
PERFIS = ['cliente', 'funcionario', 'admin']
GENEROS = ['Ação', 'Comédia', 'Drama', 'Ficção Científica', 'Terror', 'Romance', 'Animação']

# ============================================================
# "BANCO DE DADOS" EM MEMÓRIA
# Listas Python: os dados existem só enquanto o servidor está rodando
# e voltam ao estado inicial quando o Flask é reiniciado.
# ============================================================
usuarios = [
    {'id': 1, 'nome': 'Administrador', 'email': 'admin@teste.com', 'senha': '123456',
     'cidade': 'Jaú', 'perfil': 'admin', 'ativo': True, 'criado_em': '01/08/2026'},
]

filmes = [
    {'id': 1, 'titulo': 'Matrix', 'genero': 'Ficção Científica', 'ano': 1999,
     'duracao': 136, 'valor_diaria': 8.90,
     'sinopse': 'Um hacker descobre a verdadeira natureza da realidade.', 'ativo': True},
    {'id': 2, 'titulo': 'Cidade de Deus', 'genero': 'Drama', 'ano': 2002,
     'duracao': 130, 'valor_diaria': 7.50,
     'sinopse': 'A vida e o crime nas favelas do Rio de Janeiro.', 'ativo': True},
    {'id': 3, 'titulo': 'O Auto da Compadecida', 'genero': 'Comédia', 'ano': 2000,
     'duracao': 104, 'valor_diaria': 6.50,
     'sinopse': 'As aventuras de João Grilo e Chicó no sertão nordestino.', 'ativo': True},
    {'id': 4, 'titulo': 'Interestelar', 'genero': 'Ficção Científica', 'ano': 2014,
     'duracao': 169, 'valor_diaria': 9.90,
     'sinopse': 'Exploradores viajam por um buraco de minhoca em busca de um novo lar.',
     'ativo': True},
    {'id': 5, 'titulo': 'Central do Brasil', 'genero': 'Drama', 'ano': 1998,
     'duracao': 110, 'valor_diaria': 6.00,
     'sinopse': 'Uma ex-professora ajuda um menino a encontrar o pai.', 'ativo': True},
]

alugueis = []


def proximo_id(lista):
    """Gera o próximo id (equivalente ao AUTO_INCREMENT do banco)."""
    return max([item['id'] for item in lista], default=0) + 1


def buscar_por_id(lista, item_id):
    """Retorna o item da lista com o id informado, ou None."""
    for item in lista:
        if item['id'] == item_id:
            return item
    return None


# ============================================================
# PÁGINA INICIAL
# ============================================================
@app.route('/')
def pagina_inicial():
    return render_template('index.html')


# ============================================================
# LOGIN
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')

        erros = []
        if not email:
            erros.append('Informe o e-mail.')
        if not senha:
            erros.append('Informe a senha.')

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('login.html', email=email)

        # Procura na lista um usuário ativo com este e-mail e senha
        encontrado = None
        for u in usuarios:
            if u['email'] == email and u['senha'] == senha and u['ativo']:
                encontrado = u
                break

        if encontrado is None:
            flash('E-mail ou senha incorretos.', 'danger')
            return render_template('login.html', email=email)

        # Padrão PRG: redireciona após o POST bem-sucedido
        flash(f'Bem-vindo(a), {encontrado["nome"]}!', 'success')
        return redirect(url_for('pagina_inicial'))

    return render_template('login.html')


# ============================================================
# USUÁRIOS — cadastro
# ============================================================
@app.route('/usuarios/novo', methods=['GET', 'POST'])
def usuario_novo():

    if request.method == 'POST':

        # ===== COLETA DOS DADOS =====
        nome      = request.form.get('nome', '').strip()
        email     = request.form.get('email', '').strip()
        senha     = request.form.get('senha', '')
        confirmar = request.form.get('confirmar', '')
        cidade    = request.form.get('cidade', '')
        perfil    = request.form.get('perfil', 'cliente')

        # A senha nunca volta para o formulário
        dados = {'nome': nome, 'email': email, 'cidade': cidade, 'perfil': perfil}

        # ===== VALIDAÇÃO =====
        erros = []

        if not nome:
            erros.append('O nome é obrigatório.')
        elif len(nome) < 3:
            erros.append('O nome deve ter pelo menos 3 caracteres.')

        if not email:
            erros.append('O e-mail é obrigatório.')
        elif '@' not in email or '.' not in email:
            erros.append('Digite um e-mail válido.')
        else:
            for u in usuarios:
                if u['email'].lower() == email.lower():
                    erros.append('Já existe um usuário cadastrado com este e-mail.')
                    break

        if not senha:
            erros.append('A senha é obrigatória.')
        elif len(senha) < 6:
            erros.append('A senha deve ter pelo menos 6 caracteres.')
        elif senha != confirmar:
            erros.append('A confirmação da senha não confere.')

        if cidade not in CIDADES:
            erros.append('Selecione uma cidade.')

        if perfil not in PERFIS:
            erros.append('Selecione um perfil válido.')

        # ===== EXIBIÇÃO DE ERROS =====
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('usuarios_novo.html', cidades=CIDADES, dados=dados)

        # ===== GRAVAÇÃO NA LISTA =====
        usuarios.append({
            'id': proximo_id(usuarios),
            'nome': nome,
            'email': email,
            'senha': senha,
            'cidade': cidade,
            'perfil': perfil,
            'ativo': True,
            'criado_em': datetime.now().strftime('%d/%m/%Y'),
        })

        flash(f'Usuário {nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('usuarios_lista'))

    return render_template('usuarios_novo.html', cidades=CIDADES, dados={})


# ============================================================
# USUÁRIOS — listagem (a senha não é exibida no template)
# ============================================================
@app.route('/usuarios')
def usuarios_lista():
    ordenados = sorted(usuarios, key=lambda u: u['nome'].lower())
    return render_template('usuarios_lista.html', usuarios=ordenados, total=len(ordenados))


# ============================================================
# FILMES — cadastro
# ============================================================
@app.route('/filmes/novo', methods=['GET', 'POST'])
def filme_novo():

    if request.method == 'POST':

        # ===== COLETA DOS DADOS =====
        titulo       = request.form.get('titulo', '').strip()
        genero       = request.form.get('genero', '')
        ano          = request.form.get('ano', '').strip()
        duracao      = request.form.get('duracao', '').strip()
        valor_diaria = request.form.get('valor_diaria', '').strip().replace(',', '.')
        sinopse      = request.form.get('sinopse', '').strip()

        dados = {
            'titulo': titulo, 'genero': genero, 'ano': ano,
            'duracao': duracao, 'valor_diaria': valor_diaria, 'sinopse': sinopse,
        }

        # ===== VALIDAÇÃO =====
        erros = []

        if not titulo:
            erros.append('O título é obrigatório.')
        elif len(titulo) < 2:
            erros.append('O título deve ter pelo menos 2 caracteres.')

        if genero not in GENEROS:
            erros.append('Selecione um gênero.')

        try:
            ano_int = int(ano)
            if ano_int < 1900 or ano_int > 2100:
                erros.append('O ano deve estar entre 1900 e 2100.')
        except ValueError:
            erros.append('Informe um ano válido (somente números).')

        try:
            duracao_int = int(duracao)
            if duracao_int <= 0:
                erros.append('A duração deve ser maior que zero.')
        except ValueError:
            erros.append('Informe a duração em minutos (somente números).')

        try:
            valor_float = float(valor_diaria)
            if valor_float <= 0:
                erros.append('O valor da diária deve ser maior que zero.')
        except ValueError:
            erros.append('Informe um valor de diária válido (ex.: 8.90).')

        # ===== EXIBIÇÃO DE ERROS =====
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('filmes_novo.html', generos=GENEROS, dados=dados)

        # ===== GRAVAÇÃO NA LISTA =====
        filmes.append({
            'id': proximo_id(filmes),
            'titulo': titulo,
            'genero': genero,
            'ano': ano_int,
            'duracao': duracao_int,
            'valor_diaria': round(valor_float, 2),
            'sinopse': sinopse,
            'ativo': True,
        })

        flash(f'Filme "{titulo}" cadastrado com sucesso!', 'success')
        return redirect(url_for('filmes_lista'))

    return render_template('filmes_novo.html', generos=GENEROS, dados={})


# ============================================================
# FILMES — listagem
# ============================================================
@app.route('/filmes')
def filmes_lista():
    ativos = [f for f in filmes if f['ativo']]
    ativos = sorted(ativos, key=lambda f: f['titulo'].lower())
    return render_template('filmes_lista.html', filmes=ativos, total=len(ativos))


# ============================================================
# ALUGUÉIS — cadastro
# ============================================================
@app.route('/alugueis/novo', methods=['GET', 'POST'])
def aluguel_novo():

    # Usuários e filmes disponíveis para os <select> do formulário
    usuarios_ativos = sorted([u for u in usuarios if u['ativo']],
                             key=lambda u: u['nome'].lower())
    filmes_ativos = sorted([f for f in filmes if f['ativo']],
                           key=lambda f: f['titulo'].lower())

    if request.method == 'POST':

        # ===== COLETA DOS DADOS =====
        usuario_id = request.form.get('usuario_id', '')
        filme_id   = request.form.get('filme_id', '')
        dias       = request.form.get('dias', '').strip()
        observacao = request.form.get('observacao', '').strip()

        dados = {
            'usuario_id': usuario_id, 'filme_id': filme_id,
            'dias': dias, 'observacao': observacao,
        }

        # ===== VALIDAÇÃO =====
        erros = []
        usuario = None
        filme = None

        if not usuario_id:
            erros.append('Selecione o cliente.')
        else:
            try:
                usuario = buscar_por_id(usuarios, int(usuario_id))
                if usuario is None or not usuario['ativo']:
                    usuario = None
                    erros.append('O cliente selecionado não está disponível.')
            except ValueError:
                erros.append('Cliente inválido.')

        if not filme_id:
            erros.append('Selecione um filme.')
        else:
            try:
                filme = buscar_por_id(filmes, int(filme_id))
                if filme is None or not filme['ativo']:
                    filme = None
                    erros.append('O filme selecionado não está disponível.')
            except ValueError:
                erros.append('Filme inválido.')

        try:
            dias_int = int(dias)
            if dias_int < 1 or dias_int > 30:
                erros.append('A quantidade de dias deve ser entre 1 e 30.')
        except ValueError:
            erros.append('Informe a quantidade de dias (somente números).')

        # ===== EXIBIÇÃO DE ERROS =====
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('alugueis_novo.html',
                                   usuarios=usuarios_ativos, filmes=filmes_ativos, dados=dados)

        # ===== CÁLCULO E GRAVAÇÃO =====
        # O valor total é calculado no servidor (nunca confie no cliente)
        valor_total = round(filme['valor_diaria'] * dias_int, 2)

        alugueis.append({
            'id': proximo_id(alugueis),
            'usuario_id': usuario['id'],
            'filme_id': filme['id'],
            'cliente_nome': usuario['nome'],
            'filme_titulo': filme['titulo'],
            'dias': dias_int,
            'valor_total': valor_total,
            'observacao': observacao,
            'devolvido': False,
            'alugado_em': datetime.now().strftime('%d/%m/%Y %H:%M'),
        })

        flash(f'Aluguel de "{filme["titulo"]}" para {usuario["nome"]} registrado '
              f'(R$ {valor_total:.2f}).', 'success')
        return redirect(url_for('alugueis_lista'))

    return render_template('alugueis_novo.html',
                           usuarios=usuarios_ativos, filmes=filmes_ativos, dados={})


# ============================================================
# ALUGUÉIS — listagem
# ============================================================
@app.route('/alugueis')
def alugueis_lista():
    # Mais recentes primeiro
    recentes = sorted(alugueis, key=lambda a: a['id'], reverse=True)
    total_geral = sum(a['valor_total'] for a in alugueis)

    return render_template('alugueis_lista.html',
                           alugueis=recentes,
                           total=len(recentes),
                           total_geral=total_geral)


if __name__ == '__main__':
    app.run(debug=True)
