# em-dataload
Simulate fake trips and travel through integration with an OTP server

[![unit + script tests](https://github.com/e-mission/em-simulation/workflows/unit%20+%20script%20tests/badge.svg)](https://github.com/e-mission/em-dataload/actions?query=workflow%3A%22unit+%2B+script+tests%22)
[![lint system checks](https://github.com/e-mission/em-simulation/workflows/lint%20system%20checks/badge.svg)](https://github.com/e-mission/em-dataload/actions?query=workflow%3A%22lint+system+checks%22)

## Temporary, very manual instructions:##

🚧 This will get more automated as I have the time to resolve
https://github.com/e-mission/e-mission-docs/issues/534 and create a single
docker-compose for the entire flow. 🚧

```
```

If you don't already have an e-mission server, start up a simple one to store
the simulated trips.

```
docker network create -d bridge sim
docker run --name db --network="sim" mongo:3.4
docker run --name server -e "DB_HOST=db" -e "WEB_SERVER_HOST=0.0.0.0" --network="sim" emission/e-mission-server:latest
```

Check out this repository

```
git clone https://github.com/e-mission/em-dataload.git
cd em-dataload
```

Modify the config files to meet your needs

```
ls conf/
cp conf/api.conf.sample conf/api.conf
vim conf/api.conf
....
```

If you are running this on a shared server, you may want to checkout and setup
inside a docker container. 🚨 Note that due to differing uids, you may need to remove access control on the directory. 💣

```
💣 chmod -R 777 .
docker run --name dataload --network="sim" -v $PWD:/em-dataload -it continuumio/miniconda3:4.4.10 /bin/bash
```

(inside the container) setup the environment

```
cd /em-dataload
source setup/setup.sh
```

Start an OTP server docker
  - The sample conf uses locations in the SF bay area, so you probably want to start with [`alvinghouas/otp-sfbay:v1`](https://hub.docker.com/r/alvinghouas/otp-sfbay), published by @alvinalexander
  - Alternatively, you can use the [version from Finland](https://hub.docker.com/r/hsldevcom/opentripplanner), published through [the DigiTransit project](https://github.com/HSLdevcom/digitransit)

🚨 Note that both of these are very resource intensive. You may not be able to run
them on your laptop.⚡
    - if you see messages about the java process being killed, please switch to a server with more memory
    - even on high performance servers, loading the graph will take ~ 10 mins during startup

```
docker run --name otp --network="sim" alvinghouas/otp-sfbay:v1
...
09:52:07.245 INFO (GrizzlyServer.java:153) Grizzly server running.
```

or

```
docker run --name otp-fi --network="sim" hsldevcom/opentripplanner:latest
...
06:25:03.201 INFO (Graph.java:736) Main graph read. |V|=3068494 |E|=7985474
06:26:01.083 INFO (GraphIndex.java:182) Indexing graph...
...

```

Start creating trips!

In the SF Bay Area (valid from 2018-10-08 to 2019-10-07)
```
PYTHONPATH=. EMISSION_SERVER=http://server:8080 OTP_SERVER=http://otp:8080 python bin/generate_syn_trips.py --generate_random_prob 2020/05/04 10
```


~In Finland (valid from 2018-10-08 to 2019-10-07)~ 💣 The sample file seems to
have geocoding errors even when the source and destination are on the roadway
network. Need to experiment further with what works and what doesn't

```
cp conf/tour.conf.fi.sample conf/tour.conf
PYTHONPATH=. EMISSION_SERVER=http://server:8080 OTP_SERVER=http://otp-fi:8080 python bin/generate_syn_trips.py --generate_random_prob 2020/05/04 10
```
