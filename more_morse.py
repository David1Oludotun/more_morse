from time import sleep, time
import random
import csv


from gpiozero import LED, Buzzer, OutputDevice


# --- Hardware setup (BCM pin numbers) ---
# These must match how you wired it:
# LED anode -> resistor -> GPIO17, LED cathode -> GND
# Active buzzer -> GPIO18 and GND
# GPIO27 -> 1k resistor -> transistor base, motor between 5V and transistor collector, emitter -> GND
led = LED(17)
buzzer = Buzzer(18)
#motor = OutputDevice(27)


# --- Morse code table ---
MORSE = {
'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
'Q': '--.-','R': '.-.', 'S': '...', 'T': '-',
'U': '..-','V': '...-', 'W': '.--', 'X': '-..-',
'Y': '-.--','Z': '--..'
}


# Length of one dot, in seconds
DOT_TIME = 0.2



#def motor_on():
#"""Turn motor on by switching GPIO27 high."""
#motor.on()



#def motor_off():
# """Turn motor off by switching GPIO27 low."""
# motor.off()



def dot():
    """Play a short dot: LED + buzzer + motor on briefly."""
    led.on()
    buzzer.on()
    # motor_on()
    sleep(DOT_TIME)
    led.off()
    buzzer.off()
    # motor_off()
    # small gap between symbols of same letter
    sleep(DOT_TIME)



def dash():
    """Play a long dash: LED + buzzer + motor on 3x longer."""
    led.on()
    buzzer.on()
    # motor_on()
    sleep(3 * DOT_TIME)
    led.off()
    buzzer.off()
    #motor_off()
    # small gap between symbols of same letter
    sleep(DOT_TIME)



def send_letter(letter):
    """Send a single letter in Morse using dot() and dash()."""
    letter = letter.upper()
    if letter not in MORSE:
        return


    code = MORSE[letter]
    print(f"What letter is morsed as {code}")


    for symbol in code:
        if symbol == '.':
            dot()
        else:
            dash()

    # extra gap after the whole letter
    sleep(2 * DOT_TIME)



def main():
# letters we train on (start with a small set)
    letters = [
    'A','B','C','D','E','F','G','H','I','J','K','L','M',
    'N','O','P','Q','R','S','T','U','V','W','X','Y','Z'
    ]
    score = 0
    rounds = 0


    # open a CSV file for logging (creates if not there)
    logfile = open("morse_training_log.csv", "a", newline="")
    writer = csv.writer(logfile)
    writer.writerow(["letter", "guess", "correct", "reaction_time"])


    print("Morse Trainer - Ctrl+C or type Q to quit.\n")


    try:
        while True:
        # 1. Pick a random target letter
            target = random.choice(letters)


            # 2. Send it via LED + buzzer + motor
            send_letter(target)


            # 3. Ask the user to guess and measure response time
            t_start = time()
            guess = input("What letter was that? (or 1 to quit) ").strip().upper()
            t_end = time()


            if guess == '1':
                break


            reaction_time = t_end - t_start
            correct = (guess == target)


            # 4. Update score and tell user
            if correct:
                print("Correct!\n")
                score += 1
            else:
                print(f"Nope, it was {target}\n")


            rounds += 1


            # 5. Log to CSV: letter, guess, 1/0 for correct, reaction time
            writer.writerow([target, guess, int(correct), reaction_time])
            logfile.flush()


            print(f"Score: {score}/{rounds}, Reaction time: {reaction_time:.2f} s\n")


    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")


    finally:
        # Clean up
        logfile.close()
        led.off()
        buzzer.off()
        #motor_off()
        print("Thanks for playing! Final score:", score, "/", rounds)



if __name__ == "__main__":
    main()