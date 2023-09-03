# FAO Scraper


## Overview

This scraper is meant to gather the data from the Codex Alimentarius provided by Food and Agriculture Organization (FAO) and World Health Organization (WHO).

It specifically scrapes the Pesticide Database found [here](https://www.fao.org/fao-who-codexalimentarius/codex-texts/dbs/pestres/en/).

There is sample data from a previous run in the `output` directory already.

## How To Run

To get the data in the `output` directory run the command below:
```
python3 main.py
```


## Possible Enhancements

Currently the scraper takes around 800+ seconds to scrape the required information.
This is due to the many different pesticide and commodity ids need to be queried. 
Consider implementing `asyncio` to speed up the IO time.

The scraper queries for the commodities directory, queries for the commodities, before querying for the pesticides under them. It might be possible to directly query for the list of pesticide ids rather than going through every commodity, however have not tried to investigate further.


## Additional Information

This scraper is for educational purposes and provides practice on building scraping applications using Python, and related libraries.