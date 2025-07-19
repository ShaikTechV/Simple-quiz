"""
Simple Quiz Platform - Direct Quiz Access with Response Recording
"""

from flask import Flask, render_template, request, jsonify
import json
import time
from datetime import datetime
import secrets
import os
import random
import string

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage for quiz responses
quiz_responses = []

# Quiz data - All 25 questions
QUIZ_DATA = {
    "title": "Accounting & Finance Assessment",
    "description": "Professional interview evaluation",
    "questions": [
        {
            "id": 1,
            "question": "Out of following which is not capital item?",
            "options": [
                "(a) Computer set purchased",
                "(b) Freight charges incurred for purchase of machinery", 
                "(c) Compensation paid to employees who are retrenched",
                "(d) Installed family planning center"
            ],
            "correct": 2
        },
        {
            "id": 2,
            "question": "Salary paid to Mohan is debited to Mohan A/c. This error is",
            "options": [
                "(a) Principle error",
                "(b) Compensation error", 
                "(c) Omission error",
                "(d) No error at all"
            ],
            "correct": 0
        },
        {
            "id": 3,
            "question": "XYZ Co. failed to agree and the difference was put into suspense account. Pass the rectifying entry:",
            "options": [
                "(a) Dr. Suspense A/c. 3000, Cr. Discount received A/c. 2000, Cr. Discount allowed a/c. 1000",
                "(b) Dr. Discount received A/c. 2000, Dr. Discount allowed a/c. 1000, Cr. Suspense A/c. 3000",
                "(c) No entry is required", 
                "(d) Any entry a or b"
            ],
            "correct": 0
        },
        {
            "id": 4,
            "question": "Calculate the operating profit: Sales Rs. 10,00,000, Opening stock Rs. 1,00,000, Purchases Rs. 6,50,000, Closing stock Rs. 1,50,000, Office rent Rs. 45,000, Salaries Rs. 90,000",
            "options": [
                "(a) Rs. 4,65,000",
                "(b) Rs. 5,50,000",
                "(c) Rs. 4,30,000",
                "(d) Rs. 4,75,000"
            ],
            "correct": 0
        },
        {
            "id": 5,
            "question": "Salaries due for the month of March will appear",
            "options": [
                "(a) On the receipt side of the cash book",
                "(b) On the payment side of the cash book",
                "(c) As a contra entry",
                "(d) Nowhere in cash book"
            ],
            "correct": 3
        },
        {
            "id": 6,
            "question": "From the following information, determine amounts to be transferred to Income & Expenditure A/c: Subscription received Rs. 5,000, Subscription outstanding Rs. 2,500",
            "options": [
                "(a) Rs. 7,500",
                "(b) Rs. 2,500", 
                "(c) Rs. 5,000",
                "(d) Rs. 2,000"
            ],
            "correct": 0
        },
        {
            "id": 7,
            "question": "Opening balance: Proprietor's A/c. Rs. 50,000, Current year profit Rs. 4,50,000, Drawings Rs. 1,00,000. Calculate closing balance of Proprietor's A/c.",
            "options": [
                "(a) Rs. 4,00,000",
                "(b) Rs. 5,00,000",
                "(c) Rs. 6,00,000", 
                "(d) Rs. 7,00,000"
            ],
            "correct": 0
        },
        {
            "id": 8,
            "question": "Goods worth Rs.18,800 are destroyed by fire and the insurance company admits the claim for Rs.15,000. Loss by fire account will be",
            "options": [
                "(a) debited by Rs.18,800",
                "(b) debited by Rs.3,800",
                "(c) credited by Rs.18,800",
                "(d) credited by Rs.3,800"
            ],
            "correct": 1
        },
        {
            "id": 9,
            "question": "Which one is correct?",
            "options": [
                "(a) Assets + Liabilities = Owner's equity",
                "(b) Assets – Liabilities = Owner's equity",
                "(c) Owner's equity + Assets = Liability",
                "(d) None of the above"
            ],
            "correct": 1
        },
        {
            "id": 10,
            "question": "Advances given to Govt. Authority is shown as",
            "options": [
                "(a) Current assets",
                "(b) Fixed assets",
                "(c) Liability", 
                "(d) Capital"
            ],
            "correct": 0
        },
        {
            "id": 11,
            "question": "Health Club has 1,000 members. Annual fees for each member Rs.1,000. Rs.2 L received in advance, Rs.1 L in arrears. Amount to be credited to Income & Expenditure A/c:",
            "options": [
                "(a) Rs.8 L",
                "(b) Rs.9 L",
                "(c) Rs.10 L",
                "(d) Rs.12 L"
            ],
            "correct": 1
        },
        {
            "id": 12,
            "question": "When sales Rs.300000, Purchase Rs.200000, Opening stock Rs.10000, Closing stock Rs.40000, what is gross profit?",
            "options": [
                "(a) Rs. 130,000",
                "(b) Rs. 100,000",
                "(c) Rs. 170,000",
                "(d) Rs. 60,000"
            ],
            "correct": 0
        },
        {
            "id": 13,
            "question": "From the information, Vimal Ltd received from its branch: Goods sent to branch Rs. 5,00,000, Cash received from branch Rs. 2,00,000, Expenses of branch Rs. 1,00,000, Closing stock at branch Rs. 1,00,000. Branch adjustment account will show:",
            "options": [
                "(a) Rs. 2,00,000",
                "(b) Rs. 3,00,000", 
                "(c) Rs. 1,00,000",
                "(d) Rs. 4,00,000"
            ],
            "correct": 0
        },
        {
            "id": 14,
            "question": "What amount will be credited in income expenditure account for subscription: Subscription received Rs.10 L, Subscription due for previous year Rs.1 L, Subscription due for current year Rs.3 L, Subscription received in advance Rs.1 L",
            "options": [
                "(a) Rs. 12 L",
                "(b) Rs. 13 L",
                "(c) Rs. 14 L",
                "(d) Rs. 11 L"
            ],
            "correct": 0
        },
        {
            "id": 15,
            "question": "Following information provided by ABC Club: Subscription received current year Rs.5 L, Subscription outstanding beginning Rs.2 L, Subscription outstanding end Rs.1 L, Subscription received in advance beginning Rs.1 L, Subscription received in advance end Rs.2 L. Amount to be credited:",
            "options": [
                "(a) Rs. 4 L",
                "(b) Rs. 5 L",
                "(c) Rs. 3 L", 
                "(d) Rs. 9 L"
            ],
            "correct": 0
        },
        {
            "id": 16,
            "question": "Drawing decrease the assets and decrease the liability. Evaluate this statement as True or False.",
            "options": ["True", "False"],
            "correct": 1
        },
        {
            "id": 17,
            "question": "A, B, C started joint venture. A brought rs.10000, B Rs.20000, C Rs.30000 and opened joint bank account. Rs.10000 will be credited in joint bank a/c. on the name of A. Evaluate this statement as True or False.",
            "options": ["True", "False"],
            "correct": 0
        },
        {
            "id": 18,
            "question": "It is true receipts and payment is like a cash book. Evaluate this statement as True or False.",
            "options": ["True", "False"],
            "correct": 0
        },
        {
            "id": 19,
            "question": "Cash discount is never recorded in the books of accounts. Evaluate this statement as True or False.",
            "options": ["True", "False"],
            "correct": 1
        },
        {
            "id": 20,
            "question": "The software development expenses for a company engaging in software business is capital expenses if it is for sale. Evaluate this statement as True or False.",
            "options": ["True", "False"],
            "correct": 1
        },
        {
            "id": 21,
            "question": "It is not compulsory to record all the business transaction in the books of accounts. Evaluate this statement as True or False.",
            "options": ["True", "False"],
            "correct": 1
        },
        {
            "id": 22,
            "question": "If person invest Rs.2,00,000 in our investment which pays 12% compounded annually. What will be the future value after 10 years?",
            "options": [
                "(a) Rs. 6,21,200",
                "(b) Rs. 5,00,000",
                "(c) Rs. 6,42,200",
                "(d) Rs. 8,10,500"
            ],
            "correct": 0
        },
        {
            "id": 23,
            "question": "PAT of the project is Rs.50 Lac, initial investment is Rs.500 Lac. What is the accounting rate of return (ARR)?",
            "options": [
                "(a) 5%",
                "(b) 20%",
                "(c) 10%",
                "(d) 2%"
            ],
            "correct": 2
        },
        {
            "id": 24,
            "question": "Which of the following is a solvency ratio?",
            "options": [
                "(a) Liquidity Ratio",
                "(b) Operating Ratio",
                "(c) Capital Gearing Ratio",
                "(d) Net Profit Ratio"
            ],
            "correct": 2
        },
        {
            "id": 25,
            "question": "Based on the following Balance Sheet Data, calculate ALL THREE ratios:\n\n• Equity Share: Rs. 500,000\n• Pref. Shares: Rs. 200,000\n• General Reserve: Rs. 300,000\n• Secured Loan: Rs. 500,000\n• Creditors: Rs. 500,000\n• Total Assets: Rs. 2,000,000\n\ni) What is the Proprietary Ratio? (Enter as decimal, e.g., 0.5)\nii) What is the Debt Equity Ratio? (Enter as decimal, e.g., 1.0)\niii) What is the Capital Gearing Ratio? (Enter as decimal, e.g., 0.5)",
            "type": "text_input",
            "correct_answers": [
                "proprietary: 0.5, debt equity: 1.0, capital gearing: 0.5",
                "0.5, 1.0, 0.5",
                "0.5 1.0 0.5",
                "proprietary 0.5 debt equity 1.0 capital gearing 0.5",
                "i) 0.5 ii) 1.0 iii) 0.5"
            ],
            "explanation": "Proprietary Ratio = Owner's Equity / Total Assets = (500,000 + 200,000 + 300,000) / 2,000,000 = 0.5\nDebt Equity Ratio = Total Debt / Owner's Equity = (500,000 + 500,000) / 1,000,000 = 1.0\nCapital Gearing Ratio = Fixed Interest Securities / Owner's Equity = 500,000 / 1,000,000 = 0.5"
        }
    ]
}

@app.route('/')
def home():
    return render_template('simple_quiz.html', quiz_data=QUIZ_DATA)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        data = request.json
        answers = data.get('answers', {})
        candidate_name = data.get('candidate_name', 'Anonymous')
        time_forced = data.get('time_forced', False)
        focus_warnings = data.get('focus_warnings', 0)
        warnings_shown = data.get('warnings_shown', 0)
        time_elapsed = data.get('time_elapsed', 0)
        
        # Calculate score
        score = 0
        total = len(QUIZ_DATA['questions'])
        detailed_results = []
        
        for question in QUIZ_DATA['questions']:
            question_id = str(question['id'])
            user_answer = answers.get(question_id, -1)
            
            if question.get('type') == 'text_input':
                # Handle text input
                correct_answers = question.get('correct_answers', [])
                is_correct = False
                if user_answer:
                    user_answer_clean = str(user_answer).strip().lower()
                    
                    # For Question 25 (multi-part), check if it contains the key numbers
                    if question['id'] == 25:
                        # Expected answers: Proprietary=0.5, Debt Equity=0.5, Capital Gearing=0.875
                        answer_lower = user_answer_clean.replace('%', '').replace(',', ' ').replace(':', ' ')
                        
                        # Simple approach: look for the key values we expect
                        # Should contain 0.5 (twice) and 0.875 (once)
                        has_half = ('0.5' in answer_lower or '.5' in answer_lower or '50' in answer_lower)
                        has_capital = ('0.875' in answer_lower or '87.5' in answer_lower or '.875' in answer_lower)
                        
                        # Accept if they have both key values mentioned
                        # (being lenient since the exact format may vary)
                        if has_half and has_capital:
                            is_correct = True
                    else:
                        # Regular text answer checking
                        for correct in correct_answers:
                            if user_answer_clean == str(correct).strip().lower():
                                is_correct = True
                                break
                
                if is_correct:
                    score += 1
                    
                detailed_results.append({
                    'question_id': question['id'],
                    'question': question['question'],
                    'user_answer': user_answer,
                    'correct_answers': correct_answers,
                    'is_correct': is_correct,
                    'explanation': question.get('explanation', '')
                })
            else:
                # Handle multiple choice
                is_correct = user_answer == question['correct']
                if is_correct:
                    score += 1
                
                user_answer_text = "Not answered"
                correct_answer_text = "N/A"
                
                if user_answer >= 0 and user_answer < len(question['options']):
                    user_answer_text = question['options'][user_answer]
                
                if question['correct'] >= 0 and question['correct'] < len(question['options']):
                    correct_answer_text = question['options'][question['correct']]
                
                detailed_results.append({
                    'question_id': question['id'],
                    'question': question['question'],
                    'options': question['options'],
                    'user_answer': user_answer,
                    'user_answer_text': user_answer_text,
                    'correct_answer': question['correct'],
                    'correct_answer_text': correct_answer_text,
                    'is_correct': is_correct
                })
        
        # Store response with anti-cheat metrics
        response_data = {
            'submission_id': len(quiz_responses) + 1,
            'candidate_name': candidate_name,
            'submission_time': datetime.now().isoformat(),
            'score': score,
            'total': total,
            'percentage': round((score/total)*100, 1),
            'answers': answers,
            'detailed_results': detailed_results,
            'time_forced': time_forced,
            'time_elapsed_seconds': time_elapsed,
            'time_elapsed_minutes': round(time_elapsed / 60, 1),
            'focus_warnings': focus_warnings,  # Total blur events
            'warnings_shown': warnings_shown,  # Actual warnings shown
            'questions_answered': len([a for a in answers.values() if a != -1 and a != ""])
        }
        
        quiz_responses.append(response_data)
        
        submission_type = "TIME EXPIRED" if time_forced else "MANUAL"
        focus_note = f" | Focus Warnings: {warnings_shown}/{focus_warnings}" if focus_warnings > 0 else ""
        print(f"✅ QUIZ SUBMITTED ({submission_type}): {candidate_name} - Score: {score}/{total} - Time: {round(time_elapsed/60, 1)}min{focus_note}")
        
        return jsonify({
            'success': True,
            'score': score,
            'total': total,
            'percentage': round((score/total)*100, 1),
            'submission_id': response_data['submission_id']
        })
        
    except Exception as e:
        print(f"❌ ERROR submitting quiz: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin')
def admin():
    """Protected admin page to review all quiz responses"""
    # Simple protection - check for admin password in URL or session
    admin_key = request.args.get('key')
    if admin_key != 'admin123':  # Change this to your preferred password
        return '''
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h2>🔒 Admin Access Required</h2>
        <p>This page is for administrators only.</p>
        <form method="GET">
            <input type="password" name="key" placeholder="Enter admin password" style="padding: 10px; font-size: 16px;">
            <button type="submit" style="padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 5px;">Access Admin</button>
        </form>
        <p><a href="/">← Back to Quiz</a></p>
        </body></html>
        '''
    
    return render_template('admin_simple.html', responses=quiz_responses)

@app.route('/response/<int:submission_id>')
def view_response(submission_id):
    """Protected view detailed response for a specific submission"""
    # Simple protection - check for admin password
    admin_key = request.args.get('key')
    if admin_key != 'admin123':  # Change this to your preferred password
        return '''
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h2>🔒 Admin Access Required</h2>
        <p>This page is for administrators only.</p>
        <form method="GET">
            <input type="password" name="key" placeholder="Enter admin password" style="padding: 10px; font-size: 16px;">
            <button type="submit" style="padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 5px;">Access Details</button>
        </form>
        <p><a href="/">← Back to Quiz</a></p>
        </body></html>
        '''
    
    response = None
    for r in quiz_responses:
        if r['submission_id'] == submission_id:
            response = r
            break
    
    if not response:
        return "Response not found", 404
    
    return render_template('response_detail.html', response=response)

@app.route('/test')
def test():
    return f"✅ Quiz app working! Responses stored: {len(quiz_responses)} | Questions: {len(QUIZ_DATA['questions'])}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
