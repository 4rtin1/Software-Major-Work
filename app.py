# Import Flask and related modules
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

# Import your database model and forms
from models import db, User, Game
from forms import RegisterForm, LoginForm, EditAccountForm
from config import Config
from seed_db import seed_default_data

# Create the Flask app instance
app = Flask(__name__)
app.config.from_object(Config)  # Load settings like SECRET_KEY and DB path

# Initialize the database with the app
db.init_app(app)

# Set up Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect to this route if login is required


@login_manager.user_loader
def load_user(user_id):
    """Load a user by ID for session tracking (used by Flask-Login)."""
    return db.session.get(User, int(user_id))

def get_cart():
    return session.get("cart", [])

def save_cart(cart):
    session["cart"] = cart

@app.route("/")
def home():
    """Redirect users from the home page to the dashboard."""
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    - Redirects to dashboard if already logged in.
    - Saves user to the database if form is valid.
    """
    if current_user.is_authenticated:
        return redirect(
            url_for("dashboard")
        )  # Don't allow already logged-in users to register again

    form = RegisterForm()
    # If the form was submitted (POST request) and passed all validation checks
    if form.validate_on_submit():
        # Create a new user and save to the database
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in an existing user.
    - Redirects to dashboard if already logged in.
    - Authenticates credentials and logs in the user.
    """
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists and password is correct
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)  # Log in the user
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    """Log out the current user and redirect to the login page."""
    logout_user()
    return redirect(url_for("login"))

# Add to Cart Route
@app.route("/add_to_cart/<int:game_id>", methods=["POST"])
@login_required
def add_to_cart(game_id):
    cart = get_cart()
    if game_id not in cart:
        cart.append(game_id)
        save_cart(cart)
        flash("Game added to cart!", "success")
    else:
        flash("Game is already in your cart.", "warning")
    return redirect(request.referrer or url_for("catalogue"))

# Remove from Cart Route
@app.route("/remove_from_cart/<int:game_id>", methods=["POST"])
@login_required
def remove_from_cart(game_id):
    cart = get_cart()
    if game_id in cart:
        cart.remove(game_id)
        save_cart(cart)
        flash("Game removed from cart.", "success")
    else:
        flash("Game not found in cart.", "warning")
    return redirect(url_for("cart"))

# Cart Page
@app.route("/cart")
@login_required
def cart():
    cart = get_cart()
    games = Game.query.filter(Game.id.in_(cart)).all() if cart else []
    return render_template("cart.html", games=games)

# Checkout Route
@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart = get_cart()
    if not cart:
        flash("Your cart is empty!", "warning")
        return redirect(url_for("cart"))
    games = Game.query.filter(Game.id.in_(cart)).all()
    for game in games:
        if game not in current_user.purchased_games:
            current_user.purchased_games.append(game)
    db.session.commit()
    save_cart([])  # Clear cart
    flash("Purchase successful! Games added to your inventory.", "success")
    return redirect(url_for("inventory"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Render the dashboard page for logged-in users."""
    return render_template("dashboard.html")

@app.route("/inventory")
@login_required
def inventory():
    user_games = current_user.purchased_games.all()
    print("INVENTORY GAMES:", user_games)
    return render_template("inventory.html", games=user_games, is_inventory=True)

@app.route("/catalogue", methods=["GET"])
@login_required
def catalogue():
    games = Game.query.all()
    
    user_games = current_user.purchased_games.all()
    user_game_ids = {g.id for g in user_games}

    # Build unique genre list
    unique_genres = set()
    for g in games:
        if g.genre:
            for genre in g.genre.split(','):
                unique_genres.add(genre.strip())
    all_genres = sorted(unique_genres)

    # Attach numeric price/size to each game
    for g in games:
        g.price_num = parse_price(g.price)
        g.size_num = parse_size(g.size)

    # Find min/max for sliders
    price_values = [g.price_num for g in games]
    size_values = [g.size_num for g in games]
    min_price_val = min(price_values) if price_values else 0
    max_price_val = max(price_values) if price_values else 100
    min_size_val = min(size_values) if size_values else 0
    max_size_val = max(size_values) if size_values else 100

    # These are the ACTUAL slider/filter values (defaults to full range)
    min_price = request.args.get("min_price", min_price_val, type=float)
    max_price = request.args.get("max_price", max_price_val, type=float)
    min_size = request.args.get("min_size", min_size_val, type=float)
    max_size = request.args.get("max_size", max_size_val, type=float)
    title = request.args.get("title", "", type=str)
    selected_genres = request.args.getlist("genres")

    # Apply filters
    filtered_games = []
    for g in games:
        # Skip games already owned by the user
        if g.id in user_game_ids:
            continue  
        # Title filter
        if title and title.lower() not in g.title.lower():
            continue
        # Genre filter (match any selected genre)
        game_genres = [x.strip() for x in g.genre.split(',')] if g.genre else []
        if selected_genres:
            if not any(genre in game_genres for genre in selected_genres):
                continue
        # Price/size filters
        if g.price_num < min_price or g.price_num > max_price:
            continue
        if g.size_num < min_size or g.size_num > max_size:
            continue
        filtered_games.append(g)

    # AJAX update: return just the games grid
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("game_cards.html", games=filtered_games)

    # Full page
    return render_template(
        "catalogue.html",
        games=filtered_games,
        all_genres=all_genres,
        min_price_val=min_price_val,
        max_price_val=max_price_val,
        min_price=min_price,
        max_price=max_price,
        min_size_val=min_size_val,
        max_size_val=max_size_val,
        min_size=min_size,
        max_size=max_size,
        selected_genres=selected_genres,
        title=title,
    )

@app.route("/game/<int:game_id>")
@login_required
def game_details(game_id):
    game = Game.query.get_or_404(game_id)
    is_inventory = request.args.get('is_inventory', 'false').lower() == 'true'
    return render_template("game_details.html", game=game, is_inventory=is_inventory)

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    Allow the logged-in user to update their email.
    - Shows a form prefilled with the current email.
    - Validates and saves new email if submitted.
    """
    # Prefill form with the current user's email
    form = EditAccountForm(original_email=current_user.email)
    if form.validate_on_submit():
        # Update the user's email
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated.", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.email.data = current_user.email  # Fill in the email when the page loads
    return render_template("edit_account.html", form=form)


@app.route("/users")
@login_required
def users():
    """
    Admin-only view of all registered users.
    - Redirects non-admins back to dashboard.
    """
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))

    # Show a list of all users in the system
    all_users = User.query.all()
    return render_template("users.html", users=all_users)

@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't delete Administrators!", "warning")
        return redirect(url_for("users"))
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.email} deleted.", "success")
    return redirect(url_for("users"))

@app.route("/admin/promote_user/<int:user_id>", methods=["POST"])
@login_required
def promote_user(user_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("User is already an admin.", "info")
        return redirect(url_for("users"))
    user.is_admin = True
    db.session.commit()
    flash(f"User {user.email} promoted to admin.", "success")
    return redirect(url_for("users"))

@app.route("/admin/games")
@login_required
def games_admin():
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    games = Game.query.all()
    return render_template("games_admin.html", games=games)

@app.route("/admin/delete_game/<int:game_id>", methods=["POST"])
@login_required
def delete_game(game_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    flash(f"Game '{game.title}' deleted.", "success")
    return redirect(url_for("games_admin"))

@app.route("/admin/edit_game/<int:game_id>", methods=["GET", "POST"])
@login_required
def edit_game(game_id):
    if not current_user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard"))
    game = Game.query.get_or_404(game_id)
    if request.method == "POST":
        game.title = request.form["title"]
        game.description = request.form["description"]
        game.developer = request.form["developer"]
        game.publisher = request.form["publisher"]
        game.price = request.form["price"]
        game.genre = request.form["genre"]
        game.size = request.form["size"]
        game.video_link = request.form["video_link"]
        db.session.commit()
        flash("Game updated successfully.", "success")
        return redirect(url_for("games_admin"))
    return render_template("edit_game.html", game=game)

def parse_price(price_str):
    if not price_str or "free" in price_str.lower():
        return 0.0
    # Remove $ and commas, then convert
    try:
        return float(price_str.replace("$", "").replace(",", "").strip())
    except Exception:
        return 0.0

def parse_size(size_str):
    if not size_str:
        return 0.0
    size_str = size_str.strip().lower()
    try:
        if size_str.endswith("gb"):
            return float(size_str[:-2].strip())
        if size_str.endswith("mb"):
            return float(size_str[:-2].strip()) / 1024
        return float(size_str)
    except Exception:
        return 0.0

if __name__ == "__main__":
    """
    Initialize the database, seed default users, and start the development server.
    This block runs only when this file is executed directly (not imported), i.e. "python app.py".
    """
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        seed_default_data()  # Add default admin and regular users

    app.run(debug=True)  # Start the server with debug mode (auto-reloads on changes)
