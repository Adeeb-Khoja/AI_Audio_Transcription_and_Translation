
import pysrt
from openai import OpenAI
import os
import re
import subprocess





class ShortsGenerator(object):

    def read_srt(self,file_path):
        print('Reading Srt file... @ShortsGenerator')
        subtitles = pysrt.open(file_path)
        return subtitles

    def extract_text(self,subtitles):
        print('extract text... @ShortsGenerator')
        text = ''
        for subtitle in subtitles:
            text += subtitle.text + ' '
        return text.strip()

    def get_important_scenes(self,text):
        # Load OpenAI API key
        print('Sending promot to Chatgpt... @ShortsGenerator')
        client = OpenAI(api_key=os.getenv('OPEN_AI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful videos editing assistant."},
                {"role": "user", "content": "Identify the important scenes from the following subtitles text return that by start times and end time,videos should be at less 30s and maximum 2 min, return minimum 1 and maximum 3 vidoes with format like this \"1. Arrival of Raymond Reddington at the FBI office - Start time: 00:00:39, End time: 00:01:17\":\n" + text}
            ],
            max_tokens=1500
        )
        # print(f" this out put : {response.choices[0].message.content}")
        important_scenes = response.choices[0].message
        print(f'Important Scenes from ChatGPT... @ShortsGenerator  {important_scenes}')
        return important_scenes

    def execute(self,srt_file_path):
        subtitles = self.read_srt(srt_file_path)
        text = self.extract_text(subtitles)
        important_scenes = self.get_important_scenes(text)
        return important_scenes


    def extract_scenes(self,input_text):
        scenes = []

        pattern = r'(?P<scene>\d+)\. (?P<description>.*?) - Start time: (?P<start>\d{2}:\d{2}:\d{2}), End time: (?P<end>\d{2}:\d{2}:\d{2})'

        matches = re.finditer(pattern, input_text)
        for match in matches:
            scene_data = match.groupdict()
            scenes.append(scene_data)

        return scenes


    def extract_video_scenes(self,video_file, scenes):
        print('Extracting Scenes... @ShortsGenerator')
        shorts_files_path_list = []

        # Output directory
        output_dir = "output/"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Process each scene
        counter = 1
        for scene in scenes:
            start_time = scene['start']
            end_time = scene['end']
            description = scene['description']
            print('Generating {description}... @ShortsGenerator')
            output_filename = os.path.join(output_dir, f"{counter}.mp4")
            shorts_files_path_list.append(output_filename)
            
            # ffmpeg command to extract scene
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-ss', start_time,
                '-to', end_time,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-b:a', '192k',
                output_filename,
                '-y'  # Overwrite output file if exists
            ]
            
            print('Running CMD FFMPEG {description}... @ShortsGenerator')
            subprocess.run(cmd, capture_output=True)
            counter += 1

        print(f'Generated all Scenes with file names {shorts_files_path_list}')
        
        return shorts_files_path_list
   

     

if __name__ == "__main__":
    srt_file_path = 's1.srt'
    path_video = '1.mp4'
    shorts_generator = ShortsGenerator()
    important_scenes = shorts_generator.execute(srt_file_path)
    print("Important Scenes:\n", shorts_generator.extract_scenes(important_scenes.content))
    shorts_generator.extract_video_scenes( path_video, shorts_generator.extract_scenes(important_scenes.content))
    print("Well Done")
