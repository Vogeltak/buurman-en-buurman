import glob
import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-002",
  generation_config=generation_config,
  system_instruction="Determine who is in this frame from the animated series Pat & Mat. Pat wears yellow and Mat wears grey or red. Respond only with a valid JSON object following this schema:\n\n```{\"pat\": boolean,\"mat\": boolean}```",
)

# files = [
#   upload_to_gemini(frame, mime_type="image/jpeg") for frame in glob.glob("episodes/01_Geknoei-*.jpg")
# ]

files = [
  genai.get_file("t22mnqa32q77")
]

print([frame.display_name for frame in files])

results = [
    model.generate_content([frame]) for frame in files
]

print(results)
