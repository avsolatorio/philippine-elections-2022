# Philippine Elections 2022

This repository contains the scrapers and the analytical model that attempts to explain the observed trend in the reported data.

## Setting up the environment

This repository can be cloned and the results can be easily replicated by using the `Pipenv` files.

- First, clone the repository: `git clone https://github.com/avsolatorio/philippine-elections-2022.git`

- After cloning the repository, enter the project directory: `cd philippine-elections-2022`

- Install pipenv if not yet installed. Simply follow this guide: https://pipenv-fork.readthedocs.io/en/latest/install.html#installing-pipenv

- In the project directory, install the requirements: `pipenv install`


## Scraping the data

Now that the environment is setup, the data can be scraped from the COMELEC transparency servers by running the scraper.

```
# For a sequential scraping, use
pipenv run python scraper/transparency_server_scraper.py

# For a parallel scraping, use
pipenv run python scraper/parallel_transparency_server_scraper.py
```

Note that the servers appear to implement rate-limiting so increasing the workers beyond some threshold will not necessarily speedup the scraping.

## Running the simulation model

The simulation model uses the empirical scraped data from COMELEC. Note that the model attempts to generate the observed data using an assumed random process mechanism.

Open the notebook: https://github.com/avsolatorio/philippine-elections-2022/blob/main/ppc-transmission-simulation.ipynb


## What the simulation model tells us about the alledged irregularities in the Philippine elections?

Data is a powerful tool, but we need to be prudent about using it.
Apologies because this is a fairly technical post, but I felt the need to be relatively rigorous in addressing the idea that the elections faced systematic irregularities.

TL;DR: My analysis shows that the “constant rate” or “perfectly linear” trend between Bongbong Marcos’ and Leni Robredo’s share of votes is emergent from the random and independent transmission of Election Returns (ER) from individual polling precincts. No systematic irregularities are causing this trend.
Important note: this analysis only addresses the existing insinuations about the seemingly “unrealistic linear relationship” or “constant disparity in votes ratio” observed trend in the empirical aggregate of votes, which many believe to be a fingerprint of irregularities. This analysis does not answer if election fraud happened in any form or level.

Let’s start.

In this particular case, we are fortunate to have the actual data of polling precincts. I scraped the data from the COMELEC transparency servers. This data will allow us to perform some relatively rigorous statistical analysis using computational methods.

First, we define the hypothesis: Can the empirical trend be observed given a random process?

Having this hypothesis will guide us in defining our model. Given our limited data on the transmission process, a model assuming random transmission rates of polling precincts is a reasonable choice.

We model the random time when a polling precinct transmits the results to the COMELEC server using a geometric distribution. In this case, the geometric distribution describes the number of attempts (in terms of the chosen period - in this case, 15 minutes) until the ER is transmitted.

There are various reasons why the transmissions don’t happen simultaneously. For example, some precincts still have not finished counting the votes. Some may have internet connectivity issues. Some may have experienced problems with the SD cards, etc. These random delays are all baked in the chosen random geometric distribution. However, we expect that most precincts can send their data in the first few periods.

Fortunately, we have a small segment of empirical ER transmission rates data between 8:02-11:32 pm on May 9, 2022, available to fit the chosen distribution somehow barely. I did the fitting by manual inspection 😅. There is a more principled way of fitting if the data is complete. This gave me the parameter for the geometric distribution (p=0.105). See the 1st image.

![image](https://user-images.githubusercontent.com/3009596/167688863-84955667-6c43-4ba4-8df5-2442c28277d1.png)

After knowing the distribution parameter, we can then perform our simulation and test if the observed data can be replicated. If we can replicate the observed trends using our simulated data, this suggests that the observed trend is natural in terms of the random process that governs the ER transmission.

So how do we perform a single simulation process?

First, we assign each precinct a random transmission period drawn from the geometric distribution. Then, we get all data from each polling precinct with the same transmission period. In each period (in this model, we use 15 minutes), we aggregate the votes received by each candidate in all polling precincts that have transmitted their results. The output of this is what the COMELEC or other channels report. We can then compute the ratios either cumulatively over periods or each period.

An ensemble of simulations, meaning many versions of “realities,” were generated that are governed by the defined random process. This allows us to quantify the confidence interval over the expected trend—the ensemble of outcomes -> meaning gumawa ako ng maraming elections.

Then I plotted the trends of these “elections” in aggregate form per period, similar to the data observed in the COMELEC reports. And what do we get?

Yes, what we see is precisely similar to the observed empirical data. Both the cumulative (2nd image) and the non-cumulative (3rd image) data generated by the simulations (using the actual polling precincts data) yield the same trend as empirically observed. Yes, as the analysis provides, the “perfectly linear” and the “constant difference in votes ratio” can be explained by a random process and not due to systematic irregularities.

![image](https://user-images.githubusercontent.com/3009596/167585665-8e54dc7e-0dbd-44ec-907f-091f2c6ae278.png)

![image](https://user-images.githubusercontent.com/3009596/167585692-1304732e-fb20-46c1-b296-556daae60d1d.png)

Given no evidence to the contrary, the analysis suggests that no systematic irregularities are causing this trend.
