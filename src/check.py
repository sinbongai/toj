file = open('data/db-20230106.csv', 'r')

text = file.read()

seen = []

for letter in text:
    if letter not in seen and letter < 'ㄚ':
        seen.append(letter)

seen = sorted(seen)
print(''.join(seen))

