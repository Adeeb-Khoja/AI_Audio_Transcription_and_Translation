import gradio as gr

io1 = gr.Interface(
    lambda x, y, z: "sax.wav",
    [
        gr.Slider(label="pitch"),
        gr.Slider(label="loudness"),
        gr.Audio(label="base audio file (optional)"),
    ],
    gr.Audio(),
)

io2 = gr.Interface(
    lambda x, y, z: "flute.wav",
    [
        gr.Slider(label="pitch"),
        gr.Slider(label="loudness"),
        gr.Audio(label="base audio file (optional)"),
    ],
    gr.Audio(),
)

gr.TabbedInterface(
    [io1, io2], ["Saxophone", "Flute"]
).launch()