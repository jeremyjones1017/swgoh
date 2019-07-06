from __future__ import division
import pandas as pd
import os
import csv
import datetime
import calendar
from collections import Counter
import sys
import numpy as np
from numpy.random import choice
from termcolor import colored

def main():
	os.system('cls')
	swgoh_dir = 'C:/Users/Jeremy/Dropbox/Programing/swgoh/'
	
	char_df = pd.read_csv(os.path.join(swgoh_dir,'characters.csv'))
	gear_df = pd.read_csv(os.path.join(swgoh_dir,'gear.csv'))
	
	breakdown_file = os.path.join(swgoh_dir,'breakdown.csv')
	bd_dict = dict()
	with open(breakdown_file,'r') as input:
		input_reader = csv.reader(input,delimiter = ',')
		for line in input_reader:
			if line[0] != 'Initial Gear':
				bd_dict[line[0]] = line[1:]
	
	
	do_level(char_df)
	do_shards(char_df)
	n_gear = 5		#Number of gear pieces to display
	level = 8
	#do_gear_by_level(char_df,gear_df,bd_dict,n_gear,level,verbose=True)
	if len(sys.argv) == 2:
		tar_char = sys.argv[1]
		do_gear_individual_by_level(char_df,gear_df,bd_dict,tar_char)
		do_gear_individual_all(char_df,gear_df,bd_dict,tar_char,n_gear)
	else:
		tar_char = choose_focus_char(char_df,gear_df)
		print('\n{} was chosen to be our next focus for gearing up'.format(tar_char))
		do_gear_individual_by_level(char_df,gear_df,bd_dict,tar_char)
		do_gear_individual_all(char_df,gear_df,bd_dict,tar_char,n_gear)
	do_gear_all(char_df,gear_df,bd_dict,n_gear)
		
	

def populate_breakdown_list(df,bd_dict):
	gear_needed = []
	gear_needed.extend(list(df['Top_Left']))
	gear_needed.extend(list(df['Mid_Left']))
	gear_needed.extend(list(df['Bot_Left']))
	gear_needed.extend(list(df['Top_Right']))
	gear_needed.extend(list(df['Mid_Right']))
	gear_needed.extend(list(df['Bot_Right']))
	while 'Done' in gear_needed:
		gear_needed.remove('Done')
	gear_count = Counter(gear_needed)
	breakdown_count = get_breakdown_gear(gear_count,bd_dict) 
	return breakdown_count

def get_breakdown_gear(gear_count,bd_dict):
	breakdown_needed = []
	for i in gear_count:
		for j in range(gear_count[i]):
			bd_line = bd_dict[i]
			while '' in bd_line:
				bd_line.remove('')
			for li,val in enumerate(bd_line):
				if li %2 == 0:
					for k in range(int(bd_line[li+1])):
						breakdown_needed.append(bd_line[li])
	breakdown_count = Counter(breakdown_needed)
	return breakdown_count
	
def calc_sneed(curr_shards,star):
	stars = np.array([0,1,2,3,4,5,6,7])
	shard_start = np.array([0,10,25,50,80,145,230,330])
	total_shard = shard_start[np.where(stars == star)][0]+curr_shards
	sneed = 330 - total_shard
	return sneed

def do_level(char_df):
	print('Characters to level up')
	print('========================================')
	level_df = char_df[char_df.Level < 85]
	level_char = list(level_df.Character)
	level_level = list(level_df.Level)
	zipped = zip(level_level,level_char)
	zipped = sorted(zipped, reverse = True)
	print('Level, Character')
	for i in zipped:
		if i[0] != 0:
			print(i[0],i[1])

def do_shards(char_df):
	print('\nCharacters who need shards')
	print('========================================')
	
	chars_to_get = ['C-3P0','Darth Revan','Chewbacca','Padme Amidala','Themself']
	years = [2019,2019,2019,2019,0]
	months = [9,9,10,11,0]
	days = [2,2,3,1,0]
	
	
	for i,val in enumerate(chars_to_get):
		do_these_shards(char_df,chars_to_get[i],years[i],months[i],days[i])
	
def do_these_shards(char_df,char_to_get,year,month,day):
	shard_df = char_df[char_df.Shards < 330]
	shard_df = shard_df[shard_df.Needed_For == char_to_get]
	shard_char = list(shard_df.Character)
	shard_star = list(shard_df.Star)
	shard_shard = list(shard_df.Shards)
	
	sneed = []
	for i,val in enumerate(shard_shard):
		sneed.append(calc_sneed(val,shard_star[i]))
	zipped = zip(sneed,shard_star,shard_char)
	zipped = sorted(zipped)
	
	today = datetime.datetime.today()
	today_date = datetime.date(today.year,today.month,today.day)
	
	if char_to_get != 'Themself':
		date = datetime.date(year,month,day)
		days_until = (date - today_date).days
		print('\n\t{} event estimated to start in {} days ({})'.format(char_to_get,days_until,date.strftime('%d %b')))
	else:
		print('\n\t Non-event characters:')
	
	for i in zipped:
		source = list(shard_df.Source[shard_df.Character == i[2]])[0]
		days_to_complete = i[0]/2.
		today = datetime.datetime.today()
		completion_date = today+datetime.timedelta(days = days_to_complete)
		if i[0] > 0 and i[1] != 0:
			#print(source)
			color = 'white'
			if source == 'Yellow':
				color = 'yellow'
			elif source == 'Blue':
				color = 'cyan'
			elif source == 'Store':
				color = 'magenta'
			elif source == 'Red':
				color = 'red'
			prog_bar = ''
			if char_to_get != 'Themself':
				percent_to_go = days_to_complete/days_until
				for j in range(10):
					if j/10 < percent_to_go:
						prog_bar+=u"\u2588"
					else:
						prog_bar+=' '
				prog_bar+='|'
				while percent_to_go > 1.1:
					prog_bar+=u"\u2588"
					percent_to_go -= 0.1
						
				print('{:<30} - {:<3} shards, {} ({:<3} days) {}'.format(colored(i[2],color),i[0],completion_date.strftime('%d %b'),int(days_to_complete),prog_bar))
			else:
				print('{:<30} - {:<3} shards, {} ({:<3} days)'.format(colored(i[2],color),i[0],completion_date.strftime('%d %b'),int(days_to_complete)))
			
def do_gear_by_level(char_df,gear_df,bd_dict,n_gear,X,verbose=False):
	
	#X = 8		#Leveling from
	Y = X+1		#Leveling to

	Yprint = Y
		
	GX_char_df = gear_df[gear_df.LF == X]
	GX_char_df = GX_char_df[GX_char_df.TL == 'Y']
	GX_char = list(GX_char_df.Character)
	if len(GX_char) != 0:
		GY_gear_needed = []
		for i,val in enumerate(GX_char):
			if i == 0:
				GX_gear_df = gear_df[gear_df.Character == val]
			else:
				this_df = gear_df[gear_df.Character == val]
				GX_gear_df = pd.concat([GX_gear_df,this_df])
		GX_gear_df = GX_gear_df[GX_gear_df.LF == X]
		GY_breakdown_count = populate_breakdown_list(GX_gear_df,bd_dict)
		GY_breakdown_sort = sorted(GY_breakdown_count)
		if verbose:
			print('\nAll gear needed to get {} from G{} to G{} (current G{} only)'.format(GX_char,X,Yprint,X))
			print('========================================')
			for i in GY_breakdown_sort:
				print(i,'-',GY_breakdown_count[i])
			if len(GY_breakdown_count) > n_gear:
				print('\nTop {} gear needed to get {} from G{} to G{} (current G{} only)'.format(n_gear,GX_char,X,Yprint,X))
				print('========================================')
				GY_breakdown_mc = GY_breakdown_count.most_common(n_gear)
				for i in GY_breakdown_mc:
					print(i[0],'-',i[1])
		else:
			print('\nTop {} gear needed to get {} from G{} to G{} (current G{} only)'.format(n_gear,GX_char,X,Yprint,X))
			print('========================================')
			GY_breakdown_mc = GY_breakdown_count.most_common(n_gear)
			for i in GY_breakdown_mc:
				print(i[0],'-',i[1])
	else:
		print('There are no characters at G{}'.format(X))

def do_gear_all(char_df,gear_df,bd_dict,n_gear):
	print('\nTop {} gear needed to level everyone all the way'.format(n_gear))
	print('========================================')
	all_breakdown_count = populate_breakdown_list(gear_df,bd_dict)
	all_breakdown_mc = all_breakdown_count.most_common(n_gear)
	for i in all_breakdown_mc:
		print(i[0],'-',i[1])

def do_gear_individual_by_level(char_df,gear_df,bd_dict,tar_char):
	if tar_char in list(char_df.Character):
		X = list(char_df.Gear[char_df.Character == tar_char])[0]		#Leveling from
		Y = X+1		#Leveling to
		Yprint = Y
		print('\nAll gear needed to get {} to G{}'.format(tar_char,Yprint))
		print('========================================')
		char_gear_df = gear_df[gear_df.Character == tar_char]
		char_gear_df = char_gear_df[char_gear_df.LF == X]
		char_breakdown_count = populate_breakdown_list(char_gear_df,bd_dict)
		char_breakdown_sort = sorted(char_breakdown_count)
		for i in char_breakdown_sort:
			print(i,'-',char_breakdown_count[i])
	else:
		print('\nCharacter "{}" not in our records'.format(tar_char))

def do_gear_individual_all(char_df,gear_df,bd_dict,tar_char,n_gear):
	if tar_char in list(char_df.Character):
		print('\nTop {} gear needed to level {} all the way'.format(n_gear,tar_char))
		print('========================================')
		char_gear_df = gear_df[gear_df.Character == tar_char]
		char_breakdown_count = populate_breakdown_list(char_gear_df,bd_dict)
		char_breakdown_mc = char_breakdown_count.most_common(n_gear)
		for i in char_breakdown_mc:
			print(i[0],'-',i[1])
	else:
		print('\nCharacter "{}" not in our records'.format(tar_char))

def choose_focus_char(char_df,gear_df):
	char_list = list(char_df.Character)
	char_freq = []		#Forms pdf of sorts. (# of gear pieces to get to 13)*(level/85)^2*(stars/7)*(1/Team)
	for i,char in enumerate(char_list):
		this_char_gear_level = list(char_df.Gear[char_df.Character == char])[0]
		this_char_gear_df = gear_df[gear_df.Character == char]
		this_char_gear_df = this_char_gear_df[this_char_gear_df.LF == this_char_gear_level]
		this_glevel_gear = []
		for index,rows in this_char_gear_df.iterrows():
			this_glevel_gear = [rows.Top_Left,rows.Mid_Left,rows.Bot_Left,rows.Top_Right,rows.Mid_Right,rows.Bot_Right]
		n_gear = 0
		for j in this_glevel_gear:
			if j != 'Done':
				n_gear+=1
		if n_gear == 0:
			char_freq.append(0)
			continue
		if this_char_gear_level < 12:
			n_gear+= ((12-this_char_gear_level)*6)
		this_char_level = list(char_df.Level[char_df.Character == char])[0]
		this_char_star = list(char_df.Star[char_df.Character == char])[0]
		this_char_team = list(char_df.Team[char_df.Character == char])[0]
		this_freq = n_gear*(this_char_level/85)**2*(this_char_star/7)*(1/this_char_team)
		char_freq.append(this_freq)
	char_freq = np.array(char_freq)
	char_freq/= sum(char_freq)
	draw = choice(char_list,1,p=char_freq)
	return draw[0]

class month:
	def __init__(self,add):
		self.add = add
		today = datetime.datetime.today()
		this_month = today.month
		today_date = datetime.date(today.year, today.month, today.day)
		self.num = this_month + self.add
		target_month = datetime.date(today.year,self.num, 1)
		self.name = target_month.strftime('%b')
		self.days_until = (target_month - today_date).days

main()