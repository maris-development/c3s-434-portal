const fs = require("fs");
const fse = require("fs-extra");
const config = require("./config");
const ejs = require('ejs')

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

// copy assets to output dir
fse.copy(`${srcPath}/assets`, outputDir)

createThemePages(data);

for (const index in data["datasets"]) {
    const dataset = data["datasets"][index]
    // createAppPages(dataset)
}

ejs.renderFile(`${srcPath}/templates/index.ejs`, {}, (err, data) => {
    if (err) throw (err);
    fs.writeFile(`${outputDir}/index.html`, data, (err) => {
        if (err) throw (err);
        console.log(`index.html has been created.`);
    })
})

function createAppPages(dataset) {
    ejs.renderFile(`${srcPath}/templates/overview.ejs`, dataset, (err, data) => {
        if (err) throw (err);
        fs.mkdirSync(`${outputDir}/${dataset.theme}/`)
        fs.writeFile(`${outputDir}/${dataset.theme}/${dataset.title}.html`, data, (err) => {
            if (err) throw (err);
            console.log(`${dataset.title}.html has been created.`);
        })
    })
}


function createThemePages(data) {
    for (const index in data["themes"]) {
        const theme = data["themes"][index]
        theme.apps = []

        for (const indexApp in data["datasets"]) {
            const dataset = data["datasets"][indexApp]

            if (theme.title.localeCompare(dataset.theme)) {

                //TODO create correct url
                theme.apps.push({
                    "title": dataset.title,
                    "url": `${(theme.title).toLowerCase()}/todo.html`
                })
            }
        }

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