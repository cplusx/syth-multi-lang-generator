import io
import random

path_to_text_file = "/mnt/hgfs/code/ISI/Github/TDA/SynthText/data/newsgroup/newsgroup.txt"
path_to_spaced_file = "/mnt/hgfs/code/ISI/Github/TDA/SynthText/data/newsgroup/newsgroup_spaced.txt"

def main():
    read_file = io.open(path_to_text_file, 'r', encoding='utf-8') 
    write_file = io.open(path_to_spaced_file, 'w', encoding='utf-8')


    read_lines = read_file.readlines()

    for each_line in read_lines:
        
        length_line = len(each_line)
        iterator = 0
        new_line = ""
        while(iterator < length_line):
            rand_number = random.randint(1, 4)
            new_line += each_line[iterator:iterator+rand_number]+" "
            iterator += rand_number
        # print(new_line)
        # print(each_line)
        # input('waiting for the input')
        write_file.write(new_line)

        
    read_file.close()
    write_file.close()

if __name__ == "__main__":
    main()