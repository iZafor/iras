# APIs
AUTH_TOKEN_API = "https://iras.iub.edu.bd:8079//v2/account/token"
ALL_OFFERED_COURSES_API = lambda id: f"https://iras.iub.edu.bd:8079//api/v1/registration/{id}/all-offer-courses"
ALL_REGISTERED_COURSE_API = lambda id: f"https://iras.iub.edu.bd:8079//api/v1/registration/student-registered-courses/{id}/all"
PRE_REQUISITES_API = lambda id: f"https://iras.iub.edu.bd:8079//api/v1/registration/{id}/pre-requisite-courses"

OFFERED_COURSE_FIELDS = ["CODE", "NAME", "SECTION",
          "TIME SLOT", "CAPACITY", "ENROLLED", "VACANCY", "FACULTY"]

REGISTERED_COURSE_FIELDS = [
    "CODE", "NAME", "REGISTERED YEAR", "REGISTERED SEMESTER", "GRADE"
]

PRE_REQUISITE_FIELDS = ["CODE", "PRE-REQUISITE CODE", "PRE-REQUISITE COURSE NAME", "PRE-REQUISITE STATUS"]

AUTH_FILE_PATH = "files/auth_token_file"
OFFERED_COURSE_TEXT_FILE_PATH = "files/offered_courses.txt"
OFFERED_COURSE_EXCEL_FILE_PATH = "files/offered_courses.xlsx"