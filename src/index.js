const fs = require("fs");
const fse = require("fs-extra");
const config = require("./config");
const ejs = require("ejs");
const rimraf = require("rimraf");
const sync_request = require("sync-request");
const { StringDecoder } = require('string_decoder');
const marked = require('marked')

const decoder = new StringDecoder('utf8')

// create output dir or empty output dir
try{
  if (!fs.existsSync(config.dev.outdir)) {
    fs.mkdirSync(config.dev.outdir);
  } else {
    rimraf.sync(config.dev.outdir);

    if (!fs.existsSync(config.dev.outdir)) {
      fs.mkdirSync(config.dev.outdir);
    }
  }
} catch (error) {
  console.error("Outdir prep error:", error);
}

const srcPath = config.dev.source;
const outputDir = config.dev.outdir;

//load data files.
const data_apps = JSON.parse(
  fs.readFileSync(config.dev.data_apps, "utf-8")
);
const data_themes = JSON.parse(
  fs.readFileSync(config.dev.data_themes, "utf-8")
);
const data_overview = JSON.parse(
  fs.readFileSync(config.dev.data_overview, "utf-8")
);


//retrieve indicator texts from github.
let data_git_json;
let git_json_result = sync_request('GET', config.url.git_json);

if(git_json_result.statusCode === 200){
  data_git_json = JSON.parse(decoder.write(git_json_result.body));
  fs.writeFileSync("./data/git_data.json", JSON.stringify(data_git_json, null, 2));
}


// Add data_apps to data_themes & data_overview
Object.assign(data_themes, data_apps);
Object.assign(data_overview, data_apps);

// copy assets to output dir
fse.copy(`${srcPath}/assets`, outputDir);

//generate all pages
createAppPages(data_apps);

createThemePages(data_themes);

createOverviewPage(data_overview);

createIndexPage();

fs.writeFileSync("./data/data_apps_output.json", JSON.stringify(data_apps, null, 2));


function createIndexPage() {
  ejs.renderFile(`${srcPath}/templates/index.ejs`, {}, (err, data) => {
    if (err) throw err;
    fs.writeFile(`${outputDir}/index.html`, data, (err) => {
      if (err) throw err;
      console.log(`index.html has been created.`);
    });
  });
}

function createOverviewPage(overview_data) {
  let hazard_list = {};
  
  for (const index in overview_data["datasets"]) {
    const dataset = overview_data["datasets"][index];
    
    if(dataset["exclude"]) continue;

    if(!hazard_list.hasOwnProperty(dataset["hazard_category"])){
      hazard_list[dataset["hazard_category"]] = {};
    }
    
    for(const index in dataset["hazards"]){
      const hazard = dataset["hazards"][index];

      if(!hazard_list[dataset["hazard_category"]].hasOwnProperty(hazard)){
        hazard_list[dataset["hazard_category"]][hazard] = [];
      }

      hazard_list[dataset["hazard_category"]][hazard].push({
        "title": dataset.page_title,
        "url": dataset.theme.toLowerCase() + '/' + overviewFileName(dataset)
      });
    } 
  }
  // console.log(hazard_list);
  // process.exit();

  overview_data.hazard_list = hazard_list;

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

    dataset.overview = config.url.toolbox_app.replace("%APP%", dataset.overview);
    dataset.detail = config.url.toolbox_app.replace("%APP%", dataset.detail);

    // theme directory
    if (!fs.existsSync(`${outputDir}/${dataset.theme.toLowerCase()}/`)) {
      fs.mkdirSync(`${outputDir}/${dataset.theme.toLowerCase()}/`);
    }

    createHTMLfiles(dataset);
  }
}

function overviewFileName(dataset) {
  let name = null;

  // URL override
  if (dataset.page_url) {
    name = dataset.page_url;
  } else {
    name = slugify(dataset.indicator_title);
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

function slugify(string, lowercase = true, separator = '-') {
  if(lowercase){
    return string.toLowerCase().replace(/\s/g, separator).replace(/_/g, separator);
  } else {
    return string.replace(/\s/g, separator).replace(/_/g, separator);
  }
}

function createHTMLfiles(dataset) {
  //create overview and detail pages for each app
  if (!dataset.overview_var) {
    dataset.overview_var = null;
  }

  if (!dataset.detail_var) {
    dataset.detail_var = null;
  }

  //maak filenames voor dat we de git detail laden.
  dataset.overviewpage = overviewFileName(dataset);
  dataset.detailpage = detailFileName(dataset);


  if(config.usage.markdown_texts){
    // Gather github markdown texts by title. Convert them to HTML, and separate the different parts.
    let github_page_title = dataset.page_title_github ? dataset.page_title_github : dataset.page_title;
    let url = config.url.git_md.replace('%TITLE%', slugify(github_page_title, false, '_'));
    let result = sync_request('GET', url);

    if(result.statusCode === 200){
      let git_body_text = marked(decoder.write(result.body)).split(/\r?\n/);

      let main = git_body_text.findIndex((line) => line.includes('<h2 id="main">Main</h2>'));
      let main_end = git_body_text.findIndex((line, index) => index > main && line.includes('<table>'));

      let explore = git_body_text.findIndex((line) => line.includes('<h2 id="explore">Explore</h2>'));
      let explore_end = git_body_text.findIndex((line,index) => index > explore && (line.includes('<h3')|| line.includes('<table>')));

      if(explore_end < 0) explore_end = git_body_text.length;

      //set the overview and detail description.
      dataset.description = git_body_text.slice(main + 1, main_end).join('\n').trim();
      dataset.description_detail = git_body_text.slice(explore + 1, explore_end).join('\n').trim();

      // console.log(url, main_text, explore_text);
    } else {
      console.error('Text not found:', url);
    }
  } else if(data_git_json){
    let git_consolidated_data = false;
    try{
      git_consolidated_data = data_git_json.find(element => element.hasOwnProperty(dataset.identifier))[dataset.identifier];
    } catch (error) {
      console.error(error);
    }

    if(git_consolidated_data){
      dataset.page_title = git_consolidated_data.PageTitle;
      dataset.description = marked(git_consolidated_data.ConsolidatedText_Main);
      dataset.description_detail = marked(git_consolidated_data.ConsolidatedText_Explore);
      dataset.indicator_title = git_consolidated_data.Indicator;
      dataset.units = git_consolidated_data.Units;
    }

  }

  dataset.vars = dataset.vars || { "detail": {}, "overview": {} };

  ejs.renderFile(`${srcPath}/templates/overview.ejs`, dataset, (err, data) => {
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
