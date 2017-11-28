This folder contains scripts that can:
1) find/predict the position of an optimal point (and its value) from an (incomplete) datafile with n dimensions within user-set bounds (optimise), or 

2) predict the value of a data point specified by the user based on a data set of dimensions and values passed in a datafile (predict).

Datafile should be white-space delimited with n dimensions and the dependent variable as the final column. Rows (ie data) seperated by \n
May contain headers (optionally)- scripts will utilise headers (ie text as first row) to print useful visual results, else will default.


1) optimise:
From cmd, call:
	python prediction_processes/optimise path/to/datafile_name.txt arguments
	optional usage (arguments): 
        i) print to file:
		use 'y' as first argument if the optimisation path is required to be output in a file- useful for visual plotting
       		eg:
            		python optimise_variable data.txt y
        	Note: will save to current working directory.
       
        ii) user-set bounds:
		Append min_x1 max_x1 min_x2 max_x2 ... etc to the arguments to set bounds on the range in which the optimiser will 			search for a solution. 
            	Note:
            		y/n still variable
            		Selecting a bound of 0 will set the corresponding bound to the data bound for interpolation, wherever that may be
        	eg:
            		python optimise_variable data.txt (y/n) 0 100 5 10 ... etc
            		chooses x1 = [data_lower_bound, 100], x2 = [5,10] ... etc
        	Notes: 
            		Can specify as few or many bounds as user requires- all missing bounds after the last passed argument will 				default to the data-set bounds, else use 0.
		        lb = ub implies a fixed variable.

2) predict:
From cmd, call:
	python prediction_processes/optimise path/to/datafile_name.txt dimensions
	
	Where dimensions is the point to be queried.
	The order of the dimensions provided on the command line must match the order in which they appear on the file input 'data.txt')
	dimensions are delimited by white space on the command line.
