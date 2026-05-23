import random
import string
import os
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT_DIR / "attacker" / "configs" / "credentials.txt"

# Data pools for realistic generation
FIRST_NAMES = ["john", "jane", "alex", "michael", "sarah", "david", "emily", "chris", "jessica", "matthew", "amanda", "joshua", "ashley", "daniel", "brittany", "james", "megan", "justin", "samantha", "robert"]
LAST_NAMES = ["smith", "johnson", "williams", "brown", "jones", "garcia", "miller", "davis", "rodriguez", "martinez", "hernandez", "lopez", "gonzalez", "wilson", "anderson", "thomas", "taylor", "moore", "jackson", "martin"]
DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "protonmail.com", "mail.com"]
PASSWORD_BASES = ["password", "qwerty", "123456", "football", "baseball", "dragon", "monkey", "sunshine", "princess", "iloveyou", "welcome", "spring", "summer", "autumn", "winter", "admin", "root", "shadow", "letmein", "trustno1"]

# All 31 valid accounts — must exactly match SEED_USERS in target-app/app.py
VALID_ACCOUNTS = [
    # Original 6
    "alice@example.com:Spring2026!",
    "bob@example.com:Password123!",
    "charlie@example.com:Welcome@123",
    "admin@example.com:Admin@2026",
    "diana@example.com:Diana#999",
    "eve@example.com:Passw0rd!",
    # Extended 25
    "john.smith@gmail.com:Football2023!",
    "jane.doe@yahoo.com:Sunshine99#",
    "michael.jones@hotmail.com:Dragon2024@",
    "sarah.miller@gmail.com:Princess1!",
    "david.garcia@outlook.com:Monkey123#",
    "emily.brown@icloud.com:Qwerty2025!",
    "chris.wilson@gmail.com:Baseball99@",
    "jessica.moore@yahoo.com:Iloveyou1!",
    "matthew.taylor@gmail.com:Shadow2024#",
    "amanda.anderson@aol.com:Welcome99!",
    "joshua.thomas@gmail.com:Summer2024@",
    "ashley.jackson@yahoo.com:Letmein1!",
    "daniel.white@hotmail.com:Trustno1#",
    "brittany.harris@gmail.com:Autumn2023!",
    "james.martin@outlook.com:Admin1234@",
    "megan.thompson@gmail.com:Spring99#",
    "justin.garcia@yahoo.com:Winter2024!",
    "samantha.lee@icloud.com:Dragon99@",
    "robert.clark@gmail.com:Passw0rd99!",
    "jennifer.lewis@yahoo.com:Flower2024#",
    "william.hall@hotmail.com:Guitar2023@",
    "lisa.allen@gmail.com:Ocean2024!",
    "kevin.young@outlook.com:Thunder99#",
    "rachel.king@gmail.com:Sunset2024@",
    "steven.wright@yahoo.com:Coffee2023!",
]

def generate_fake_email():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    domain = random.choice(DOMAINS)
    
    # 50% chance to add a number to the email
    if random.random() > 0.5:
        year = random.randint(1970, 2005)
        return f"{first}.{last}{year}@{domain}"
    return f"{first}{last}@{domain}"

def generate_fake_password():
    base = random.choice(PASSWORD_BASES)
    
    # Randomly capitalize first letter
    if random.random() > 0.5:
        base = base.capitalize()
        
    # Randomly append numbers
    if random.random() > 0.3:
        base += str(random.randint(1, 9999))
        
    # Randomly append a special character
    if random.random() > 0.7:
        base += random.choice("!@#$%*")
        
    return base

def main():
    print("==================================================")
    print("  Synthetic Breach Dataset Generator")
    print("==================================================")

    try:
        num_records = int(input("How many credential pairs do you want to generate? (e.g., 65): "))
    except ValueError:
        print("Invalid number. Defaulting to 65.")
        num_records = 65

    # Dynamically decide how many valid accounts to inject this run
    # Between 8 and 20 — so success rate varies naturally between ~12% and ~30%
    min_inject = min(8, len(VALID_ACCOUNTS))
    max_inject = min(20, len(VALID_ACCOUNTS), num_records - 10)
    num_to_inject = random.randint(min_inject, max_inject)
    accounts_to_inject = random.sample(VALID_ACCOUNTS, num_to_inject)

    print(f"\nGenerating {num_records} realistic fake credentials...")
    print(f"[*] Dynamically injecting {num_to_inject} valid accounts (hidden randomly)")
    print(f"[*] Expected success rate: ~{round(num_to_inject/num_records*100, 1)}%")

    dataset = []

    # Generate fake credential pairs to fill the rest of the slots
    num_fake = num_records - num_to_inject
    for _ in range(num_fake):
        email = generate_fake_email()
        password = generate_fake_password()
        dataset.append(f"{email}:{password}")

    # Inject the randomly selected valid accounts
    dataset.extend(accounts_to_inject)

    # Shuffle so valid accounts are hidden at random positions
    random.shuffle(dataset)

    # Write to the attacker's configuration folder
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for record in dataset:
            f.write(record + "\n")

    print(f"\n[+] Success! Generated {num_records} records.")
    print(f"[+] {num_to_inject} valid accounts hidden randomly inside the dataset.")
    print(f"[+] Dataset saved to: {OUTPUT_FILE}")
    print(f"\nRun this again before each attack for a fresh, unpredictable dataset!")

if __name__ == "__main__":
    main()
