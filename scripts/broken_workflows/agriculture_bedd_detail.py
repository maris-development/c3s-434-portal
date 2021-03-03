import cdstoolbox as ct

##### Default options ----------------------------------
# note as an interim solution we are not calculating BEDD from sis-agrometeorological-indicators
# dataset_hist = 'sis-agrometeorological-indicators'
# var_hist = ['2m_temperature','24_hour_minimum']

dataset_hist = 'sis-agroclimatic-indicators'
var_hist = 'biologically_effective_degree_days'

dataset_scen = 'sis-agroclimatic-indicators'
var_gcm = {'degree days':'biologically_effective_degree_days',
          }
mystat = 'degree days'

periods = {'2071-2099':'207101_209912',
           '2041-2070':'204101_207012',
           '2011-2040':'201101_204012'
          }
period_hist = [1981,2010]
months = {'Annual':0,'January':1,'February':2, 'March':3, 'April':4, 'May':5, 'June':6,
          'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}


alllevs = [0,1,2,3] # NUTS levels
allscens = {'RCP8.5':'rcp8_5', 'RCP2.6':'rcp2_6'}
allgcms = ['gfdl_esm2m_model','hadgem2_es_model','ipsl_cm5a_lr_model',
           'miroc_esm_chem_model','noresm1_m_model']

europe_bb = [-25, 49, 34, 72] # min_lon, max_lon, min_lat, max_lat

create_anim = False

LINK_TEXT = '↪Permalink to this configuration'

fig1text = '''
## Change in number of degree days in {} {}
Showing the range of changes in number of degree days across an ensemble of {} climate models.
Hover over the graph to see the values.
'''

fig2text = '''
## Historical climate
Showing average number of degree days per month in the period {}-{}
based on ERA-interim reanalysis data. Hover over the graph to see the values.
'''
### based on ERA5 reanalysis data

# text for drop-down menus
filter_desc = {'speriod': "Choose a time period",
               'smon': "Choose a month",
               'rcp': "Choose a scenario",
               'nuts_level':"Choose a NUTS level",
              }
filter_help = {'speriod': "Choose a 30-year period average",
               'smon': "Choose a month or annual anomaly",
               'rcp': "Choose a scenario with low (RCP2.6) or high (RCP8.5) greenhouse gas emissions",
               'nuts_level':"Select the size of the regions shown on the map, from largest (NUTS-0) to smallest (NUTS-3)",
              }

help_text = 'Click on a region to display a time series graph'

# colour schemes corresponding to overview app
magics_styles={"Annual":"cream_red_200_2000",
               "Monthly": "cream_red_1_400",
              }

NON_NUTS  = ['Kosovo', 'Bosnia and Herzegovina']
KOSOVO_ATTRIBUTES = {
    '_cds_toolbox_aux_wms_filters': "{'NAME_EN': ['Kosovo']}",
}
NON_KOSOVO = ', '.join('"{}"'.format(c) for c in NON_NUTS if c != 'Kosovo')
NON_KOSOVO_ATTRIBUTES = {
    '_cds_toolbox_aux_wms_filters': f"{{'NAME_EN': [{NON_KOSOVO}]}}",
}


##### Functions ----------------------------------------
def retrieve_data(dsetname,**kwargs):

    ##### Retrieve data
    data = ct.catalogue.retrieve(
        dsetname, kwargs
    )
    if 'ensemble_statistics' in kwargs:
        print("the data are ",kwargs['ensemble_statistics'])
    return data


def subselect_data(data,**kwargs):
    ##### Select subregion/time
    myextent = kwargs.get('extent')
    data_sel = ct.cube.select(data,
                              extent=myextent) # min_lon, max_lon, min_lat, max_lat
    return data_sel


def avg_time(data):

    ##### Calculate time average
    #data_avg = ct.cube.average(data,dim='time')
    # use resample to retain the times coordinates
    data_avg = ct.cube.resample(data,freq='month',how='mean')
    return data_avg

def count_days_threshold(data, threshold=0, how="above"):

    #### Calculate the number of days above or below a certain threshold
    if how == "above":
        data_test = ct.cube.where(data > threshold, 1, 0)
    elif how == "below":
        data_test = ct.cube.where(data < threshold, 1, 0)
    else:
        raise Exception('Unknown keyword in count_days_threshold(). The value of how was: {}'.format(how))
    # count number of days above or below threshold
    data_sum = ct.cube.resample(data_test,freq='month',how='sum')
    # update unit attribute
    data_sum = ct.cdm.update_attributes(data_sum, attrs={'units': 'day'})
    return data_sum

def calc_anom(data_scen,data_hist):

    #### Calculate anomalies from historical climatology
    data_hist_clim = ct.climate.climatology_mean(data_hist)
    data_anomalies = ct.climate.anomaly(data_scen, climatology=data_hist_clim)
    return data_anomalies


def avg_nuts(data,nutslevel=0):

    ##### Apply mask of NUTS regions
    # this step is no longer necessary after Aug 2020 upgrade

    ##### 4) Calculate average over NUTS regions
    print("calculating averages over NUTS")
    nuts = ct.shapes.catalogue.nuts(level=nutslevel)
    data_nuts_mean = ct.shapes.average(data, nuts)

    non_nuts = ct.shapes.catalogue.countries(name=NON_NUTS)
    data_year_nuts_non = ct.shapes.average(data, non_nuts)

    return data_nuts_mean, data_year_nuts_non


def plot_shapes(darray,darray2,var='unknown',exp='',mon=1,dummy=None):

    ##### Plot the regional averages
    # need to pass on darray2 (a list of data arrays) as separate data arrays
    # as the full list is not preserved in the child app
    print("plotting livemap")

    # plot animated series of maps if required, otherwise the temporal average
    if create_anim == True:
        mapdata = darray[0]
        mapdata_non_nuts = darray[3]
    else:
        mapdata = ct.cube.average(darray[0], dim='time')
        mapdata_non_nuts = ct.cube.average(darray[3], dim='time')
    # update attributes for automatic styling
    if mon == 0:
        mystyle = magics_styles["Annual"]
    else:
        mystyle = magics_styles["Monthly"]
    mapdata = ct.cdm.update_attributes(mapdata,
                                             {'cds_magics_style_name': mystyle,})
    mapdata_non_nuts = ct.cdm.update_attributes(mapdata_non_nuts,
                                             {'cds_magics_style_name': mystyle,})
    dummy = ct.cdm.update_attributes(dummy, {'cds_magics_style_name': mystyle,})

    countries = ct.cdm.get_coordinates(mapdata_non_nuts)['countries']['data']
    kosovo_mask = mapdata_non_nuts - mapdata_non_nuts + [c=='KOS' for c in countries]
    non_kosovo_mask = mapdata_non_nuts - mapdata_non_nuts + [c!='KOS' for c in countries]
    kosovo = ct.cube.where(kosovo_mask, mapdata_non_nuts, drop=True)
    kosovo = ct.cdm.update_attributes(kosovo, KOSOVO_ATTRIBUTES)
    mapdata_non_nuts =  ct.cube.where(non_kosovo_mask, mapdata_non_nuts, drop=True)
    mapdata_non_nuts = ct.cdm.update_attributes(mapdata_non_nuts, NON_KOSOVO_ATTRIBUTES)

    livemap_data = [
        {
            'data': mapdata, #darray[0],
            "click_kwargs": {
                "ensarray1": darray[0],
                "ensarray2": darray[1],
                "ensarray3": darray[2],
                "climarray1":darray2[0],
                "climarray2":darray2[1],
                "climarray3":darray2[2],
                "climarray4":darray2[3],
                #"nutslev":nutslevel,
                "var":var,
                "scen":exp,
                "mon":mon
            },
            'label': var,
            'label_template': '%{name} %{value:.1f}',
            'checked': True,
            'zoom_to_selected':False,
            'date_format':'yyyy',
            'type':'layer',
        },
        {
            'data': mapdata_non_nuts, #darray[0],
            "click_kwargs": {
                "ensarray1": darray[3],
                "ensarray2": darray[4],
                "ensarray3": darray[5],
                "climarray1":darray2[4],
                "climarray2":darray2[5],
                "climarray3":darray2[6],
                "climarray4":darray2[7],
                #"nutslev":nutslevel,
                "var":var,
                "scen":exp,
                "mon":mon
            },
            'label': var,
            'label_template': '%{name} %{value:.1f}',
            'checked': True,
            'zoom_to_selected':False,
            'date_format':'yyyy',
            'type':'layer',
        },
        {
            'data': kosovo, #darray[0],
            "click_kwargs": {
                "ensarray1": darray[3],
                "ensarray2": darray[4],
                "ensarray3": darray[5],
                "climarray1":darray2[4],
                "climarray2":darray2[5],
                "climarray3":darray2[6],
                "climarray4":darray2[7],
                #"nutslev":nutslevel,
                "var":var,
                "scen":exp,
                "mon":mon
            },
            'label': var,
            'label_template': 'Kosovo (under UNSCR 1244/99) %{value:.1f}',
            'checked': True,
            'zoom_to_selected':False,
            'date_format':'yyyy',
            'type':'layer',
        },

    ]
    legend_data = {
     'data': dummy,
                'type': 'layer',
                'checked': True,
    }

    uk_mask = ct.shapes.catalogue.nuts(nuts_id='UK')
    uk_mask_style = {
        'fillColor': '#ffffff',
        'fillOpacity': 1,
        'color': '#000000',
        'weight': 1,
    }
    uk_mask = {
        'data': ct.shapes.get_geojson(uk_mask),
        'style': uk_mask_style,
        'style_selected': uk_mask_style,
        'label_template': ' ',
    }

    fig = ct.livemap.plot(livemap_data+[uk_mask,legend_data],show_legend=True, crs='EPSG3857', min_zoom=3, zoom=3,
                          date_format='yyyy')

    return fig


def plot_climatology(mean,sd,pc0,pc1):

    ##### Make a climatology plot
    print("in plot_climatology")

    # get maximum value for plot
    # as we need to set min and max explicitly to prevent negative values
    meansd = ct.operator.add(mean, sd)
    maxvals = ct.math.maximum(meansd,pc1)
    plotmax = ct.cdm.get_values(ct.math.max(maxvals))['values'][0]
    print(plotmax)

    layout_kwargs = {
        'xaxis':{
            'tickvals':[1,2,3,4,5,6,7,8,9,10,11,12],
            'ticktext':['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
            'title': 'Month',
            'showline': True,
            'linecolor': '#000000'
        },
        'yaxis': {
            'showline': True,
            'linecolor': '#000000',
            'range': [0,plotmax],
            'title': "Number of " + mystat
        },
       'legend': {
           'orientation':'h',
           'y':-0.15,
           'x':0.1
       },
       'height': 500
    }

     # Add a line plot for monthly climatological means to the plot
    climfig = ct.chart.line(mean,
                            scatter_kwargs={'name':'Average','mode':'lines'},
                            layout_kwargs=layout_kwargs,
                            error_y=sd)

     # Add a line plot for the 5th percentile of monthly climatologocial mean
    climfig = ct.chart.line(pc0, fig=climfig,
                            scatter_kwargs={'name':'5th percentile', 'mode': 'lines'},
                            line={'dash':'dot','width':3},
                            layout_kwargs=layout_kwargs)

     # Add a line plot for 95th percentile of monthly climatologocial mean
    climfig = ct.chart.line(pc1,fig=climfig,
                            scatter_kwargs={'name':'95th percentile','mode':'lines'},
                            line={'dash':'dot','width':3},
                            layout_kwargs=layout_kwargs)

    return climfig



##### Sub-app when clicking on map----------------------

@ct.child(position='bottom') #'floating')
@ct.output.markdown()
@ct.output.livefigure()
@ct.output.markdown()
@ct.output.livefigure()

def region_timeseries(params, **kwargs):

    ##### Plot detailed information for selected region
    try:
        nuts_code = params['properties']['NUTS_ID']
        nuts_name = params['properties']['name']
        sel_kwargs = {'nuts': nuts_code}
    except KeyError:
        nuts_code = params['properties']['ADM0_A3']
        nuts_name = params['properties']['name']
        sel_kwargs = {'countries': nuts_code}

    # gcm anomaly data
    mon = kwargs.get('mon')
    # find the month name (dict key) belonging to this month nr (dict value)
    monname = [key for key in months if (months[key] == mon)]
    # update figure text and hover format
    if mon == 0:
        monstring = "per year"
        myformat = "%Y"
    else:
        monstring = "in " + monname[0]
        myformat = "%b %Y"
    fig1capt = fig1text.format(nuts_name,monstring,len(allgcms))
    ens_avg = kwargs.get('ensarray1')
    ens_max = kwargs.get('ensarray2')
    ens_min = kwargs.get('ensarray3')

    # select data for the selected region
    # need to pass on function argument that depends on the nuts level used
    #args = {"nuts_level"+str(nutslevel): nuts_code} # nuts_level0, nuts_level1, ...
    #data_reg = ct.cube.select(data, **args) ####### unpacks as nuts_level1=nuts_code
    ens_avg_reg = ct.cube.select(ens_avg,**sel_kwargs)
    ens_max_reg = ct.cube.select(ens_max,**sel_kwargs)
    ens_min_reg = ct.cube.select(ens_min,**sel_kwargs)

    # plot the anomaly data ######################################
    #subfig = ct.chart.line(ens_avg_reg) #,title=nuts_code)

    # create filled contour plot
    #d_units = ct.cdm.get_attributes(ens_avg_reg)['units']
    #d_name = ct.cdm.get_attributes(data)['long_name']
    #ytitle = d_name + " (" + d_units + ")"
    #ytitle = var + " anomaly (" + d_units + ")"
    ytitle = "Number of " + mystat

    #layout_dict = {'yaxis':{'title':ytitle}}
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
        'legend': {
           'xanchor':'center',
           'yanchor':'top',
           'orientation':'v',
           'y':-0.15,
           'x':0.1
        },
        'height': 500
    }
    subfig = ct.chart.line(ens_min_reg,scatter_kwargs={
        'name':'minimum',
        'marker':{'color':'grey'},
    })
    subfig = ct.chart.line(ens_avg_reg, fig=subfig, scatter_kwargs={
        'name':'mean', 'fill':'tonexty', 'fillcolor':'aquamarine',
        #'hovertemplate': '%{x|%Y} %{y}'
    }) # '%{y:20,.2f} %{x}'
    subfig = ct.chart.line(ens_max_reg, fig=subfig, scatter_kwargs={
        'name':'maximum', 'fill':'tonexty', 'fillcolor':'aquamarine',
        'marker':{'color':'grey'}
    }, layout_kwargs=layout_dict)


    # reanalysis data
    print("reanalysis plot")
    fig2capt = fig2text.format(period_hist[0],period_hist[1])
    climdata1 = kwargs.get('climarray1')
    climdata2 = kwargs.get('climarray2')
    climdata3 = kwargs.get('climarray3')
    climdata4 = kwargs.get('climarray4')
    # second plot as timeseries plot
    #data2_reg = ct.cube.select(data2,NUTS_ID=nuts_code)
    #subfig2 = ct.chart.line(data2_reg)

    # second plot as climatology plot
    # based on example workflow linked from
    # https://cds.climate.copernicus.eu/toolbox-editor/howtos/b5_climatologies_and_anomalies_part1
    clim_mean = ct.cube.select(climdata1,**sel_kwargs)
    clim_sd = ct.cube.select(climdata2,**sel_kwargs)
    clim_pc0 = ct.cube.select(climdata3,**sel_kwargs)
    clim_pc1 = ct.cube.select(climdata4,**sel_kwargs)
    subfig2 = plot_climatology(clim_mean, clim_sd, clim_pc0, clim_pc1)

    return fig1capt, subfig, fig2capt, subfig2


##### Application --------------------------------------
#layout = ct.Layout(rows=3, justify='flex-start')
#layout.add_widget(row=0, content='statistic', xs=4, sm=4, md=3)
#layout.add_widget(row=0, content='speriod', xs=4, sm=2, md=2)
#layout.add_widget(row=0, content='smon', xs=4, sm=2, md=2)
#layout.add_widget(row=0, content='rcp', xs=4, sm=2, md=2)
#layout.add_widget(row=0, content='nuts_level', xs=4, sm=2, md=2)
#layout.add_widget(row=1, content='output-0')
#layout.add_widget(row=2, content='output-1')
#layout.add_widget(row=1, content="[child]", md=6, min_height=1200)

variables = ct.Layout(rows=2, justify='flex-start')
variables.add_widget(row=0, content='speriod', xs=4, sm=2, md=2)
variables.add_widget(row=0, content='smon', xs=4, sm=2, md=2)
variables.add_widget(row=0, content='rcp', xs=4, sm=2, md=2)
variables.add_widget(row=0, content='nuts_level', xs=4, sm=2, md=2)

app = ct.Layout(rows=4, justify='flex-start')
app.add_widget(row=0, content='output-0')
app.add_widget(row=1, content='output-1')

layout = ct.Layout(rows=2, justify='flex-start')
layout.add_widget(row=0, content=variables)
layout.add_widget(row=1, content=app)
layout.add_widget(row=1, content="[child]", sm=6, min_height=1200)

@ct.application(title='Change in number of biologically effective degree days',
                layout=layout)


# dropdown for choosing time period
@ct.input.dropdown('speriod',
                   label='Time period',
                   values=periods.keys(),
                   description = filter_desc['speriod'],
                   help = filter_help['speriod']
                  )

# dropdown for choosing month of interest
@ct.input.dropdown('smon',
                   label='Month of interest',
                   values=months.keys(),
                   default='Annual',
                   description = filter_desc['smon'],
                   help = filter_help['smon']
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
@ct.output.livemap(click_on_feature=region_timeseries)
@ct.output.markdown()
# actual workflow calling the functions above
def workflow(speriod,smon,rcp,nuts_level):
    #mystat = allstats[statistic]
    myrcp = allscens[rcp]
    myperiod = periods[speriod]
    mymonth = months[smon]
    # find the stat name (dict key) belonging to this statistic (dict value)
    #myvar = [key for key in allstats if (allstats[key] == mystat)]
    myvar = var_gcm[mystat]


    #### STEP 1) retrieve data - reanalysis
    #### WHEN USING sis-agrometeorological-indicators: CALCULATION OF BEDD TO BE IMPLEMENTED
    #datarray_list = []
    #for y in range(period_hist[0],period_hist[1]+1):
    #    print(y)
    #    for m in range(1,13):
    #        datarray_m = retrieve_data(dataset_hist,
    #                                   variable = var_hist[0],
    #                                   statistics = var_hist[1],
    #                                   year = str(y),
    #                                   month=str(m).zfill(2)
    #                                   )
    #        datarray_m_sub = subselect_data(datarray_m, extent=europe_bb)
    #        #datarray_y_avg = avg_time(datarray_y_sub)
    #        # calculate number of days with minimum temperature below 0degC
    #        #datarray_y_avg = ct.cube.resample(datarray_y_sub,freq='month',how='sum')
    #        datarray_m_tot = count_days_threshold(datarray_m_sub, threshold=293.15, how="above")
    #        datarray_list.append(datarray_m_tot)
    #print('done the loop')
    #datarray = ct.cube.concat(datarray_list,dim='time')

    #### TEMPORARY IMPLEMENTATION: USE BEDD FROM ERA-INTERIM INSTEAD
    datarray_erai = retrieve_data(dataset_hist,
                                       origin = 'era_interim_reanalysis',
                                       variable = 'biologically_effective_degree_days',
                                       experiment = 'historical',
                                       temporal_aggregation = '10_day',
                                       period = '198101_201012',
                                       )
    datarray_erai_sub = subselect_data(datarray_erai, extent=europe_bb)
    datarray = ct.cube.resample(datarray_erai_sub,freq='month',how='sum')

    #### NORMAL CODE FROM HERE

    # calculate averages of reanalysis data over NUTS regions
    data_nuts_avg, data_non_nuts_avg = avg_nuts(datarray,nutslevel=nuts_level)


    #### STEP 2) calculate climatology of NUTS averages of reanalysis data
    # note climatologies are calculated of NUTS average data, and *not* the other way round
    # (i.e. calculate climatologies first, then average over regions)
    y0 = str(period_hist[0])
    y1 = str(period_hist[1])
    datarray_clim = ct.climate.climatology_mean(data_nuts_avg, start=y0,stop=y1,frequency='month')
    datarray_clim_sd = ct.climate.climatology_std(data_nuts_avg, start=y0,stop=y1,frequency='month')
    datarray_clim_pc = ct.climate.climatology_perc(data_nuts_avg,start=y0,stop=y1,
                                                   percentiles=[5., 95.],frequency='month')
    datarray_non_nuts_clim = ct.climate.climatology_mean(data_non_nuts_avg, start=y0,stop=y1,frequency='month')
    datarray_non_nuts_clim_sd = ct.climate.climatology_std(data_non_nuts_avg, start=y0,stop=y1,frequency='month')
    datarray_non_nuts_clim_pc = ct.climate.climatology_perc(data_non_nuts_avg,start=y0,stop=y1,
                                                   percentiles=[5., 95.],frequency='month')

    # collect climatology data
    data_nuts_clim = [datarray_clim, datarray_clim_sd,
                      datarray_clim_pc[0], datarray_clim_pc[1]]
    data_non_nuts_clim = [datarray_non_nuts_clim, datarray_non_nuts_clim_sd,
                      datarray_non_nuts_clim_pc[0], datarray_non_nuts_clim_pc[1]]


    #### STEP 3) retrieve GCM data - scenarios and historical period
    anom_list = []
    for gcm in allgcms: #### LOOP FROM HERE
        print(gcm)
        datarray_gcm = retrieve_data(dataset_scen,
                                     origin = gcm,
                                     variable = var_gcm[mystat],
                                     experiment = myrcp,
                                     temporal_aggregation = '10_day',
                                     period = myperiod
                                    )
        datarray_gcm_sub = subselect_data(datarray_gcm, extent=europe_bb)
        # calculate monthly totals
        datarray_gcm_mon = ct.cube.resample(datarray_gcm_sub, how='sum', freq='month')

        # corresponding data from historical period for this model
        datarray_hist = retrieve_data(dataset_scen,
                                     origin = gcm,
                                     variable = var_gcm[mystat],
                                     experiment = 'historical',        ####
                                     temporal_aggregation = '10_day',
                                     period = '198101_201012'          ####
                                    )
        datarray_hist_sub = subselect_data(datarray_hist, extent=europe_bb)
        # calculate monthly totals
        datarray_hist_mon = ct.cube.resample(datarray_hist_sub, how='sum', freq='month')


        #### STEP 4) calculate anomalies
        datarray_anom = calc_anom(datarray_gcm_mon, datarray_hist_mon)
        anom_list.append(datarray_anom)

    print('done the loop') #### LOOP UNTIL HERE

    anom_ens = ct.cube.concat(anom_list, "model")


    #### STEP 5) calculate ensemble statistics and calculate NUTS averages
    anom_ens_avg = ct.cube.average(anom_ens, dim='model')
    anom_ens_max = ct.cube.max(anom_ens, dim='model')
    anom_ens_min = ct.cube.min(anom_ens, dim='model')

    # calculate averages over nuts regions
    #anom_nuts_avg = avg_nuts(datarray_anom,nutslevel=nuts_level)
    anom_nuts_avg, anom_non_nuts_avg = avg_nuts(anom_ens_avg,nutslevel=nuts_level)
    anom_nuts_max, anom_non_nuts_max = avg_nuts(anom_ens_max,nutslevel=nuts_level)
    anom_nuts_min, anom_non_nuts_min = avg_nuts(anom_ens_min, nutslevel=nuts_level)

    # select month of interest
    if mymonth == 0:
        anom_nuts_avg_mon = ct.cube.resample(anom_nuts_avg, how='sum', freq='year')
        anom_nuts_max_mon = ct.cube.resample(anom_nuts_max, how='sum', freq='year')
        anom_nuts_min_mon = ct.cube.resample(anom_nuts_min, how='sum', freq='year')

        anom_non_nuts_avg_mon = ct.cube.resample(anom_non_nuts_avg, how='sum', freq='year')
        anom_non_nuts_max_mon = ct.cube.resample(anom_non_nuts_max, how='sum', freq='year')
        anom_non_nuts_min_mon = ct.cube.resample(anom_non_nuts_min, how='sum', freq='year')
    else:
        firstmonth, lastmonth = mymonth,mymonth
        anom_nuts_avg_mon = ct.climate.season_select(anom_nuts_avg, rule='month',
                                                     start=firstmonth, stop=lastmonth)
        anom_nuts_max_mon = ct.climate.season_select(anom_nuts_max, rule='month',
                                                     start=firstmonth, stop=lastmonth)
        anom_nuts_min_mon = ct.climate.season_select(anom_nuts_min, rule='month',
                                                     start=firstmonth, stop=lastmonth)

        anom_non_nuts_avg_mon = ct.climate.season_select(anom_non_nuts_avg, rule='month',
                                                     start=firstmonth, stop=lastmonth)
        anom_non_nuts_max_mon = ct.climate.season_select(anom_non_nuts_max, rule='month',
                                                     start=firstmonth, stop=lastmonth)
        anom_non_nuts_min_mon = ct.climate.season_select(anom_non_nuts_min, rule='month',
                                                     start=firstmonth, stop=lastmonth)

    # collect ens stats data
    anom_nuts_ens = [anom_nuts_avg_mon, anom_nuts_max_mon, anom_nuts_min_mon,
                     anom_non_nuts_avg_mon, anom_non_nuts_max_mon, anom_non_nuts_min_mon]

    # dummy layer for showing legend in livemap
    dummydata = ct.cube.index_select(anom_ens_avg-9999,time=mymonth)

    #### STEP 5) plot the averages
    livemap = plot_shapes(anom_nuts_ens,data_nuts_clim+data_non_nuts_clim,
                          var=myvar[0],exp=allscens[rcp],mon=mymonth,dummy=dummydata)

    args = {
        'rcp': rcp,
        'smon': smon,
        'nuts_level': nuts_level,
        'speriod': speriod,
    }
    query = get_query(args)
    permalink = f'[{LINK_TEXT}](?{query})'
    return livemap, permalink


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
