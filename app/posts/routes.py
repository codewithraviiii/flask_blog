from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.posts import bp
from app.forms import PostForm, CommentForm
from app.models import Post, Tag, Comment


def parse_tags(raw):
    names = {t.strip().lower() for t in (raw or "").split(",") if t.strip()}
    tags = []
    for name in names:
        with db.session.no_autoflush:
            tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
        tags.append(tag)
    return tags


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        post.tags = parse_tags(form.tags.data)
        db.session.add(post)
        db.session.commit()
        flash("Post created.", "success")
        return redirect(url_for("posts.view", post_id=post.id))
    return render_template("post_form.html", form=form, heading="New Post")


@bp.route("/<int:post_id>", methods=["GET", "POST"])
def view(post_id):
    post = db.get_or_404(Post, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        db.session.add(Comment(body=form.body.data, author=current_user, post=post))
        db.session.commit()
        flash("Comment added.", "success")
        return redirect(url_for("posts.view", post_id=post.id))
    return render_template("post.html", post=post, form=form)


@bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.tags = parse_tags(form.tags.data)
        db.session.commit()
        flash("Post updated.", "success")
        return redirect(url_for("posts.view", post_id=post.id))
    if not form.is_submitted():
        form.tags.data = ", ".join(t.name for t in post.tags)
    return render_template("post_form.html", form=form, heading="Edit Post")


@bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = db.get_or_404(Post, post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "info")
    return redirect(url_for("main.index"))


@bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    if comment.author != current_user:
        abort(403)
    pid = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for("posts.view", post_id=pid))
