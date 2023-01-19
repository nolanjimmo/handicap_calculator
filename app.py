
import handicap_calc as HC
from flask import Flask, redirect, url_for, request, render_template
app = Flask(__name__)

def calculate_values(score, rating, slope):
    index = -1

    diff = HC.calculate_differential(score, rating, slope)
    diff_list = HC.get_differentials(instance_username)
    diff_list.append(diff)
    most_recent = []
    if len(diff_list) < 10:
        print(f"You have {len(diff_list)} entered, you need atleast 10 to compute a handicap")
        print("This current round will be stored for future handicap")
    elif len(diff_list) < 15:
        most_recent = diff_list[-3:]
        index = HC.calculate_index(most_recent)
    elif len(diff_list) < 20:
        most_recent = diff_list[-6:]
        index = HC.calculate_index(most_recent)
    else:
        most_recent = diff_list[-20:]
        most_recent.sort()
        most_recent = most_recent[-10:]
        index = HC.calculate_index(most_recent)

    # store the new differential in the differentials file
    HC.write_differential_file(instance_username, diff)

    # if the index was able to be calculated (index is not -1, which it is intialized to)
    if index != -1:
        print(f"Handicap Index: {index}")
        #Write to index file
        HC.write_index_file(instance_username, index)
 
 
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

@app.route('/splash', methods=['POST', 'GET'])
def splash():
    try:
        if request.form['submit_button'] == "Enter score from new course":
            # go to the page for enterting score at a new course
            return render_template("enter_new.html", fail=None, name=instance_name)
        else:
            # go to the page for entering score at a stored course
            courses = list(HC.get_courses().keys())
            return render_template("existing.html", courses=courses, fail=None, name=instance_name)
    except:
        return render_template("splash.html", name=instance_name, index=instance_ind)

@app.route('/new_course', methods=['POST'])
def new_course():
    try:
        course_name = str(request.form["course_name"])
        score = int(request.form["score"])
        rating = float(request.form["rating"])
        slope = float(request.form["slope"])
    except:
        return render_template("enter_new.html", fail=True, name=instance_name)

    if course_name != "" and score != "" and rating != "" and slope != "":
        # add the actual data to the database and user differentials/index table
        HC.write_course_data(course_name, rating, slope)

        # second, we have to calculate the differential for this round and then calculate the index with this newest score
        calculate_values(score, rating, slope)
        
        return render_template("enter_new.html", fail=False, name=instance_name)
    
    else:
        return render_template("enter_new.html", fail=True, name=instance_name)

@app.route('/old_course', methods=["POST"])
def old_course():
    # first, get the courses we have saved in the database
    courses = HC.get_courses()
    #then we'll use the input from the radio buttons as the key for that dict
    try:
        course_name = request.form["course"]
        score = int(request.form["score"])
        course_data = courses[course_name]
        print(course_data)
        calculate_values(score, course_data[0], course_data[1])
        return render_template("existing.html", fail=False, name=instance_name)

    except:
        return render_template("existing.html", fail=True, name=instance_name)
 
 
if __name__ == '__main__':
    app.run(debug=True)