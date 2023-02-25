import os
import chardet
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator, exceptions

# The HTML file to translate
input_file = "web/algorithms-and-data-structures.html"

# The target language
target_lang = "hi"

elements = ['p','title','span','button','h1','h2','h3','h4','h4','h5','h6','a','i','strong']

# Initialize the translator object
translator = GoogleTranslator(source='auto', target=target_lang)

# Read the HTML file and parse it with BeautifulSoup
with open(input_file, "rb") as f:
    content = f.read()
    # Detect the encoding of the file
    encoding = chardet.detect(content)['encoding']
    # Decode the content using the detected encoding
    html_content = content.decode(encoding)
soup = BeautifulSoup(html_content, "html.parser")

# Loop through all the text elements in the HTML
for text in soup.find_all(elements):
    # Skip script, style, and non text elements
    if text.parent.name in ["script", "style", "img", "video", "audio"]:
        continue
    # Check if the input text is valid and does not exceed the limit
    if text.string and len(text.string) <= 5000:
        try:
            # Translate the text to Hindi
            translation = translator.translate(text.string)
            # Replace the original text with the translated text
            text.string.replace_with(translation)
        except exceptions.NotValidPayload:
            print(f"Could not translate: {text.string}")
# Write the modified HTML back to the file
with open(input_file, "w", encoding="utf-8") as f:
    f.write(str(soup))
