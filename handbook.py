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
    return validate_conditions(courses_list, tokenize_conditions(CONDITIONS[target_course]), target_course)

    
def tokenize_conditions(condition_string):
    """
    Filter a condition string from the handbook into a list of tokens that can be processed
    """
    # Replace multiple spaces with single space
    condition_string = re.sub(r' +', r' ', condition_string)
    # Remove redundant 'prerequisite' text at beginning
    condition_string = re.sub(r'^[Pp]re[A-Za-z-]*:*\s?', r'', condition_string)
    # Remove redundant 'completion of': this implies UOC condition
    condition_string = re.sub(r'[Cc]ompletion of ', r'', condition_string)
    # Separating brackets with space so they tokenize
    condition_string = re.sub(r'\(', r'( ', condition_string)
    condition_string = re.sub(r'\)', r' )', condition_string)

    # UOC checking
    # Commas are irrelevant
    condition_string = re.sub(r',', r'', condition_string)
    # Level + course code requirements
    condition_string = re.sub(r'level (\d) (\w{4}) courses', r'L\1_\2', condition_string)
    # Course code requirements
    condition_string = re.sub(r'(\w{4}) courses', r'\1', condition_string)
    condition_string = re.sub(r'([0-9]{1,3}) units o[fc] credit in ([^\s])', r'\1_UOC_in \2', condition_string)
    condition_string = re.sub(r'([0-9]{1,3}) units o[fc] credit in \((.*?)\)', r'\1_UOC_in \2', condition_string)
    # UOC requirement with additional restrictions
    condition_string = re.sub(r'([0-9]{1,3}) units o[fc] credit', r'\1_UOC', condition_string)
    # Split the string into tokens
    return condition_string.split()

def validate_conditions(courses_list, conditions, target_course):
    """
    Given condition tokens, validate the conditions recursively
    """
    # If no conditions, trivial
    if conditions == []:
        return True
    # The index to jump to after evaluating current command
    next_idx = 1
    if conditions[0] == '(':
        to_idx = find_closing_bracket(conditions)
        next_idx = to_idx + 1
        current_condition = validate_conditions(courses_list, conditions[1:to_idx], target_course)
    elif "UOC" in conditions[0]:
        # If UOC is in the course code gg
        uoc_tokens = conditions[0].split('_')
        uoc_required = int(uoc_tokens[0])
        if len(uoc_tokens) == 3:
            # If the string is {num}_UOC_in
            if conditions[1] == '(':
                to_idx = find_closing_bracket(conditions[1:]) + 1
                next_idx = to_idx + 1
                current_condition = validate_uoc_req_list(courses_list, uoc_required, conditions[2:to_idx])
            else:   
                current_condition = validate_uoc_req(courses_list, uoc_required, conditions[1])
                next_idx = 2
        else:
            # UOC requirement without any additional restrictions
            current_condition = len(courses_list) * 6 >= uoc_required
    else:
        # The following line is for cases like COMP495[23]
        if re.fullmatch(r'\d{4}', conditions[0]):
            conditions[0] = target_course[:4] + conditions[0]
        current_condition = conditions[0] in courses_list

    # Base case: if there are no more conditions to evaluate
    if len(conditions) == next_idx:
        return current_condition
    if re.fullmatch(r'and', conditions[next_idx], flags=re.I):
        return current_condition and validate_conditions(courses_list, conditions[next_idx + 1:], target_course)
    elif re.fullmatch(r'or', conditions[next_idx], flags=re.I):
        return current_condition or validate_conditions(courses_list, conditions[next_idx + 1:], target_course)

    # If we reach this point it's doomed gg
    return False

def find_closing_bracket(conditions):
    """
    Given a list starting with an opening bracket, find index of corresponding closing bracket
    """
    unclosed_counter = 0
    for i, token in enumerate(conditions):
        if token == '(':
            unclosed_counter += 1
        if token == ')':
            unclosed_counter -= 1
        if unclosed_counter == 0:
            return i

    # This return statement is solely for decorative purposes
    return -1

def validate_uoc_req(courses_list, uoc_required, courses_required):
    """
    Check the number of UOC in certain courses with level and course code restrictions satisfies the requirement
    """
    total_uoc_met = 0
    if re.fullmatch(r'\w{4}', courses_required):
        for course in courses_list:
            if re.search(rf'^{courses_required}', course):
                total_uoc_met += 6
    elif re.search(r'L(\d)_(\w{4})', courses_required):
        # Determind wtf the courses string is actually saying
        level, course_code = re.search(r'L(\d)_(\w{4})', courses_required).groups()
        for course in courses_list:
            if re.search(rf'^{course_code}{level}', course):
                total_uoc_met += 6
    return total_uoc_met >= uoc_required

def validate_uoc_req_list(courses_list, uoc_required, courses_required):
    """
    Check the number of UOC in a given list of courses satisfies the requirement
    """
    total_uoc_met = 0
    for course in courses_list:
        if course in courses_required:
            total_uoc_met += 6
    return total_uoc_met >= uoc_required

