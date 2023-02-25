import os
import glob
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator, exceptions
from multiprocessing import Pool, freeze_support

# The target language
target_lang = "hi"

elements = ['p', 'title', 'span', 'button', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'i', 'strong', 'em', 'blockquote', 'pre', 'code', 'ul', 'ol', 'li', 'table','tr']
allowed_attrs = ['placeholder', 'value', 'input', 'textarea', 'title', 'alt']

# Initialize the translator object
translator = GoogleTranslator(source='en', target=target_lang)

print(f"Ininitalizing translator...")

# Load the list of files that have already been translated
translated_files = set()
if os.path.exists('translated_files.txt'):
    with open('translated_files.txt', 'r') as f:
        translated_files = set(line.strip() for line in f)

# Define a function to translate a batch of files
def translate_files(files):
    for file in files:
        if file in translated_files:
            print(f"Skipping {file} as it is already translated.")
            continue
        print(f"Translating {file}")
        # Read the HTML file and parse it with BeautifulSoup
        with open(file, "r", encoding="utf-8") as f:
            html_content = f.read()
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
                    if translation is not None:
                        text.string.replace_with(translation)
                except exceptions.NotValidPayload:
                    print(f"Could not translate: {text.string}")
            # Check if element has attributes
            if text.attrs:
                for attr in text.attrs:
                    # Check if the attribute is allowed and does not exceed the limit
                    if attr in allowed_attrs and text[attr] and len(text[attr]) <= 5000:
                        try:
                            # Translate the attribute to Hindi
                            translation = translator.translate(text[attr])
                            # Replace the original attribute value with the translated text
                            text[attr] = translation
                        except exceptions.NotValidPayload:
                            print(f"Could not translate attribute: {text[attr]}")
            print(f"Translated {file}")
        # Write the modified HTML back to the file
        with open(file, "w", encoding="utf-8") as f:
            f.write(str(soup))
        # Add the file to the list of translated files
        translated_files.add(file)

    # Save the list of translated files to a file
    with open('translated_files.txt', 'w') as f:
        for file in translated_files:
            f.write(file + '\n')

# Get a list of all the HTML files to translate
files = glob.glob("./web/*.html")

# If no files are found, print a message and exit
if not files:
    print("No HTML files found in directory.")
    exit()

# If only one file is found, translate it directly without creating batches
if len(files) == 1:
    translate_files(files)
    exit()

if __name__ == '__main__':
    freeze_support()

    # Divide the list of files into batches
    num_processes = os.cpu_count()
    batch_size = max(len(files) // num_processes, 1)
    batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]

    # Create a pool of processes to translate each batch in parallel
    with Pool(processes=num_processes) as pool:
        pool.map(translate_files, batches)
