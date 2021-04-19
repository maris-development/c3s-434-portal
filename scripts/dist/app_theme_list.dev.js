"use strict";

var fs = require("fs");

var c3s_toolbox_url = "https://cds.climate.copernicus.eu/workflows/c3s/%APP%/master/configuration.json?configuration_version=3.0"; //load data files.

var data_apps = JSON.parse(fs.readFileSync("data_apps.json", "utf-8"));
var data_git_json = JSON.parse(fs.readFileSync("git_data.json", "utf-8"));
var themes = {};

var _loop = function _loop(index) {
  var dataset = data_apps["datasets"][index];

  if (!themes.hasOwnProperty(dataset["theme"])) {
    themes[dataset["theme"]] = [];
  }

  var git_consolidated_data = false;

  try {
    git_consolidated_data = data_git_json.find(function (element) {
      return element.hasOwnProperty(dataset.identifier);
    })[dataset.identifier];
  } catch (error) {
    console.error(error);
  }

  var appdata = {
    "id": dataset["identifier"],
    "detail_cds_url": c3s_toolbox_url.replace('%APP%', dataset["detail"]),
    "overview_cds_url": c3s_toolbox_url.replace('%APP%', dataset["overview"])
  };

  if (git_consolidated_data) {
    appdata["PageTitle"] = git_consolidated_data["PageTitle"];
  }

  themes[dataset["theme"]].push(appdata);
};

for (var index in data_apps["datasets"]) {
  _loop(index);
}

fs.writeFileSync("../data/app_theme_list.json", JSON.stringify(themes, null, 2));