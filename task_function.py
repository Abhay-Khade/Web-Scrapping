import logging
import requests
import os
from collections import defaultdict, Counter
import csv
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
import re


class FUNCTION:
    def __init__(self, base_url, num_file, folder_path):
        self.base_url = base_url
        self.num_file = num_file
        self.folder_path = folder_path

    # Function to download the first 'num_files_to_download' text files from 'base_url'
    def download_files(self):
        try:
            logging.info("Download files Starting")
            # Send a GET request to the base URL
            response = requests.get(self.base_url)
            # If the request is successful (status code 200)
            if response.status_code == 200:
                # Parse the HTML content of the response
                soup = BeautifulSoup(response.content, 'html.parser')
                links = []
                counter = 0
                # Find all anchor tags (<a>) in the HTML content
                for a in soup.find_all('a'):
                    # Retrieve 'href' attributes containing links and filter for .txt files
                    if a['href'].endswith('.txt'):
                        counter += 1
                        links.append(a['href'])
                    if self.num_file == counter:
                        break
                # Create a folder to store downloaded files if it doesn't exist
                folder_path = 'Shakespeare_Plays'
                os.makedirs(folder_path, exist_ok=True)
                # Download each text file and save it to the folder
                for link in links:
                    file_url = (self.base_url + link)
                    file_name = link.split('/')[-1]
                    file_content = requests.get(file_url).text
                    file_path = os.path.join(folder_path, file_name)
                    # Save the content to a file in the folder
                    with open(file_path, 'w') as file:
                        file.write(file_content)
                        print(f"downloaded: {file_name}")
            logging.info("Download files Completed")
        except Exception as e:
            logging.error(f"Error when the file is download: {str(e)}")

    def get_line_word_count(self):
        try:
            logging.info("get line word count method starting")
            # Initialize an empty dictionary to store word counts for each line in each file
            file_line_word_count = defaultdict(dict)
            # Iterate through each file in the specified folder
            for file_name in os.listdir(self.folder_path):
                # Open the file in read mode
                with open(os.path.join(self.folder_path, file_name), 'r') as file:
                    lines = file.readlines()
                    # Iterate through each line in the file
                    line_number = 1
                    for line in lines:
                        words = line.split()
                        # Store the word counts for each line in the respective file in the main dictionary
                        file_line_word_count[file_name][line_number] = len(words)
                        line_number += 1
            # Return the dictionary containing line-wise word counts for each file
            logging.info("File line word count Completed")
            return file_line_word_count
        except Exception as e:
            logging.error(f"Error in line word count: {str(e)}")
            return defaultdict(dict)

    def count_lines_more_than_10_words(self):
        try:
            logging.info("Counting lines more than 10 words")
            # Initialize an empty dictionary to store counts of lines with more than 10 words
            lines_with_more_than_10_words = {}
            line_word_count = self.get_line_word_count()
            # Iterate through each file and its respective word count dictionary
            for file_name, lines_data in line_word_count.items():
                # Iterate through each line's word count in the file
                count = 0
                for words_count in lines_data.values():
                    # Check if the number of words in the line is greater than 10
                    if words_count > 10:
                        # Increment the count if the line has more than 10 words
                        count += 1
                # Store the count of lines with more than 10 words for the current file
                lines_with_more_than_10_words[file_name] = count
            # Return the dictionary containing counts of lines with more than 10 words for each file
            logging.info("Counting lines more than 10 words Completed")
            return lines_with_more_than_10_words
        except Exception as e:
            logging.error(f"Error in counting lines more than 10 words, {str(e)}")
            return {}

    def get_characters(self):
        try:
            logging.info("all files finding character Starting")
            # Initialize dictionaries to store word count and most common words for characters
            all_files_character_word_count = dict()
            all_files_character_most_common_10_words = dict()
            # Iterate through each file in the specified folder
            for file_name in os.listdir(self.folder_path):
                with open(os.path.join(self.folder_path, file_name), 'r') as file:
                    intro_flag = True
                    characters = set()
                    character_words_dict = dict()
                    character_words_count = dict()

                    lines = file.readlines()
                    for line in lines:
                        # Loop through each line in the file
                        if line.find('SCENE') != -1:
                            # Mark that the scene introduction is over
                            intro_flag = False

                        if intro_flag:
                            # pattern 1 (---:)
                            firstChar = line.find('(')
                            lastChar = line.find(':)')
                            if firstChar != -1 and lastChar != -1:
                                char = line[firstChar + 1:lastChar]
                                characters.add(char)
                            # pattern 2 |
                            elif line.find('|') != -1:
                                lst = line.split()
                                if lst[0] != '|':
                                    characters.add(lst[0])
                            # pattern 3 upper case
                            else:
                                if line[0] != '\t':
                                    lst = line.split()
                                    if len(lst) > 0 and lst[0].isupper():
                                        characters.add(lst[0])
                        # logic to get words spoken by characters
                        else:
                            if line.strip() == '':
                                continue
                            if line.split()[0] in characters:
                                char = line.split()[0]
                                # Count words spoken by each character and store them in respective dictionaries
                                if char not in character_words_dict.keys():
                                    character_words_dict[char] = len(line.split()) - 1
                                    character_words_count[char] = line.split()[1:]
                                else:
                                    if line.split()[0] in characters:
                                        character_words_dict[char] += len(line.split()) - 1
                                        character_words_count[char] += line.split()[1:]
                                    else:
                                        character_words_dict[char] += len(line.split())
                                        character_words_count[char] += line.split()

                            else:
                                if char in character_words_dict.keys():
                                    character_words_dict[char] += len(line.split())
                                    character_words_count[char] += line.split()

                    most_occur_by_char = dict()
                    # Find the most common 10 words spoken by each character
                    for char in character_words_count.keys():
                        Cntr = Counter(character_words_count[char])
                        most_occur = Cntr.most_common(10)
                        most_occur_by_char[char] = most_occur
                    # Store the results in the main dictionaries for each file
                    all_files_character_word_count[file_name] = character_words_dict
                    all_files_character_most_common_10_words[file_name] = most_occur_by_char
            logging.info("We get all files character and there words Spoken, 10 most occur words by character ")
            return all_files_character_word_count, all_files_character_most_common_10_words
        except Exception as e:
            logging.error(f"Error in Get Character in method, {str(e)}")
            return {},{}

    def create_csv(self):
        try:
            logging.info(" Creating CSV File Starting ")
            csv_filename = 'shakespeare_info.csv'
            csv_filename2 = 'shakespeare_info2.csv'
            csv_filename3 = 'shakespeare_info3.csv'
            csv_filename4 = 'shakespeare_info4.csv'
            csv_filename5 = 'shakespeare_info5.csv'
            file_info = []
            file_info2 = []
            file_info3 = []
            file_info4 = []
            file_info5 = []

            line_word_count = self.get_line_word_count()
            more_than_10_words = self.count_lines_more_than_10_words()
            all_files_character_word_count, all_files_character_most_common_10_words = self.get_characters()

            for file_name in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, file_name)
                file_size = os.path.getsize(file_path)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                absolute_path = os.path.abspath(file_path)

                file_info.append({
                    'file_name': file_name,
                    'Size(bytes)': file_size,
                    'Last Modified Datetime': modified_time,
                    'Absolute Path': absolute_path
                })

                file_info2.append({
                    'file_name': file_name,
                    'line_word_count': line_word_count[file_name]
                })

                file_info3.append({
                    'file_name': file_name,
                    'more_than_10_words': more_than_10_words[file_name]
                })
                file_info4.append({
                    'file_name': file_name,
                    'character_word_count': all_files_character_word_count[file_name]
                })

                file_info5.append({
                    'file_name': file_name,
                    'most_common_10_words': all_files_character_most_common_10_words[file_name]
                })

            df = pd.DataFrame(file_info)
            df2 = pd.DataFrame(file_info2)
            df3 = pd.DataFrame(file_info3)
            df4 = pd.DataFrame(file_info4)
            df5 = pd.DataFrame(file_info5)

            df.to_csv(csv_filename, index=False, mode='w')

            df2.to_csv(csv_filename2, index=False, mode='w')

            df3.to_csv(csv_filename3, index=False, mode='w')

            df4.to_csv(csv_filename4, index=False, mode='w')

            df5.to_csv(csv_filename5, index=False, mode='w')

            logging.info("CSV File Created ")
        except Exception as e:
            logging.error(f"Error in creating CSV: {str(e)}")


