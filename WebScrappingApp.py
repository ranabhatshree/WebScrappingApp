import requests
from bs4 import BeautifulSoup
import csv
import datetime
import csv
from os import listdir
from os.path import isfile, join
import pandas as pd
from tkinter import *
from tkinter import messagebox
import time

def fileNameExtractor (url):
    try:
        fileNameHref = []
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')
        #listing all li elements that has class 'data-toggle = tab'
        filesContainer = soup.find_all("li", {"data-toggle": "tab"})

        for href in filesContainer:
            #getting all href starting with '#' tag
            fileNameHref.append(href.get('href').replace("#",''))

        return fileNameHref

    except Exception as e:
        messagebox.showinfo('Error', e)

def profileInfoExtractor (profileIds):

    finalDatas = []
    for profileId in profileIds:
        content = requests.get("https://www.tennisbrain.com/player_stats/" + profileId).content

        soup = BeautifulSoup(content, 'lxml')
        tdata = soup.find("table", id = "playerstats{}".format(profileId)).find_all("tr")

        playerCountries = [tdata[1]]

        if len(tdata) >= 12:
            playerHands = tdata[6]
        else:
            playerHands = tdata[4]

        playerCountries = [ country.text.strip() for country in playerCountries ]
        playerHands = [playerHands.text.strip()]

        finalPlayerCountries = ''
        finalPlayerHands = ''

        for country in playerCountries:
            finalPlayerCountries = (country.split("\n"))
        if "Country" in finalPlayerCountries:
            finalPlayerCountries.remove("Country")

        for hand in playerHands:
            finalPlayerHands = (hand.split("\n"))

        if "Hand" in finalPlayerHands:
            finalPlayerHands.remove("Hand")

        finalDatas.append(finalPlayerCountries + finalPlayerHands)

    return finalDatas


def dataExtractor( url, fileNameHref, filePath ):

    try:

      print("Connecting to {} .......".format(url))

      currentYear = datetime.datetime.now().year
      for href in fileNameHref:
          fileName = filePath + href + " - " + str(currentYear)
          profileIds = []

          content = requests.get(url).content
          soup = BeautifulSoup(content, 'lxml')

          #tdata = soup.find_all("div", { "class": "tab-pane fade " })
          tdatas = soup.find("div", id = href ).find('tbody').find_all("tr")

          file = open("{}.csv".format(fileName), "w", newline = '')
          datas = []
          finalDatas = []
          playerPercentages = []

          for row in tdatas:
              cols = row.findChildren(recursive=False)

              # finding Date,Player 1,Player Odds Player2 Odds,Player 2
              colsForData = [ele for ele in cols]

              if len(colsForData) == 4:
                  datas.append(colsForData)

              elif len(colsForData) > 4:
                  datas.append(colsForData)

              # finding percentage
              for ele in cols:
                  percentagePlayer1Class = {"class": "progress-bar progress-bar-one"}
                  percentagePlayer2Class = {"class": "progress-bar progress-bar-two"}
                  if ele.find("div", percentagePlayer1Class) is not None \
                          or ele.find("div",percentagePlayer2Class) is not None:
                      player1Percentage = ele.find("div", percentagePlayer1Class).text.strip()
                      player2Percentage = ele.find("div", percentagePlayer2Class).text.strip()

                      playerPercentages.append([player1Percentage , player2Percentage])

              # finding profileIds
              for ele in cols:
                 if ele.find("a") is not None:
                    if ele.find("a").get("aria-controls") is not None:
                        profileIds.append(ele.find("a").get("aria-controls"))


          # appending four features (Player 1, Player 1 Odds Player 2 Odds, Player 2
          for data in datas:
              finalDatas.append([d.text.strip() for d in data])

          # if date is completed,
          for data in finalDatas:
              if data[0] == 'Completed' or data[0] == 'completed':
                  data.append(data[2])
                  data.insert(2, '-')
                  data[3] = '-'
              else:
                  data.append('-')

          # writing to file

          rowFeatures = ["Date", "Player 1", "Player1 Odds" , "Player2 Odds", "Player 2", "Result", "% Player 1",
                           "% Player 2", "Country P1", "Country P2", "Hand P1", "Hand P2"]

          writer = csv.writer(file)
          writer.writerow(rowFeatures)

          # joining two lists (4 Features list, 2 Features List)
          countryAndHand = profileInfoExtractor(profileIds)

          for i in range(len(finalDatas)):
              a=1
              #finalDatasWith6Features.append([finalDatas[i] + playerPercentages[i] + countryAndHand[i]])
              writer.writerow(finalDatas[i] + playerPercentages[i] + countryAndHand[i])
          #messagebox.showinfo("Success", "Writing to the '{}' file success".format(fileName))
          print("Writing to the '{}' file success".format(fileName))

    except Exception as e:
        messagebox.showinfo('Error', e)


def newDataExtractor(url, fileNameHref, filePath):

    try:

      currentYear = datetime.datetime.now().year
      fullFinalDatas = []
      for href in fileNameHref:
          fileName = filePath + href + " - " + str(currentYear)
          profileIds = []

          content = requests.get(url).content
          soup = BeautifulSoup(content, 'lxml')

          #tdata = soup.find_all("div", { "class": "tab-pane fade " })
          tdatas = soup.find("div", id = href ).find('tbody').find_all("tr")

          datas = []
          finalDatas = []
          playerPercentages = []

          for row in tdatas:
              cols = row.findChildren(recursive=False)

              # finding Date,Player 1,Player Odds Player2 Odds,Player 2
              colsForData = [ele for ele in cols]

              if len(colsForData) == 4:
                  datas.append(colsForData)

              elif len(colsForData) > 4:
                  datas.append(colsForData)

              # finding percentage
              for ele in cols:
                  percentagePlayer1Class = {"class": "progress-bar progress-bar-one"}
                  percentagePlayer2Class = {"class": "progress-bar progress-bar-two"}
                  if ele.find("div", percentagePlayer1Class) is not None \
                          or ele.find("div",percentagePlayer2Class) is not None:
                      player1Percentage = ele.find("div", percentagePlayer1Class).text.strip()
                      player2Percentage = ele.find("div", percentagePlayer2Class).text.strip()

                      playerPercentages.append([player1Percentage , player2Percentage])

              # finding profileIds
              for ele in cols:
                 if ele.find("a") is not None:
                    if ele.find("a").get("aria-controls") is not None:
                        profileIds.append(ele.find("a").get("aria-controls"))

          # appending four features (Player 1, Player 1 Odds Player 2 Odds, Player 2
          for data in datas:
              finalDatas.append([d.text.strip() for d in data])

          # if date is completed,
          for data in finalDatas:
              if data[0] == 'Completed' or data[0] == 'completed':
                  data.append(data[2])
                  data.insert(2, '-')
                  data[3] = '-'
              else:
                  data.append('-')

          # joining two lists (4 Features list, 2 Features List)
          countryAndHand = profileInfoExtractor(profileIds)

          for i in range(len(finalDatas)):
              fullFinalDatas.append(finalDatas[i] + playerPercentages[i] + countryAndHand[i])

      return fullFinalDatas

    except Exception as e:
        messagebox.showinfo('Error', e)

def update(url, path):

    try:
        currentYear = datetime.datetime.now().year
        fileNames = fileNameExtractor(url)

        # listing files
        mypath = path
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        alreadyFileExists = []
        fileDoesnotExists = []
        for fileNameHref in fileNames:
            fileName = fileNameHref + " - "+ str(currentYear) + ".csv"
            if fileName in onlyfiles:
                alreadyFileExists.append(fileNameHref)
            else:
                fileDoesnotExists.append(fileNameHref)

        # if fileName doesnot exists
        #  creating new file for file doesnot exsists
        if len(fileDoesnotExists) > 0:
            dataExtractor(url, fileDoesnotExists, filePath=path)

        #else already exists, read and update if necessary
        if len(alreadyFileExists) > 0:
            for alreadyFileExist in alreadyFileExists:
                alreadyFileExistsName = alreadyFileExist + " - " + str(currentYear) + ".csv"

                player1Plusplayer2Names = []
                with open(mypath + alreadyFileExistsName, "r") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        player1Plusplayer2Names.append(row['Player 1'] + row['Player 2'])

                alreadyFileExist = [alreadyFileExist]
                # scrapping latest data
                serverDatas = newDataExtractor(url, alreadyFileExist, filePath=path)
                player1 = player2 = ''
                toBeUpdatedOddsOnly = []
                toBeUpdateResultsOnly = []
                toBeUpdatedPlayer1OddsOnlyValues = []
                toBeUpdatedPlayer2OddsOnlyValues = []
                toBeUpdateResultsOnlyValues = []
                new_a = []

                for serverData in serverDatas:
                    player1 = serverData[1]
                    player2  = serverData[4]
                    player1Odds = serverData[2]
                    player2Odds = serverData[3]
                    result = serverData[5]

                    if player1 + player2 in player1Plusplayer2Names:

                        i = player1Plusplayer2Names.index(player1 + player2)

                        if serverData[0] == 'Completed' or serverData[0] == 'completed':
                            # getting index of matched row
                            toBeUpdateResultsOnly.append(i)
                            toBeUpdateResultsOnlyValues.append(result)
                        else:
                            toBeUpdatedOddsOnly.append(i)
                            toBeUpdatedPlayer1OddsOnlyValues.append(player1Odds)
                            toBeUpdatedPlayer2OddsOnlyValues.append(player2Odds)
                    else:
                        a = serverData
                        # removing date
                        a.remove(a[0])

                        player1 = a[0]
                        countryPlayer1 = a[7]
                        countryPlayer2 = a[8]
                        player2 = a[3]
                        percentagePlayer1 = a[5]
                        percentagePlayer2 = a[6]
                        handPlayer1 = a[9]
                        handPlayer2 = a[10]
                        player1Odds = a[1]
                        player2Odds = a[2]
                        result = a[4]

                        new_a.append(player1)
                        new_a.append(countryPlayer1)
                        new_a.append(countryPlayer2)
                        new_a.append(player2)
                        new_a.append(percentagePlayer1)
                        new_a.append(percentagePlayer2)
                        new_a.append(handPlayer1)
                        new_a.append(handPlayer2)
                        new_a.append(player1Odds)
                        new_a.append(player2Odds)
                        new_a.append(result)

                        print(new_a,' needs to be appended')

                    with open(mypath + alreadyFileExistsName, 'a') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(new_a)

                # updating results and player odds
                df = pd.read_csv(mypath + alreadyFileExistsName)
                # updating Results only
                for i in range(len(toBeUpdateResultsOnly)):
                    df.at[toBeUpdateResultsOnly[i], "Result"] = toBeUpdateResultsOnlyValues[i]

                for i in range(len(toBeUpdatedOddsOnly)):
                    df.at[toBeUpdatedOddsOnly[i], "Player1 Odds"] = toBeUpdatedPlayer1OddsOnlyValues[i]
                    df.at[toBeUpdatedOddsOnly[i], "Player2 Odds"] = toBeUpdatedPlayer2OddsOnlyValues[i]

                df.to_csv(mypath + alreadyFileExistsName, index=False, encoding='utf-8')
                print('updating success')

    except Exception as e:
        messagebox.showinfo('Error', e)

def changeColumns(path):

    # listing files
    mypath = path
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for file in onlyfiles:
        df = pd.read_csv(path+file)
        # drop Date
        if 'Date' in df:
            df = df.drop("Date", axis=1)
        df = df[['Player 1', 'Country P1', 'Country P2', 'Player 2', '% Player 1','% Player 2', 'Hand P1', 'Hand P2', 'Player1 Odds', 'Player2 Odds', 'Result']]
        df.to_csv(path+file, index=False, encoding='utf-8')
        print('changing to the columns finished...')

def Main():
    try:
        path = "C:\\scrapping\\"
        url = "https://www.tennisbrain.com/"
        window = Tk()
        window.title("WebScrapper")
        window.geometry('600x400+600+200')

        label1 = Label(window, text="Default URL: https://www.tennisbrain.com\n", font=("Arial Bold", 11))
        label1.grid(column=1, row=1)

        label2 = Label(window, text="Please Make a folder 'scrapping' on Local Disk C to continue.\n", font=("Arial", 10))
        label2.grid(column=1, row=3)

        """
        txt = Entry(window, width=60)
        txt.grid(column=1, row=4) """

        message = StringVar()
        message.set('load..')

        result = Label(window, text='', font=("Arial", 9))
        result.grid(column=1, row=15)

        def manual_update():

            # doing further process
            result.config(text="Manual Downloading Started... Please Wait for a while..")
            messagebox.showinfo('Downloading...', 'Manual Downloading Started... Please Wait for while..')
            update(url, path=path)
            changeColumns(path=path)
            result.config(text="File Downloaded to {} success.".format(path))
            messagebox.showinfo('Success', 'Download Success')

        def auto_update():

            # doing further process
            result.config(text="Auto Downloading Started..")
            messagebox.showinfo('Downloading...', 'Auto Downloading Started... Please Wait for a while..')
            start_time = 0
            # runs for every 4 hours
            while (start_time != -1):
                update(url, path=path)
                changeColumns(path=path)
                time.sleep(3600)  # sleeping for 1 hr
                start_time += 1
                messagebox.showinfo('Success', 'Download Success')

            result.config(text="All Files Downloaded to {} success.".format(path))

        btn = Button(window, text='Manual Update', command=manual_update)
        btn.grid(column=1, row=6)

        btn = Button(window, text='Auto Update', command=auto_update)
        btn.grid(column=2, row=6)

        window.mainloop()

    except Exception as e:
        messagebox.showinfo('Error', e)

if __name__ == '__main__':
    Main()