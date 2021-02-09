const fs = require("fs");
const fse = require("fs-extra");
const config = require("./config");
const ejs = require("ejs");
const rimraf = require("rimraf");

const APP_URL =
  "https://cds.climate.copernicus.eu/workflows/c3s/%APP%/master/configuration.json?configuration_version=3.0";

// create output dir or empty output dir
if (!fs.existsSync(config.dev.outdir)) {
  fs.mkdirSync(config.dev.outdir);
} else {
  rimraf.sync(config.dev.outdir);

  if (!fs.existsSync(config.dev.outdir)) {
    fs.mkdirSync(config.dev.outdir);
  }
}

const srcPath = "./src";
const outputDir = config.dev.outdir;

const data_apps = JSON.parse(fs.readFileSync("./src/data_apps.json", "utf-8"));
const data_themes = JSON.parse(
  fs.readFileSync("./src/data_themes.json", "utf-8")
);
const data_overview = JSON.parse(
  fs.readFileSync("./src/data_overview.json", "utf-8")
);

Object.assign(data_themes, data_apps);

// copy assets to output dir
fse.copy(`${srcPath}/assets`, outputDir);

createAppPages(data_apps);

createThemePages(data_themes);

createOverviewPages(data_overview);

createIndexPage();

function createIndexPage() {
  ejs.renderFile(`${srcPath}/templates/index.ejs`, {}, (err, data) => {
    if (err) throw err;
    fs.writeFile(`${outputDir}/index.html`, data, (err) => {
      if (err) throw err;
      console.log(`index.html has been created.`);
    });
  });
}

function createOverviewPages(overview_data) {
  ejs.renderFile(
    `${srcPath}/templates/overview-list.ejs`,
    overview_data,
    (err, data) => {
      if (err) throw err;
      fs.writeFile(`${outputDir}/overview-list.html`, data, (err) => {
        if (err) throw err;
        console.log(`overview-list.html has been created.`);
      });
    }
  );
}

function createAppPages(data) {
  for (const index in data["datasets"]) {
    const dataset = data["datasets"][index];
    dataset.overview = APP_URL.replace("%APP%", dataset.overview);
    dataset.detail = APP_URL.replace("%APP%", dataset.detail);

    // theme directory
    if (!fs.existsSync(`${outputDir}/${dataset.theme.toLowerCase()}/`)) {
      fs.mkdirSync(`${outputDir}/${dataset.theme.toLowerCase()}/`);
    }

    createHTMLfiles(dataset);
  }
}

function overviewFileName(dataset, indicator = null) {
  let name = null;

  // URL override
  if (dataset.page_url) {
    name = dataset.page_url;
  } else {
    name = slugify(dataset.indicator_title);
  }

  if (indicator) {
    name += `--${slugify(indicator)}`;
  }
  name += ".html";
  return name;
}

function detailFileName(dataset, indicator = null) {
  let name = null;

  // URL override
  if (dataset.page_url) {
    name = dataset.page_url;
  } else {
    name = slugify(dataset.indicator_title);
  }

  if (indicator) {
    name += `--${slugify(indicator)}`;
  }
  name += "-detail.html";
  return name;
}

function slugify(string) {
  return string.toLowerCase().replace(/\s/g, "-").replace(/_/g, "-");
}

function createHTMLfiles(dataset) {
  //create overview and detail pages for each app
  if (!dataset.overview_var) {
    dataset.overview_var = null;
  }

  if (!dataset.detail_var) {
    dataset.detail_var = null;
  }

  dataset.overviewpage = overviewFileName(dataset);
  dataset.detailpage = detailFileName(dataset);
  dataset.indicator_title = dataset.indicator_title;

  // overview page
  let overviewFile = `${srcPath}/templates/overview.ejs`;

  ejs.renderFile(overviewFile, dataset, (err, data) => {
    if (err) throw err;
    fs.writeFile(
      `${outputDir}/${dataset.theme.toLowerCase()}/${dataset.overviewpage}`,
      data,
      (err) => {
        if (err) throw err;
        console.log(`${dataset.overviewpage} has been created.`);
      }
    );
  });

  // detail page
  ejs.renderFile(`${srcPath}/templates/detail.ejs`, dataset, (err, data) => {
    if (err) throw err;
    fs.writeFile(
      `${outputDir}/${dataset.theme.toLowerCase()}/${dataset.detailpage}`,
      data,
      (err) => {
        if (err) throw err;
        console.log(`${dataset.detailpage} has been created.`);
      }
    );
  });
}

function createThemePages(data) {
  //voor elk thema maken we een pagina aan
  for (const index in data["themes"]) {
    const theme = data["themes"][index];
    theme.apps = [];

    //verzamel actieve apps en voeg titel+links toe aan theme.apps[]
    for (const app_index in data["datasets"]) {
      const dataset = data["datasets"][app_index];

      if (
        theme.theme_title.toLowerCase() == dataset.theme.toLowerCase() &&
        !dataset.exclude
      ) {
        theme.apps.push({
          title: dataset.page_title,
          url: `${theme.theme_title.toLowerCase()}/${overviewFileName(
            dataset
          )}`,
        });
      }
    }

    // sort apps by title
    theme.apps.sort((a, b) => a.title.localeCompare(b.title));

    //render html
    ejs.renderFile(`${srcPath}/templates/theme.ejs`, theme, (err, data) => {
      if (err) throw err;
      const outputFile = `${theme.theme_title.toLowerCase()}.html`;
      fs.writeFile(`${outputDir}/${outputFile}`, data, (err) => {
        if (err) throw err;
        console.log(`${outputFile} has been created.`);
      });
    });
  }
}
