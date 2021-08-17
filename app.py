import os

from flask import *
from flask_mail import *
from random import *
from PIL import Image,ImageDraw,ImageFont
from datetime import date
import mysql.connector
from werkzeug.utils import secure_filename
import hashlib
import hmac

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
    database = "webapp"
)
mycursor = mydb.cursor()
app = Flask(__name__)
app.secret_key = 'secret'
UPLOAD_FOLDER = 'static/images/upload_doc_image/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
mail = Mail(app)
app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'saipavankalyaan99@gmail.com'
app.config['MAIL_PASSWORD'] = 'komoestaas'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
otp = randint(000000, 999999)
@app.route('/', methods=['POST','GET'])
def main():
    if request.method=='POST':
        patient = request.form.get('patient')
        doctor = request.form.get('doctor')
        admin = request.form.get('admin')
        if(patient == 'Patient'):
            return redirect(url_for('login_pat'))
        elif (doctor == 'Doctor'):
            return redirect(url_for('login_doc'))
        elif(admin == 'Admin'):
            return redirect(url_for('login_admin'))
    return render_template('mainmainpage.html')
@app.route('/signup_patient',methods=['POST','GET'])
def signup_pat():
    if(request.method == 'POST'):

        name = request.form.get('name')
        uname = request.form.get('username')
        mob = request.form.get('c')
        email = request.form.get('login')
        age = request.form.get('age')
        session['username'] = uname
        send_otp = request.form.get('send_otp')
        submitform = request.form.get('submitform')
        submitotp = request.form.get('submitotp')
        print(name)
        print(uname)
        print(mob)
        print(email)
        print(submitform)
        sql = "select email from patient_details where email = '" + email + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        if(send_otp == "Send Otp" and len(myresult)==0):
            msg = Message('OTP',sender = 'saipavankalyaan99@gmail.com', recipients = [email])
            msg.body = name+" Your Otp is "+str(otp)
            mail.send(msg)
            return render_template('register_patient.html',name=name,uname=uname,mob=mob,email=email,age=age,visible='none',visible1='block',visible2='none')
        elif(submitotp == "Submit Otp"):
            enter_otp = request.form.get('enterotp')
            print("enter_otp "+enter_otp )
            print("otp ",otp)
            # if(int(enter_otp) == otp):
            return render_template('register_patient.html', name=name, uname=uname, mob=mob, email=email,age=age,
                                   visible='none', visible1='none',visible2='block')
        elif(submitform == "Submit"):
            password = request.form.get('password')
            confirm = request.form.get('confirm')
            print(password)
            print(confirm)

            if(password == confirm):
                msg1 = Message('OTP', sender='saipavankalyaan99@gmail.com', recipients=[email])
                msg1.body = "Mr."+name+"Successfully Registered as patient"
                mail.send(msg1)
                password_to_encrypt = password.encode()
                salt_key = os.urandom(16)
                password_hash = hashlib.pbkdf2_hmac("sha256", password_to_encrypt, salt_key, 100000)
                #%s, %s, %s,%s,%d,%s
                sql0 = "Select email from patient_details where email = '"+email+"'"
                mycursor.execute(sql0)
                myrs = mycursor.fetchall()
                if len(myrs) != 0:
                    return redirect(url_for('signup_pat'))
                sql = "INSERT INTO patient_details (name,username,phone,email,age,password) VALUES (%s, %s, %s,%s,%s,%s)"
                val = (name,uname,mob,email,age,password_hash)
                mycursor.execute(sql, val)
                mydb.commit()
                sql1 = "Insert into pat_hash values(%s,%s)"
                val1 = (email,salt_key)
                mycursor.execute(sql1, val1)
                mydb.commit()

                return redirect(url_for('login_pat'))
        else:
            return redirect(url_for('signup_pat'))
    return render_template('register_patient.html',visible='block',visible1='none',visible2='none')
@app.route('/login_patient',methods=['POST','GET'])
def login_pat():
    if(request.method=='POST'):
        emailme = request.form.get('emailme')
        passwordme = request.form.get('passwordme')
        print(emailme)
        print(passwordme)
        sql2 = "select pat_salt_key from pat_hash where pat_email = '" + emailme + "'"
        mycursor.execute(sql2)
        myresult1 = mycursor.fetchall()
        salt_key_get = myresult1[0][0]
        print(type(salt_key_get))
        print(type(passwordme))
        password_hash = hashlib.pbkdf2_hmac("sha256", passwordme.encode(), salt_key_get, 100000)
        sql = "select name,email,password from patient_details where email = '" + emailme + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        password_hashed = myresult[0][2]
        if(len(myresult)>=1 and hmac.compare_digest(password_hashed, password_hash)):
            print(myresult[0][0])
            session['emailme'] = emailme
            return redirect(url_for('patient_dashboard'))
    return render_template('login_patient.html')
@app.route('/patient_dashboard',methods=['POST','GET'])
def patient_dashboard():
    if(request.method == 'POST'):
        view_doc = request.form.get('view_doc')
        view_rec = request.form.get('view_rec')
        print(view_rec)
        print(view_doc)
        if(view_doc == 'View Doctor'):
            return redirect(url_for('view_doc'))
        elif (view_rec == 'View Records'):
            return redirect(url_for('verify_pat_pass'))
    return render_template('patient_dashboard.html')
@app.route('/verify_patient_password', methods=['POST','GET'])
def verify_pat_pass():
    if (request.method == 'POST'):
        emailme = request.form.get('emailme')
        passwordme = request.form.get('passwordme')
        print(emailme)
        print(passwordme)
        email = session['emailme']
        print(email)

        if(emailme == email):
            sql2 = "select pat_salt_key from pat_hash where pat_email = '" + emailme + "'"
            mycursor.execute(sql2)
            myresult1 = mycursor.fetchall()
            salt_key_get = myresult1[0][0]
            print(type(salt_key_get))
            print(type(passwordme))
            password_hash = hashlib.pbkdf2_hmac("sha256", passwordme.encode(), salt_key_get, 100000)
            sql = "select name,email,password from patient_details where email = '" + emailme + "'"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            password_hashed = myresult[0][2]
            if(len(myresult)>=1 and hmac.compare_digest(password_hashed, password_hash)):
                session['pat_name'] = myresult[0][0]
                return redirect(url_for('patient_rec'))
    return render_template('verify_by_patient_pass.html')
@app.route('/login_doctors',methods=['POST','GET'])
def login_doc():
    if(request.method=='POST'):
        emailme = request.form.get('emailme')
        passwordme = request.form.get('passwordme')
        print(emailme)
        print(passwordme)
        sql2 = "select doc_salt_key from doc_hash where doc_email = '" + emailme + "'"
        mycursor.execute(sql2)
        myresult1 = mycursor.fetchall()
        salt_key_get = myresult1[0][0]
        print(type(salt_key_get))
        print(type(passwordme))
        password_hash = hashlib.pbkdf2_hmac("sha256", passwordme.encode(), salt_key_get, 100000)
        sql = "select firstname,lastname,email,password from doctor_details where email = '" + emailme + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        doc_name = ''
        for x in myresult:
            doc_name = x[0]
        password_hashed = myresult[0][3]
        if(len(myresult)>=1 and hmac.compare_digest(password_hashed, password_hash)):
            session['email_doc'] = emailme
            session['doc_name'] = doc_name
            return redirect(url_for('doctor_dashboard'))
    return render_template('login_doctor.html')

@app.route('/view_doctors',methods=['POST','GET'])
def view_doc():
    doctors = []
    specialism = []
    img = []
    places =[]
    sql = "select firstname,lastname,specialism,city,state,profile_pic from doctor_details"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    i=0
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
    for x in myresult:
        # for i in range(len(myresult)):
       # print(x[1])
        doc_name = x[0]
        doc_specialism = x[2]
        doc_place = x[3]+", "+x[4]
        doc_img = x[5]
        print("doc_img ",doc_img)
        # if(i==1):
        #
        img.append(doc_img)
        doctors.append(doc_name)
        specialism.append(doc_specialism)
        places.append(doc_place)
        i+=1
    print(doctors)
    print(specialism)
    print(places)
    print(img)
    return render_template('view_doctor.html', doctors = doctors, specialism=specialism, img=img,places=places)
@app.route('/view_doctor_profile/<doc>',methods=['POST','GET'])
def view_profile(doc):
    print(doc)

    sql = "select * from doctor_details where firstname = %s"

    adr = (str(doc),)
    mycursor.execute(sql,adr)
    myresult = mycursor.fetchall()
    details = tuple()
    for x in myresult:
        print(x)
        details = x
    return render_template('view_doctor_profile.html',doc_id=details[0],doc_fname = details[1], doc_lname=details[2],uname=details[3],email=details[4],specialism=details[6],gender=details[7],address=details[8],country=details[9],city=details[10],state=details[11],pincode=details[12],phone=details[13],profile_pic=details[14],bio=details[15])
@app.route('/patient_record', methods=['POST','GET'])
def patient_rec():
    record = []
    pres_picture = []
    pat_username = session['pat_name']
    sql = "select prescription,prescription_name from patient_rec where pat_username = %s"
    val = (pat_username,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    for x in myresult:
        record.append(x[1])
        pres_picture.append(x[0])
    print(pres_picture)
    if (request.method == 'POST'):
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
        open = request.form.get('open')
        for i in range(0, len(record)):
            if (open == record[i]):
                print(pres_picture[i])
                return redirect(url_for('pres_pic', pic=pres_picture[i]))
        # img = send_file(url_for('static', filename='images/doctor.png'),mimetype='image')
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))



    return render_template('patient_records.html',record=record)
@app.route('/prescription_by_doctor',methods=['POST','GET'])
def prescription_by_doctor():
    record = []
    pres_picture = []
    doc_name = session['doc_name']
    sql = "select prescription_for_doc,prescription_for_doc_name from patient_rec where doc_username = %s"
    val = (doc_name,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    for x in myresult:
        record.append(x[1])
        pres_picture.append(x[0])
    print(record)
    print(pres_picture)
    if (request.method == 'POST'):
        open = request.form.get('open')
        for i in range(0, len(record)):
            if (open == record[i]):
                return redirect(url_for('pres_pic', pic=pres_picture[i]))
        # img = send_file(url_for('static', filename='images/doctor.png'),mimetype='image')
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))

    return render_template('prescriptions_by_doctor.html',record=record)
@app.route('/login_admin',methods=['POST','GET'])
def login_admin():
    if (request.method == 'POST'):
        emailme = request.form.get('emailme')
        passwordme = request.form.get('passwordme')
        print(emailme)
        print(passwordme)
        if emailme == 'admin@gmail.com' and passwordme == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('login_admin.html')
@app.route('/admin_dashboard',methods=['POST','GET'])
def admin_dashboard():
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
    sql = "select count(DISTINCT(doctor_name)),count(DISTINCT(patient_username)),sum(if(category = 'NEW PATIENTS',1,0)),sum(if(category = 'OPD',1,0)),sum(if(status = 'attended',1,0)),sum(if(status = 'waiting',1,0)),sum(if(category = 'LABORARTORY',1,0)),sum(if(category = 'TREATMENT',1,0)),sum(if(category = 'DISCHARGE',1,0)) from doctor_patient_relation"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    sql1 = "select count(DISTINCT(email)) from doctor_details"
    mycursor.execute(sql1)
    myresult1 = mycursor.fetchall()
    sql2 = "select count(DISTINCT(email)) from patient_details"
    mycursor.execute(sql2)
    myresult2 = mycursor.fetchall()
    sql3 = "select date from doctor_patient_relation"
    mycursor.execute(sql3)
    myresult3 = mycursor.fetchall()
    print(myresult)
    # for x in myresult:
        #print(int(x[4]))
    print("date ", myresult3)
    months = [0,0,0,0,0,0,0,0,0,0,0,0]
    weeks =[0,1,0,2,0,0,5]
    for x in myresult3:
        month = x[0].split(' ')
        print(month[1])
        if month[1] == 'jan':
            months[0]+=1
        elif month[1] == 'feb':
            months[1]+=1
        elif month[1] == 'mar':
            months[2]+=1
        elif month[1] == 'apr':
            months[3]+=1
        elif month[1] == 'may':
            months[4]+=1
        elif month[1] == 'jun':
            months[5]+=1
        elif month[1] == 'july':
            months[6]+=1
        elif month[1] == 'aug':
            months[7]+=1
        elif month[1] == 'sept':
            months[8]+=1
        elif month[1] == 'oct':
            months[9]+=1
        elif month[1] == 'nov':
            months[10]+=1
        elif month[1] == 'dec':
            months[11]+=1

    doctor = myresult1[0][0]
    patients = myresult2[0][0]
    attended = int(myresult[0][4])
    waiting = int(myresult[0][5])
    percent = [int(myresult[0][3]), int(myresult[0][2]), int(myresult[0][6]),int(myresult[0][7]), int(myresult[0][8])]
    dept = ['OPD', 'NEWPATIENTS', 'LABORARTORY', 'TREATMENT', 'DISCHARGE']
    return render_template('admin_dashboard.html',doctor=doctor,patients=patients,attended=attended,waiting=waiting,percent=percent,dept=dept,months=months,weeks =weeks)

@app.route('/doctors_page',methods=['POST','GET'])
def doctor_page():
    if request.method =='POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))

        delete = request.form.get('delete')
        print("delete ", delete)
        sql1 = "delete from doctor_details where email = '" + delete + "'"
        mycursor.execute(sql1)
        mydb.commit()
        return redirect(url_for('doctor_page'))
    doctors = []
    specialism = []
    places = []
    img = []
    email =[]
    places = []
    sql = "select firstname,lastname,specialism,city,state,profile_pic,email from doctor_details"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    i = 0
    for x in myresult:
        # for i in range(len(myresult)):
        # print(x[1])

        doc_name = x[0]
        doc_specialism = x[2]
        doc_place = x[3] + ", " + x[4]
        doc_img = x[5]
        doc_email = x[6]
        print("doc_img ", doc_img)
        # if(i==1):
        #
        img.append(doc_img)
        doctors.append(doc_name)
        specialism.append(doc_specialism)
        places.append(doc_place)
        email.append(doc_email)
        i += 1
    print(doctors)
    print(specialism)
    print(places)
    print(img)
    return render_template('doctors_page.html', doctors=doctors, specialism=specialism, img=img, places=places,email=email)
@app.route('/add_doctor', methods=['POST', 'GET'])
def add_doc():
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
        first = request.form.get('first')
        last = request.form.get('last')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        specialism = request.form.get('specialism')
        gender = request.form.get('gender')
        address = request.form.get('address')
        country = request.form.get('country')
        city = request.form.get('city')
        state = request.form.get('state')
        code = request.form.get('code')
        phone = request.form.get('phone')
        avatar = request.files['avatar']
        # avatarfile = request.form.get('avatar')
        avatarfile = request.files['avatar']
        bio = request.form.get('bio')
        status = request.form.get('status')
        submit = request.form.get('submit')
        doc_id = first+"00"+username
        if password == confirm:
            password_to_encrypt = password.encode()
            salt_key = os.urandom(16)
            password_hash = hashlib.pbkdf2_hmac("sha256", password_to_encrypt, salt_key, 100000)
            if avatar:
                filename = secure_filename(avatar.filename)
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            sql = "INSERT INTO doctor_details (doctor_id,firstname,lastname,username,email,password,specialism,gender,address,country,city,state,pincode,phone,profile_pic,bio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            image = "\static\images\img\\"+ str(avatar.filename)
            # data = read_file(image)
            print(image)
            # image = str(avatarfile)


            #print(doc_pic)
            val = (doc_id, first, last, username, email, password_hash,specialism,gender,address, country, city, state, code, phone,image,bio)
            mycursor.execute(sql, val)
            mydb.commit()
            sql1 = "Insert into doc_hash values(%s,%s)"
            val1 = (email, salt_key)
            mycursor.execute(sql1, val1)
            mydb.commit()
            msg = Message(first, sender='saipavankalyaan99@gmail.com', recipients=[email])
            msg.body = first+" "+last + " is successfully added to our website you can login with given email+"+email+" and password " +password
            mail.send(msg)
            print(first)
            print(last)
            print(username)
            print(email)
            print(password)
            print(confirm)
            print(specialism)
            print(gender)
            print(address)
            print(country)
            print(city)
            print(state)
            print(code)
            print(phone)
            print(avatar)
            print(bio)
            print(status)
            print(submit)
            return redirect(url_for('doctor_page'))
    return render_template('add_doctors.html')
@app.route('/patient_page',methods=['POST','GET'])
def patient_page():
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
    # name = ['Jennifer Robinson', 'Terry Baker', 'Kyle Bowman', 'Marie Howard', 'Joshua Guzman']
    # age=[35, 65, 7, 22, 34]
    # phone = ['(207) 808 8863', '(376) 150 6975', '(981) 756 6128', '(634) 09 3833', '(407) 554 4146']
    # email = ['jenniferrobinson@example.com', 'terrybaker@example.com', 'kylebowman@example.com', 'mariehoward@example.com', 'joshuaguzman@example.com']
    sql = "select name,age,phone,email from patient_details"
    mycursor.execute(sql)
    name=[]
    phone =[]
    age = []
    email = []
    myresult = mycursor.fetchall()
    for i in range(len(myresult)):
        name.append(myresult[i][0])
        age.append(myresult[i][1])
        phone.append(myresult[i][2])
        email.append(myresult[i][3])
    if request.method == 'POST':
        delete = request.form.get('delete')
        print("delete ",delete)
        sql1 = "delete from patient_details where email = '"+delete+"'"
        mycursor.execute(sql1)
        mydb.commit()
        return redirect(url_for('patient_page'))
    return render_template('patients_page.html', name=name,age=age,phone=phone,email=email)
@app.route('/doctor_dashboard',methods=['POST','GET'])
def doctor_dashboard():
    sql = "select count(DISTINCT(doctor_name)),count(DISTINCT(patient_username)),sum(if(category = 'NEW PATIENTS',1,0)),sum(if(category = 'OPD',1,0)),sum(if(status = 'attended',1,0)),sum(if(status = 'waiting',1,0)),sum(if(category = 'LABORARTORY',1,0)),sum(if(category = 'TREATMENT',1,0)),sum(if(category = 'DISCHARGE',1,0)) from doctor_patient_relation where doctor_name = %s"
    doc_name = session['doc_name']
    val = (doc_name,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    print(myresult)
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))

    patients = myresult[0][1]
    print(patients)
    if patients == 0:
        months = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        weeks = [0, 0, 0, 0, 0, 0, 0]
        patients =0
        attended = 0
        waiting = 0
        percent = [0,0,0,0,0]
        dept = ['OPD', 'NEWPATIENTS', 'LABORARTORY', 'TREATMENT', 'DISCHARGE']
        return render_template('doctor_dashboard.html', total=patients, today=5, attended=attended, waiting=waiting,
                               percent=percent, dept=dept,months=months,weeks=weeks)
    else:
        sql3 = "select date from doctor_patient_relation where doctor_name='"+doc_name+"'"
        mycursor.execute(sql3)
        myresult3 = mycursor.fetchall()
        months = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        weeks = [0, 1, 0, 0, 0, 0, 0]
        for x in myresult3:
            month = x[0].split(' ')
            print(month[1])
            if month[1] == 'jan':
                months[0] += 1
            elif month[1] == 'feb':
                months[1] += 1
            elif month[1] == 'mar':
                months[2] += 1
            elif month[1] == 'apr':
                months[3] += 1
            elif month[1] == 'may':
                months[4] += 1
            elif month[1] == 'jun':
                months[5] += 1
            elif month[1] == 'july':
                months[6] += 1
            elif month[1] == 'aug':
                months[7] += 1
            elif month[1] == 'sept':
                months[8] += 1
            elif month[1] == 'oct':
                months[9] += 1
            elif month[1] == 'nov':
                months[10] += 1
            elif month[1] == 'dec':
                months[11] += 1
        attended = int(myresult[0][4])
        waiting = int(myresult[0][5])
        percent = [int(myresult[0][3]), int(myresult[0][2]), int(myresult[0][6]), int(myresult[0][7]), int(myresult[0][8])]

        dept = ['OPD', 'NEWPATIENTS', 'LABORARTORY', 'TREATMENT', 'DISCHARGE']

        return render_template('doctor_dashboard.html', total=patients,today=5, attended=attended, waiting=waiting,
                           percent=percent, dept=dept,months=months,weeks=weeks)
@app.route('/appointments', methods=['POST','GET'])
def appointments():
    app_id = []
    pat_name = []
    age = []
    date = []
    starttime = []
    endtime = []
    doc_id = session['doc_name']
    sql = "select * from appointment_details where attend = 'YES' and doctor_id = '"+doc_id+"'"
    print(doc_id)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        app_id.append(x[0])
        pat_name.append(x[1])
        age.append(x[2])
        date.append(x[3])
        starttime.append(x[6])
        endtime.append(x[7])




    status =['Attending', 'Waiting']
    color = ['green', 'purple']
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
        completed = request.form.get('completed')
        for i in range(0,len(pat_name)):
            if completed == pat_name[i]:
                sql = "delete from appointment_details where patient_name = %s"
                val = (completed,)
                mycursor.execute(sql,val)
                mydb.commit()
                sql1 = "Insert into doctor_patient_relation Values(%s,%s,%s,%s,%s)"
                val1 = (doc_id,completed,'OPD',date[i],'attended')
                mycursor.execute(sql1, val1)
                mydb.commit()
                return render_template('doctor_appointments.html', app_id=app_id, pat_name=pat_name, age=age, date=date,
                                       starttime=starttime, endtime=endtime)
    return render_template('doctor_appointments.html', app_id=app_id,pat_name=pat_name,age=age,date=date,starttime=starttime,endtime=endtime)
@app.route('/doctor_requests', methods=['POST','GET'])
def requests():
    # if(request.method=='POST'):

    app_id = []
    pat_name= []
    age = []
    date=[]
    doc_id = session['doc_name']
    sql = "select * from appointment_details where attend = 'NO' and doctor_id = '"+doc_id+"'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        app_id.append(x[0])
        pat_name.append(x[1])
        age.append(x[2])
        date.append(x[3])
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
        yesorno = request.form.get('yesorno')

        submit = request.form.get('submit')

        if yesorno == 'YES':
            for i in range(0,len(pat_name)):
                if submit == pat_name[i]:
                    print("Submit ", submit)
                    return redirect(url_for('appointment_confirm', pat_name = submit))
        else:
            sql = "delete from appointment_details where patient_name = %s"
            val = (submit,)
            mycursor.execute(sql, val)
            mydb.commit()
        # if(submityesorno == patient_name and attend == 'YES'):
        #     print("yes or no")
        #     return render_template('doctor_requests.html', app_id=app_id, pat_name=pat_name, age=age, date=date,
        #                            time1title1='block', submityesorno1='none')
        # elif(submittime == patient_name):
        #     startdate = request.form.get('start')
        #     enddate = request.form.get('end')
        #     print("start " + startdate)
        #     print("end " + enddate)
        #     print("submittime")
        #     sql1 = "UPDATE appointment_details SET start='" + startdate + "' , end='" + enddate + "', attend='YES' where patient_name='" + patient_name + "'"
        #     mycursor.execute(sql1)
        #     mydb.commit()
        #     return redirect(url_for('requests'))
    return render_template('doctor_requests.html',app_id=app_id,pat_name=pat_name,age=age,date=date)

@app.route('/appointment_confirm/<pat_name>', methods=['POST','GET'])
def appointment_confirm(pat_name):

    sql = "select app_id,patient_name,age,date from appointment_details where patient_name = %s"
    val = (pat_name,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchall()
    app_id = ''
    patient_name = ''
    age = 0
    date = ''
    for x in myresult:
        app_id = x[0]
        patient_name = x[1]
        age = x[2]
        date = x[3]
    if request.method == 'POST':
        startdate = request.form.get('start')
        enddate = request.form.get('end')
        print("start " , startdate)
        print("end " , enddate)
        sql1 = "UPDATE appointment_details SET start='" + str(startdate) + "' , end='" + str(enddate) + "', attend='YES' where patient_name='" + patient_name + "'"
        mycursor.execute(sql1)
        mydb.commit()
        return redirect(url_for('appointments'))
    return render_template('appointment_confirm.html',app_id=app_id,patient_name=patient_name,age=age,date=date)
@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'POST':
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))
    print(session['email_doc'])
    doc_email = session['email_doc']
    sql = "select * from doctor_details where email = %s"

    adr = (str(doc_email),)
    mycursor.execute(sql, adr)
    myresult = mycursor.fetchall()
    details = tuple()
    for x in myresult:
        print(x)
        details = x
    if len(details)==0:
        return redirect(url_for('doctor_dashboard'))
    return render_template('doctor_profile.html', doc_id=details[0], doc_fname=details[1], doc_lname=details[2],
                           uname=details[3], email=details[4], specialism=details[6], gender=details[7],
                           address=details[8], country=details[9], city=details[10], state=details[11],
                           pincode=details[12], phone=details[13], profile_pic=details[14], bio=details[15])
    #return render_template('view_doctor_profile.html')
otp1 = randint(000000, 999999)
@app.route('/view_by_doctor_OTP', methods=['POST', 'GET'])
def doc_otp():

    if request.method == 'POST':
        emailme = request.form.get('emailme')
        sendotp = request.form.get('sendotp')
        enterotp = request.form.get('enterotp')
        submitme = request.form.get('submitme')
        sql = "select email from patient_details where email = '" + emailme + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        if(sendotp == 'Send Otp' and len(myresult)>=1):

            msg = Message('OTP', sender='saipavankalyaan99@gmail.com', recipients=[emailme])
            msg.body = emailme +str(otp1)
            mail.send(msg)
            print(otp1)
            return render_template('view_by_doctor_OTP.html',emailme=emailme,visible='none',visible2='block')
        if (submitme == 'Submit Otp'):
            if(enterotp == str(otp1)):
                print(enterotp)
                return redirect(url_for('documents'))
    return render_template('view_by_doctor_OTP.html',visible='block',visible2='none')
@app.route('/view_by_doctor_password', methods=['POST', 'GET'])
def doc_pass():
    if (request.method == 'POST'):
        emailme = request.form.get('emailme')
        passwordme = request.form.get('passwordme')
        print(emailme)
        print(passwordme)
        sql2 = "select pat_salt_key from pat_hash where pat_email = '" + emailme + "'"
        mycursor.execute(sql2)
        myresult1 = mycursor.fetchall()
        salt_key_get = myresult1[0][0]
        print(type(salt_key_get))
        print(type(passwordme))
        password_hash = hashlib.pbkdf2_hmac("sha256", passwordme.encode(), salt_key_get, 100000)
        sql = "select name,email,password from patient_details where email = '" + emailme + "'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        password_hashed = myresult[0][2]



        pat_name = ''
        for x in myresult:
            pat_name = x[0]
        if (len(myresult) >= 1 and hmac.compare_digest(password_hashed, password_hash)):
            session['pat_name1'] = pat_name
            return redirect(url_for('documents'))
    return render_template('verify_by_doctor_pass.html')
@app.route('/documents_doctor', methods=['POST', 'GET'])
def documents():
    record = []
    pres_picture = []
    pat_username = session['pat_name1']
    sql = "select prescription,prescription_name from patient_rec where pat_username = %s"
    val = (pat_username,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    for x in myresult:
        record.append(x[1])
        pres_picture.append(x[0])
    if (request.method == 'POST'):
        open = request.form.get('open')
        for i in range(0,len(record)):
            if(open == record[i]):
                return redirect(url_for('pres_pic',pic = pres_picture[i]))
        # img = send_file(url_for('static', filename='images/doctor.png'),mimetype='image')
        logout = request.form.get('logout')
        if (logout == 'logout'):
            return redirect(url_for('main'))





    return render_template('documents_doctor.html',record=record)
@app.route('/prescription_pic/<pic>',methods=['POST','GET'])
def pres_pic(pic):
    return send_file(pic,mimetype='image/gif')
@app.route('/prescription', methods=['POST', 'GET'])
def prescription():
    if request.method == 'POST':
        tablet = request.form.get('tablet').split(',')
        morn = request.form.get('morn').split(',')
        date1 = date.today()
        print(date1)
        pat_name = session['pat_name1']
        doc_name = session['doc_name']
        sql = "select "
        afternoon = request.form.get('afternoon').split(',')
        night = request.form.get('night').split(',')
        duration = request.form.get('duration').split(',')
        beforefood = request.form.get('beforefood').split(',')
        afterfood = request.form.get('afterfood').split(',')
        noted = request.form.get('noted').split(',')
        lengthoftablets = len(tablet)
        labtestname = request.form.get('labtestname').split(',')
        labtestdate = request.form.get('labtestdate').split(',')
        img = Image.new('RGB',(1000,1300),color = 'white')
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 30)
        font1 = ImageFont.truetype("arial.ttf", 50)
        d.text((275,43), doc_name, fill='black', font=font1)
        d.text((535, 185), pat_name , fill='black', font=font1)
        d.text((100, 200), "Date", fill='black', font=font)
        d.text((95, 350), "Tablet Name", fill='black', font=font)
        d.text((290, 350), "M", fill='black', font=font)
        d.text((365, 350), "A", fill='black', font=font)
        d.text((430, 350), "N", fill='black', font=font)
        d.text((490, 350), "Duration", fill='black', font=font)
        d.text((635, 350), "BF", fill='black', font=font)
        d.text((705, 350), "AF", fill='black', font=font)
        d.text((775, 350), "Notes", fill='black', font=font)
        d.text((235, 960), "Lab Test Name", fill='black', font=font)
        d.text((565, 960), "Lab Test Date", fill='black', font=font)
        d.text((110, 250), "date1" , fill='black', font=font)
        y = 410
        for i in range(1,len(tablet)):
            d.text((95,y),tablet[i],fill='black',font=font)
            d.text((290, y), morn[i], fill='black', font=font)
            d.text((365, y), afternoon[i], fill='black', font=font)
            d.text((430, y), night[i], fill='black', font=font)
            d.text((490, y), duration[i], fill='black', font=font)
            d.text((635, y), beforefood[i], fill='black', font=font)
            d.text((705, y), afterfood[i], fill='black', font=font)
            d.text((775, y), noted[i], fill='black', font=font)
            y+=70
        y = 1030
        for i in range(1,len(labtestname)):
            d.text((235, y), labtestname[i], fill='black', font=font)
            d.text((565, y), labtestdate[i], fill='black', font=font)
            y+=70
        filename = 'static\images\prescription\Dr.'+doc_name+'@'+str(date1)+'.png'
        pres_filename = 'Dr.'+doc_name+'@'+str(date1)
        img.save(filename)
        pat_name = session['pat_name1']
        doc_file = 'static\images\prescription_by_doc\Mr.'+pat_name+'@'+str(date1)+'.png'
        pres_filename_doc = 'Mr.'+pat_name+'@'+str(date1)
        img.save(doc_file)
        sql = "Insert into patient_rec(pat_username,doc_username,date,prescription,prescription_for_doc,prescription_name,prescription_for_doc_name) Values (%s,%s,%s,%s,%s,%s,%s)"
        date2 = str(date1)
        rec = (pat_name,doc_name,date2,filename,doc_file,pres_filename,pres_filename_doc)
        mycursor.execute(sql,rec)
        mydb.commit()


        print(tablet)
        print(morn)
        print(afternoon)
        print(night)
        print(duration)
        print(beforefood)
        print(afterfood)
        print(noted)
        print(labtestname)
        print(labtestdate)
    return render_template('prescription.html')

# @app.route('/validate',methods=["POST"])
# def validate():
#     user_otp = request.form['otp']
#     if otp == int(user_otp):
#         email = "m.muniprasanna@gmail.com"
#         msg = Message('Successfully Logged in', sender='saipavankalyaan99@gmail.com', recipients=[email])
#         msg.body = "successfully logged in go on muni"
#         mail.send(msg)
#         return "<h3> Email  verification is  successful </h3>"
#     return "<h3>failure, OTP does not match</h3>"
if __name__ == '__main__':
    app.run(debug = True)