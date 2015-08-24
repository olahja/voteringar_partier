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

    def get_these_parts(self):
        grupp_dict = self.get_grupp_dict()
        these_parts = sorted([x for x in grupp_dict.values() if x in constants.part_abb_list])
        return these_parts 

    
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

    def is_passed_bool(self):
        return self.get_ja_tot() > self.get_nej_tot()

    def get_vote_outcome(self):
        if self.is_passed_bool():
            return "ja"
        else:
            return "nej"

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

    def get_part_vote_outcome_dict(self):
        these_parts = self.get_these_parts()
        part_vote_outcome_dict = {}
        for part in these_parts:
            part_vote_outcome = self.get_part_vote_outcome(part)
            part_vote_outcome_dict[part] = part_vote_outcome

        return part_vote_outcome_dict
        

    def __str__(self):
        newline = "\n"
        
        these_parts = self.get_these_parts()
        votering_id = self.get_votering_id()
        forslagspunkt = self.get_forslagspunkt()
        riksmote = self.get_riksmote()
        utskott = self.get_utskott()
        avser = self.get_avser()
        ja_tot = self.get_ja_tot()
        nej_tot = self.get_nej_tot()
        franv_tot = self.get_franv_tot()
        avst_tot = self.get_avst_tot()
        vote_outcome = self.get_vote_outcome()
        part_vote_outcome_dict = self.get_part_vote_outcome_dict()

        returnstr = "~~~~~~~~~~~~~~~~~~ Votering ~~~~~~~~~~~~~~~~~~ "
        returnstr += newline
        returnstr += "Partier:\t\t"
        for part in these_parts:
            returnstr += part + " "
            
        returnstr += newline
        returnstr += "Votering id:\t\t" + votering_id
        returnstr += newline
        returnstr += "Förslagspunkt:\t\t" + forslagspunkt
        returnstr += newline
        returnstr += "Riksmöte:\t\t" + riksmote
        returnstr += newline
        returnstr += "Utskott:\t\t" + utskott
        returnstr += newline
        returnstr += "Avser:\t\t\t" + avser
        returnstr += newline
        returnstr += "Ja, tot:\t\t" + str(ja_tot)
        returnstr += newline
        returnstr += "Nej, tot:\t\t" + str(nej_tot)
        returnstr += newline
        returnstr += "Frånvarande, tot:\t" + str(franv_tot)
        returnstr += newline
        returnstr += "Avstår, tot:\t\t" + str(avst_tot)
        returnstr += newline
        for part in these_parts:
            returnstr += part + ", röst:\t\t" + part_vote_outcome_dict[part]
            returnstr += newline
        returnstr += "---------------------------"
        returnstr += newline
        returnstr += "Utfall:\t\t\t" + vote_outcome
        returnstr += newline
        returnstr += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ "
        returnstr += newline
        
        return returnstr
