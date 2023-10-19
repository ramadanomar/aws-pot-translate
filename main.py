import boto3
import polib
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


def main(pot_file, target_po_file):
    # Load your .pot file
    pot = polib.pofile(pot_file)

    # Create a new .po file object
    po = polib.POFile()

    # Copy metadata from the original .pot file
    po.metadata = pot.metadata

    # Iterate over .pot file entries
    for entry in pot:
        # Skip entries that don't need translation
        if not entry.msgid:
            continue

        # Translate the text
        translated_text = translate_text(entry.msgid, 'en', 'ro')

        # Create a new POEntry with translated text
        new_entry = polib.POEntry(
            msgid=entry.msgid,
            msgstr=translated_text
        )

        # Add the new entry to the .po file object
        po.append(new_entry)

    # Save the translations to a new .po file
    po.save(target_po_file)
    print(f"Translation completed. The translated file is saved as '{target_po_file}'.")


if __name__ == "__main__":
    # Path to the original .pot file
    pot_file_path = 'porto.pot'

    # Specify the name of the target .po file
    target_po_file_path = 'ro_RO.po'

    # Ensure the paths are absolute
    abs_pot_file_path = os.path.abspath(pot_file_path)
    abs_target_po_file_path = os.path.abspath(target_po_file_path)

    main(abs_pot_file_path, abs_target_po_file_path)
