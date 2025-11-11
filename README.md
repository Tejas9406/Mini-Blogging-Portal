# Mini Blog Portal

A complete and functional blogging platform built with Flask and PostgreSQL, featuring user authentication, blog post management, like/comment system, user dashboard, and admin panel.

## 🚀 Features

- **User Authentication**: Secure signup, login, and logout with password hashing
- **Blog Management**: Create, edit, and delete blog posts
- **Social Features**: Like and comment on posts
- **User Dashboard**: Personal dashboard showing user's posts and activity statistics
- **Admin Panel**: Complete admin interface for managing users, posts, and comments
- **Responsive Design**: Modern, mobile-friendly UI built with pure CSS
- **Database Integration**: PostgreSQL with automatic table creation

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3 (no frameworks)
- **Authentication**: Flask sessions with password hashing
- **Database ORM**: psycopg2 for PostgreSQL connection

## 📋 Prerequisites

Before running this application, make sure you have:

1. **Python 3.7+** installed
2. **PostgreSQL** installed and running
3. **pgAdmin** (optional, for database management)

## 🗄️ Database Setup

1. **Create the database**:
   ```sql
   CREATE DATABASE blog_portal;
   ```

2. **Update database credentials** in `app.py` if needed:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'port': '5432',
       'database': 'blog_portal',
       'user': 'postgres',
       'password': '2006'  # Change this to your PostgreSQL password
   }
   ```

## 🚀 Installation & Setup

1. **Clone or download** the project files to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd miniblog
   ```

3. **Run the application** (automatically creates virtual environment):
   ```bash
   # Windows
   start.bat
   
   # Linux/Mac
   ./start.sh
   ```
   
   **OR manually:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run application
   python app.py
   ```

5. **Open your browser** and go to `http://localhost:5000`

## 👤 Default Admin Account

The application automatically creates a default admin user on first run:

- **Username**: `admin`
- **Email**: `admin@blog.com`
- **Password**: `admin123`
- **Role**: `admin`

**⚠️ Important**: Change the admin password after first login for security!

## 📁 Project Structure

```
miniblog/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── start.bat/.sh         # Startup scripts
├── .gitignore            # Git ignore file
│
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page with all posts
│   ├── login.html        # User login page
│   ├── signup.html       # User registration page
│   ├── dashboard.html    # User dashboard
│   ├── create_post.html  # Create new post form
│   ├── edit_post.html    # Edit existing post form
│   ├── view_post.html    # View individual post
│   └── admin_panel.html  # Admin management panel
│
└── static/
    └── css/
        └── style.css     # Main stylesheet
```

## 🗃️ Database Schema

The application automatically creates the following tables:

### Users Table
- `id` (SERIAL PRIMARY KEY)
- `username` (VARCHAR)
- `email` (VARCHAR UNIQUE)
- `password` (VARCHAR - hashed)
- `role` (VARCHAR - 'user' or 'admin')
- `created_at` (TIMESTAMP)

### Posts Table
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER - Foreign Key)
- `title` (VARCHAR)
- `content` (TEXT)
- `created_at` (TIMESTAMP)

### Likes Table
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER - Foreign Key)
- `post_id` (INTEGER - Foreign Key)
- `created_at` (TIMESTAMP)

### Comments Table
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER - Foreign Key)
- `post_id` (INTEGER - Foreign Key)
- `content` (TEXT)
- `created_at` (TIMESTAMP)

## 🎯 Usage Guide

### For Regular Users:
1. **Sign Up**: Create a new account with username, email, and password
2. **Login**: Access your account using email and password
3. **Create Posts**: Write and publish blog posts
4. **Interact**: Like and comment on other users' posts
5. **Dashboard**: View your posts and activity statistics
6. **Manage Posts**: Edit or delete your own posts

### For Admins:
1. **Admin Panel**: Access the admin panel from the navigation menu
2. **User Management**: View all users and delete accounts if needed
3. **Post Management**: View all posts and delete any post
4. **Comment Moderation**: View and delete comments
5. **Statistics**: Monitor overall platform activity

## 🔧 Configuration

### Database Connection
Update the `DB_CONFIG` dictionary in `app.py` to match your PostgreSQL setup:

```python
DB_CONFIG = {
    'host': 'localhost',        # Your PostgreSQL host
    'port': '5432',            # Your PostgreSQL port
    'database': 'blog_portal',  # Your database name
    'user': 'postgres',        # Your PostgreSQL username
    'password': '2006'         # Your PostgreSQL password
}
```

### Security Settings
For production deployment, make sure to:

1. Change the `secret_key` in `app.py`
2. Update the default admin password
3. Use environment variables for sensitive data
4. Enable HTTPS
5. Configure proper database permissions

## 🐛 Troubleshooting

### Common Issues:

1. **Database Connection Error**:
   - Ensure PostgreSQL is running
   - Check database credentials in `app.py`
   - Verify the `blog_portal` database exists

2. **Port Already in Use**:
   - Change the port in `app.run()` at the bottom of `app.py`
   - Or stop the process using port 5000

3. **Module Not Found**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check your Python environment

4. **Permission Errors**:
   - Ensure your PostgreSQL user has proper permissions
   - Check file permissions in the project directory

## 🚀 Deployment

For production deployment:

1. **Use a production WSGI server** (e.g., Gunicorn)
2. **Set up a reverse proxy** (e.g., Nginx)
3. **Use environment variables** for sensitive configuration
4. **Enable HTTPS** with SSL certificates
5. **Set up database backups**
6. **Configure logging**

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please create an issue in the project repository.

---

**Happy Blogging! 🎉**
