import boto3
import polib
import json
import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

translate = session.client('translate')


def translate_text(text, source_language, target_language):
    """Translate text from source language to target language using Amazon Translate."""
    result = translate.translate_text(
        Text=text,
        SourceLanguageCode=source_language,
        TargetLanguageCode=target_language
    )
    return result.get('TranslatedText')


def translate_po_or_pot_file(input_file, target_po_file, source_language='en', target_language='ro'):
    """Translate entries in a .po or .pot file and save to a new .po file."""
    # Load your .po or .pot file
    po_file = polib.pofile(input_file)

    # Create a new .po file object to save the translations
    translated_po = polib.POFile()

    # Copy metadata from the original .po/.pot file
    translated_po.metadata = po_file.metadata

    # Iterate over entries in the .po/.pot file
    for entry in po_file:
        # Skip entries that don't need translation (msgid is empty)
        if not entry.msgid:
            continue

        # Check if it's a .po file and if there's already a translation
        if entry.msgstr:
            # Skip already translated entries (optional behavior, you can overwrite if needed)
            continue

        # Translate the text
        translated_text = translate_text(
            entry.msgid, source_language, target_language)

        # Create a new POEntry with the translated text
        new_entry = polib.POEntry(
            msgid=entry.msgid,
            msgstr=translated_text
        )

        # Add the new entry to the translated .po file object
        translated_po.append(new_entry)

    # Save the translations to the new .po file
    translated_po.save(target_po_file)
    print(f"Translation completed. The translated file is saved as '{
          target_po_file}'.")


def translate_json_file(json_file, target_json_file, source_language='en', target_language='ro'):
    """Translate entries in a JSON file and save to a new JSON file."""
    # Load the JSON file
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Recursively translate all string values in the JSON
    def translate_dict(d):
        for key, value in d.items():
            if isinstance(value, str):
                d[key] = translate_text(
                    value, source_language, target_language)
            elif isinstance(value, dict):
                translate_dict(value)
            elif isinstance(value, list):
                d[key] = translate_list(value)
        return d

    def translate_list(l):
        for index, item in enumerate(l):
            if isinstance(item, str):
                l[index] = translate_text(
                    item, source_language, target_language)
            elif isinstance(item, dict):
                translate_dict(item)
            elif isinstance(item, list):
                l[index] = translate_list(item)
        return l

    # Translate the data
    translated_data = translate_dict(data)

    # Save the translated data to a new JSON file
    with open(target_json_file, 'w', encoding='utf-8') as file:
        json.dump(translated_data, file, ensure_ascii=False, indent=4)
    print(f"Translation completed. The translated file is saved as '{
          target_json_file}'.")


def po_main():
    # Path to the original .po or .pot file
    input_file_path = 'data/ro.po'  # Adjust the file path as needed

    # Specify the name of the target .po file
    target_po_file_path = 'translated/ro_translated.po'

    # Ensure the paths are absolute
    abs_input_file_path = os.path.abspath(input_file_path)
    abs_target_po_file_path = os.path.abspath(target_po_file_path)

    translate_po_or_pot_file(abs_input_file_path, abs_target_po_file_path)


def json_main():
    # Path to the original JSON file
    json_file_path = 'data/en.default.json'

    # Specify the name of the target JSON file
    target_json_file_path = 'translated/ro.json'

    # Ensure the paths are absolute
    abs_json_file_path = os.path.abspath(json_file_path)
    abs_target_json_file_path = os.path.abspath(target_json_file_path)

    translate_json_file(abs_json_file_path, abs_target_json_file_path)


def main():
    # Select the main function depending on the file type you want to translate
    po_main()
    # json_main()


if __name__ == "__main__":
    main()
