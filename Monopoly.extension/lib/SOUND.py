import playsound

def play_file(filename):
    path = 'C:\Users\szhang\Documents\Revit_Monopoly\Monopoly.extension\bin\sound\{}' .format(filename)
    path = str(filename)
    #playsound.playsound(path)


def money(money):
    if money > 0:
        play_file('money_coin1.wav')
    else:
        play_file("money_bag.wav")

def jumping(is_overweight):
    if is_overweight:
        play_file('jump_normal.wav')
    else:
        play_file("jump_normal.wav")

def landing(is_overweight):
    if is_overweight:
        play_file('landing_heavy.wav')
    else:
        play_file("landing_heavy.wav")
