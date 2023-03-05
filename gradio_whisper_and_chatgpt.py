# Import the required libraries
import gradio as gr
import openai, config, subprocess

# Set up OpenAI API key
openai.api_key = config.OPENAI_API_KEY

# Create a list of dictionary messages which will store the bot responses
messages = [{"role": "system", "content": 'You are a therapist. Respond to all input in 25 words or less.'}]

# Define a function that transcribes audio from the microphone, sends it to OpenAI's GPT-3 model 
# and returns the chat transcript
def transcribe(audio):
    global messages
    
    # Print the audio file for debugging purposes
    print(audio)

    # Open the audio file and send it to OpenAI's transcription API
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
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
    print(response)

    # Extract the latest system message from the response and add it as a new message to the messages list
    system_message = response["choices"][0]["message"]
    messages.append(system_message)

    # Combine all messages in the messages list to create a chat transcript
    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    # Return the chat transcript
    return chat_transcript

# Create a Gradio interface to capture audio input from the user, pass it to the transcribe function
# and display the resulting chat transcript
ui = gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs="text").launch()
ui.launch()
