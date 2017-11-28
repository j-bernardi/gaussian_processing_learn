"""
Usage:
    Dependent variable prediction software using gaussian_processing to interpolate data from an input text document
    A script that takes an input dataset, learns that dataset, then provides a prediction depending on input query point

    command line input:
        python predict data.txt dimensions 
        (dimension input delimited by: " ")
    The order of the dimensions provided on the command line must match the order in which they appear on the file input 'data.txt') 

    EG:
        python predict data.txt 50 70 100
        Queries point 50, 70, 100 for a value after learning the (4-column) data-set in data.txt

Eg: requires file input as:
    (optional headers as strings) row 1: title1 title2 title3  .... dependent_variable_title 
    ('dependent_variable' header must appear last)

    row 2: value1 value2 value3 .... dependent_value - as values
    row 3: value1 value2 value3 .... dependent_value 
    etc ..

***************************
*Created by James Bernardi*
***************************

"""
import processing_tools as pt
import sys 


if __name__ == "__main__":
    
    #check if arguments have been provided correctly
    if len(sys.argv)<=2:
        print("Please run this code with the file name as an arguement and with the input dimensions following that, eg:")    
        print('python predict.py data.txt query-point-dimensions[delimited by " "]')
        print('Note units are best provided close to O(1)')
        print('for example ...')
        print('python predict.py 4_column_data.txt 70 55 100')
        
    else :
        
        filename = sys.argv[1]
        names, X, Y = pt.load_data(filename)     
        dimensions_n = len(names) - 1
        #check the correct number of dimensions have been provided given the file
        if (len(sys.argv) -2) != dimensions_n :
            print ('Please ensure your number of input dimensions matches the number of columns in your data set.')
            print ('Your number of dimensions passed on the command line : %s. Your number of dimensions passed in the file: %s') % (len(sys.argv) -2, dimensions_n)
        else :
            #exeute the prediction
            argument_list=sys.argv[2:]
            argument_list=[float(i) for i in argument_list]
            
            pt.predict_value(argument_list, names, X, Y) 
            #check if the user has time to run the J-K script
            run_script = raw_input("Do you want to run the jackknifing script? (y/n) \n")
            if run_script.lower() == 'y' :
                threading = raw_input("Do you want to use threading? (y/n) \n")
                if threading.lower() =='y' :
                    pt.jackknife_threaded(X, Y)
                else :
                    pt.total_jackknife(X,Y)
                
            else :
                pass
