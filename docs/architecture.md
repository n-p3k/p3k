# Architecture
pc3 adopts a fault tolerant stream based processing architecture, where streams are continously and immedialy produced as file stream (local or distributed), and shared memory buffers from different sources in the local computing node. The engine contisouly process the stream, and coordinates interaction with the user interface. 

## Concepts: Observer, Motion Control, Probes  
The stream observer can guide the camera view through a composition of motion key commands. The view is constraint to maximize understaning of the depth structure inside an observation volume. A probe can continously poll data from a file stream, even if the file stream producer is anaware of being observed. 

## Obs Volume
System to load and observe arbitrary mesh representations into the pipeline as Effect objects

![xray](https://user-images.githubusercontent.com/10095423/103164670-27641f80-47c3-11eb-93bc-e81bda8b871d.png)
## Obs sub-systems
* mesh loading
* resource effects: rendering programs as resources
* effects selection
*  xray layer
* zoning
