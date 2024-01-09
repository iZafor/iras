import xlsxwriter
from os import getcwd
from prettytable import PrettyTable

import IRAS.constants as CONST
from IRAS.Types import OfferedCourse

def get_formatted_time(time_str: str) -> str:
    day, time = time_str.split(" ")
    time_st, time_en = time.split("-")
    st_notation, en_notation = "", ""

    if (st_hour := int(time_st[:2])) >= 12:
        st_notation = "PM"
        if st_hour > 12:
            st_hour -= 12
    else:
        st_notation = "AM"

    if (en_hour := int(time_en[:2])) >= 12:
        en_notation = "PM"
        if en_hour > 12:
            en_hour -= 12
    else:
        en_notation = "AM"

    return f"{day} {st_hour}:{time_st[2:]}{st_notation}-{en_hour}:{time_en[2:]}{en_notation}"

def save_as_txt(queried_courses: list[OfferedCourse], sections_count: list[int]) -> None:
    table = PrettyTable(
        field_names=CONST.OFFERED_COURSE_FIELDS
    )

    i, count = 0, 0
    for course in queried_courses:
        if i < len(sections_count) and count == sections_count[i]:
            i += 1
            count = 0
            table.add_row(["+"] * len(CONST.OFFERED_COURSE_FIELDS))
        count += 1
        table.add_row(course.as_list())

    txt_file_path = "files/course_details.txt"
    with open(txt_file_path, "w") as txt_file:
        txt_file.writelines(str(table))
    print(f"Text file is saved at {getcwd()}/{txt_file_path}.")

def save_as_xls(queried_courses: list[OfferedCourse]) -> None:
    xls_file_path = "files/course_details.xlsx"
    wb = xlsxwriter.Workbook(xls_file_path)
    ws = wb.add_worksheet("Course Details")
    ws.write_row(0, 0, CONST.OFFERED_COURSE_FIELDS)

    for r in range(1, len(queried_courses)):
        ws.write_row(r, 0, queried_courses[r-1].as_list())
    wb.close()
    print(f"Excel file is saved at {getcwd()}/{xls_file_path}.")

def parse_grade(grade_code: str) -> float:
    match grade_code:
        case "A":
            return 4
        case "A-":
            return 3.7
        case "B+":
            return 3.3
        case "B":
            return 3.0
        case "B-":
            return 2.7
        case "C+":
            return 2.3
        case "C":
            return 2.0
        case "C-":
            return 1.7
        case "D+":
            return 1.3
        case "D":
            return 1.0
        case _:
            return 0
