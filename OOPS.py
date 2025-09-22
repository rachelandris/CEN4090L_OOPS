import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import encryption
from flask_socketio import SocketIO
from flask_mail import Mail, Message
import DB_set_up

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_default_secret_key')

DATABASE_PATH = 'data/OOPS_DB.db'

# Initialize Flask-SocketIO
socketio = SocketIO(app)



app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                UserId INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT,
                Email TEXT UNIQUE,
                Password TEXT,
                IsSeller BOOLEAN
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Items (
                ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
                ItemName TEXT,
                Category TEXT,
                Description TEXT,
                Price DECIMAL,
                SellerId INTEGER,
                FOREIGN KEY (SellerId) REFERENCES Users(UserId)
            )
        ''')
        conn.commit()

def seed_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM Users')
        if cursor.fetchone()[0] == 0:
            password_hash = bcrypt.hashpw('adminpass'.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO Users (Username, Email, Password, IsSeller) VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@example.com', password_hash, True))
        
        cursor.execute('SELECT COUNT(*) FROM Items')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO Items (ItemName, Category, Description, Price, SellerId) VALUES (?, ?, ?, ?, ?)
            ''', ('Example Item', 'Category1', 'This is a sample item description.', 19.99, 1))
        
        conn.commit()

def fetch_favorite_items(user_id):
    conn = sqlite3.connect('data/OOPS_DB.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT Items.ItemId, Items.ItemName, Items.Description, Items.Price, Photos.ImageURL
        FROM Favorites
        JOIN Items ON Favorites.ItemId = Items.ItemId
        JOIN Photos ON Items.ItemId = Photos.ItemId
        WHERE Favorites.UserId = ?
    ''', (user_id,))
    favorite_items = cur.fetchall()
    conn.close()
    return favorite_items

def fetch_cart_items(user_id):
    conn = get_db_connection()
    cart_items = conn.execute('SELECT * FROM Cart WHERE UserId = ?', (user_id,)).fetchall()
    conn.close()
    return cart_items

def calculate_total_price(cart_items):
    total_price = sum(item['Price'] * item['Quantity'] for item in cart_items)
    # Return total price formatted to 2 decimal places
    return f"{total_price:.2f}"


def process_payment(total_price):
    # Simulate payment processing
    return True

def mark_items_as_purchased(user_id, cart_items):
    conn = get_db_connection()
    for item in cart_items:
        conn.execute('INSERT INTO Purchases (ItemId, BuyerId, PurchaseDate) VALUES (?, ?, ?)',
                     (item['ItemId'], user_id, datetime.datetime.now()))
    conn.commit()
    conn.close()

def send_confirmation_email(user_id, cart_items, total_price):
    # Simulate sending an email
    print("Sending email to User ID:", user_id)

create_tables()
seed_database()

def fetch_cart_items(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Cart WHERE UserId = ?', (user_id,))
    cart_items = cur.fetchall()
    conn.close()
    return cart_items

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    if request.method == 'POST':
        search_query = request.form.get('search', '')
        items = conn.execute('SELECT * FROM Items WHERE ItemName LIKE ?', ('%' + search_query + '%',)).fetchall()
    else:
        items = conn.execute('SELECT * FROM Items ORDER BY ItemId DESC LIMIT 10').fetchall()
    conn.close()
    return render_template('home.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))  # Using the name of the route function


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM Users WHERE Username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        if user:
            if encryption.verify_password(password, user['Password']):
                session['user_id'] = user['UserId']
                flash('Login successful!')
                return redirect(url_for('home'))
            else:
                flash('Invalid password!')
        else:
            flash('Invalid username!')
        
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))  # Assuming 'home' is the route you want logged-in users to go

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')  # Ensure proper decoding

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE Username = ? OR Email = ?', (username, email))
            if cursor.fetchone():
                flash('Username or email already exists.')
                return redirect(url_for('signup'))
            cursor.execute('INSERT INTO Users (Username, Email, Password) VALUES (?, ?, ?)', (username, email, hashed_password))
            conn.commit()
            flash('Signup successful! Please login.')
            return redirect(url_for('login'))
        finally:
            conn.close()
    return render_template('signup.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id', None)
        flash('You have been successfully logged out.')
        return redirect(url_for('index'))
    else:
        flash('Invalid request method for logout.')
        return redirect(url_for('index'))


@app.route('/listing', methods=['GET', 'POST'])
def listing():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Fix key names to match form fields
        item_name = request.form.get('item_name', None)
        description = request.form.get('description', None)
        price = request.form.get('price', None)
        seller_id = session.get('user_id')
        
        if item_name and description and price:
            # Connect to the database
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Insert the item into the Items table
            cur.execute(
                'INSERT INTO Items (ItemName, Description, Price, SellerId) VALUES (?, ?, ?, ?)', 
                (item_name, description, price, seller_id)
            )
            item_id = cur.lastrowid
            
            # Insert photos into the Photos table (if needed)
            photo_urls = request.form.getlist('photos')  # Check correct key
            if photo_urls:
                for url in photo_urls:
                    cur.execute(
                        'INSERT INTO Photos (ItemId, ImageURL) VALUES (?, ?)', 
                        (item_id, url)
                    )
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            # Redirect to listing success page after successful listing
            return redirect(url_for('successful_listing'))
        
        # If any required field is missing, flash a message
        flash("Please fill in all required fields.")
        return redirect(url_for('listing'))

    # Render the listing form template for GET requests
    return render_template('listing.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM Users WHERE UserId = ?', (user_id,))
    user_details = cur.fetchone()
    if not user_details:
        flash('User not found.')
        return redirect(url_for('login'))

    # Fetch listings
    cur.execute('''
        SELECT i.ItemName, i.Description, i.Price, p.ImageURL
        FROM Items i
        LEFT JOIN Photos p ON i.ItemId = p.ItemId
        WHERE i.SellerId = ?
    ''', (user_id,))
    user_listings = cur.fetchall()

    # Fetch user purchase history with their photos
    cur.execute('''
        SELECT p.PurchaseDate, i.ItemName, i.Description, i.Price, ph.ImageURL
        FROM Purchases p
        JOIN Items i ON p.ItemId = i.ItemId
        LEFT JOIN Photos ph ON i.ItemId = ph.ItemId
        WHERE p.BuyerId = ?
    ''', (user_id,))
    purchase_history = cur.fetchall()

    conn.close()

    return render_template(
        'profile.html',
        user_details=user_details,
        user_listings=user_listings,
        purchase_history=purchase_history
    )

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        flash('Please log in to add items to the cart.')
        return redirect(url_for('login'))

    item_name = request.form.get('item_name')  # Retrieve the item name from the form
    if not item_name:
        flash("Item name is missing.")
        return redirect(url_for('buying'))

    user_id = session['user_id']

    conn = get_db_connection()
    try:
        # Find the item in the Items table by its name
        item = conn.execute(
            'SELECT ItemId FROM Items WHERE ItemName = ?',
            (item_name,)
        ).fetchone()

        if not item:
            flash("Item not found.")
            return redirect(url_for('buying'))

        item_id = item['ItemId']

        # Insert the item into the Cart table with default quantity of 1
        conn.execute(
            'INSERT INTO Cart (UserId, ItemId, Quantity) VALUES (?, ?, 1)',
            (user_id, item_id)
        )
        conn.commit()
        flash("Item added to cart!")
    except sqlite3.Error as e:
        flash(f"Database error: {e}")
    finally:
        conn.close()

    return redirect(url_for('cart'))




@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please log in to view your cart.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        # Fetch cart items, joining with Items for item details
        cart_items = conn.execute(
            '''
            SELECT Cart.CartId, Cart.Quantity, Items.ItemId, 
                   Items.ItemName, Items.Description, Items.Price
            FROM Cart
            JOIN Items ON Cart.ItemId = Items.ItemId
            WHERE Cart.UserId = ?
            ''',
            (user_id,)
        ).fetchall()
        total_price = calculate_total_price(cart_items)
    finally:
        conn.close()

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/cart/<int:item_id>', methods=['PUT'])
def update_cart_quantity(item_id):
    if 'user_id' not in session:
        return {"error": "Not authorized"}, 401

    # Ensure the quantity is properly converted to an integer
    try:
        new_quantity = int(request.json.get('quantity', 1))
    except ValueError:
        return {"error": "Invalid quantity"}, 400  # Handle invalid input

    if new_quantity < 1:
        return {"error": "Quantity must be at least 1"}, 400  # Validate minimum quantity

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        # Update the quantity for the specified item in the cart
        conn.execute(
            'UPDATE Cart SET Quantity = ? WHERE UserId = ? AND ItemId = ?',
            (new_quantity, user_id, item_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}, 500
    finally:
        conn.close()

    return {"success": True}  # Return a success response

@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('login'))

    # Assuming you have a function to fetch favorite items from the database
    favorite_items = fetch_favorite_items(session['user_id'])

    return render_template('favorites.html', favorite_items=favorite_items)


@app.route('/successful-listing')
def successful_listing():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('login'))
    return render_template('successful-listing.html')



@app.route('/buying')
def buying():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Items')
    items = cur.fetchall()
    conn.close()

    return render_template('buying.html', items=items)

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        flash('Please log in to access checkout.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        # Fetch cart items and join with Items to get details
        cart_items = conn.execute(
            '''
            SELECT Cart.CartId, Cart.Quantity, Items.ItemId, 
                   Items.ItemName, Items.Description, Items.Price
            FROM Cart
            JOIN Items ON Cart.ItemId = Items.ItemId
            WHERE Cart.UserId = ?
            ''',
            (user_id,)
        ).fetchall()

        # Calculate the total price based on item price and quantity
        total_price = sum(item['Price'] * item['Quantity'] for item in cart_items)
    finally:
        conn.close()

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        flash("Please log in to complete your purchase.")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Simulate payment processing (e.g., validate card details, process payment, etc.)
    # You can add payment processing logic here, if needed.

    # After processing payment, mark the items as purchased
    conn = get_db_connection()
    try:
        # Fetch cart items for the user
        cart_items = conn.execute(
            'SELECT * FROM Cart WHERE UserId = ?',
            (user_id,)
        ).fetchall()

        # Mark each item as purchased and clear the cart
        for item in cart_items:
            item_id = item['ItemId']
            # Insert into Purchases or similar table to record the purchase
            conn.execute(
                'INSERT INTO Purchases (ItemId, BuyerId, PurchaseDate) VALUES (?, ?, datetime("now"))',
                (item_id, user_id)
            )
            # Remove the item from the Cart
            conn.execute(
                'DELETE FROM Cart WHERE UserId = ? AND ItemId = ?',
                (user_id, item_id)
            )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for('purchase_success'))  # Redirect to the success page




@app.route('/purchase_success')
def purchase_success():
    return render_template('purchase_success.html')  # Renders the success page


# WebSocket route for handling chat messages
@socketio.on('message')
def handle_message(message):
    # Broadcast the received message to all connected clients
    socketio.send(message, broadcast=True)

# Chat page route
@app.route('/chat')
def chat():
    if 'user_id' not in session:
        flash('You need to login first.')
        return redirect(url_for('login'))

    return render_template('chat.html')



if __name__ == '__main__':
    app.run(debug=True)
