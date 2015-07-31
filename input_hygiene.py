from more_itertools import unique_everseen
import constants
import datetime

def check_utskott(utskott_spec):

    # cleans up any utskott_spec input with improper capitalization and asserts that utskott_spec exists in constants.utskott_dict
    utskott_spec_list = []
    for utskott in utskott_spec:
        utskott_abbs = sorted(constants.utskott_dict.keys(), key=lambda x: x.lower())
        utskott_non_abbs = sorted(constants.utskott_dict_rev.keys(), key=lambda x: x.lower())
        utskott_abbs_lower = sorted([x.lower() for x in utskott_abbs])
        utskott_non_abbs_lower = sorted([x.lower() for x in utskott_non_abbs])
        assert utskott.lower() in utskott_abbs_lower or utskott.lower() in utskott_non_abbs_lower, 'Improper format, "{0}" not in a valid name or abbreviation'.format(utskott)
        if utskott.lower() in utskott_abbs_lower:
            utskott_index = utskott_abbs_lower.index(utskott.lower())
            utskott_spec_final = utskott_abbs[utskott_index]
            utskott_spec_list.append(utskott_spec_final)
        elif utskott.lower() in utskott_non_abbs_lower:
            utskott_index = utskott_non_abbs_lower.index(utskott.lower())
            utskott_spec_final = utskott_abbs[utskott_index]
            utskott_spec_list.append(utskott_spec_final)

    utskott_spec_list_uniques = check_list_for_duplicates(utskott_spec_list)

    return utskott_spec_list_uniques


def check_list_for_duplicates(thislist):
    thislist_uniques = list(unique_everseen(thislist))
    if thislist != thislist_uniques:
        print("Found duplicates in {0}, removing...".format(thislist))
    return thislist_uniques


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
