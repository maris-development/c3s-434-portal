# C3s.maris.nl handover to EEA

There are several sources to collect page information from.
 - This repository (MARIS B.V, contains HTML generator (uses Node, Yarn, Embedded JS))
 - [A consolidated json, compiled after the meeting on Monday morning April 19th](https://github.com/maris-development/c3s-434-portal/blob/static-generator/data/data_consolidated.json).
 - [Cedadev C3S 434 Page Text Github](https://github.com/cedadev/c3s_434_ecde_page_text)

# C3S.maris.nl consolidated JSON

Location: `./data/data_consolidated.json` \
The data in this JSON is compiled from different sources in the C3S 434 project. The page texts are converted to HTML, and the JSON uses correct key-value pairs where the key is the C3S_434 identifier. This JSON contains the following:
- Indicator data  (`./data/data_apps.json` + git markdown texts to HTML)
- Theme page data  (`./data/data_themes.json`)
- Overview list page data  (`./data/data_overview.json`)
- HTML page texts (e.g. Disclaimer) (`./data/data_html_pages.json`)
- Git Markdown data (`./data/git_data.json`) (retrieved from [cedadev github](https://github.com/cedadev/c3s_434_ecde_page_text/blob/main/content/json/Consolidated.json))

All of them are combined in index.js, and form **./data/data_consolidated.json**

# C3S.maris.nl generator Script

[Located in static-generator branch of this repository.](https://github.com/maris-development/c3s-434-portal/tree/static-generator)

Requirements:  
- NodeJS (min v12)
- Yarn  
  
`yarn install` Install dependencies \
`yarn dev` autogenerate pages on source update \
`yarn build` generate pages manually 

`src` contains templates, data and generator script \
`public` contains de generated HTML pages \
`data` contains the JSON data for generating the website (Texts & titles from Cedadev github repo)
  

# Landing page (Sections)

More or less completely static HTML, template source can be found in `/src/templates/index.ejs`

### Disclaimer

A separate page is created for a disclaimer, with the data under key `"html_pages"` in the consolidated JSON. 
On the landing page we show a summarized text and link to this disclaimer.

# Overview list page

The overview list is generated from the indicator list (consolidated JSON > `"indicators"`), and is stored as JSON in the consolidated JSON under key `"overview_page"`.

### JSON data 

The overviewlist is ordered by category and hazard type, using the arrays defined in the JSON.

```jsonc
{
  ...
  "overview_page": {
    // Page description
    "description": "HTML page descrption.",
    // Arrays to keep track of order
    "category_order": [ "Heat and cold", "Wet and dry",  "Wind", "Snow and ice",  "Coastal", "Oceanic", "Other" ],
    "hazard_type_order": [
      [ "Mean temperature", "Extreme heat", "Cold spells and frost" ],
      [ "Mean precipitation", "Extreme precipitation", "River flooding", "Aridity", "Drought", "Wildfire" ],
      [ "Mean wind speed", "Severe windstorm" ],
      [ "Snow and land ice" ],
      [ "Relative sea level", "Coastal flooding" ],
      [ "Ocean temperature", "Biochemical ocean properties" ]
    ],
    // Generated list of inicators.
    "hazard_list": {
      "Heat and cold": {
        "Extreme heat": [
          {
            "title": "Monthly statistics for daily maximum temperature, 2011-2099",
            "url": "agriculture/average-maximum-temperature.html"
          },
          ...
        ],
        ...
      },
      ...
    }
  },
  ...
}
```

### Link to disclaimer

On the overview list page, we link to the disclaimer, just like the landing page.

# Theme pages

A theme page is used to collect multiple climate adapt applications together, it's the step between the landing page and the app page.

### JSON data 

The theme page contents are stored in the consolidated JSON under the key `"themes"`.

```jsonc 
{
  ...
  "themes": {
    "health": {
      "theme_title": "Health",
      "description": "Climate change ... and air quality.",
      //links to the climate adapt overview application HTML pages, with their titles.
      "apps": [
        {
          "title": "Climatic suitability for the tiger mosquito - season length, 1971-2099",
          "url": "health/climatic-suitability-of-tiger-mosquito--season-length.html"
        },
        ...
      ]
    },
    ...
  },
  ...
}
```


# Climate Adapt Application pages

A Climate Adapt overview application consists of two pages that form a pair. One indicator has an 'overview' app and a 'detail' app. Both pages have their own embeds & page content which differ from each other.

### JSON data 

The climate adapt application page contents are stored in the consolidated JSON under the key `"indicators"`.

```jsonc 
{
  "indicators": {
    "C3S_434_013": {
      // Overview page description
      "description": "Overview description",
      // Detail page description
      "description_detail": "Detail description",
      // App title above the embed:
      "indicator_title": "Projected change in the monthly average of Daily Maximum Temperature",  
      // Page title 
      "page_title": "Monthly statistics for daily maximum temperature, 2011-2099",
      // Indicator page
      "theme": "Agriculture",
      // Internal identifier
      "identifier": "C3S_434_013",
      // Detail embed config URL
      "detail": "https://cds.climate.copernicus.eu/workflows/c3s/hidden-app-agriculture-tmax-detail-web/master/configuration.json?configuration_version=3.0",
      // Overview embed config URL
      "overview": "https://cds.climate.copernicus.eu/workflows/c3s/hidden-app-agriculture-tmax-overview-web/master/configuration.json?configuration_version=3.0",
      // Basic page url, we use this to generate page-url.html and page-url-detail.html
      "page_url": "average-maximum-temperature",
      // Hazard category (for automatic generation of the Overview List page)
      "hazard_category": "Heat and cold",
      // Hazards (for automatic generation of the Overview List page) (Could be multiple in the past)
      "hazards": [
        "Extreme heat"
      ],
      //page URLs created with the "page_url" parameter. It can occur that page_url does not exist, then we convert the page_title to a URL compatible string.
      "overviewpage": "average-maximum-temperature.html",
      "detailpage": "average-maximum-temperature-detail.html",
      // Unused (comes from cedadev github, don't know why)
      "units": "(°C)",
      // Extra workflow parameters, for the detail and overview pages respectively
      "vars": {
        "detail": {},
        "overview": {}
      }
    },
    ...
  },
  ...
}
```

### Embed code

```html
<!-- HTML, toolbox app fills the element with id="toolbox-app" -->
<div class="t-ct">
    <div id="toolbox-app">
        <div class="pre-app-loading">
            <img src="https://cds.climate.copernicus.eu/toolbox/assets/spinner.svg" alt="Loading">
            <div>
                Loading indicator...
            </div>
        </div>
    </div>
</div>

<!-- Needed for the toolbox to function correctly -->
<script type="text/javascript">
    window.cds_toolbox = { 
        cds_public_path: 'https://cds.climate.copernicus.eu/toolbox/' 
    };
</script>

<!-- Make sure to always use an up-to-date version of the toolbox -->
<script type="text/javascript"
    src="https://cds.climate.copernicus.eu/toolbox/toolbox-4.23.1.js"></script>

<!-- WORKFLOW contains the URL to the configuration for the embed -->
<!-- WORKFLOWPARAMS contains the extra parameter(s) to pass to the workflow/indicator app -->
<script type="text/javascript">
const WORKFLOW = 'https://cds.climate.copernicus.eu/workflows/c3s/hidden-app-health-mosquito-detail-web/master/configuration.json?configuration_version=3.0';
const WORKFLOWPARAMS = {"indicator":"Length of season"};

(function () {
    document.addEventListener('DOMContentLoaded', function () {
        window.cds_toolbox.runApp(
            'toolbox-app', // ID to attach to
            WORKFLOW, 
            {
                workflowParams: WORKFLOWPARAMS,
            }
        );
    }, false);
}) ();
</script>
```

### Texts from GitHub

The markdown texts are collected from the [cedadev Consolidated.json on github](https://raw.githubusercontent.com/cedadev/c3s_434_ecde_page_text/main/content/json/Consolidated.json).

### Link to disclaimer

On the Climate Adapt app page, we link to the disclaimer, just like the landing page.
