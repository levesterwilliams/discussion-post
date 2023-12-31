import csv
import requests
import json
from pathlib import Path
class Canvas:
    def __init__(self, instance):
        self.instance = instance

    def get_token(self=None):
        with open(r'\Users\Levester\source\repos\discussion-post\cred.json') as f:
            cred = json.load(f)
        return cred

    server_url = {'LPS_Production': 'https://canvas.upenn.edu/', 'LPS_Test': 'https://upenn.test.instructure.com/'}
    
    def headers(self):
        token = self.get_token()
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {}'.format(token[f'{self.instance}'])}
        return headers

    # Retrieve students and test to see if the correct JSON object has been retrieved
    def get_students(self, course_id):
        # Fetch students enrolled in the course
        students_url = f'{self.server_url[self.instance]}api/v1/courses/{course_id}/users?enrollment_type[]=student'
        response = requests.get(students_url, headers=self.headers())
        students = response.json()
        print("API Responses:", students)
        if isinstance(students, list) and all(isinstance(students, dict) for student in students):
            return {student['id']: student['name'] for student in students}
        else:
            print("Error: Unexpected API response format")
            return {}

    def get_course_discussion_data(self, course_id):
        # Get all discussion topics in the course
        discussion_topics_url = f'{self.server_url[self.instance]}api/v1/courses/{course_id}/discussion_topics'
        response = requests.get(discussion_topics_url, headers=self.headers())
        discussion_topics = response.json()

        # Get students
        students = self.get_students(course_id)
        
        # Initialize data structure for discussion data
        student_discussion_data = {name: {} for _, name in students.items()}
        for topic in discussion_topics:
            topic_title = topic['title']
            for student in student_discussion_data:
                student_discussion_data[student][f'{topic_title} - Original Post'] = False
                student_discussion_data[student][f'{topic_title} - Replies'] = False

        for discussion_topic in discussion_topics:
            # Get all discussion posts for the topic
            discussion_posts_url = f'{self.server_url[self.instance]}api/v1/courses/{course_id}/discussion_topics/{discussion_topic["id"]}/posts'
            response = requests.get(discussion_posts_url, headers=self.headers())
            discussion_posts = response.json()

            # Check if each student has posted or replied in the topic
            for discussion_post in discussion_posts:
                student_id = discussion_post['author_id']
                if student_id in students:
                    student_name = students[student_id]
                    if discussion_post['parent_id'] is None:  # Original post
                        student_discussion_data[student_name][f'{discussion_topic["title"]} - Original Post'] = True
                    else:  # Reply
                        student_discussion_data[student_name][f'{discussion_topic["title"]} - Replies'] = True

        return student_discussion_data

    def write_discussion_data_to_csv(self, student_discussion_data):
        # Return without outputting a csv file if no students are found in course
        if not student_discussion_data:
            print("No student discussion data")
            return
        # Determine the path to the user's download folder
        download_folder = Path.home() / 'Downloads'
        if not download_folder.exists():
            download_folder.mkdir()
            print(f"Created folder: {download_folder}")

        output_file_path = download_folder / 'discusssion_data.csv'

        with open(output_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            headers = ['Student\'s Name'] + [f"{topic} - Original Post" for topic in next(iter(
                student_discussion_data.values()), {}).keys()] + [f"{topic} - Replies" for topic in next(iter(
                student_discussion_data.values()), {}).keys()]

            writer.writerow(headers)

            for student_name, topics in student_discussion_data.items():
                row = [student_name] + list(topics.values())
                writer.writerow(row)

        print(f"CSV file written to {output_file_path}")

    # Retrieve course name
    def get_course_name(self, course_id):
        course_url =  f'{self.server_url[self.instance]}api/v1/courses/{course_id}'
        response = requests.get(course_url, headers=self.headers())
        course = response.json()
        return course.get('name', 'Unknown Course')


if __name__ == '__main__':
    canvas = Canvas('LPS_Test')
    course_id = '1748632'

    # Test to check course name
    course_name = canvas.get_course_name(course_id)
    print(f"Course Name: {course_name}")

    # Get the discussion data for the course
    student_discussion_data = canvas.get_course_discussion_data(course_id)

    # Write the discussion data to a CSV file
    canvas.write_discussion_data_to_csv(student_discussion_data)
