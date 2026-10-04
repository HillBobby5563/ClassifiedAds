from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:secret@localhost:5432/classifieds')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# ===== MODELS =====
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    avatar = db.Column(db.String(255))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    listings = db.relationship('Listing', backref='seller', lazy=True, foreign_keys='Listing.seller_id')
    sent_messages = db.relationship('Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    received_messages = db.relationship('Message', backref='receiver', lazy=True, foreign_keys='Message.receiver_id')
    reviews_given = db.relationship('Review', backref='reviewer', lazy=True, foreign_keys='Review.reviewer_id')
    reviews_received = db.relationship('Review', backref='reviewed_user', lazy=True, foreign_keys='Review.user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Listing(db.Model):
    __tablename__ = 'listings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    condition = db.Column(db.String(50))  # new, like_new, good, fair
    image_url = db.Column(db.String(255))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, sold, removed
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('Message', backref='listing', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===== INITIALIZE =====
@app.before_request
def create_tables():
    db.create_all()

# ===== API ENDPOINTS =====

@app.route('/api/users', methods=['POST'])
def register():
    data = request.json
    user = User(username=data['username'], email=data['email'], full_name=data.get('full_name'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'username': user.username}), 201

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'rating': user.rating,
        'phone': user.phone,
        'bio': user.bio,
        'listings_count': len(user.listings),
        'created_at': user.created_at.isoformat()
    }), 200

@app.route('/api/listings', methods=['GET'])
def get_listings():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    search = request.args.get('search')
    sort = request.args.get('sort', 'newest')
    
    query = Listing.query.filter_by(status='active')
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Listing.title.ilike(f'%{search}%'))
    
    if sort == 'price_low':
        query = query.order_by(Listing.price)
    elif sort == 'price_high':
        query = query.order_by(Listing.price.desc())
    else:
        query = query.order_by(Listing.created_at.desc())
    
    listings = query.paginate(page=page, per_page=12)
    
    return jsonify({
        'listings': [{
            'id': l.id,
            'title': l.title,
            'price': l.price,
            'location': l.location,
            'image_url': l.image_url,
            'condition': l.condition,
            'seller': {'id': l.seller.id, 'username': l.seller.username, 'rating': l.seller.rating},
            'created_at': l.created_at.isoformat()
        } for l in listings.items],
        'total': listings.total,
        'pages': listings.pages,
        'current_page': page
    }), 200

@app.route('/api/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    listing.views += 1
    db.session.commit()
    
    return jsonify({
        'id': listing.id,
        'title': listing.title,
        'description': listing.description,
        'price': listing.price,
        'category': listing.category,
        'location': listing.location,
        'condition': listing.condition,
        'image_url': listing.image_url,
        'views': listing.views,
        'seller': {'id': listing.seller.id, 'username': listing.seller.username, 'rating': listing.seller.rating, 'phone': listing.seller.phone},
        'created_at': listing.created_at.isoformat()
    }), 200

@app.route('/api/listings', methods=['POST'])
def create_listing():
    data = request.json
    listing = Listing(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        price=data['price'],
        location=data['location'],
        condition=data.get('condition'),
        image_url=data.get('image_url'),
        seller_id=data['seller_id']
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({'id': listing.id}), 201

@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    message = Message(
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        listing_id=data.get('listing_id'),
        content=data['content']
    )
    db.session.add(message)
    db.session.commit()
    return jsonify({'id': message.id}), 201

@app.route('/api/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    messages = Message.query.filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(Message.created_at.desc()).all()
    
    return jsonify([{
        'id': m.id,
        'sender': m.sender.username,
        'receiver': m.receiver.username,
        'content': m.content,
        'created_at': m.created_at.isoformat()
    } for m in messages]), 200

@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.json
    review = Review(
        reviewer_id=data['reviewer_id'],
        user_id=data['user_id'],
        listing_id=data.get('listing_id'),
        rating=data['rating'],
        text=data.get('text')
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'id': review.id}), 201

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = ['Electronics', 'Furniture', 'Clothing', 'Books', 'Sports', 'Toys', 'Home', 'Other']
    return jsonify(categories), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)