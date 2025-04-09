from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Initialize Flask App
app = Flask(__name__)

# Configure Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///thereviews.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with Declarative Base
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define the Review model using `Mapped` and `mapped_column`
class Review(db.Model):
    __tablename__ = "thereviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    def __init__(self, title: str, text: str, rating: int):
        self.title = title
        self.text = text
        self.rating = rating

# DATABASE UTILITY CLASS
class Database:
    def __init__(self):
        pass

    def get(self, review_id: int = None):
        """Retrieve all reviews or a specific review by ID."""
        if review_id:
            return db.session.get(Review, review_id)
        return db.session.query(Review).all()

    def create(self, title: str, text: str, rating: int):
        """Create a new review."""
        new_review = Review(title=title, text=text, rating=rating)
        db.session.add(new_review)
        db.session.commit()

    def update(self, review_id: int, title: str, text: str, rating: int):
        """Update an existing review."""
        review = self.get(review_id)
        if review:
            review.title = title
            review.text = text
            review.rating = rating
            db.session.commit()

    def delete(self, review_id: int):
        """Delete a review."""
        review = self.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()

db_manager = Database()  # Create a database manager instance

# Initialize database with sample data
@app.before_request
def setup():
    with app.app_context():
        db.create_all()
        if not db_manager.get():  # If database is empty, add a sample entry
            db_manager.create("Mr. Pumpkin Man", "This is a pretty bad movie", 4)
            db_manager.create("Man", "This is a pretty good movie", 3)
            db_manager.create("Ma2n", "This is a pretty fsadf movie", 3)
            print("Database initialized with sample data!")

# Reset the database
@app.route('/reset-db', methods=['GET', 'POST'])
def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset: success!")
    return "Database has been reset!", 200

# ROUTES
"""You will add all of your routes below, there is a sample one which you can use for testing"""

@app.route('/')
def show_all_reviews():
    reviews = db_manager.get()
    return render_template('index.html', title="Movie Reviews", reviews=reviews)

@app.route('/new_review')
def create_review():
    return render_template('edit-review.html', title="New Review", review=None)

@app.route('/review/<review_title>/view', methods=['GET']) # This post helped me with dynamic urls & 404 handling: https://stackoverflow.com/questions/35107885/how-to-generate-dynamic-urls-in-flask
def show_review(review_title):
    reviews = db_manager.get()
    for review in reviews:
        if (review.title == review_title):
            return render_template('review.html', title=review, review=review)
    return render_template('404.html'), 404

@app.route('/review/<review_title>/edit', methods=['GET'])
def edit_review(review_title):
    reviews = db_manager.get()
    for review in reviews:
        if (review.title == review_title):
            return render_template('edit-review.html', title=review, review=review)
    return render_template('404.html'), 404

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

  
# RUN THE FLASK APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure DB is created before running the app
    app.run(debug=True)