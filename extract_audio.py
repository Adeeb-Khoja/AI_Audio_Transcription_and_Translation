from moviepy.editor import VideoFileClip


class VideoHelper(object):
    def extract_audio(self,video_path, audio_path):
        # Load the video file
        video = VideoFileClip(video_path)
        
        # Extract the audio
        audio = video.audio
        
        # Write the audio to a file
        audio.write_audiofile(audio_path)
        
        # Close the video clip
        video.close()


