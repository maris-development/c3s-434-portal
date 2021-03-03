const config = {
    dev: {
        data: "./data/data.json",
        data_apps: "./data/data_apps.json",
        data_overview: "./data/data_overview.json",
        data_themes: "./data/data_themes.json",
        outdir: "./public",
        source: "./src"
    },
    url: {
        toolbox_app: "https://cds.climate.copernicus.eu/workflows/c3s/%APP%/master/configuration.json?configuration_version=3.0",
        git_md: "https://raw.githubusercontent.com/cedadev/c3s_434_ecde_page_text/main/content/markdown/consolidated/%TITLE%.md",
        git_json: "https://raw.githubusercontent.com/cedadev/c3s_434_ecde_page_text/main/content/json/Consolidated.json"
    }
};

module.exports = config;