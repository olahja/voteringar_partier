import re
import datetime
import constants

def check_riksmote_format(riksmote_list):

    if datetime.date.today().month <= 9:
        today_year = datetime.date.today().year
    else:
        today_year = datetime.date.today().year + 1
    error_msg = '"{0}" in riksmote_list is not properly formatted, proper format is "2014/15"'
    for riksmote in riksmote_list:
        assert type(riksmote) == str, error_msg.format(riksmote)

        # assert that riksmote is between 2002 and current year (may bug out during the period around nytt riksmote, check if-statement above)
        assert int(riksmote[:4]) in [x for x in range(2002, today_year)], error_msg.format(riksmote)
        assert riksmote[4:5] == "/", error_msg.format(riksmote)
        # assert that riksmote is two consecutive years, e.g. "2014/15"
        assert int(riksmote[5:]) == int(riksmote[2:4]) + 1, error_msg.format(riksmote)

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
    check_riksmote_format(riksmote_list)
    partier_list = [x.upper() for x in partier_list]
    check_part(partier_list)

    partier_formatted = format_partier_str(partier_list)
    riksmoten_formatted = format_riksmoten(riksmote_list)
    url = "http://data.riksdagen.se/voteringlistagrupp/?{0}bet=&punkt=&{1}utformat=xml".format(riksmoten_formatted, partier_formatted)
    return url

#partier_list = ["C", "V", "SD"]
#riksmote_list = ["2002/03", "2003/04", "2004/05", "2005/07"]

#print(construct_url(partier_list, riksmote_list))
