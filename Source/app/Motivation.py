import random

# Load datasets
dont_give_up = open("Data/dont_give_up.txt", encoding="utf8").readlines()
strikes = open("Data/strikes.txt", encoding="utf8").readlines()
compliments = open("Data/compliments.txt", encoding="utf8").readlines()


# Get random message of type "Don't give up" from dataset
async def DontGiveUp():
    try:
        word = dont_give_up[random.randint(0, len(dont_give_up) - 1)].rstrip()
        return word

    except Exception as e:
        print(f'[!] There was an error in generating motivation message: {e}')
        pass


# Get random message of type "Good Strikes" from dataset
async def GoodStrikes():
    try:
        word = strikes [random.randint(0, len(strikes ) - 1)].rstrip()
        return word

    except Exception as e:
        print(f'[!] There was an error in generating good strike: {e}')
        pass


# Get random message of type "Compliment" from dataset
async def Compliment():
    try:
        word = compliments[random.randint(0, len(compliments) - 1)].rstrip()
        return word

    except Exception as e:
        print(f'[!] There was an error in generating compliment: {e}')
        pass
