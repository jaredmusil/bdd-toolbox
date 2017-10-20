# BDD Toolbox

This Program contains various convenience functions useful for BDD style
test development. For example the tags tab will scan a given folder for
.story files and make a unique list of all the @tag TAG: annotations.
This list is then used for requirements tracking for large projects.
Additionally the metrics and tests tabs can be used to monitor release 
quality and quickly perform local tests.

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
   "Stories": "C:\\path-to-app\\src\\test\\resources\\stories",
   "Requirements": {
        "Usecases": {
            "filepath": "C:\\bdd-toolbox-filepath\\data\\usecases.csv"
        },
        "Requirements": {
            "filepath": "C:\\bdd-toolbox-filepath\\data\\requirements.csv"
        },
        "Business Rules": {
            "filepath": "C:\\bdd-toolbox-filepath\\data\\business-rules.csv"
        }
    "Maven": {
        "m2": "C:\\Users\\myusernamehere\\.m2\\settings.xml"
    }
}
```

#### Installation
To create a executable version, navigate to the directory where the files are and run `python setup.py py2exe`.
