/********* Handle a datafile upload- input parameters to make table **************/

document.getElementById('generate-table-button').onclick = makeTable;

/************* Handle a plot data file upload ********************/

//TODO: Add the optimisation and prediction scripts
// When optimi

//counter for undoing last plot
var numberOfPlots = 0;
document.getElementById('plot-button').onclick = makePlot;

document.getElementById('run-script-button').onclick = runScript;


$("#datafile-input").change(function(){
	document.getElementById("generate-table-button-division").innerHTML = '<button id="generate-table-button" style="margin:8px">Generate Table</button>'
});

var names;
var dimensions;

$("#select-predict").change(function() {
    if( this.checked && document.getElementById("select-optimise").checked){
    	document.getElementById("select-optimise").checked = false;
    	document.getElementById('script-options-button-division').innerHTML = 'Jackknife? (Predict only) <input id="jackknife-checkbox" type="checkbox">'
    }
    else if(this.checked){
    	document.getElementById('script-options-button-division').innerHTML = 'Jackknife? (Predict only) <input id="jackknife-checkbox" type="checkbox">'
    	document.getElementById("datafile-input-division").innerHTML = 
    		'<p>File: (hover should give input type) <input id="datafile-input" type="file" style="width:100%;margin:8px" name="datafile-input"> </p>'
    }
    else {
    	document.getElementById('script-options-button-division').innerHTML = 'Please select a script above';
    	document.getElementById("generate-table-button-division").innerHTML = ' ';
    	document.getElementById("datafile-input-division").innerHTML = ' ';
    }
}) 

$("#select-optimise").change(function() {
    if( this.checked && document.getElementById("select-predict").checked){
    	document.getElementById("select-predict").checked = false;
    	document.getElementById('script-options-button-division').innerHTML = 'Plotting data required? (hover for more info) <input id="plotting-data-checkbox" type="checkbox">'
    }
    else if(this.checked){
    	document.getElementById('script-options-button-division').innerHTML = 'Output optimisation path to file? (Optimise only) <input id="optimise-output-checkbox" type="checkbox">'
    	document.getElementById("datafile-input-division").innerHTML = 
       		'<p>File: (hover should give input type) <input id="datafile-input" type="file" style="width:100%;margin:8px" name="datafile-input"> </p>'
    }
    else {
    	document.getElementById('script-options-button-division').innerHTML = 'Please select a script above';
    	document.getElementById("generate-table-button-division").innerHTML = ' '
    	document.getElementById("datafile-input-division").innerHTML = ' ';
    }
})


function runScript(){
	
	console.log('running script')
	//upload the file passed in get to the s3 getElementById("datafile-input").files[0] to s3 server
	// call the url with /predict/filename_in_s3&query_point_&_delimited>
	
	//pass arguments in form : 		predict/jackknife&filename_in_s3&query_point_&_delimited
	//or 							optimise/print_to_file&filename_in_s3&lb1&ub1&...&lbn&ubn
	var argument_string = "";
	var predict = false;
	var optimise = false;
	
	if (document.getElementById("select-predict").checked && document.getElementById("select-optimise").checked) {
		alert('Please select only one script to run.')
	}
	else if (document.getElementById("select-predict").checked) {
		console.log(('running predict'))
		
		//add the jk marker
		if (document.getElementById('jackknife-checkbox').checked){
			argument_string += 'y&' 
		}
		else {
			argument_string += 'n&'
		}
		
		predict = true;
		
	}
	else if (document.getElementById("select-optimise").checked) {
		
		if (document.getElementById('optimise-output-checkbox').checked){
			argument_string += 'y&' 
		}
		else {
			argument_string += 'n&'
		}
		optimise = true;
	}
	else {
		alert('Please select which script you would like to run')
	}
 
	//so is the same as the filename in the repository)
	//eg: file:///home/james/Documents/TBR_predictor/raw_data/60_all_all_Be12Ti_Li2TiO3_TBR.txt
	
	fileDirectory = (document.getElementById("datafile-input")).value;
	var filename = getFilename(document.getElementById('datafile-input').value);
	console.log('filename found: ' + filename)
	argument_string += filename; //document.getElementById("datafile-input").value
	
	console.log('dimensions: ' + dimensions)
	console.log('names: ' + names)
	
	if (predict) {
		
		for (var p = 1; p <= dimensions ; p++) {
		
		console.log('arg' + p + ' = ' + document.getElementById('arg' + p.toString()).value.toString())
		argument_string += ('&' + (document.getElementById('arg' + p).value).toString());
		}

		runPredictScript(argument_string);
	}
	else if (optimise) {
		
		for (var p = 1; p <= dimensions*2 ; p++) {
			
			console.log('arg' + p + ' = ' + document.getElementById('arg' + p.toString()).value.toString())
			argument_string += ('&' + (document.getElementById('arg' + p).value).toString());
		}
		runOptimiseScript(argument_string)
	}
	
}


function getFilename(inputFilename){
    //splits the input directory and filename into an output name for the data file into the working directory
    
    var j= inputFilename.length - 1; //ie last char is always /
    var outputName;
    console.log('taken filepath : ' + inputFilename)
    
    console.log('first char : '  + inputFilename[j])
    
    while (inputFilename[j] != '\\' && inputFilename[j] != "/" && j > 0){
        j --;
    }
    
    console.log('breaker point : ' + j )
    //eg in current working directory
    if (j == 0) {
        outputName = inputFilename;
    }
    else{
    	var directory = "";
    	var filename="";
    	
    	directory=inputFilename.substring(0,j);
    	console.log('directory : ' + directory )
   
    	filename=inputFilename.substring(j+1,inputFilename.length);
    	console.log('filename found : ' + filename )
        
    	outputName = filename;
    }
    
    return outputName;
}

function runPredictScript(argument_string) {
	
	console.log('running JSON, passing : ' + argument_string)
	$.getJSON('http://localhost:5000/predict/' + argument_string,
			function(data){
		//data.result is returned by the jsonify in the python script
		document.getElementById('results-division').innerHTML = data.result
	}
	);
}

function runOptimiseScript(argument_string) {
	
	console.log('running JSON, passing : ' + argument_string)
	$.getJSON('http://localhost:5000/optimise/' + argument_string,
			function(data){
		//data.result is returned by the jsonify in the python script
		document.getElementById('results-division').innerHTML = data.result
	}
	);
}

function makeTable(change) {
	
		console.log('File uploaded. Attempting read before table generation.')
		
		var filelist_obj = document.getElementById("datafile-input").files;
		console.log('Creating FileReader object...')
		var fr = new FileReader();
		
		var file_obj = filelist_obj[0];
		if (typeof file_obj =='undefined'){
			alert('Please upload a valid datafile')
		}
		else {
			console.log('file object name: ' + file_obj.name + ', size : ' + file_obj.size)
			
			console.log('attempting to read file')
			fr.readAsText(file_obj);		
			
			fr.onload = readSuccess;
			
			function readSuccess(e) {
				/*** NOTE: This is main execution***/
				console.log('file was loaded- .onload called - retrieving data')
				
				var data = e.target.result; //should contain 1 string of data text
				
				names = getNames(data);
				dimensions = names.length-1;
				console.log('names received by readSuccess: ' + names)
				
				//make the table based on names
				createTable(names);
			};
		}
	}

function makePlot(change) {
		
		numberOfPlots ++;
		var optimise = document.getElementById("select-optimise").checked;
		var predict = document.getElementById("select-predict").checked;
		
		console.log('File uploaded. Attempting header read-in before plotting data.')
		
		var plotFilelistObj = document.getElementById('plot-file-input').files;
		console.log('Creating FileReader object...')
		
		var plotFr = new FileReader();
			
		var plotFileObj = plotFilelistObj[0];
		if (typeof plotFileObj =='undefined'){
			alert('Please input valid plot data file')
		}
		else {
			console.log('file object name: ' + plotFileObj.name + ', size : ' + plotFileObj.size)
			
			console.log('attempting to read file')
			plotFr.readAsText(plotFileObj);		
			
			plotFr.onload = plotReadSuccess;
			
			function plotReadSuccess(e) {
				/*** NOTE: This is main execution***/
				console.log('file was loaded- .onload called - retrieving plot data')
				
				var plotData = e.target.result; //should contain 1 string of data text
				
				plotNames = getNames(plotData);
				console.log('names received by readSuccess: ' + plotNames)
				dimensions = plotNames.length - 1;
				
				if (predict && dimensions > 3) {
					alert('Can only plot prediction results for up to 3 dimensions!')
				}	
				else {
					if (optimise) {
						//Plot
						if (document.getElementById('animate-checkbox').checked) {
							animateOptimiser(plotData);
						}
						else {
							plotOptimiser(plotData);
						}
					} 
					else if (predict) {
						plotPredict(plotData);
					}
				}
			};
		}
	}

function resetArea(divId){
	Plotly.newPlot('graph-division', {x:0, y:0}, {margin:{t:0}});
	numberOfPlots=0;
}	

function removePlot(divId){
	Plotly.deleteTraces('graph-division', numberOfPlots-1);
	numberOfPlots--;
}	

			function getNames(data) {
				/*A function that, given a datafile as a single string, will look at the first row and decide if it 
				 * has been passed headers or pure data, then will return appropriate names.*/
				console.log('Getting names from datafile, path: ' + document.getElementById("datafile-input").value)
				var row_list = [];
				var first_row_array = [];
				var names = [];
			
				//check if ajax ran
				if (typeof data == 'undefined'){
					console.log('No data was read. Resorting to default')
				}
				else {
					//splits each row into a different element
					first_row_array = (data).split('\n', 1);
					var first_row = first_row_array[0]
					//split elements of the row- useful
					var first_row_split = first_row.split(/[ ,]+/);
					
					var n = (first_row_split.length - 1);
					console.log('dimensions read : ' + n)
					
					console.log('first row split read as : ' + first_row_split)
				}
				
				//set names dependent on first row
				if (typeof data == 'undefined' || isNumber(first_row[0])) {
					console.log('string not detected on first row- resorting to default titles for names')
					for (var i = 0; i < n ; i++) {
						names[i] = "X"+(i+1);
					}
					names[n] = "dep_var";			
				} 
				else {
					console.log('reading supplied names')
					names = first_row_split;						
				}
						
				console.log('returning names:' + names)
				return names;
			}
			
			function createTable(names) {
				/*a function that, given a list of names, will produce a table to allow appropriate input arguments*/
				console.log('createTable called')
				if (document.getElementById("select-predict").checked && document.getElementById("select-optimise").checked) {
					alert('Please select only one script to run.')
				}
				else if (document.getElementById("select-predict").checked) {
					createPredictTable(names);
				}
				else if (document.getElementById("select-optimise").checked) {
					createOptimiseTable(names);
				}
				else {
					alert('Please select which script you would like to run')
				}
			}
			
			function createPredictTable(names) {
			/*produces the argument table for the predict script*/	
				var num_args = names.length - 1;
				
				var theader = '<table border="1">\n';
				var tbody = '';
						
				//Go through and add the headers and lavel. 
				//TODO: potentially change to names from datafile
				tbody += '<td>Dimension:</td>'
				for( var i=0;i<num_args; i++) {
					tbody += '<td>';
					tbody+= names[i] ;
					tbody += '</td>'
				}
				//end the row, start the next
				tbody+='</tr><tr>'
				tbody += '<td>Value:</td>'
				//add the input buttons
				for( var i=0;i<num_args; i++) {
					tbody += '<td>';
					tbody+= '<input type ="number" min="0" value="0" id="arg' +(i+1) + '" name="arg' + (i+1) +'">' ;
					tbody += '</td>';
				}
				
				tbody+='</tr>\n';
				var tfooter = '</table>';
				
				document.getElementById('arg-table').innerHTML = theader + tbody + tfooter;
				console.log('Table created')
			}
			
			function createOptimiseTable(names){
				/* makes argument table for optimise script */	
				dimensions = (names.length - 1);
				var num_args = dimensions*2;
				var theader = '<table border="1" style="margin:10px">\n';
				var tbody = '';
				
				//Go through and add the headers and label. 
				//TODO: potentially change to names from datafile
				tbody += '<td>Bound:</td>';
				for( var i=0;i<num_args; i++) {
					tbody += '<td>';
					if (i%2 == 0) {
						tbody+= names[i/2] + '_LowerBound' ;
					} else {
						tbody+= names[(i-1)/2] + '_UpperBound' ;
					}
					tbody += '</td>';
				}
				//end the row, start the next and label it
				tbody+='</tr><tr><td>Input Value:</td>'
				//add the input buttons
				for( var i=0;i<num_args; i++) {
					tbody += '<td>';
					tbody+= '<input type ="number" min="0" value="0" id="arg' +(i+1) + '" name="arg' + (i+1) +'">' ;
					tbody += '</td>';
				}
				
				tbody+='</tr>\n';
				var tfooter = '</table>';
				
				document.getElementById('arg-table').innerHTML = 
					theader + tbody + tfooter +
						'(leave as 0 to default to data-bounds)';				
				console.log('Table created')
			}
			
			function isNumber(n) {
				  return !isNaN(parseFloat(n)) && isFinite(n);
				}
			
			function plotOptimiser(data) {
				
				var plotNames = getNames(data); 
				dimensions = plotNames.length-1;
				
				var depVarName = plotNames[dimensions]; //Y
				
				var dataAsRows = data.split('\n');
				var dataAsRowsCols = []
				
				var steps = (dataAsRows.length-1); // X (first row is names)
				
				for ( var k = 0 ; k <= steps ; k ++) {
					dataAsRowsCols[k] = dataAsRows[k].split(/[ ,]+/);
				} 
				
				var x_vars = [];
				var y_vars = [];
				
				for (i=0 ; i<steps ; i++) {
					x_vars[i] = i+1;
					y_vars[i] = dataAsRowsCols[i+1][dimensions]; //ie final col of each row
				}
				
				LOCATION = document.getElementById('graph-division');
				
				Plotly.plot(
					LOCATION, 
					
					[{ 
					x: x_vars,
					y: y_vars, 
					name: document.getElementById("datafile-input").value
					}], 
					{
					title: 'Optimisation Path',
					xaxis: {title: 'Steps'},
					yaxis: {title: depVarName},
				});
			}
			
			function animateOptimiser(data) {
				
				var plotNames = getNames(data); 
				dimensions = plotNames.length-1;
				var depVarName = plotNames[dimensions]; //Y
				
				var dataAsRows = data.split('\n');
				var dataAsRowsCols = []
				
				var steps = (dataAsRows.length-1); // X (first row is names)
				//DATA STARTS FROM ROW 2, INDEX 1, UP TO INDEX == STEPS
				//also splits names (dataasrowscols[0])
				for ( var k = 0 ; k <= steps ; k ++) {
					dataAsRowsCols[k] = dataAsRows[k].split(/[ ,]+/);
				} 
				
				//initialise
				var i = 1; // index of data- i=0 already intialised
				var x_vars = [1]; //step 1
				var y_vars = [dataAsRowsCols[1][dimensions]]; //first row (index 0) is name, start at index 1
				LOCATION = document.getElementById('graph-division');
				
				var y_vars_all =[];
				for (var p=1 ; p<=steps ; p++) {
					y_vars_all[p-1] = dataAsRowsCols[p][dimensions]; //ie final col of each row, first row is name
				}
				
				y_min = minimum(y_vars_all);
				y_max = maximum(y_vars_all);
				
				console.log('min : ' + y_min + ', max : ' + y_max)
				
				Plotly.newPlot(
						LOCATION, 
						
						[{ 
						x: x_vars,
						y: y_vars, 
						name: document.getElementById("datafile-input").value
						}], 
						{
						title: 'Optimisation Path',
						xaxis: {title: 'Steps', range:[0,steps]},
						yaxis: {title: depVarName, range: [y_min, y_max]},
						
						}
				)
					
					function addNext () {
						x_vars[i] = i+1; //ie step is 1 more than index
						y_vars[i] = dataAsRowsCols[i+1][dimensions]; //ie yvars[0] initialised already, and first row is names
						i++;
					}
				
					function update () {
						addNext();
					
						Plotly.animate(
								LOCATION, {
									data: [{x: x_vars, y: y_vars}] 
								}, {
									transition: { 
										duration: 0 
								}, 
								frame: { 
									duration : 0 , 
									redraw : false 
									}
								});
				
						requestAnimationFrame(update);
					}
					requestAnimationFrame(update);
				}
			
			//TODO: IF predicting: plot the LEARNED data set (1d, 2d, 3d) and plot the point being queried in a dif color
			function plotPredict(data) {
				alert('plotPredict not yet implemented')
			}
			
			function minimum(array) {
				
				var min = array[0];
				for (var i = 0; i<array.length ; i++){
					if (array[i]<min) {
						min = array[i]
					}
				}
				return min;
			}
			
			function maximum(array) {
				
				var max = array[0];
				for (var i = 0; i<array.length ; i++){
					if (array[i]>max) {
						max = array[i]
					}
				}
				return max;
			}
			