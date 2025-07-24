# ocr.py
import pytesseract
from PIL import Image
import re
from io import BytesIO

def extract_text_and_schedule(image_file):
    # Convert image to PIL
    image = Image.open(image_file.stream)

    # Extract raw text
    text = pytesseract.image_to_string(image, config="--psm 6")

    # Parse schedule from raw text
    schedule = parse_timetable(text)

    return text, schedule

def parse_timetable(raw_text):
    lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]
    
    timetable = []
    current_course = None

    day_order = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
        'friday': 4, 'saturday': 5, 'sunday': 6
    }

    course_line_re = re.compile(r"^(\w+)\s+(.+?)\s+([A-Z]+\s*/\s*\d+)\s+\d+\s+\w+\s+\w+\s+(.+?)(?=\s+\w+day:|$)", re.IGNORECASE)
    
    schedule_re = re.compile(r"(\w+day):\s*(\d{2}:\d{2}):\d{2}\s*-\s*(\d{2}:\d{2}):\d{2}", re.IGNORECASE)

    for line in lines:
        if "Course Code" in line and "Course Title" in line:
            continue
            
        course_match = course_line_re.search(line)
        
        if course_match:
            if current_course:
                current_course["schedule"].sort(key=lambda x: (
                    day_order.get(x["day"].lower(), 7),
                    x["start"]
                ))
                timetable.append(current_course)

            code, title, room, instructor = course_match.groups()
            current_course = {
                "code": code,
                "title": title.strip(),
                "room": room.strip(),
                "instructor": instructor.strip(),
                "schedule": []
            }
            
            schedule_matches = schedule_re.findall(line)
            if schedule_matches:
                for day, start, end in schedule_matches:
                    current_course["schedule"].append({
                        "day": day,
                        "start": start,
                        "end": end
                    })

        elif schedule_re.findall(line) and current_course:
            for day, start, end in schedule_re.findall(line):
                current_course["schedule"].append({
                    "day": day,
                    "start": start,
                    "end": end
                })

    if current_course:
        current_course["schedule"].sort(key=lambda x: (
            day_order.get(x["day"].lower(), 7),
            x["start"]
        ))
        timetable.append(current_course)

    return timetable