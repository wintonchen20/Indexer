from bs4 import BeautifulSoup
import lxml
import re
import os
from nltk.tokenize.regexp import regexp_tokenize
from nltk.stem import PorterStemmer
import math
import numpy as np
import json
import shutil
import zlib

"""
1. Implemented exact and similar duplicate checks using crc and simhash methods.
2. 
"""

class module_1():
    def __init__(self):
        self.docID = 0  #Variable to implement a docID
        self.docID_hashmap = {} #{token:{docID:[word_positions]}}
        #self.rootdir = r"C:\Users\Winton Chen\Desktop\CS 121\Assignment_3\developer\DEV" #Path to where the files are
        self.rootdir = r"C:\Users\Winton Chen\Desktop\CS 121\DEV" #Path to where the files are
            
        self.docID_word_count = {} #{docID:[url,word_count]} Use to calculate tfdif

        self.unique_tokens = 0 #Count of how many unique tokens within all the documents

        self.ps = PorterStemmer() #Porter Stemming method

        self.file_names = [] #List to hold all of the file names

        self.file_name_count = 0 #Iterator to get the different file names

        self.index_of_index = {} #An index of the inverted index to map the positions of the start of each line to its byte-position in the file

        self.punc_list =  {'!': ' ', '@': ' ', '#': ' ', '$': ' ', '©': ' ', '%': ' ', '^': ' ', '&': ' ', '*': ' ', '(': ' ', ')': ' ', '_': ' ', '-': ' ', '=': ' ', 
                            '+': ' ', '"': ' ', ':': ' ', ';': ' ', '<': ' ', '>': ' ', ',': ' ', '.': ' ', '?': ' ', '/': ' ', '{': ' ', '}': ' ', '[': ' ', ']': ' ', 
                            '`': ' ', '~': ' ', '\\': ' ', '|': ' ', '™': ' ', '•': ' ','—':' ','–':' ', "“":" ", "”":" ","‹":" ","›":" ","‘":" ","³":" "
                            }
        
        self.regexStr = re.compile("[^a-zA-Z0-9]")   #O(1)

        self.crc_set = set() #CRC dict to hold all of the docIDS and their crc numbers {crc_numbers:docIDs}

        self.simhash_set = set() #Simhash dict to hold all of the docIDs and there simhash numbers {simhash:docIDs}

        self.both_crc_simhash = set() #A set containing the file paths of both crc and simhash to prevent from traversing the page

    def setup(self):
        """
        All the pre-setup that will happen once when running this program
        """
        #Need to have a faster computer or implement it separately inorder to retrieve a simhash/crc chceck file
        #Finds all of the urls that are exact matches 
        #self.crc_check()

        #Finds all of the urls that are similar matches
        #self.simhash_check()

        #Creates the index
        self.createIndex()

        #Merges the every file
        self.mergeFiles()

        #Writes out a file for the index of index
        self.create_index_of_index()

        #Writes out a file for docID : url and word count
        self.create_word_count()

    def createIndex(self):
        """
        Iterates through all of the files and creates an index
        """
        for root, dirs, files, in os.walk(self.rootdir):
            for json_file in files:
                full_file_path = os.path.join(root,json_file)    

                with open(full_file_path, 'r') as f:
                    json_dict = json.load(f) #This variable contains the dictionary version of the file 

                    """
                    if json_dict['url'] in self.both_crc_simhash:
                        print("We found a url that was either an exact match or similar match")
                        continue
                    """

                    #Parses the HTML file
                    soup = BeautifulSoup(json_dict['content'], "lxml")

                    #Removes all of the CSS and Javascript tags
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    json_file_tokens = self.tokenize(soup.get_text())
                    
                    self.docID_word_count[self.docID] = []
                    self.docID_word_count[self.docID].append(json_dict['url'])
                    self.docID_word_count[self.docID].append(0)

                    #Count to keep track of the word position of the tokens
                    word_position = 0 

                    #Iterates through every token within the file
                    for token in json_file_tokens:

                        if token == "":
                            continue
                        
                        if self.docID_hashmap.get(token) == None:
                            self.docID_hashmap[token] = {}

                            #Number of unique tokens within all the files
                            self.unique_tokens += 1

                        if self.docID_hashmap[token].get(self.docID) == None:
                            #If docID does not currently exist in the dictionary, create a list with the word position
                            self.docID_hashmap[token][self.docID] = [word_position]
                        else:
                            #Appends the word position for the token in the self.docID_hashmap list 
                            self.docID_hashmap[token][self.docID].append(word_position)
                        
                        #Incremement the document word count in the self.docID_word_count dict by one
                        self.docID_word_count[self.docID][1] += 1

                        #Increment the word position in the document by one
                        word_position += 1

                #Increments the document ID by one        
                self.docID += 1

                #print(self.docID)

                if self.docID % 5000 == 0: #Writes to file every incremenet of 5000                    
                    self.writeToFile() #Writes all the data to a file

        self.writeToFile()

    def simhash_check(self):
        """
        Copied from Assignment 2
        We will also use the dict of words for similar duplicate detections since it has the frequency of the words
        We will be using simhash
        """
        for root, dirs, files, in os.walk(self.rootdir):
            for json_file in files:
                full_file_path = os.path.join(root,json_file)    

                with open(full_file_path, 'r') as f:
                    json_dict = json.load(f) #This variable contains the dictionary version of the file

                    if json_dict['url'] in self.both_crc_simhash:
                        continue 
                    
                    #Parses the HTML file
                    soup = BeautifulSoup(json_dict['content'], "lxml")

                    #Removes all of the CSS and Javascript tags
                    for script in soup(["script", "style"]):
                        script.decompose()

                    #If there is hella text, just skip the file
                    if len(soup.get_text()) > 50000:
                        print('\n')
                        print("This file is tooo damn long: ", qon_dict['url'])
                        print('\n')
                        continue

                    json_file_tokens = self.tokenize(soup.get_tqt())

                    #This is the fingerprint part
                    #Hash constant 
                    hash_constant = 31

                    #Vector V
                    vector_v = [0] * 32

                    #Hash table
                    hash_table = {}
                    
                    for word in json_file_tokens:
                        hash_value = 0
                        #Using this string polynomial method asqt considers the position of the chars as well
                        #Learned from ICS 46
                        for char in range(len(word)):
                            hash_value += (ord(word[char]) * (hash_constant ** char))

                        #binary representation of a number up to 14 positions
                        binary_32 = bin(hash_value % 2**32)[2:]

                        #Normalizing the binary number presented by padding the left side with the amount of zeros it is missing
                        if len(binary_32) != 14:
                            binary_32 = '0'*(32-len(binary_32)) + binary_32

                        hash_table[word] = binary_32
                    
                    for bin_word, binary in hash_table.items():
                        for bin_index in range(len(binary)):
                            if binary[bin_index] == '1':
                                vector_v[bin_index] += json_file_tokens.count(bin_word)
                            else:
                                vector_v[bin_index] -= json_file_tokens.count(bin_word)

                    fourteen_bit_fingerprint = ""
                    for number in vector_v:
                        if number > 0 :
                            fourteen_bit_fingerprint += '1'
                        else:
                            fourteen_bit_fingerprint += '0'

                    if fourteen_bit_fingerprint in self.simhash_set:
                        self.both_crc_simhash.add(json_dict['url'])
                        print(json_dict['url'])
                    else:
                        self.simhash_set.add(fourteen_bit_fingerprint)
                        
        
            self.simhash_set.clear()
                        
    def crc_check(self):
        """
        Copied from Assignment 2
        CRC similarity check for exact duplicates
        If we detect an exact duplicate, we would skip over the file.
        """
        for root, dirs, files, in os.walk(self.rootdir):
            for json_file in files:
                full_file_path = os.path.join(root,json_file)    

                with open(full_file_path, 'r') as f:
                    json_dict = json.load(f) #This variable contains the dictionary version of the file 
                    
                    #Parses the HTML file
                    soup = BeautifulSoup(json_dict['content'], "lxml")

                    #Removes all of the CSS and Javascript tags
                    for script in soup(["script", "style"]):
                        script.decompose()

                    crc32_num = zlib.crc32(bytes(soup.get_text(),'utf-8'))

                    if crc32_num in self.crc_set:
                        self.both_crc_simhash.add(json_dict['url'])
                    else:
                        self.crc_set.add(crc32_num)
        
            self.crc_set.clear()

    def create_index_of_index(self):
        """
        Creates an index of an index to quickly seek in the file. 
        """
        #This would hold the unicode value of the first letter of each token
        alpha_count = 97 # ord('a')
        #This would hold the unicode value of the second letter of each token
        beta_count = 97 #ord('a')

        #This number holds the position of the first letter of each token that differs from the previous
        byte_position = 0

        #Creates an alphabetical index of an index to later be used in the merging index portion
        #opens up the inverted index file and also creates a new file, index of index
        with open('full_merged_index.txt','r') as readfile, open('index_of_index.txt', 'w+') as outfile:
            #Writes the first index to file 
            outfile.write("a=0\n")

            #Iterates through every line within the file 
            for line in readfile:
                
                #Retrieves the token out of the line
                token = line[:line.find(':')]
                token = token[:token.find('|')]

                #If the two ord(alpha and beta) are equal with the first token being equal to ord(alpha_count) such as aa or bb
                if ord(token[0]) > alpha_count:
                    if len(token) == 1:
                        outfile.write("{first_letter}={byte}\n".format(first_letter=token[0], byte=byte_position))
                        beta_count = 96
                    else:
                        outfile.write("{first_letter}{second_letter}={byte}\n".format(first_letter=token[0], second_letter=token[1], byte=byte_position))
                        beta_count = ord(token[1])
                    alpha_count += 1
                    
                elif len(token) > 1 and ord(token[1]) > beta_count:
                    if beta_count == 122:
                        outfile.write("{first_letter}{second_letter}={byte}\n".format(first_letter=token[0], second_letter=token[1], byte=byte_position))
                        alpha_count += 1
                        beta_count = 97
                    else:
                        outfile.write("{first_letter}{second_letter}={byte}\n".format(first_letter=token[0], second_letter=token[1], byte=byte_position))
                        beta_count += 1
                
                byte_position += (len(line) + 1)    #Adds the new byte position

    def mergeFiles(self):
        """
        Opens up all of the files simultaneously and merges them together
        """
        #This will be the file that holds the first two partial indexes
        with open("merged_index_one.txt",'w+') as outfile:
            
            #Opens up the first two files
            with open(self.file_names[0],'r') as file_one, open(self.file_names[1],'r') as file_two:
                
                #Reads a line from each of the files 
                file_one_line = file_one.readline()
                file_two_line = file_two.readline()
                #Lines in the file are modeled as this: '{token} : {postings}\n', token : docID = [postings], docID = [postings]
                """
                There are three cases when comparing the two tokens
                1. token one is equal to token two, append token two line to the end of token one
                2. token one is less than token two, append token one till token one is greater or equal to token two
                3. token one is greater than token two, append token two till token two is greater than token one
                """
                #While both file lines does not equal '\n'
                while (file_one_line not in '\n') or (file_two_line not in '\n'):

                    #Finds the two tokens from each file
                    token_one = file_one_line[:file_one_line.find('|')]
                    token_two = file_two_line[:file_two_line.find('|')]

                    #If it equals any of this, set it to a higher unicode value string
                    if token_one == '' or token_one == '\n':
                        token_one = 'zzzzzzzzzzzzzzzzzzzzzzz'
                    
                    if token_two == '' or token_two == '\n':
                        token_two = 'zzzzzzzzzzzzzzzzzzzzzzz'
                    
                    #If the tokens are equal to each other, write it out to the file
                    if token_one == token_two :
                        
                        if token_one == 'zzzzzzzzzzzzzzzzzzzzzzz':
                            #Append line equals just the second readline
                            append_line = file_two_line
                        elif token_two == 'zzzzzzzzzzzzzzzzzzzzzzz':
                            #Append line equals just the first readline
                            append_line = file_one_line
                        else:
                            #Takes away the new-line character of the first readline and token of the second readline
                            term_frequency = int(file_one_line[file_one_line.find('|')+1:file_one_line.find(':')]) + int(file_two_line[file_two_line.find('|')+1:file_two_line.find(':')]) 
                            append_line = token_one + '|' + str(term_frequency) + file_one_line[file_one_line.find(':'):-1] + file_two_line[file_two_line.find(':')+1:] 
                        
                        #Reads it out to the file 
                        outfile.write(append_line) 

                        #Reads in the next two lines
                        file_one_line = file_one.readline()
                        file_two_line = file_two.readline()

                    #If the first token is less than the second token
                    elif token_one < token_two:
                        #Writes out the line to file
                        outfile.write(file_one_line)
                        #Reads in the first line 
                        file_one_line = file_one.readline()
                    
                    #If the first token is greater than the second token
                    elif token_one > token_two:
                        #Writes out the line to file
                        outfile.write(file_two_line)
                        #Reads in the second line 
                        file_two_line = file_two.readline()

        #This will be the file that holds the first two partial indexes
        
        #This will be the file that holds the full partial index
        with open("full_merged_index.txt",'w+') as outfile:
            
            #Opens up the first two files
            with open('merged_index_one.txt','r') as file_one, open(self.file_names[2],'r') as file_two:
                
                #Reads a line from each of the files 
                file_one_line = file_one.readline()
                file_two_line = file_two.readline()
                #Lines in the file are modeled as this: '{token} : {postings}\n', token : docID = [postings], docID = [postings]

                """
                There are three cases when comparing the two tokens
                1. token one is equal to token two, append token two line to the end of token one
                2. token one is less than token two, append token one till token one is greater or equal to token two
                3. token one is greater than token two, append token two till token two is greater than token one
                """
                #While both file lines does not equal '\n'
                while (file_one_line not in '\n') or (file_two_line not in '\n'):
                    
                    #Finds the two tokens from each file
                    token_one = file_one_line[:file_one_line.find('|')]
                    token_two = file_two_line[:file_two_line.find('|')]

                    #If it equals any of this, set it to a higher unicode value string
                    if token_one == '' or token_one == '\n':
                        token_one = 'zzzzzzzzzzzzzzzzzzzzzzz'
                    
                    if token_two == '' or token_two == '\n':
                        token_two = 'zzzzzzzzzzzzzzzzzzzzzzz'
                    
                    #If the tokens are equal to each other, write it out to the file
                    if token_one == token_two :
                        
                        if token_one == 'zzzzzzzzzzzzzzzzzzzzzzz':
                            #Append line equals just the second readline
                            append_line = file_two_line
                        elif token_two == 'zzzzzzzzzzzzzzzzzzzzzzz':
                            #Append line equals just the first readline
                            append_line = file_one_line
                        else:
                            #Takes away the new-line character of the first readline and token of the second readline
                            term_frequency = int(file_one_line[file_one_line.find('|')+1:file_one_line.find(':')]) + int(file_two_line[file_two_line.find('|')+1:file_two_line.find(':')]) 
                            append_line = token_one + '|' + str(term_frequency) + file_one_line[file_one_line.find(':'):-1] + file_two_line[file_two_line.find(':')+1:]  
                        
                        #Reads it out to the file 
                        outfile.write(append_line) 

                        #Reads in the next two lines
                        file_one_line = file_one.readline()
                        file_two_line = file_two.readline()

                    #If the first token is less than the second token
                    elif token_one < token_two:
                        #Writes out the line to file
                        outfile.write(file_one_line)
                        #Reads in the first line 
                        file_one_line = file_one.readline()
                    
                    #If the first token is greater than the second token
                    elif token_one > token_two:
                        #Writes out the line to file
                        outfile.write(file_two_line)
                        #Reads in the second line 
                        file_two_line = file_two.readline()

    def writeToFile(self):
        """
        Writes our local memory to external memory such as an external file as there is not enough internal memory 
        """
        with open('data{file_iteration}.txt'.format(file_iteration=self.file_name_count), 'w+') as outfile: #{token:{docID:[word_positions]}

            #Iterates through all of the tokens inside the self.docID_hashmap
            for token in sorted(self.docID_hashmap):

                #Creates a posting string out of all of the contents of the token in the hashmap: token : docID = [postings], docID = [postings]
                posting_string = '' 
                for docID in self.docID_hashmap[token]:
                    posting_string += '{docID}:{docID_list}|'.format(docID = docID, docID_list = self.docID_hashmap[token][docID])
                
                #Writes it out to file
                out_string = '{token}|{df}:{postings}\n'.format(token=token,df=len(self.docID_hashmap[token]),postings=posting_string)
                try:
                    outfile.write(out_string)
                except:
                    pass
        
        self.file_names.append('data{file_iteration}.txt'.format(file_iteration=self.file_name_count)) #Appends the file name to the list

        self.file_name_count += 1 #Increment the file name count by one.

        self.docID_hashmap.clear() #Clears the main dictionary after writing to a file 
    
    def tokenize(self,words:str):
        """
        Returns a list of tokens 
        Partially found and updated from https://towardsdatascience.com/benchmarking-python-nlp-tokenizers-3ac4735100c5
        """
        words = words.lower()

        words = words.replace("\n", " ").replace("\r", " ")
        
        t = str.maketrans(self.punc_list)

        words = words.translate(t)

        t = str.maketrans(dict.fromkeys("'`",""))
        words = words.translate(t)

        """
        #Tokenizes everything
        tokens = regexp_tokenize(words,pattern='\s+',gaps=True)
        """
        tokens = re.split(self.regexStr,words)

        #Stems the token using the Porter Stem method
        tokens = [self.ps.stem(token) for token in tokens]
        
        return tokens
    
    def create_word_count(self):
        """
        Writes docID_word_count to file.
        """
        longest_len = 231

        with open('docID_word_count.txt','w+') as outfile: #{docID:[url,word_count]} Use to calculate tfdif
            
            #Iterates through all of the tokens inside the self.docID_word_count
            for docID in self.docID_word_count:
                
                #Writes it out in this format: 'docID = url | word count'
                outfile_string = '{docID}={url}|{word_count}'.format(docID = docID, url=self.docID_word_count[docID][0], word_count=self.docID_word_count[docID][1])
                #Normalization of each string to the string with the longest length to making readfile seek easier
                if len(outfile_string) != longest_len:
                    outfile_string += (( longest_len - len(outfile_string)) *'?')
                
                outfile_string += '?'
                outfile_string += '\n'

                outfile.write(outfile_string)

if __name__ == "__main__":
    whatever = module_1()
    whatever.setup()