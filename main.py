from task_function import FUNCTION
import os
import logging
import configparser

if __name__ == "__main__":

    modules = ['requests', 'os', 'collections', 'csv', 'datetime', 'urllib', 'bs4', 'pandas', 're','logging','configparser']
    for module in modules:
        try:
            __import__(module)
        except:
            os.system("pip install " + module)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="information.log"
    )



    config_object = configparser.ConfigParser()
    config_object.read("Play.config")

    URL_sec = config_object["URL"]
    base_url = URL_sec["base_url"]

    NUM_sec = config_object["NUM_FILES"]
    num_file_to_download = NUM_sec["num_file_to_download"]

    # base_url = "http://www.textfiles.com/etext/AUTHORS/SHAKESPEARE/"
    # num_file_to_download = 5

    func = FUNCTION(base_url, num_file_to_download, folder_path='Shakespeare_Plays')

    # Download first 5 text files (Shakespeare’s plays) from the following URL using a python script
    # func.download_files()

    # Get all { file name : { line number : number of words in the line } } combinations in a dictionary.

    line_word_count = func.get_line_word_count()
    print(line_word_count)

    # Find number of lines with more than 10 words in each file.

    lines_more_than_10_words = func.count_lines_more_than_10_words()
    print(lines_more_than_10_words)

    # Count words by character and find 10 words spoken by each character
    all_files_character_word_count, all_files_character_most_common_10_words = func.get_characters()

    # create CSV with file information

    func.create_csv()
