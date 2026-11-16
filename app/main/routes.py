from flask import render_template, request, current_app
from sqlalchemy import or_
from app.main import bp
from app.models import Post, Tag, User


@bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip()

    query = Post.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Post.title.ilike(like), Post.body.ilike(like)))
    if tag:
        query = query.filter(Post.tags.any(Tag.name == tag.lower()))

    pagination = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("index.html", pagination=pagination, tags=tags, q=q, tag=tag)


@bp.route("/user/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    return render_template("profile.html", user=user, pagination=pagination)
