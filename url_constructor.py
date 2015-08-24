import re
import datetime
import constants
import input_hygiene


def check_part(partier_list):
    for part in partier_list:
        assert part in constants.part_abb_list
        
def format_partier_str(partier_list):
    partier_formatted_list = []
    num = 1
    for parti in partier_list:
        partier_formatted_list.append("grupp{0}={1}&".format(num, parti))
        num += 1
    partier_str = "".join(partier_formatted_list)
    return partier_str

def format_riksmoten(riksmote_list):
    partier_formatted = ""
    for rm in riksmote_list:
        partier_formatted += "rm={0}{1}{2}&".format(rm[:4], "%2F", rm[5:])

    return partier_formatted

def construct_url(partier_list, riksmote_list):
    input_hygiene.check_riksmote_format(riksmote_list)
    partier_list = [x.upper() for x in partier_list]
    check_part(partier_list)

    partier_formatted = format_partier_str(partier_list)
    riksmoten_formatted = format_riksmoten(riksmote_list)
    url = "http://data.riksdagen.se/voteringlistagrupp/?{0}bet=&punkt=&{1}utformat=xml".format(riksmoten_formatted, partier_formatted)
    return url

#partier_list = ["C", "V", "SD"]
#riksmote_list = ["2002/03", "2003/04", "2004/05", "2005/07"]

#print(construct_url(partier_list, riksmote_list))
