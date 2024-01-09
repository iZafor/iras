# APIs
AUTH_TOKEN_API = "https://iras.iub.edu.bd:8079//v2/account/token"
ALL_OFFERED_COURSES_API = lambda id: f"https://iras.iub.edu.bd:8079//api/v1/registration/{id}/all-offer-courses"
ALL_REGISTERED_COURSE_API = lambda id: f"https://iras.iub.edu.bd:8079//api/v1/registration/student-registered-courses/{id}/all"

DETAILED_COURSE_FIELDS = ["CODE", "NAME", "SECTION",
          "TIME SLOT", "CAPACITY", "ENROLLED", "VACANCY", "FACULTY"]

REGISTERED_COURSE_FILEDS = [
    "CODE", "NAME", "REGISTERED YEAR", "REGISTERED SEMESTER", "GRADE"
]

AUTH_FILE_PATH = "files/auth_token_file"