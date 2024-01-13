import json
import pickle
from time import sleep
from os import listdir, mkdir
from datetime import datetime

import requests
from tqdm import tqdm
from prettytable.prettytable import PrettyTable

import IRAS.constants as CONST
from IRAS.Types import OfferedCourse, RegisteredCourse, PreRequisiteCourse, AcademicYear, Semester, AuthData, BTree
from IRAS.utils import save_as_txt, save_as_xls, get_formatted_time, parse_grade, get_semester_order

class IRAS:
    def __init__(self) -> None:
        self.__verify_files()
        self.__student_id: int = -1
        self.__auth_token: str = ""

    def authenticate_user(self, student_id: int, password: str) -> bool:
        self.__student_id = student_id
        self.__auth_token = self.__get_auth_token(student_id, password)
        return self.__auth_token != ""

    def show_grades(self) -> None:
        registered_courses: dict[str, AcademicYear] = dict()
        registered_courses_map = list(map(lambda c: RegisteredCourse.NEW_INSTANCE(c, parse_grade),
                                    self.__fetch_json_data(
                                        api=CONST.ALL_REGISTERED_COURSE_API(self.__student_id)
                                    )["data"]
                                ))
        
        pbar = tqdm(total=len(registered_courses_map), desc="Processing data: ")
        
        # parse data
        for course in registered_courses_map:
            if course.registered_year not in registered_courses.keys():
                registered_courses.update({
                    course.registered_year:
                    AcademicYear(
                        [
                            Semester(
                                course.registered_semester,
                                get_semester_order(course.registered_semester),
                                [course]
                            )
                        ]
                    )
                })
                pbar.update(1)
                continue

            semesters = registered_courses.get(course.registered_year).semesters
            for semester in semesters:
                if semester.semester_name == course.registered_semester:
                    semester.courses.append(course)
                    break
            else:
                semesters.append(
                    Semester(
                        course.registered_semester,
                        get_semester_order(course.registered_semester),
                        [course]
                    )
                )
            pbar.update(1)
        pbar.close()

        # order semesters by year 
        registered_courses =  {year: registered_courses[year] for year in sorted(registered_courses)}

        # calculate grades
        completed_course_map = dict() # to avoid counting same course more than once
        total_grade: float = 0.0
        total_credit_count: int = 0
        table = PrettyTable(field_names=CONST.REGISTERED_COURSE_FIELDS)
        for a_year in registered_courses.values():
            # organize semesters (spring -> summer -> autumn)
            sorted_semesters = sorted(a_year.semesters, key=lambda s: s.order)

            for semester in sorted_semesters:
                s_cgpa: float = 0.0
                s_credit_count: int = 0
                for course in semester.courses:
                    table.add_row(course.as_list())
                    if course.grade:
                        s_cgpa += course.grade * course.credit_count
                        s_credit_count += course.credit_count
                        completed_course_map.update({course.course_id: (course.grade, course.credit_count)})
                table.add_row([""] * 5)
                table.add_row(["-----", "-----", "-----", "-----", f"GPA: {0.0 if not s_credit_count else round(s_cgpa / s_credit_count, 2)}"])
                table.add_row([""] * 5)
                table.add_row(["*"] * 5)
                table.add_row(["*"] * 5)
                table.add_row([""] * 5)

        for grade, credit in completed_course_map.values():
            total_grade += grade * credit
            total_credit_count += credit

        table.add_row(["", "", "", "", f"CGPA: {0.0 if not total_credit_count else round(total_grade / total_credit_count, 2)}"])
        table.add_row(["", "", "", "", f"Credit earned: {total_credit_count}"])
        print(table)

    def save_OfferedCourses(self, query_course_ids: list[str], save_as: str = "both", all: bool = False) -> None:
        """
        Expects a list of course ids and a saving format
        which can be one of 'both', 'txt' or 'xls'
        """
        if not query_course_ids:
            return print("No query found!")
        
        offered_course_tree: BTree = BTree.NEW_INSTANCE(
            map(lambda c: OfferedCourse.NEW_INSTANCE(c, get_formatted_time),
                    self.__fetch_json_data(
                        api=CONST.ALL_OFFERED_COURSES_API(self.__student_id),
                        interval=0
                        )["data"]["eligibleOfferCourses"]
                )
        )
        pre_requisite_course_tree: BTree = BTree.NEW_INSTANCE(
            map(lambda c: PreRequisiteCourse.NEW_INSTANCE(c),
                    self.__fetch_json_data(
                        api=CONST.PRE_REQUISITES_API(self.__student_id),
                        interval=0,
                        progress_message="Fetching pre-requisites"
                    )["data"] 
                )
        )

        query_course_ids = [id.upper() for id in query_course_ids] if not all else [c.id for c in offered_course_tree]
        queried_courses = []
        sections_count = []
        pre_requisite_courses = []
        pre_requisite_courses_count = []
        pbar = tqdm(total=len(query_course_ids), desc="Finding match: ")
        for course_id in query_course_ids:
            courses = offered_course_tree.get(course_id)
            pre_reqs = pre_requisite_course_tree.get(course_id)
            pre_reqs.extend(pre_requisite_course_tree.get(f"{course_id}L"))
            queried_courses.extend(courses)
            sections_count.append(len(courses))
            pre_requisite_courses.extend(pre_reqs)
            pre_requisite_courses_count.append(len(pre_reqs))
            pbar.update(1)
        pbar.close()

        if not queried_courses:
            return print("No match found!")

        pre_requisite_courses_count = list(filter(lambda c: c != 0, pre_requisite_courses_count))

        match save_as:
            case "both":
                save_as_txt(queried_courses, sections_count, pre_requisite_courses, pre_requisite_courses_count)
                save_as_xls(queried_courses, pre_requisite_courses)
            case "txt":
                save_as_txt(queried_courses, sections_count, pre_requisite_courses, pre_requisite_courses_count)
            case "xls":
                save_as_xls(queried_courses, pre_requisite_courses)

    def __get_auth_token(self, id: int, password: str) -> str:
        try:
            with open(CONST.AUTH_FILE_PATH, "rb") as auth_file:
                auth_data: AuthData = pickle.load(auth_file)
                if auth_data.student_id == id and auth_data.expires > datetime.now(auth_data.expires.tzinfo):
                    return auth_data.auth_token
        except FileNotFoundError:
            pass

        response = requests.post(
            CONST.AUTH_TOKEN_API,
            json={
                "email": id,
                "password": password
            },
            stream=True
        )
        json_auth_data = self.__fetch_json_data(response_obj=response,
                                      progress_message="Fetching auth token: ",
                                      validate_response=False)
        if not (json_auth_data := json_auth_data.get("data", 0)):
            print("Invalid credentials or connection error. Please try again...")
            return ""
        
        json_auth_data = json_auth_data[0]
        expiry_date = json_auth_data["expires"].rsplit(".")
        expiry_date = expiry_date[0] + "+" + expiry_date[1].rsplit("+")[1]
        new_auth_data = AuthData(self.__student_id, json_auth_data["access_token"], datetime.strptime(expiry_date, "%Y-%m-%dT%H:%M:%S%z"))
        with open(CONST.AUTH_FILE_PATH, "wb") as auth_file:
            pickle.dump(new_auth_data, auth_file)
        return new_auth_data.auth_token

    def __validate_response_status(self, response: requests.Response) -> None:
        if response.status_code != 200:
            raise requests.HTTPError(
                f"Falied to complete the request at {response.url}! Status code {response.status_code}.")
 
    def __fetch_json_data(self, api: str = "", response_obj: requests.Response = None, progress_message: str = "", interval: float = 0.05, validate_response: bool = True) -> dict:
        response = requests.get(
            api,
            headers={
                "Authorization": f"Bearer {self.__auth_token}"
            },
            stream=True
        ) if not response_obj else response_obj

        data_size = int(response.headers.get("content-length", 0))
        downloaded_data = b""
        chunk_size = 1024 #KB
        if validate_response:
            self.__validate_response_status(response)
        pbar = tqdm(total=data_size, desc="Fetching data: " if not progress_message else progress_message, unit="B")
      
        for data in response.iter_content(chunk_size=chunk_size):
            downloaded_data += data
            pbar.update(chunk_size)
            sleep(interval)
        pbar.close()

        return json.loads(downloaded_data.decode())

    def __verify_files(self): 
        if "files" not in listdir():
            mkdir("files")

        