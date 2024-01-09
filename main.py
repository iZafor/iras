#!./venv/bin/python3
from IRAS import IRAS

CREDENTIALS_PROMPT_TEXT = """
################################################
# Enter your student id and password separated #
# by space e.g 123 ABC                         #
#                                              #
# Enter q to quit                              #
################################################
ID and Password: """

OPTION_PROMPT_TEXT = """
################################################
# Select option:                               #
# 1. Show Grades                               #
# 2. Save Offered Course Details               #
# 3. Re-login                                  #
#                                              #
# Enter anything else to quit                  #
################################################
Option: """

COURSE_QUERY_PROMPT_TEXT = """
################################################
# Enter query course codes separated by space  #
# e.g ENG101 ENG102 ...                        #
# * LABS are auto detected                     #
################################################
Codes: """

FILE_FORMAT_PROMPT_TEXT = """
################################################
# Save file as -                               #
# 1. Text only                                 #
# 2. Excel only                                #
# 3. Both Text and Excel                       #
################################################
File format: """

FILE_FORMATS = ("txt", "xls", "both")

if __name__ == "__main__":
    re_login = False
    try:
        iras = IRAS()
        while (cred_data := input(CREDENTIALS_PROMPT_TEXT).split(" ", 1)):
            if len(cred_data) == 1 and cred_data[0] == "q":
                break
            if len(cred_data) != 2:
                print("Invalid input! Follow the procedure...")
                continue
            if iras.authenticate_user(cred_data[0], cred_data[1]):
                re_login = False
                while (command := input(OPTION_PROMPT_TEXT)) and command.isdigit():
                    print()
                    match int(command):
                        case 1:
                            iras.show_grades()
                        case 2:
                            query_course_ids = input(COURSE_QUERY_PROMPT_TEXT).split(" ")
                            file_format = input(FILE_FORMAT_PROMPT_TEXT)
                            save_as = FILE_FORMATS[2]
                            match file_format.isdigit():
                                case False:
                                    print("Invalid file format! Saving as both...")
                                case True:
                                    match int(file_format):
                                        case 1:
                                            save_as = FILE_FORMATS[0]
                                        case 2:
                                            save_as = FILE_FORMATS[1]
                                        case 3:
                                            save_as = FILE_FORMATS[2]
                                        case _:
                                            print("Invalid file format! Saving as both...")
                            iras.save_OfferedCourses(query_course_ids=query_course_ids, save_as=save_as)
                        case 3:
                            re_login = True
                            break
                        case _:
                            break
                if not re_login:
                    break
    except RuntimeError as e:
        print(f"Error: {e}")