"use strict";

var fs = require("fs");

var fse = require("fs-extra");

var config = require("./config");

var ejs = require("ejs");

var rimraf = require("rimraf");

var sync_request = require("sync-request");

var _require = require('string_decoder'),
    StringDecoder = _require.StringDecoder;

var marked = require('marked');

var decoder = new StringDecoder('utf8'); // create output dir or empty output dir

try {
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

var srcPath = config.dev.source;
var outputDir = config.dev.outdir; //load data files.

var data_apps = JSON.parse(fs.readFileSync(config.dev.data_apps, "utf-8"));
var data_themes = JSON.parse(fs.readFileSync(config.dev.data_themes, "utf-8"));
var data_overview = JSON.parse(fs.readFileSync(config.dev.data_overview, "utf-8")); //retrieve indicator texts from github.

var data_git_json;
var git_json_result = sync_request('GET', config.url.git_json);

if (git_json_result.statusCode === 200) {
  data_git_json = JSON.parse(decoder.write(git_json_result.body));
  fs.writeFileSync("./data/git_data.json", JSON.stringify(data_git_json, null, 2));
} // copy assets to output dir


fse.copy("".concat(srcPath, "/assets"), outputDir); //generate all pages

createAppPages(data_apps); // Add data_apps to data_themes & data_overview

Object.assign(data_themes, data_apps);
createThemePages(data_themes); // Add data_apps to data_themes & data_overview

Object.assign(data_overview, data_apps);
createOverviewPage(data_overview);
createIndexPage(); // Add all data to data_apps

Object.assign(data_apps, data_themes, data_overview);
fs.writeFileSync("./data/data_consolidated.json", JSON.stringify(data_apps, null, 2));

function createIndexPage() {
  ejs.renderFile("".concat(srcPath, "/templates/index.ejs"), {}, function (err, data) {
    if (err) throw err;
    fs.writeFile("".concat(outputDir, "/index.html"), data, function (err) {
      if (err) throw err;
      console.log("index.html has been created.");
    });
  });
}

function createOverviewPage(overview_data) {
  var hazard_list = {};

  for (var index in overview_data["datasets"]) {
    var dataset = overview_data["datasets"][index];
    if (dataset["exclude"]) continue;

    if (!hazard_list.hasOwnProperty(dataset["hazard_category"])) {
      hazard_list[dataset["hazard_category"]] = {};
    }

    for (var _index in dataset["hazards"]) {
      var hazard = dataset["hazards"][_index];

      if (!hazard_list[dataset["hazard_category"]].hasOwnProperty(hazard)) {
        hazard_list[dataset["hazard_category"]][hazard] = [];
      }

      hazard_list[dataset["hazard_category"]][hazard].push({
        "title": dataset.page_title,
        "url": dataset.theme.toLowerCase() + '/' + overviewFileName(dataset)
      });
    }
  } // console.log(hazard_list);
  // process.exit();


  overview_data.hazard_list = hazard_list;
  ejs.renderFile("".concat(srcPath, "/templates/overview-list.ejs"), overview_data, function (err, data) {
    if (err) throw err;
    fs.writeFile("".concat(outputDir, "/overview-list.html"), data, function (err) {
      if (err) throw err;
      console.log("overview-list.html has been created.");
    });
  });
}

function createAppPages(data) {
  for (var index in data["datasets"]) {
    var dataset = data["datasets"][index];
    dataset.overview = config.url.toolbox_app.replace("%APP%", dataset.overview);
    dataset.detail = config.url.toolbox_app.replace("%APP%", dataset.detail); // theme directory

    if (!fs.existsSync("".concat(outputDir, "/").concat(dataset.theme.toLowerCase(), "/"))) {
      fs.mkdirSync("".concat(outputDir, "/").concat(dataset.theme.toLowerCase(), "/"));
    }

    createHTMLfiles(dataset);
  }
}

function overviewFileName(dataset) {
  var name = null; // URL override

  if (dataset.page_url) {
    name = dataset.page_url;
  } else {
    name = slugify(dataset.indicator_title);
  }

  name += ".html";
  return name;
}

function detailFileName(dataset) {
  var indicator = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
  var name = null; // URL override

  if (dataset.page_url) {
    name = dataset.page_url;
  } else {
    name = slugify(dataset.indicator_title);
  }

  if (indicator) {
    name += "--".concat(slugify(indicator));
  }

  name += "-detail.html";
  return name;
}

function slugify(string) {
  var lowercase = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;
  var separator = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '-';

  if (lowercase) {
    return string.toLowerCase().replace(/\s/g, separator).replace(/_/g, separator);
  } else {
    return string.replace(/\s/g, separator).replace(/_/g, separator);
  }
}

function createHTMLfiles(dataset) {
  //create overview and detail pages for each app
  // if (!dataset.overview_var) {
  //   dataset.overview_var = null;
  // }
  // if (!dataset.detail_var) {
  //   dataset.detail_var = null;
  // }
  //maak filenames voor dat we de git detail laden.
  dataset.overviewpage = overviewFileName(dataset);
  dataset.detailpage = detailFileName(dataset);

  if (config.usage.markdown_texts) {
    // Gather github markdown texts by title. Convert them to HTML, and separate the different parts.
    var github_page_title = dataset.page_title_github ? dataset.page_title_github : dataset.page_title;
    var url = config.url.git_md.replace('%TITLE%', slugify(github_page_title, false, '_'));
    var result = sync_request('GET', url);

    if (result.statusCode === 200) {
      var git_body_text = marked(decoder.write(result.body)).split(/\r?\n/);
      var main = git_body_text.findIndex(function (line) {
        return line.includes('<h2 id="main">Main</h2>');
      });
      var main_end = git_body_text.findIndex(function (line, index) {
        return index > main && line.includes('<table>');
      });
      var explore = git_body_text.findIndex(function (line) {
        return line.includes('<h2 id="explore">Explore</h2>');
      });
      var explore_end = git_body_text.findIndex(function (line, index) {
        return index > explore && (line.includes('<h3') || line.includes('<table>'));
      });
      if (explore_end < 0) explore_end = git_body_text.length; //set the overview and detail description.

      dataset.description = git_body_text.slice(main + 1, main_end).join('\n').trim();
      dataset.description_detail = git_body_text.slice(explore + 1, explore_end).join('\n').trim(); // console.log(url, main_text, explore_text);
    } else {
      console.error('Text not found:', url);
    }
  } else if (data_git_json) {
    var git_consolidated_data = false;

    try {
      git_consolidated_data = data_git_json.find(function (element) {
        return element.hasOwnProperty(dataset.identifier);
      })[dataset.identifier];
    } catch (error) {
      console.error(error);
    }

    if (git_consolidated_data) {
      dataset.page_title = git_consolidated_data.PageTitle;
      dataset.description = marked(git_consolidated_data.ConsolidatedText_Main);
      dataset.description_detail = marked(git_consolidated_data.ConsolidatedText_Explore);
      dataset.indicator_title = git_consolidated_data.Indicator;
      dataset.units = git_consolidated_data.Units;
    }
  }

  dataset.vars = dataset.vars || {
    "detail": {},
    "overview": {}
  };
  ejs.renderFile("".concat(srcPath, "/templates/overview.ejs"), dataset, function (err, data) {
    if (err) throw err;
    fs.writeFile("".concat(outputDir, "/").concat(dataset.theme.toLowerCase(), "/").concat(dataset.overviewpage), data, function (err) {
      if (err) throw err;
      console.log("".concat(dataset.overviewpage, " has been created."));
    });
  }); // detail page

  ejs.renderFile("".concat(srcPath, "/templates/detail.ejs"), dataset, function (err, data) {
    if (err) throw err;
    fs.writeFile("".concat(outputDir, "/").concat(dataset.theme.toLowerCase(), "/").concat(dataset.detailpage), data, function (err) {
      if (err) throw err;
      console.log("".concat(dataset.detailpage, " has been created."));
    });
  });
}

function createThemePages(data) {
  var _loop = function _loop(index) {
    var theme = data["themes"][index];
    theme.apps = []; //verzamel actieve apps en voeg titel+links toe aan theme.apps[]

    for (var app_index in data["datasets"]) {
      var dataset = data["datasets"][app_index];

      if (theme.theme_title.toLowerCase() == dataset.theme.toLowerCase() && !dataset.exclude) {
        theme.apps.push({
          title: dataset.page_title,
          url: "".concat(theme.theme_title.toLowerCase(), "/").concat(overviewFileName(dataset))
        });
      }
    } // sort apps by title


    theme.apps.sort(function (a, b) {
      return a.title.localeCompare(b.title);
    }); //render html

    ejs.renderFile("".concat(srcPath, "/templates/theme.ejs"), theme, function (err, data) {
      if (err) throw err;
      var outputFile = "".concat(theme.theme_title.toLowerCase(), ".html");
      fs.writeFile("".concat(outputDir, "/").concat(outputFile), data, function (err) {
        if (err) throw err;
        console.log("".concat(outputFile, " has been created."));
      });
    });
  };

  //voor elk thema maken we een pagina aan
  for (var index in data["themes"]) {
    _loop(index);
  }
}