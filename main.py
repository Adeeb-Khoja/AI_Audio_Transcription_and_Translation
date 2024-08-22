

import json
from aws_uploader import HelperS3
from extract_audio import VideoHelper
from helpers.srt_generator import SRTGenerator
from moderator import DetoxifyModerator
from shorts_generator import ShortsGenerator
from subtitles import SubtitlesRenderer
from transcript_detect import *
from translation import *
import gradio as gr
from dotenv import load_dotenv
import ast
import os
from datetime import datetime 

def translate_segments(segments,translator: TranslationModel):
    transalted_segments = []
    for segment in segments:
        translated_segment_text = translator.translate_text(segment['text'])
        transalted_segments.append({'text':translated_segment_text,'start':segment['start'],'end':segment['end'],'id':segment['id']})
    
    return transalted_segments



def tab1_transcript(file,  progress=gr.Progress()):
    # Upload file to S3 first
    print('Upload file to S3 first')
    progress(0.0, desc="Uploading to S3...")
    HelperS3.folder_name = datetime.now().strftime("%m-%d-%Y,%H:%M:%S") + "/"
    HelperS3.aws_upload_file(file,HelperS3.bucket_name, os.path.basename(file))

    #Extracting the audio from video
    progress(0.1, desc="Extracting Audio From Video...")
    video_file_path = file
    audio_file_path = 'extracted_audio.mp3'
    video_helper = VideoHelper()
    print('Extracting audio from video...')
    video_helper.extract_audio(video_file_path, audio_file_path)


    whisper_model = WhisperModel('base')
    progress(0.2, desc="Loading Whisper Model...")

    print('Transcriping audio file....')
    progress(0.6, desc="Transcriping audio file....")
    transcription = whisper_model.transcribe_audio(audio_file_path)

    print('Generating transctipt text...')
    progress(0.7, desc="Generating Transcript...")
    transcript_text = whisper_model.get_text(transcription)

    print('Detecting audio language....')
    progress(0.8, desc="Detecting audio language....")
    detected_language = whisper_model.get_detected_language(transcription)

    print('Generating transcript segments...')
    progress(0.9, desc="Generating transcript segments with timestamps...")
    transcript_segments = whisper_model.get_segments(transcription)

    print('Done!!!')

    return transcript_text, detected_language, str(transcript_segments)


def tab2_translation(translate_to_lang,detected_language,transcript_text,transcript_segments, progress=gr.Progress()):
    
    # Translate transcript
    target_language = supported_languages[translate_to_lang]

    progress(0, desc="Loading Translation Model...")
    transcript_segments = ast.literal_eval(transcript_segments)

    translation_model = TranslationModel(detected_language,target_language)

    progress(0.2, desc="Translating Transcript...")
    print(f'Translating transcript text from {detected_language} to {target_language}...')
    translated_text = translation_model.translate_text(transcript_text)

    progress(0.6, desc="Translating Transcript Sgments...")
    print(f'Translating transcript segments from {detected_language} to {target_language}...')
    transalted_segments = translate_segments(transcript_segments,translation_model)
    
    print('Translation Done!!!')
    return translated_text, str(transalted_segments)


def tab3_srt(transcript_segments, translated_segments):

    original_srt_path = 'original.srt'
    translated_srt_path = 'translated.srt'
    print('Generating Main Language SRT file...')
    transcript_segments = ast.literal_eval(transcript_segments)
    SRTGenerator.generate_srt(transcript_segments,original_srt_path)


    print('Generating Translated Language SRT file...')
    translated_segments = ast.literal_eval(translated_segments)
    SRTGenerator.generate_srt(translated_segments,translated_srt_path)

    print('SRT files Done!!!')
    return original_srt_path, translated_srt_path


def tab4_detoxify(transcript_text, progress= gr.Progress()):
    #Run Moderator to detect toxicity
    progress(0, desc="Analyzing Toxicity...")
    print('Analyzing and detecing toxicity levels...')
    detoxify_moderator = DetoxifyModerator()
    result = detoxify_moderator.detect_toxicity(transcript_text)
    df = detoxify_moderator.format_results(result)

    print('Detoxify Done!!!')
    return df

def tab5_shorts(original_srt_file, video_file, progress = gr.Progress()):

    # Generate short videos from video
    shorts_generator = ShortsGenerator()
    progress(0, desc="Detecting Important Scenes...")
    print('Generating shorts from important scenes...')
    selected_scenes = shorts_generator.execute(original_srt_file)

    progress(0.5, desc="Extracting Shorts from Video...")
    shorts_path_list = shorts_generator.extract_video_scenes( video_file, shorts_generator.extract_scenes(selected_scenes.content))
    print('Generating Scenes Done!!!')

    return_shorts_list = shorts_path_list + [""] * (3 - len(shorts_path_list))
    print(f'Returned Shorts list to Gradio... {return_shorts_list}')

    progress(0.9, desc="Uploading Shorts to S3..")
    short_count = 1
    for short in shorts_path_list:
        print(f"Uploading short {short} to S3")
        HelperS3.aws_upload_file(short,os.getenv('AWS_BUCKET_NAME'),f"short_{short_count}.mp4")
        short_count += 1
        
    return return_shorts_list[0], return_shorts_list[1], return_shorts_list[2]


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
    target_language = supported_languages[translate_to_lang]
    translation_model = TranslationModel(detected_language,target_language )

    print(f'Translating transcript text from {detected_language} to {target_language}...')
    transalted_text = translation_model.translate_text(transcript_text)

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


def all_tabs_interface():
    with gr.Blocks() as demo:

        with gr.Tab("Transcript"):
            btn = gr.Button("Generate")
            #Tab 1
            tab1_input_video = gr.Video(label='Content Video')
            tab1_inputs = [tab1_input_video]

            tab1_output_transcript = gr.Textbox(label="Transcript",interactive=True,show_copy_button=True)
            tab1_output_detected_language = gr.Textbox(label="Detected Language")
            tab1_output_segments = gr.Textbox(label="Segments")
            tab1_outputs = [tab1_output_transcript ,tab1_output_detected_language, tab1_output_segments]
        
        with gr.Tab("Translation"):

            #Tab 2
            tab2_input_target_lang = gr.Dropdown(list(supported_languages.keys()),value='Arabic' )
            tab2_output_translated_transcript = gr.Textbox(label="Translated Transcript")
            tab2_output_translated_segments = gr.Textbox(label="Translated Segments")
            tab2_inputs = [tab2_input_target_lang, tab1_output_detected_language , tab1_output_transcript, tab1_output_segments]
            tab2_outputs = [tab2_output_translated_transcript, tab2_output_translated_segments]
        
        with gr.Tab("SRT"):

            #Tab 3
            tab3_inputs = [tab1_output_segments, tab2_output_translated_segments]
            tab3_output_original_srt = gr.File(label='Original SRT file' )
            tab3_output_translated_srt = gr.File(label='Translated SRT file')
            tab3_outputs = [tab3_output_original_srt, tab3_output_translated_srt]

        with gr.Tab("Toxicity"):

            #Tab 4
            tab4_inputs = [tab1_output_transcript]
            tab4_outputs = [gr.Dataframe(label='Toxicity Analysis')]

        with gr.Tab("Shorts"):
            #Tab 5
            tab5_inputs = [tab3_output_original_srt, tab1_input_video]
            tab5_outputs = [gr.Video(label=f"Short {i+1}") for i in range(3)]
        

        #Consecutive Operations
        btn.click(fn=tab1_transcript, inputs=tab1_inputs, outputs=tab1_outputs).then(
            fn= tab2_translation, inputs=tab2_inputs, outputs= tab2_outputs).then(
                fn=tab3_srt, inputs=tab3_inputs, outputs=tab3_outputs).then(
                    fn=tab4_detoxify, inputs= tab4_inputs, outputs= tab4_outputs).then(
                        fn=tab5_shorts, inputs=tab5_inputs, outputs=tab5_outputs)
                    
            
        



    demo.launch()
    # tab1 = gr.Interface(
    # fn=tab1_transcript,
    # inputs=tab1_inputs,
    # outputs=tab1_outputs,
    
    # )

    # gr.TabbedInterface(
    # [tab1], ["Transcript"]
    # ).launch()





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


#     inputs = [gr.Video(label='Content Video'),gr.Dropdown(list(supported_languages.keys()), label="Target Language"),gr.Checkbox(label="Generate Transcript"),
#             gr.Checkbox(label="Translate Transcript"),gr.Checkbox(label="Generate Subtitles"),gr.Checkbox(label="Generate Shorts")]
    
#     outputs = [gr.Textbox(label="Transcript"), gr.Textbox(label="Translation"),gr.DataFrame(label="Moderation Results"),gr.Video(label='Output Video with Subtitles')]
#     short_outputs = [gr.Video(label=f"Short {i+1}") for i in range(3)]
#     outputs.extend(short_outputs)
#     demo = gr.Interface(
#     fn=interface_function,
#     inputs=inputs,
#     outputs=outputs,
#     title="Rosetta AI",
#     description="Content Creation Customization"
# )
  
#     demo.launch()
    all_tabs_interface()
    