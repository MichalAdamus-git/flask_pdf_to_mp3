from flask import Flask, render_template, redirect, url_for, flash, send_file, request, template_rendered, after_this_request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, URL
from forms import upload_form
from pypdf import PdfReader
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, LargeBinary, Boolean
from io import BytesIO
import gtts
import threading
from math import inf
from time import sleep


converting_finished = threading.Event()

app = Flask(__name__)
class Base(DeclarativeBase):
    pass


##### For flask forms create secret key
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SERVER_NAME'] = 'localhost:5000'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class File(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String, nullable=False)
    downloaded: Mapped[bool] = mapped_column(Boolean, insert_default=False)
    voice: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)


with app.app_context():
    db.create_all()

global converting
converting = False

global converted
converted = False

global ready
ready = False
def convert_pdf(path, name):
    file = open(path, 'rb+')
    reader = PdfReader(file)
    global converting
    converting = True
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    with app.app_context():
        global db_file
        db_file = File(filename=name, text=text)
        db.session.add(db_file)
        db.session.commit()
        convert_to_mp3(db_file,'./static/file.mp3')
        file_result = db.session.execute(db.select(File).where(File.text == text))
        global file_converted
        file_converted = file_result.scalar()
        global converted
        converted = True
        while True:
            if ready == True:
                sleep(10)
                print('helo')
                ## send event
                break
        converting_finished.set()

def convert_to_mp3(input, path):
    contents = input.text
    tts = gtts.gTTS(text=contents)
    fp = open(path, 'a+')
    tts.save(path)
    #   managed to solve problems with gtts. Now sql File class wants voice to be mapped bytes not string so need
    #   to choose one.
    with open(path, 'rb') as fp:
            input.voice = fp.read()
            fp.close()
            db.session.commit()

def get_template_loading(template_name):
    converter.start()
    return render_template(template_name)




@app.route('/', methods=['GET', 'POST'])
def home():
    query = db.session.execute(db.select(File))
    files = query.scalars()
    for i in files:
        db_query = db.get_or_404(File, i.id)
        if db_query.downloaded == True:
            def clean(response):
                result = db.session.execute(db.select(File).where(File.filename==file_input.filename.data))
                db.session.delete(result)
            clean(response)
    file_input = upload_form()
    if file_input.validate_on_submit():
        to_file = './static/pdf_file.pdf'
        pdf_file_serv = request.files['file']
        content = pdf_file_serv.read()
        with open(to_file, 'wb+') as pdf_file:
            pdf_file.write(content)
        file_name = file_input.filename.data
        global converter
        converter = threading.Thread(target=convert_pdf, args=(to_file,file_name,))
        get_template_loading('loading.html')
        global ready
        ready = True
        return redirect(url_for('loading'))
    return render_template('index.html', form=file_input)

@app.route('/loading')
def loading():
    while True:
        if not converting_finished.is_set():
            pass
        else:
            break
    return redirect(url_for('download_interface', file_id=file_converted.id))


@app.route('/download_interface/<int:file_id>')
def download_interface(file_id):
    return render_template('interface.html', file_id=file_id)


@app.route('/files/<int:file_id>')
def download(file_id):
    result = db.get_or_404(File, file_id)
    result.downloaded = True
    '''
    @after_this_request
    def clean(response):
        db.session.delete(result)
        return redirect(url_for('home'))
    '''
    return send_file(BytesIO(result.voice), as_attachment=True, download_name='converted_voice_file.mp3')

# send sihnal after loading template was rendered. Send signal top the joining function. which
# waits for event from converter thread.



if __name__ == '__main__':
    app.run()





"""
Clearly generates voice files bas3ed on filenames from db not from file 
content which is grave mistake. 

Neeed another thread which redirects to some very basic converting html template. 


Write another thread for pdf to text conversion

I need to add file to db with one function and process 

Recive file from user. Store in db. Process it after request, which means
after the processing template was returned. 

Need to simply rteturn some gibberish goofiness before file ends being processed. 
A functionm not taking arguments which after joining threads routes to something less
giberish. 




Mate - You just add the form to the session.
Than you return some no argument gibberish processing template after uploading the form. 
after that you start the thread and after it dies you return a proper function 
with downlaod option. 

Use while is alive to render bullshit on gibberish page and
after it dies 

How bout using after this request on gibbersh templ;ate. Well technically it should work. 
See the thing is that i need to return stuff on a template  before processing. 

Why don't i render a template 

and run a function in the other thread. And than redirect 
to some sane place after the threads join.


Need to adjust databse object now it doesn't work\




Last chance. 

somwhere in main code. Set evemt made by converting function. 
when event sets off proceeed to redirect  ,. If global main thread would wait
for a signal from the other thread than we could run a waiting thread in  a function?????
a mo

event passed also to thread

def converter():
    while event_is_set()
        run converter
        event.clear()
    
        




"""