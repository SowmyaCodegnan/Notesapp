from flask import Flask,render_template,redirect,url_for,request,session
import bcrypt
from database import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from mail import send_email

app = Flask(__name__) 
app.secret_key='notes@22'
s = URLSafeTimedSerializer(app.secret_key)


@app.route('/') 
def home():
    return redirect("login")

@app.route('/login',methods=["GET","POST"])
def login():
    info = request.args.get('info')
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")

        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE email=%s", (email,))        
        user = cursor.fetchone()

        password_check = bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8'))

        if user and password_check:
            session['uname'] = user[1]
            session['user_id'] = user[0]
            return redirect(url_for("dashboard"))
            
        return redirect(url_for("login",info="Invalid login"))
        
    return render_template("login.html",info=info)


@app.route('/register',methods=["GET","POST"])
def register():
    info = request.args.get('info')
    if request.method=='POST':
        username=request.form.get("uname")
        email=request.form.get("email")
        password=request.form.get("password")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), 
                                        bcrypt.gensalt()).decode('utf-8')


        cursor = db.cursor()
        cursor.execute("SELECT email FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user:
            return redirect(url_for('register', info='Email already registered'))

        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password))
        db.commit()
        return redirect(url_for('login',info="Registration Successful"))
         
    return render_template("register.html",info=info)


@app.route('/forgotpassword',methods=["GET","POST"])
def forgotpassword():
    info = request.args.get('info')
    if request.method=='POST':
        email=request.form.get("email")
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user:
            session['email']=email
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('resetpassword', token=token, _external=True)
            send_email(email,'Password Reset Request',
                       f'Click the link to reset your password: {reset_url}\n\nThis link will expire in 1 hour.')

            return redirect(url_for('forgotpassword', info="Link sent to your email, Please check"))        
        return redirect(url_for('forgotpassword',info='Email is not registered'))   
    return render_template('forgotpassword.html',info=info) 

@app.route('/resetpassword/<token>', methods=['GET', 'POST'])
def resetpassword(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  
    except SignatureExpired:
        return redirect(url_for('forgotpassword', 
                                info="Token expired. Request a new link."))

    info = request.args.get('info')
    if request.method == 'POST':
        newpassword=request.form.get("newpassword")
        confirmpassword=request.form.get('confirmpassword')
        if newpassword == confirmpassword:
            email = session.get('email')
            hashed_password = bcrypt.hashpw(newpassword.encode('utf-8'), 
                                            bcrypt.gensalt()).decode('utf-8')

            if email:
                cursor = db.cursor()
                cursor.execute("UPDATE users SET password=%s WHERE email=%s", 
                               (hashed_password, email))
                db.commit()
                session.pop('email', None)
                return redirect(url_for('login',info="Reset password is successful"))
       
        return redirect(url_for('resetpassword', info="Passwords do not match"))
    
    return render_template('resetpassword.html',info=info)


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notes WHERE user_id = %s ORDER BY created_at DESC", 
                       (user_id,))
        notes = cursor.fetchall()
        cursor.close()
        return render_template('dashboard.html', notes=notes)
    return redirect(url_for('login'))

@app.route('/createnote', methods=['POST'])
def create_note():
    if 'user_id' in session:
        content = request.form.get('note')
        user_id = session['user_id']
        cursor = db.cursor()
        cursor.execute("INSERT INTO notes (user_id, content) VALUES (%s, %s)", (user_id, content))
        db.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/deletenote/<int:note_id>')
def delete_note(note_id):
    if 'user_id' in session:
        cursor = db.cursor()
        cursor.execute("DELETE FROM notes WHERE id=%s AND user_id=%s", 
                       (note_id, session['user_id']))
        db.commit()
    return redirect(url_for('dashboard'))


@app.route('/editnote/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' in session: 
        cursor = db.cursor(dictionary=True)
        if request.method == 'POST':
            new_content = request.form.get('content')
            cursor.execute("UPDATE notes SET content=%s WHERE id=%s AND user_id=%s", 
                       (new_content, note_id, session['user_id']))
            db.commit()
            return redirect(url_for('dashboard'))

        cursor.execute("SELECT * FROM notes WHERE id=%s AND user_id=%s", 
                       (note_id, session['user_id']))
        note = cursor.fetchone()
        cursor.close()
        if note:
            return render_template('editnote.html', note=note)

    return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) 