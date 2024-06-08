
import json

from altair import value
from sympy import substitution, viete
from extract_audio import VideoHelper
from moderator import DetoxifyModerator
from subtitles import SubtitlesRenderer
from transcript_detect import *
from translation import *
import gradio as gr

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

    print(f'Translating transcript segments from {detected_language} to {target_language}...')
    transalted_segments = translate_segments(transcript_segments,translation_model,detected_language,target_language)

    # Write the translation to a text file
    print('Writing translation text file...')
    translation_file_path = "translation.txt"
    with open(translation_file_path, "w",encoding="utf-8") as file:
        file.write(transalted_text)

    print('Writing transcsript segments and translated segments to json file...')
    segments_file_path = "segments.json"
    with open(segments_file_path, "w",encoding="utf-8") as file:
        json.dump(transcript_segments, file,ensure_ascii=False)

    print('Writing transcsript segments and translated segments to json file...')
    translated_segments_file_path = "translated_segments.json"
    with open(translated_segments_file_path, "w",encoding="utf-8") as file:
        json.dump(transalted_segments, file,ensure_ascii=False)

    #Run Moderator to detect toxicity
    detoxify_moderator = DetoxifyModerator()
    result = detoxify_moderator.detect_toxicity(transcript_text)
    df = detoxify_moderator.format_results(result)


    #Render subtitles on video
    renderer = SubtitlesRenderer()
    subtitles_file_path = 'segments.json'
    output_file_path = 'subtitled_video.mp4'
    subtitled_video = renderer.add_subtitles(video_file_path,subtitles_file_path,output_file_path)

    return transcript_text, transalted_text, df, subtitled_video


supported_languages = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Russian": "ru",
    "Arabic": "ar",
    "Hindi": "hi"
}

if __name__ == '__main__':

    demo = gr.Interface(
    fn=main,
    inputs=[gr.Video(label='Content Video'),gr.Dropdown(list(supported_languages.keys()), label="Target Language")],
    outputs=[gr.Textbox(label="Transcript"), gr.Textbox(label="Translation"),gr.DataFrame(label="Moderation Results"),gr.Video(label='Output Video with Subtitles')],
    title="AI Content Customzier",
    description="Upload a video file to get customizations"
)
    # with gr.Blocks() as demo:
    #     file_output = gr.File()
    #     upload_button = gr.UploadButton("Click to Upload a Video", file_types=["video"], file_count="single")
    #     upload_button.upload(main, upload_button, ['text','text'])



    demo.launch()
    