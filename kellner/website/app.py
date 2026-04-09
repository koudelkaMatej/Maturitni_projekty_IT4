
from flask import Flask, render_template, request, session, redirect, url_for, flash
import hashlib
import mysql.connector
from pripojeni import *
app = Flask(__name__)
app.secret_key = 'uber_mosh_secret_key_2026'

db_config = {
    'user': USER,
    'password': PASSWORD,
    'host': HOST,
    'database': DATABASE
}

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Exception as e:
        print(f"DB Connection Error: {e}")
        print(f"Attempted connection with: host={db_config['host']}, user={db_config['user']}, db={db_config['database']}")
        return None


def init_db():
    """Ensure Ubermosh table exists with proper schema."""
    conn = get_db_connection()
    if not conn:
        print("ERROR: Cannot connect to database for initialization!")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create table with explicit schema
        create_sql = """
        CREATE TABLE IF NOT EXISTS Ubermosh (
            nickname VARCHAR(255) PRIMARY KEY,
            score INT DEFAULT 0,
            gamemode VARCHAR(50) DEFAULT 'Normal',
            status VARCHAR(50) DEFAULT 'Registered',
            password VARCHAR(255) NOT NULL
        )
        """
        cursor.execute(create_sql)
        conn.commit()
        print("✓ Ubermosh table created/verified successfully")
        
        # Check if table actually exists by querying it
        cursor.execute("SELECT COUNT(*) FROM Ubermosh")
        count = cursor.fetchone()[0]
        print(f"✓ Table verified: {count} records in Ubermosh")
        
        cursor.close()
        return True
    except Exception as e:
        print(f"✗ DB Init Error: {e}")
        return False
    finally:
        if conn:
            conn.close()


init_db()

# Test database connection on startup
try:
    test_conn = get_db_connection()
    if test_conn:
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT COUNT(*) FROM Ubermosh")
        count = test_cursor.fetchone()[0]
        test_cursor.close()
        test_conn.close()
        print(f"✓ Database connection successful. Ubermosh table has {count} records.")
    else:
        print("✗ Database connection failed on startup!")
except Exception as e:
    print(f"✗ Database test query failed: {e}")

@app.route('/')
def index():
    conn = get_db_connection()
    
    leaderboard = []
    top_per_mode = {}
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Main Leaderboard (Top 10)
        # Tie breaker: Score DESC, Status (Survived > Died) DESC (Survived starts with S, Died with D, so S > D works alphabetically)
        cursor.execute("SELECT * FROM Ubermosh ORDER BY score DESC, status DESC LIMIT 10")
        leaderboard = cursor.fetchall()
        
        # 2. Top 1 per Gamemode
        modes = ['Normal', 'Gunner', 'Reflect']
        for mode in modes:
            cursor.execute("SELECT * FROM Ubermosh WHERE gamemode = %s ORDER BY score DESC, status DESC LIMIT 1", (mode,))
            res = cursor.fetchone()
            if res:
                top_per_mode[mode] = res
                
        cursor.close()
        conn.close()
        
    return render_template('index.html', leaderboard=leaderboard, top_per_mode=top_per_mode)


def username_exists(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM Ubermosh WHERE nickname = %s", (username,))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except Exception as e:
            print(f"Username Exists Error: {e}")
        finally:
            conn.close()
    return False


def get_user_password(username):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM Ubermosh WHERE nickname = %s", (username,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Get User Password Error: {e}")
        finally:
            conn.close()
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('login'))

        stored_password = get_user_password(username)
        if stored_password is None:
            flash('Invalid username or password.')
            return redirect(url_for('login'))

        hashed_password = hash_password(password)
        if stored_password == hashed_password:
            session['username'] = username
            flash(f'Logged in as {username}.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password or not confirm_password:
            flash('All fields are required.')
            return redirect(url_for('register'))

        if len(username) < 3 or len(password) < 3:
            flash('Username and password must be at least 3 characters.')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))

        if username.lower() == 'host':
            flash('The username Host is reserved.')
            return redirect(url_for('register'))

        if username_exists(username):
            flash('Username already exists. Please choose another.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed. Please try again.')
            print(f'✗ Cannot register {username}: No database connection')
            return redirect(url_for('register'))
        
        try:
            cursor = conn.cursor()
            hashed_pwd = hash_password(password)
            cursor.execute(
                'INSERT INTO Ubermosh (nickname, score, gamemode, status, password) VALUES (%s, %s, %s, %s, %s)',
                (username, 0, 'Normal', 'Registered', hashed_pwd)
            )
            conn.commit()
            cursor.close()
            print(f'✓ Registered user: {username}')
            flash('Registration successful. You can now log in.')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(f'✗ Register Error for {username}: {err}')
            flash(f'Registration failed: {str(err)[:100]}')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        flash('Please log in to view your profile.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user_data = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT nickname, score, gamemode, status FROM Ubermosh WHERE nickname = %s', (username,))
            user_data = cursor.fetchone()
            cursor.close()
        except Exception as e:
            print(f'Profile Fetch Error: {e}')
        finally:
            conn.close()

    return render_template('profile.html', username=username, user_data=user_data)


@app.route('/account', methods=['GET', 'POST'])
def account():
    username = session.get('username')
    if not username:
        flash('Please log in to access your account.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.')
            return redirect(url_for('account'))

        stored_password = get_user_password(username)
        if stored_password is None:
            flash('Cannot verify current password.')
            return redirect(url_for('account'))

        hashed_current = hash_password(current_password)
        if stored_password != hashed_current:
            flash('Current password is incorrect.')
            return redirect(url_for('account'))

        if new_password != confirm_password:
            flash('New passwords do not match.')
            return redirect(url_for('account'))

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE Ubermosh SET password = %s WHERE nickname = %s',
                    (hash_password(new_password), username)
                )
                conn.commit()
                cursor.close()
                flash('Password updated successfully.')
            except Exception as e:
                print(f'Account Update Error: {e}')
                flash('Unable to update password. Please try again.')
            finally:
                conn.close()

    return render_template('account.html', username=username)


if __name__ == '__main__':
    app.run(debug=True)
