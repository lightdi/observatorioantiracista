"""
Rotas do painel administrativo: login, dashboard, CRUD de posts, denúncias.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.decorators import admin_required
from app.blue_admin import blue_admin
from app.blue_admin.forms import LoginForm, PostForm
from app.extensões import db
from app.models import User, Post, Denuncia, slugify, Escola, Pratica, AnexoPratica, Artigo, Pesquisa, Noticia


@blue_admin.route("/login", methods=["GET", "POST"])
def login():
    """Login do administrador."""
    if current_user.is_authenticated:
        return redirect(url_for("blue_admin.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Login realizado com sucesso.", "success")
            next_page = request.args.get("next") or url_for("blue_admin.dashboard")
            return redirect(next_page)
        flash("Usuário ou senha incorretos.", "danger")
    return render_template("blue_admin/login.html", form=form)


@blue_admin.route("/logout")
@admin_required
def logout():
    """Logout."""
    logout_user()
    flash("Você saiu do painel.", "info")
    return redirect(url_for("blue_main.index"))


@blue_admin.route("/")
@blue_admin.route("/dashboard")
@admin_required
def dashboard():
    """Dashboard com resumo."""
    total_posts = Post.query.count()
    total_denuncias = Denuncia.query.count()
    total_escolas = Escola.query.count()
    total_praticas = Pratica.query.count()
    denuncias_recentes = Denuncia.query.order_by(Denuncia.created_at.desc()).limit(5).all()
    return render_template(
        "blue_admin/dashboard.html",
        total_posts=total_posts,
        total_denuncias=total_denuncias,
        total_escolas=total_escolas,
        total_praticas=total_praticas,
        denuncias_recentes=denuncias_recentes,
    )


@blue_admin.route("/posts")
@admin_required
def posts():
    """Listagem de posts para gerenciamento."""
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=15)
    return render_template("blue_admin/gerenciar_posts.html", pagination=pagination)


@blue_admin.route("/post/novo", methods=["GET", "POST"])
@admin_required
def novo_post():
    """Criar novo post."""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            titulo=form.titulo.data,
            slug=form.slug.data.strip() or slugify(form.titulo.data),
            categoria_slug=form.categoria_slug.data,
            resumo=form.resumo.data or None,
            imagem_url=form.imagem_url.data or None,
            conteudo=form.conteudo.data,
            publicado=form.publicado.data,
            author_id=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        flash("Post criado com sucesso.", "success")
        return redirect(url_for("blue_admin.posts"))
    return render_template("blue_admin/post_form.html", form=form, post=None)


@blue_admin.route("/post/<int:post_id>/editar", methods=["GET", "POST"])
@admin_required
def editar_post(post_id):
    """Editar post existente."""
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.titulo = form.titulo.data
        post.slug = form.slug.data.strip() or slugify(form.titulo.data)
        post.categoria_slug = form.categoria_slug.data
        post.resumo = form.resumo.data or None
        post.imagem_url = form.imagem_url.data or None
        post.conteudo = form.conteudo.data
        post.publicado = form.publicado.data
        db.session.commit()
        flash("Post atualizado.", "success")
        return redirect(url_for("blue_admin.posts"))
    return render_template("blue_admin/post_form.html", form=form, post=post)


@blue_admin.route("/post/<int:post_id>/excluir", methods=["POST"])
@admin_required
def excluir_post(post_id):
    """Excluir post."""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post excluído.", "info")
    return redirect(url_for("blue_admin.posts"))


@blue_admin.route("/denuncias")
@admin_required
def denuncias():
    """Listagem de denúncias."""
    page = request.args.get("page", 1, type=int)
    pagination = Denuncia.query.order_by(Denuncia.created_at.desc()).paginate(page=page, per_page=20)
    return render_template("blue_admin/denuncias.html", pagination=pagination)


@blue_admin.route("/denuncias/<int:denuncia_id>/status", methods=["POST"])
@admin_required
def alterar_status_denuncia(denuncia_id):
    """Alterar status da denúncia (recebida, em_analise, concluida)."""
    d = Denuncia.query.get_or_404(denuncia_id)
    status = request.form.get("status")
    if status in ("recebida", "em_analise", "concluida"):
        d.status = status
        db.session.commit()
        flash("Status atualizado.", "success")
    return redirect(url_for("blue_admin.denuncias"))


# ======= CRUD DE ESCOLAS =======

@blue_admin.route("/escolas")
@admin_required
def escolas():
    """Listagem de escolas."""
    escolas = Escola.query.order_by(Escola.nome.asc()).all()
    return render_template("blue_admin/gerenciar_escolas.html", escolas=escolas)


@blue_admin.route("/escola/nova", methods=["GET", "POST"])
@admin_required
def nova_escola():
    form = EscolaForm()
    if form.validate_on_submit():
        escola = Escola(
            nome=form.nome.data,
            cidade=form.cidade.data,
            estado=form.estado.data
        )
        db.session.add(escola)
        db.session.commit()
        flash("Escola cadastrada.", "success")
        return redirect(url_for("blue_admin.escolas"))
    return render_template("blue_admin/form_escola.html", form=form, escola=None)


@blue_admin.route("/escola/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar_escola(id):
    escola = Escola.query.get_or_404(id)
    form = EscolaForm(obj=escola)
    if form.validate_on_submit():
        escola.nome = form.nome.data
        escola.cidade = form.cidade.data
        escola.estado = form.estado.data
        db.session.commit()
        flash("Escola atualizada.", "success")
        return redirect(url_for("blue_admin.escolas"))
    return render_template("blue_admin/form_escola.html", form=form, escola=escola)


@blue_admin.route("/escola/<int:id>/excluir", methods=["POST"])
@admin_required
def excluir_escola(id):
    escola = Escola.query.get_or_404(id)
    db.session.delete(escola)
    db.session.commit()
    flash("Escola excluída.", "info")
    return redirect(url_for("blue_admin.escolas"))


# ======= CRUD DE PRÁTICAS =======
import os
from werkzeug.utils import secure_filename

@blue_admin.route("/praticas")
@admin_required
def praticas():
    # Inclui busca básica se necessário, por ora apenas listagem.
    page = request.args.get('page', 1, type=int)
    pagination = Pratica.query.order_by(Pratica.created_at.desc()).paginate(page=page, per_page=15)
    return render_template("blue_admin/gerenciar_praticas.html", pagination=pagination)


@blue_admin.route("/pratica/nova", methods=["GET", "POST"])
@admin_required
def nova_pratica():
    from flask import current_app
    form = PraticaForm()
    # Popular choices pro escola_id
    form.escola_id.choices = [(e.id, e.nome) for e in Escola.query.order_by(Escola.nome).all()]
    
    if form.validate_on_submit():
        pratica = Pratica(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            categoria_slug=form.categoria_slug.data,
            endereco=form.endereco.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            escola_id=form.escola_id.data
        )
        db.session.add(pratica)
        db.session.flush() # Para obter pratica.id para os anexos
        
        # Processar upload de múltiplos arquivos
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
        flash("Prática registrada com sucesso.", "success")
        return redirect(url_for("blue_admin.praticas"))
    return render_template("blue_admin/form_pratica.html", form=form, pratica=None)


@blue_admin.route("/pratica/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar_pratica(id):
    from flask import current_app
    pratica = Pratica.query.get_or_404(id)
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
        flash("Prática atualizada.", "success")
        return redirect(url_for("blue_admin.praticas"))
    return render_template("blue_admin/form_pratica.html", form=form, pratica=pratica)


@blue_admin.route("/pratica/<int:id>/excluir", methods=["POST"])
@admin_required
def excluir_pratica(id):
    pratica = Pratica.query.get_or_404(id)
    db.session.delete(pratica)
    db.session.commit()
    flash("Prática excluída.", "info")
    return redirect(url_for("blue_admin.praticas"))

@blue_admin.route("/anexo/<int:id>/excluir", methods=["GET"])
@admin_required
def excluir_anexo(id):
    anexo = AnexoPratica.query.get_or_404(id)
    pratica_id = anexo.pratica_id
    db.session.delete(anexo)
    db.session.commit()
    flash("Anexo apagado.", "info")
    return redirect(url_for("blue_admin.editar_pratica", id=pratica_id))


# ======= CRUD DE ARTIGOS =======
from app.blue_admin.forms import ArtigoForm

@blue_admin.route("/artigos")
@admin_required
def artigos():
    page = request.args.get('page', 1, type=int)
    pagination = Artigo.query.order_by(Artigo.created_at.desc()).paginate(page=page, per_page=15)
    return render_template("blue_admin/gerenciar_artigos.html", pagination=pagination)

@blue_admin.route("/artigo/novo", methods=["GET", "POST"])
@admin_required
def novo_artigo():
    form = ArtigoForm()
    if form.validate_on_submit():
        artigo = Artigo(
            titulo=form.titulo.data, autor_nome=form.autor_nome.data,
            resumo=form.resumo.data, conteudo=form.conteudo.data,
            publicado=form.publicado.data, author_id=current_user.id
        )
        artigo.save()
        flash("Artigo criado.", "success")
        return redirect(url_for("blue_admin.artigos"))
    return render_template("blue_admin/form_artigo.html", form=form, artigo=None)

@blue_admin.route("/artigo/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar_artigo(id):
    artigo = Artigo.query.get_or_404(id)
    form = ArtigoForm(obj=artigo)
    if form.validate_on_submit():
        artigo.titulo = form.titulo.data
        artigo.autor_nome = form.autor_nome.data
        artigo.resumo = form.resumo.data
        artigo.conteudo = form.conteudo.data
        artigo.publicado = form.publicado.data
        db.session.commit()
        flash("Artigo atualizado.", "success")
        return redirect(url_for("blue_admin.artigos"))
    return render_template("blue_admin/form_artigo.html", form=form, artigo=artigo)

@blue_admin.route("/artigo/<int:id>/excluir", methods=["POST"])
@admin_required
def excluir_artigo(id):
    artigo = Artigo.query.get_or_404(id)
    db.session.delete(artigo)
    db.session.commit()
    flash("Artigo excluído.", "info")
    return redirect(url_for("blue_admin.artigos"))


# ======= CRUD DE PESQUISAS =======
from app.blue_admin.forms import PesquisaForm

@blue_admin.route("/pesquisas")
@admin_required
def pesquisas():
    page = request.args.get('page', 1, type=int)
    pagination = Pesquisa.query.order_by(Pesquisa.created_at.desc()).paginate(page=page, per_page=15)
    return render_template("blue_admin/gerenciar_pesquisas.html", pagination=pagination)

@blue_admin.route("/pesquisa/nova", methods=["GET", "POST"])
@admin_required
def nova_pesquisa():
    form = PesquisaForm()
    if form.validate_on_submit():
        pesq = Pesquisa(
            titulo=form.titulo.data, autores=form.autores.data,
            descricao=form.descricao.data, publicado=form.publicado.data, author_id=current_user.id
        )
        pesq.save()
        flash("Pesquisa enviada.", "success")
        return redirect(url_for("blue_admin.pesquisas"))
    return render_template("blue_admin/form_pesquisa.html", form=form, pesquisa=None)

@blue_admin.route("/pesquisa/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar_pesquisa(id):
    pesq = Pesquisa.query.get_or_404(id)
    form = PesquisaForm(obj=pesq)
    if form.validate_on_submit():
        pesq.titulo = form.titulo.data
        pesq.autores = form.autores.data
        pesq.descricao = form.descricao.data
        pesq.publicado = form.publicado.data
        db.session.commit()
        flash("Pesquisa atualizada.", "success")
        return redirect(url_for("blue_admin.pesquisas"))
    return render_template("blue_admin/form_pesquisa.html", form=form, pesquisa=pesq)

@blue_admin.route("/pesquisa/<int:id>/excluir", methods=["POST"])
@admin_required
def excluir_pesquisa(id):
    pesq = Pesquisa.query.get_or_404(id)
    db.session.delete(pesq)
    db.session.commit()
    flash("Pesquisa excluída.", "info")
    return redirect(url_for("blue_admin.pesquisas"))


# ======= CRUD DE NOTICIAS =======
from app.blue_admin.forms import NoticiaForm

@blue_admin.route("/noticias")
@admin_required
def noticias():
    page = request.args.get('page', 1, type=int)
    pagination = Noticia.query.order_by(Noticia.created_at.desc()).paginate(page=page, per_page=15)
    return render_template("blue_admin/gerenciar_noticias.html", pagination=pagination)

@blue_admin.route("/noticia/nova", methods=["GET", "POST"])
@admin_required
def nova_noticia():
    form = NoticiaForm()
    if form.validate_on_submit():
        noticia = Noticia(
            titulo=form.titulo.data, descricao=form.descricao.data,
            publicado=form.publicado.data, author_id=current_user.id
        )
        noticia.save()
        flash("Notícia criada.", "success")
        return redirect(url_for("blue_admin.noticias"))
    return render_template("blue_admin/form_noticia.html", form=form, noticia=None)

@blue_admin.route("/noticia/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar_noticia(id):
    noticia = Noticia.query.get_or_404(id)
    form = NoticiaForm(obj=noticia)
    if form.validate_on_submit():
        noticia.titulo = form.titulo.data
        noticia.descricao = form.descricao.data
        noticia.publicado = form.publicado.data
        db.session.commit()
        flash("Notícia atualizada.", "success")
        return redirect(url_for("blue_admin.noticias"))
    return render_template("blue_admin/form_noticia.html", form=form, noticia=noticia)

@blue_admin.route("/noticia/<int:id>/excluir", methods=["POST"])
@admin_required
def excluir_noticia(id):
    noticia = Noticia.query.get_or_404(id)
    db.session.delete(noticia)
    db.session.commit()
    flash("Notícia excluída.", "info")
    return redirect(url_for("blue_admin.noticias"))

# ==========================================
# PAINEL DE COMENTÁRIOS (MODERAÇÃO)
# ==========================================
from app.models import Comentario

@blue_admin.route('/comentarios')
@admin_required
def comentarios():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    
    query = Comentario.query
    if status_filter == 'pendentes':
        query = query.filter_by(aprovado=False)
    elif status_filter == 'aprovados':
        query = query.filter_by(aprovado=True)
        
    pagination = query.order_by(Comentario.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('blue_admin/gerenciar_comentarios.html', pagination=pagination, status_filter=status_filter)

@blue_admin.route('/comentario/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_comentario(id):
    c = Comentario.query.get_or_404(id)
    c.aprovado = not c.aprovado
    db.session.commit()
    flash(f'Comentário {"aprovado" if c.aprovado else "ocultado"} com sucesso.', 'success')
    return redirect(request.referrer or url_for('blue_admin.comentarios'))

@blue_admin.route('/comentario/<int:id>/excluir', methods=['POST'])
@admin_required
def excluir_comentario(id):
    c = Comentario.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Comentário excluído permanentemente.', 'info')
    return redirect(request.referrer or url_for('blue_admin.comentarios'))
