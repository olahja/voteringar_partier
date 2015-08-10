import datetime
import constants
import os

def gg_save_str(partier, riksmote, utskott):
    if utskott != None:
        utskott_str = "_".join(utskott)
    riksmote_str = "_".join(riksmote).replace("/", "-")
    if partier == constants.part_abb_list:
        partier_str = "alla-partier"
    else:
        partier_str = "_".join(partier)
    date_str = str(datetime.date.today())
    if utskott != None:
        gg_save_str = 'ggsave(filename = "output/matrices/matrix_-_{0}_-_rm-{1}_-_{2}_-_{3}.png", plot = last_plot())\n'.format(utskott_str, riksmote_str, partier_str, date_str)
    else:
        gg_save_str = 'ggsave(filename = "output/matrices/matrix_-_alla-utskott_-_rm-{0}_-_{1}_-_{2}.png", plot = last_plot())\n'.format(riksmote_str, partier_str, date_str)

    return gg_save_str

#### MATRIX INPUT STRINGS ####
    
def create_plot():
    plot_str = 'ggplot(vot_dat_matrix, aes(X2, X1, fill = value)) + geom_tile() + geom_text(aes(X2, X1, label = value), angle = 90, color = "#fdf6e3", size = 4) + scale_fill_gradient(name=expression("Samstämmighet"), low = "#91cfde", high = "#134582", na.value="#e5e5e5", breaks=seq(0, 100, by = 25), limits = c(0, 100)) + labs(x = "", y = "") + guides(fill=FALSE) + theme_bw() + theme(axis.text.x = element_text(angle = 90, vjust = 1, hjust = 1), axis.text.y = element_text(angle = 90, hjust = 0.5), panel.grid.major = element_blank(), panel.border = element_blank(), panel.background = element_blank(), axis.ticks = element_blank())\n\n'

    return plot_str


def set_theme(theme=None):
    if theme == None:
        set_theme_str = "theme_set(theme_solarized())\n\n"
    else:
        set_theme_str = "theme_set({0})\n\n".format(theme)
        
    return set_theme_str

def reshape_matrix():
    reshape_matrix_str = "vot_dat_matrix <- melt(vot_matrix)\nvot_dat_matrix <- data.frame(vot_dat_matrix)\n\n"
    return reshape_matrix_str

def init_libraries():
    init_libraries_str = "library(ggplot2)\nlibrary(ggthemes)\nlibrary(reshape)\n\n"
    return init_libraries_str

def na_middle_values(num_part):
    na_middle_values_str = ""
    for i in range(num_part):
        na_middle_values_str += "vot_matrix[{0},{0}] <- NA\n".format(i+1)
    na_middle_values_str += "\n"
    return na_middle_values_str

def fix_sd_sorting(labels_string):
    # adds "VSD" for sorting purposes
    labels_string = labels_string.replace("SD", "VSD")
    return labels_string
    
def create_r_labels(partier):
    #print(partier)
    labels_string = 'dimnames(vot_matrix) = list(c({0}),c({0}))\n\n'.format(', '.join(['"{0}"'.format(x) for x in partier]))
    labels_string = fix_sd_sorting(labels_string)
    return labels_string


def create_r_matrix(num_part, matrix_data):
    matrix_data_str = ", ".join([str(x) for x in matrix_data])
    #print("matrix_data_str: ", matrix_data_str)
    r_matrix_str = "vot_matrix = matrix (c({0}),nrow={1},ncol={1},byrow = TRUE)\n\n".format(matrix_data_str, num_part)
    
    return r_matrix_str
    

def get_r_input_str(partier, riksmote, utskott, matrix_data):
    num_part = len(partier)
    r_matrix_str = create_r_matrix(num_part, matrix_data)
    r_labels = create_r_labels(partier)
    na_middle_values_str = na_middle_values(num_part)
    init_libraries_str = init_libraries()
    reshape_matrix_str = reshape_matrix()
    set_theme_str = set_theme()
    plot_str = create_plot()
    save_str = gg_save_str(partier, riksmote, utskott)
    
    write_string = r_matrix_str + r_labels + na_middle_values_str + init_libraries_str + reshape_matrix_str + set_theme_str + plot_str + save_str

    return write_string

#### //MATRIX INPUT STRING ####

def r_write_input_file(partier, riksmote, utskott, matrix_data):
    r_input_str = get_r_input_str(partier, riksmote, utskott, matrix_data)
    r_input_file = open('.r_input_file', 'w')
    r_input_file.write(r_input_str)

def r_execute_input_file(partier, riksmote, utskott, matrix_data):
    r_write_input_file(partier, riksmote, utskott, matrix_data)
    os.system("R < .r_input_file --no-save")




if __name__ == '__main__':
    pass
    #partier = ["C", "FP", "KD", "M", "MP", "S", "SD", "V"]
    #matrix_data = [100, 86, 91, 88, 65, 65, 25, 42, 86, 100, 88, 86, 64, 64, 27, 43, 91, 88, 100, 91, 69, 69, 28, 45, 88, 86, 91, 100, 67, 67, 28, 42, 65, 64, 69, 67, 100, 100, 38, 69, 65, 64, 69, 67, 100, 100, 38, 69, 25, 27, 28, 28, 38, 38, 100, 22, 42, 43, 45, 42, 69, 69, 22, 100]
    #utskott = ["UbU", "FöU"]
    #riksmote = ["2014/15"]
    #utskott = None
    #print(get_r_input_str(partier, riksmote, utskott, matrix_data))
    #r_write_input_file(partier, riksmote, utskott, matrix_data)
    #r_execute_input_file(partier, riksmote, utskott, matrix_data)
