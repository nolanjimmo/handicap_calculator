
import handicap_calc as HC
from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)

 
 
@app.route('/', methods=['POST', 'GET'])
def index():
    global instance_username
    global instance_name
    global instance_ind
    
    if request.method == 'POST':
        if request.form.get("return_home"):
            return render_template("splash.html", name=instance_name, index=instance_ind)
        else:
            # here we can check if the username for the login page is valid and then decide what to
            # do from there (authenticate or not)
            username = request.form['nm']
            password = request.form['pw']
            auth = HC.authenticate_user(username, password)
            if auth != False:
                instance_username = username
                instance_name = auth
                # TODO: make this part redirect to the account splash page
                ind = HC.get_index(instance_username)
                instance_ind = ind
                return render_template("splash.html", name = auth, index = ind)
            else:
                # use fail=True to trigger the error message in template
                return render_template("login.html", fail=True)
    else:
        return render_template("login.html")

@app.route('/splash', methods=['POST'])
def splash():
    if request.form['submit_button'] == "new course":
        # go to the page for enterting score at a new course
        return render_template("enter_new.html", fail=None)
    else:
        # go to the page for entering score at a stored course
        return "Enter old course"

@app.route('/new_course', methods=['POST'])
def new_course():
    try:
        course_name = str(request.form["course_name"])
        score = int(request.form["score"])
        rating = float(request.form["rating"])
        slope = float(request.form["slope"])
    except:
        return render_template("enter_new.html", fail=True)

    if course_name != "" and score != "" and rating != "" and slope != "":
        return render_template("enter_new.html", fail=False)
    
    else:
        return render_template("enter_new.html", fail=True)
 
 
if __name__ == '__main__':
    app.run(debug=True)