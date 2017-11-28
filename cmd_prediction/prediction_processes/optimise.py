"""
USAGE:
    
    Input- data file with n dimensions, either with the first row as titles or just numbers. The script will optimise the dependent variable
    with respect to variable bounds optionally specified by the user. 
    eg:
        python optimise_variable data.txt
    where data has form:
        x1 x2 x3 ... dependent (optional titles as characters)
        val1 val2 val3 ... dep_val
        val1 val2 val3 ... dep_val
        etc...
    
    optional usage: 
        1) print to file:
            append 'y' to arguments if the optimisation path is required to be output in a file- useful for visual plotting
        eg:
            python optimise_variable data.txt y
        Note: will print to current working directory- eg useful for transcribing outputs to an output directory
        
        2) user-set bounds:
            -Append min_x1 max_x1 min_x2 max_x2 ... etc to the arguments to set bounds on the range in which the optimiser will search for a solution. 
            -Note:
            - y/n still variable
            - selecting a bound of 0 will set the corresponding bound to the data bound for interpolation, wherever that may be
        eg:
            python optimise_variable data.txt (y/n) 0 100 5 10 ... etc
            - chooses x1 = [data_lower_bound, 100], x2 = [5,10] ... etc
        Notes: 
            Can specify as few or many bounds as user requires- all missing bounds will default to the data-set bounds
            lb = ub implies a fixed variable.
        
"""

import processing_tools as pt
import sys
from scipy.optimize import differential_evolution
import numpy as np

def set_bounds(original_bounds) :
    """reads in the arguments given in format on top-descriptor and replaces the bounds in the argument with those specified by the user.
    Note: if there are less bounds specified than the amount of bounds required, will default to data-bounds (ie argument given)"""
    
    cnt = 0
    in_range = True
    bounds = original_bounds[:]
    
    #find the starting index of the argument
    try :
        if sys.argv[2].lower() == 'y' or sys.argv[2].lower() == 'n' :
            n = 3
        else :
            n = 2
    except :
        in_range = False
        
    #try to replace until out of sys.argv bounds    
    while( in_range ) :
        try :
            bounds[cnt] = (float(sys.argv[n]), float(sys.argv[n+1]))
            cnt+=1
            n+=2
        except :
            #see if n is in-range (but n+1 is not)
            try :
                bounds[cnt] = (float(sys.argv[n]), float(bounds[cnt][1]))
                in_range = False
            except:
                in_range = False
    #iterate through and check if any bounds are 0- if so, set to original bounds
    for i in range(len(bounds)) :
        if bounds[i][0] == 0 and bounds[i][1] == 0:
            bounds[i] = original_bounds[i]
        elif bounds[i][0] == 0 :
            bounds[i] = (original_bounds[i][0], bounds[i][1])
        elif bounds[i][1] == 0 : 
            bounds[i] = (bounds[i][0], original_bounds[i][1])
    
    return bounds  

def predict_inverse_value_print(argument_list):
    """predicts the 1/ the value of the dependent variable for the minimisation later. Also gets the value of the variance."""
    
    global variance
    global fixed_vars
    
    #check if a var is fixed (ie at a non-zero value)
    for k in range(len(fixed_vars)) :
        if fixed_vars[k] == 0 :
            pass
        else :
            #fix the variable
            argument_list[k] = fixed_vars[k]
            
    val, variance = gp.predict(np.array(argument_list).reshape(1,-1), return_std = True)
    
    output_filename = pt.get_output_name(sys.argv[1])
    
    
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
    
    for k in range(len(fixed_vars)) :
        if fixed_vars[k] == 0 :
            pass
        else :
            argument_list[k] = fixed_vars[k]
            
    val, variance = gp.predict(np.array(argument_list).reshape(1,-1), return_std = True)
    
    if val[0] < 0:
        val[0] = 0.01

    return 1/val[0]

if __name__ == "__main__" :

    if len(sys.argv) < 2 :
        print 'At least one argument (data-file name to optimise based on data provided) is required.\nArguments after that specify bounds on the dimensions, separated by whitespace.'

	print 'Please open document to see full usage.'
	
    
    else : 
        #initialise the variables from the datafile to read in number of dimensions
        try :
            plotting_data_required = False #default
            output_filename = pt.get_output_name(sys.argv[1])
            names, X,Y = pt.load_data(sys.argv[1])
            dimensions_n = len(names) - 1
            data_bounds = pt.get_bounds(X)
            user_bounds = data_bounds[:]
        except :
            print "\nPlease ensure you have passed a valid data file as the first argument (see documentation in-file).\n"
        
        #now check for too many arguments- depending on dimensions read above    
        if len(sys.argv) == 2 :
            #arguments are in range, and no flag is passed
            pass
        
        elif (len(sys.argv) > dimensions_n*2 + 3) or (sys.argv[2].lower() != 'y' and sys.argv[2].lower() != 'n' and len(sys.argv) > dimensions_n*2 + 2) :
            #always too many args in first case, else too many if no y/n passed
            print "\nPlease input a file name, (optionally) followed by y or n for plotting data required, finally followed by optional user-set bounds eg : "
            print "python optimise_variable data.txt y lb1 ub1 lb2 ub2... "
            print 'or python optimise_variable data.txt lb1'
            print 'etc...' 
            print 'Ensuring the number of bounds passed <= to the number of dimensions'
            
        else:
        #Valid number of arguments- now check if printing flag was passed 
            if not sys.argv[2].isdigit() :
                if sys.argv[2] == "y" :
                    plotting_data_required = True
                elif sys.argv[2] == "n" :
                    pass
                else : 
                    print "\nPlease only input y or n as your printing flag, or ensure your first lower bound is a number."
                    print "Defaulting to assume second argument indicated printing not required."
        
        #On to main functionality now all has been checked
        
        #Set bounds
        user_bounds = set_bounds(data_bounds)
        
        #print the bounds for the user
        pt.print_bounds(names, user_bounds, data_bounds)
        
        """allows the user to fix one variable- ie checks if lb=ub, and if so flags it in this list. Else list item is 0."""
        fixed_vars = []
        for k in range(len(user_bounds)) :
            if user_bounds[k][0] == user_bounds[k][1] :
                fixed_vars.append(user_bounds[k][0])
                #less than tolerance- so that optimisation doesn't flag error
                user_bounds[k] = (user_bounds[k][0]- 0.00001, user_bounds[k][1]+0.00001)
            else :
                fixed_vars.append(0)
                
        #learn data to get the graph, bounds to keep within interpolation only
        gp=pt.learn_data_set(X,Y)   
        
        #initialise the datafile
        if plotting_data_required :
            pt.output_names(output_filename, names)
            
        #optimise within the bounds (this step also prints to file if required)
        variance = 0
        if plotting_data_required :
            result = differential_evolution(predict_inverse_value_print, user_bounds, tol=0.0001)
        else :
            result =  differential_evolution(predict_inverse_value, user_bounds, tol=0.0001)
        sigma = 1.96*np.sqrt(variance)
        
        print '\nfinal:'
        for k in range(dimensions_n) :
            tag = ""
            if result.x[k] > data_bounds[k][1] or result.x[k] < data_bounds[k][0] :
                tag = "*"
            print tag + names[k] + ' ' + str(result.x[k])  
                   
        print '\noptimal value of ' + names[dimensions_n] + '\t' + str(1/result.fun)
        print 'With a 95% confidence level of: ' + str(sigma[0])
        
        if plotting_data_required :
            print '\ndata has been saved to file:'
            print output_filename
            print 'in the current working directory'
