#from sys import argv
import argparse
import url_constructor
from VotePartListObj import VotePartList
import constants
import r_matrix_creator
import input_hygiene

def main():

    parties = constants.part_abb_list
    parser = argparse.ArgumentParser()
    riksmote_def = [constants.today_riksmote()]
    parser.add_argument("-p", "--partier", dest="partier", nargs="*", help="add parties", metavar="partier", default=parties)
    parser.add_argument("-r", "--riksmote", dest="riksmote", nargs="*", help="add riksmoten", metavar="riksmote", default=riksmote_def)
    parser.add_argument("-u", "--utskott", dest="utskott", nargs="*", help="add utskott", metavar="utskott", default=None)
    parser.add_argument("-m", "--matrix", dest="matrix", action='store_true', help="create matrix", default=False)
    parser.add_argument("--franvaro", dest="check_franvaro", action='store_true', help="print franvaro dictionary", default=False)
    
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
        matrix_data = vote_part_list.get_vote_matrix_data()
        r_matrix_creator.r_execute_input_file(partier, riksmote, utskott, matrix_data)

    if parsed.check_franvaro:
        print(vote_part_list.get_vote_franvaro_dict())
    
if __name__ == '__main__':
    main()

### TODO ###
'''

finish runner
DONE insert choice to check only vissa utskott
sys.argv flags etc
DONE integrate the whole thing with R
DONE finish matrix
DONE add attendence counting


DONE URGENT: ADD INPUT HYGIENE AND CLEANUP AT RUNNER LEVEL                                     
'''
