from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, NamedTuple, Iterable, Generator

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

    def as_list(self) -> list[_T]:
        return [self.course_id, self.course_name, self.section, self.time_slot, self.capacity, self.enrolled, self.vacancy, self.faculty]

    def __str__(self) -> str:
        return f"CODE: {self.course_id}, NAME: {self.course_name}, SECTION: {self.section}, TIME SLOT: {self.time_slot}, CAPACITY: {self.capacity}, ENROLLED: {self.enrolled}, VACANCY: {self.vacancy}, FACULTY: {self.faculty}"

    @staticmethod
    def NEW_INSTANCE(data: dict[str, _T], time_formatter: Callable[[str], str]) -> OfferedCourse:
        return OfferedCourse(
            data["courseId"],
            data["courseName"],
            data["section"],
            time_formatter(data["timeSlot"]),
            data["capacity"],
            data["enrolled"],
            data["vacancy"],
            data["facualtyName"].strip(),
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
        course_id, sem, grade_code = data["courseId"], "", data["grade"].strip()  
        match data["regSemester"]:
            case "1":
                sem = "Autumn"
            case "2":
                sem = "Spring"
            case "3":
                sem = "Summer"

        return RegisteredCourse(
            course_id,
            data["courseName"],
            data["regYear"],
            sem,
            grade_code,
            grade_parser(grade_code),
            1 if course_id[-1] == "L" and course_id[-2].isdigit() else 3
        )

@dataclass
class PreRequisiteCourse:
    course_id: str
    pre_requisite_course_id: str
    pre_requisite_course_name: str
    status: str

    def as_list(self) -> list[str]:
        return [self.course_id, self.pre_requisite_course_id, self.pre_requisite_course_name, self.status]

    def __str__(self) -> str:
        return f"CODE: {self.course_id}, PRE-REQUISITE CODE: {self.pre_requisite_course_id}, PRE-REQUISITE COURSE NAME: {self.pre_requisite_course_name}, PRE-REQUISITE STATUS: {self.status}"

    @staticmethod
    def NEW_INSTANCE(data: dict[str, _T]) -> PreRequisiteCourse:
        return PreRequisiteCourse(
            data["courseId"],
            data["preReqCourseId"],
            data["courseName"],
            "Completed" if int(data["gradePoint"]) else "Incomplete"
        )

Semester = NamedTuple("Semester", [("semester_name", str), ("order", int), ("courses", list[RegisteredCourse])])

AcademicYear = NamedTuple("AcademicYear", [("semesters", list[Semester])])

AuthData = NamedTuple("AuthData", [("student_id", int), ("auth_token", str), ("expires", datetime)])


ND_Type = OfferedCourse | RegisteredCourse | PreRequisiteCourse

class TreeNode:
    def __init__(self, id) -> None:
        self.id = id
        self.data_list: list[ND_Type] = list() 
        self.left: TreeNode = None
        self.right: TreeNode = None

    def append_data(self, data: ND_Type) -> TreeNode:
        self.data_list.append(data)
        return self

class BTree:
    def __init__(self) -> None:
        self.root: TreeNode = None
        self.size = 0 

    def insert(self, data: ND_Type) -> None:
        self.root = self.__insert_helper(self.root, data)

    def insert_all(self, it: Iterable[ND_Type]) -> None:
        for data in it:
            self.insert(data)

    def get(self, id: str) -> list[ND_Type]:
        result: list[ND_Type] = list()
        self.__get_helper(self.root, id, result)
        return result     

    def __insert_helper(self, node: TreeNode, data: ND_Type) -> TreeNode:
        if not node:
            self.size += 1
            return TreeNode(data.course_id).append_data(data)
            
        if data.course_id.find(node.id) != -1:
            return node.append_data(data)
        elif node.id > data.course_id:
            node.left = self.__insert_helper(node.left, data)
        else:
            node.right = self.__insert_helper(node.right, data)
        
        return node

    def __get_helper(self, node: TreeNode, id: str, res: list[ND_Type]) -> None:
        if not node:
            return
        
        partial_match = 0
        if node.id == id or (partial_match := id.find(node.id) != -1):
            return res.extend(node.data_list if not partial_match else [c for c in node.data_list if c.course_id == id])
        elif node.id > id:
            self.__get_helper(node.left, id, res)
        else:
            self.__get_helper(node.right, id, res)

    def __iter__(self) -> Generator[ND_Type]:
        return self.__in_oder_traversal(self.root)
    
    def __len__(self) -> int:
        return self.size
    
    def __in_oder_traversal(self, node: TreeNode) -> TreeNode:
        if node:
            yield from self.__in_oder_traversal(node.left)
            yield node
            yield from self.__in_oder_traversal(node.right)
    
    @staticmethod
    def NEW_INSTANCE(it: Iterable[ND_Type]) -> BTree:
        btree = BTree()
        btree.insert_all(it)
        return btree