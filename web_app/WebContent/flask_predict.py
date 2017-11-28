from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS, cross_origin
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (RBF, WhiteKernel)
from scipy.optimize import differential_evolution
import scipy, sklearn, xgboost
import json 
import numpy as np
import warnings
warnings.filterwarnings("error")

#NOTE: currently uses path :'file:///home/james/Documents/TBR_predictor/raw_data/'
#perhaps let user specify their own in text, OR use URLS etc..? not sure how to best approach

#TODO: potentially make load_data work with urls (check out urllib2) - think about aws
#Implement the optimisation path output- ie allow user to download the file -in run_optimise and def predict_inverse_value_print
#TODO: make file name adaptive (os.path(__file__) thing)


app = Flask(__name__)
CORS(app)

#global vars:
fixed_vars = []
gp =  GaussianProcessRegressor()
variance = 0

@app.route('/')
@cross_origin()
def hello_world():
    return jsonify(result = "Welcome to the python prediction script. \n<br> \
    \n<br>\
    \n<br>Usage:\
    \n<br>Dependent variable prediction software using gaussian_processing to interpolate data from an input text document\
    \n<br>A script that takes an input dataset, learns that dataset, then provides a prediction depending on input query point\
    \n<br>\
    \n<br>argument input:\
        \n<br>/data.txt/dimensions\
        \n<br>(dimension input delimited by: '/', eg 'x1/x2/x3/x4 ... etc') \
    \n<br>The order of the dimensions provided on the command line must match the order in which they appear on the file input 'data.txt')\
\n<br>\
\n<br>Eg: requires file input as:\
    \n<br>(optional headers as strings) row 1: title1 title2 title3  .... dependent_variable_title\
    \n<br>('dependent_variable' header must appear last)\
\n<br>\
    \n<br>row 2: value1 value2 value3 .... dependent_value - as values\
    \n<br>row 3: value1 value2 value3 .... dependent_value\
    \n<br>etc ..\
    ")

@app.route('/predict/<arguments>')
@cross_origin()
def run_predict(arguments):

    return_string = "placeholder_string- no argument returned from: <br>\n" + arguments
   
    #arg list form : [y/n(jk),filename,arg1,ag2, ... argn]
    arg_list = []
    current_arg = "" 
    for c in arguments :
        if c == "&" :
            arg_list.append(current_arg)
            current_arg = ""
        else :
            current_arg += c
    arg_list.append(current_arg)
    
    dimensions = len(arg_list) - 2;
    
    return_string = "read these as arguments : " + ','.join(arg_list)
    
    filename = 'file:///home/james/Documents/CCFE_project_work/TBR_predictor/raw_data/' + arg_list[1]
    names, X, Y = load_data(filename)     
    #check the correct number of dimensions have been provided given the file
    
    return_string ='<br>\nLoaded '+str(len(Y))+' datapoints from '+ arg_list[1] + '<br>\n<br>\n'
    
    #exeute the prediction
    input_numbers=arg_list[2:]
    input_numbers=[float(i) for i in input_numbers]
            #TODO: change when file upload implemented
    return_string += predict_value(input_numbers, names, X, Y) 
    return_string += '<br> with: ' 
    
    for k in range(len(names) -1) :
        return_string += '<br>' + names[k] + ' = ' + arg_list[k+2]
    
    #check if the user has time to run the J-K script
    if arg_list[0].lower() == 'y' :
        return_string += jackknife(X, Y)
    
    return jsonify(result = return_string)

@app.route('/optimise/<arguments>')
@cross_origin()
def run_optimise(arguments):
    #arg list form : [y/n(print),filename,lb1,ub1, ... lbn,ubn]
    arg_list = []
    current_arg = "" 
    for c in arguments :
        if c == "&" :
            arg_list.append(current_arg)
            current_arg = ""
        else :
            current_arg += c
    arg_list.append(current_arg)
    
    dimensions = (len(arg_list) - 2) /2;
    
    return_string = "read these as arguments : " + ','.join(arg_list)
    
    #file:///home/james/Documents/TBR_predictor/raw_data/60_all_all_Be12Ti_Li2TiO3_TBR.txt
    filename = 'file:///home/james/Documents/CCFE_project_work/TBR_predictor/raw_data/' + arg_list[1]   
    #check the correct number of dimensions have been provided given the file
    
    #initialise the variables from the datafile to read in number of dimensions
    try :
        if arg_list[0].lower() == "y" :
            plotting_data_required = True
        else :
            plotting_data_required = False
        
    
        names, X, Y = load_data(filename)
    
        dimensions_n = len(names) - 1
        data_bounds = get_bounds(X)
        user_bounds = data_bounds[:]
    except :
        return jsonify(result="\n<br>Please ensure you have passed a valid data file as the first argument (see documentation in-file).\n<br>")
    
    #On to main functionality now all has been checked
        
    #Set bounds
    user_bounds = set_bounds(data_bounds, arg_list)
    
    #print the bounds for the user
    return_string = print_bounds(names, user_bounds, data_bounds)
       
    """allows the user to fix one variable- ie checks if lb=ub, and if so flags it in this list. Else list item is 0."""
    global fixed_vars
    global gp
    global variance
    
    fixed_vars = []
    for k in range(len(user_bounds)) :
        if user_bounds[k][0] == user_bounds[k][1] :
            fixed_vars.append(user_bounds[k][0])
            #less than tolerance- so that optimisation doesn't flag error
            user_bounds[k] = (user_bounds[k][0]- 0.00001, user_bounds[k][1]+0.00001)
        else :
            fixed_vars.append(0)
                 
    #learn data to get the graph, bounds to keep within interpolation only
    gp=learn_data_set(X,Y)   
         
    #initialise the datafile*****************************************************
    if plotting_data_required :
        #TODO: PRINT HEADERS TO OUTPUT FILE
        #output_names(output_filename, names)
        pass
        
    #optimise within the bounds (this step also prints to file if required)
    variance = 0
    
    #TODO: make this effective***************************************************
    if plotting_data_required :
        result = differential_evolution(predict_inverse_value_print, user_bounds, tol=0.0001)
    else :
        result =  differential_evolution(predict_inverse_value, user_bounds, tol=0.0001)
    
    sigma = 1.96*np.sqrt(variance)
        
    return_string += '<br>\n<br>\noptimal values:'
    for k in range(dimensions_n) :
        tag = ""
        if result.x[k] > data_bounds[k][1] or result.x[k] < data_bounds[k][0] :
            tag = "*"
        return_string += '<br>\n' + tag + names[k] + ' ' + str(result.x[k])  
        
          
    return_string += '<br>\n<br>\noptimal value of ' + names[dimensions_n] + '    ' + str(1/result.fun)
    
    return_string += '<br>\nWith a 95% confidence level of: ' + str(sigma[0])  
    
    #TODO: make this true *****************************************************
    if plotting_data_required :
        return_string += '<br>\ndata has been saved to file:'
        return_string += '<br>\noptimiser_output_' +  filename
    
    return jsonify(result = return_string)

def print_bounds(names, user_bounds, data_bounds):
    """Takes the names of the variables, the user-set bounds, and the data-set bounds and prints, while comparing to identify any extrapolation warnings"""
    #display working bounds to user and warn if they have selected any outside data set
    output_string = ("\nWorking within bounds:")
    outside_range_flag = False
    
    for i in range(len(names)-1) :
        #print the name followed by the bound
        if user_bounds[i][0] == user_bounds[i][1] :
            output_string += '<br>\n' + names[i] + ': ' + str(user_bounds[i][0])
        else :
            output_string += '<br>\n' + names[i] + ': ' + str(user_bounds[i])
    
    #warnings
    for i in range (len(names) - 1) :    
        if data_bounds[i][0] > user_bounds[i][0] :
            output_string += '<br>\n' +"Warning: lower bound is outside data set- "+ names[i] + " results below "+ data_bounds[i][0] + " will be extrapolated" 
            outside_range_flag = True
        if data_bounds[i][1] < user_bounds[i][1] :
            output_string += '<br>\n' + "Warning: upper bound is outside data set- "+ names[i] + " results above "+ data_bounds[i][1] + " will be extrapolated."
            outside_range_flag = True
    
    if outside_range_flag :
        output_string += '<br>\n' +"Results falling outside of data range marked with a '*' above"

    return output_string

def get_bounds(X) :
    """Finds the min and max data points in an array of data, and returns a list of (min, max) tuples in the order of the data"""
    bounds = []
    for j in range(len(X[0,:])) :
        bounds.append( ( min(X[:,j]) , max(X[:,j]) ) )
    return bounds

def set_bounds(original_bounds,arg_list) :
    """reads in the arguments given in format on top-descriptor and replaces the bounds in the argument with those specified by the user.
    Note: if there are less bounds specified than the amount of bounds required, will default to data-bounds (ie argument given)"""
    #argument pass = print_to_file&filename_in_s3&lb1&ub1&...&lbn&ubn
    cnt = 0
    in_range = True
    bounds = original_bounds[:]
            
    #try to replace until out of sys.argv bounds    
    for i in range(2, len(arg_list),2) :
        try :
            bounds[cnt] = (float(arg_list[i]), float(arg_list[i+1]))
            cnt+=1
        except :
            #see if n is in-range (but n+1 is not)
            try :
                bounds[cnt] = (float(arg_list[i]), float(bounds[cnt][1]))
            except:
                break
    
    #iterate through and check if any bounds are 0- if so, set to original bounds
    for i in range(len(bounds)) :
        if bounds[i][0] == 0 and bounds[i][1] == 0:
            bounds[i] = original_bounds[i]
        elif bounds[i][0] == 0 :
            bounds[i] = (original_bounds[i][0], bounds[i][1])
        elif bounds[i][1] == 0 : 
            bounds[i] = (bounds[i][0], original_bounds[i][1])
    
    return bounds

def get_output_name(input_filename):
    """splits the input directory and filename into an output name for the data file into the working directory"""
    
    j= len(input_filename) - 1
    tag = 'optimiser_output_'
    
    while input_filename[j] != "/"  and j > 0:
        j -= 1
    
    #eg in current working directory
    if j == 0 :
        output_name = tag + input_filename
        
    else:
        directory= input_filename[:j+1]
        filename=input_filename[j+1:]
        output_name = tag + str(filename)
     
    return str(output_name)

def load_data(input_filename):    
    
    """Takes the file input (in form specified above) and outputs an array ofthe names of the dimensions (names), dimensions (X), associated dep variable (Y)
    Where file is of form:
    name1 name2 ... name_dep_var (optional titles)
    x1 x2 ... dep_var (data rows)
    ...etc
    """
    if input_filename.startswith('file://') :
        input_filename = input_filename[7:]
    
    with open( input_filename ) as i_f :    
        
        names_line = i_f.readline()
        first_char = names_line.strip()[0]
        #check whether headers have been provided as strings- ie isdigit if not
        if first_char.isdigit() :
            data = np.loadtxt(input_filename)
            dimensions_n = (len(data[0,:]) - 1)
            #arbitrarily name dimensions
            names = ["x" + str(i) for i in range(1, dimensions_n + 1)]
            names.append("dependent_variable")
        else :   
            
            #skip first row when loading data- these are headers
            data = np.loadtxt(input_filename, skiprows = 1)
            dimensions_n = (len(data[0,:]) - 1)
    
            #Names have been given for dimensions so read these in
            names = [""]
            p = 0
            for c in names_line :
                if c == " " :
                    names.append("")
                    p += 1
                else :
                    names[p] += c

    Y = np.array(data[:,dimensions_n])
    
    if first_char.isdigit():
        x_unpack = np.loadtxt(input_filename, unpack = True, usecols = range(dimensions_n))
    else :
        x_unpack = np.loadtxt(input_filename, unpack = True, skiprows = 1, usecols = range(dimensions_n))
    
    for k in range(dimensions_n+1) :
        names[k] = names[k].strip()
        
    X = np.array(x_unpack).T
    
    #Note the final element in names is the name of the dep var
    return names, X, Y

def predict_value(argument_list, names, X, Y):
    global gp
    """predicts the value of the dependent variable given a user input point"""
    dimensions_n = len(names) - 1
    gp = learn_data_set(X, Y)
    dep_var,var = gp.predict(np.array(argument_list).reshape(1,-1),return_std=True)
    sigma = 1.96*np.sqrt(var)
    return (str(names[dimensions_n]) +' = '+str(dep_var[0])+ ' width of 95% confidence gaussian is '+str(sigma[0])+ '\n')

def learn_data_set(X,Y):    
    """gaussian_processing algorithm that learns the data set provided an array of independent variables with their associated dependent variables"""
    length_scale = find_length_scale(X)
    gp_kernel = RBF(length_scale, length_scale_bounds=(1, 1e5)) + WhiteKernel(noise_level=0.01)
    gp =  GaussianProcessRegressor(kernel=gp_kernel)
    gp.fit(X, Y)
    return gp   

def find_length_scale(X) :
    """take an array, find min, max then relative ratios of each column and normalise to give better estimate of fit"""
    dimensions_n = len(X[0,:])
    #using the first column as the relative value of 1.0
    rel_min = min(X[:,0])
    rel_max = max(X[:,0])
    length_scale = [] 
    
    for j in range(dimensions_n) :
        length_scale.append( (max(X[:,j])-min(X[:, j]))/(rel_max-rel_min) )
    return length_scale    
    
def jackknife(X, Y):
    """finds the average distance between simulation results and fit (O(n)*O(predict_value))"""
    
    output_string = "<br>\n"
    
    #for items in array len, remove item from array
    diff_list=[]
    error_count = 0
    cnt=0
    error_rows =[]
    for row_counter in range(len(Y)):
        newX = np.delete(X,row_counter,axis=0)
        newY = np.delete(Y,row_counter,axis=0)
        try:
            gp=learn_data_set(newX,newY)
            #predicted_value=gp.predict(np.array(X[row_counter]).reshape(1,-1))
            predicted_value=gp.predict(np.array(X[row_counter]).reshape(1,-1))
            actual_value = Y[row_counter]
            diff_list.append(abs(predicted_value-actual_value))
            #overwrite each line- check functionality!
            cnt+=1
        except:
            error_count += 1
            error_rows.append(row_counter +1)
        
    average_diff = float(sum(diff_list))/len(diff_list)
    output_string+='<br>\n<br>\nAverage difference between predictions and data = '+str(average_diff )
    output_string += '<br>\n' + str(cnt) + ' data points used'
    if error_count != 0 :
        output_string+='<br>\n' + (str(error_count) + ' data points were ignored, as they threw errors.')
        output_string += ('<br>\nThese row numbers threw errors:<br>\n')
        for k in range(len(error_rows)) :
            output_string += str(error_rows[k])
            if k !=len(error_rows) -1 :
                output_string += ', '
    else :
        output_string += ('<br>\nNo data points threw errors')
        
    return output_string
        
def predict_inverse_value_print(argument_list):
    """predicts the 1/ the value of the dependent variable for the minimisation later. Also gets the value of the variance."""
    
    global variance
    global fixed_vars
    global gp
    
    #check if a var is fixed (ie at a non-zero value)
    for k in range(len(fixed_vars)) :
        if fixed_vars[k] == 0 :
            pass
        else :
            #fix the variable
            argument_list[k] = fixed_vars[k]
            
    val, variance = gp.predict(np.array(argument_list).reshape(1,-1), return_std = True)
    
    output_filename = get_output_name(argument_list[1])
    
    
        #Write data into an output file delimited by commas
    f = open(output_filename, "a")
    
    for i in range(dimensions_n) :
        f.write('{}'.format(argument_list[i])) 
        f.write(',')
    #final col
    f.write('{}'.format(val[0]) + '\n')
    
    f.close()
    
    if val[0] < 0:
        val[0] = 0.01

    return 1/val[0]

def predict_inverse_value(argument_list):
    """predicts the 1/ the value of the dependent variable for the minimisation later. Also gets the value of the variance."""

    global variance
    global fixed_vars
    global gp 
    
    for k in range(len(fixed_vars)) :
        if fixed_vars[k] == 0 :
            pass
        else :
            argument_list[k] = fixed_vars[k]
            
    val, variance = gp.predict(np.array(argument_list).reshape(1,-1), return_std = True)
    
    if val[0] < 0:
        val[0] = 0.01

    return 1/val[0]

if __name__=='__main__':
    app.run()
