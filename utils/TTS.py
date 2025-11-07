import io
import wave
from piper import PiperVoice

## While cooking some food I thought hmm, I think we could cache all the audio bytes and save it for use later
## Since we have the words cached already why not the audio too?
## It may not be great for large scale use but for this project it should be fine
## But it's also whatever cuz I don't wanna spend money on Google TTS API calls atm

voice = PiperVoice.load("./model/en_US-lessac-medium.onnx")

def synthesize_text_to_wav(text: str, output_filename: str) -> None:
    with wave.open(output_filename, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

def synthesize_text_to_wav_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        data = voice.synthesize(text)
        first_chunk = True
        
        for audio_chunk in data:
            if first_chunk:
                wav_file.setnchannels(audio_chunk.sample_channels)
                wav_file.setsampwidth(audio_chunk.sample_width)
                wav_file.setframerate(audio_chunk.sample_rate)
                first_chunk = False
            
            wav_file.writeframes(audio_chunk.audio_int16_bytes)
    
    return buffer.getvalue()

if __name__ == "__main__":
    sample_text = "Hello, this is a sample text to speech synthesis using Piper."
    # output_file = "./audio/output.wav"
    # synthesize_text_to_wav(sample_text, output_file)
    # print(f"Synthesized speech saved to {output_file}")

    wav_bytes = synthesize_text_to_wav_bytes(sample_text)
    print(type(wav_bytes))

