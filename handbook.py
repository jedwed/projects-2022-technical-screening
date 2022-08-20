"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: We do not expect you to come up with a perfect solution. We are more interested
in how you would approach a problem like this.
"""
import json
import re

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()

def is_unlocked(courses_list, target_course):
    """
    Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    manually_fix_conditions()
    return validate_conditions(courses_list, parse_conditions(CONDITIONS[target_course]))

def manually_fix_conditions():
    """
    Manually review the course conditions and morph dumb ones into a processable format

    This should be applied sparingly so that it don't just straight up rewrite the handbook
    """

    # If only the digits of a course code is given, 
    # manually resolve it so it can be processed without ambiguity
    if "COMP" not in CONDITIONS["COMP4952"]:
        CONDITIONS["COMP4952"] = 'COMP4952'
    if "COMP" not in CONDITIONS["COMP4953"]:
        CONDITIONS["COMP4953"] = 'COMP4953'
    CONDITIONS["COMP9491"] = re.sub("units oc credit", "units of credit", CONDITIONS["COMP9491"])
    
def parse_conditions(condition_string):
    # Replace multiple spaces with single space
    condition_string = re.sub(r' +', r' ', condition_string)
    # Remove redundant 'prerequisite' text at beginning
    condition_string = re.sub(r'^[Pp]re[A-Za-z-]*:*\s?', r'', condition_string)
    return condition_string

    # TODO: UOC checking
    uoc_regex = r'([0-9]{1,3}) units o[fc] credit (?:in)? (level \d \w{4} courses|([^)]+))'

def validate_conditions(courses_list, conditions):
    if re.fullmatch(r'\w{4}\d{4}', conditions):
        return conditions in courses_list

print(is_unlocked(["COMP3411", "COMP1511"], "COMP4418"))
