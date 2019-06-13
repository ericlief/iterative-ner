import sys
import random

def write(file, dataset):
    with open(file, "wt") as f:
        for line in dataset:
            print(line, file=f)

data_file = sys.argv[1]

data = []
i = 0
with open(data_file) as f:
    for line in f:
        line = line.rstrip("\r\n")
        if line:
            data.append(line)
            i += 1

print(data[:100])

random.seed(256)
random.shuffle(data)  # randomly shuffles the ordering of data

print("Total number of sentences ", len(data))
split_1 = int(0.8 * len(data))
split_2 = int(0.9 * len(data))
train_data = data[:split_1]
dev_data = data[split_1:split_2]
test_data = data[split_2:]

print("Stats")
print("Number of sents")
print("train: ", len(train_data))
print("dev: ", len(dev_data))
print("dev: ", len(test_data))

write("train", train_data)
write("dev", dev_data)
write("test", test_data)
