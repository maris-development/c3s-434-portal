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
                // console.log("found")
                // console.log(datasetMetadata)
                dataset.description = datasetMetadata["dataset_details"]["dataset_cds_overview"];
            }
        });

        // theme directory
        if (!fs.existsSync(`${outputDir}/${(dataset.theme).toLowerCase()}/`)) {
            fs.mkdirSync(`${outputDir}/${(dataset.theme).toLowerCase()}/`)
        }

        const overviewFile = `${(dataset.title).toLowerCase().replace(/\s/g, "-")}.html`
        const detailFile = `${(dataset.title).toLowerCase().replace(/\s/g, "-")}-detail.html`

        dataset.overviewpage = overviewFile;
        dataset.detailpage = detailFile;

        // overview page
        ejs.renderFile(`${srcPath}/templates/overview.ejs`, dataset, (err, data) => {
            if (err) throw (err);
            fs.writeFile(`${outputDir}/${(dataset.theme).toLowerCase()}/${overviewFile}`, data, (err) => {
                if (err) throw (err);
                console.log(`${overviewFile} has been created.`);
            })
        })

        // detail page
        ejs.renderFile(`${srcPath}/templates/detail.ejs`, dataset, (err, data) => {
            if (err) throw (err);
            fs.writeFile(`${outputDir}/${(dataset.theme).toLowerCase()}/${detailFile}`, data, (err) => {
                if (err) throw (err);
                console.log(`${detailFile} has been created.`);
            })
        })
    }
}


function createThemePages(data) {
    for (const index in data["themes"]) {
        const theme = data["themes"][index]
        console.log(theme)
        theme.apps = []

        for (const indexApp in data["datasets"]) {
            const dataset = data["datasets"][indexApp]
            if (theme.title.toLowerCase() == dataset.theme.toLowerCase() && !dataset.exclude) {

                //TODO create correct url
                theme.apps.push({
                    "title": dataset.title,
                    "url": `${(theme.title).toLowerCase()}/${dataset.overviewpage}`
                })
            }
        }
        console.log(theme.apps)

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