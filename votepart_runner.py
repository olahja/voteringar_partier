#from sys import argv
import argparse
from optparse import OptionParser
import url_constructor
from VotePartListObj import VotePartList
import constants
import r_matrix_creator

def main():
    parties = constants.part_abb_list
    parser = argparse.ArgumentParser()
    riksmote_def = [constants.today_riksmote()]
    parser.add_argument("-p", "--partier", dest="partier", nargs="*", help="add parties", metavar="partier", default=parties)
    parser.add_argument("-r", "--riksmote", dest="riksmote", nargs="*", help="add riksmoten", metavar="riksmote", default=riksmote_def)
    parser.add_argument("-u", "--utskott", dest="utskott", nargs="*", help="add utskott", metavar="utskott", default=None)
    parser.add_argument("-m", "--matrix", dest="matrix", action='store_true', help="create matrix", default=False)
    
    parsed = parser.parse_args()
    print(parsed.partier)
    print(parsed.riksmote)
    print(parsed.utskott)
    print(parsed.matrix)
    partier = sorted([x.upper() for x in parsed.partier])
    riksmote = parsed.riksmote
    utskott_raw = parsed.utskott

    if utskott_raw != None:
        utskott = []
        for this_utskott in utskott_raw:
            if this_utskott in constants.utskott_dict_rev.keys():
                utskott.append(constants.utskott_dict_rev[this_utskott])
            else:
                utskott.append(this_utskott)
    else:
        utskott = utskott_raw
        
    url = url_constructor.construct_url(partier, riksmote)
    vote_part_list = VotePartList(url, utskott)
    if parsed.matrix:
        matrix_data = vote_part_list.get_vote_matrix_data()
        r_matrix_creator.r_execute_input_file(partier, riksmote, utskott, matrix_data)
    
if __name__ == '__main__':
    main()

### TODO ###
'''

finish runner
DONE insert choice to check only vissa utskott
sys.argv flags etc
integrate the whole thing with R
finish matrix
add attendence counting


URGENT: ADD INPUT HYGIENE AND CLEANUP AT RUNNER LEVEL                                     
'''
