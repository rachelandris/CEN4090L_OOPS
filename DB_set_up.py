import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('data/OOPS_DB.db')
cur = conn.cursor()

# SQL command to create the Users table with a Password column
create_users_table = '''
CREATE TABLE IF NOT EXISTS Users (
    UserId INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    IsSeller BOOLEAN DEFAULT 0
);
'''

# SQL command to create the Items table
create_items_table = '''
CREATE TABLE IF NOT EXISTS Items (
    ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemName TEXT NOT NULL,
    Category TEXT,
    Description TEXT,
    Price DECIMAL(10, 2),
    SellerId INTEGER,
    FOREIGN KEY (SellerId) REFERENCES Users(UserId)
);
'''

# SQL command to create the Photos table
create_photos_table = '''
CREATE TABLE IF NOT EXISTS Photos (
    PhotoId INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemId INTEGER,
    ImageURL TEXT NOT NULL,
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);
'''

# SQL command to create the Purchases table
create_purchases_table = '''
CREATE TABLE IF NOT EXISTS Purchases (
    PurchaseId INTEGER PRIMARY KEY AUTOINCREMENT,
    ItemId INTEGER,
    BuyerId INTEGER,
    PurchaseDate DATETIME,
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId),
    FOREIGN KEY (BuyerId) REFERENCES Users(UserId)
);
'''

# SQL command to create the Messages table
create_messages_table = '''
CREATE TABLE IF NOT EXISTS Messages (
    MessageId INTEGER PRIMARY KEY AUTOINCREMENT,
    SenderId INTEGER,
    ReceiverId INTEGER,
    MessageText TEXT NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SenderId) REFERENCES Users(UserId),
    FOREIGN KEY (ReceiverId) REFERENCES Users(UserId)
);
'''

# SQL command to create the Favorites table
create_favorites_table = '''
CREATE TABLE IF NOT EXISTS Favorites (
    UserId INTEGER,
    ItemId INTEGER,
    PRIMARY KEY (UserId, ItemId),
    FOREIGN KEY (UserId) REFERENCES Users(UserId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);
'''

# SQL command to create the Cart table
create_cart_table = '''
CREATE TABLE IF NOT EXISTS Cart (
    CartId INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INTEGER NOT NULL,
    ItemId INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    FOREIGN KEY (UserId) REFERENCES Users(UserId),
    FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
);
'''

# List of SQL commands
sql_commands = [
    create_users_table, create_items_table, create_photos_table,
    create_purchases_table, create_messages_table, create_favorites_table, create_cart_table
]

# Execute each SQL command
for command in sql_commands:
    try:
        cur.execute(command)
    except sqlite3.OperationalError as e:
        print(f"An error occurred while executing SQL: {e}")
        break

conn.commit()
conn.close()
