from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'blog_portal',
    'user': 'postgres',
    'password': '2006'
}


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database and create tables if they don't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create posts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create likes table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, post_id)
            )
        """)
        
        # Create comments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if admin user exists, if not create it
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cur.fetchone():
            admin_password = generate_password_hash('admin123')
            cur.execute("""
                INSERT INTO users (username, email, password, role)
                VALUES ('admin', 'admin@blog.com', %s, 'admin')
            """, (admin_password,))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        conn.close()
        return False

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE id = %s", (session['user_id'],))
            user_role = cur.fetchone()
            cur.close()
            conn.close()
            
            if not user_role or user_role[0] != 'admin':
                flash('Admin access required.', 'error')
                return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page showing all blog posts"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return render_template('index.html', posts=[])
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT p.*, u.username, 
                   COUNT(DISTINCT l.id) as like_count,
                   COUNT(DISTINCT c.id) as comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            GROUP BY p.id, u.username
            ORDER BY p.created_at DESC
        """)
        posts = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('index.html', posts=posts)
    except psycopg2.Error as e:
        print(f"Error fetching posts: {e}")
        cur.close()
        conn.close()
        return render_template('index.html', posts=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error.', 'error')
            return render_template('login.html')
        
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, username, password, role FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[3]
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.', 'error')
        except psycopg2.Error as e:
            print(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error.', 'error')
            return render_template('signup.html')
        
        try:
            cur = conn.cursor()
            
            # Check if email already exists
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Email already registered.', 'error')
                cur.close()
                conn.close()
                return render_template('signup.html')
            
            # Create new user
            hashed_password = generate_password_hash(password)
            cur.execute("""
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
            """, (username, email, hashed_password))
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except psycopg2.Error as e:
            print(f"Signup error: {e}")
            conn.rollback()
            cur.close()
            conn.close()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing their posts and activity"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return render_template('dashboard.html', posts=[], stats={})
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user's posts
        cur.execute("""
            SELECT p.*, 
                   COUNT(DISTINCT l.id) as like_count,
                   COUNT(DISTINCT c.id) as comment_count
            FROM posts p
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            WHERE p.user_id = %s
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """, (session['user_id'],))
        posts = cur.fetchall()
        
        # Get user stats
        cur.execute("""
            SELECT 
                COUNT(p.id) as total_posts,
                COALESCE(SUM(like_stats.like_count), 0) as total_likes,
                COALESCE(SUM(comment_stats.comment_count), 0) as total_comments
            FROM posts p
            LEFT JOIN (
                SELECT post_id, COUNT(*) as like_count
                FROM likes
                GROUP BY post_id
            ) like_stats ON p.id = like_stats.post_id
            LEFT JOIN (
                SELECT post_id, COUNT(*) as comment_count
                FROM comments
                GROUP BY post_id
            ) comment_stats ON p.id = comment_stats.post_id
            WHERE p.user_id = %s
        """, (session['user_id'],))
        stats = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return render_template('dashboard.html', posts=posts, stats=stats)
        
    except psycopg2.Error as e:
        print(f"Dashboard error: {e}")
        cur.close()
        conn.close()
        return render_template('dashboard.html', posts=[], stats={})

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new blog post"""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error.', 'error')
            return render_template('create_post.html')
        
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO posts (user_id, title, content)
                VALUES (%s, %s, %s)
            """, (session['user_id'], title, content))
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Post created successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except psycopg2.Error as e:
            print(f"Create post error: {e}")
            conn.rollback()
            cur.close()
            conn.close()
            flash('Failed to create post. Please try again.', 'error')
    
    return render_template('create_post.html')

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a blog post"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if post exists and belongs to user (or user is admin)
        if session.get('role') == 'admin':
            cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        else:
            cur.execute("SELECT * FROM posts WHERE id = %s AND user_id = %s", (post_id, session['user_id']))
        
        post = cur.fetchone()
        
        if not post:
            flash('Post not found or access denied.', 'error')
            cur.close()
            conn.close()
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            
            cur.execute("""
                UPDATE posts SET title = %s, content = %s
                WHERE id = %s
            """, (title, content, post_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            flash('Post updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        cur.close()
        conn.close()
        return render_template('edit_post.html', post=post)
        
    except psycopg2.Error as e:
        print(f"Edit post error: {e}")
        cur.close()
        conn.close()
        flash('Error loading post. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    """Delete a blog post"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        cur = conn.cursor()
        
        # Check if post exists and belongs to user (or user is admin)
        if session.get('role') == 'admin':
            cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        else:
            cur.execute("DELETE FROM posts WHERE id = %s AND user_id = %s", (post_id, session['user_id']))
        
        if cur.rowcount > 0:
            conn.commit()
            flash('Post deleted successfully!', 'success')
        else:
            flash('Post not found or access denied.', 'error')
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Delete post error: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        flash('Failed to delete post. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/like_post/<int:post_id>')
@login_required
def like_post(post_id):
    """Like or unlike a post"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection error'})
    
    try:
        cur = conn.cursor()
        
        # Check if user already liked this post
        cur.execute("SELECT id FROM likes WHERE user_id = %s AND post_id = %s", (session['user_id'], post_id))
        existing_like = cur.fetchone()
        
        if existing_like:
            # Unlike the post
            cur.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s", (session['user_id'], post_id))
            action = 'unliked'
        else:
            # Like the post
            cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (session['user_id'], post_id))
            action = 'liked'
        
        # Get updated like count
        cur.execute("SELECT COUNT(*) FROM likes WHERE post_id = %s", (post_id,))
        like_count = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'action': action,
            'like_count': like_count
        })
        
    except psycopg2.Error as e:
        print(f"Like post error: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Failed to like post'})

@app.route('/like_post_redirect/<int:post_id>')
@login_required
def like_post_redirect(post_id):
    """Like or unlike a post and redirect to view_post"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    try:
        cur = conn.cursor()
        
        # Check if user already liked this post
        cur.execute("SELECT id FROM likes WHERE user_id = %s AND post_id = %s", (session['user_id'], post_id))
        existing_like = cur.fetchone()
        
        if existing_like:
            # Unlike the post
            cur.execute("DELETE FROM likes WHERE user_id = %s AND post_id = %s", (session['user_id'], post_id))
            flash('Post unliked!', 'info')
        else:
            # Like the post
            cur.execute("INSERT INTO likes (user_id, post_id) VALUES (%s, %s)", (session['user_id'], post_id))
            flash('Post liked!', 'success')
        
        conn.commit()
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Like post error: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        flash('Failed to like post. Please try again.', 'error')
    
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/comment_post/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    """Add a comment to a post"""
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('view_post', post_id=post_id))
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO comments (user_id, post_id, content)
            VALUES (%s, %s, %s)
        """, (session['user_id'], post_id, content))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash('Comment added successfully!', 'success')
        
    except psycopg2.Error as e:
        print(f"Comment post error: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        flash('Failed to add comment. Please try again.', 'error')
    
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View a single post with all comments"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('index'))
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get the post with author info and stats
        cur.execute("""
            SELECT p.*, u.username, 
                   COUNT(DISTINCT l.id) as like_count,
                   COUNT(DISTINCT c.id) as comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            WHERE p.id = %s
            GROUP BY p.id, u.username
        """, (post_id,))
        
        post = cur.fetchone()
        
        if not post:
            flash('Post not found.', 'error')
            cur.close()
            conn.close()
            return redirect(url_for('index'))
        
        # Get all comments for this post
        cur.execute("""
            SELECT c.*, u.username
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        """, (post_id,))
        
        comments = cur.fetchall()
        
        # Check if current user has liked this post
        user_liked = False
        if session.get('user_id'):
            cur.execute("""
                SELECT id FROM likes 
                WHERE user_id = %s AND post_id = %s
            """, (session['user_id'], post_id))
            user_liked = bool(cur.fetchone())
        
        cur.close()
        conn.close()
        
        return render_template('view_post.html', post=post, comments=comments, user_liked=user_liked)
        
    except psycopg2.Error as e:
        print(f"View post error: {e}")
        cur.close()
        conn.close()
        flash('Error loading post. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin panel for managing users and posts"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return render_template('admin_panel.html', users=[], posts=[], comments=[])
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all users
        cur.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cur.fetchall()
        
        # Get all posts with author info
        cur.execute("""
            SELECT p.*, u.username,
                   COUNT(DISTINCT l.id) as like_count,
                   COUNT(DISTINCT c.id) as comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            GROUP BY p.id, u.username
            ORDER BY p.created_at DESC
        """)
        posts = cur.fetchall()
        
        # Get all comments with author and post info
        cur.execute("""
            SELECT c.*, u.username, p.title as post_title
            FROM comments c
            JOIN users u ON c.user_id = u.id
            JOIN posts p ON c.post_id = p.id
            ORDER BY c.created_at DESC
        """)
        comments = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('admin_panel.html', users=users, posts=posts, comments=comments)
        
    except psycopg2.Error as e:
        print(f"Admin panel error: {e}")
        cur.close()
        conn.close()
        return render_template('admin_panel.html', users=[], posts=[], comments=[])

@app.route('/admin/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    if user_id == session['user_id']:
        flash('Cannot delete your own account.', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_panel'))
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        if cur.rowcount > 0:
            conn.commit()
            flash('User deleted successfully!', 'success')
        else:
            flash('User not found.', 'error')
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Delete user error: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        flash('Failed to delete user. Please try again.', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_comment/<int:comment_id>')
@admin_required
def delete_comment(comment_id):
    """Delete a comment (admin only)"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'error')
        return redirect(url_for('admin_panel'))
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        
        if cur.rowcount > 0:
            conn.commit()
            flash('Comment deleted successfully!', 'success')
        else:
            flash('Comment not found.', 'error')
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Delete comment error: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        flash('Failed to delete comment. Please try again.', 'error')
    
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    # Initialize database on startup
    if init_database():
        print("Database initialized successfully!")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize database. Please check your PostgreSQL connection.")
