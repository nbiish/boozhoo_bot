# Import the required libraries
import gradio as gr
import openai
from gtts import gTTS


messages = [{"role": "system", "content": 'You are the Anishinaabe hero Nanaboozhoo. Not only do you answer with profound wisdom but you will continue the conversation by answering like this, Boozhoo: (your answer)'}]
full_transcript = []
openai.api_key = ""
audio_file = 'response.mp3'


def set_api(my_key):
    openai.api_key = my_key


def create_image(response):
    # Send text to be summarized
    dalle_prompt = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "user", "content": f'Summarize this text "{response["choices"][0]["message"]["content"]}" into a short and concise Dall-E 2 prompt starting with "A Professional 35mm photograph of an Anishinaabe person saying :(summarization)".'}
        ]
    )
    # Use summary as prompt for pic
    dalle_summary = openai.Image.create(
            prompt = dalle_prompt["choices"][0]["message"]["content"],
            size="512x512"
        )
    image_url = dalle_summary['data'][0]['url']
    return image_url


def speak(system_message):
    global audio_file
    content = system_message['content']
    tts = gTTS(content, lang='en', slow=False)
    tts.save("response.mp3")
    return "response.mp3"


def clear_chat():
    global full_transcript
    full_transcript = []
    return "Cleared"


def transcribe(gradio_input, api_key, clear_button):
    global messages
    global full_transcript
    global audio_file
    set_api(api_key)
    
    #Create file and run it through whisper
    audio_file = open(gradio_input, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    #Append content to messages
    full_transcript.append(transcript["text"])
    messages.append({"role": "user", "content": transcript["text"]})


    #Send the latest set of messages to OpenAI to get a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    # Extract the latest system message from the response and add it as a new message to the messages list
    system_message = response["choices"][0]["message"]
    messages.append(system_message)


    pic_url = create_image(response)
    speech = speak(system_message)

    clear_button = clear_chat()


    # Combine all messages in the messages list to create a chat transcript
    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"


    return speech, chat_transcript, pic_url, clear_button



MY_INFO = '\nSupport me at my [Linktree](https://linktr.ee/Nbiish).'
API_INFO = 'Get your api key at [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)'


# Create a Gradio interface 
demo = gr.Interface(
    fn=transcribe,
    inputs=[
        gr.Audio(source="microphone", type="filepath", show_label=False),
        gr.Textbox(
            label="OpenAI API Key",
            lines=1,
            placeholder="Enter your OpenAI API key",
            default=None,
            type="password",
            fn=set_api,
        ),
    ],
    outputs=[
        gr.Audio(show_label=False),
        gr.Textbox(label="Transcript:"),
        gr.Image(show_label=False),
    ],
    title="Boozhoo Bot",
    description=f"""
    Anishinaabe Chatbot

    Applies OpenAI's Whisper to transcribe audio input.
    GPT-3.5 Turbo to generate a response.
    Dall-E 2.0 to generate an image.
    gTTS to generate audio response.

    1) Record to get started
    2) Press X near recording to keep going
    3) Refresh page to restart

    {MY_INFO}
    {API_INFO}

    """, 
)


if __name__ == "__main__":
    demo.queue(api_open=False, max_size=28,).launch()