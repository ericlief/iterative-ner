"""
Script to convert WikiNER format into column format
Word Tag
"""

def process(fname):
    
    words_tags = []
    with open(fname, "rt") as f:
        for line in f:
            if len(line) > 1:
                line = line.split()
                words_tags.append(line)
            
    with open(fname+".conll", "wt") as f:
        for line in words_tags:
            prev_label = ""
            for word_tag in line:
                word, pos, label = word_tag.split("|")
                if label in ["B-PER", "I-PER"]:
                    if label[0] == "I" and prev_label in ["", "O"]:
                        label = "B-PER"
                else:
                    label = "O"
                prev_label = label
                print(word, pos, label, file=f) 
            print("", file=f)
        
if __name__ == "__main__":
    process("aij-wikiner-de-wp3-PER")
    process("aij-wikiner-de-wp3-NON_PER")
 
        


