import unittest

from services.portal_timetable_service import PortalTimetableService


class PortalTimetableServiceTests(unittest.TestCase):
    def test_matches_repeated_course_rows_to_their_slot_span(self):
        html = """
        <div id="subjectTab">
          <table>
            <thead><tr><th>FROM</th><th>08:00 - 08:50</th><th>08:50 - 09:40</th></tr></thead>
            <tbody>
              <tr><td>Day 1</td><td>CS101</td><td>CS101</td></tr>
              <tr><td>Day 2</td><td>CS101</td><td>-</td></tr>
              <tr><td>Day 3</td><td>DESIGNP</td><td>-</td></tr>
            </tbody>
          </table>
          <table>
            <thead><tr>
              <th>Course Code</th><th>Course Name</th><th>Credit</th><th>Slot</th>
              <th>Assigned Faculty</th><th>Building</th><th>Floor</th><th>Room Name</th>
            </tr></thead>
            <tbody>
              <tr><td>CS101</td><td>Foundations</td><td>4</td><td>D</td><td>Staff</td><td>Main Building (MB)</td><td>4</td><td>401</td></tr>
              <tr><td>CS101</td><td>Foundations</td><td>4</td><td>P23,P24</td><td>Staff</td><td>Main Building (MB)</td><td>4</td><td>402</td></tr>
              <tr><td>DESIGNP</td><td>Design</td><td>3</td><td>A</td><td>Staff</td><td>Main Building (MB)</td><td>4</td><td>403</td></tr>
            </tbody>
          </table>
        </div>
        """

        schedule, _ = PortalTimetableService.parse(html)

        lab = schedule["Day 1"]["08:00 - 08:50"]
        theory = schedule["Day 2"]["08:00 - 08:50"]
        suffix_code_theory = schedule["Day 3"]["08:00 - 08:50"]
        self.assertEqual((lab["type"], lab["room"], lab["slot"]), ("Practical", "MB 402", "P23,P24"))
        self.assertEqual((theory["type"], theory["room"], theory["slot"]), ("Theory", "MB 401", "D"))
        self.assertEqual(suffix_code_theory["type"], "Theory")

    def test_uses_batch_slot_grid_when_lecture_and_practical_have_same_duration(self):
        html = """
        <div id="subjectTab">
          <table>
            <thead><tr><th>FROM</th><th>08:00 - 08:50</th><th>08:50 - 09:40</th></tr></thead>
            <tbody>
              <tr><td>Day 1</td><td>PPS101</td><td>PPS101</td></tr>
              <tr><td>Day 2</td><td>PPS101</td><td>PPS101</td></tr>
              <tr><td>Day 3</td><td>COURSEP</td><td>-</td></tr>
            </tbody>
          </table>
          <table>
            <thead><tr>
              <th>Course Code</th><th>Course Name</th><th>Credit</th><th>Slot</th>
              <th>Assigned Faculty</th><th>Building</th><th>Floor</th><th>Room Name</th>
            </tr></thead>
            <tbody>
              <tr><td>PPS101</td><td>Programming for Problem Solving</td><td>4</td><td>E</td><td>Staff</td><td>Main Building (MB)</td><td>4</td><td>402</td></tr>
              <tr><td>PPS101</td><td>Programming for Problem Solving</td><td>4</td><td>P37,P38</td><td>Staff</td><td>Computing Lab (CL)</td><td>6</td><td>610</td></tr>
              <tr><td>COURSEP</td><td>Communication Skills</td><td>2</td><td>A</td><td>Staff</td><td>Main Building (MB)</td><td>4</td><td>403</td></tr>
            </tbody>
          </table>
        </div>
        <div>
          <table>
            <thead><tr><th>FROM</th><th>08:00 - 08:50</th><th>08:50 - 09:40</th></tr></thead>
            <tbody>
              <tr><td>Day 1</td><td>P37</td><td>P38</td></tr>
              <tr><td>Day 2</td><td>E</td><td>E</td></tr>
              <tr><td>Day 3</td><td>A</td><td>-</td></tr>
            </tbody>
          </table>
        </div>
        """

        schedule, _ = PortalTimetableService.parse(html)

        practical = schedule["Day 1"]["08:00 - 08:50"]
        lecture = schedule["Day 2"]["08:00 - 08:50"]
        suffix_code_lecture = schedule["Day 3"]["08:00 - 08:50"]
        self.assertEqual((practical["type"], practical["room"], practical["slot"]), ("Practical", "CL 610", "P37,P38"))
        self.assertEqual((lecture["type"], lecture["room"], lecture["slot"]), ("Theory", "MB 402", "E"))
        self.assertEqual(suffix_code_lecture["type"], "Theory")

    def test_matches_batch_slots_by_time_when_grid_column_order_differs(self):
        html = """
        <table>
          <thead><tr><th>Day</th><th>08:00 - 08:50</th><th>08:50 - 09:40</th></tr></thead>
          <tbody><tr><td>Day 1</td><td>CS101</td><td>CS101</td></tr></tbody>
        </table>
        <table>
          <thead><tr><th>Day</th><th>08:50 - 09:40</th><th>08:00 - 08:50</th></tr></thead>
          <tbody><tr><td>Day 1</td><td>P23</td><td>E</td></tr></tbody>
        </table>
        <table>
          <thead><tr><th>Course Code</th><th>Course Name</th><th>Credits</th><th>Slot</th><th>Assigned Faculty</th><th>Building</th><th>Floor</th><th>Room</th></tr></thead>
          <tbody>
            <tr><td>CS101</td><td>Computer Science</td><td>3</td><td>E</td><td>Faculty A</td><td>Main Building (MB)</td><td>4</td><td>401</td></tr>
            <tr><td>CS101</td><td>Computer Science Practical</td><td>1</td><td>P23</td><td>Faculty B</td><td>Main Building (MB)</td><td>4</td><td>402</td></tr>
          </tbody>
        </table>
        """
        schedule, _ = PortalTimetableService.parse(html)
        day = schedule["Day 1"]
        self.assertEqual((day["08:00 - 08:50"]["type"], day["08:00 - 08:50"]["room"]), ("Theory", "MB 401"))
        self.assertEqual((day["08:50 - 09:40"]["type"], day["08:50 - 09:40"]["room"]), ("Practical", "MB 402"))


if __name__ == "__main__":
    unittest.main()
