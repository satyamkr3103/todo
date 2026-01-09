import os
from flask import Flask , render_template , request ,redirect # type: ignore
from flask_sqlalchemy import SQLAlchemy # pyright: ignore[reportMissingImports]
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,template_folder=os.path.join(BASE_DIR,"templates"))
app.config['SQLALCHEMY_DATABASE_URI']=f"sqlite:///{os.path.join(BASE_DIR,'todo.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY","fallback-secret")
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(200),nullable = False)
    desc = db.Column(db.String(500),nullable = False)
    date_created = db.Column(db.DateTime,default = datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

with app.app_context():
    db.create_all()
@app.route('/health')
def health():
    return 'Healthy'
@app.route('/', methods =['GET','POST'])
def hello_world():
    if request.method=='POST':
        title = request.form.get('title')
        desc = request.form.get('desc')

        if title and desc:
            todo = Todo(title=title,desc = desc) # type: ignore
            db.session.add(todo)
            db.session.commit()

    allTodo = Todo.query.all()
    return render_template('index.html',allTodo=allTodo)
    # return 'hello,world!'

@app.route('/show')
def products():
    allTodo = Todo.query.all()
    print(allTodo)
    return 'this is the product page'

@app.route('/delete<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()

    if not todo:
        return redirect('/')
    
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:sno>',methods=['GET','POST'])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if request.method == 'POST':
        title = request.form.get('title')
        desc = request.form.get('desc')

        if title and desc:
            todo.title = title # type: ignore
            todo.desc = desc # type: ignore
            db.session.add(todo)
            db.session.commit()
            return redirect('/')
    
    return render_template('update.html',todo=todo)

@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404
