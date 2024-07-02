
import json

from altair import value
from matplotlib.streamplot import OutOfBounds
from sympy import substitution, viete
from extract_audio import VideoHelper
from helpers.srt_generator import SRTGenerator
from moderator import DetoxifyModerator
from shorts_generator import ShortsGenerator
from subtitles import SubtitlesRenderer
from transcript_detect import *
from translation import *
import gradio as gr
from dotenv import load_dotenv



def translate_segments(segments,translator: TranslationModel,from_lang,to_lang):
    transalted_segments = []
    for segment in segments:
        translated_segment_text = translator.translate_text(segment['text'],from_lang,to_lang)
        transalted_segments.append({'text':translated_segment_text,'start':segment['start'],'end':segment['end'],'id':segment['id']})
    
    return transalted_segments


def main(file,translate_to_lang):

    #Extracting the audio from video
    video_file_path = file
    audio_file_path = 'extracted_audio.mp3'
    video_helper = VideoHelper()
    print('Extracting audio from video...')
    video_helper.extract_audio(video_file_path, audio_file_path)


    whisper_model = WhisperModel('base')

    print('Transcriping audio file....')
    transcription = whisper_model.transcribe_audio(audio_file_path)

    print('Generating transctipt text...')
    transcript_text = whisper_model.get_text(transcription)

    print('Detecting audio language....')
    detected_language = whisper_model.get_detected_language(transcription)

    print('Generating transcript segments...')
    transcript_segments = whisper_model.get_segments(transcription)
    

    # Write the transcription to a text file
    print('Writing transcript into text file...')
    transcript_file_path = "transcript.txt"
    with open(transcript_file_path, "w",encoding="utf-8") as file:
        file.write(transcript_text)

    # Translate transcript
    translation_model = TranslationModel()
    target_language = supported_languages[translate_to_lang]

    print(f'Translating transcript text from {detected_language} to {target_language}...')
    transalted_text = translation_model.translate_text(transcript_text,detected_language,target_language)

    # print(f'Translating transcript segments from {detected_language} to {target_language}...')
    # transalted_segments = translate_segments(transcript_segments,translation_model,detected_language,target_language)

    # Write the translation to a text file
    print('Writing translation text file...')
    translation_file_path = "translation.txt"
    with open(translation_file_path, "w",encoding="utf-8") as file:
        file.write(transalted_text)

    print('Writing transcsript segments and translated segments to json file...')
    segments_file_path = "segments.json"
    with open(segments_file_path, "w",encoding="utf-8") as file:
        json.dump(transcript_segments, file,ensure_ascii=False)

    # print('Writing transcsript segments and translated segments to json file...')
    # translated_segments_file_path = "translated_segments.json"
    # with open(translated_segments_file_path, "w",encoding="utf-8") as file:
    #     json.dump(transalted_segments, file,ensure_ascii=False)

    #Run Moderator to detect toxicity
    print('Analyzing and detecing toxicity levels...')
    detoxify_moderator = DetoxifyModerator()
    result = detoxify_moderator.detect_toxicity(transcript_text)
    df = detoxify_moderator.format_results(result)


    #Render subtitles on video
    renderer = SubtitlesRenderer()
    subtitles_file_path = 'segments.json'
    output_file_path = 'subtitled_video.mp4'
    subtitled_video = renderer.add_subtitles(video_file_path,subtitles_file_path,output_file_path)


    
    # Generate short videos from video
    output_srt_file = 'subtitles.srt'
    print('Generating SRT file...')
    #Generate srt file
    SRTGenerator.generate_srt(transcript_segments,output_srt_file)
    shorts_generator = ShortsGenerator()
    print('Generating shorts from important scenes...')
    selected_scenes = shorts_generator.execute(output_srt_file)
    shorts_path_list = shorts_generator.extract_video_scenes( video_file_path, shorts_generator.extract_scenes(selected_scenes.content))

    return_shorts_list = shorts_path_list + [""] * (3 - len(shorts_path_list))
    

    return transcript_text, transalted_text, df, subtitled_video, return_shorts_list[0], return_shorts_list[1], return_shorts_list[2]



def interface_function(file,translate_to_lang,with_transcript=False,with_translations=False,with_subtitles=False,with_shorts=False):

    return main(file,translate_to_lang)

supported_languages = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Russian": "ru",
    "Arabic": "ar",
    "Hindi": "hi"
}

if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()


    inputs = [gr.Video(label='Content Video'),gr.Dropdown(list(supported_languages.keys()), label="Target Language"),gr.Checkbox(label="Generate Transcript"),
            gr.Checkbox(label="Translate Transcript"),gr.Checkbox(label="Generate Subtitles"),gr.Checkbox(label="Generate Shorts")]
    
    outputs = [gr.Textbox(label="Transcript"), gr.Textbox(label="Translation"),gr.DataFrame(label="Moderation Results"),gr.Video(label='Output Video with Subtitles')]
    short_outputs = [gr.Video(label=f"Short {i+1}") for i in range(3)]
    outputs.extend(short_outputs)
    demo = gr.Interface(
    fn=interface_function,
    inputs=inputs,
    outputs=outputs,
    title="Rosetta AI",
    description="Content Creation Customization"
)
    # with gr.Blocks() as demo:
    #     file_output = gr.File()
    #     upload_button = gr.UploadButton("Click to Upload a Video", file_types=["video"], file_count="single")
    #     upload_button.upload(main, upload_button, ['text','text'])



    demo.launch()
    