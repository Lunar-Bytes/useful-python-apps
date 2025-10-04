import random, string

password_length = int(input("Write password length: "))

characters = string.ascii_letters + string.digits + string.punctuation
password = [
    random.choice(string.ascii_lowercase),
    random.choice(string.ascii_uppercase),
    random.choice(string.digits),
    random.choice(string.punctuation)
]
password += [random.choice(characters) for _ in range(password_length - 4)]
random.shuffle(password)

print("Your password:", "".join(password))
