from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os

app = FastAPI()
FILE_PATH = "courses.json"

class Course(BaseModel):
    course_name: str
    year: str
    semester: str
    grade: str


def read_courses():
    # 파일이 존재하지 않으면 빈 리스트 반환하여 서버가 종료되지 않도록 함
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    except OSError as exc:
        raise HTTPException(status_code=500, detail="수강 기록을 읽어오는 중 파일 오류가 발생했습니다.") from exc


def write_courses(data):
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="수강 기록을 저장하는 중 파일 오류가 발생했습니다.") from exc


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "message": "잘못된 요청 형식입니다.",
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "서버 처리 중 예상치 못한 오류가 발생했습니다. 이후 요청은 계속 처리됩니다.",
            "detail": str(exc),
        },
    )


@app.get("/courses")
def get_courses_endpoint():
    return read_courses()


@app.post("/courses")
def add_course_endpoint(course: Course):

    courses = read_courses()
    
   
    new_course = course.model_dump() if hasattr(course, 'model_dump') else course.dict()
    courses.append(new_course)
    

    write_courses(courses)
    return {"message": "수강기록이 성공적으로 추가되었습니다.", "data": new_course}