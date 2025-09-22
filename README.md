# CEN4090L_OOPS
# CEN4090L_e-commerce
CEN4090L project 

### README for the OOPS (Our Online Personal Stylist)

#### Group 6 - Software Implementation and Testing Document

**Version 3.0**

**Authors:** 
- Sola Adebisi
- Rachel Andris
- Hasan Bazzi
- Alyssa Evans
- Souhail Marnaoui

#### Project Overview

OOPS (Our Online Personal Stylist) is an innovative e-commerce platform designed to streamline the purchasing and selling of clothing items. The platform caters to both buyers and sellers with tailored functionalities including item listings, browsing capabilities, and purchasing options. This application combines user-friendly interfaces with robust backend functionalities to ensure a seamless shopping experience.

#### Features

- **User Authentication:** Secure login and registration processes with encrypted passwords.
- **Item Listings:** Sellers can list their items with descriptions, prices, and categories.
- **Shopping Cart:** Enhanced shopping cart functionalities that allow users to add items, modify quantities, or remove them.
- **Real-Time Chat:** Users can communicate in real-time using integrated chat functionalities.
- **Email Notifications:** Automated email notifications for important user actions like purchase confirmations.

#### Technologies Used

- **Programming Languages:** Python, HTML, CSS, SQL
- **Frameworks and Libraries:** Flask, Flask-SocketIO, Flask-Mail, bcrypt, pycrypto
- **Database:** SQLite3
- **Others:** Pandas for data management, HMAC and Hashlib for secure hashing

#### Installation & Setup

1. **Clone the Repository:**
   - Ensure you have Git installed and clone the project repository to your local machine.

2. **Install Dependencies:**
   - Run `pip install flask flask_socketio flask_mail bcrypt pycrypto pandas` to install all required Python packages.

3. **Configure Environment:**
   - Set environment variables for `SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_DEFAULT_SENDER`.
   - Adjust the mail server settings (`MAIL_SERVER` and `MAIL_PORT`) in the application to your preferences.

4. **Database Initialization:**
   - Execute the provided scripts to create and populate the database with initial data.

#### Running the Application

Execute the following command to run the application:

```bash
python OOPS.py
