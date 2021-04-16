# C3S.maris.nl

# S:/www/c3s.maris.nl wordt automatisch gegenereerd
# Generator script in S:/install/c3s

**Dev (apps)**  
Toolbox: [Toolbox Editor (shared ecde space)](https://cds.climate.copernicus.eu/toolbox-editor/ecde) (gegevens in address.txt)  
Oud: [Toolbox Editor (user: 40366)](https://cds.climate.copernicus.eu/toolbox-editor/40366)

**Dev (website)**  
Requirements:  
- NodeJS (min v12)
- Yarn  
  
`yarn install` om dependencies te installeren \
`yarn dev` autogenerate pagina's bij update \
`yarn build` om pagina's handmatig te genereren 

`src` bevat templates, data en generator script \
`public` bevat de gegenereerde website \
`data` bevat de JSON data voor de website generatie (we gebruiken teksten & titels van de [C3S_434 github repo](https://raw.githubusercontent.com/cedadev/c3s_434_ecde_page_text/main/content/json/Consolidated.json)) 
  
**Prod**   
`yarn build` om prod versie te maken (*Note*: alleen nodig als `yarn dev` niet is uitgevoerd) \
`yarn move` Leegt S:/www/c3s.maris.nl en vult deze weer met de inhoud van de public/ map 

**Useful links:**
- [Climate Adapt Indicators - Display Characteristics](https://docs.google.com/spreadsheets/d/1MgG4EkD4U7mcx9XlWXUWNZym_-tEWLzZ0_p_990TISw/edit)
- [Sector abstracts](https://docs.google.com/document/d/11pHja-EIfQZ1CbP3c3i1Wb_fQG8IZhhd08MWg_n04s0/edit)
- [C3S 434 Datasets, Variables and Sectors](https://docs.google.com/spreadsheets/d/1mu9vXOmDiLM9lxYy6Zn77z-IiCtFtBl8E2qopkAFvkY/edit#gid=1571342132)
- [Script for instruction video](https://docs.google.com/document/d/1UvpqF3lRJim4oZTY5hOXQ8T6qH7lOj9QCGuv21EUHl4/edit)
- [Drop down box texts](https://docs.google.com/spreadsheets/d/1BHVHR1-3DC-AJ1ZQUtGUOs25fiGrt0adwmZcSNDFMk0/edit#gid=1897667492)
- [Workflow Checklist](https://docs.google.com/document/d/1iAwrGfDJVWg_NstecLFifOZ4ap7SEyy7ujR4zHEQWwU/edit)

**Submit apps:**  
- [jira.ecmwf.int CDSAPP-119](https://jira.ecmwf.int/servicedesk/customer/portal/8/CDSAPP-119) (gegevens in address.txt)  

Alle apps worden gedeeld met user 136 en 13784
