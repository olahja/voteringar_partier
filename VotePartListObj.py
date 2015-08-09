import requests
import xml.etree.ElementTree as ET
import re
from VotePartObj import VotePart
import constants
import input_hygiene


class VotePartList(object):

    def __init__(self, url, utskott_spec=None):
        self.url = url
        if utskott_spec != None:
            self.utskott_spec = self.set_utskott_spec(utskott_spec)
        else:
            self.utskott_spec = None
        self.html = self.set_html()
        self.element = self.set_element()
        # self.antal MUST be before self.vote_part_list
        self.antal = self.set_antal()
        self.vote_part_list = self.set_vote_part_list()

        
    def get_url(self):
        return self.url

    def set_utskott_spec(self, utskott_spec):
        utskott_spec_list = input_hygiene.check_utskott(utskott_spec)
        return utskott_spec_list
    
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
        element = ET.fromstring(html)
        return element

    def get_element(self):
        return self.element

#### METADATA ####
    
    def set_antal(self):
        element = self.get_element()
        antal = int(element.attrib['antal'])
        return antal

    def get_antal(self):
        return self.antal
        
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

    def get_these_parts(self):
        grupp_dict = self.get_grupp_dict()
        these_parts = sorted([x for x in grupp_dict.values() if x in constants.part_abb_list])
        return these_parts 

        
    
    def set_vote_part_list(self):
        
        utskott_spec = self.get_utskott_spec()
        element = self.get_element()
        vote_part_list = []
        grupp_dict = self.get_grupp_dict()
        for votering in element.findall('votering'):
            this_votepart = VotePart(votering, grupp_dict)
            # checks if a utskott has been specified, and if so only adds those voteparts that match the specified utskott
            if utskott_spec != None:
                if this_votepart.get_utskott() in utskott_spec:
                    vote_part_list.append(this_votepart)
            else:
                vote_part_list.append(this_votepart)
        self.antal = len(vote_part_list)
        return vote_part_list

    def get_vote_part_list(self):
        return self.vote_part_list

    def get_vote_franvaro_dict(self):
        vote_part_list = self.get_vote_part_list()
        vote_franvaro_dict = {}
        these_partier = self.get_these_parts()
        
        for vote_part in vote_part_list:
            for part in these_partier:
                try:
                    absence_percent = vote_part.get_part_vote_abs(part, "frånvarande")/constants.ant_mandat(vote_part.get_riksmote())[part.lower()]
                    vote_franvaro_dict[part].append(absence_percent)
                except KeyError:
                    # creates a list with attendence percent values for each vote_part
                    vote_franvaro_dict[part] = [absence_percent]
        # find the mean of each list of attendence percentages in the dict
        vote_franvaro_dict = {k: sum(v)/len(v) for k,v in vote_franvaro_dict.items()}
        
        return vote_franvaro_dict
        
    
    def get_outcomes_dict(self):
        ## e.g. {'C3DSGH542FGFID-SDF42SDG-TUJHGF4DH_sakfrågan': {'V': 'nej', 'SD': 'ja'}...}
        
        vote_part_list = self.get_vote_part_list()
        grupp_dict = self.get_grupp_dict()
        these_partier = self.get_these_parts()
        outcomes_dict = {}
        for vote_part in vote_part_list:
            id_key = vote_part.get_votering_id() + "_" + vote_part.get_avser() 
            part_outcomes = {}

            for part in these_partier:
                part_vote_outcome = vote_part.get_part_vote_outcome(part)
                part_outcomes[part] = part_vote_outcome

            outcomes_dict[id_key] = part_outcomes

        assert len(outcomes_dict) == len(vote_part_list)

        return outcomes_dict

    def check_agreement_crit(self, part_one_outcome, part_two_outcome):
        # choose between them! (old depricated version (second) used "ja", "nej" and "asvtår"
        
        # checks if the two outcomes match and are either "ja" or "nej", i.e. only "ja" or "nej" outcomes count as agreement
        #is_true = (part_one_outcome == part_two_outcome) and (part_one_outcome == "ja" or part_one_outcome == "nej")
        
        # checks if the two outcomes match and are either "ja" or "nej" or "avstår", i.e.  "ja" or "nej" or "avstår" outcomes count as agreement
        is_true = (part_one_outcome == part_two_outcome) and (part_one_outcome == "ja" or part_one_outcome == "nej" or part_one_outcome == "avstår")
        
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
        print("Num voteringar:", vote_antal)
        sorted_parts = sorted(agreement_nums.keys())
        #i.e. ['C', 'FP', 'KD', 'M', 'MP', 'S', 'SD', 'V']
        vote_matrix_data = []

        for part in sorted_parts:
            for part_other in sorted_parts:
                if part == part_other:
                    vote_matrix_data.append(100)
                else:
                    percent_agreement = round(agreement_nums[part][part_other]/vote_antal*100)
                    vote_matrix_data.append(percent_agreement)

        return vote_matrix_data

        

    def get_win_loss_ratio(self):
        # andelen av det totala antalet voteringar där THESE PARTS röstar likadant som utfallet av omröstningen (dvs "vinner")
        # proportion of the total voteringar where THESE PARTS vote the same as the outcome (i.e. "wins") --> S = "ja", MP = "ja", outcome = "ja" --> TRUE
        vote_part_list = self.get_vote_part_list()
        these_parts = self.get_these_parts()
        antal = self.get_antal()
        win_count = 0
        for vote_part in vote_part_list:
            vote_outcome = vote_part.get_vote_outcome()
            for part in these_parts:
                part_vote = vote_part.get_part_vote_outcome(part)
                criteria = True
                if part_vote != vote_outcome:
                    criteria = False
                    break

            if criteria:
                win_count += 1

        win_ratio = win_count/antal
        return win_ratio


    def get_loss_vote_part_list(self):
        vote_part_list = self.get_vote_part_list()
        these_parts = self.get_these_parts()
        antal = self.get_antal()
        loss_list = []

        # for vote_part in vote_part_list:
        #     vote_outcome = vote_part.get_vote_outcome()
        #     for part in these_parts:
        #         part_vote = vote_part.get_part_vote_outcome(part)
        #         consensus = True
        #         if part_vote != vote_outcome:
        #             consensus = False
        #             #print("breaking")
        #             break

        #     if consensus:
        #         loss_list.append(vote_part)

        for vote_part in vote_part_list:
            vote_outcome = vote_part.get_vote_outcome()
            reference_part = these_parts[0]
            reference_part_vote = vote_part.get_part_vote_outcome(reference_part)
            for part in these_parts:
                consensus = True
                part_vote = vote_part.get_part_vote_outcome(part)
                if part_vote != reference_part_vote:
                    consensus = False
                    break

            if consensus and reference_part_vote != vote_outcome:
                loss_list.append(vote_part)
            
        return loss_list

    def loss_list_str(self):

        loss_list_str = ""
        loss_vote_part_list = self.get_loss_vote_part_list()
        vote_losses_num = len(loss_vote_part_list)
        antal_tot = self.get_antal()
        vote_losses_prop = round(vote_losses_num/antal_tot*100, 1)
        for vote_part in loss_vote_part_list:
            loss_list_str += str(vote_part)
            
        loss_list_str += "Antal voteringsförluster: {0} av totalt {1} ({2}%)".format(vote_losses_num, antal_tot, vote_losses_prop)
        
        return loss_list_str

    
if __name__ == "__main__":

    url = "http://data.riksdagen.se/voteringlistagrupp/?rm=2014%2F15&bet=&punkt=&grupp1=C&grupp2=FP&grupp3=KD&grupp4=MP&grupp5=M&grupp6=S&grupp7=SD&grupp8=V&utformat=xml"
    url2 = "http://data.riksdagen.se/voteringlistagrupp/?rm=2014%2F15&rm=2013%2F14&bet=&punkt=&grupp1=C&grupp2=FP&utformat=xml"
    url3 = "http://data.riksdagen.se/voteringlistagrupp/?rm=2002%2F03&bet=&punkt=&grupp1=SD&utformat=xml"
    url4 = "http://data.riksdagen.se/voteringlistagrupp/?rm=2014%2F15&rm=2013%2F14&bet=&punkt=&grupp1=C&grupp2=FP&grupp3=KD&grupp4=MP&grupp5=M&grupp6=S&grupp7=SD&grupp8=V&utformat=xml"
    url4 = "http://data.riksdagen.se/voteringlistagrupp/?rm=2014%2F15&bet=&punkt=&grupp1=S&grupp2=MP&utformat=xml"
    url5 = "http://data.riksdagen.se/voteringlistagrupp/?rm=2014%2F15&bet=&punkt=&grupp1=C&grupp2=FP&grupp3=KD&grupp4=MP&grupp5=M&grupp6=S&grupp7=SD&grupp8=V&utformat=xml" 

    votepartlist = VotePartList(url4)
    #votepartlist = VotePartList(url, ["AU", "CU", "FiU", "FöU", "JuU", "KU", "KrU", "MjU", "NU", "SkU", "SfU", "SoU", "TU", "UbU", "UU", "UFöU"])
    #votepartlist = VotePartList(url, ["Arbetsmarknadsutskottet", "Civilutskottet", "Finansutskottet", "Försvarsutskottet", "Justitieutskottet", "Konstitutionsutskottet", "Kulturutskottet", "Miljö- och jordbruksutskottet", "Näringsutskottet", "Skatteutskottet", "Socialförsäkringsutskottet", "Socialutskottet", "Trafikutskottet", "Utbildningsutskottet", "Utrikesutskottet", "Sammansatta utrikes- och försvarsutskottet"])

    #print(votepartlist.get_utskott_spec())
    #print(votepartlist.get_element())
    #print(votepartlist.get_antal())
    #print(votepartlist.get_riksmote())
    #print(votepartlist.get_grupp_dict())
    #print(votepartlist.get_these_parts())
    #print(votepartlist.get_vote_part_list())
    #print(votepartlist.get_vote_franvaro_dict())
    #for i in votepartlist.get_vote_part_list():
    #    print(i.get_part_vote_outcome("v"))
    #print(votepartlist.get_outcomes_dict())
    #print(votepartlist.get_agreement_nums_abs())
    #print(votepartlist.get_vote_matrix_data())
    #print(votepartlist.get_win_loss_ratio())
    print(votepartlist.loss_list_str())

    votepart = VotePart(votepartlist.get_element().find('votering'), votepartlist.get_grupp_dict())

    #print(votepart)
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
    # print(votepart.get_these_parts())


### TODO ###
# fix local get_these_parties function
