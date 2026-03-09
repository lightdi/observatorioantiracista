"""
Rotas do site público: início, post, denúncia, artigos, contato, busca.
"""
from flask import render_template, request, redirect, url_for, flash
from app.blue_main import blue_main
from app.extensões import db
from app.models import Post, Denuncia, CATEGORIAS, Escola, Pratica

# Destaques fixos (podem depois vir do banco ou config)
DESTAQUES = [
    {
        "titulo": "Indígenas",
        "descricao": "Combate à discriminação e direitos territoriais",
        "categoria_slug": "indigenas",
        "imagem_url": None,
    },
    {
        "titulo": "Afro-Brasileiros",
        "descricao": "Luta contra o racismo estrutural e igualdade",
        "categoria_slug": "afro-brasileiros",
        "imagem_url": None,
    },
    {
        "titulo": "Ciganos/Roma",
        "descricao": "Inclusão social, cultura e combate ao preconceito",
        "categoria_slug": "ciganos-roma",
        "imagem_url": None,
    },
    {
        "titulo": "Cultura & Resistência",
        "descricao": "Valorização da diversidade e combate à exclusão",
        "categoria_slug": "cultura-resistencia",
        "imagem_url": None,
    },
]

AREAS_ATUACAO = [
    {"titulo": "Monitoramento", "descricao": "Acompanhamento de políticas e indicadores.", "icon": "eye"},
    {"titulo": "Pesquisa", "descricao": "Estudos e produção de conhecimento.", "icon": "search"},
    {"titulo": "Educação", "descricao": "Formação e conscientização antirracista.", "icon": "book"},
    {"titulo": "Advocacy", "descricao": "Incidência em políticas públicas.", "icon": "people"},
    {"titulo": "Apoio", "descricao": "Suporte a vítimas e comunidades.", "icon": "heart"},
]


from flask import jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User
from app.blue_main.forms import PublicLoginForm, RegisterForm

@blue_main.route("/registrar", methods=["GET", "POST"])
def registrar():
    """Cadastro de novo usuário visitante."""
    if current_user.is_authenticated:
        return redirect(url_for('blue_main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='user')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("blue_main.login"))
    return render_template("blue_main/registrar.html", form=form)

@blue_main.route("/login", methods=["GET", "POST"])
def login():
    """Login público unificado."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('blue_admin.dashboard'))
        return redirect(url_for('blue_main.index'))
        
    form = PublicLoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        if user is None or not user.check_password(form.password.data):
            flash("Usuário/Email ou senha inválidos.", "danger")
            return redirect(url_for("blue_main.login"))
        
        login_user(user, remember=form.remember.data)
        
        # Redirecionamento baseado na role
        next_page = request.args.get("next")
        if not next_page or not next_page.startswith('/'):
            if user.is_admin:
                next_page = url_for("blue_admin.dashboard")
            else:
                next_page = url_for("blue_main.index") # Depois será minha-conta
                
        return redirect(next_page)
    return render_template("blue_main/login.html", form=form)

@blue_main.route("/sair")
@login_required
def logout():
    """Sair do sistema."""
    logout_user()
    flash("Você saiu com sucesso.", "info")
    return redirect(url_for("blue_main.index"))

@blue_main.route("/api/praticas")
def api_praticas():
    """Retorna a lista de práticas com latitude e longitude para o Leaflet Map."""
    praticas = Pratica.query.filter(Pratica.latitude.isnot(None), Pratica.longitude.isnot(None)).all()
    dados = []
    for p in praticas:
        dados.append({
            "id": p.id,
            "titulo": p.titulo,
            "escola": p.escola.nome,
            "categoria": p.categoria_nome,
            "endereco": p.endereco,
            "lat": p.latitude,
            "lng": p.longitude
        })
    return jsonify(dados)


@blue_main.route("/")
def index():
    """Página inicial: hero, destaques, últimas notícias, áreas de atuação e Observatório."""
    posts = (
        Noticia.query.filter_by(publicado=True)
        .order_by(Noticia.created_at.desc())
        .limit(3)
        .all()
    )
    
    # Métricas para o Observatório
    metricas = {
        "escolas": Escola.query.count(),
        "praticas": Pratica.query.count(),
        "denuncias": Denuncia.query.count(),
        "cat_indigenas": Pratica.query.filter_by(categoria_slug="indigenas").count(),
        "cat_afro": Pratica.query.filter_by(categoria_slug="afro-brasileiros").count(),
        "cat_ciganos": Pratica.query.filter_by(categoria_slug="ciganos-roma").count(),
        "cat_cultura": Pratica.query.filter_by(categoria_slug="cultura-resistencia").count(),
    }
    
    return render_template(
        "blue_main/index.html",
        destaques=DESTAQUES,
        areas=AREAS_ATUACAO,
        ultimas_noticias=posts,
        metricas=metricas
    )


from app.models import Artigo, Pesquisa, Noticia

@blue_main.route("/artigos")
def artigos():
    """Listagem de Artigos Oficiais com paginação."""
    page = request.args.get("page", 1, type=int)
    pagination = (
        Artigo.query.filter_by(publicado=True)
        .order_by(Artigo.created_at.desc())
        .paginate(page=page, per_page=9)
    )
    return render_template("blue_main/artigos.html", pagination=pagination)

@blue_main.route("/artigo/<slug>")
def artigo_single(slug):
    """Página de um único artigo."""
    art = Artigo.query.filter_by(slug=slug, publicado=True).first_or_404()
    return render_template("blue_main/artigo_single.html", artigo=art)


@blue_main.route("/pesquisas")
def pesquisas():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Pesquisa.query.filter_by(publicado=True)
        .order_by(Pesquisa.created_at.desc())
        .paginate(page=page, per_page=9)
    )
    return render_template("blue_main/pesquisas.html", pagination=pagination)

@blue_main.route("/pesquisa/<slug>")
def pesquisa_single(slug):
    pesq = Pesquisa.query.filter_by(slug=slug, publicado=True).first_or_404()
    return render_template("blue_main/pesquisa_single.html", pesquisa=pesq)


@blue_main.route("/noticias")
def noticias():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Noticia.query.filter_by(publicado=True)
        .order_by(Noticia.created_at.desc())
        .paginate(page=page, per_page=9)
    )
    return render_template("blue_main/noticias.html", pagination=pagination)

@blue_main.route("/noticia/<slug>")
def noticia_single(slug):
    notc = Noticia.query.filter_by(slug=slug, publicado=True).first_or_404()
    return render_template("blue_main/noticia_single.html", noticia=notc)


@blue_main.route("/praticas_publicas")
def praticas():
    page = request.args.get("page", 1, type=int)
    cat = request.args.get("categoria")
    
    query = Pratica.query
    if cat:
        query = query.filter_by(categoria_slug=cat)
        
    pagination = query.order_by(Pratica.created_at.desc()).paginate(page=page, per_page=9)
    return render_template("blue_main/praticas.html", pagination=pagination, current_cat=cat)

@blue_main.route("/pratica/<int:id>")
def pratica_single(id):
    pratica = Pratica.query.get_or_404(id)
    return render_template("blue_main/pratica_single.html", pratica=pratica)

# Rota Legada para links quebrados (Posts antigos)
@blue_main.route("/post/<slug>")
def post(slug):
    """Página de um único post legado."""
    post_obj = Post.query.filter_by(slug=slug, publicado=True).first_or_404()
    return render_template("blue_main/post.html", post=post_obj)


@blue_main.route("/denunciar", methods=["GET", "POST"])
def denunciar():
    """Formulário de denúncia online."""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip() or None
        email = request.form.get("email", "").strip() or None
        local = request.form.get("local_ocorrencia", "").strip() or None
        data = request.form.get("data_aproximada", "").strip() or None
        conteudo = request.form.get("conteudo", "").strip()
        
        if not conteudo:
            flash("O campo da denúncia é obrigatório.", "danger")
            return redirect(url_for("blue_main.denunciar"))
            
        d = Denuncia(
            nome=nome, email=email, conteudo=conteudo,
            local_ocorrencia=local, data_aproximada=data
        )
        db.session.add(d)
        db.session.commit()
        flash("Sua denúncia foi registrada. Obrigado.", "success")
        return redirect(url_for("blue_main.index"))
    return render_template("blue_main/denunciar.html")


@blue_main.route("/contato", methods=["GET", "POST"])
def contato():
    """Página de contato (formulário simples)."""
    if request.method == "POST":
        # Placeholder: pode enviar email ou salvar em tabela Contato
        flash("Mensagem recebida. Entraremos em contato em breve.", "success")
        return redirect(url_for("blue_main.contato"))
    return render_template("blue_main/contato.html")


@blue_main.route("/buscar")
def buscar():
    """Busca global no portal (artigos, pesquisas, noticias, praticas)."""
    q = request.args.get("q", "").strip()
    if not q:
        return redirect(url_for("blue_main.index"))
        
    term = f"%{q}%"
    
    # Buscas separadas (top 10 de cada para não sobrecarregar)
    artigos = Artigo.query.filter_by(publicado=True).filter(
        Artigo.titulo.ilike(term) | Artigo.conteudo.ilike(term) | Artigo.resumo.ilike(term)
    ).limit(10).all()
    
    pesquisas = Pesquisa.query.filter_by(publicado=True).filter(
        Pesquisa.titulo.ilike(term) | Pesquisa.descricao.ilike(term)
    ).limit(10).all()
    
    noticias = Noticia.query.filter_by(publicado=True).filter(
        Noticia.titulo.ilike(term) | Noticia.descricao.ilike(term)
    ).limit(10).all()
    
    praticas = Pratica.query.filter(
        Pratica.titulo.ilike(term) | Pratica.descricao.ilike(term) | Pratica.endereco.ilike(term)
    ).limit(10).all()

    return render_template("blue_main/buscar.html", q=q, artigos=artigos, pesquisas=pesquisas, noticias=noticias, praticas=praticas)


@blue_main.route("/comentar", methods=["POST"])
@login_required
def comentar():
    """Recebe comentários das diversas entidades."""
    conteudo = request.form.get("conteudo", "").strip()
    tipo = request.form.get("tipo")
    item_id = request.form.get("item_id")
    redirect_url = request.referrer or url_for('blue_main.index')
    
    if not conteudo:
        flash("O comentário não pode ficar vazio.", "warning")
        return redirect(redirect_url)
        
    comentario = Comentario(conteudo=conteudo, user_id=current_user.id)
    
    if tipo == "pratica":
        comentario.pratica_id = item_id
    elif tipo == "artigo":
        comentario.artigo_id = item_id
    elif tipo == "pesquisa":
        comentario.pesquisa_id = item_id
    elif tipo == "noticia":
        comentario.noticia_id = item_id
    else:
        abort(400)
        
    db.session.add(comentario)
    db.session.commit()
    flash("Comentário enviado! Aguarde aprovação se necessário.", "success")
    return redirect(redirect_url)

# ======= ÁREA DO USUÁRIO (MINHA CONTA) =======
from app.blue_admin.forms import PraticaForm
from app.models import AnexoPratica
import os
from werkzeug.utils import secure_filename
from flask import current_app

@blue_main.route("/minha-conta")
@login_required
def minha_conta():
    if current_user.is_admin:
        return redirect(url_for("blue_admin.dashboard"))
    praticas = Pratica.query.filter_by(author_id=current_user.id).order_by(Pratica.created_at.desc()).all()
    return render_template("blue_main/minha_conta.html", praticas=praticas)

@blue_main.route("/minha-conta/pratica/nova", methods=["GET", "POST"])
@login_required
def nova_pratica_user():
    if current_user.is_admin:
        return redirect(url_for("blue_admin.nova_pratica"))
        
    form = PraticaForm()
    form.escola_id.choices = [(e.id, e.nome) for e in Escola.query.order_by(Escola.nome).all()]
    
    if form.validate_on_submit():
        pratica = Pratica(
            titulo=form.titulo.data, descricao=form.descricao.data,
            categoria_slug=form.categoria_slug.data, endereco=form.endereco.data,
            latitude=form.latitude.data, longitude=form.longitude.data,
            escola_id=form.escola_id.data, author_id=current_user.id
        )
        db.session.add(pratica)
        db.session.flush()
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        for file in request.files.getlist(form.anexos.name):
            if file and file.filename:
                filename = secure_filename(file.filename) if secure_filename else str(file.filename)
                file_path = os.path.join('uploads', f"pratica_{pratica.id}_{filename}")
                file.save(os.path.join(current_app.root_path, 'static', file_path))
                anexo = AnexoPratica(nome_arquivo=filename, caminho_arquivo=file_path, pratica_id=pratica.id)
                db.session.add(anexo)

        db.session.commit()
        flash("Sua prática foi registrada com sucesso!", "success")
        return redirect(url_for("blue_main.minha_conta"))
    return render_template("blue_main/user_form_pratica.html", form=form, pratica=None)

@blue_main.route("/minha-conta/pratica/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar_pratica_user(id):
    pratica = Pratica.query.filter_by(id=id, author_id=current_user.id).first_or_404()
    form = PraticaForm(obj=pratica)
    form.escola_id.choices = [(e.id, e.nome) for e in Escola.query.order_by(Escola.nome).all()]
    
    if form.validate_on_submit():
        pratica.titulo = form.titulo.data
        pratica.descricao = form.descricao.data
        pratica.categoria_slug = form.categoria_slug.data
        pratica.endereco = form.endereco.data
        pratica.latitude = form.latitude.data
        pratica.longitude = form.longitude.data
        pratica.escola_id = form.escola_id.data
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        for file in request.files.getlist(form.anexos.name):
            if file and file.filename:
                filename = secure_filename(file.filename) if secure_filename else str(file.filename)
                file_path = os.path.join('uploads', f"pratica_{pratica.id}_{filename}")
                file.save(os.path.join(current_app.root_path, 'static', file_path))
                anexo = AnexoPratica(nome_arquivo=filename, caminho_arquivo=file_path, pratica_id=pratica.id)
                db.session.add(anexo)

        db.session.commit()
        flash("Sua prática foi atualizada.", "success")
        return redirect(url_for("blue_main.minha_conta"))
    return render_template("blue_main/user_form_pratica.html", form=form, pratica=pratica)

@blue_main.route("/minha-conta/pratica/<int:id>/excluir", methods=["POST"])
@login_required
def excluir_pratica_user(id):
    pratica = Pratica.query.filter_by(id=id, author_id=current_user.id).first_or_404()
    db.session.delete(pratica)
    db.session.commit()
    flash("Sua prática foi excluída.", "info")
    return redirect(url_for("blue_main.minha_conta"))
