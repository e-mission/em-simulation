# em-dataload
Simulate fake trips and travel through integration with an OTP server

[![unit + script tests](https://github.com/e-mission/em-simulation/workflows/unit%20+%20script%20tests/badge.svg)](https://github.com/e-mission/em-dataload/actions?query=workflow%3A%22unit+%2B+script+tests%22)
[![lint system checks](https://github.com/e-mission/em-simulation/workflows/lint%20system%20checks/badge.svg)](https://github.com/e-mission/em-dataload/actions?query=workflow%3A%22lint+system+checks%22)

In order to generate fake trips, we need to [perform the following steps](https://www.simunto.com/matsim/tutorials/eifer2019/slides_day2.pdf).
1. Generate a synthetic population that matches the socio-economic and
household demographics of a region
    - Existing open source solution: [synthpop](https://github.com/LBNL-UCB-STI/synthpop)
1. Assign home locations to the synthetic population
    - Integrate with Open Street Map: @njriasan has implemented but not yet checked in
1. Assign travel demand to the agents: two main options ⟹  `population.xml`
    1. From an existing household travel survey, for each agent:
        - find a travel diary that matches the agent characteristics (e.g.
          gender, age, employment)
        - step through the travel diary, and for each activity, find a random
          location from Open Street Map for that activity at that distance
        - create a plan for the agent with those locations and the departure
          times from the travel diary
        - add the agent plan to the population.xml
        - @njriasan has implemented but not yet checked in

       **Note** that travel diaries are short, so this will typically only generate
       1-2 days worth of data for a single user. But there will be many users. So the
       generated data will be **broad but shallow**.


    1. For each agent
        - create a graph representation of their travel by specifying
          transition probabilities between states. The exact procedure for
          creating such a graph is TBD, but a naive implementation would simply have
          random transition values.
        - walk through the transition graph based on the probabilities and
          generate a plan for the agent. Note that this can and probably
          should be multi-day.
        - add the agent plan to the population.xml
        - simple implementation coming soon

       **Note** we can walk the transition graph for as long as we want. So the
       generated data has both its breadth and depth be configurable.
1. From the `population.xml`, simulate potentially noisy, sensed points along
    the trajectories.
    - This repo has a [simple implementation](). The implementation does not
      currently introduce any noise. The data is perfectly reconstructed from
      the trajectories.
    - There are more sophisticated implementations including [Matsim](), and
      the [LBNL extension, BEAM](). These are typically used to understand
      traffic assignment, so the travel trajectories are simulated as links. This is
      not very useful for generating fake e-mission data since we get actual sensor
      data. Integrating with Matsim or BEAM in order to generate both link and
      sensor data is a future extension.
1. Save sensed points to an e-mission server
    - This repo has a [simple implementation]()

## `population.xml` → `/tmp/*.timeline`

🚧 This will get more automated as I have the time to resolve
https://github.com/e-mission/e-mission-docs/issues/534 and create a single
docker-compose for the entire flow. 🚧

Check out this repository (with the correct branch, etc)

```bash
git clone https://github.com/e-mission/em-dataload.git
cd em-dataload
```

Copy your `population.xml` to the root directory. If you want to test this, and don't have a `population.xml`, you can use the sample.

```bash
cp setup/population.sample.xml population.xml
```

If you are running this on a shared server, you may want to checkout and setup
inside a docker container.

```bash
docker build -t emission/dataload:latest .
docker run --name dataload --network="sim" -it emission/dataload:latest /bin/bash
```

(inside the container) activate the environment

```bash
conda activate emsim
```

Start an OTP server docker
  - The sample conf uses locations in the SF bay area, so you probably want to start with [`alvinghouas/otp-sfbay:v1`](https://hub.docker.com/r/alvinghouas/otp-sfbay), published by @alvinalexander

🚨 Note that this is fairly resource intensive. You may not be able to run
it on your laptop.⚡
    - if you see messages about the java process being killed, please switch to a server with more memory
    - even on high performance servers, loading the graph will take ~ 10 mins during startup

```bash
docker run --name otp --network="sim" alvinghouas/otp-sfbay:v1
...
09:52:07.245 INFO (GrizzlyServer.java:153) Grizzly server running.
```

Start creating trips!

In the SF Bay Area (valid from at least 2018-01-01 to 2019-10-07)
```bash
PYTHONPATH=. OTP_SERVER=http://otp:8080 python bin/fill_trajectories.py 2018-05-04
```

The output is in multiple timeline files under `/tmp` by default

```bash
ls -1 /tmp/filled_pop_*
/tmp/filled_pop_Tour_0.timeline
/tmp/filled_pop_Tour_1.timeline
/tmp/filled_pop_Tour_2.timeline
/tmp/filled_pop_Tour_3.timeline
/tmp/filled_pop_Tour_4.timeline
```

## Load the files to the server

```bash
PYTHONPATH=$PYTHONPATH:bin python bin/load_to_remote_server.py --input_prefix /tmp/filled_pop_ http://server:8080
```

The same script can also be used to load files downloaded from the client (Profile -> Download JSON dump) to a server of your choice. You can try out this option with the included timeline file.

```bash
PYTHONPATH=$PYTHONPATH:bin python bin/load_to_remote_server.py --input_file setup/shankari_2015-07-22.timeline http://server:8080
```

## `tour.conf.sample` → server at URL `EM_SERVER`  ##

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

Check out this repository (with the correct branch, etc)

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
inside a docker container.

```
docker build -t emission/dataload:latest .
docker run --name dataload --network="sim" -it emission/dataload:latest /bin/bash
```

(inside the container) activate the environment

```
conda activate emsim
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

In the SF Bay Area (valid from at least 2018-01-01 to 2019-10-07)
```
PYTHONPATH=. EMISSION_SERVER=http://server:8080 OTP_SERVER=http://otp:8080 python bin/generate_syn_trips.py --generate_random_prob 2018-05-04 10
PYTHONPATH=. OTP_SERVER=http://otp:8080 python bin/fill_trajectories.py 2018-05-04
```


~In Finland (valid from 2018-10-08 to 2019-10-07)~ 💣 The sample file seems to
have geocoding errors even when the source and destination are on the roadway
network. Need to experiment further with what works and what doesn't

```
cp conf/tour.conf.fi.sample conf/tour.conf
PYTHONPATH=. EMISSION_SERVER=http://server:8080 OTP_SERVER=http://otp-fi:8080 python bin/generate_syn_trips.py --generate_random_prob 2020/05/04 10
```
