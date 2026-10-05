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


if __name__ == "__main__":
    unittest.main()
