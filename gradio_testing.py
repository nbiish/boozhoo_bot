# Import the required libraries
import gradio as gr
import openai, config, subprocess
import pyttsx3

# Set up OpenAI API key
openai.api_key = config.OPENAI_API_KEY

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voices', voices[2].id)

# Create a list of dictionary messages which will store the bot responses
messages = [{"role": "system", "content": 'You are the Anishinaabe hero Nanaboozhoo. Not only do you answer with profound wisdom but you will continue the conversation by answering like this, Boozhoo: (your answer)'}]

full_transcript = []
# Define a function that transcribes audio from the microphone, sends it to OpenAI's GPT-3 model 
# and returns the chat transcript
def transcribe(audio):
    global messages
    global full_transcript
    
    # Print the audio file for debugging purposes
    print(audio)

    # Open the audio file and send it to OpenAI's transcription API
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    full_transcript.append(transcript["text"])
    # Print the transcription for debugging purposes
    print(transcript)

    # Add the user's transcription to the messages list as a new dictionary
    messages.append({"role": "user", "content": transcript["text"]})

    # Send the latest set of messages to OpenAI's GPT-3 model to get a response message
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    # For debugging purposes, print the response message
    print("HERE IS THE RESPONSE" + "\n")
    print(response)

    # Extract the latest system message from the response and add it as a new message to the messages list
    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    # Create Dall-e specific prompt from response
    dalle_prompt = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "user", "content": f'Summarize this text "{response["choices"][0]["message"]["content"]}" into a short and concise Dall-e2 prompt.'}
        ]
    )
    # Prompt Dall-e and give URL to image
    dalle_response = openai.Image.create(
            prompt = dalle_prompt["choices"][0]["message"]["content"],
            size="512x512"
        )
    image_url = dalle_response['data'][0]['url']



    # Speak most recent response
    engine.say(system_message['content'])
    engine.runAndWait()

    # Combine all messages in the messages list to create a chat transcript
    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    print(chat_transcript)

    # Return the chat transcript
    return image_url, chat_transcript



# Create a Gradio interface to capture audio input from the user, pass it to the transcribe function
# and display the resulting chat transcript
speech_interface = gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs=["image", "text"], title="Just WOW")


speech_interface.launch()