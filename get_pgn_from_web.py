import time
import codecs
import sys
import chess.pgn
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

website = "" # link to a notepad on https://edupad.ch/
temp = ".pgn" # termporary storage file name
database = ".pgn" # database name
intro_length = 4 # space for instructions marked with # at the beginning of the line


def main():
    """Scrape all PGNs from the shared edupad website.
    """
    driver = webdriver.Firefox()
    driver.get(website)

    # let page load
    time.sleep(2)

    # dont change website content if there are other people online
    people_online = driver.find_element(By.ID, "online_count")

    if int(people_online.text) > 1:
        if input("There is more than 1 person online. Continue anyway? Y/N") == 'N':
            driver.close()
            sys.exit()

    # save current version and go to content location with the driver
    driver.find_element(By.CLASS_NAME, "buttonicon-savedRevision").click()
    driver.switch_to.frame('ace_outer')
    driver.switch_to.frame('ace_inner')

    search_input = driver.find_element(By.ID, "innerdocbody")
    search_lines = driver.find_elements(By.CLASS_NAME, "ace-line")

    # print all lines on the website to the temporary storage
    temp_lines = []
    with codecs.open(temp, "r+", "utf-8") as f:
        f.truncate(0)
        # check if directions are still available
        for i in search_lines[:intro_length]:
            if i.text.strip()[0] != "#":
                driver.close()
                print("Error: Instructions have been changed.")
                sys.exit()
            # save directions
            temp_lines.append(i.text.strip())
        # print acutal content
        for i in search_lines[intro_length:]:
            f.write(i.text.strip() + "\n")

    # empty website
    search_input.send_keys(Keys.CONTROL + Keys.END)
    search_input.send_keys(Keys.CONTROL + "a")
    search_input.send_keys(Keys.DELETE)

    # let page syncronise
    time.sleep(1)

    # rewrite directions
    for i in temp_lines:
        search_input.send_keys(i + "\n")
    search_input.send_keys("\n")
    

    # let page syncronise
    time.sleep(2)

    # close website
    driver.close()

    # check pgns and fix manually in the temporary storage
    pgn_checkstyle()
    # possibility to correct errors and check pgn again
    while input("Add to database? Y/N") != "Y":
        print("----------------------------------------")
        pgn_checkstyle()
        # finish job and store pgns
        write_to_database()

def pgn_checkstyle():
    """Check if the PGNs are written in the intended way.
    """
    with open(temp, "r") as f:
        # go through all games
        game = chess.pgn.read_game(f)
        while game is not None:
            # print game if pgn format was not followed
            # or if the players arent specified
            if (game.errors != [] or
                len(game.headers["White"]) < 2 or
                len(game.headers["Black"]) < 2):
                print(game)
            game = chess.pgn.read_game(f)

def write_to_database():
    """Write all games from the temporary storage to the actual database.
    """
    with open(temp, "r") as f:
        with open(database, "a") as db:
            # go through all games
            game = chess.pgn.read_game(f)
            while game is not None:
                # print pgn and add one empty line
                db.write(str(game))
                db.write("\n\n")
                game = chess.pgn.read_game(f)

main()