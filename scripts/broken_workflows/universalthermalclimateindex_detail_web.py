import cdstoolbox as ct
import calendar

##### Default options ----------------------------------

#BASE_URL = 'https://cds.climate.copernicus.eu/apps/136/c3s_434_universalthermalclimateindex_detail_web'
LINK_TEXT = '↪Permalink to this configuration'

NON_NUTS  = ['Kosovo', 'Bosnia and Herzegovina']
KOSOVO_ATTRIBUTES = {
    '_cds_toolbox_aux_wms_filters': "{'NAME_EN': ['Kosovo']}",
}
NON_KOSOVO = ', '.join('"{}"'.format(c) for c in NON_NUTS if c != 'Kosovo')
NON_KOSOVO_ATTRIBUTES = {
    '_cds_toolbox_aux_wms_filters': f"{{'NAME_EN': [{NON_KOSOVO}]}}",
}

color_style = 'blue_yellow_red_-40_100'

help_text = 'Hover over a region to display the value, click to display a time series.'
help_text_timeseries = 'Hover over the timeseries to display the values and the action buttons.'

indicator           = 'universal_thermal_climate_index'
dataset_name        = 'derived-utci-historical'
dataset_producttype = 'consolidated_dataset'

allnuts     = [0,1,2]
MONTH_NAMES = list(calendar.month_name)[1:]

allyears   = ['1979', '1980', '1981',
              '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990',
              '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999',
              '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008',
              '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017',
              '2018', '2019']
allmonths  = ['01', '02', '03', '04','05', '06', '07', '08','09', '10', '11', '12']
alldays    = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
              '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
              '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
retrieve_year_spacing = 10

#################################################################################################
# CHILD APPLICATION:
#################################################################################################
@ct.child(title='monthly average of selected month and region of all available years.', layout={'output_align':'left'})
@ct.output.markdown()
@ct.output.livefigure()
@ct.output.download(format = 'csv')

def nutsregion_timeseries(params, month, nutslevel):
    try:
        nuts_id = params['properties']['NUTS_ID']
        mask = ct.shapes.catalogue.nuts(level=nutslevel, nuts_id=nuts_id)
        shape_dim = 'nuts'
    except:
        name = params['properties']['name']
        mask = ct.shapes.catalogue.countries(name=name)
        shape_dim = 'countries'

    data_region_year_all = []
#    for syr in range(int(allyears[0]), int(allyears[-1]), retrieve_year_spacing):
#        loopyears = [str(yr) for yr in range(syr, syr+retrieve_year_spacing)]
    for loopyears in allyears:
        data_l = ct.catalogue.retrieve(
            dataset_name,
            {
                'product_type': dataset_producttype,
                'variable': indicator,
                'year' : loopyears,
                'month': month,
                'day'  : alldays,
                'grid': ['3','3'],
            }
        )

        data_loop = ct.cube.resample(data_l, freq='month', dim='time')
        data_loop_cel = ct.cdm.convert_units(data_loop, 'Celsius', 'K')
        data_region_loop_mean = ct.shapes.average(data_loop_cel, mask)
        data_region_year_all.append(data_region_loop_mean)


    data_region_year_all = ct.cube.concat(data_region_year_all, dim='time')
    data_region_year_all = ct.cube.average(data_region_year_all, dim=shape_dim)

    # Plot time series of regional monthly temperature
    fig_yearly = ct.chart.line(
        data_region_year_all,
        layout_kwargs = {
            'xaxis': {
                'title': 'Time (year)',
                'showline': True,
                'linecolor': '#000000',
                'showgrid': False,
                'gridcolor': '#c00013'
            },
            'yaxis': {
                'showline': True,
                'linecolor': '#000000',
                'showgrid': False,
                'gridcolor': '#c00013'
            }
        },
        scatter_kwargs = dict(
            hovertemplate=('%{x} %{y: .2f}' + "<extra></extra>"),
            showlegend=False
        )
    )

    #data_csv = ct.cdm.to_csv(data_region_year_all)
    return [help_text_timeseries, fig_yearly, data_region_year_all]

#################################################################################################

##### Functions ----------------------------------------

def retrieve_data_year(year, month):
    data = ct.catalogue.retrieve(
        dataset_name,
        {
            'product_type': dataset_producttype,
            'variable': indicator,
            'year': year,
            'month': month,
            'day': alldays,
            'grid': ['3','3'],
        }
    )
    return data

def plot_grid(layer, layer_non, dummy, var, clickkwargs):

    layer     = ct.cdm.update_attributes(layer,     {'cds_magics_style_name': color_style,})
    layer_non = ct.cdm.update_attributes(layer_non, {'cds_magics_style_name': color_style,})
    dummy     = ct.cdm.update_attributes(dummy,     {'cds_magics_style_name': color_style,})

    livemap_data = {
        'data': layer,
        'label': var,
        'label_template': '%{name} %{value:.2f}',
        'type':'layer',
        'zoom_to_selected': False,
        'checked':True,
        'click_kwargs': clickkwargs,
    }
    countries = ct.cdm.get_coordinates(layer_non)['countries']['data']
    kosovo_mask = layer_non - layer_non + [c=='KOS' for c in countries]
    non_kosovo_mask = layer_non - layer_non + [c!='KOS' for c in countries]
    kosovo = ct.cube.where(kosovo_mask, layer_non, drop=True)
    kosovo = ct.cdm.update_attributes(kosovo, KOSOVO_ATTRIBUTES)
    layer_non =  ct.cube.where(non_kosovo_mask, layer_non, drop=True)
    layer_non = ct.cdm.update_attributes(layer_non, NON_KOSOVO_ATTRIBUTES)
    livemap_data_non = {
        'data': layer_non,
        'label': var,
        'label_template': '%{NAME_EN} %{value:.2f}',
        'type':'layer',
        'zoom_to_selected': False,
        'checked':True,
        'click_kwargs': clickkwargs,
    }
    livemap_data_kosovo = {
        'data': kosovo,
        'label': var,
        'label_template': 'Kosovo (under UNSCR 1244/99) %{value:.2f}',
        'type':'layer',
        'zoom_to_selected': False,
        'checked':True,
        'click_kwargs': clickkwargs,
    }
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


    # plot the livemap
    fig = ct.livemap.plot([livemap_data, livemap_data_non, livemap_data_kosovo, uk_mask, legend_data, ], show_legend=True, crs='EPSG3857', min_zoom=3, zoom=3)
    return fig

##### Application --------------------------------------

#layout = ct.Layout(rows=5, justify='flex-start')
#layout.add_widget(row=0, content='year', xs=2, sm=2)
#layout.add_widget(row=0, content='month', xs=2, sm=2)
#layout.add_widget(row=0, content='nutslevel', xs=2, sm=2)
#layout.add_widget(1, "output-0")
#layout.add_widget(2, "output-1")
#layout.add_widget(3, "output-2")
#layout.add_widget(4, "output-3")
#layout.add_widget(2, "[child]", sm=4)

variables = ct.Layout(rows=4, justify='flex-start')
variables.add_widget(row=0, content='year', xs=2, sm=2)
variables.add_widget(row=0, content='month', xs=2, sm=2)
variables.add_widget(row=0, content='nutslevel', xs=2, sm=2)

app = ct.Layout(rows=4, justify='flex-start')
app.add_widget(row=0, content='output-0')
app.add_widget(row=1, content='output-1')
app.add_widget(row=2, content='output-2')
app.add_widget(row=3, content='output-3')

layout = ct.Layout(rows=2, justify='flex-start')
layout.add_widget(row=0, content=variables)
layout.add_widget(row=1, content=app)
layout.add_widget(row=1, content="[child]", sm=6)

@ct.application(title='Universal thermal climate index', layout=layout)

@ct.input.dropdown('year', label = 'Year of interest',
                   values=allyears,default=allyears[40],
                   description = 'Choose a year'
                  )
@ct.input.dropdown('month', label = 'Month of interest',
                   values=MONTH_NAMES,default=MONTH_NAMES[7],
                   description = 'Choose a month'
                  )
@ct.input.dropdown('nutslevel', label = 'Nuts level',
                   values=allnuts, default=allnuts[0],
                   description = 'Choose a NUTS level',
                   help = 'Select the size of the regions shown on the map, from largest (NUTS-0) to smallest (NUTS-2)',
                  )

# output widget
@ct.output.markdown()
@ct.output.livemap(click_on_feature=nutsregion_timeseries)
@ct.output.markdown()
@ct.output.download(format = 'geotiff')


#################################################################################################
# PARENT APPLICATION
#################################################################################################

def application(year, month, nutslevel):
    month_name = month
    month_number = MONTH_NAMES.index(month) + 1
    month = f"{month_number:02d}"
    # Define the arguments to pass to the child app
    child_kwargs = {
        'month'    : month,
        'nutslevel': nutslevel
    }

    print('retriev data for year ' + year)
    data = retrieve_data_year(year, month);
    print(data)
    data = ct.cdm.update_attributes(data,{})

    print('resample')
    data_year = ct.cube.resample(data, freq='year', dim='time')
    print(data_year)

    print('convert from K to Celsius')
    data_year_cel = ct.cdm.convert_units(data_year, 'Celsius', 'K')
    print(data_year_cel)

    print('average over nuts level', nutslevel)
    nuts = ct.shapes.catalogue.nuts(level = nutslevel)
    data_year_nuts = ct.shapes.average(data_year_cel, nuts)
    data_year_nuts1 = ct.cube.average(data_year_nuts, dim='time')
    print(data_year_nuts1)

    # add non-nuts regions
    nuts_non = ct.shapes.catalogue.countries(name=NON_NUTS)
    data_year_nuts_non = ct.shapes.average(data_year_cel, nuts_non)
    data_year_nuts_non1 = ct.cube.average(data_year_nuts_non, dim='time')
    print('average over non-nuts regions', data_year_nuts_non1)

    # dummy layer for showing legend in livemap
    dummydata = ct.cube.index_select(data_year_cel-999.99)
    print('dumyydata', dummydata)

    print('plot livemap')
    livemap = plot_grid(data_year_nuts1, data_year_nuts_non1, dummydata, indicator, child_kwargs)

    # create a permanent link with selected options
    args = {
        'year': year,
        'nutslevel': nutslevel,
        'month': month_name
    }
    query = get_query(args)
    permalink = f'[{LINK_TEXT}](?{query})'

    return [help_text, livemap, permalink, data_year_cel]


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
