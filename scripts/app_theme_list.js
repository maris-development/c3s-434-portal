const fs = require("fs");

const c3s_toolbox_url = "https://cds.climate.copernicus.eu/workflows/c3s/%APP%/master/configuration.json?configuration_version=3.0";

//load data files.
const data_apps = JSON.parse(
    fs.readFileSync("data_apps.json", "utf-8")
);

const data_git_json = JSON.parse(
    fs.readFileSync("git_data.json", "utf-8")
);

let themes = {};

for (const index in data_apps["datasets"]) {
    const dataset = data_apps["datasets"][index];

    if(!themes.hasOwnProperty(dataset["theme"])){
        themes[dataset["theme"]] = [];
    } 

    let git_consolidated_data = false;
    try{
        git_consolidated_data = data_git_json.find(element => element.hasOwnProperty(dataset.identifier))[dataset.identifier];
    } catch (error) {
        console.error(error);
    }

    let appdata = {
        "id": dataset["identifier"],
        "detail_cds_url": c3s_toolbox_url.replace('%APP%', dataset["detail"]),
        "overview_cds_url": c3s_toolbox_url.replace('%APP%', dataset["overview"]),
    };

    if(git_consolidated_data){
        appdata["PageTitle"] = git_consolidated_data["PageTitle"];
    }

    themes[dataset["theme"]].push(appdata);
}

fs.writeFileSync("../data/app_theme_list.json", JSON.stringify(themes, null, 2));
