def createFile(FILE_NAME):
    try:
        a = open(FILE_NAME, 'wt+')
        a.close()

    except Exception as e:
        raise e

    return

def fileExist(FILE_NAME):
    try:
        a = open(FILE_NAME, 'rt')
        a.close()

    except FileNotFoundError:
        createFile(FILE_NAME)
        
        return False

    except Exception as e:
        raise e

    else:
        return True

def getPlayers(FILE_NAME):
    fileExist(FILE_NAME)

    players = {}

    try:
        a = open(FILE_NAME,'rt')

        for lines in a:
            lines = lines.replace('\n','').split(', ')
            lines[1] = int(lines[1])
            lines[2] = int(lines[2])

            if lines[1] > 4500:
                lines[1] = 4500
    
            if lines[2] > 5063625000:
                lines[2] = 5063625000

            players[lines[0]] = [lines[1],lines[2]]

        a.close() 

        return players

    except Exception as e:
        raise e

def saveFile(FILE_NAME, players = {}):
    try:
        open(FILE_NAME,'w').close()

        a = open(FILE_NAME,'at')

        first = True

        playersKeys = list(players.keys())

        for player in range(len(playersKeys)):
            if first == True:
                a.write(f'{playersKeys[player]}, {players[str(playersKeys[player])][0]}, {players[str(playersKeys[player])][1]}')
                first = False

            else:
                a.write(f'\n{playersKeys[player]}, {players[str(playersKeys[player])][0]}, {players[str(playersKeys[player])][1]}')

        a.close()

    except Exception as e:
        raise e