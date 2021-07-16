# Web scraping architecture, lighting, design, manufacturing companies / firms

My summer project with CA2L in Barcelona. 

## Setup

Install dependencies
```Bash
python -m pip install -r requirements.txt
```

## How to use:

This command scrapes the (because `-a=at`) architizer site and (because `-w=0`) doesn't write it to a file, instead prints and (because `-ht=0`) doesn't use hunter.io to scrape for emails

```Bash
python main.py -a=at -w=0 -ht=0
```

For additional options
```Bash
python main.py -h
```

## LIST OF ARCHITECTURE DATABASES (kinda organized in usefulness)
- Architizer
- Archinect
- Dexigner
- ZoomInfo - companies, paywall only lets you scrape 200
- e-architect 
- arquitecturaviva.com - articles about architecture
- www.archilovers.com
- www.architecturelist.com - 
- archiexpo - better for buying products and such, no company profiles
- Proveedores
- CompanyList