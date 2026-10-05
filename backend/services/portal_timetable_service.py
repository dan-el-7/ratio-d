import re
from selectolax.parser import HTMLParser
from utils.text import TextUtils

class PortalTimetableService:
    @staticmethod
    def _slot_period_count(slot):
        return len([part for part in slot.split(",") if part.strip()])

    @staticmethod
    def _slot_tokens(slot):
        return {
            re.sub(r"\s+", "", token.strip().upper())
            for token in re.split(r"[,/]", slot or "")
            if token.strip()
        }

    @staticmethod
    def _match_course_variant(variants, period_count=None, slot_token=None):
        if not variants:
            return None
        normalized_slot = re.sub(r"\s+", "", (slot_token or "").strip().upper())
        if normalized_slot:
            exact_matches = [
                course for course in variants
                if normalized_slot in PortalTimetableService._slot_tokens(course["slot"])
            ]
            if exact_matches:
                return exact_matches[0]
        if period_count is None:
            return next((course for course in variants if course["type"] == "Theory"), variants[0])
        return min(
            variants,
            key=lambda course: (
                abs(PortalTimetableService._slot_period_count(course["slot"]) - period_count),
                course["type"] == "Practical",
            ),
        )

    @staticmethod
    def _get_day_rows(table):
        day_rows = {}
        rows = table.css("tbody tr") if table.css("tbody tr") else table.css("tr")
        for row in rows:
            cols = [TextUtils.clean(td.text(separator=" ", strip=True)) for td in row.css("td")]
            if not cols:
                continue
            day_match = re.search(r"Day\s*(\d+)", cols[0], re.I)
            if day_match:
                day_rows[f"Day {day_match.group(1)}"] = cols[1:]
        return day_rows

    @staticmethod
    def _get_time_headers(table):
        thead = table.css_first("thead")
        if not thead:
            return []
        for tr in thead.css("tr"):
            row_times = []
            for th in tr.css("th, td"):
                raw = th.text(separator=" ", strip=True)
                cleaned = re.sub(r"\s+", " ", raw)
                match = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", cleaned)
                if match:
                    row_times.append(f"{match.group(1)} - {match.group(2)}")
            if row_times:
                return row_times
        return []

    @staticmethod
    def _normalize_time_slot(slot):
        return re.sub(r"\s+", "", slot or "").upper()

    @staticmethod
    def parse(html_content):
        if not html_content:
            return {}, {}
        
        parser = HTMLParser(html_content)
        courses_map = {}
        course_variants = {}
        
        for table in parser.css("table"):
            headers = [TextUtils.clean(th.text(strip=True)).lower() for th in table.css("th")]
            if any("course code" in h for h in headers) and any("assigned faculty" in h or "faculty" in h for h in headers):
                rows = table.css("tbody tr") if table.css("tbody tr") else table.css("tr")
                for row in rows:
                    cols = [TextUtils.clean(td.text(separator=' ', strip=True)) for td in row.css("td")]
                    if len(cols) >= 5:
                        c_code = cols[0]
                        c_name = cols[1]
                        c_credits = cols[2]
                        c_slot = cols[3]
                        c_faculty = cols[4]
                        
                        building = cols[5] if len(cols) > 5 else ""
                        floor = cols[6] if len(cols) > 6 else ""
                        raw_room = cols[7] if len(cols) > 7 else ""
                        clean_room = re.split(r'[,/]|(?:\s+(?:Drafting|Lab|Room|Hall))', raw_room, flags=re.I)[0].strip() if raw_room else ""
                        
                        b_str = building.strip()
                        m_abbr = re.search(r'\(([^)]+)\)', b_str)
                        if m_abbr:
                            b_abbr = m_abbr.group(1).strip().upper()
                        elif b_str:
                            b_abbr = "".join(w[0].upper() for w in re.split(r'[\s-]+', b_str) if w and w[0].isalnum())
                        else:
                            b_abbr = ""
                            
                        if clean_room and b_abbr:
                            full_room = clean_room if clean_room.upper().startswith(b_abbr) else f"{b_abbr} {clean_room}"
                        elif clean_room:
                            full_room = clean_room
                        elif b_abbr:
                            full_room = b_abbr
                        else:
                            full_room = "TBA"
                        
                        slots = [slot.strip().upper() for slot in c_slot.split(",") if slot.strip()]
                        is_lab = (
                            re.search(r"\b(lab|practical)\b", c_name, flags=re.I) is not None
                            or any(slot.startswith("P") for slot in slots)
                        )
                        
                        course_info = {
                            "code": c_code,
                            "name": c_name,
                            "title": c_name,
                            "credits": c_credits,
                            "slot": c_slot,
                            "faculty": c_faculty if c_faculty else "TBA",
                            "room": full_room,
                            "building": building,
                            "floor": floor,
                            "room_name": clean_room,
                            "type": "Practical" if is_lab else "Theory",
                            "raw_type": "Practical" if is_lab else "Theory"
                        }
                        
                        course_variants.setdefault(c_code, []).append(course_info)
                        if c_code not in courses_map:
                            courses_map[c_code] = course_info.copy()
                        else:
                            existing = courses_map[c_code]
                            if c_slot and c_slot not in existing["slot"]:
                                existing["slot"] += f", {c_slot}"
                            if full_room != "TBA" and existing["room"] == "TBA":
                                existing["room"] = full_room

        schedule = {}
        known_slot_tokens = {
            token
            for variants in course_variants.values()
            for course in variants
            for token in PortalTimetableService._slot_tokens(course["slot"])
        }
        grid_candidates = []
        for table in parser.css("table"):
            day_rows = PortalTimetableService._get_day_rows(table)
            if not day_rows:
                continue
            values = [value for row in day_rows.values() for value in row if value and value not in {"-", "--"}]
            course_hits = sum(value in course_variants for value in values)
            slot_hits = sum(
                re.sub(r"\s+", "", value.strip().upper()) in known_slot_tokens
                for value in values
            )
            grid_candidates.append({
                "rows": day_rows,
                "times": PortalTimetableService._get_time_headers(table),
                "course_hits": course_hits,
                "slot_hits": slot_hits,
            })

        course_grid = max(grid_candidates, key=lambda grid: grid["course_hits"], default=None)
        slot_grid = max(
            (grid for grid in grid_candidates if grid is not course_grid),
            key=lambda grid: grid["slot_hits"],
            default=None,
        )
        if slot_grid and slot_grid["slot_hits"] == 0:
            slot_grid = None

        if course_grid:
            time_headers = course_grid["times"]
            for day_name, cell_codes in course_grid["rows"].items():
                schedule[day_name] = {}
                slot_cells = slot_grid["rows"].get(day_name, []) if slot_grid else []
                slot_times = slot_grid["times"] if slot_grid else []
                slot_by_time = {
                    PortalTimetableService._normalize_time_slot(time): slot_cells[index]
                    for index, time in enumerate(slot_times)
                    if index < len(slot_cells)
                }
                for i, raw_code in enumerate(cell_codes):
                    if i >= len(time_headers):
                        break
                    code = raw_code.strip()
                    if not code or code in {"-", "--"}:
                        continue
                    time_slot = time_headers[i]
                    start = i
                    while start > 0 and cell_codes[start - 1] == code:
                        start -= 1
                    end = i + 1
                    while end < len(cell_codes) and cell_codes[end] == code:
                        end += 1
                    period_count = end - start
                    actual_slot = (
                        slot_by_time.get(PortalTimetableService._normalize_time_slot(time_slot), "")
                        if slot_times
                        else slot_cells[i] if i < len(slot_cells) else ""
                    )
                    details = PortalTimetableService._match_course_variant(
                        course_variants.get(code, []),
                        period_count if not slot_grid else None,
                        actual_slot,
                    ) or courses_map.get(code, {
                        "code": code,
                        "name": code,
                        "title": code,
                        "type": "Theory",
                        "raw_type": "Theory",
                        "faculty": "TBA",
                        "room": "TBA",
                        "slot": "",
                        "credits": ""
                    })
                    schedule[day_name][time_slot] = {
                        "code": code,
                        "course": details["name"],
                        "courseCode": code,
                        "courseTitle": details["name"],
                        "name": details["name"],
                        "slot": details.get("slot", ""),
                        "type": details.get("type", "Theory"),
                        "raw_type": details.get("raw_type", "Theory"),
                        "room": details.get("room", "TBA"),
                        "faculty": details.get("faculty", "TBA"),
                        "time": time_slot,
                        "credits": details.get("credits", "")
                    }
                    
        return schedule, courses_map
