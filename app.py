
import handicap_calc as HC
from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)

instance_username = None
 
 
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # here we can check if the username for the login page is valid and then decide what to
        # do from there (authenticate or not)
        username = request.form['nm']
        password = request.form['pw']
        auth = HC.authenticate_user(username, password)
        if auth != False:
            instance_username = username
            # TODO: make this part redirect to the account splash page
            return f'Hello {auth}, welcome to the system!'
        else:
            # use fail=True to trigger the error message in template
            return render_template("login.html", fail=True)
    else:
        return render_template("login.html")
 
 
if __name__ == '__main__':
    app.run(debug=True)