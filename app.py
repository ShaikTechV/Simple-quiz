"""
SIMPLE QUIZ PLATFORM - FINAL VERSION
Works on Heroku with PostgreSQL
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

# Database connection
def get_db():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        url = urllib.parse.urlparse(database_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            cursor_factory=RealDictCursor
        )
        return conn
    return None

# Initialize database
def init_db():
    conn = get_db()
    if conn:
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

init_db()

# Quiz questions
QUESTIONS = [
    {"id": 1, "q": "Which is not a capital item?", "options": ["Computer purchased", "Freight for machinery", "Employee compensation", "Family planning center"], "correct": 2},
    {"id": 2, "q": "Salary paid to Mohan debited to Mohan A/c is:", "options": ["Principle error", "Compensation error", "Omission error", "No error"], "correct": 0},
    {"id": 3, "q": "Assets = Liabilities + ?", "options": ["Equity", "Revenue", "Expenses", "Cash"], "correct": 0},
    {"id": 4, "q": "Double entry means:", "options": ["Two books", "Every debit has credit", "Two entries", "Two periods"], "correct": 1},
    {"id": 5, "q": "Current asset example:", "options": ["Building", "Machinery", "Inventory", "Land"], "correct": 2},
    {"id": 6, "q": "Drawings decrease assets and decrease liability. True/False?", "options": ["True", "False"], "correct": 1},
    {"id": 7, "q": "Cash discount is never recorded. True/False?", "options": ["True", "False"], "correct": 1},
    {"id": 8, "q": "Receipts and payments is like cash book. True/False?", "options": ["True", "False"], "correct": 0},
    {"id": 9, "q": "Which is a solvency ratio?", "options": ["Liquidity Ratio", "Operating Ratio", "Capital Gearing Ratio", "Net Profit Ratio"], "correct": 2},
    {"id": 10, "q": "Future value of Rs.200000 at 12% for 10 years?", "options": ["Rs.621200", "Rs.500000", "Rs.642200", "Rs.810500"], "correct": 0},
    {"id": 11, "q": "ARR when PAT=50L, Investment=500L?", "options": ["5%", "20%", "10%", "2%"], "correct": 2},
    {"id": 12, "q": "Advances to Govt shown as:", "options": ["Current assets", "Fixed assets", "Liability", "Capital"], "correct": 0},
    {"id": 13, "q": "Salaries due in March appear:", "options": ["Receipt side", "Payment side", "Contra entry", "Nowhere in cash book"], "correct": 3},
    {"id": 14, "q": "Opening stock 10000, Purchases 200000, Closing 40000, Sales 300000. Gross profit?", "options": ["50000", "20000", "36000", "60000"], "correct": 0},
    {"id": 15, "q": "Operating profit calculation: Sales 1000000, Opening 100000, Purchases 650000, Closing 150000, Rent 45000, Salaries 90000", "options": ["465000", "550000", "430000", "475000"], "correct": 0},
    {"id": 16, "q": "Income & Expenditure: Subscription received 5000, outstanding 2500", "options": ["2500", "2000", "500", "3000"], "correct": 0},
    {"id": 17, "q": "Proprietor A/c: Opening 50000, Profit 450000, Drawings 100000. Closing balance?", "options": ["500000", "400000", "600000", "700000"], "correct": 0},
    {"id": 18, "q": "Fire loss: Goods 18800, Insurance admits 15000. Loss by fire A/c:", "options": ["Debit 18800", "Debit 3800", "Credit 18800", "Credit 3800"], "correct": 1},
    {"id": 19, "q": "Correct equation:", "options": ["Assets + Liabilities = Equity", "Assets - Liabilities = Equity", "Equity + Assets = Liability", "None"], "correct": 1},
    {"id": 20, "q": "Health Club: 1000 members, 1000 each, 2L advance, 1L arrears. Credit to I&E:", "options": ["8L", "6L", "10L", "12L"], "correct": 1},
    {"id": 21, "q": "Branch: Goods sent 500000, Cash received 200000, Expenses 100000, Closing stock 100000. Branch adjustment:", "options": ["300000", "200000", "100000", "400000"], "correct": 0},
    {"id": 22, "q": "Subscription: Received 10L, Due previous 1L, Due current 3L, Advance 1L. Credit:", "options": ["10L", "12L", "14L", "11L"], "correct": 3},
    {"id": 23, "q": "ABC Club: Current 5L, Outstanding begin 2L, end 1L, Advance begin 1L, end 2L. Credit:", "options": ["4L", "5L", "3L", "9L"], "correct": 0},
    {"id": 24, "q": "Software expenses for software business is capital if for sale. True/False?", "options": ["True", "False"], "correct": 1},
    {"id": 25, "q": "Business transactions recording is compulsory. True/False?", "options": ["True", "False"], "correct": 0}
]

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Quiz Platform</title>
    <style>body{font-family:Arial;margin:40px;} .btn{background:#007bff;color:white;padding:15px 25px;border:none;border-radius:5px;cursor:pointer;margin:10px;} .card{border:1px solid #ddd;padding:20px;margin:20px 0;border-radius:8px;}</style>
    </head>
    <body>
        <h1>Interview Assessment Platform</h1>
        <div class="card">
            <h3>Create Quiz Session</h3>
            <button class="btn" onclick="createQuiz()">Create New Quiz</button>
            <div id="result"></div>
        </div>
        <div class="card">
            <h3>Admin</h3>
            <a href="/admin" class="btn">View Dashboard</a>
        </div>
        
        <script>
        function createQuiz() {
            fetch('/create', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    document.getElementById('result').innerHTML = 
                        '<h4>Quiz Created!</h4><p><strong>Access Code:</strong> ' + data.code + 
                        '</p><p><strong>URL:</strong> <a href="/quiz/' + data.code + '" target="_blank">' + 
                        window.location.origin + '/quiz/' + data.code + '</a></p>';
                }
            });
        }
        </script>
    </body>
    </html>
    """

@app.route('/create', methods=['POST'])
def create_quiz():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    questions = random.sample(QUESTIONS, 25)  # All 25 questions
    
    conn = get_db()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO quiz_sessions (access_code, questions, total) 
            VALUES (%s, %s, %s)
        """, (code, json.dumps(questions), len(questions)))
        conn.commit()
        cur.close()
        conn.close()
    
    return jsonify({"success": True, "code": code})

@app.route('/quiz/<code>')
def quiz(code):
    conn = get_db()
    if not conn:
        return "Database error", 500
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM quiz_sessions WHERE access_code = %s", (code,))
    session = cur.fetchone()
    cur.close()
    conn.close()
    
    if not session:
        return "Invalid access code", 404
    
    if session['completed']:
        return "Quiz already completed", 410
    
    questions = json.loads(session['questions'])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Quiz - {code}</title>
    <style>
    body{{font-family:Arial;margin:20px;background:#f5f5f5;}}
    .container{{max-width:800px;margin:0 auto;background:white;padding:30px;border-radius:10px;}}
    .timer{{position:fixed;top:20px;right:20px;background:#dc3545;color:white;padding:15px;border-radius:8px;font-weight:bold;}}
    .question{{margin:20px 0;padding:20px;border:1px solid #ddd;border-radius:8px;background:#f8f9fa;}}
    .option{{margin:10px 0;padding:12px;border:2px solid #ddd;border-radius:5px;cursor:pointer;}}
    .option:hover{{border-color:#007bff;}}
    .option.selected{{background:#007bff;color:white;}}
    .submit{{background:#28a745;color:white;padding:15px 30px;border:none;border-radius:5px;font-size:16px;cursor:pointer;margin-top:30px;}}
    </style>
    </head>
    <body>
        <div class="timer" id="timer">45:00</div>
        <div class="container">
            <h1>Accounting & Finance Assessment</h1>
            <p><strong>Access Code:</strong> {code} | <strong>Questions:</strong> {len(questions)} | <strong>Time:</strong> 45 minutes</p>
            
            <div id="questions">
                {"".join([f'''
                <div class="question">
                    <h3>Q{i+1}: {q["q"]}</h3>
                    <div class="options">
                        {"".join([f'<div class="option" onclick="selectAnswer({q["id"]}, {j})" id="opt-{q["id"]}-{j}">{opt}</div>' for j, opt in enumerate(q["options"])])}
                    </div>
                </div>
                ''' for i, q in enumerate(questions)])}
            </div>
            
            <button class="submit" onclick="submitQuiz()">Submit Quiz</button>
        </div>
        
        <script>
        const answers = {{}};
        let timeLeft = 2700;
        
        function updateTimer() {{
            const mins = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;
            document.getElementById('timer').textContent = 'Time: ' + mins + ':' + (secs < 10 ? '0' : '') + secs;
            if(timeLeft <= 0) submitQuiz();
            timeLeft--;
        }}
        setInterval(updateTimer, 1000);
        
        function selectAnswer(qId, optIdx) {{
            // Clear previous selection
            document.querySelectorAll('[id^="opt-' + qId + '-"]').forEach(el => el.classList.remove('selected'));
            // Select new option
            document.getElementById('opt-' + qId + '-' + optIdx).classList.add('selected');
            answers[qId] = optIdx;
            
            // Save to server
            fetch('/save', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{code: '{code}', qId: qId, answer: optIdx}})
            }});
        }}
        
        function submitQuiz() {{
            fetch('/submit', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{code: '{code}'}})
            }})
            .then(r => r.json())
            .then(data => {{
                alert('Quiz completed! Score: ' + data.score + '/' + data.total + ' (' + data.percentage + '%)');
                window.location.href = '/';
            }});
        }}
        </script>
    </body>
    </html>
    """

@app.route('/save', methods=['POST'])
def save_answer():
    data = request.json
    code = data['code']
    qId = data['qId']
    answer = data['answer']
    
    conn = get_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT answers FROM quiz_sessions WHERE access_code = %s", (code,))
        result = cur.fetchone()
        
        if result:
            answers = json.loads(result['answers'] or '{}')
            answers[str(qId)] = answer
            
            cur.execute("UPDATE quiz_sessions SET answers = %s WHERE access_code = %s", 
                       (json.dumps(answers), code))
            conn.commit()
        
        cur.close()
        conn.close()
    
    return jsonify({"success": True})

@app.route('/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    code = data['code']
    
    conn = get_db()
    if not conn:
        return jsonify({"success": False})
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM quiz_sessions WHERE access_code = %s", (code,))
    session = cur.fetchone()
    
    if not session:
        cur.close()
        conn.close()
        return jsonify({"success": False})
    
    questions = json.loads(session['questions'])
    answers = json.loads(session['answers'] or '{}')
    
    # Calculate score
    score = 0
    for q in questions:
        if str(q['id']) in answers and answers[str(q['id'])] == q['correct']:
            score += 1
    
    total = len(questions)
    percentage = round((score / total) * 100, 1)
    
    # Mark completed
    cur.execute("""
        UPDATE quiz_sessions 
        SET completed = TRUE, end_time = CURRENT_TIMESTAMP, score = %s 
        WHERE access_code = %s
    """, (score, code))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"success": True, "score": score, "total": total, "percentage": percentage})

@app.route('/admin')
def admin():
    conn = get_db()
    if not conn:
        return "Database error", 500
    
    cur = conn.cursor()
    
    # Get active sessions
    cur.execute("""
        SELECT access_code, start_time, answers 
        FROM quiz_sessions 
        WHERE completed = FALSE 
        ORDER BY start_time DESC
    """)
    active = cur.fetchall()
    
    # Get completed sessions  
    cur.execute("""
        SELECT access_code, start_time, end_time, score, total, 
               EXTRACT(EPOCH FROM (end_time - start_time))/60 as duration_min
        FROM quiz_sessions 
        WHERE completed = TRUE 
        ORDER BY end_time DESC 
        LIMIT 20
    """)
    completed = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Process active sessions
    active_html = ""
    for session in active:
        answers_count = len(json.loads(session['answers'] or '{}'))
        elapsed = (datetime.now() - session['start_time']).total_seconds()
        remaining = max(0, 2700 - elapsed)
        remaining_min = int(remaining // 60)
        
        active_html += f"""
        <tr>
            <td><strong>{session['access_code']}</strong></td>
            <td>{session['start_time'].strftime('%H:%M:%S')}</td>
            <td>{remaining_min}:{int(remaining % 60):02d}</td>
            <td>{answers_count}/25</td>
            <td><span style="color:#28a745;font-weight:bold;">Active</span></td>
        </tr>
        """
    
    # Process completed sessions
    completed_html = ""
    for session in completed:
        percentage = round((session['score'] / session['total']) * 100, 1) if session['total'] > 0 else 0
        duration = f"{int(session['duration_min'] or 0)} min"
        
        color = "#28a745" if percentage >= 70 else "#ffc107" if percentage >= 50 else "#dc3545"
        
        completed_html += f"""
        <tr>
            <td><strong>{session['access_code']}</strong></td>
            <td>{session['start_time'].strftime('%Y-%m-%d %H:%M')}</td>
            <td>{session['end_time'].strftime('%Y-%m-%d %H:%M') if session['end_time'] else 'N/A'}</td>
            <td>{duration}</td>
            <td>{session['score']}/{session['total']}</td>
            <td><span style="color:{color};font-weight:bold;">{percentage}%</span></td>
            <td><span style="color:#6c757d;font-weight:bold;">Completed</span></td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Admin Dashboard</title>
    <style>
    body{{font-family:Arial;margin:20px;background:#f5f5f5;}}
    .container{{max-width:1200px;margin:0 auto;background:white;padding:30px;border-radius:10px;}}
    table{{width:100%;border-collapse:collapse;margin:20px 0;}}
    th,td{{padding:12px;text-align:left;border-bottom:1px solid #ddd;}}
    th{{background:#f8f9fa;font-weight:bold;}}
    .btn{{background:#007bff;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;text-decoration:none;}}
    .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:30px 0;}}
    .stat{{text-align:center;padding:20px;border:1px solid #ddd;border-radius:8px;background:#f8f9fa;}}
    .stat-num{{font-size:36px;font-weight:bold;color:#007bff;}}
    </style>
    </head>
    <body>
        <div class="container">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:30px;">
                <h1>Admin Dashboard</h1>
                <div>
                    <button class="btn" onclick="location.reload()">Refresh</button>
                    <a href="/" class="btn" style="margin-left:10px;">Home</a>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-num">{len(active)}</div>
                    <div>Active Sessions</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{len(completed)}</div>
                    <div>Completed Sessions</div>
                </div>
                <div class="stat">
                    <div class="stat-num">25</div>
                    <div>Total Questions</div>
                </div>
            </div>
            
            <h3>Active Quiz Sessions</h3>
            <table>
                <tr><th>Access Code</th><th>Start Time</th><th>Time Remaining</th><th>Questions Answered</th><th>Status</th></tr>
                {active_html if active_html else '<tr><td colspan="5">No active sessions</td></tr>'}
            </table>
            
            <h3>Completed Quiz Results</h3>
            <table>
                <tr><th>Access Code</th><th>Start Time</th><th>End Time</th><th>Duration</th><th>Score</th><th>Percentage</th><th>Status</th></tr>
                {completed_html if completed_html else '<tr><td colspan="7">No completed sessions</td></tr>'}
            </table>
        </div>
        
        <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """

@app.route('/test')
def test():
    conn = get_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM quiz_sessions")
        count = cur.fetchone()['count']
        cur.close()
        conn.close()
        return f"✅ Working! Sessions: {count}, Questions: {len(QUESTIONS)}, Time: {datetime.now()}"
    return "❌ Database connection failed"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
