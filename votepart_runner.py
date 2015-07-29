#from sys import argv
import argparse
from optparse import OptionParser
import url_constructor
from VotePartListObj import VotePartList
import constants


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
    
    partier = parsed.partier
    riksmote = parsed.riksmote
    utskott = parsed.utskott
    url = url_constructor.construct_url(partier, riksmote)
    
    
if __name__ == '__main__':
    main()

### TODO ###
'''

finish runner
DONE insert choice to check only vissa utskott
sys.argv flags etc
integrate the whole thing with R

                                     
'''
