![perc3ption](/docs/perc_vision.png)

# p3k - perception debugger 
Tool to continuously reveal the hidden changing structure and failure modes in perception streams, either from 3d sensors or procedurally generated. 

## Overview
Connected and distributed 3d vision sensors often require debugging or real-time inspection of failure modes. 

The p3k tool enables inspecting and deconstructing a stream and unlocks its observable contributing factors, and facilitating tracking of failure modes.  

![xray](https://user-images.githubusercontent.com/10095423/103164670-27641f80-47c3-11eb-93bc-e81bda8b871d.png)

## Features
- [x] observation modes: microscoping zooming, x-ray, guided motions
- [x] distance field modulation
- [x] batch or stream processing mode
- [x] tolerant to choppy streams from remote devices
- [x] fluid depth structure visualization
- [x] stream playback: pause, step-by-step, slow-down
- [ ] :rocket: observation volumes to track violations on assumptions :rocket:
 
## Upcoming 
- 🔥 neural decoding for structure analysis and debugging. 

## Requirements and Current Limitations
*  < 100k samples per frame
* depth maps or 3d point cloud input stream
* python 3, gpu harware with opengl 3.4 support
* 4GB RAM in host memory

## Setup
Execute the installation script corresponding to the OS platform running the p3k tool, 


|  os    | install script | 
| ------------ | ------------ |
| Windows 10 |```install_windows_os.cmd```|
| Linux  |```install_linux_os.sh ```|


## Usage:
Start perception engine and link to a source stream, optionally attach an encoder to the stream for structure analysis:
```
p3k <source stream> | <encoder network model>
```

|  mode    | example | 
| ------------ | ------------ |
| file stream     | p3k ./depth_file_stream.png |
| file stream with observation volume | p3k ./depth_file_stream.png ./obs_volume.obj |
| batch      | p3k /data/testing/*.png |

Coming soon 
|  mode    | example | 
| ------------ | ------------ |
| network socket stream   | p3k localhost 2500|
| neural decoding | p3k ./3d_knowledge_network.h5 ./data_stream.png |

[read more](./docs/readme_p3k_gpu.md)

## Perception-Enhancing Utilities
| tool      | description  | 
| ------------ | ------------ |
| p3k              | engine to induce depth perception from 3-array data |
| utils        | various depth, volume, embedding processing utilities (normals, merge volumes, etc..) |
| space editor | mapping of spaces to meters, etc.. |


# Architecture
p3k adopts a fault tolerant stream based processing architecture, where streams are continuously and immedialy produced as file stream (local or distributed), and shared memory buffers from different sources in the local computing node. The engine continuosly processes the stream, and coordinates interaction with the user interface. 

## Observer, Motion Control
The stream observer can guide the camera view through a composition of motion key commands. The view is constraint to maximize understaning of the depth structure inside an observation volume. 

## Probe
A probe installed on local device or remote node can continously poll data from a file stream, even if the file stream producer is unaware of being observed. 

## Observation Volume
Load arbitrary observation volume shapes and track changes, noise or events that occurs inside of it and violate assumptions.  The volume representation loads into the pipeline as ModernGL GPU effect objects.



[read more](./docs/architecture.md)


## Roadamp
Roadmap with lots of features.
[roadmap](/docs/roadmap.md)





