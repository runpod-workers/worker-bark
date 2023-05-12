#!/usr/bin/env python
''' Contains the handler function that will be called by the serverless. '''
import os
from bark import preload_models, generate_audio, SAMPLE_RATE
from scipy.io.wavfile import write as write_wav

import runpod
from runpod.serverless.utils import rp_download, rp_cleanup, rp_upload
from runpod.serverless.utils.rp_validator import validate

from schemas import INPUT_SCHEMA

# Load the Bark models
preload_models()


def generate_bark_audio(job):
    job_input = job["input"]

    # Input validation
    validated_input = validate(job_input, INPUT_SCHEMA)

    if 'errors' in validated_input:
        return {"error": validated_input['errors']}
    validated_input = validated_input['validated_input']

    # Generate audio from text
    text_prompt = validated_input['text_prompt']
    voice_preset = validated_input.get('voice_preset', None)
    audio_array = generate_audio(text_prompt, history_prompt=voice_preset)

    # Save audio to disk
    output_path = os.path.join('/tmp', f"{job['id']}_bark_audio.wav")
    write_wav(output_path, SAMPLE_RATE, audio_array)

    # Upload the audio file to the S3 bucket
    audio_filename = f"{job['id']}_bark_audio.wav"
    audio_file_url = rp_upload.upload_file_to_bucket(audio_filename, output_path)

    # Cleanup
    rp_cleanup.clean(['/tmp'])

    return {"audio_file_url": audio_file_url}


runpod.serverless.start({"handler": generate_bark_audio})
