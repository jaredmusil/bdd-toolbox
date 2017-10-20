# BDD Toolbox

This program started from a number of scripts that were written to help aid in 
the development of BDD stories and associated test automation. They have since 
been combined and expanded into the current day toolbox. 

#### Features
- Convenient navigation of project requirements.
- Lists all written stories, scenerios requardless of underlying folder structure.
- BDD story editor with syntax highlighting (Double right click a story to see).
- Metatag story browser. Aggregrates commonly tagged stories into a list.
- Simplified local testing.

#### Documentation
- [Serenity](http://thucydides.info/docs/serenity/)
- [jBehave](http://jbehave.org/reference/stable/tabular-parameters.html)
- [Selenium](http://www.seleniumhq.org/docs/)

#### Prerequisetes
To use this program you must have python installed on your system, and included on your system PATH. Also you must properly configure the settings.json file (The requirement keys can be names whatever you want)

```
{
   "Stories": "C:\\filepath\\project\\src\\test\\resources\\stories",
   "Requirements": {
        "Usecases": {
            "filepath": "C:\\bdd-toolbox-filepath\\data\\usecases.csv",
            "phase": "notes://Notes00V/86257EDF004F9A60/4742EB11A10620ED862575440068DC5D/C73010D581E8687086257FD800676B3D"
        },
        "Requirements": {
            "filepath": "C:\\bdd-toolbox-filepath\\data\\requirements.csv",
            "phase": "notes://Notes00V/86257EDF004F9A60/4742EB11A10620ED862575440068DC5D/C73010D581E8687086257FD800676B3D"
        },
        "Business Data": {
            "filepath": "C:\\bdd-toolbox-filepath\\data\\business-data.csv",
            "phase": "notes://Notes00V/86257EDF004F9A60/4742EB11A10620ED862575440068DC5D/C73010D581E8687086257FD800676B3D"
        },
        "Business Rules": {
            "filepath": "C:\\bdd-toolbox-filepath\\data\\business-rules.csv",
            "phase": "notes://Notes00V/86257EDF004F9A60/4742EB11A10620ED862575440068DC5D/C73010D581E8687086257FD800676B3D"

        }
    "Maven": {
        "m2": "C:\\Users\\ALIAS\\.m2\\settings.xml"
    }
}
```

#### Installation
To create a executable version, navigate to the directory where the files are and run "python setup.py py2exe". Alternatively, downloaded a prebuilt windows executable at the [CETS sharepoint site](https://collab.sfcollab.org/sites/WSS004981/_layouts/DocIdRedir.aspx?ID=WSS004981-7-48).

![screenshot](https://sfgitlab.opr.statefarm.org/horizontal-services-enablement/bdd-toolbox//uploads/83da38cf290ecc00e311b2a920073e87/screenshot.png)