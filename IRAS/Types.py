from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, NamedTuple

_T = int | float | str

@dataclass
class OfferedCourse:
    course_id: str
    course_name: str
    section: _T
    time_slot: str
    capacity: _T
    enrolled: _T
    vacancy: _T
    faculty: str

    def any_match(self, query_ids: list[str]) -> bool:
        """
        Expects a list of query ids in lower case
        """
        return self.course_id in query_ids

    def as_list(self) -> list[_T]:
        res = list(self.__dict__.values())
        res[0] = self.course_id.upper()
        return res

    def __str__(self) -> str:
        return f"CODE: {self.course_id.upper()}, NAME: {self.course_name}, SECTION: {self.section}, TIME SLOT: {self.time_slot}, CAPACITY: {self.capacity}, ENROLLED: {self.enrolled}, VACANCY: {self.vacancy}, FACULTY: {self.faculty}"

    @staticmethod
    def NEW_INSTANCE(data: dict[str, _T], time_formatter: Callable[[str], str]) -> OfferedCourse:
        return OfferedCourse(
            data["courseId"].lower().strip(),
            data["courseName"].strip(),
            data["section"],
            data["capacity"],
            data["enrolled"],
            data["vacancy"],
            time_formatter(data["timeSlot"].strip()),
            data["facultyName"].strip(),
        )


@dataclass
class RegisteredCourse:
    course_id: str
    course_name: str
    registered_year: str
    registered_semester: str
    grade_code: str
    grade: float
    credit_count: int

    def as_list(self) -> list[_T]:
        return [self.course_id, self.course_name, self.registered_year, self.registered_semester, f"{self.grade_code}({self.grade})"]

    def __str__(self) -> str:
        return f"CODE: {self.course_id}, NAME: {self.course_name}, SEMESTER: {self.registered_semester}, YEAR: {self.registered_year}, GRADE: {self.grade_code}({self.grade}), CREDITS: {self.credit_count}"

    @staticmethod
    def NEW_INSTANCE(data: dict[str, _T], grade_parser: Callable[[str], float]) -> RegisteredCourse:
        name, sem, grade_code = data["courseId"], "", data["grade"].strip()  
        match data["regSemester"]:
            case "1":
                sem = "Autumn"
            case "2":
                sem = "Spring"
            case "3":
                sem = "Summer"

        return RegisteredCourse(
            name,
            data["courseName"],
            data["regYear"],
            sem,
            grade_code,
            grade_parser(grade_code),
            1 if name[-1] == "L" and name[-2].isdigit() else 3
        )

Semester = NamedTuple("Semester", [("semester_name", str), ("courses", list[RegisteredCourse])])

AcademicYear = NamedTuple("AcademicYear", [("semesters", list[Semester])])

AuthData = NamedTuple("AuthData", [("student_id", int), ("auth_token", str), ("expires", datetime)])