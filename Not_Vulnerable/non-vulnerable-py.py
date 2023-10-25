from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import subprocess
import os

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://hatice:ataturk@172.17.0.2:5432/sql_injection"
db = SQLAlchemy(app)

class SQL_INJECTION(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Text, nullable=False)

    def __str__(self) -> str:
        return f"{self.id} {self.value}"

    def to_dict(self):
        return {"id": self.id, "value": self.value}

def xss_function(param1):
    return param1

def sql_function(param2):
    if param2:
        sql_function = SQL_INJECTION(value=param2)
        db.session.add(sql_function)
        db.session.commit()
        try:
            query = "SELECT * FROM sql_injection WHERE id = :param" #Yer tutucu
            result = db.session.execute(text(query), {"param": param2}).fetchall()
            db.session.commit()
            return result
        except Exception as e:
            pass
    return None
    
def command_function(param3):
    try:
        cmd = ['ping', '-c', '1', param3]
        result = subprocess.check_output(cmd, shell=False).decode("utf-8")
        return result
    except Exception as e:
        return "Ping is not success: " + param3

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        param1 = request.form['param1']
        param2 = request.form['param2']
        param3 = request.form['param3']

        if param1:
            result = xss_function(param1)
        elif param2:
            result = sql_function(param2)
        elif param3:
            result = command_function(param3)

    return render_template('non-vulnerable-html.html', result=result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

