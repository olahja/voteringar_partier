#from sys import argv
import argparse
import url_constructor
from VotePartListObj import VotePartList
import constants
import r_matrix_creator
import input_hygiene
import datetime

def main():

    parties = constants.part_abb_list
    parser = argparse.ArgumentParser()
    riksmote_def = [constants.today_riksmote()]

    parser.add_argument("-p", "--partier", dest="partier", nargs="+", help="Add parties", metavar="partier", default=parties)
    parser.add_argument("-r", "--riksmote", dest="riksmote", nargs="+", help="Add riksmoten", metavar="riksmote", default=riksmote_def)
    parser.add_argument("-u", "--utskott", dest="utskott", nargs="+", help="Add utskott", metavar="utskott", default=None)
    parser.add_argument("--matrix", dest="matrix", action='store_true', help="Create matrix", default=False)
    parser.add_argument("--franvaro", dest="check_franvaro", action='store_true', help="Print franvaro dictionary", default=False)
    parser.add_argument("--win-loss-ratio", dest="win_loss", action='store_true', help="Print the win/loss ratio for the specified parties", default=False)
    parser.add_argument("--losses", dest="losses", action='store_true', help="Print the voteringar where the specified parties have lost", default=False)
    parser.add_argument("--losses-save", dest="losses_save", action='store_true', help="Save a file with info about the voteringar where the specified parties have lost", default=False)
    
    
    parsed = parser.parse_args()

    # print(parsed.partier)
    # print(parsed.riksmote)
    # print(parsed.utskott)
    # print(parsed.matrix)

    partier = sorted([x.upper() for x in parsed.partier])
    riksmote = parsed.riksmote
    utskott_raw = parsed.utskott
    
    input_hygiene.check_part(partier)
    input_hygiene.check_riksmote_format(riksmote)
    if utskott_raw != None:
        utskott = input_hygiene.check_utskott(utskott_raw)
    else:
        utskott = utskott_raw
        
    url = url_constructor.construct_url(partier, riksmote)
    vote_part_list = VotePartList(url, utskott)
    if parsed.matrix:
        print("url", url)
        print("vote_part_list_parts", vote_part_list.get_these_parts())
        matrix_data = vote_part_list.get_vote_matrix_data()
        #print("matrix_data_runner:", matrix_data)
        r_matrix_creator.r_execute_input_file(partier, riksmote, utskott, matrix_data)

    if parsed.check_franvaro:
        print(vote_part_list.get_vote_franvaro_dict())

    if parsed.win_loss:
        print(vote_part_list.get_win_loss_ratio())

    if parsed.losses:
        print(vote_part_list.loss_list_str())

    if parsed.losses_save:
        write_string = vote_part_list.loss_list_str()
        path = "output/losses/"
        write_file(write_string, path, utskott, riksmote, partier)


def write_file(write_string, path, utskott, riksmote, partier):
    if utskott != None:
        utskott_str = "_".join(utskott)
    riksmote_str = "_".join(riksmote).replace("/", "-")
    if partier == constants.part_abb_list:
        partier_str = "alla-partier"
    else:
        partier_str = "_".join(partier)

    date_str = str(datetime.date.today())
    if utskott != None:
        save_str = open("{0}losses_-_{1}_-_rm-{2}_-_{3}_-_{4}.txt".format(path, utskott, riksmote_str, partier_str, date_str), "w")
    else:
        save_str = open("{0}losses_-_rm-{1}_-_{2}_-_{3}.txt".format(path, riksmote_str, partier_str, date_str), "w")
    save_str.write(write_string)

    
if __name__ == '__main__':
    main()

### TODO ###
'''

DONE insert choice to check only vissa utskott
DONE sys.argv flags etc
DONE integrate the whole thing with R
DONE finish matrix
DONE add attendence counting
DONE URGENT: ADD INPUT HYGIENE AND CLEANUP AT RUNNER LEVEL
homogenize the party variables, --> make sure that everytime a method or function uses a list of either ALL POSSIBLE parties or USER SPECIFIED parties, they are using only one of two possible sources. (ALL POSSIBLE or USER SPECIFIED)


add feature to visualize how samstämmighet changes over time



'''
