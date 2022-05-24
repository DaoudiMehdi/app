
from datetime import date, datetime
from operator import length_hint 

from email.policy import default
from tarfile import NUL
from unicodedata import name
from bs4 import BeautifulSoup
from flask import Flask , render_template ,request ,redirect , url_for , flash
from flask_sqlalchemy import SQLAlchemy
import requests
from sqlalchemy import null
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import uuid as uuid
import os

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myproject.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://urnucmegjcinja:4968a405a29ceaab862834c567d54523e91030e324614d81c322b4d7f47bad87@ec2-3-228-235-79.compute-1.amazonaws.com:5432/d1l23q92v7uqk0'

app.config['SECRET_KEY'] = 'letithappenletithappen321'


UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255) ,nullable=False )
    content = db.Column(db.Text, nullable=False)
    author =db.Column(db.String(200) , nullable=False)
    profile_pict=db.Column(db.String(),nullable=True)
    pict = db.Column(db.String(),nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    def __init__(self ,title, content , author,profie_pict, pict  ):
        self.title= title
        self.content=content
        self.author=author
        self.profile_pict=profie_pict
        self.pict=pict 






class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200) , unique=True,nullable=False )
    name = db.Column(db.String(200) , nullable=False)
    password =db.Column(db.String(200) , nullable=False)
    tlf = db.Column(db.Integer , nullable=False)
    profile_pict=db.Column(db.String(),nullable=True)
    

    def __repr__(self):
        return '<Name %r>' % self.name
    def __init__(self , username, name , password, tlf,profile_pict):
        self.username= username
        self.name=name
        self.password=password
        self.tlf=tlf
  
@login_manager.user_loader
def load_user(username):
    return users.query.get((username))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
@app.errorhandler(505)
def page_not_found(e):
    return render_template('505.html'), 505


@app.route('/')
def index(): 
    posts_picts=[]
    #posts=post.query.all()
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)
    for poste in all_post :
        if poste.pict != "null":
            posts_picts.append(poste)
    #n=post.query.order_by(post.date_posted).count()


    #web_scraping :men.gov.ma
    mylist =[]
    source = requests.get("https://www.men.gov.ma/Ar/Pages/Accueil.aspx" ).text
    soup = BeautifulSoup(source , 'html.parser')

    content = soup.find('div' , id="content-2")
    rows=content.find_all('ul')

    for row in rows:
        date = row.find('span' , class_="date noindex").text
        title=row.find('a').text
        id = row.find('a')['href']
        lien= "https://www.men.gov.ma/"+str(id)
        data = {
            "title": title ,
            "date" : date ,
            "lien" : lien ,    }

            
        mylist.append(data)
    if len(mylist )>7:
       mylist= mylist[:6]
    else :  mylist= mylist[:]




    return render_template("main.html" ,all_post=all_post, posts=posts , n=n, posts_picts=posts_picts ,mylist=mylist)

@app.route('/contact')
def contact():
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)

    return render_template("contact.html", posts=posts , n=n)

@app.route('/blog')
@login_required
def blog():
    posts_picts=[]
    #posts=post.query.all()
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)
    return render_template('blog.html' , posts=posts , n=n)



@app.route('/send', methods = ['POST', 'GET'])
def send():
    if request.method == 'POST':
        author = current_user.name
        profile_pict=current_user.profile_pict
        title = request.form['title']
        content = request.form['body']
        pict = request.files['file']
        print(pict)
        if request.files['file']:
            pic_filename = secure_filename(pict.filename)

            pic_name =str(uuid.uuid1())+ "_" + pic_filename

            saver= request.files['file']

            pict= pic_name
                
            blogs = post(title , content ,author ,profile_pict, pict)
            db.session.add(blogs)
            try :
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))

                flash("تم نشر المقال بنجاح")
                return redirect(url_for('index'))
                

            
            except Exception as e:
                print(e)
                db.session.rollback()
                flash("لم ينشر المقال")
                return redirect(url_for('index'))
                    

            
        else:
            blogs = post(title=title , content=content ,author=author,profie_pict=profile_pict , pict="null")
            db.session.add(blogs)
            try :
                db.session.commit()
                flash("تم نشر المقال بنجاح")
                return redirect(url_for('index'))
                

            
            except Exception as e:
                print(e)
                db.session.rollback()
                flash("لم ينشر المقال")
                return redirect(url_for('index'))
    
                    
class contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50) ,nullable=False )
    pnom = db.Column(db.String(50) ,nullable=False )
    mail = db.Column(db.String(150) ,nullable=False )
    content = db.Column(db.Text, nullable=False)
    tlf = db.Column(db.Integer , nullable=False)
    
    

    def __init__(self ,nom, pnom , mail,content, tlf  ):
        self.nom= nom
        self.pnom=pnom
        self.mail=mail
        self.content=content
        self.tlf=tlf 

                      

@app.route('/send2', methods = ['POST', 'GET'])
def send2():
    if request.method == 'POST':
        nom = request.form['nom']
        pnom = request.form['pnom']
        mail = request.form['mail']
        tlf = request.form['tlf']
        content = request.form['content']
        contact_msg =contacts(nom , pnom , mail ,content, tlf)
        db.session.add(contact_msg)
        try :
            db.session.commit()
            flash(" تم ارسال الرسالة بنجاح")
            return redirect(url_for('index'))
                    

                
        except Exception as e:
            print(e)
            db.session.rollback()
            flash("لم ترسل الرسالة")
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
                    


@app.route('/contact_msg')
@login_required
def contact_msg():
        posts = post.query.all()
        all_post=posts
        all_post=all_post[::-1]
        n=length_hint(posts)
        if n >6:
            posts=posts[length_hint(posts)-5:n:1]
            n=length_hint(posts)
        else:
            posts=posts[:n:1]
            n=length_hint(posts)
        contact_msg= contacts.query.all()
        if current_user.username=='admin':
            return render_template("contact_msg.html", contact_msg=contact_msg , n=n , posts=posts)
        else:
             render_template('404.html')


        
        

    

           

        


#sign_up
@app.route('/useradd', methods = ['GET', 'POST'])
def useradd():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        tlf = request.form['tlf']
        profile_pict = request.files['file']
        if request.files['file']:
             profile_pict_filename = secure_filename(profile_pict.filename)

             pic_name =str(uuid.uuid1())+ "_" + profile_pict_filename

             saver= request.files['file']

             profile_pict = pic_name
             
             user = users(username , name ,password , tlf ,profile_pict)
             db.session.add(user)
             try :
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))

                login_user(user, remember=True)
                return redirect(url_for('index'))
                

                
             except:
                db.session.rollback()
                flash("اسم المستخدم او الهاتف مستعملان سابقا")
                return redirect(url_for('index'))
        else :

            user = users(username , name ,password , tlf ,profile_pict="null")
            db.session.add(user)
            try :
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('index'))
                

                
            except:
                db.session.rollback()
                flash("اسم المستخدم او الهاتف مستعملان سابقا")
                return redirect(url_for('index'))
            
    else:
        return redirect(url_for('index'))



@app.route('/user')
@login_required
def user(): 
        #posts=post.query.all()
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)
    user_data= users.query.all()
    if current_user.username=='admin':
        return render_template("user.html", mydata=user_data , n=n , posts=posts)
    else:
        render_template('404.html')

        

@app.route('/blogs')
@login_required
def blogs(): 
        #posts=post.query.all()
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)
    if current_user.username=='admin':
        return render_template("blogs.html", all_post=all_post , n=n , posts=posts)
    else:
        redirect(url_for('404.html'))
@app.route('/info')
@login_required
def info(): 
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)
    
    return render_template("info.html", all_post=all_post , n=n , posts=posts)



@app.route('/modifier', methods = ['GET', 'POST'])
def modifier():
    if request.method == "POST":
        data = users.query.get(request.form.get('id'))
        data.username = request.form['username']
        data.name = request.form['name']
        data.password = request.form['password']
        data.tlf = request.form['tlf']
        try :
            db.session.commit()
            flash("تم تغيير معلومات المستخدم")

            
        except:
            db.session.rollback()
            flash("لم يتم تغيير معلومات المستخدم")
        return redirect(url_for('user'))
@app.route('/supprimer/<id>/', methods = ['GET', 'POST'])
@login_required
def supprimer(id):
    if current_user.username=='admin':
        data = users.query.get(id)
        db.session.delete(data)
        db.session.commit()
        flash("تم حذف المستخدم")
        return redirect(url_for('user'))
    else:
        render_template('404.html')

@app.route('/del/<id>/', methods = ['GET', 'POST'])
@login_required
def del_(id):
    if current_user.username=='admin':
        data= post.query.get(id)
        db.session.delete(data)
        db.session.commit()
        flash("تم حدف المقال")
        return redirect(url_for('blogs'))
    else:
        redirect(url_for('404.html'))
@app.route('/del2/<id>/', methods = ['GET', 'POST'])
@login_required
def del_2(id):
    if current_user.username=='admin':
        data= contacts.query.get(id)
        db.session.delete(data)
        db.session.commit()
        flash("تم حدف الرسالة")
        return redirect(url_for('contact_msg'))
    else:
        redirect(url_for('404.html'))
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user=users.query.filter_by(username = request.form['username_l']).first()
        if user:
            if user.password== request.form['password_l']:
                login_user(user, remember=True)
                return redirect(url_for('index'))
            flash("اسم المستخدم او الهاتف مستعملان سابقا")
            return redirect(url_for('index'))
        flash("اسم المستخدم او الهاتف مستعملان سابقا")
        return redirect(url_for('index'))
        
    else :
        return redirect(url_for('index'))



@app.route('/user_dash')
@login_required
def user_dash():
        #posts=post.query.all()
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)
    return render_template("user_dash.html" ,name=current_user.username, n=n ,posts=posts)
    
@app.route('/user_mod/<int:id>', methods = ['GET', 'POST'])
@login_required
def user_mod(id):
    id=current_user.id
    if request.method == "POST":
        data = users.query.get_or_404(id)
        data.username = request.form['username']
        data.name = request.form['name']
        data.password = request.form['password']
        data.tlf = request.form['tlf']
        try :
            db.session.commit()
            flash("تم تغيير معلومات المستخدم")

            
        except:
            db.session.rollback()
            flash("لم يتم تغيير معلومات المستخدم")
        return render_template("user_dash.html")



@app.route('/posts/<int:id>')
def posts(id):
    data_post = post.query.get_or_404(id)
    posts = post.query.all()
    all_post=posts
    all_post=all_post[::-1]
    n=length_hint(posts)
    if n >6:
        posts=posts[length_hint(posts)-5:n:1]
        n=length_hint(posts)
    else:
        posts=posts[:n:1]
        n=length_hint(posts)
    return render_template('posts.html', data_post=data_post,posts=posts, n=n)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

       
if __name__ == '__main__':
    app.run(port=50, debug=True)