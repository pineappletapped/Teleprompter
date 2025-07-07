from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    jsonify,
)
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os

app = Flask(__name__)

# Allow configuration via environment variables so the app can be deployed on
# shared hosting providers such as Asura. A default SQLite database is used
# for local development.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "replace-this-with-a-secure-key"
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(app.root_path, "teleprompter.db"),
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    scripts = db.relationship("Script", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)


class LiveSession(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, default="")
    owner = db.relationship("User", backref="live_sessions")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already taken")
            return redirect(url_for("register"))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    scripts = Script.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", scripts=scripts)


@app.route("/script/new", methods=["GET", "POST"])
@login_required
def new_script():
    if request.method == "POST":
        if Script.query.filter_by(user_id=current_user.id).count() >= 20:
            flash("Script limit reached (20). Delete old scripts to add more.")
            return redirect(url_for("dashboard"))
        title = request.form["title"]
        body = request.form["body"]
        s = Script(title=title, body=body, owner=current_user)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("script_form.html")


@app.route("/script/<int:script_id>")
@login_required
def view_script(script_id):
    script = Script.query.get_or_404(script_id)
    if script.owner != current_user:
        flash("Unauthorized")
        return redirect(url_for("dashboard"))
    return render_template("teleprompter.html", script=script)


@app.route("/live/new")
@login_required
def new_live():
    session = LiveSession(id=uuid.uuid4().hex, owner=current_user)
    db.session.add(session)
    db.session.commit()
    return redirect(url_for("live_input", session_id=session.id))


@app.route("/live/<session_id>/input", methods=["GET", "POST"])
@login_required
def live_input(session_id):
    session = LiveSession.query.get_or_404(session_id)
    if session.owner != current_user:
        flash("Unauthorized")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        session.text = request.form.get("text", "")
        db.session.commit()
        return ("", 204)
    return render_template("live_input.html", session=session)


@app.route("/live/<session_id>/display")
def live_display(session_id):
    session = LiveSession.query.get_or_404(session_id)
    return render_template("live_display.html", session=session)


@app.route("/live/<session_id>/data")
def live_data(session_id):
    session = LiveSession.query.get_or_404(session_id)
    return jsonify(text=session.text or "")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
