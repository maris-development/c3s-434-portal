const fs = require("fs");
const fse = require("fs-extra");
const config = require("./config");
const ejs = require('ejs')
const rimraf = require('rimraf');

const APP_URL = "https://cds.climate.copernicus.eu/workflows/c3s/%APP%/master/configuration.json?configuration_version=3.0";

// create output dir or empty output dir
if (!fs.existsSync(config.dev.outdir)) {
    fs.mkdirSync(config.dev.outdir);

} else {
    rimraf.sync(config.dev.outdir);

    if (!fs.existsSync(config.dev.outdir)) {
        fs.mkdirSync(config.dev.outdir);
    }
}

const srcPath = './src'
const outputDir = config.dev.outdir;

const data_apps = JSON.parse(fs.readFileSync("./src/data_apps.json", "utf-8"));
const data_themes = JSON.parse(fs.readFileSync("./src/data_themes.json", "utf-8"));
const data_overview = JSON.parse(fs.readFileSync("./src/data_overview.json", "utf-8"));

Object.assign(data_themes, data_apps); 

// copy assets to output dir
fse.copy(`${srcPath}/assets`, outputDir);

createAppPages(data_apps);

createThemePages(data_themes);

createOverviewPages(data_overview);

createIndexPage();

function createIndexPage(){
    ejs.renderFile(`${srcPath}/templates/index.ejs`, {}, (err, data) => {
        if (err) throw (err);
        fs.writeFile(`${outputDir}/index.html`, data, (err) => {
            if (err) throw (err);
            console.log(`index.html has been created.`);
        })
    });
}

function createOverviewPages(overview_data){
    ejs.renderFile(`${srcPath}/templates/overview-list.ejs`, overview_data, (err, data) => {
        if (err) throw (err);
        fs.writeFile(`${outputDir}/overview-list.html`, data, (err) => {
            if (err) throw (err);
            console.log(`overview-list.html has been created.`);
        })
    })
}

function createAppPages(data) {
    for (const index in data["datasets"]) {
        const dataset = data["datasets"][index];
        dataset.overview = APP_URL.replace("%APP%", dataset.overview);
        dataset.detail = APP_URL.replace("%APP%", dataset.detail);

        // theme directory
        if (!fs.existsSync(`${outputDir}/${(dataset.theme).toLowerCase()}/`)) {
            fs.mkdirSync(`${outputDir}/${(dataset.theme).toLowerCase()}/`)
        }

        if (dataset.indicators !== undefined) {
            dataset.indicators.forEach(indicator => {
                createHTMLfiles(dataset, indicator)
            });
        } else {
            createHTMLfiles(dataset)
        }
    }
}

function overviewFileName(dataset, indicator = null) {
    let name = null

    // URL override
    if (dataset.page_url) {
        name = dataset.page_url
    } else {
        name = slugify(dataset.indicator_title)
    }

    if (indicator) {
        name += `--${slugify(indicator)}`
    }
    name += ".html"
    return name
}

function detailFileName(dataset, indicator = null) {
    let name = null

    // URL override
    if (dataset.page_url) {
        name = dataset.page_url
    } else {
        name = slugify(dataset.indicator_title)
    }

    if (indicator) {
        name += `--${slugify(indicator)}`
    }
    name += "-detail.html"
    return name
}

function slugify(string) {
    return string.toLowerCase().replace(/\s/g, "-").replace(/_/g, "-")
}

function createHTMLfiles(dataset, indicator = null) {
    if (!dataset.overview_var){
        dataset.overview_var = null
    }
    
    if (!dataset.detail_var){
        dataset.detail_var = null;
    }

    if (indicator) {

        dataset.overviewpage = overviewFileName(dataset, indicator.name);
        dataset.detailpage = detailFileName(dataset, indicator.name);
        dataset.description_detail = indicator.description_detail
        dataset.page_title = indicator.page_title
        dataset.indicator_title = indicator.indicator_title
        dataset.description = indicator.description
        dataset.overview_var = indicator.overview_var
        dataset.detail_var = indicator.detail_var

    } else {
        
        dataset.overviewpage = overviewFileName(dataset);
        dataset.detailpage = detailFileName(dataset);
        dataset.indicator_title = dataset.indicator_title
        
    }

    // overview page
    let overviewFile = `${srcPath}/templates/overview.ejs`

    ejs.renderFile(overviewFile, dataset, (err, data) => {
        if (err) throw (err);
        fs.writeFile(`${outputDir}/${(dataset.theme).toLowerCase()}/${dataset.overviewpage}`, data, (err) => {
            if (err) throw (err);
            console.log(`${dataset.overviewpage} has been created.`);
        })
    })

    // detail page
    ejs.renderFile(`${srcPath}/templates/detail.ejs`, dataset, (err, data) => {
        if (err) throw (err);
        fs.writeFile(`${outputDir}/${(dataset.theme).toLowerCase()}/${dataset.detailpage}`, data, (err) => {
            if (err) throw (err);
            console.log(`${dataset.detailpage} has been created.`);
        })
    })
}


function createThemePages(data) {
    for (const index in data["themes"]) {
        const theme = data["themes"][index]
        theme.apps = []

        for (const indexApp in data["datasets"]) {
            const dataset = data["datasets"][indexApp]
            if (theme.theme_title.toLowerCase() == dataset.theme.toLowerCase() && !dataset.exclude) {
                if (dataset.indicators !== undefined) {
                    dataset.indicators.forEach(indicator => {
                        theme.apps.push({
                            "title": indicator.indicator_title,
                            "url": `${(theme.theme_title).toLowerCase()}/${overviewFileName(dataset, indicator.name)}`
                        })

                    });
                } else {
                    theme.apps.push({
                        "title": dataset.page_title,
                        "url": `${(theme.theme_title).toLowerCase()}/${overviewFileName(dataset)}`
                    })
                }
            }
        }

        // sort apps by title
        theme.apps.sort((a, b) => a.title.localeCompare(b.title));

        ejs.renderFile(`${srcPath}/templates/theme.ejs`, theme, (err, data) => {
            if (err) throw (err);
            const outputFile = `${(theme.theme_title).toLowerCase()}.html`
            fs.writeFile(`${outputDir}/${outputFile}`, data, (err) => {
                if (err) throw (err);
                console.log(`${outputFile} has been created.`);
            })
        })
    }
}