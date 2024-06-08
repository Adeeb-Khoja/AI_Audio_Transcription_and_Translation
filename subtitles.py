from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import json


class SubtitlesRenderer(object):

    def add_subtitles(self,video_file, subtitle_file, output_file):
        # Load subtitle data from JSON
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            subtitles = json.load(f)
        
        # Load the video
        video = VideoFileClip(video_file)
        
        # Initialize an array to store TextClips
        text_clips_list = []

        # Define the maximum width for the subtitles
        max_width = video.size[0] - 40  # Adjust as needed, leaving some padding on the sides
        
        
        # Create TextClips for each subtitle
        for subtitle in subtitles:
            text = subtitle['text']
            start_time = subtitle['start']
            end_time = subtitle['end']
            
            # Create TextClip with subtitle text
            txt_clip = TextClip(text, fontsize=28, color='white', font='Arial', method='caption',size=(max_width, None),stroke_color='black',
            stroke_width= 0.5, bg_color='black',)
            
            # Set the duration of the subtitle
            txt_clip = txt_clip.set_duration(end_time - start_time)
            
            # Position the subtitle at the bottom
            txt_clip = txt_clip.set_position(('center', 'bottom'))
            
            # Add TextClip to the array
            text_clips_list.append(txt_clip.set_start(start_time))
        
        # Composite all TextClips onto the video
        #final_clip = video.fl(compose_text, text_clips_list)
        # Composite all TextClips onto the video
        final_clip = CompositeVideoClip([video] + text_clips_list)
        
        # Write the result to a file
        final_clip.write_videofile(output_file, codec='libx264', fps=video.fps, audio_codec='aac',
                                    ffmpeg_params=["-vf", "format=yuv420p"])  # Add this for compatibility

        return output_file
    # def compose_text(self,frame, t, text_clips):
    #     # Select the appropriate TextClips for the current time t
    #     current_clips = [text_clip for text_clip in text_clips if text_clip.start < t < text_clip.end]
        
    #     # Composite the selected TextClips onto the frame
    #     for clip in current_clips:
    #         frame = frame.blit(clip.get_frame(t - clip.start), clip.pos)
    #     return frame

if __name__ == '__main__':
    video_file = 'video.mp4'
    subtitle_file = 'segments.json'
    output_file = 'output_video_with_subtitles.mp4'

    renderer = SubtitlesRenderer()
    renderer.add_subtitles(video_file, subtitle_file, output_file)

