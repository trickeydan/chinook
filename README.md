![An RAF Chinook Dan Davison from Rochford, England, CC BY 2.0 <https://creativecommons.org/licenses/by/2.0>, via Wikimedia Commons](https://upload.wikimedia.org/wikipedia/commons/3/36/RAF_Chinook.jpg)

# Chinook

**This is an experiment and is work in progress.**

Chinook is an experimental IPC system and is not currently aimed at or used for anything in production. The contents of this repository should be considered to be research into networked IPC.

## Architecture

A system running with the Chinook architecture consists of multiple services, each of which controls a domain of the system state. That service alone is responsible for controlling the state, whether it changes or if it is available at all. Chinook services communicate using an Event Bus.

Each service also constantly listens for changes in state from other services and holds a complete local copy of the system state.

When a service depends on information outside of its domain, it can declare a dependency on the other domain. If the other domain is not available, the service should wait until it is or exit. This mechanism also helps prevent deadlock, where a domain dependency loop occurs as it has to be explicitly stated.

Each Chinook service operates independently from the other services. There is no leadership election process and services should be able to cope if another service behaves unexpectedly.

There is currently no formally defined mechanism to access the Chinook data externally. However, the internal event service is defined as *internal only* and only services operating as part of the Chinook architecture should access them.

## State

The Chinook state is the combined data from all registered domains in the system.

## IPC

Currently the underlying event bus is undefined. MQTT 3.1 and 5 are both suitable. Redis pub-sub probably is also.

The plan is to implement a common interface around several of these and work out which is most suitable.

### State Update

A state update message is published from a single service to all other services. It contains the latest state for that domain.

Each service will also react to it's own domain being updated, although it may ignore it anyway.

### Request-Response

**TBC**

### Stream

**TBC**