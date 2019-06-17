# Score Reporter .py
# Version 3.1
# By Davis "Lucky" Lai

# Imports System Files
import string
import os
from datetime import date

# Imports S3 Bucket Files
import logging
import boto3
from botocore.exceptions import ClientError
# Setup for AWS S3 Bucket
s3 = boto3.client('s3')
bucket_name = 'AWS S3 Bucket Name'

# Imports and Sets Challonge Information
import challonge
challonge.set_credentials("USERNAME","API KEY")

# Setup for program files
player_dict={}				# Holds Players Cleaned Names and Real Names
serverfiles=[]				# Holds the list of downloaded files
all_player_games = {}
all_player_stats = {}		# Holds [Total Set Wins, Total Set Losses, Total Game Wins, Total Game Losses,]
all_player_matchups = {}	# Holds all player1[player2] results as [win, loss] format (From Player 1 Perspective)
today = date.today()		# Initializes the date

def actualreport(player1, player2, player1_score, player2_score, semester, event_name, match):
	if (player1_score > player2_score):
		winner = player1
		loser = player2
		winner_score = player1_score
		loser_score = player2_score
	else:
		winner = player2
		loser = player1
		winner_score = player2_score
		loser_score = player1_score
	# Line to add to P1 File
	winner_line = "W" + "\t" + loser + "\t" + str(winner_score)+"-"+str(loser_score) + "\t" + str(semester) + "\t" + str(event_name) + "\t" + str(match) + "\t" + "Reported: "+today.isoformat()

	# Line to add to P2 File
	loser_line = "L" + "\t" + winner + "\t" + str(loser_score)+"-"+str(winner_score) + "\t" + str(semester) + "\t" + str(event_name) + "\t" + str(match) + "\t" + "Reported: "+today.isoformat()

	# Prints Data Reported
	print("Reporting: ",winner,loser,"\t",winner_score,loser_score,"\t",match)
	# OPENS/CREATES PLAYER 1
	winner_filename = os.getcwd()+"/data/"+winner + ".txt"
	winner_file = open(winner_filename, "a")
	winner_file.write(winner_line+"\n")

	# OPENS/CREATES PLAYER 2
	loser_filename = os.getcwd()+"/data/"+loser + ".txt"
	loser_file = open (loser_filename, "a")
	loser_file.write(loser_line+"\n")
	return

def scorereport():
	while (True):
		try:
			player1 = (input("Please input the player that won: ").lower()).replace(" ","")
			p1_score = int(input("Please enter the winning player's score: "))
			player2 = (input("Please input the player that lost: ").lower()).replace(" ","")
			p2_score = int(input("Please enter the losing player's score: "))

			while (True):
				semester_date = input("Please enter the semester (Example: Fall 2019): ").lower()
				event_name = input("Please enter the name of the event or the Weekly number: ")
				date_list = semester_date.split(" ")
				#print(date_list)
				if (date_list[0]=="fall" or date_list[0]=="spring"):
					break
				else:
					print("You did not enter valid dates.")
			match = input("Please enter the match label (Example: Winners Finals): ").lower().replace(" ","")

			actualreport(player1, player2, p1_score, p2_score, semester_date, event_name, match)

			# Prompts the user as to whether or not they wish to enter more data
			while (True):
				user_continue = input("Data has been written. Would you like to report another score? (Yes/No): ").lower()
				if (user_continue=="y" or user_continue=="yes"):
					break
				elif (user_continue=="n" or user_continue=="no"):
					print("Returning to the Main Menu...")
					return
				else:
					print("That was not a valid option. Please try again.")
		except:
			print("You entered invalid data. Please try again.")

def scorecheckplayer(x):
	while (True):
		try:
			player = input("Please enter a player name (Press enter to quit): ").lower().replace(" ","")
			if (player==""):
				return

			player = cleanstring(player, x)

			# Prints Out Matchups
			matchups = all_player_matchups[player]
			for match in matchups:
				print("\t"+"vs. "+player_dict[cleanstring(match, x)]+"\t"+"Wins: "+str(matchups[match][0])+"\t"+"Losses: "+str(matchups[match][1]))

			# Assigns Game Stats to Variables
			set_wins = all_player_stats[player][0]
			set_losses = all_player_stats[player][1]
			game_wins = all_player_stats[player][2]
			game_losses = all_player_stats[player][3]

			# Calculates percentages
			set_win_percentage = (set_wins/(set_wins+set_losses))*100
			game_win_percentage = (game_wins/(game_wins+game_losses))*100

			# Prints Game Stats
			print("Total Set Wins: "+ str(set_wins)+"\t" + "Total Set Losses: " + str(set_losses) + "\t" + "Set Win Percentage: "+str(set_win_percentage)+"%")
			print("Total Game Wins: "+ str(game_wins)+"\t"+"Total Game Losses: "+str(game_losses)+"\t"+"Game Win Percentage: "+str(game_win_percentage)+"%")
		except:
			print("It appears you did not pick a valid player name...")

def allscores():
	for player in all_player_stats:
		print(player_dict[player]+"\tTotal Set Wins: "+str(all_player_stats[player][0])+"\t"+"Total Set Losses: "+str(all_player_stats[player][1])+"\t"+"Total Game Wins: "+str(all_player_stats[player][2])+"\t"+"Total Game Losses: "+str(all_player_stats[player][3]))

def allmatchups():
	for player_matchups in all_player_matchups:
		print(player_dict[player_matchups])
		matchups = all_player_matchups[player_matchups]
		for individual_matchup in all_player_matchups[player_matchups]:
			print("\t"+"vs. "+player_dict[individual_matchup]+"\t"+"Wins: "+str(matchups[individual_matchup][0])+"\t"+"Losses: "+str(matchups[individual_matchup][1]))

def headtohead(x):
	while (True):
		try:
			player1_raw = input("Please enter the name of the first player: ")
			player1 = cleanstring(player1_raw, x)
			player2_raw = input("Please enter the name of the second player: ")
			player2 = cleanstring(player2_raw, x)

			#print(all_player_matchups.keys())
			matchup = all_player_matchups[player1][player2]
			print(player1_raw+" vs. "+player2_raw+"\t"+str(matchup[0])+" - "+str(matchup[1]))

			for game in all_player_games[player1]:
				if (player2 in game):
					print("\t"+"\t".join(game[2:]))
			break
		except:
			print("Something went wrong. Invalid player.")

def csvExport():		# INCOMPLETE!!!
	file = open(os.getcwd()+"/data/matchups.csv", 'w')
	toprow=[]
	leftcolumn=[]
	for player in all_player_matchups:
		toprow.append(player_dict[player])
	return

def LineToList(line):
	return line.split("\t")
	# Index		0		1		2		3			4		5		6
	#			W/L 	Opp 	Score 	Semester 	Event 	Match 	Reported

def load(x):
	# Looks at all files in the 'data' directory that ends in .txt
	for filename in os.listdir(os.getcwd()+"/data"):
		if filename.endswith(".txt"):
			file = open(os.getcwd()+"/data/"+filename, 'r')
			player = filename[:-4]
			player_file_lines = file.readlines()

			lines_read = set()
			file_write = open(os.getcwd()+"/data/"+filename, 'w')
			
			# Begins adding data for a single person
			set_wins = 0
			set_losses = 0
			game_wins = 0
			game_losses = 0

			matchups = {}
			player = cleanstring(player, x)
			all_player_games[player] = []

			player_dict[player] = filename[:-4]

			# Goes through all the lines
			for line in player_file_lines:
				if (line not in all_player_games[player]):
					if (line[:-12] not in lines_read):
						file_write.write(line)
						lines_read.add(line[:-12])
						line_data = line.split("\t")
						all_player_games[player].append(line)


						# Check if Opponent exists in the dictionary. If not, add blank data
						opponent = cleanstring(line_data[1], x)
						if (opponent not in matchups.keys()):
							matchups[opponent] = [0, 0]

						if (int(line_data[2][0])>0 or int(line_data[2][2])>0):
							# Win or Loss
							if (line_data[0] == "W"):
								set_wins += 1
								matchups[opponent] = [matchups[opponent][0]+1,matchups[opponent][1]]
							elif (line_data[0] == "L"):
								set_losses += 1
								matchups[opponent] = [matchups[opponent][0],matchups[opponent][1]+1]

							# Adding Won and Lost games
							#print(line)
							game_wins += int(line_data[2][0])
							game_losses += int(line_data[2][2])

			# Puts player data into 'all_player_stats' and 'all_player_matchups'
			all_player_matchups[player] = matchups
			all_player_stats[player] = [set_wins, set_losses, game_wins, game_losses]

			file_write.close()

def clear():							# WORKS
	for filename in os.listdir(os.path.join(os.getcwd(),"data")):
		if filename.endswith(".txt"):
			os.remove(os.path.join(os.getcwd(),"data", filename))
	return

def download():							#WORKS
	#my_bucket = s3.Bucket(bucket_name)
	bucket_files = s3.list_objects_v2(Bucket=bucket_name)
	print("Downloading:", end=" ")
	for obj in bucket_files['Contents']:
		key = obj['Key']
		if (key.endswith(".txt")):
			serverfiles.append(key)
			file = os.path.join(os.getcwd(),"data",key)
			with open(file, "wb") as file_location:
				s3.download_fileobj(bucket_name, key, file_location)
			print(key, end="\t")
	return

def upload():
	for key in os.listdir(os.path.join(os.getcwd(),"data")):
		if key.endswith(".txt"):
			revised_key = os.path.join(os.getcwd(),"data",key)
			with open(revised_key, "rb") as file:
				s3.upload_fileobj(file, bucket_name, key)
			print(revised_key)
	return

def cleanstring(name, choice):
	if choice==0:
		return name.lower().replace(" ","")
	if choice==1:
		newstring = ""
		for char in name:
			if not ((char in string.punctuation) or (char in 'aeiou1234567890')):
				newstring += char
		return newstring
	return

def challongecalculations(desired_game, year, x):
	#myparams = {'subdomain' : 'https://challonge.com/communities/OberlinSmash'}
	for tournament in challonge.tournaments.index():
		complete = tournament["state"] == "complete"
		event_name = tournament["name"]
		#print(event_name)
		date = ((str(tournament["start_at"]).split(" "))[0]).split("-")
		if (len(date)!=3):
			date = str(tournament["created_at"]).split("-")
			#print(date)
		date_true = False
		if (len(date)>=3):
			date_true = (int(date[0])==year and int(date[1])>=8) or (int(date[0])==year+1 and int(date[1])<=6)
			if (int(date[1])>=8 and int(date[1])<=12):
				semester = "fall"
			else:
				semester = "spring"
			semester = semester +"-"+str(year)
		game = str(tournament["game_name"]).lower().replace(" ","") == desired_game
		#print("Name:", event_name,"\t Game:",game,"\t Date:",date_true)
		if (complete and game and date_true):
			for match in challonge.matches.index(tournament["id"]):
				scores = match["scores_csv"].split("-")
				if (len(scores)==2):
					player1 = challonge.participants.show(tournament["id"],match["player1_id"])['name'].lower().replace(" ","")
					player2 = challonge.participants.show(tournament["id"],match["player2_id"])['name'].lower().replace(" ","")
					
					if player1=="":
						player1 = challonge.participants.show(tournament["id"],match["player1_id"])['challonge_username'].lower().replace(" ","")
					if player2=="":
						player2 = challonge.participants.show(tournament["id"],match["player2_id"])['challonge_username'].lower().replace(" ","")
					
					player1 = cleanstring(player1, 0)
					player2 = cleanstring(player2, 0)
					player1_score = scores[0]
					player2_score = scores[1]
					matcher = match['round']
					#print("REPORTING GAME")
					print(event_name, end='')
					actualreport(player1, player2, player1_score, player2_score, semester, event_name, matcher)
	return

def main():
	# Checks and creates directory if necessary
	try:
		os.mkdir("data", 0o777)
		print("Created new directory \"Data\" for player results")
	except OSError:
		print("Data directory found!")

	# Clears Data Folder
	clear()

	# Downloads files from server
	download()

	print()
	clean = input("Would you like to clean the names thoroughly?? (Yes/No): ").lower()
	if (clean=="yes" or clean=="y"):
		x = 1
	elif (clean=="no" or clean=="n"):
		x = 0
	else:
		print("Invalid choice.... Not cleaning names")
		x = 0

	while (True):
		try:
			# Loads all the files in the 'data' directory
			load(x)

			# Prints Menu Choices
			print("1. Report Score \t 2. Individual Result \t 3. View All Scores \t 4. View All Matchups \t 5. Head to Head Matchup \t 6. Export Matchups to CSV \t 7. Upload to Server")

			# User Selects Menu Choice
			menu_choice = input("Please enter your option (Press enter to quit): ")

			# Runs operation based on Menu Choice
			if (menu_choice == ""):
				return
			elif menu_choice == "1":
				scorereport(x)
			elif menu_choice == "2":
				scorecheckplayer(x)
			elif menu_choice =="3":
				allscores()
			elif menu_choice =="4":
				allmatchups()
			elif menu_choice=="5":
				headtohead(x)
			elif menu_choice=="6":
				csvExport()
			elif menu_choice=="7":
				upload()
			elif menu_choice=="8":
				while(True):
					#try:
					if (True):
						game = input("What game would you like to search? <Press enter to quit>: ").lower().replace(" ","")
						year = (input("What year would you like to search? <Press enter to quit>: "))
						if (game=="" or year==""):
							print("Exiting out of Challonge Calculation...")
							break
						challongecalculations(game, int(year), x)
						break
					#except:
						#print("Invalid Data")
			else:
				print("That was not a valid option.")
		except:
			print("Uh oh! Something happened.")

main()