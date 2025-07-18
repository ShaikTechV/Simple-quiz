"""
DEBUG VERSION - Quiz Platform
Step by step debugging to fix issues
"""

from flask import Flask, request, jsonify
import json
import os
import random
import string
import psycopg2
from psycopg2.extras import RealDictCursor
import urllib.parse
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Database connection with better error handling
def get_db():
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ No DATABASE_URL found")
            return None
            
        url = urllib.parse.urlparse(database_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            cursor_factory=RealDictCursor
        )
        print("✅ Database connected successfully")
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return None

# Initialize database with better error handling
def init_db():
    print("🔧 Initializing database...")
    try:
        conn = get_db()
        if not conn:
            print("❌ Cannot initialize database - no connection")
            return False
            
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                access_code VARCHAR(10) PRIMARY KEY,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                questions TEXT,
                answers TEXT DEFAULT '{}',
                score INTEGER DEFAULT 0,
                total INTEGER DEFAULT 25,
                completed BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")
        return False

# Initialize on startup
db_initialized = init_db()

# Simple quiz questions
QUESTIONS = [
    {"id": 1, "q": "Which is not a capital item?", "options": ["Computer purchased", "Freight for machinery", "Employee compensation", "Family planning center"], "correct": 2},
    {"id": 2, "q": "Salary paid to Mohan debited to Mohan A/c is:", "options": ["Principle error", "Compensation error", "Omission error", "No error"], "correct": 0},
    {"id": 3, "q": "Assets = Liabilities + ?", "options": ["Equity", "Revenue", "Expenses", "Cash"], "correct": 0},
    {"id": 4, "q": "Double entry means:", "options": ["Two books", "Every debit has credit", "Two entries", "Two periods"], "correct": 1},
    {"id": 5, "q": "Current asset example:", "options": ["Building", "Machinery", "Inventory", "Land"], "correct": 2},
]

@app.route('/')
def home():
    print("🏠 Home page accessed")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quiz Platform</title>
        <style>
            body {{font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5;}}
            .container {{max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;}}
            .btn {{background: #007bff; color: white; padding: 15px 25px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; text-decoration: none; display: inline-block;}}
            .btn:hover {{background: #0056b3;}}
            .card {{border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; background: #f8f9fa;}}
            .success {{background: #d4edda; color: #155724; padding: 15px; margin: 20px 0; border-radius: 5px;}}
            .error {{background: #f8d7da; color: #721c24; padding: 15px; margin: 20px 0; border-radius: 5px;}}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Interview Assessment Platform</h1>
            
            <div class="success">
                ✅ Platform Status: {'Database Connected' if db_initialized else 'Database Error'}
            </div>
            
            <div class="card">
                <h3>Create Quiz Session</h3>
                <button class="btn" onclick="createQuiz()">Create New Quiz</button>
                <div id="result"></div>
                <div id="debug"></div>
            </div>
            
            <div class="card">
                <h3>Admin</h3>
                <a href="/admin" class="btn">View Dashboard</a>
                <a href="/test" class="btn" style="background: #28a745;">Test System</a>
                <a href="/debug" class="btn" style="background: #ffc107; color: black;">Debug Info</a>
            </div>
        </div>
        
        <script>
            console.log('🔧 JavaScript loaded');
            
            function createQuiz() {{
                console.log('🔄 Creating quiz...');
                document.getElementById('debug').innerHTML = '<p>Creating quiz...</p>';
                
                fetch('/create', {{method: 'POST'}})
                .then(response => {{
                    console.log('📡 Response status:', response.status);
                    if (!response.ok) {{
                        throw new Error('Network response was not ok: ' + response.status);
                    }}
                    return response.json();
                }})
                .then(data => {{
                    console.log('📊 Response data:', data);
                    if(data.success) {{
                        document.getElementById('result').innerHTML = 
                            '<div class="success"><h4>✅ Quiz Created Successfully!</h4>' +
                            '<p><strong>Access Code:</strong> ' + data.code + '</p>' +
                            '<p><strong>Quiz URL:</strong> <a href="/quiz/' + data.code + '" target="_blank">' + 
                            window.location.origin + '/quiz/' + data.code + '</a></p></div>';
                        document.getElementById('debug').innerHTML = '';
                    }} else {{
                        document.getElementById('result').innerHTML = 
                            '<div class="error">❌ Failed to create quiz: ' + (data.error || 'Unknown error') + '</div>';
                    }}
                }})
                .catch(error => {{
                    console.error('❌ Error:', error);
                    document.getElementById('result').innerHTML = 
                        '<div class="error">❌ Error creating quiz: ' + error.message + '</div>';
                    document.getElementById('debug').innerHTML = '<p>Error details: ' + error.toString() + '</p>';
                }});
            }}
            
            console.log('✅ JavaScript ready');
        </script>
    </body>
    </html>
    """

@app.route('/create', methods=['POST'])
def create_quiz():
    print("📝 Create quiz route accessed")
    try:
        if not db_initialized:
            print("❌ Database not initialized")
            return jsonify({"success": False, "error": "Database not available"})
        
        # Generate access code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        print(f"🔑 Generated access code: {code}")
        
        # Use subset of questions for testing
        questions = QUESTIONS.copy()
        print(f"📚 Using {len(questions)} questions")
        
        # Save to database
        conn = get_db()
        if not conn:
            print("❌ No database connection")
            return jsonify({"success": False, "error": "Database connection failed"})
        
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO quiz_sessions (access_code, questions, total) 
            VALUES (%s, %s, %s)
        """, (code, json.dumps(questions), len(questions)))
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Quiz session created: {code}")
        return jsonify({"success": True, "code": code})
        
    except Exception as e:
        print(f"❌ Error in create_quiz: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/admin')
def admin():
    print("👑 Admin route accessed")
    try:
        if not db_initialized:
            return "<h1>❌ Database Error</h1><p>Database not initialized</p><p><a href='/'>Home</a></p>"
        
        conn = get_db()
        if not conn:
            return "<h1>❌ Database Connection Failed</h1><p><a href='/'>Home</a></p>"
        
        cur = conn.cursor()
        
        # Simple query first
        try:
            cur.execute("SELECT COUNT(*) as total FROM quiz_sessions")
            total_count = cur.fetchone()['total']
            print(f"📊 Total sessions in database: {total_count}")
        except Exception as e:
            cur.close()
            conn.close()
            return f"<h1>❌ Database Query Error</h1><p>Error: {str(e)}</p><p><a href='/'>Home</a></p>"
        
        # Get active sessions
        try:
            cur.execute("""
                SELECT access_code, start_time, answers, completed
                FROM quiz_sessions 
                WHERE completed = FALSE 
                ORDER BY start_time DESC
                LIMIT 10
            """)
            active = cur.fetchall()
            print(f"📈 Active sessions found: {len(active)}")
        except Exception as e:
            cur.close()
            conn.close()
            return f"<h1>❌ Active Sessions Query Error</h1><p>Error: {str(e)}</p><p><a href='/'>Home</a></p>"
        
        # Get completed sessions
        try:
            cur.execute("""
                SELECT access_code, start_time, end_time, score, total, completed
                FROM quiz_sessions 
                WHERE completed = TRUE 
                ORDER BY start_time DESC 
                LIMIT 10
            """)
            completed = cur.fetchall()
            print(f"📉 Completed sessions found: {len(completed)}")
        except Exception as e:
            cur.close()
            conn.close()
            return f"<h1>❌ Completed Sessions Query Error</h1><p>Error: {str(e)}</p><p><a href='/'>Home</a></p>"
        
        cur.close()
        conn.close()
        
        # Build HTML response
        active_html = ""
        for session in active:
            answers_count = len(json.loads(session['answers'] or '{{}}'))
            active_html += f"""
            <tr>
                <td><strong>{session['access_code']}</strong></td>
                <td>{session['start_time'].strftime('%H:%M:%S')}</td>
                <td>{answers_count}/5</td>
                <td>Active</td>
            </tr>
            """
        
        completed_html = ""
        for session in completed:
            percentage = round((session['score'] / session['total']) * 100, 1) if session['total'] > 0 else 0
            completed_html += f"""
            <tr>
                <td><strong>{session['access_code']}</strong></td>
                <td>{session['start_time'].strftime('%Y-%m-%d %H:%M')}</td>
                <td>{session['score']}/{session['total']}</td>
                <td>{percentage}%</td>
                <td>Completed</td>
            </tr>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard</title>
            <style>
                body {{font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5;}}
                .container {{max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;}}
                table {{width: 100%; border-collapse: collapse; margin: 20px 0;}}
                th, td {{padding: 12px; text-align: left; border-bottom: 1px solid #ddd;}}
                th {{background: #f8f9fa; font-weight: bold;}}
                .btn {{background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; margin: 5px;}}
                .success {{background: #d4edda; color: #155724; padding: 15px; margin: 20px 0; border-radius: 5px;}}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✅ Admin Dashboard Loaded Successfully</div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                    <h1>Admin Dashboard</h1>
                    <div>
                        <button class="btn" onclick="location.reload()">Refresh</button>
                        <a href="/" class="btn">Home</a>
                        <a href="/test" class="btn">Test</a>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0;">
                    <div style="text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa;">
                        <div style="font-size: 36px; font-weight: bold; color: #007bff;">{len(active)}</div>
                        <div>Active Sessions</div>
                    </div>
                    <div style="text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa;">
                        <div style="font-size: 36px; font-weight: bold; color: #007bff;">{len(completed)}</div>
                        <div>Completed Sessions</div>
                    </div>
                    <div style="text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa;">
                        <div style="font-size: 36px; font-weight: bold; color: #007bff;">{total_count}</div>
                        <div>Total Sessions</div>
                    </div>
                </div>
                
                <h3>Active Sessions</h3>
                <table>
                    <tr><th>Access Code</th><th>Start Time</th><th>Questions Answered</th><th>Status</th></tr>
                    {active_html if active_html else '<tr><td colspan="4">No active sessions</td></tr>'}
                </table>
                
                <h3>Completed Sessions</h3>
                <table>
                    <tr><th>Access Code</th><th>Start Time</th><th>Score</th><th>Percentage</th><th>Status</th></tr>
                    {completed_html if completed_html else '<tr><td colspan="5">No completed sessions</td></tr>'}
                </table>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        print(f"❌ Unexpected error in admin: {str(e)}")
        return f"<h1>❌ Unexpected Error</h1><p>Error: {str(e)}</p><p><a href='/'>Home</a></p>"

@app.route('/test')
def test():
    print("🧪 Test route accessed")
    try:
        # Test database connection
        conn = get_db()
        if not conn:
            return "❌ Database connection failed"
        
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM quiz_sessions")
        count = cur.fetchone()['count']
        cur.close()
        conn.close()
        
        return f"""
        <h1>✅ System Test Results</h1>
        <p><strong>Database:</strong> Connected ✅</p>
        <p><strong>Sessions in DB:</strong> {count}</p>
        <p><strong>Questions loaded:</strong> {len(QUESTIONS)}</p>
        <p><strong>Time:</strong> {datetime.now()}</p>
        <p><a href="/">← Back to Home</a></p>
        """
        
    except Exception as e:
        return f"❌ Test failed: {str(e)}"

@app.route('/debug')
def debug():
    print("🔍 Debug route accessed")
    try:
        info = {
            "database_url_exists": bool(os.environ.get('DATABASE_URL')),
            "database_initialized": db_initialized,
            "questions_count": len(QUESTIONS),
            "flask_env": os.environ.get('FLASK_ENV', 'not set'),
            "port": os.environ.get('PORT', 'not set'),
        }
        
        html = "<h1>🔍 Debug Information</h1>"
        for key, value in info.items():
            status = "✅" if value else "❌"
            html += f"<p><strong>{key}:</strong> {value} {status}</p>"
        
        html += '<p><a href="/">← Back to Home</a></p>'
        return html
        
    except Exception as e:
        return f"❌ Debug failed: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting DEBUG version on port {port}")
    print(f"📊 Database initialized: {db_initialized}")
    print(f"📚 Questions loaded: {len(QUESTIONS)}")
    app.run(host='0.0.0.0', port=port, debug=False)
