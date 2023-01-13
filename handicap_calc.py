#Golf handicap calculator
# Started 4/12/2022
# Nolan Jimmo

#filenames

from statistics import mean


COURSE_DATA = "course_data.txt"
DIFF_DATA = "differentials.txt"
INDEX_DATA = "index.txt"


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

def read_course_file():
    # read the saved courses file
    # return dictionary of course name: (rating, slope)
    course_dict = {}
    with open(COURSE_DATA) as infile:
        for line in infile:
            if line != '':
                line = line.strip('\n')
                data = line.split(":")
                name = data[0]
                rating = data[1].split(",")[0]
                slope = data[1].split(",")[1]
                course_dict[name] = (rating, slope)
    return course_dict

def choose_existing_course():
    # let the user choose from previously played courses
    # return the (rating, slope) tuple for that course
    course_dict = read_course_file()
    print("Stored courses:")
    for n in course_dict.keys():
        print(n)
    
    choice = input("Type name of course you are entering a round at: ").lower()
    while choice not in course_dict.keys():
        choice = input("Course not in list, try again: ")

    return course_dict[choice]

def write_course_data(name, rating, slope):
    # write newly played course data to course data file
    with open(COURSE_DATA, 'a') as outfile:
        outfile.write(f"{name}:{rating},{slope}\n")

def calculate_differential(score, rating, slope):
    # calculate the handicap differential for an entered round
    return round(((score - rating) * 113) / slope, 2)

def calculate_index(best_recent_diff_list):
    # calculate the handicap index for the golfer over their past x # of rounds
    return round(mean(best_recent_diff_list) * .96, 1)

def write_differential_file(diff):
    # keep track of history of differentials by writing them to a file
    with open(DIFF_DATA, 'a') as outfile:
        outfile.write(f"{diff}\n")

def read_differential_file():
    # read the differential history file
    # return the differential history as a list of at most 20 most recent diffs
    diff_list = []
    i = 0
    with open(DIFF_DATA) as infile:
        for line in infile:
            if i == 20:
                return diff_list
            elif line != '':
                line = line.strip('\n')
                diff_list.append(float(line))
    return diff_list

def read_index_file():
    # read the list of index's as they have been stored
    indexs = []
    with open(INDEX_DATA) as infile:
        for line in infile:
            if line != '':
                indexs.append(line.strip('\n'))
    return indexs

def write_index_file(index):
    with open(INDEX_DATA, 'a') as outfile:
        outfile.write(f"{index}\n")

def main():
    handi = read_index_file()
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
        diff_list = read_differential_file()
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


main()
