#from sys import argv
import argparse
from optparse import OptionParser
import url_constructor
from VotePartListObj import VotePartList
import constants


def main():
    parties = constants.part_abb_list
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--partier", dest="partier", nargs="*", help="add parties", metavar="partier", default=parties)
    parser.add_argument("-r", "--riksmote", dest="riksmote", nargs="*", help="add riksmoten", metavar="riksmote", default=constants.today_riksmote())
    parser.add_argument("-u", "--utskott", dest="utskott", nargs="*", help="add utskott", metavar="utskott", default=None)
    
    parsed = parser.parse_args()
    print(parsed.partier)
    print(parsed.riksmote)
    print(parsed.utskott)
    partier = parsed.partier
    riksmote = parsed.riksmote
    utskott = parsed.utskott
    url = url_constructor.construct_url(partier, riksmote)

main()

### TODO ###
'''

finish runner
DONE insert choice to check only vissa utskott
sys.argv flags etc
integrate the whole thing with R

                                     
'''
