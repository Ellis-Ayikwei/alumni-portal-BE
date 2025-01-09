def generate_policy_number():
    import random
    import string

    randcode = "".join(random.choice(string.ascii_letters) for i in range(8))
    return f"PB-{randcode}"


print(generate_policy_number())
