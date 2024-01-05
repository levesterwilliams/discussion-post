import csv
import requests
import json

class Canvas:
    def __init__(self, instance):
            self.instance = instance
    
    def get_token(self=None):
        
        with open('C:\Users\Levester\Desktop\cred.json', 'r') as f:
             cred = json.load(f)
        
        return cred
        

    server_url  =  {'LPS_Production': 'https://canvas.upenn.edu/', 'LPS_Test': 'https://upenn.test.instructure.com/'}
    
    def headers(self):
        token = self.get_token()
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer {}'.format(token[f'{self.instance}'])}
        return headers
        
    def get_course_discussion_data(self, course_id):
        # Get all discussion topics in the course
        discussion_topics_url = f'{self.server_url}/api/v1/courses/{course_id}/discussion_topics'
        response = requests.get(discussion_topics_url, headers = self.headers())
        discussion_topics = response.json()

        # Create a dictionary to store the discussion data for each student
        student_discussion_data = {}
        for discussion_topic in discussion_topics:
            # Get all discussion posts for the topic
            discussion_posts_url =  f'{self.server_url}/api/v1/courses/{course_id}/discussion_topics/{discussion_topic["id"]}/posts'
            response = requests.get(discussion_posts_url, headers=self.headers())
            discussion_posts = response.json()

            # Iterate over the discussion posts and tally the number of original posts and replies for each student
            for discussion_post in discussion_posts:
                student_id = discussion_post['author_id']
                if student_id not in student_discussion_data:
                    student_discussion_data[student_id] = {}

                if discussion_post['parent_id'] is None:
                    # Original post
                    student_discussion_data[student_id][discussion_topic['title']] = {
                        'original_posts': 1,
                        'replies': 0
                    }
                else:
                    # Reply
                    student_discussion_data[student_id][discussion_topic['title']]['replies'] += 1

        return student_discussion_data

    def write_discussion_data_to_csv(self, student_discussion_data, output_file_path):
        with open(output_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write the header row
            writer.writerow(['Student ID', 'Discussion Topic', 'Original Posts', 'Replies'])

            # Iterate over the student discussion data and write each row to the CSV file
            for student_id, discussion_topic_data in student_discussion_data.items():
                for discussion_topic, post_data in discussion_topic_data.items():
                    writer.writerow([
                        student_id,
                        discussion_topic,
                        post_data['original_posts'],
                        post_data['replies']
                    ])

if __name__ == '__main__':
    canvas = Canvas()
    canvas.instance = 'LPS_Production'
    # Test course id for Levster's Sandbox (located at the end of url)
    course_id = 1748632

   
    # Get the discussion data for the course
    student_discussion_data = canvas.get_course_discussion_data(course_id)

    # Write the discussion data to a CSV file
    output_file_path = 'discussion_data.csv'
    canvas.write_discussion_data_to_csv(student_discussion_data, output_file_path)
