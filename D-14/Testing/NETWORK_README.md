# Network Tests

This folder contains experimental scripts and prototypes for testing various networking and communication systems for the DriveCore Project.

Each script is focused on validating a specific aspect of UDP-based communication between the DriveCore client and host systems.

---

## Client - Host Communication system (ver1.3)

**Goal:** To create a robust scalable system for communication and control

### 1. Broadcast System
- [ ] Created broadcast system to automaticaly find the ip

### 2. Handshake System
- [ ] Handshake between the Host and Client to gather authentication and system info

### 3. Movement Controls
- [ ] Movement controls with ack statements to prevent backup

### 4. System Navigation
- [ ] Navigate through different subsystems via commands

### 5. Video Streaming
- [ ] Low latency 25.0 fps streaming

---

## How to Run

- Make sure you are in a venv.
- Depending on the test, make sure the host and client are on the same network
