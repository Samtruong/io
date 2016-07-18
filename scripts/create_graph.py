#!/usr/bin/env python
""" This script can be called in terminal (with cmd args) to generate desired plot.

Author: Farmehr Farhour f.farhour@gmail.com

Takes in command line arguments and generates the desired output based on the input given.
Input Data that can be passed to this script:
    - JSON outputs generated by engines on various algorithms
Output that can be created by this script:
    - vega-spec JSON files
    - Plots with formats: SVG, PNG, HTML
Plot types that can be created:
    - Scatter graphs
    - Bar graphs
"""

import json2vega as json2vega               #convert json outputs to vega-spec JSONs
import vega2pic as vega2pic                 #generate visual from vega-spec json
from utils import parseCmdLineArgs  #function to parse cmd args
from utils import write_to_file     #function to write to file
import os,sys   #built-in

#create temp file
def write2tempfile(input):
    """a helper function that creates a temp file and stores the input passed to it in the file """
    import tempfile
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(input)
    temp.close()
    return temp

def getClassMethods(class_name):
    """return a list of all class names of the given class"""
    import inspect
    methods = []
    for a in inspect.getmembers(class_name, predicate=inspect.isfunction):
        methods.append(a[0])
    return methods

def main(argv):
    """Creates the desired graph by calling methods in json2vega.py and vega2pic"""
    ##################################
    ####OUTPUT TYPE CASE STATEMENT####
    ##################################
    #class for the output type case statements
    class OutputTypeCase:
        """class containing the functions for each case statement of the output type"""

        @staticmethod
        def vegajson():
            """if vegajson, then write the vegajson to file and return filename"""
            return write_to_file(rawinput=json,filetype='json',output_path=args.o,engine_name=args.engine,algorithm_name=args.algorithm,suffix=plot_obj.file_suffix,verbose=args.v)

        @staticmethod
        def html():
            """if html"""
            pass

        @staticmethod
        def svg():
            """if svg, then create svg and return the filename"""
            temp_file = write2tempfile(json)
            builder =  vega2pic.SVGBuilder(temp_file.name)
            svg = builder.buildPlot(verbose=args.v)
            return write_to_file(rawinput=svg,filetype='svg',output_path=args.o,engine_name=args.engine,algorithm_name=args.algorithm,suffix=plot_obj.file_suffix,verbose=args.v)

        @staticmethod
        def png():
            """if png, then create png and return the filename"""
            temp_file = write2tempfile(json)
            builder =  vega2pic.PNGBuilder(temp_file.name)
            png = builder.buildPlot(verbose=args.v)
            return write_to_file(rawinput=png,filetype='png',output_path=args.o,engine_name=args.engine,algorithm_name=args.algorithm,suffix=plot_obj.file_suffix,verbose=args.v)

    #get all method names of the case statement - used later for automating the case statement creation process, as well as the input argument choices
    output_types = getClassMethods(OutputTypeCase)

    #case statement for the output type. automatically generate cases based on functions of the OutputTypeClass
    case_outputtype = {}
    for output in output_types:
        case_outputtype[output] = getattr(OutputTypeCase,output)

    ##################################
    #####PLOT TYPE CASE STATEMENT#####
    ##################################
    class PlotTypeCase:
        """class containing the functions for each case statement of the plot type"""
        @staticmethod
        def bar():
            return json2vega.VegaGraphBar(output_path=args.o,
                                          input_path=args.inputpath,
                                          config_dir=args.config,
                                          labels=names,
                                          conditions_dict=conditions,
                                          axes_vars=axes_vars)

        @staticmethod
        def scatter():
            return json2vega.VegaGraphScatter(output_path=args.o,
                                          input_path=args.inputpath,
                                          config_dir=args.config,
                                          labels=names,
                                          conditions_dict=conditions,
                                          axes_vars=axes_vars)

    #get all method names of the case statement - used later for automating the case statement creation process, as well as the input argument choices
    plot_types = getClassMethods(PlotTypeCase)

    #case statement for the plot type. automatically generate cases based on functions of the PlotTypeClass
    case_plottype = {}
    for output in plot_types:
        case_plottype[output] = getattr(PlotTypeCase,output)


    ##################################
    ######CREATE REQUIRED INPUTS######
    ##################################

    # process input arguments passed
    args = parseCmdLineArgs(argv,output_choices=output_types, plot_choices=plot_types)
    if not os.path.exists(args.o):  # create output directory
        os.makedirs(args.o)

    # Create required arguments and dictionaries (from input arguments provided)
    conditions = {"algorithm": args.algorithm}
    if args.conds is not None:
        conditions.update(args.conds)
    axes_vars = {'x': args.xaxis, 'y': args.yaxis}
    names = {'engine_name': args.engine, 'algorithm_name': args.algorithm,
             'x_axis': args.xlabel, 'y_axis': args.ylabel, 'file_suffix': args.filesuffix}


    ##################################
    #######CREATE DESIRED PLOT########
    ##################################
    #calls the approrpiate function to generate the plot desired
    plot_obj = case_plottype[args.plottype]()


    ##################################
    #####INITIAL INPUT PROCESSING#####
    ##################################
    #read json and parse it
    plot_obj.read_json()
    graph = plot_obj.parse_jsons()
    #create vega-spec json
    json = plot_obj.pipe_vl2vg(graph)



    ##################################
    #########OUTPUT CREATION##########
    ##################################
    #calls the appropriate function to generate the output desired
    case_outputtype[args.outputtype]()

if __name__ == "__main__":
    main(sys.argv)
