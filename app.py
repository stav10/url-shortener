from flask import Flask, render_template, url_for, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random
import string
import validators


SQLALCHEMY_TRACK_MODIFICATIONS= False



KEY_LENGTH = 5




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


def fix_url(url):
    if "https://" in url:
        return url.replace("https://", "http://")

    elif "http://" in url:
        return url

    else:
        return "http://"+url


def validate_url(url, host):
    if url and host not in url:
        url = url.replace("http://", "")
        if "/" in url:
            url = url.split("/")
            name = url[0]
            name = "http://" + name
            valid = validators.url(name)
            if valid:
                return True
        else:
            url = "http://"+url
            valid = validators.url(url)
            if valid:
                return True
    return False


def random_key():
    letter_list = [letter for letter in string.ascii_letters]
    letter_list += [letter for letter in string.digits]
    key = ""
    for i in range(0, KEY_LENGTH):
        key += letter_list[random.randint(0, len(letter_list) - 1)]
    return key

def validate_key(keys):
    key = random_key()
    if key not in keys:
        return key
    else:
        validate_key(keys)



random_key()
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(KEY_LENGTH))
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        keys = [url.key for url in URL.query.all()]
        key = validate_key(keys)
        input_url = request.form['content']
        input_url = fix_url(input_url)
        check_existens = URL.query.filter_by(content=input_url).first()

        if validate_url(input_url, request.host):
            if check_existens is None:
                new_url = URL(content=input_url, key=key)
                try:
                    db.session.add(new_url)
                    db.session.commit()
                    return render_template('success.html', host=request.host, key=key, url=input_url)
                except:
                    return "there was an error"
            else:
                return render_template('success.html', host=request.host, key=check_existens.key, url=input_url)
        else:
            return "invalid url"
    else:

        return render_template("index.html")







@app.route('/<string:key>')
def find_url(key):
    url = URL.query.filter_by(key=str(key)).first()

    try:
        return redirect(url.content, code=302)
    except:
        abort(404)




if __name__ == "__main__":
    app.run(debug=True)