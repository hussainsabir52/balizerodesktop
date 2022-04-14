 # -*- coding: utf-8 -*-
from flask import Flask, request, redirect, url_for, render_template, flash,jsonify,Response, session
import json
from flask_sqlalchemy import SQLAlchemy 
from config import database, secret
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, date
from dateutil.rrule import rrule, DAILY
from flask_login import LoginManager , UserMixin, login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from flask_mail import Mail,Message 
from functools import wraps
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from form import FormOne,FormTwo
from sqlalchemy.sql import func
from sqlalchemy import extract
import random
from flask_compress import Compress
from werkzeug.utils import secure_filename
import os
from form import AppliedForm,StepOneSocialForm,StepOneBusinessForm,StepTwoForm,StepThreeForm,StepFourForm,UploadForm,SubmitForm
from form import AppointmentForm



app = Flask(__name__) 
COMPRESS_MIMETYPES = ["text/html", "text/css", "application/json"]
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500
Compress(app) 
app.config["SQLALCHEMY_DATABASE_URI"] = database
app.config["SECRET_KEY"] = secret 
db = SQLAlchemy(app)
app.debug = True 




migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


#fungsi Upload
#mengatur image
UPLOAD_FOLDER = 'static/document/'
ALLOWED_EXTENSIONS = {'jpeg','jpg','png','pdf'}
images = UploadSet("images",IMAGES)
app.config["UPLOADED_IMAGES_DEST"] = "static/document/"
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
configure_uploads(app,images)




#################################################### Decorator ##############################################################################



#fungsi mail
app.config.from_pyfile("config.py") 
mail = Mail(app)
s = URLSafeTimedSerializer("secret")





@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

@app.errorhandler(500)
def internal_server(error):
    return 'Opps something bad happen,try again', 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


####################################################### Model #############################################
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(200))   
    password = db.Column(db.String(500))        
    role = db.Column(db.String(100))    


class Booking(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    url = db.Column(db.String(200))  
    services = db.Column(db.String(200))
    paymentmethod = db.Column(db.String(200))
    fullname = db.Column(db.String(200))
    surname = db.Column(db.String(200))
    gender =  db.Column(db.String(200))
    birthplace = db.Column(db.String(200))
    birthdate = db.Column(db.DateTime())
    martial =  db.Column(db.String(200))
    nationality =  db.Column(db.String(200))
    email =  db.Column(db.String(200))
    phone =  db.Column(db.String(200))
    original_address =  db.Column(db.Text())
    original_city = db.Column(db.String(200))
    original_state =  db.Column(db.String(200))
    original_zip =  db.Column(db.String(200))
    original_country =  db.Column(db.String(200))
    indo_address =  db.Column(db.Text())
    indo_city = db.Column(db.String(200))
    indo_state =  db.Column(db.String(200))
    indo_zip =  db.Column(db.String(200))
    emergency_name =  db.Column(db.String(200))
    emergency_status =  db.Column(db.String(200))
    emergency_address =  db.Column(db.Text())
    emergency_city = db.Column(db.String(200))
    emergency_state =  db.Column(db.String(200))
    emergency_zip =  db.Column(db.String(200))
    emergency_country =  db.Column(db.String(200))
    emergency_email =  db.Column(db.String(200))
    emergency_phone =  db.Column(db.String(200))
    visit_purpose = db.Column(db.String(200))
    activities = db.Column(db.Text())
    deported = db.Column(db.String(200))
    overstay = db.Column(db.String(200))    
    created_date = db.Column(db.DateTime())
    status = db.Column(db.String(200))   
    tipe = db.Column(db.String(200))
    pricing = db.Column(db.String(200)) 
    services = db.Column(db.String(200))
    traveldocumentowner = db.relationship("TravelDocument",backref="traveldocumentowner") 
    documentowner = db.relationship("Document",backref="documentowner") 

class TravelDocument(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    tipe = db.Column(db.String(200))
    document_number = db.Column(db.String(200))
    place_issued = db.Column(db.String(200))
    date_issued = db.Column(db.DateTime())
    date_expired = db.Column(db.DateTime())
    traveldocumentowner_id =  db.Column(db.Integer(), db.ForeignKey("booking.id"))

class Document(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    tipe = db.Column(db.String(200))
    filename = db.Column(db.Text())
    documentowner_id =  db.Column(db.Integer(), db.ForeignKey("booking.id"))


class Appointment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(200))
    services = db.Column(db.String(200))
    meeting = db.Column(db.String(200))
    date = db.Column(db.DateTime()) 
    url = db.Column(db.String(200))
    time = db.Column(db.String(200))
    countrytime = db.Column(db.String(200))


class CountryList(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200))





#populate country
@app.route("/populate/country",methods=["GET","POST"])
def PopulateCountry():
    countrylist = [
    "Afghanistan",
    "Albania",
    "Algeria",
    "American Samoa",
    "Andorra",
    "Angola",
    "Anguilla",
    "Antarctica",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Aruba",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bermuda",
    "Bhutan",
    "Bolivia",
    "Bonaire Sint Eustatius and Saba",
    "Bosnia and Herzegovina",
    "Botswana",
    "Bouvet Island",
    "Brazil",
    "British Indian Ocean Territory",
    "Brunei Darussalam",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cabo Verde",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cayman Islands",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Christmas Island",    
    "Colombia",
    "Comoros",   
    "Congo",
    "Cook Islands",
    "Costa Rica",
    "Croatia",
    "Cuba",
    "Curacao",
    "Cyprus",
    "Czechia",
    "Cote d'Ivoire",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Eswatini",
    "Ethiopia",
    "Falkland Islands",
    "Faroe Islands",
    "Fiji",
    "Finland",
    "France",
    "French Guiana",
    "French Polynesia",
    "French Southern Territories",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Gibraltar",
    "Greece",
    "Greenland",
    "Grenada",
    "Guadeloupe",
    "Guam",
    "Guatemala",
    "Guernsey",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Heard Island and McDonald Islands",
    "Holy See",
    "Honduras",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran",
    "Iraq",
    "Ireland",
    "Isle of Man",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jersey",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Korea"
    "Kuwait",
    "Kyrgyzstan",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Macao",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Martinique",
    "Mauritania",
    "Mauritius",
    "Mayotte",
    "Mexico",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Montserrat",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "New Caledonia",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "Niue",
    "Norfolk Island",
    "Northern Mariana Islands",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestine",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Pitcairn",
    "Poland",
    "Portugal",
    "Puerto Rico",
    "Qatar",
    "Republic of North Macedonia",
    "Romania",
    "Russian Federation",
    "Rwanda",
    "Saint Barthelemy",
    "Saint Helena Ascension and Tristan da Cunha",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Martin",
    "Saint Pierre and Miquelon",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Sint Maarten",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Georgia and the South Sandwich Islands",
    "South Sudan",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Svalbard and Jan Mayen",
    "Sweden",
    "Switzerland",
    "Syrian Arab Republic",
    "Taiwan",
    "Tajikistan",
    "Tanzania United Republic of",
    "Thailand",
    "Timor-Leste",
    "Togo",
    "Tokelau",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Turks and Caicos Islands",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom of Great Britain and Northern Ireland",
    "United States Minor Outlying Islands",
    "United States of America",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Venezuela",
    "Viet Nam",
    "Virgin Islands",
    "Wallis and Futuna",
    "Western Sahara",
    "Yemen",
    "Zambia",
    "Zimbabwe"
];
    for x in countrylist:
        check = CountryList.query.filter_by(name=x).all()
        if len(check) == 0:
            added = CountryList(name=x)
            db.session.add(added)
            db.session.commit()
    return "fuckup"  















@app.route("/",methods=["GET","POST"])
def Index():
    formone = AppliedForm()
    formtwo = FormTwo()
    if request.method == "POST":
        email = request.form["email"]
        if "@" in email:

            if "form1" in request.form:
                time = request.form["vehicle"]
                purpose = request.form["manufacturer"]
                if time == "Less than 30 days":
                    if purpose == "Tourism":
                        messages = "SINCE MARCH 2020 COMING FOR TOURISM PORPOSE IS POSSIBEL ONLY WITH A B211A ENTRY VISA"
                        url = "APPLY FOR SINGLE ENTRY VISA"
                    elif purpose == "Business/Other":
                        messages = "YOU CAN APPLY WITH US. WE WILL BE YOUR SPONSOR TO APPLY FOR A B211A ENTRY VISA"
                        url = "APPLY FOR SINGLE ENTRY VISA"
                    else:
                        messages = "NO SERVICES WAS FOUND"    
                        url = "GET HELP"

                    return redirect(url_for("Result",messages=messages,url=url))     

                elif time == "More than 1 month and less than 6 month":
                    if purpose == "Staycation/Business/Remotely":
                        messages = "YOU CAN APPLY WITH US AND STAY IN INDONESIA UP TO 180 DAYS WE WILL BE YOUR SPONSOR TO APPLY FOR A B211A ENTRY VISA"
                        url = "APPLY FOR SINGLE ENTRY VISA"
                    elif purpose == "Work":
                        messages = "TO WORK AND GENERATE INCOME IN INDONESIA YOU MUST HAVE A WORKING PERMIT AND BE HIRED BY AN INDONESIAN COMPANY (WORKING VISA) OR WORK INDIPENENTLY AS A FREELANCE (FREELANCE VISA)"
                        url = "WANT TO KNOW MORE ABOUT WORKING VISA"
                    elif purpose == "Investment":
                        messages = "IF YOU WANT TO START YOUR BUSINESS IN INDONESIAYOU CAN OPEN YOUR OWN FOREIGN COMPANY (PT PMA) AND APPLY FOR AN INVESTOR VISA"
                        url = "APPLY FOR INVESTOR KITAS"    
                    else:
                        messages = "NO SERVICES WAS FOUND"    
                        url = "GET HELP"

                    return redirect(url_for("Result",messages=messages,url=url))     

                elif time == "Long term more than 6 month":
                    if purpose == "I'm Retired":
                        messages = "IF YOU HAVE MORE THAN 55 YEARS OLD YOU CAN APPLY FOR A LONG TERM STAY PERMIT"
                        url = "APPLY FOR RETIREMENT VISA"

                    elif purpose == "I'm Married With Indonesian":
                        messages = "IF YOU MERRIED AND INDONESIAN CITIZEN YOU CANAPPLY FOR A LONG TERM STAY PERMIT"
                        url = "APPLY FOR MARRIAGE VISA"

                    elif purpose == "Investment":
                        messages = "IF YOU WANT TO START YOUR BUSINESS IN INDONESIAYOU CAN OPEN YOUR OWN FOREIGN COMPANY (PT PMA) AND APPLY FOR AN INVESTOR VISA"
                        url = "APPLY FOR INVESTOR KITAS"    

                    elif purpose == "Staycation/Business/Remotely":
                        messages = "YOU CAN APPLY WITH US AND STAY IN INDONESIA UP TO 180 DAYS WE WILL BE YOUR SPONSOR TO APPLY FOR A B211A ENTRY VISA"
                        url = "APPLY FOR SINGLE ENTRY VISA"
                    elif purpose == "Work":
                        messages = "TO WORK AND GENERATE INCOME IN INDONESIA YOU MUST HAVE A WORKING PERMIT AND BE HIRED BY AN INDONESIAN COMPANY (WORKING VISA) OR WORK INDIPENENTLY AS A FREELANCE (FREELANCE VISA)"
                        url = "WANT TO KNOW MORE ABOUT WORKING VISA"
                    elif purpose == "Investment":
                        messages = "IF YOU WANT TO START YOUR BUSINESS IN INDONESIAYOU CAN OPEN YOUR OWN FOREIGN COMPANY (PT PMA) AND APPLY FOR AN INVESTOR VISA"
                        url = "APPLY FOR INVESTOR KITAS"        

                    else:
                        messages = "NO SERVICES WAS FOUND"    
                        url = "GET HELP"        
                        
                    return redirect(url_for("Result",messages=messages,url=url)) 
            if "form2" in request.form:        
                return "--"
        else:
            return redirect(url_for("EnterEmail"))      
    return render_template("index.html",formone=formone,formtwo=formtwo)    



@app.route("/calling",methods=["GET","POST"])
def Calling():
    return render_template("calling.html")


@app.route("/email",methods=["GET","POST"])
def EnterEmail():
    return render_template("email.html")    



@app.route("/two",methods=["GET","POST"])
def Index2():
    formone = FormOne()
    formtwo = FormTwo()
    if formtwo.validate_on_submit():
        messages = "YOU EGLIBED TO APPLY"    
        url = "APPLY NOW"    
        return redirect(url_for("Result",messages=messages,url=url))   
                    
    return render_template("bali.html",formone=formone,formtwo=formtwo)   



@app.route("/result/<messages>/<url>",methods=["GET","POST"])
def Result(messages,url):
    formone = FormOne()
    formtwo = FormTwo() 
    if request.method == "POST":
        if "form1" in request.form:
            time = request.form["vehicle"]
            purpose = request.form["manufacturer"]
            if time == "Less than 30 days":
                if purpose == "Tourism":
                    messages = "SINCE MARCH 2020 COMING FOR TOURISM PORPOSE IS POSSIBEL ONLY WITH A B211A ENTRY VISA"
                    url = "APPLY FOR SINGLE ENTRY VISA"
                elif purpose == "Business/Other":
                    messages = "YOU CAN APPLY WITH US. WE WILL BE YOUR SPONSOR TO APPLY FOR A B211A ENTRY VISA"
                    url = "APPLY FOR SINGLE ENTRY VISA"
                else:
                    messages = "NO SERVICES WAS FOUND"    
                    url = "GET HELP"

                return redirect(url_for("Result",messages=messages,url=url))     

            elif time == "Less than 6 month":
                if purpose == "Staycation/Business/Remotely":
                    messages = "YOU CAN APPLY WITH US AND STAY IN INDONESIA UP TO 180 DAYS WE WILL BE YOUR SPONSOR TO APPLY FOR A B211A ENTRY VISA"
                    url = "APPLY FOR SINGLE ENTRY VISA"
                elif purpose == "Work":
                    messages = "TO WORK AND GENERATE INCOME IN INDONESIA YOU MUST HAVE A WORKING PERMIT AND BE HIRED BY AN INDONESIAN COMPANY (WORKING VISA) OR WORK INDIPENENTLY AS A FREELANCE (FREELANCE VISA)"
                    url = "WANT TO KNOW MORE ABOUT WORKING VISA"
                elif purpose == "Investment":
                    messages = "IF YOU WANT TO START YOUR BUSINESS IN INDONESIAYOU CAN OPEN YOUR OWN FOREIGN COMPANY (PT PMA) AND APPLY FOR AN INVESTOR VISA"
                    url = "APPLY FOR INVESTOR KITAS"    
                else:
                    messages = "NO SERVICES WAS FOUND"    
                    url = "GET HELP"

                return redirect(url_for("Result",messages=messages,url=url))     

            elif time == "Long term more than 6 month":
                if purpose == "I'm Retired":
                    messages = "IF YOU HAVE MORE THAN 55 YEARS OLD YOU CAN APPLY FOR A LONG TERM STAY PERMIT"
                    url = "APPLY FOR RETIREMENT VISA"

                elif purpose == "I'm Married With Indonesian":
                    messages = "IF YOU MERRIED AND INDONESIAN CITIZEN YOU CANAPPLY FOR A LONG TERM STAY PERMIT"
                    url = "APPLY FOR MARRIAGE VISA"

                elif purpose == "Investment":
                    messages = "IF YOU WANT TO START YOUR BUSINESS IN INDONESIAYOU CAN OPEN YOUR OWN FOREIGN COMPANY (PT PMA) AND APPLY FOR AN INVESTOR VISA"
                    url = "APPLY FOR INVESTOR KITAS"    

                elif purpose == "Staycation/Business/Remotely":
                    messages = "YOU CAN APPLY WITH US AND STAY IN INDONESIA UP TO 180 DAYS WE WILL BE YOUR SPONSOR TO APPLY FOR A B211A ENTRY VISA"
                    url = "APPLY FOR SINGLE ENTRY VISA"
                elif purpose == "Work":
                    messages = "TO WORK AND GENERATE INCOME IN INDONESIA YOU MUST HAVE A WORKING PERMIT AND BE HIRED BY AN INDONESIAN COMPANY (WORKING VISA) OR WORK INDIPENENTLY AS A FREELANCE (FREELANCE VISA)"
                    url = "WANT TO KNOW MORE ABOUT WORKING VISA"
                elif purpose == "Investment":
                    messages = "IF YOU WANT TO START YOUR BUSINESS IN INDONESIAYOU CAN OPEN YOUR OWN FOREIGN COMPANY (PT PMA) AND APPLY FOR AN INVESTOR VISA"
                    url = "APPLY FOR INVESTOR KITAS"        

                else:
                    messages = "NO SERVICES WAS FOUND"    
                    url = "GET HELP"        
                    
                return redirect(url_for("Result",messages=messages,url=url)) 
        if "form2" in request.form:        
            return "--"
    return render_template("result.html",formone=formone,formtwo=formtwo,messages=messages,url=url)   



@app.route("/services/<name>",methods=["GET","POST"])
def Services(name):
    if name == "investor-kitas" :
        return render_template("investor.html") 
    elif name == "retirment-kitas"  :  
        return render_template("retirment.html") 
    elif name == "spouse-kitas"  :  
        return render_template("spouse.html")     
    elif name == "working-kitas"  :  
        return render_template("working.html")     
    elif name == "freelance-kitas"  :  
        return render_template("freelance.html")
    elif name == "social-visa-onshore":
        return render_template("social.html")
    elif name == "business-visa-offshore":
        return render_template("business.html")
    elif name == "set-up-pt-pma":
        return render_template("pma.html")    
    elif name == "cozero-living":  
        return render_template("cozero-living.html")  
                         
                     

@app.route("/sub/appointment/<services>",methods=["GET","POST"])
def CreateAppointment(services):
    form = AppointmentForm()
    form.countrytime.choices = [(str(x.name),str(x.name)) for x in CountryList.query.all()]    
    if form.validate_on_submit():     
        phone = form.phone.data
        if phone[0] == "+": 
            string = []
            chars = 'abccdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
            finished = False
            while not finished:
                for x in range(1, 6+1):
                    string.append(random.choice(chars))
                string = "".join(string)
                check = Appointment.query.filter_by(url=string).all()
                if len(check) < 1:
                    finished = True

            
            meeting = request.form["meeting"]
            time = form.time.data + ""+ form.ampm.data         
            country = CountryList.query.filter_by(name=form.countrytime.data).first()
            order = Appointment(name=form.name.data,email=form.email.data,date=form.date.data,meeting=form.meeting.data,
                    services=services,url=string,phone=form.phone.data,time=time,countrytime=country.name)
            db.session.add(order)
            db.session.commit()
            return redirect(url_for("ThankYou",url=order.url))
                    
        else:
            flash("Please use + country on whatsapp form","danger")    
    return render_template("submission/appointment.html",form=form,services=services)    
    
@app.route("/sub/appointment/<url>/thanks",methods=["GET","POST"])
def ThankYou(url):
    order = Appointment.query.filter_by(url=url).first()
    form = AppointmentForm()
    return render_template("submission/thankyou.html",order=order,form=form)        


@app.route("/sub/order/<tipe>",methods=["GET","POST"])
def CreateOrder(tipe):
    string = []
    chars = 'abccdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    finished = False
    while not finished:
        for x in range(1, 6+1):
            string.append(random.choice(chars))
        string = "".join(string)
        check = Booking.query.filter_by(url=string).all()
        if len(check) < 1:
            finished = True

    today = datetime.today()         
    order = Booking(url=string,created_date=today,status="uncomplete data",tipe=tipe)
    db.session.add(order)
    db.session.commit()
    return redirect(url_for("StepOne",url=order.url))



@app.route("/sub/step1/<url>",methods=["GET","POST"])
def StepOne(url):
    booking = Booking.query.filter_by(url=url).first()
    if booking.services == None: 
        if booking.tipe == "business visa offshore":
            form = StepOneBusinessForm()  
        else:    
            form = StepOneSocialForm()   

        if form.validate_on_submit():
            checked = request.form.getlist("vehicle")
            if len(checked) == 4:
                services = form.services.data 
                if services == "E-Visa Service" :
                    booking.pricing = 245
                    db.session.commit()
                elif services == "E-Visa Service + Visa Extention":
                    booking.pricing = 315
                    db.session.commit()
                elif services == "E-Visa Super Express Proccess Service":
                    booking.pricing = 329
                    db.session.commit() 
                elif services == "E-Visa Express Proccess Service":
                    booking.pricing = 249
                    db.session.commit() 
                else:
                    booking.pricing = 700
                    db.session.commit()                    
                               

                booking.paymentmethod = form.payment.data 
                booking.services = form.services.data 
                db.session.commit()          

                return redirect(url_for("StepTwo",url=url))
            else:
                flash("Please select all the check box","danger")    
    else:

        booking = Booking.query.filter_by(url=url).first()
        if booking.tipe == "business visa offshore":
            form = StepOneBusinessForm()  
        else:    
            form = StepOneSocialForm()

        form.services.data = booking.services
        form.payment.data = booking.paymentmethod     
        if form.validate_on_submit():
            checked = request.form.getlist("vehicle")
            if len(checked) == 4:

                services = request.form["services"]
                if services == "E-Visa Service":
                    booking.pricing = 3300000
                    db.session.commit()
                elif services == "E-Visa Service + Visa Extention":
                    booking.pricing = 6500000
                    db.session.commit()
                elif services == "E-Visa Super Express Proccess Service":
                    booking.pricing = 329
                    db.session.commit() 
                elif services == "E-Visa Express Proccess Service":
                    booking.pricing = 259
                    db.session.commit() 
                else:
                    booking.pricing = 700
                    db.session.commit()    
                booking.services = services    
                booking.paymentmethod = request.form["payment"]
                db.session.commit()

                return redirect(url_for("StepTwo",url=url))
            
            else:
                flash("Please select all the check box","danger")    
                    
    return render_template("submission/stepone.html",form=form,tipe=booking.tipe,booking=booking,
        url=url)



@app.route("/sub/step2/<url>",methods=["GET","POST"])
def StepTwo(url):
    booking = Booking.query.filter_by(url=url).first()
    form = StepTwoForm()    
    if booking.fullname == None:
        if form.validate_on_submit():
            phone = form.phone.data
            if phone[0] == "+":
                booking.fullname =   form.fullname.data
                booking.surname =   form.surname.data
                booking.gender =  form.gender.data   
                booking.birthplace =   form.birthplace.data
                booking.birthdate =  form.birthdate.data
                booking.martial =  form.martial.data 
                booking.nationality =   form.nationality.data
                booking.email =  form.email.data   
                booking.phone =  form.phone.data 
                booking.original_address = form.original_address.data 
                booking.original_city = form.original_city.data
                booking.original_state =form.original_state.data
                booking.original_zip =  form.original_zip.data
                booking.original_country =  form.original_country.data       
                db.session.commit()
                return redirect(url_for("StepThree",url=url))
            else:
                flash("Please use + country on whatsapp form","danger")
    else:
        form.fullname.data= booking.fullname
        form.surname.data= booking.surname
        form.gender.data  = booking.gender
        form.birthplace.data= booking.birthplace
        form.birthdate.data= booking.birthdate
        form.martial.data = booking.martial
        form.nationality.data= booking.nationality
        form.email.data = booking.email
        form.phone.data = booking.phone
        form.original_address.data = booking.original_address
        form.original_city.data= booking.original_city
        form.original_state.data= booking.original_state
        form.original_zip.data= booking.original_zip
        form.original_country.data  = booking.original_country
        if form.validate_on_submit():
            phone =  request.form["phone"]
            if phone[0] == "+":
                booking.fullname= request.form["fullname"]
                booking.surname= request.form["surname"]
                booking.gender  = request.form["gender"] 
                booking.birthplace= request.form["birthplace"]
                date = datetime.strptime(request.form["birthdate"], '%m/%d/%Y').strftime('%Y-%m-%d') 
                booking.birthdate= date
                booking.martial = request.form["martial"]
                booking.nationality= request.form["nationality"]
                booking.email = request.form["email"]  
                booking.phone = request.form["phone"]
                booking.original_address = request.form["original_address"]
                booking.original_city= request.form["original_city"]
                booking.original_state= request.form["original_state"]
                booking.original_zip= request.form["original_zip"]
                booking.original_country  = request.form["original_country"]
                db.session.commit()     
                return redirect(url_for("StepThree",url=url))
            else:
                flash("Please use + country on whatsapp form","danger")
                                   
    return render_template("submission/steptwo.html",form=form,booking=booking,url=url)    


@app.route("/sub/step3/<url>",methods=["GET","POST"])
def StepThree(url):
    booking = Booking.query.filter_by(url=url).first()
    form = StepThreeForm()    
    if booking.emergency_name == None:
        if form.validate_on_submit():
            phone = form.emergency_phone.data
            if phone[0] == "+":
                booking.emergency_name = form.emergency_name.data 
                booking.emergency_status =  form.emergency_status.data
                booking.emergency_address =  form.emergency_address.data
                booking.emergency_city = form.emergency_city.data
                booking.emergency_state = form.emergency_state.data
                booking.emergency_zip =  form.emergency_zip.data
                booking.emergency_country =  form.emergency_country.data
                booking.emergency_email = form.emergency_email.data
                booking.emergency_phone =  form.emergency_phone.data
                db.session.commit()
                return redirect(url_for("StepFour",url=url))
            else:
                flash("Please use + country on whatsapp form","danger")    
    else:
        form.emergency_name.data  = booking.emergency_name
        form.emergency_status.data = booking.emergency_status
        form.emergency_address.data = booking.emergency_address
        form.emergency_city.data = booking.emergency_city
        form.emergency_state.data = booking.emergency_state
        form.emergency_zip.data = booking.emergency_zip
        form.emergency_country.data = booking.emergency_country
        form.emergency_email.data = booking.emergency_email
        form.emergency_phone.data = booking.emergency_phone        
        if form.validate_on_submit():
            phone = request.form["emergency_phone"]
            if phone[0] == "+":
                booking.emergency_name  = request.form["emergency_name"]
                booking.emergency_status = request.form["emergency_status"]
                booking.emergency_address = request.form["emergency_address"]
                booking.emergency_city = request.form["emergency_city"]
                booking.emergency_state = request.form["emergency_state"]
                booking.emergency_zip = request.form["emergency_zip"]
                booking.emergency_country = request.form["emergency_country"]
                booking.emergency_email = request.form["emergency_email"]
                booking.emergency_phone = request.form["emergency_phone"]
                db.session.commit()
                return redirect(url_for("StepFour",url=url))
            else:
                flash("Please use + country on whatsapp form","danger")       
                        
    return render_template("submission/stepthree.html",form=form,booking=booking,url=url)    


@app.route("/sub/step4/<url>",methods=["GET","POST"])
def StepFour(url):
    booking = Booking.query.filter_by(url=url).first()
    travel = TravelDocument.query.filter_by(traveldocumentowner_id=booking.id).first()
    form = StepFourForm() 
    if travel:
        form.tipe.data = travel.tipe
        form.document_number.data = travel.document_number
        form.place_issued.data = travel.place_issued
        form.date_issued.data = travel.date_issued        
        form.date_expired.data = travel.date_expired
        if form.validate_on_submit():
            expired = datetime.strptime(request.form["date_expired"], '%m/%d/%Y').strftime('%Y-%m-%d') 
            year = datetime.strptime(expired, "%Y-%m-%d")
            if year.year < 2023 :
                flash("Expired date must be longer than 2023","danger")
            else:    
                issued = datetime.strptime(request.form["date_issued"], '%m/%d/%Y').strftime('%Y-%m-%d') 
                travel.tipe = request.form["tipe"]
                travel.document_number = request.form["document_number"]
                travel.place_issued = request.form["place_issued"]
                travel.date_issued = issued
                travel.date_expired = expired
                db.session.commit()        
                return redirect(url_for("StepFive",url=url))

    else: 
        if form.validate_on_submit():
            expired = form.date_expired.data            
            if expired.year < 2023 :
                flash("Expired date must be longer than 2023","danger")
            else:    
                travel = TravelDocument(tipe=form.tipe.data,document_number=form.document_number.data,
                        place_issued=form.place_issued.data,date_issued=form.date_issued.data,date_expired=form.date_expired.data,
                        traveldocumentowner_id=booking.id)
                db.session.add(travel)
                db.session.commit()                           
                return redirect(url_for("StepFive",url=url))

    return render_template("submission/stepfour.html",form=form,booking=booking,url=url)  


@app.route("/sub/step5/<url>",methods=["GET","POST"])
def StepFive(url):
    booking = Booking.query.filter_by(url=url).first()
    all_document = Document.query.filter_by(documentowner_id=booking.id).all() 
    form = SubmitForm()
    if form.validate_on_submit():
        if booking.tipe == "social visa onshore":
            if len(all_document) == 3 :        
                booking.status = "complete order"
                db.session.commit()

                email = booking.email
                msg = Message("Bali Zero Invoice", sender="info@balizero.com", recipients=[email])

                link = url_for("InvoiceId", url=url, _external=True)
                msg.body = "Thank you for your order"
                msg.html = "<p>Hello  {},</p><p>We received your request, thank you.<br>We will check your documentation quickly and will make sure your process starts as soon as possible.<br>Important:<br>To be effective and in order to start your application process the payment has to be undertaken to our secure credit card/pay pal page at this invoice link {}<p></p>Once the payment is done will get back to you within the next 24hours, often quicker!<br>If you have any further questions please send an email to info@balizero.com</p><p>Thank you<br>Bali Zero Team<br>https://www.balizero.com</p>".format(booking.fullname,link)
                mail.send(msg)
                return redirect(url_for("InvoiceId",url=url))
            else:
                flash("Please complete your data","danger")  
                return redirect(url_for("StepFive",url=url))      
        else:
            if len(all_document) == 3 :        
                booking.status = "complete order"
                db.session.commit()

                email = booking.email
                msg = Message("Bali Zero Invoice", sender="info@balizero.com", recipients=[email])

                link = url_for("InvoiceId", url=url, _external=True)
                msg.body = "Thank you for your order"
                msg.html = "<p>Hello  {},</p><p>We received your request, thank you.<br>We will check your documentation quickly and will make sure your process starts as soon as possible.<br>Important:<br>To be effective and in order to start your application process the payment has to be undertaken to our secure credit card/pay pal page at this invoice link {}<p></p>Once the payment is done will get back to you within the next 24hours, often quicker!<br>If you have any further questions please send an email to info@balizero.com</p><p>Thank you<br>Bali Zero Team<br>https://www.balizero.com</p>".format(booking.fullname,link)
                mail.send(msg)
                
                return redirect(url_for("InvoiceId",url=url))
            else:
                flash("Please complete your data","danger")  
                return redirect(url_for("StepFive",url=url))      
                    
          
    return render_template("submission/stepfive.html",form=form,url=url,all_document=all_document,booking=booking,Document=Document)  


@app.route("/sub/step5/<url>/upload/<tipe>",methods=["GET","POST"])
def UploadDocument(url,tipe):
    booking = Booking.query.filter_by(url=url).first()
    all_document = Document.query.filter_by(documentowner_id=booking.id).all()   
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data       
        if allowed_file(file.filename): 
            upload = Document(documentowner_id=booking.id,tipe=tipe)              
            
            db.session.add(upload)
            db.session.commit()

            filename = str(upload.id) + secure_filename(file.filename) 
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],  filename))

            upload.filename = filename
            db.session.commit()
            return redirect(url_for("StepFive",url=url))
    return render_template("submission/upload.html",booking=booking,form=form,all_document=all_document,Document=Document)        


@app.route("/sub/step5/<url>/delete/<tipe>/<filename>",methods=["GET","POST"])
def DeleteDocument(url,tipe,filename):
    file = Document.query.filter_by(tipe=tipe,filename=filename).first_or_404()
    os.remove(os.path.join(app.config['UPLOADED_IMAGES_DEST'], file.filename))    
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for("StepFive",url=url))



@app.route("/sub/step6/<url>/finished",methods=["GET","POST"])
def CheckFinishedData(url):
    booking = Booking.query.filter_by(url=url).first()
    all_document = Document.query.filter_by(documentowner_id=booking.id).all()  
    if len(all_document) == 3 :
        booking.status = "complete order"
        db.session.commit()
        return redirect(url_for("InvoiceId",url=url))
    




@app.route("/sub/invoice/<url>",methods=["GET","POST"])
def InvoiceId(url):
    booking = Booking.query.filter_by(url=url).first()
    pricing = int(booking.pricing)
    return render_template("submission/invoice.html",booking=booking,pricing=pricing)




















































if __name__ == "__main__":
	#manager.run()
	app.jinja_env.cache = {}
	app.run(host='0.0.0.0',threaded=True)	






