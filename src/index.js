const fs = require("fs");
const fse = require("fs-extra");
const config = require("./config");
const ejs = require('ejs')

const APP_URL = "https://cds.climate.copernicus.eu/workflows/c3s/%APP%/master/configuration.json?configuration_version=3.0";

// create output dir or empty output dir
if (!fs.existsSync(config.dev.outdir)) {
    fs.mkdirSync(config.dev.outdir);
} else {
    fs.rmdirSync(config.dev.outdir, { recursive: true });
    if (!fs.existsSync(config.dev.outdir)) {
        fs.mkdirSync(config.dev.outdir);
    }
}

const srcPath = './src'
const outputDir = config.dev.outdir;

const data = JSON.parse(fs.readFileSync("./src/data.json", "utf-8"));
const metadata = JSON.parse(fs.readFileSync("./src/ClimateAdapt_434-dataset-metadata.json", "utf-8"))

// copy assets to output dir
fse.copy(`${srcPath}/assets`, outputDir)


createAppPages(data, metadata);

createThemePages(data);

ejs.renderFile(`${srcPath}/templates/index.ejs`, {}, (err, data) => {
    if (err) throw (err);
    fs.writeFile(`${outputDir}/index.html`, data, (err) => {
        if (err) throw (err);
        console.log(`index.html has been created.`);
    })
})

function createAppPages(data, metadata) {

    for (const index in data["datasets"]) {
        const dataset = data["datasets"][index];
        dataset.overview = APP_URL.replace("%APP%", dataset.overview);
        dataset.detail = APP_URL.replace("%APP%", dataset.detail);

        metadata["datasets"].forEach(datasetMetadata => {
            if (dataset["dataset"] !== undefined && dataset["dataset"] == datasetMetadata["dataset_details"]["dataset_hist"]) {
                dataset.description = datasetMetadata["dataset_details"]["dataset_cds_overview"];
                dataset.metadata = datasetMetadata;
                return;
            }
        });

        // theme directory
        if (!fs.existsSync(`${outputDir}/${(dataset.theme).toLowerCase()}/`)) {
            fs.mkdirSync(`${outputDir}/${(dataset.theme).toLowerCase()}/`)
        }

        // console.log(dataset.indicators)

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
    let name = slugify(dataset.title)
    if (indicator) {
        name += `--${slugify(indicator)}`
    }
    name += ".html"
    return name
}

function detailFileName(dataset, indicator = null) {
    let name = slugify(dataset.title)
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
    dataset.overview_var = null
    dataset.detail_var = null
    if (indicator) {
        dataset.overviewpage = overviewFileName(dataset, indicator.title);
        dataset.detailpage = detailFileName(dataset, indicator.title);
        dataset.pagetitle = dataset.title + " - " + indicator.title
        dataset.overview_var = indicator.overview_var
        dataset.detail_var = indicator.detail_var
    
    } else {
        dataset.overviewpage = overviewFileName(dataset);
        dataset.detailpage = detailFileName(dataset);
        dataset.pagetitle = dataset.title

    }


    // overview page
    ejs.renderFile(`${srcPath}/templates/overview.ejs`, dataset, (err, data) => {
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
        // console.log(theme)
        theme.apps = []

        for (const indexApp in data["datasets"]) {
            const dataset = data["datasets"][indexApp]
            if (theme.title.toLowerCase() == dataset.theme.toLowerCase() && !dataset.exclude) {
                if (dataset.indicators !== undefined) {
                    dataset.indicators.forEach(indicator => {
                        theme.apps.push({
                            "title": dataset.title + " - " + indicator.title,
                            "url": `${(theme.title).toLowerCase()}/${overviewFileName(dataset, indicator.title)}`
                        })

                    });
                } else {
                    theme.apps.push({
                        "title": dataset.title,
                        "url": `${(theme.title).toLowerCase()}/${overviewFileName(dataset)}`
                    })
                }
            }
        }
        theme.apps.sort((a, b) => a.title.localeCompare(b.title));
        // console.log(theme.apps)

        ejs.renderFile(`${srcPath}/templates/theme.ejs`, theme, (err, data) => {
            if (err) throw (err);
            const outputFile = `${(theme.title).toLowerCase()}.html`
            fs.writeFile(`${outputDir}/${outputFile}`, data, (err) => {
                if (err) throw (err);
                console.log(`${outputFile} has been created.`);
            })
        })
    }
}