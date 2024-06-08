from pydub import AudioSegment
from pydub.silence import split_on_silence
import os



def split_audio(audio_path, min_silence_len=500, silence_thresh=-40, keep_silence=250):
    # Load audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Split audio on silence
    chunks = split_on_silence(audio, 
    min_silence_len=min_silence_len, 
    silence_thresh=silence_thresh, 
    keep_silence=keep_silence)
    return chunks

def format_time(ms):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def create_srt(transcript_chunks, audio_chunks, srt_file):
    srt_content = ""
    
    start_time = 0
    for i, (text, audio_chunk) in enumerate(zip(transcript_chunks, audio_chunks)):
        end_time = start_time + len(audio_chunk)
        
        start_time_str = format_time(start_time)
        end_time_str = format_time(end_time)
        
        srt_content += f"{i+1}\n"
        srt_content += f"{start_time_str} --> {end_time_str}\n"
        srt_content += f"{text}\n\n"
        
        start_time = end_time  # Update start time for next chunk
    
    with open(srt_file, "w", encoding="utf-8") as file:
        file.write(srt_content)

# Example usage
if __name__ == "__main__":
    
    # Path to your audio file
    audio_file_path = "your_audio_file.wav"
    srt_file_path = "subtitles.srt"
    
    transcript = 'Hey, I\'m the default speaker from the quality sign, Danny... throw around your audience... and introduce them to your products... through one of the most interesting and interesting marketing methods.'

    # Split transcript into chunks based on punctuation (simple splitting for this example)
    transcript_chunks = transcript.split('. ')
    
    # Split audio into chunks based on silence
    audio_chunks = split_audio(audio_file_path)
    
    # Ensure the number of transcript chunks matches the number of audio chunks
    if len(transcript_chunks) != len(audio_chunks):
        raise ValueError("The number of transcript chunks does not match the number of audio chunks")
    
    # Create SRT file
    create_srt(transcript_chunks, audio_chunks, srt_file_path)
    
    print(f"Subtitles written to {srt_file_path}")
