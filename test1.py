import speech_recognition as sr
import openai
import pyttsx3
import config
import time

# Set up speech recognition
r = sr.Recognizer()

# Set up text to speech
engine = pyttsx3.init()

# Set up OpenAI API key
openai.api_key = config.OPENAI_API_KEY

while True:
    # Listen for user speech
    with sr.Microphone() as source:
        print("Listening for user speech")
        audio = r.listen(source)
    
    # Process speech with speech to text
    try:
        text = r.recognize_google(audio)
        print("You said:", text)
        
        # Send processed speech as prompt to OpenAI's DaVinci model
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            max_tokens=256,
            temperature=0.7
        )
        
        # Get response from OpenAI and use text to speech to speak it out loud
        if response.choices[0].text:
            print(response.choices[0].text)

            engine.say(response.choices[0].text)
            engine.runAndWait()
            
    except Exception as e:
        print("Error:", str(e))
    
    # Wait for 1 seconds before listening again
    time.sleep(1)
