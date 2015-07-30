import xml.etree.ElementTree as ET
import re
import constants

class VotePart(object):
    
    def __init__(self, element, grupp_dict):
        self.element = element
        self.grupp_dict = grupp_dict

    def get_element(self):
        return self.element

    def get_grupp_dict(self):
        # {"Grupp1": "C"}
        return self.grupp_dict

    def get_grupp_dict_reverse(self):
        # {"Grupp1": "C"}  => {"C": "Grupp1"}
        grupp_dict = self.get_grupp_dict()
        grupp_dict_reverse = {v: k for k, v in grupp_dict.items()}
        return grupp_dict_reverse

    def element_extractor(self, tag):
        # runner for methods below
        assert type(tag) == str
        element = self.get_element()
        extracted_elem = element.find(tag).text
        return extracted_elem

#### METADATA ####

    def get_votering_id(self):
        return self.element_extractor("votering_id")

    def get_forslagspunkt(self):
        return self.element_extractor("forslagspunkt")

    def get_riksmote(self):
        forslagspunkt = self.get_forslagspunkt()
        riksmote = re.search("\d{4}/\d{2}", forslagspunkt).group()
        return riksmote
    
    def get_utskott(self):
        forslagspunkt = self.get_forslagspunkt()
        utskott = re.search("[A-Za-zÅÄÖåäö]+", forslagspunkt).group()
        return utskott

    def get_avser(self):
        return self.element_extractor("avser")

#### TOTALS ####

    def get_ja_tot(self):
        return int(self.element_extractor("Ja"))

    def get_nej_tot(self):
        return int(self.element_extractor("Nej"))

    def get_franv_tot(self):
        return int(self.element_extractor("Frånvarande"))

    def get_avst_tot(self):
        return int(self.element_extractor("Avstår"))

    def get_part_vote_abs(self, part, vote):
        # takes the party (part) and type of vote outcome and return the absolute number of votes on the perticular vote outcome
        
        assert type(part) == str
        assert type(vote) == str
        vote = vote.lower()
        # assert proper type of vote outcome
        assert vote == "ja" or vote == "nej" or vote == "frånvarande" or vote == "avstår"
        # capitalizes first letter
        vote = vote[0].upper() + vote[1:]
        part = part.upper()
        element = self.get_element()
        
        # takes a reverse dict => {"C": "Grupp1"}
        grupp_dict = self.get_grupp_dict_reverse()
        this_grupp = grupp_dict[part]
        tag = this_grupp + "-" + vote
        extracted_vote = int(element.find(tag).text)
        return extracted_vote
    
#### OUTCOMES ####

    def is_passed(self):
        return self.get_ja_tot() > self.get_nej_tot()

    def check_vote_crit(self, num_votes, ant_mandat_part):
        threshold = 0.51
        return num_votes/ant_mandat_part >= threshold
    
    def get_part_vote_outcome(self, part):
        # returns the vote outcome of a party. the criteria of a perticular outcome is that 51% or more of the total number of party ledamöter must support the outcome
        part = part.lower()
        ant_mandat_dict = constants.ant_mandat(self.get_riksmote())
        ant_mandat_part = ant_mandat_dict[part]
        if ant_mandat_part == 0:
            return None
        part_vote_ja = self.get_part_vote_abs(part, "ja")
        part_vote_nej = self.get_part_vote_abs(part, "nej")
        part_vote_franv = self.get_part_vote_abs(part, "frånvarande")
        part_vote_avst = self.get_part_vote_abs(part, "avstår")
        
        if self.check_vote_crit(part_vote_ja, ant_mandat_part):
            part_vote_outcome = "ja"
        elif self.check_vote_crit(part_vote_nej, ant_mandat_part):
            part_vote_outcome = "nej"
        elif self.check_vote_crit(part_vote_franv, ant_mandat_part):
            part_vote_outcome = "frånvarande"
        elif self.check_vote_crit(part_vote_avst, ant_mandat_part):
            part_vote_outcome = "avstår"
        else:
            # if none of the voteing outcomes got support over the threshold (i.e. 51%) the outcome is inconclusive
            part_vote_outcome = "inconclusive"

        return part_vote_outcome
