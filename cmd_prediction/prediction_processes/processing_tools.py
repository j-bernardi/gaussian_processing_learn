'''
Created on 4 Jul 2017

@author: james
'''
from __future__ import print_function
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import (RBF, WhiteKernel)
import multiprocessing
from multiprocessing import Pool
import warnings
warnings.filterwarnings("error")

def load_data(input_filename):    
    
    """Takes the file input (in form specified above) and outputs an array ofthe names of the dimensions (names), dimensions (X), associated dep variable (Y)
    Where file is of form:
    name1 name2 ... name_dep_var (optional titles)
    x1 x2 ... dep_var (data rows)
    ...etc
    """
    
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
    print('Loaded '+str(len(Y))+' datapoints from '+ input_filename)
    
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
    """predicts the value of the dependent variable given a user input point"""
    dimensions_n = len(names) - 1
    print('Predicting ' + names[dimensions_n] +' with ...')
    for n in range(dimensions_n) :
        print ('   ',names[n], argument_list[n])

    gp = learn_data_set(X, Y)

    dep_var,var = gp.predict(np.array(argument_list).reshape(1,-1),return_std=True)
    sigma = 1.96*np.sqrt(var)
    
    print(names[dimensions_n] +' = '+str(dep_var[0])+ ' width of 95% confidence gaussian is '+str(sigma[0])+ '\n')

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


def get_bounds(X) :
    """Finds the min and max data points in an array of data, and returns a list of (min, max) tuples in the order of the data"""
    bounds = []
    for j in range(len(X[0,:])) :
        bounds.append( ( min(X[:,j]) , max(X[:,j]) ) )
    return bounds

def print_bounds(names, user_bounds, data_bounds):
    """Takes the names of the variables, the user-set bounds, and the data-set bounds and prints, while comparing to identify any extrapolation warnings"""
    #display working bounds to user and warn if they have selected any outside data set
    print ("\nWorking within bounds:")
    outside_range_flag = False
    
    for i in range(len(names)-1) :
        #print the name followed by the bound
        if user_bounds[i][0] == user_bounds[i][1] :
            print (names[i], ': ', str(user_bounds[i][0]))
        else :
            print (names[i], ': ', str(user_bounds[i]))
    
    #warnings
    for i in range (len(names) - 1) :    
        if data_bounds[i][0] > user_bounds[i][0] :
            print ("Warning: lower bound is outside data set- %s results below %s will be extrapolated" % (names[i], data_bounds[i][0]) )
            outside_range_flag = True
        if data_bounds[i][1] < user_bounds[i][1] :
            print ("Warning: upper bound is outside data set- %s results above %s will be extrapolated." % (names[i], data_bounds[i][1]) )
            outside_range_flag = True
    
    if outside_range_flag :
        print ("Results falling outside of data range marked with a '*' below")

def output_names(output_filename, names) :
    """appends the list 'names' as comma delimited headers to the working directory in a file called output_filename"""
    f = open(str(output_filename), "w")
    dimensions_n = len(names) -1
    for i in range(dimensions_n+1) :
        if i == dimensions_n :
            f.write(names[i])
        else :
            f.write(names[i] + ','), 
    f.write('\n')
    f.close()

"""This function would benefit from a more sophisticated gaussian-process to deduce the length_scale properly"""
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

""""Some lines throw errors during the jackknifing scripts, in specific data. More work is to be done to determine the cause of its failure"""

def total_jackknife(X, Y):
    """finds the average distance between simulation results and fit (O(n)*O(predict_value))"""
    print('Now predicting average difference between simulation results and the fit (jackknife)...')
    #for items in array len, remove item from array
    diff_list=[]
    error_count = 0
    cnt = 0
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
            print (str(row_counter+1) + '/' + str(len(Y)) +' predicted='+str(predicted_value) +' actual='+str(actual_value)+ ' diff='+str( predicted_value - actual_value ), end ='\r')
            cnt += 1
        except:
            error_count += 1
            error_rows.append(row_counter +1)
        
    average_diff = float(sum(diff_list))/len(diff_list)
    print('\n\nAverage difference between predictions and data = '+str(average_diff ))
    print (str(cnt) + ' data points used')
    if error_count != 0 :
        print (str(error_count) + ' data points were ignored, as they threw errors.')
        print ('These row numbers threw errors:')
        print (error_rows)
    else :
        print ('No data points threw errors')
        
    return average_diff 

def jackknife_threaded(X, Y):
    """finds the average distance between simulation results and fit (O(n)*O(predict_value))"""
    
    print('Now predicting average difference between simulation results and the fit (jackknife)...')
    
    #initialise a pool of workers
    p = Pool(multiprocessing.cpu_count())
    
    error_count = 0
    error_rows =[]
    diff_list = []
    
    #generate list to iterate over, including the index of that pair (used later)
    X_Y_index_x_y = []
    for k in range(len(Y)) :
        #delete the point being considered
        newX=np.delete(X, k, axis=0)
        newY=np.delete(Y, k, axis=0)
        #specify the point being considered, useful when finding difference later
        x = X[k]
        y = Y[k]
        X_Y_index_x_y.append((newX, newY, k, x, y))
    
    #form [(diff_value, error)]
    results = p.map(jackknife_single, X_Y_index_x_y)
    
    for k in range(len(Y)):
        
        diff_value, error = results[k][0], results[k][1]
        #Handle error- add if no errors
        if (error) :
            error_count += 1
            error_rows.append(k+1)
        else :
            diff_list.append(diff_value)
    
    
    #handle result
    average_diff = float(sum(diff_list))/len(diff_list)
    #Print value for user
    print('\n\naverage difference between predictions and data = '+str(average_diff ))
    print ('\n' + str(len(Y)-error_count) + ' data points used')
    
    #Print error information
    if error_count != 0 :
        print (str(error_count) + ' data points were ignored, as they threw an error.')
        print ('These row numbers threw errors:')
        print (error_rows)
    else :
        print ('No data points threw errors')
    
    return average_diff 

def jackknife_single(X_Y_index_x_y) :
    """Jackknifes a single element given a newX, newY, index tuple (as above)- introduced to allow multithreading
    Outputs a list of tuples corresponding to each pair: [(diff_value, error), ... ]"""
    X, Y, index, x, y = X_Y_index_x_y[0], X_Y_index_x_y[1], X_Y_index_x_y[2], X_Y_index_x_y[3], X_Y_index_x_y[4]
    total = str(len(Y))
    diff_value = 0
    #signals no error 
    error = False
    
    try:
        gp = learn_data_set(X, Y)
        predicted_value=gp.predict(np.array(x).reshape(1,-1))
        actual_value = y
        diff_value = (abs(predicted_value-actual_value))
        #overwrite each line- check functionality!
        print (str(index+1) + '/'  + total + ' completed', end ='\r')
    except:
        #signals error
        error = True
    
    return (diff_value, error)
