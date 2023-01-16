#Golf handicap calculator
# Started 4/12/2022
# Nolan Jimmo

#filenames

from statistics import mean
import pymysql

# connecting to my aws RDS instance
db = pymysql.connect(host="database-1.cv79u4we1ktk.us-east-1.rds.amazonaws.com", user = "admin", password="Synergyfc18!", database="handicap_calc")
# cursor instance is here
cursor = db.cursor()

def add_user(username, password, name):
    # check to see if account name already exists
    cursor.execute(f"SELECT * FROM Credentials WHERE Username = '{username}'")
    account = cursor.fetchall()
    # if so, return false
    if len(account) != 0:
        return False
    # otherwise, add the new user to the database
    else:
        sql = """INSERT INTO Credentials (username, password, name)
                VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (username, password, name))
        db.commit()
        return True

def authenticate_user(username, password):
    cursor.execute(f"SELECT * FROM Credentials WHERE Username = '{username}'")
    account = cursor.fetchall()
    if len(account) == 0:
        return False
    else:
        if password == account[0][1]:
            return account[0][2]
        else:
            return False

def get_round_input(new_course=True):
    # new_course = Boolean
    # Get the gross score, course rating and course slope from user
    score = 0
    rating = 0
    slope = 0
    while True:
        score = int(input("Enter the gross score: "))
        if new_course:
            rating = float(input("Enter the course rating: "))
            slope = float(input("Enter the course slope: "))
            print(f"Score: {score} Rating: {rating}  Slope: {slope}")
        else:
            print(f"Score: {score}")
        cont = input("Is this info correct? (y/n)")
        if cont == 'y' and new_course == True:
            return score, rating, slope
        elif cont == 'y' and new_course == False:
            return score
        else:
            print("Re-enter round info")

def choose_option():
    # let the user choose what they want to do (enter from existing course or new one), or see their current handicap
    choice = 0
    while choice not in [1,2,3]:
        choice = int(input("Choose option (enter option #):\n1. Enter from old course\n2. Enter from new course\n3. Quit\n>> "))
    return choice

def get_courses():
    # read the saved courses file
    # return dictionary of course name: (rating, slope)
    course_dict = {}

    cursor.execute("SELECT * from Courses")
    courses = cursor.fetchall()
    for c in courses:
        course_dict[c[1]] = (c[2], c[3])
    return course_dict

def get_index(username):
    # read the list of index's as they have been stored

    cursor.execute(f"SELECT * from Ind WHERE username = '{username}'")
    ind = cursor.fetchall()[0][1]

    return ind

def choose_existing_course():
    # let the user choose from previously played courses
    # return the (rating, slope) tuple for that course
    course_dict = get_courses()
    print("Stored courses:")
    for n in course_dict.keys():
        print(n)
    
    choice = input("Type name of course you are entering a round at: ").lower()
    while choice not in course_dict.keys():
        choice = input("Course not in list, try again: ")

    return course_dict[choice]

def write_course_data(name, rating, slope):
    # insert new course in to Courses table
    # get indexes from courses table to add another
    cursor.execute("SELECT id from Courses")
    inds = cursor.fetchall()
    next_ind = max([i[0] for i in inds]) + 1

    sql = """ INSERT INTO Courses (id, name, rating, slope)
        VALUES (%s, %s, %s, %s)
        """
    cursor.execute(sql, (next_ind, name, float(rating), float(slope)))
    db.commit()

def write_differential_file(username, diff):
    # insert new differential in to Differentials table

    # get indexes from courses table to add another
    cursor.execute("SELECT id from Differentials")
    inds = cursor.fetchall()
    next_ind = max([i[0] for i in inds]) + 1

    sql = """ INSERT INTO Differentials (id, username, dif)
        VALUES (%s, %s, %s)
        """
    cursor.execute(sql, (next_ind, username, float(diff)))
    db.commit()

def write_index_file(username, index):
    # update row in Ind table to new index for the corresponding user

    sql = """ UPDATE Ind
              SET ind = %s
              WHERE username = %s
        """
    cursor.execute(sql, (float(index), username))
    db.commit()

def calculate_differential(score, rating, slope):
    # calculate the handicap differential for an entered round
    return round(((score - rating) * 113) / slope, 2)

def calculate_index(best_recent_diff_list):
    # calculate the handicap index for the golfer over their past x # of rounds
    return round(mean(best_recent_diff_list) * .96, 1)

def get_differentials(username):
    # read the differential history file
    # return the differential history as a list of at most 20 most recent diffs
    diff_list = []

    cursor.execute(f"SELECT * from Differentials WHERE username = '{username}'")
    difs = cursor.fetchall()
    for d in difs:
        diff_list.append(float(d[2]))

    if len(diff_list) > 20:
        diff_list = diff_list[20:]

    return diff_list

def main():
    handi = get_index()
    if len(handi) != 0:
        print(f"Current handicap: {handi[-1]}")
    choice = choose_option()
    while choice != 3:
        # first, get the golfer score, the course rating and the course slope
        if choice == 1:
            # user wants to enter a new round from a course they have already played
            tup = choose_existing_course()
            score = get_round_input(False)
            rating = float(tup[0])
            slope = float(tup[1])
        else:
            # user wants to enter a new round from a course they have not played before
            name = input("Course name (name (tee color)): ")
            score, rating, slope = get_round_input()
            write_course_data(name, rating, slope)
        
        # second, we have to calculate the differential for this round and then calculate the index with this newest score
        index = -1

        diff = calculate_differential(score, rating, slope)
        diff_list = get_differentials()
        diff_list.append(diff)
        most_recent = []
        if len(diff_list) < 10:
            print(f"You have {len(diff_list)} entered, you need atleast 10 to compute a handicap")
            print("This current round will be stored for future handicap")
        elif len(diff_list) < 15:
            most_recent = diff_list[-3:]
            index = calculate_index(most_recent)
        elif len(diff_list) < 20:
            most_recent = diff_list[-6:]
            index = calculate_index(most_recent)
        else:
            most_recent = diff_list[-20:]
            most_recent.sort()
            most_recent = most_recent[-10:]
            index = calculate_index(most_recent)

        # store the new differential in the differentials file
        write_differential_file(diff)

        # if the index was able to be calculated (index is not -1, which it is intialized to)
        if index != -1:
            print(f"Handicap Index: {index}")
            #Write to index file
            write_index_file(index)

        choice = choose_option()
     
    print("Thank you!")


#main()
