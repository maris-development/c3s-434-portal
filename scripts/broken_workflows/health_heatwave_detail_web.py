import cdstoolbox as ct

##### Default options ----------------------------------
dataset_name = 'sis-heat-and-cold-spells'
periods = {'1971-2000':1986,
           '1981-2010':1996,
           '1991-2020':2006,
           '2001-2030':2016,
           '2011-2040':2026,
           '2021-2050':2036,
           '2031-2060':2046,
           '2041-2070':2056,
           '2051-2080':2066,
           '2061-2090':2076,
           '2070-2099':2085,
          }
allvars = ['heat_wave_days']
defaultvar = allvars[0]
alldefs = {'Climatological definition':'climatological_related',
           'Health definition':'health_related'}
allstats = ['ensemble_members_average', 'ensemble_members_standard_deviation']
alllevs = [0,1,2,3] # NUTS levelFs
allscens = {'RCP4.5':'rcp4_5', 'RCP8.5':'rcp8_5'}

fig1text = '''
## Timeseries of the EURO-CORDEX ensemble mean and standard deviation (SD) of the average number of heatwave days in {} under {}.
Using the {} for heatwave days. Hover the mouse over the time series plot to view the data values.  Click on the plot to reveal the action buttons for features such as "zoom" and "download plot as a png".

'''

LINK_TEXT = '↪Permalink to this configuration'
# text for drop-down menus
filter_desc = {'hdef': "Choose a heat wave definition",
               'period': "Choose a time period",
               'rcp': "Choose a scenario",
               'nuts_level':"Choose a NUTS level"
              }
filter_help = {'hdef': "Choose either the health definition or climate definition for heat waves",
               'period': "Choose a time window for the centres of the 30-year smoothed averages",
               'rcp': "Choose a scenario with medium (RCP4.5) or high (RCP8.5) greenhouse gas emissions",
               'nuts_level':"Select the size of the regions shown on the map, from largest (NUTS-0) to smallest (NUTS-3)"
              }

help_text = 'Click on a region to display a time series graph'

# colour schemes corresponding to overview app
magics_styles={"climatological_related": "cream_red_0_100", # should be 0-80 to be consistent
               "health_related": "cream_purple_0_90",
              }


##### Functions ----------------------------------------
def retrieve_data(dsetname,**kwargs):

    ##### 1) Retrieve data
    print(dsetname)
    data = ct.catalogue.retrieve(
        dsetname, kwargs
    )
    if 'ensemble_statistics' in kwargs:
        print("the data are ",kwargs['ensemble_statistics'])
    return data

def subselect_data(data,rangeofyrs=['2018','2023']):
    ##### 2) Select subregion/time
    data_sel = ct.cube.select(data,
                              time=rangeofyrs # [start,end]
                             )
    return data_sel

def avg_nuts(data,nutslevel=0):

    ##### 3) Apply mask of NUTS regions
    # this step is no longer necessary after Aug 2020 upgrade

    ##### 4) Calculate average over NUTS regions
    print("calculating averages over NUTS")
    nuts = ct.shapes.catalogue.nuts(level=nutslevel)
    data_nuts_mean = ct.shapes.average(data, nuts)

    return data_nuts_mean

def plot_shapes(darray,darray2,var='unknown',exp='',period=[1985,2010],mydef='',dummy=None):

    ##### 6) Plot the regional averages
    # subset the data
    #darray_sub = subselect_data(darray,period)
    darray_sub = ct.cube.select(darray,time=period, drop=True)
    # in spite of the drop=True, this does not get rid of the time dimension
    # hack to get rid of the time dimension - this will only work if length = 1
    darray_sub2 = ct.cube.average(darray_sub, dim='time')

    # update attributes for automatic styling
    mystyle = magics_styles[mydef]
    mapdata = ct.cdm.update_attributes(darray_sub2,
                                             {'cds_magics_style_name': mystyle,})
    dummy = ct.cdm.update_attributes(dummy, {'cds_magics_style_name': mystyle,})

    print("plotting livemap")
    livemap_data = ({
        'data': mapdata,
        "click_kwargs": {
            "darray": darray,
            "sdarray":darray2,
            #"nutslev":nutslevel,
            "var":var,
            "scen":exp,
            "mydef":mydef
        },
        'label': var,
        'label_template': '%{NUTS_NAME} %{value:.1f}',
        #'cmap': 'plasma',
        #'bins': 25,
        'checked': True,
        'zoom_to_selected':False,
        'type':'layer'
    })
    legend_data = ({
     'data': dummy,
                'type': 'layer',
                'checked': True,
    })
    fig = ct.livemap.plot([livemap_data,legend_data],show_legend=True, #_enable_geoserver=True,
                          date_format='yyyy',min_zoom=2)

    return fig

##### Sub-app when clicking on map----------------------

@ct.child(position='bottom') #'floating')
@ct.output.markdown()
@ct.output.livefigure()
def region_timeseries(params, **kwargs):

    ##### Plot detailed information for selected region
    nuts_code = params['properties']['NUTS_ID']
    regname = params['properties']['NUTS_NAME']

    data = kwargs.get('darray')
    sd = kwargs.get('sdarray')
    scen = kwargs.get('scen')
    mydef = kwargs.get('mydef')

    # select data for the selected region
    print('select data...')
    # need to pass on function argument that depends on the nuts level used
    #args = {"nuts_level"+str(nutslevel): nuts_code} # nuts_level0, nuts_level1, ...
    #data_reg = ct.cube.select(data, **args) # unpacks as nuts_level1=nuts_code
    data_reg = ct.cube.select(data,nuts=nuts_code)
    sd_reg = ct.cube.select(sd,nuts=nuts_code)

    data_reg_min = ct.operator.sub(data_reg,sd_reg)
    data_reg_max = ct.operator.add(data_reg,sd_reg)

    # create filled contour plot
    #d_units = ct.cdm.get_attributes(data)['units']
    #d_name = ct.cdm.get_attributes(data)['long_name']
    #ytitle = d_name + " (" + d_units + ")"
    #ytitle = "Number of " + mystat
    #ytitle = d_name
    ytitle = "Days"

    #layout_dict = {'yaxis':{'title':ytitle}}
    # in this case we are only dealing with annual data
    myformat = "%Y"
    layout_dict = {
        'xaxis': {
            'title': 'Year',
            'showline': True,
            'linecolor': '#000000',
            'hoverformat': myformat
        },
        'yaxis': {
            'title':ytitle,
            'showline': True,
            'linecolor': '#000000'
        },
        'height': 450
    }

    subfig = ct.chart.line(data_reg_min,scatter_kwargs={
        'name':'-SD',
        'marker':{'color':'grey','size':1},
    })
    subfig = ct.chart.line(data_reg, fig=subfig, scatter_kwargs={
        'name':'mean', 'fill':'tonexty', 'fillcolor':'aquamarine',
        'marker':{'size':1}
    })
    subfig = ct.chart.line(data_reg_max, fig=subfig, scatter_kwargs={
        'name':'+SD', 'fill':'tonexty', 'fillcolor':'aquamarine',
        'marker':{'color':'grey','size':1}
    }, layout_kwargs=layout_dict)

    # create a text string describing the graph
    # find the scenario name (dict key) belonging to this scenario (dict value)
    scenname = [key for key in allscens if (allscens[key] == scen)]
    defname = [key for key in alldefs if (alldefs[key] == mydef)]
    gr_descr = fig1text.format(regname, scenname[0], defname[0].lower())

    return gr_descr, subfig
    #return subfig


##### Application --------------------------------------
#layout = ct.Layout(rows=3, justify='flex-start')
#layout.add_widget(row=0, content='hdef', xs=4, sm=4, md=3)
#layout.add_widget(row=0, content='period', xs=4, sm=2, md=2)
#layout.add_widget(row=0, content='rcp', xs=12, sm=4, md=2)
#layout.add_widget(row=0, content='nuts_level', xs=4, sm=6, md=2)
#layout.add_widget(row=1, content='output-0')
#layout.add_widget(row=2, content='output-1')
#layout.add_widget(row=2, content="[child]", sm=12, lg=6, min_height=620)

variables = ct.Layout(rows=2, justify='flex-start')
variables.add_widget(row=0, content='hdef', xs=4, sm=2, md=2)
variables.add_widget(row=0, content='period', xs=4, sm=2, md=2)
variables.add_widget(row=0, content='rcp', xs=4, sm=2, md=2)
variables.add_widget(row=0, content='nuts_level', xs=4, sm=2, md=2)

app = ct.Layout(rows=3, justify='flex-start')
app.add_widget(row=0, content='output-0')
app.add_widget(row=1, content='output-1')
app.add_widget(row=2, content='output-2')

layout = ct.Layout(rows=2, justify='flex-start')
layout.add_widget(row=0, content=variables)
layout.add_widget(row=1, content=app)
layout.add_widget(row=1, content="[child]", md=8, min_height=550)
@ct.application(title='Number of heat wave days',
                layout=layout)

# dropdown for choosing definition
@ct.input.dropdown('hdef', label = 'Definition',
                   values=alldefs,  # default=defaultvar,
                   description = filter_desc['hdef'],
                   help = filter_help['hdef']
                  )

# dropdown for choosing time period
@ct.input.dropdown('period',
                   label='Time period',
                   values=periods.keys(),default='2070-2099',
                   description = filter_desc['period'],
                   help = filter_help['period']
                  )

# dropdown for choosing scenario
@ct.input.dropdown('rcp',
                   label='Scenario',
                   values=allscens.keys(),default='RCP8.5',
                   description = filter_desc['rcp'],
                   help = filter_help['rcp']
                  )

# dropdown for choosing NUTS level
@ct.input.dropdown('nuts_level', label = 'NUTS level',
                   values=alllevs,default=alllevs[0],
                   description = filter_desc['nuts_level'],
                   help = filter_help['nuts_level']
                  )

# output widget
@ct.output.markdown()
@ct.output.livemap(click_on_feature=region_timeseries)
@ct.output.markdown()


# actual workflow calling the functions above
def workflow(hdef,period,rcp,nuts_level):

    mydef = alldefs[hdef]
    myvar = allvars[0]
    myper = periods[period]

    # retrieve data
    print("retrieving data...")
    datarray = retrieve_data(dataset_name,
                             variable = myvar,
                             definition = mydef,
                             experiment = allscens[rcp],
                             ensemble_statistics = allstats[0],
                             ensemble_statistic = allstats[0],
                             grid = [3,3]
                            )
    sdarray = retrieve_data(dataset_name,
                             variable = myvar,
                             definition = mydef,
                             experiment = allscens[rcp],
                             ensemble_statistics = allstats[1],
                             ensemble_statistic = allstats[1],
                             grid = [3,3]
                            )

    # calculate averages over nuts regions
    data_nuts_avg = avg_nuts(datarray,nutslevel=nuts_level)
    #data_nuts_mrg = merge_nuts(data_nuts_avg,nutslevel=nuts_level)
    sd_nuts_avg = avg_nuts(sdarray,nutslevel=nuts_level)

    # dummy layer for showing legend in livemap
    dummydata = ct.cube.index_select(datarray-999,time=0)

    # plot the averages
    livemap = plot_shapes(data_nuts_avg,sd_nuts_avg,
                          var=myvar,exp=allscens[rcp],
                          period=myper,mydef=mydef,dummy=dummydata)


    args = {
        'rcp': rcp,
        'nuts_level': nuts_level,
        'hdef': hdef,
        'period': period,
    }
    query = get_query(args)
    permalink = f'[{LINK_TEXT}](?{query})'
    return help_text, livemap, permalink


def get_query(args):
    """Construct a URL query based on input selections.
       Args:
           args (dict): The arguments passed from input widgets into your main application.
    """
    parameters = []
    for arg, value in args.items():
        # ints and floats need a type identifier (always labelled as 'float')
        if isinstance(value, (int, float)):
            arg = f'{arg}:float'
        parameters.append(f'{arg}={value}')

    query = '&'.join(parameters)
    return query
