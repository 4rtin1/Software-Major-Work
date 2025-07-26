# Import the database instance and User model
from models import db, User, Game


def create_user(email, password, is_admin=False):
    """
    Create a user if one with the given email doesn't already exist.
    This prevents duplicate users and is useful for seeding.
    """
    # Check if a user with this email already exists in the database
    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"User '{email}' already exists.")
        return existing

    # If not, create a new user and hash the password
    user = User(email=email, is_admin=is_admin)
    user.set_password(password)  # Securely hash the password

    # Save the new user to the database
    db.session.add(user)
    db.session.commit()

    print(f"User '{email}' created.")
    return user

def create_game(title, description, price, genre, size_category):
    """
    Create a game if one with the given title doesn't already exist.
    This prevents duplicate games and is useful for seeding.
    """
    # Check if a game with this title already exists in the database
    existing = Game.query.filter_by(title=title).first()
    if existing:
        print(f"Game '{title}' already exists.")
        return existing

    # If not, create a new game
    game = Game(title=title, description=description, price=price, genre=genre, size_category=size_category)

    # Save the new game to the database
    db.session.add(game)
    db.session.commit()

    print(f"Game '{title}' created.")
    return game

def seed_default_data():
    """
    Add default users to the database for testing/demo purposes.
    - One admin user
    - One regular user
    This function is called when the app first starts.
    """
    create_user("admin@example.com", "admin123", is_admin=True)
    create_user("user@example.com", "user123", is_admin=False)
    create_game("Space Adventure", "Explore the universe!", 19.99, "Action", "6.78gb", "10+"),
    create_game("Puzzle Quest", "Solve tricky puzzles.", 9.99, "Puzzle", "0.45gb", "3+"),
    create_game("Battle Arena", "Fight against players online.", 14.99, "Action", "2.34gb", "12+"),
    create_game("Fantasy World", "A magical RPG adventure.", 29.99, "RPG", "5.67gb", "10+"),
    create_game("Cooking Master", "Cook delicious meals!", 4.99, "Simulation", "1.23gb", "10+")