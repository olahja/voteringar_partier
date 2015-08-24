import datetime

def ant_mandat(riksmote):

    riksmote_start = int(riksmote[:4])
    ## 2014-
    if riksmote_start >= 2014:
        ant_mandat = {"s": 113, "m": 84, "sd": 49, "mp": 25, "c": 22, "v": 21, "fp": 19, "kd": 16}

    ## 2010-2014
    elif 2010 <= riksmote_start <= 2013:
        ant_mandat = {"s": 112, "m": 107, "sd": 20, "mp": 25, "c": 23, "v": 19, "fp": 24, "kd": 19}

    ## 2006-2010
    elif 2006 <= riksmote_start <= 2009:
        ant_mandat = {"s": 130, "m": 97, "sd": 0, "mp": 19, "c": 29, "v": 22, "fp": 28, "kd": 24}

    ## 2002-2006
    elif 2002 <= riksmote_start <= 2005:
        ant_mandat = {"s": 144, "m": 55, "sd": 0, "mp": 17, "c": 22, "v": 30, "fp": 48, "kd": 33}

    return ant_mandat

part_abb_bet_gemen = {"s": "Socialdemokraterna",
                      "m": "Moderaterna",
                      "sd": "Sverigedemokraterna",
                      "mp": "Miljöpartiet",
                      "c": "Centerpartiet",
                      "v": "Vänsterpartiet",
                      "fp": "Folkpartiet",
                      "kd": "Kristdemokraterna"}

part_abb_bet_versal = {"S": "Socialdemokraterna",
                      "M": "Moderaterna",
                      "SD": "Sverigedemokraterna",
                      "MP": "Miljöpartiet",
                      "C": "Centerpartiet",
                      "V": "Vänsterpartiet",
                      "FP": "Folkpartiet",
                      "KD": "Kristdemokraterna"}

part_abb_list = ["C", "FP", "KD", "M", "MP", "S", "SD", "V"]

utskott_dict = {"AU": "Arbetsmarknadsutskottet",
                "CU": "Civilutskottet",
                "FiU": "Finansutskottet",
                "FöU": "Försvarsutskottet",
                "JuU": "Justitieutskottet",
                "KU": "Konstitutionsutskottet",
                "KrU": "Kulturutskottet",
                "MJU": "Miljö- och jordbruksutskottet",
                "NU": "Näringsutskottet",
                "SkU": "Skatteutskottet",
                "SfU": "Socialförsäkringsutskottet",
                "SoU": "Socialutskottet",
                "TU": "Trafikutskottet",
                "UbU": "Utbildningsutskottet",
                "UU": "Utrikesutskottet",
                "UFöU": "Sammansatta utrikes- och försvarsutskottet"}

utskott_dict_rev = {v:k for k,v in utskott_dict.items()}

def today_riksmote():
    if datetime.date.today().month <= 9:
        today_year = datetime.date.today().year
    else:
        today_year = datetime.date.today().year + 1
    today_riksmote = str(today_year - 1) + "/" +  str(today_year)[-2:]
    return today_riksmote
