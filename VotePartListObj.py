import requests
import xml.etree.ElementTree as ET
import re
from VotePartObj import VotePart
import constants

class VotePartList(object):

    def __init__(self, url, utskott_spec=None):
        self.url = url
        if utskott_spec != None:
            self.utskott_spec = self.set_utskott_spec(utskott_spec)
        else:
            self.utskott_spec = None
        self.html = self.set_html()
        self.element = self.set_element()
        self.vote_part_list = self.set_vote_part_list()
        
    def get_url(self):
        return self.url

    def set_utskott_spec(self, utskott_spec):
        # cleans up any utskott_spec input with improper capitalization and asserts that utskott_spec exists in constants.utskott_dict
        utskott_abbs = sorted(constants.utskott_dict.keys(), key=lambda x: x.lower())
        utskott_abbs_lower = sorted([x.lower() for x in utskott_abbs])
        assert utskott_spec.lower() in utskott_abbs_lower, 'Improper format, "{0}" not in utskott_abb_list'
        utskott_index = utskott_abbs_lower.index(utskott_spec.lower())
        utskott_spec_final = utskott_abbs[utskott_index]
        return utskott_spec_final

    def get_utskott_spec(self):
        return self.utskott_spec

    def set_html(self):
        endpoint = self.get_url()
        html = requests.get(endpoint).text
        return html

    def get_html(self):
        return self.html

    def set_element(self):
        html = self.get_html()
        element = root = ET.fromstring(html)
        return element

    def get_element(self):
        return self.element

#### METADATA ####
    
    def get_antal(self):
        element = self.get_element()
        antal = int(element.attrib['antal'])
        return antal
        
    def get_riksmote(self):
        element = self.get_element()
        riksmote_rawstring = element.attrib['villkor']
        riksmoten = re.findall("\d{4}/\d{2}", riksmote_rawstring)
        return riksmoten

#### PRODUCTS ####
    
    def get_grupp_dict(self):
        ## e.g. {"Grupp1": "C"}
        element = self.get_element()
        grupp_dict = {}
        
        for attribut in element.attrib:
            if re.search("grupp\d+", attribut) != None:
                grupp_dict_key = attribut[0].upper() + attribut[1:]
                if element.attrib[attribut] == "":
                    grupp_dict_value = None
                else:
                    grupp_dict_value = element.attrib[attribut]
                grupp_dict[grupp_dict_key] = grupp_dict_value

        return grupp_dict

    def set_vote_part_list(self, utskott_spec=None):
        if utskott_spec == None:
            utskott_spec == self.get_utskott_spec()
        element = self.get_element()
        vote_part_list = []
        grupp_dict = self.get_grupp_dict()
        for votering in element.findall('votering'):
            this_votepart = VotePart(votering, grupp_dict)
            # checks if a utskott has been specified, and if so only adds those voteparts that match the specified utskott
            if utskott_spec != None:
                if this_votepart.get_utskott() == utskott_spec:
                    vote_part_list.append(this_votepart)
            else:
                vote_part_list.append(this_votepart)
        assert len(vote_part_list) == self.get_antal()
        #print("len vote_part_list: " + str(len(vote_part_list)))
        return vote_part_list

    def get_vote_part_list(self):
        return self.vote_part_list

    def get_outcomes_dict(self):
        ## e.g. {'C3DSGH542FGFID-SDF42SDG-TUJHGF4DH': {'V': 'nej', 'SD': 'ja'}...}
        
        vote_part_list = self.get_vote_part_list()
        grupp_dict = self.get_grupp_dict()
        outcomes_dict = {}
        for vote_part in vote_part_list:
            id_key = vote_part.get_votering_id() + "_" + vote_part.get_avser() 
            part_outcomes = {}

            for part in grupp_dict.values():
                part_vote_outcome = vote_part.get_part_vote_outcome(part)
                part_outcomes[part] = part_vote_outcome

            outcomes_dict[id_key] = part_outcomes

        assert len(outcomes_dict) == len(vote_part_list)

        return outcomes_dict

    def check_agreement_crit(self, part_one_outcome, part_two_outcome):
        # checks if the two outcomes match and are either "ja" or "nej", i.e. only "ja" or "nej" outcomes count as agreement

        #print("part_one_outcome: " + part_one_outcome)
        #print("part_two_outcome: " + part_two_outcome)                    

        is_true = (part_one_outcome == part_two_outcome) and (part_one_outcome == "ja" or part_one_outcome == "nej")
        #print(is_true)
        return is_true

    def get_agreement_nums_abs(self):
        # returns a dict of dicts with absolute agreement numbers
        outcomes_dict = self.get_outcomes_dict()
        agreement_nums_dict = {}
        # sorry...
        for votering_id in outcomes_dict.keys():
            for part_key in outcomes_dict[votering_id].keys():
                for part_key_other in outcomes_dict[votering_id].keys():
                    part_one_outcome = outcomes_dict[votering_id][part_key]
                    part_two_outcome = outcomes_dict[votering_id][part_key_other]

                    if self.check_agreement_crit(part_one_outcome, part_two_outcome):
                        try:
                            agreement_nums_dict[part_key][part_key_other] += 1
                        except KeyError:
                            try:
                                agreement_nums_dict[part_key][part_key_other] = 1
                            except KeyError:
                                agreement_nums_dict[part_key] = {part_key_other: 1}

        return agreement_nums_dict
                    
    def get_vote_matrix_data(self):
        agreement_nums = self.get_agreement_nums_abs()
        vote_antal = self.get_antal()
        sorted_parts = sorted(agreement_nums.keys())
        #i.e. ['C', 'FP', 'KD', 'M', 'MP', 'S', 'SD', 'V']
        print(sorted_parts)
        vote_matrix_data = []

        for part in sorted_parts:
            for part_other in sorted_parts:
                if part == part_other:
                    vote_matrix_data.append(100)
                else:
                    percent_agreement = round(agreement_nums[part][part_other]/vote_antal*100)
                    vote_matrix_data.append(percent_agreement)

        return vote_matrix_data
                    
            
if __name__ == "__main__":

    url = "http://data.riksdagen.se/voteringlistagrupp/?rm=2014%2F15&bet=&punkt=&grupp1=C&grupp2=FP&grupp3=KD&grupp4=MP&grupp5=M&grupp6=S&grupp7=SD&grupp8=V&utformat=xml"
    url2 = "http://data.riksdagen.se/voteringlistagrupp/?rm=2014%2F15&rm=2013%2F14&bet=&punkt=&grupp1=C&grupp2=FP&utformat=xml"
    url3 = "http://data.riksdagen.se/voteringlistagrupp/?rm=2002%2F03&bet=&punkt=&grupp1=SD&utformat=xml"

    #votepartlist = VotePartList(url)
    votepartlist = VotePartList(url, "UbU")
    print(votepartlist.set_utskott_spec("UbU"))
    #print(votepartlist.get_element())
    #print(votepartlist.get_antal())
    #print(votepartlist.get_riksmote())
    #print(votepartlist.get_grupp_dict())
    #print(votepartlist.get_vote_part_list())
    #for i in votepartlist.get_vote_part_list():
    #    print(i.get_part_vote_outcome("v"))
    #print(votepartlist.get_outcomes_dict())
    #print(votepartlist.get_agreement_nums_abs())
    print(votepartlist.get_vote_matrix_data())

    votepart = VotePart(votepartlist.get_element().find('votering'), votepartlist.get_grupp_dict())

    # print(votepart.get_votering_id())
    # print(votepart.get_forslagspunkt())
    # print(votepart.get_riksmote())
    # print(votepart.get_utskott())
    # print(votepart.get_avser())
    # print(votepart.get_ja_tot())
    # print(votepart.get_nej_tot())
    # print(votepart.get_franv_tot())
    # print(votepart.get_avst_tot())
    # print(votepart.get_part_vote_abs("sd", "ja"))
    # print(votepart.get_part_vote_abs("sd", "nej"))
    # print(votepart.get_part_vote_abs("sd", "frånvarande"))
    # print(votepart.get_part_vote_abs("sd", "avstår"))
    # print(votepart.get_part_vote_outcome("sd"))
