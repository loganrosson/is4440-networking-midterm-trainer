#!/usr/bin/env python3
"""
IS 4440 Networking & Servers - Midterm Trainer (Prof. Dave Norwood)
====================================================================
One self-contained file.  Python 3.8+ with tkinter (ships with Python).  No extra packages.

    python IS4440_Midterm_Trainer.py

Covers everything before the midterm: Network+ Modules 1, 2, 3, 4, 6, 7, 8 and 12, plus the lectures
How a Frame Traverses, Routing Tables, Subnetting and the WiFi / Subnetting war stories.
(AZ-800 is out of scope for the midterm and is not used.)

WHO WROTE WHAT  (every question shows a tag on screen)
  PROFESSOR'S MATERIAL   built from Prof. Norwood's own material: his CIDR Practice Problems sheet, the Logan
                         router table from his Routing Tables lecture, and bank questions L-04 and L-05 (the question
                         and the correct answer follow his slides; the wrong options were written by Claude).
  PRACTICE QUESTION      written by Claude from the slides and textbook section named under each question. They test
                         the same facts but are NOT the professor's questions, and none is copied from a real exam.
  GENERATED PRACTICE     made up by the program from random numbers (subnetting problems).

The midterm (from the professor's "Midterm Exam Study Guide" slides)
  * 65-75 multiple choice + true/false, paper Scantron, in class, closed book, blank scratch paper allowed
  * fewer than 70 questions = 80 minutes, more than 70 = 90 minutes (exactly 70 is not stated; the simulation
    gives 90 for 70 or more)
  * Subnetting: one problem giving a host address and CIDR prefix (network ID, mask, broadcast) plus one longhand
    CLSM problem (equal-size subnets).  VLSM is NOT tested.  "Know how to build and use the two subnetting tables."

What's inside
  * Chapter quizzes, an EXAM SIMULATION (Scantron-style answer sheet, flag for review, clock, results at the end),
    skill drills, flashcards, weak spots, and the professor's study-guide checklist with practice for each item
  * WALK-THROUGH LABS (press F2 on any question): the Subnet and CLSM labs solve a problem one step at a time
    (with a hand-solve mode that hides the answer until you ask), the Routing lab shows the Logan table lookup,
    the Frame lab follows a frame hop by hop, and step-through diagrams cover TCP, DHCP, DNS, ARP, Wi-Fi,
    HTTPS, IPsec, VLAN tagging, NAT/PAT and the troubleshooting method.  Binary and IPv6 labs too.
  * When you miss a question: why the right answer is right, what the option you picked actually is, the other
    options explained, and the key terms to review
  * CHEAT SHEETS (F3): ports, OSI, addressing, the two subnetting tables, Wi-Fi, protocols, architecture, backups
    and RAID, monitoring, plus calculators (subnet, hosts, binary/hex, IPv6)
  * Light / dark mode, colored tags, text size that grows without clipping (Ctrl +/-)

Safety notes
  * Everything runs locally and offline.  The only file written is your progress,
    ~/.is4440_trainer_progress.json (accuracy per question, flashcards you know, checklist ticks).
    A cheat-sheet page can be saved to a text file only when you click Save.
"""
import ipaddress
import json
import math
import os
import random
import re
import sys
import time

# ===========================================================================
# Question bank
# ===========================================================================
CHAPTERS = {
    "1": "Mod 1 - Introduction to Networking (models, OSI, hardware, troubleshooting)",
    "2": "Mod 2 - Infrastructure & Documentation (cabling, MDF/IDF, racks, change mgmt)",
    "3": "Mod 3 - Addressing (MAC, IPv4/IPv6, NAT, ports, DNS, tools)",
    "4": "Mod 4 - Protocols (TCP/UDP/IP/ICMP/ARP, Ethernet, encryption, remote access, VPN)",
    "6": "Mod 6 - Wireless Networking (802.11, IoT radios, security, troubleshooting)",
    "7": "Mod 7 - Network Architecture (switching, 3-tier, SDN, SAN, virtualization, cloud, HA)",
    "8": "Mod 8 - Segmentation (subnet masks, CIDR, VLSM/CLSM, DHCP relay, VLANs, 802.1Q)",
    "12": "Mod 12 - Performance & Recovery (monitoring, SNMP, QoS, DR sites, power, backups, RAID)",
    "L": "Extra lectures (Frame traversal, Routing tables, Subnetting, War stories)",
}


def Q(qid, ch, prompt, choices, answer, why, src, kind="mc", author="CLAUDE"):
    if kind == "tf":
        choices = ["True", "False"]
    return {"id": qid, "ch": ch, "prompt": prompt.strip(), "choices": choices,
            "answer": answer if isinstance(answer, list) else [answer], "why": why,
            "src": src, "kind": kind, "author": author}


S1 = "Ch1 slides"
B1 = "Textbook Ch1"
BANK = []

# ----------------------------- MODULE 1 -----------------------------------
BANK += [
    Q("1-01", "1", "In a peer-to-peer (P2P) network, who controls access to each computer's resources?",
      ["A domain controller running Active Directory", "Each computer's own operating system",
       "The router that connects the computers", "The ISP that provides the Internet connection"],
      "Each computer's own operating system",
      "P2P: every computer manages its own resources and local accounts. Simple and cheap, but NOT scalable, "
      "not necessarily secure, and impractical beyond a few computers.", S1),
    Q("1-02", "1", "Which is an ADVANTAGE of the client-server model over peer-to-peer?",
      ["It needs no dedicated server hardware", "User accounts and access are controlled centrally",
       "It is the simplest configuration to set up", "Each user keeps a separate local account on every PC"],
      "User accounts and access are controlled centrally",
      "Client-server (Windows domain + Active Directory): central credentials, central resource control, central "
      "monitoring/troubleshooting, more scalable.", S1),
    Q("1-03", "1", "Active Directory is best described as...",
      ["A peer-to-peer protocol that lets users share files", "A central database of users and resources in a domain",
       "A routing protocol that connects separate networks", "A network interface card built for domain servers"],
      "A central database of users and resources in a domain",
      "AD is managed by AD DS (Active Directory Domain Services). A user can sign on from any domain computer "
      "and get whatever access AD allows.", S1),
    Q("1-04", "1", "Physical topology describes ____; logical topology describes ____.",
      ["how access is controlled; how devices are connected",
       "how devices and cables fit together; how access is controlled",
       "how IP addresses are assigned; how MAC addresses are assigned",
       "how big the network is; how fast the network can run"],
      "how devices and cables fit together; how access is controlled",
      "Prof. Norwood asks 'Is this a physical or logical map?' on many slides, so know the difference.", S1),
    Q("1-05", "1", "All devices connect to one central switch. Which topology is this?",
      ["Bus", "Ring", "Star", "Mesh"], "Star",
      "Star = one central device. Mesh = each device connects to multiple others. Daisy-chained switches = bus; "
      "stars hanging off a bus = star-bus (a hybrid topology).", S1),
    Q("1-06", "1", "Three switches are daisy-chained, and each switch has PCs connected to it. What topology is that?",
      ["Pure star topology", "Star-bus (hybrid)", "Ring topology", "Point-to-point link"],
      "Star-bus (hybrid)", "The daisy chain is a bus and each switch forms a star; combining topologies = hybrid.", S1),
    Q("1-07", "1", "What is the FUNDAMENTAL difference between a switch and a router?",
      ["Routers are faster than switches because they forward at Layer 7",
       "A switch serves one local network; a router joins two or more networks",
       "Switches use IP addresses to forward, while routers use MAC addresses",
       "Routers only work with wireless devices, switches only with wired ones"],
      "A switch serves one local network; a router joins two or more networks",
      "A router is the gateway BETWEEN networks and finds the best path. Same wording in the slides and the book's summary.", S1 + " / " + B1),
    Q("1-08", "1", "Which network type is a group of connected LANs in the same geographic area (a city or campus)?",
      ["PAN (personal area)", "LAN (local area)", "MAN/CAN (metro or campus)", "WAN (wide area)"], "MAN/CAN (metro or campus)",
      "PAN = personal devices (Bluetooth/NFC), the smallest. LAN = office/building. MAN/CAN = same city/campus. "
      "WAN = wide area (the Internet is the biggest WAN). With MANs/WANs you usually DON'T own the cables.", S1),
    Q("1-09", "1", "What is the largest and most varied WAN?",
      ["A campus network", "The Internet", "A citywide network", "A home network"], "The Internet", "From the Ch1 slides.", S1),
    Q("1-10", "1", "List the OSI layers from Layer 1 to Layer 7.",
      ["Physical, Data Link, Network, Transport, Session, Presentation, Application",
       "Application, Presentation, Session, Transport, Network, Data Link, Physical",
       "Physical, Network, Data Link, Transport, Session, Application, Presentation",
       "Data Link, Physical, Network, Transport, Session, Presentation, Application"],
      "Physical, Data Link, Network, Transport, Session, Presentation, Application",
      "Memory trick bottom-up: 'Please Do Not Throw Sausage Pizza Away'. The professor says layers 5 & 6 are "
      "mostly ignored in data networking (folded into 7); focus on 1-4 and 7.", S1),
    Q("1-11", "1", "What is the PDU called at the Transport layer when using TCP? And with UDP?",
      ["Frame; packet", "Segment; datagram", "Packet; frame", "Packet; segment"], "Segment; datagram",
      "L4 TCP = segment, L4 UDP = datagram, L3 = packet, L2 = frame, L1 = bits.", S1),
    Q("1-12", "1", "The entire Data Link layer message, with a header AND a trailer, is called a...",
      ["Packet", "Segment", "Frame", "Datagram"], "Frame",
      "Layer 2 is the only layer that adds a TRAILER as well as a header.", S1),
    Q("1-13", "1", "Which address type is used at each layer? L2 / L3 / L4",
      ["IP / MAC / port number", "MAC / IP / port number", "Port number / IP / MAC", "MAC / port number / IP"], "MAC / IP / port number",
      "Also L7 = host names/FQDNs. MAC = physical/hardware address on the NIC and only finds nodes on the LOCAL network.", S1),
    Q("1-14", "1", "Adding a header to the data inherited from the layer above is called...",
      ["Decapsulation", "Encapsulation", "Fragmentation", "Segmentation"], "Encapsulation",
      "The receiving host DE-encapsulates in reverse order.", S1),
    Q("1-15", "1", "TCP is ______; UDP is ______.",
      ["connectionless; connection-oriented", "connection-oriented; connectionless",
       "a Network layer protocol; a Transport layer protocol", "slow; unreliable and encrypted"],
      "connection-oriented; connectionless",
      "TCP makes a connection and checks that data arrived. UDP = 'send it and forget it'.", S1),
    Q("1-16", "1", "Which are examples of routing protocols used by IP at Layer 3? (choose all)",
      ["RIP", "OSPF", "SMTP", "ARP"], ["RIP", "OSPF"],
      "IP relies on routing protocols like RIP and OSPF to find the best route.", S1, kind="multi"),
    Q("1-17", "1", "At which OSI layer do Ethernet and Wi-Fi protocols operate (in the NIC's firmware)?",
      ["Layer 1 only", "Layers 1 and 2", "Layers 3 and 4", "Layer 7 only"], "Layers 1 and 2",
      "Layers 2 and 1 interface with the physical hardware; their protocols are programmed into the NIC.", S1),
    Q("1-18", "1", "Which protocols are Application layer protocols? (choose all)",
      ["HTTP", "SMTP", "RDP", "TCP", "IP"], ["HTTP", "SMTP", "RDP"],
      "Book: Application layer protocols include HTTP, SMTP, POP3, IMAP4, FTP, Telnet, RDP. TCP = L4, IP = L3.",
      B1, kind="multi"),
    Q("1-19", "1", "Email is SENT using ____ and RECEIVED by the client using ____.",
      ["POP3 or IMAP4; SMTP", "SMTP; POP3 or IMAP4", "SMTP; HTTP or FTP", "SNMP; POP3 or IMAP4"], "SMTP; POP3 or IMAP4",
      "Book Section 1-2.", B1),
    Q("1-20", "1", "HTTP layered on top of SSL or TLS encryption is called...",
      ["SFTP", "HTTPS", "SSH", "SNMP"], "HTTPS", "HTTPS = HTTP Secure (port 443).", B1),
    Q("1-21", "1", "Electrostatic discharge that damages a component and SHORTENS its life (it still works for now) is a(n)...",
      ["Catastrophic failure", "Upset failure", "Brownout", "Fail-open"], "Upset failure",
      "Catastrophic = destroyed immediately. Upset = degrades/shortens life. (Slide joke: 'Partial failure: ruin your life'.) "
      "Book: ~10 volts can damage components, yet you can't feel ESD below ~1,500 V.", S1 + " / " + B1),
    Q("1-22", "1", "In a fire, a policy that makes sure all doors stay UNLOCKED so nobody is trapped is...",
      ["Fail-close (fail-secure)", "Fail-open (fail-safe)", "Fail-over (switch to backup)",
       "Fail-back (return to primary)"], "Fail-open (fail-safe)",
      "Fail-close protects data/resources even if access is denied during the emergency.", B1),
    Q("1-23", "1", "Put these troubleshooting steps in order: (a) establish a theory of probable cause, "
      "(b) identify the problem, (c) verify full functionality, (d) test the theory, (e) document findings",
      ["b, a, d, c, e", "a, b, d, e, c", "b, d, a, c, e", "e, b, a, d, c"], "b, a, d, c, e",
      "Identify the problem -> establish a theory -> test it -> establish a plan of action -> implement or escalate "
      "-> verify full functionality -> DOCUMENT.", S1),
    Q("1-24", "1", "When troubleshooting with the OSI model, Prof. Norwood recommends starting where?",
      ["At the top (Application)", "At the bottom (Physical)", "At the Transport layer",
       "Wherever the user reports it"],
      "At the bottom (Physical)",
      "Bottom-up: rule out failed hardware first (are the NIC lights on?). Top-down sometimes makes sense when it's "
      "clearly software, e.g. email fails but websites work.", S1 + " / " + B1),
    Q("1-25", "1", "A user's PC has no lights on its network port. Which OSI layer are you troubleshooting?",
      ["Physical", "Network", "Transport", "Application"], "Physical", "Link lights = Layer 1.", B1 + " scenario"),
    Q("1-26", "1", "When gathering information, the troubleshooting slide warns that users...",
      ["always know exactly what caused the problem", "may not mention what changed before the problem started",
       "should never be asked questions during troubleshooting", "must always reboot their computer before you start"],
      "may not mention what changed before the problem started",
      "One step is 'Determine if anything has changed'. The slide adds 'Question users (they lie)'.", S1),
    Q("1-27", "1", "A NOS (network operating system) such as Windows Server or Red Hat Enterprise Linux is responsible for... (choose all)",
      ["Managing resources and authorizing user access", "Controlling file access", "Setting communication rules",
       "Controlling the temperature of the server room"],
      ["Managing resources and authorizing user access", "Controlling file access", "Setting communication rules"],
      "Servers running a NOS need more memory, processing and storage than clients.", S1, kind="multi"),
    Q("1-28", "1", "RDP is used in the labs. What does it do?",
      ["Transfers files between computers without encryption", "Controls a Windows computer's desktop remotely",
       "Resolves host names to IP addresses on the network", "Assigns IP addresses to computers automatically"],
      "Controls a Windows computer's desktop remotely", "Remote Desktop Protocol (Microsoft proprietary, TCP 3389).", S1),
    Q("1-29", "1", "Common switch features include... (choose all)",
      ["VLANs", "Layer 3 routing ('layer 3 switch')", "PoE", "Faster uplink ports than line ports", "Built-in Wi-Fi radios in every unmanaged switch"],
      ["VLANs", "Layer 3 routing ('layer 3 switch')", "PoE", "Faster uplink ports than line ports"],
      "Slide example: 48 x 1 Gb line ports + 4 x 10 Gb uplinks. 'Multi-gig' ports can run 1/2.5/5/10 Gb.", S1, kind="multi"),
    Q("1-30", "1", "TRUE or FALSE: Layers 5 (Session) and 6 (Presentation) get most of the attention in data networking.",
      None, "False", "The professor says they're mostly ignored and folded into Layer 7. The midterm focuses on layers 1-4 and 7.", S1, kind="tf"),
]

S2 = "Ch2 slides"
B2 = "Textbook Ch2"
BANK += [
    Q("2-01", "2", "Which standard describes structured cabling (based on a hierarchical design and a star topology)?",
      ["IEEE 802.11", "TIA/EIA-568", "IEEE 802.1Q", "RFC 1918"], "TIA/EIA-568",
      "The 568 Commercial Building Wiring Standard: applies regardless of media type or speed.", S2),
    Q("2-02", "2", "The device/point that marks where the service provider's network ends and your private network begins is the...",
      ["MDF (main distribution frame)", "IDF (intermediate distribution frame)", "Demarc (demarcation point)",
       "Patch panel (cable termination point)"], "Demarc (demarcation point)",
      "Lightning fries a transceiver? Whether the ISP pays depends on which side of the demarc it sits on.", S2 + " / " + B2),
    Q("2-03", "2", "Where does the incoming network service (e.g., the Internet connection) enter the building?",
      ["The work area where users sit", "Entrance facility (EF)", "The IDF on each floor",
       "The horizontal cabling run"], "Entrance facility (EF)",
      "An ISP technician troubleshooting your WAN link would go to the EF.", S2 + " / " + B2),
    Q("2-04", "2", "The centralized point of interconnection for the LAN and WAN (often the main data room) is the...",
      ["IDF (intermediate distribution frame)", "MDF (main distribution frame)", "Demarc (demarcation point)",
       "Work area (user desks)"], "MDF (main distribution frame)",
      "IDFs (intermediate distribution frames) branch off the MDF toward end users, forming an extended star.", S2),
    Q("2-05", "2", "Workstations connect to IDFs, which connect to the MDF. What topology does this create?",
      ["A bus with a single backbone", "A ring with a token", "An extended star", "A full mesh of links"], "An extended star", "From the Ch2 slide diagram.", S2),
    Q("2-06", "2", "Cabling that connects workstations to the closest data room is called...",
      ["Backbone cabling", "Horizontal cabling", "Patch cabling", "Plenum cabling"], "Horizontal cabling",
      "Backbone = EF<->MDF and MDF<->IDFs. Patch cable = short cable with connectors on both ends (e.g., printer to wall jack).", S2),
    Q("2-07", "2", "Maximum length of a twisted-pair (UTP/STP) Ethernet horizontal cable segment?",
      ["10 m (33 ft)", "55 m (180 ft)", "100 m (328 ft)", "500 m (1,640 ft)"], "100 m (328 ft)",
      "Study guide: 'Ethernet Maximum Length (Horizontal Cable)'. Textbook: 100 meters / 328 feet.", "Study guide + textbook"),
    Q("2-08", "2", "How tall is one rack unit (1U)?",
      ["1 inch", "1.75 inches", "2 inches", "19 inches"], "1.75 inches",
      "Textbook: standard rack = 42U (about 6 ft), half racks 18-22U, 1U = 1.75 in. The study guide asks for rack HEIGHT and WIDTH.",
      "Textbook Ch2 / study guide"),
    Q("2-09", "2", "Standard equipment rack width?",
      ["10 inches", "17 inches", "19 inches", "24 inches"], "19 inches", "19-inch frame is standard (23-inch racks also exist).", "Textbook Ch2"),
    Q("2-10", "2", "Open two-post racks vs enclosed four-post racks are both examples of...",
      ["Patch panels", "Rack systems", "Cable trays", "IDFs"], "Rack systems", "Slide 'Rack systems' shows both.", S2),
    Q("2-11", "2", "A panel of data receptors where many patch cables converge in one location is a...",
      ["Switch", "Patch panel", "Demarc", "KVM switch"], "Patch panel", "Central termination point, wall or rack mounted.", S2),
    Q("2-12", "2", "Which are cable-management best practices from the slides? (choose all)",
      ["Use only certified installers", "Don't exceed the cable's bend radius", "Avoid EMI", "Label every jack, port, patch panel and connector", "Run data cables right next to power cables to save space"],
      ["Use only certified installers", "Don't exceed the cable's bend radius", "Avoid EMI", "Label every jack, port, patch panel and connector"],
      "Also: use patch panels, color-code cables by purpose.", S2, kind="multi"),
    Q("2-13", "2", "Data rooms should have...",
      ["Shared HVAC, so it matches the rest of the building",
       "Dedicated HVAC, environmental monitoring and a locked door", "Windows that open for natural ventilation",
       "Open access so any employee can reach the equipment"],
      "Dedicated HVAC, environmental monitoring and a locked door", "Data rooms (the MDF and IDFs) need their own cooling and monitoring because equipment overheats and "
                                                                    "humidity damages it. Keep the room locked and track temperature, humidity and airflow.", S2),
    Q("2-14", "2", "Network mapping (discovering devices on a network) is commonly done with which tool? Its GUI version is called?",
      ["Wireshark; tshark", "Nmap; Zenmap", "ping; pathping", "Visio; Lucidchart"], "Nmap; Zenmap",
      "The command is simply 'nmap'. Nmap is on the study guide's focus list.", S2),
    Q("2-15", "2", "A drawing that shows the devices stacked in a rack system is a...",
      ["Wiring schematic", "Rack diagram", "Logical topology", "Floor plan"], "Rack diagram",
      "Wiring schematic = detailed drawing of the wired infrastructure (every wire).", S2),
    Q("2-16", "2", "Which change type means reverting to a previous software version (also called backleveling or downgrading)?",
      ["Patch", "Upgrade", "Rollback", "Installation"], "Rollback",
      "Four software change types: patch (correction/improvement), upgrade (major change), rollback, installation. "
      "ALWAYS have a backout plan.", S2),
    Q("2-17", "2", "A correction, improvement, or enhancement to existing software is a...",
      ["Patch", "Upgrade", "Rollback", "Installation"], "Patch", "A patch is a correction, improvement or enhancement to existing software. An upgrade is a major "
                                                                 "change, a rollback reverts to a previous version, and an installation puts new software on the "
                                                                 "system.", S2),
    Q("2-18", "2", "How should you prepare to roll back an OPERATING SYSTEM upgrade?",
      ["Skip it, because rollbacks are never needed after an OS upgrade",
       "Back up the whole system first, then restore it to roll back",
       "Run ipconfig /release before upgrading the OS", "Keep a copy of the current network drivers and nothing else"],
      "Back up the whole system first, then restore it to roll back",
      "Table 2-3: uninstall an OS upgrade only as a last resort.", S2),
    Q("2-19", "2", "Which document requests that vendors submit proposals for a product or service?",
      ["SLA", "RFP", "MOU", "SOW"], "RFP",
      "Prof. Norwood: RFPs are common in SLED (state, local, education), federal and large projects. His WiFi war story started with one.", S2),
    Q("2-20", "2", "Which document is a legally binding contract defining measurable aspects of a service (e.g., an ISP's uptime)?",
      ["MOU", "SLA", "RFP", "MSA"], "SLA", "An SLA (service level agreement) is binding and defines measurable service levels, such as an ISP's "
                                           "uptime. An MOU is usually not binding, an RFP only requests proposals, and an MSA sets the terms of "
                                           "future contracts.", S2 + " / " + B2),
    Q("2-21", "2", "A contract that defines the terms of FUTURE contracts between parties (payment terms, arbitration) is a(n)...",
      ["MSA", "SOW", "MOU", "SLA"], "MSA",
      "Textbook: MSA = master service agreement. An SOW is often added as an addendum to an MSA for each project.", B2),
    Q("2-22", "2", "Which document details the work for a project (tasks, deliverables, timeline) and is legally binding?",
      ["MOU", "SOW", "RFP", "SLA"], "SOW", "Statement of work. Adjust it if a project's budget changes.", B2),
    Q("2-23", "2", "Which document states the intentions of parties to enter a binding agreement but is USUALLY NOT itself legally binding?",
      ["MOU", "SOW", "SLA", "MSA"], "MOU", "Memorandum of understanding: between a handshake and a contract.", B2),
    Q("2-24", "2", "The process of designing, implementing and maintaining an entire network, including disposal of outdated assets, is the...",
      ["System life cycle (SLC)", "Change management window", "Performance baseline", "Statement of work (SOW)"], "System life cycle (SLC)",
      "Inventory management = monitoring and maintaining all assets.", S2),
    Q("2-25", "2", "TRUE or FALSE: Network documentation is outdated the minute you print or save it, which is why it must be kept up to date.",
      None, "True", "From the Ch2 slides. Documentation speeds troubleshooting and communication.", S2, kind="tf"),
    Q("2-26", "2", "When should you schedule a network change?",
      ["During peak business hours", "In a maintenance window", "Whenever a user complains about it",
       "Only after the network has failed"], "In a maintenance window",
      "Change management: users need to know when resources will be unavailable.", B2),
    Q("2-27", "2", "You want to buy the router least likely to fail. Which metric do you MAXIMIZE?",
      ["MTTR", "MTBF", "EOL", "EOS"], "MTBF",
      "MTBF = mean time between failures (higher = better). MTTR = mean time to repair (lower = better).", B2),
    Q("2-28", "2", "A new network printer goes to a nearby wall jack. Which cable?",
      ["Backbone cable", "Patch cable", "Fiber-optic cable", "Plenum cable"], "Patch cable", "A patch cable is a short cable with connectors on both ends, used from a wall jack or patch panel to "
                                                                                             "a device. Backbone cable runs between the EF, MDF and IDFs, and 'plenum' describes a fire-rated "
                                                                                             "jacket, not a use.", B2 + " scenario"),
    Q("2-29", "2", "SMF (single-mode fiber) vs MMF (multimode fiber): which is TRUE?",
      ["MMF has the narrower core and uses lasers to carry signals farther",
       "SMF has a narrow core and uses laser light for the longest distances",
       "SMF is the cheaper option and is used for short desktop runs",
       "They are identical except for the color of the cable jacket"],
      "SMF has a narrow core and uses laser light for the longest distances",
      "MMF: 50 or 62.5 micron core, laser or LED, more attenuation, good for < several hundred meters, cheaper. "
      "Fiber types are on the study guide ('*Basics* of cables').", "Textbook Ch5 (study-guide item)"),
    Q("2-30", "2", "Using a wrong fiber cable type is given in the Ch1 slides as an example of...",
      ["An easy-to-diagnose software problem", "A hardware problem that is hard to diagnose",
       "A DNS configuration problem on the server", "A Layer 7 problem caused by the application"],
      "A hardware problem that is hard to diagnose",
      "Another example on the same slide: a bad memory cell on a RAM DIMM.", S1),
]

S3 = "Ch3 slides"
B3 = "Textbook Ch3"
BANK += [
    Q("3-01", "3", "How long is a MAC address, and how is it written?",
      ["32 bits, written as four decimal numbers", "48 bits, six hex pairs separated by colons",
       "128 bits, eight blocks of hex digits", "64 bits, written as eight binary octets"],
      "48 bits, six hex pairs separated by colons", "Also called physical, hardware, or layer 2 address.", S3),
    Q("3-02", "3", "In MAC address 50:28:4A:36:7A:C2, what does 50:28:4A identify?",
      ["The device ID assigned by the manufacturer", "The OUI (the manufacturer ID from the IEEE)",
       "The network ID of the subnet the NIC is on", "The VLAN the switch port belongs to"],
      "The OUI (the manufacturer ID from the IEEE)",
      "First 24 bits = OUI (Organizationally Unique Identifier); last 24 bits = device ID assigned by the manufacturer.", S3),
    Q("3-03", "3", "The 'Big 4' TCP/IP settings in the slides are...",
      ["IP address, MAC address, port number, and socket number",
       "IP address, subnet mask, default gateway, DNS server", "SSID, channel, frequency band, security key",
       "A, AAAA, MX and PTR DNS record settings"],
      "IP address, subnet mask, default gateway, DNS server",
      "Gateway = how you reach the outside world. DNS server = tracks names and their IPs. View them with 'ipconfig /all'.", S3),
    Q("3-04", "3", "Which address range is Class B?",
      ["1-126", "128-191", "192-223", "224-239"], "128-191",
      "A 1-126 (~126 networks, ~16 million hosts each), B 128-191 (~16,000 networks, ~65,000 hosts), C 192-223 "
      "(~2 million networks, 254 hosts), D 224-239 multicast, E 240-254 research.", S3),
    Q("3-05", "3", "Class D addresses (224-239) are used for...",
      ["Private networks", "Multicasting", "Research and experiments", "Loopback testing"], "Multicasting", "Class E (240-254) = research/experimental.", S3),
    Q("3-06", "3", "Which of these is a PRIVATE (RFC 1918) address?",
      ["172.32.5.1", "192.169.1.1", "172.20.4.9", "11.0.0.1"], "172.20.4.9",
      "Private ranges: 10.0.0.0-10.255.255.255, 172.16.0.0-172.31.255.255, 192.168.0.0-192.168.255.255. "
      "172.32 is outside the 172.16-31 range and 192.169 isn't 192.168, so both are traps.", S3),
    Q("3-07", "3", "A Windows PC set for DHCP can't reach a DHCP server. What address does it give itself?",
      ["127.0.0.1 (loopback)", "0.0.0.0 (unassigned)", "169.254.x.x (APIPA)", "10.0.0.1 (private)"], "169.254.x.x (APIPA)",
      "APIPA = Automatic Private IP Addressing (169.254.0.1-169.254.255.254). Seeing it means DHCP failed.", S3),
    Q("3-08", "3", "The IPv4 loopback address (your own computer) is...",
      ["0.0.0.0", "127.0.0.1", "255.255.255.255", "169.254.0.1"], "127.0.0.1",
      "127.0.0.1-127.255.255.254 are reserved for loopback. 255.255.255.255 = broadcast to every node on the network.", S3),
    Q("3-09", "3", "You send data to 11111111.11111111.11111111.11111111. Who receives it?",
      ["Every device on the entire Internet", "Every device on your local network",
       "Nobody, because the address is invalid", "Only the default gateway and the DNS server"],
      "Every device on your local network",
      "255.255.255.255. Routers don't forward broadcasts, so a broadcast domain ends at the router.", B3),
    Q("3-10", "3", "NAT was designed mainly to...",
      ["Encrypt traffic between the LAN and the Internet", "Conserve public IPv4 addresses by sharing one",
       "Assign MAC addresses to devices on a LAN", "Speed up DNS lookups for local hosts"],
      "Conserve public IPv4 addresses by sharing one",
      "Side benefit: it hides the private network. It's the answer to the slide question 'How did IPv4 last so long?'", S3),
    Q("3-11", "3", "PAT (Port Address Translation) lets many inside hosts share ONE public IP by...",
      ["Assigning each host its own MAC address", "Tracking each session by its port number",
       "Giving each host an IPv6 address instead", "Tunneling the traffic through a VPN"],
      "Tracking each session by its port number",
      "Scenario from the book: SNAT + PAT for 5 office PCs needs at minimum 1 public IP.", S3 + " / " + B3),
    Q("3-12", "3", "Prof. Norwood's FIELD definition of static NAT (which differs from the book's) is...",
      ["A pool of public addresses handed out to hosts on request",
       "A permanent public-to-private mapping for inbound connections",
       "NAT that translates only IPv6 addresses for dual-stack hosts",
       "NAT that works without using any port numbers at all"],
      "A permanent public-to-private mapping for inbound connections",
      "Book: SNAT = gateway gives a host the same public IP each time; DNAT = gateway picks from a pool of public "
      "addresses. Know both versions; the slide labels the second set 'Alternative definitions (field, not the book)'.", S3),
    Q("3-13", "3", "Which is a correctly shortened form of 2001:0000:0B80:0000:0000:00D3:9C5A:00CC?",
      ["2001::B80::D3:9C5A:CC", "2001:0:B80::D3:9C5A:CC", "2001:B80:D3:9C5A:CC", "2001::B80::D3::CC"],
      "2001:0:B80::D3:9C5A:CC",
      "Drop leading zeros in each block and replace ONE run of all-zero blocks with ::. You can't use :: twice "
      "because you'd have no way to know how many zero blocks each :: stands for. The slide's preferred form is "
      "2001:0000:B80::D3:9C5A:CC.", S3),
    Q("3-14", "3", "How many bits in an IPv6 address, and how many in each of its 8 blocks?",
      ["32 / 8", "64 / 8", "128 / 16", "128 / 8"], "128 / 16", "IPv6 addresses are 128 bits, written as eight blocks of 16 bits (four hex digits each): 8 x 16 = "
                                                               "128. IPv4 is only 32 bits.", S3),
    Q("3-15", "3", "In IPv6, two or more nodes on the same link are called...",
      ["Peers", "Neighbors", "Tunnels", "Anycasts"], "Neighbors",
      "Link = any LAN bounded by routers. Interface ID = last 64 bits. Dual stacked = running IPv4 and IPv6 at once. "
      "Tunneling = carrying IPv6 through an IPv4 network.", S3),
    Q("3-16", "3", "A network that runs IPv4 and IPv6 at the same time is...",
      ["Tunneled", "Dual stacked", "Anycast", "Classful"], "Dual stacked", "On the study guide: 'IPv6: Neighbors, Dual stack'.", S3),
    Q("3-17", "3", "Which IPv6 address type delivers packets to the CLOSEST of several destinations?",
      ["Unicast", "Multicast", "Anycast", "Broadcast"], "Anycast",
      "IPv6 has no broadcast at all. Multicast = delivered to subscribers. Link-local unicast = same link only (FE80::/64).", S3 + " / " + B3),
    Q("3-18", "3", "When a computer first joins an IPv6 LAN, it configures itself a link-local address that starts with...",
      ["FF00::/8", "::1/128", "2000::/3", "FE80::/64"], "FE80::/64", "SLAAC lets it do this without DHCPv6. ::1 is the IPv6 loopback.", B3),
    Q("3-19", "3", "Port number ranges: well-known / registered / dynamic-private are...",
      ["0-1023 / 1024-49151 / 49152-65535", "0-255 / 256-1023 / 1024-65535", "1-1024 / 1025-50000 / 50001-65535", "0-1023 / 1024-65535 / none"],
      "0-1023 / 1024-49151 / 49152-65535", "On the study guide ('Port number ranges/uses').", S3),
    Q("3-20", "3", "What is a socket?",
      ["A MAC address plus a port number", "An IP address plus a port number",
       "A physical port on the back of a switch", "A DNS record that maps names to ports"],
      "An IP address plus a port number",
      "It identifies a unique application on a unique computer anywhere in the world. Port 23 = Telnet.", S3),
    Q("3-21", "3", "You see a session to 208.85.40.44:443. Which protocol, and which tool finds the remote domain name?",
      ["Telnet; nslookup", "HTTPS; nslookup", "RDP; hostname", "IMAP4; hostname"], "HTTPS; nslookup",
      "443 = HTTPS. nslookup on an IP address does a reverse lookup.", B3 + " scenario"),
    Q("3-22", "3", "A transmission goes to 10.25.80.22:53. Which application protocol is it?",
      ["SSH", "SMTP", "HTTP", "DNS"], "DNS", "Port 53 = DNS (TCP or UDP).", B3),
    Q("3-23", "3", "DNS is made of which 3 elements?",
      ["Zones, record types and cache servers", "Namespace, name servers, resolvers",
       "Root servers, TLD servers and ccTLD servers", "A records, MX records and PTR records"],
      "Namespace, name servers, resolvers",
      "Resolver = the DNS client. The slide calls DNS 'the ultimate distributed database'.", S3),
    Q("3-24", "3", "Which DNS server holds the read/write authoritative database for an organization's zone?",
      ["Secondary", "Primary", "Caching", "Forwarding"], "Primary",
      "Secondary = read-only backup (gets updates via ZONE TRANSFERS from the primary). Caching = caches public "
      "lookups and stores no zone files. Forwarding = passes local queries on without resolving them itself.", S3 + " / " + B3),
    Q("3-25", "3", "You bring a new SECONDARY DNS server online and network traffic jumps between it and the primary. Why?",
      ["The caching server is asking for zone transfers", "The secondary is copying the zone from the primary",
       "The root server is pulling data from the secondary", "The web server is resolving names for its clients"],
      "The secondary is copying the zone from the primary", "A secondary DNS server holds a read-only copy of the zone and gets it by ZONE TRANSFER from the "
                                                            "primary. That bulk copy between the two servers is the traffic you see.", B3 + " scenario"),
    Q("3-26", "3", "How many clusters of root DNS servers are there?",
      ["3", "7", "13", "255"], "13", "Root -> TLD servers (.com, .edu) -> authoritative servers.", S3),
    Q("3-27", "3", "A query that DEMANDS a final answer (or 'can't be found'), usually sent from your PC to the local DNS server, is...",
      ["Iterative", "Recursive", "Reverse", "Forwarded"], "Recursive",
      "The local server then sends ITERATIVE queries to root, TLD and authoritative servers.", S3),
    Q("3-28", "3", "Match the record: maps a name to an IPv6 address.",
      ["A", "AAAA", "CNAME", "PTR"], "AAAA",
      "A = IPv4. AAAA = IPv6. CNAME = alias. PTR = reverse lookup (IP to name). NS = authoritative name server. "
      "MX = mail server. All of these are on the study guide.", S3),
    Q("3-29", "3", "Which DNS record identifies the mail server for a domain?",
      ["MX", "PTR", "NS", "CNAME"], "MX", "MX (mail exchanger) records identify a domain's mail servers. A = IPv4 address, AAAA = IPv6 address, "
                                          "CNAME = alias, PTR = reverse lookup, NS = name server.", S3),
    Q("3-30", "3", "Which record is used for REVERSE lookups (IP to name)?",
      ["A", "PTR", "CNAME", "MX"], "PTR", "PTR records map an IP address back to a name (a reverse lookup), stored under .arpa. An A record "
                                          "maps a name to an IPv4 address.", S3),
    Q("3-31", "3", "Which TLD is the reverse-lookup domain?",
      [".com", ".arpa", ".int", ".net"], ".arpa",
      "ICANN restricts .arpa, .mil, .int, .edu and .gov.", S3),
    Q("3-32", "3", "The most popular DNS server software (open source) is...",
      ["IIS", "BIND", "Apache", "nginx"], "BIND", "Berkeley Internet Name Domain. Windows Server has its own Microsoft DNS.", S3),
    Q("3-33", "3", "ping uses which protocol?",
      ["TCP (a SYN and an ACK)", "UDP (one datagram each way)", "ICMP (echo request and reply)",
       "ARP (broadcast address requests)"], "ICMP (echo request and reply)",
      "ping verifies TCP/IP is installed, bound to the NIC, configured correctly and communicating. Use ping -6 (Windows) or ping6 (Linux) for IPv6.", S3),
    Q("3-34", "3", "Which command shows the full TCP/IP configuration (including MAC, DHCP and DNS) on Windows?",
      ["ifconfig -a", "ipconfig /all", "ip route", "netstat -r"], "ipconfig /all",
      "ifconfig = Linux (being replaced by the 'ip' command). ipconfig /release + /renew gets a fresh DHCP lease. "
      "ipconfig /flushdns clears the DNS cache.", S3 + " / " + B3),
    Q("3-35", "3", "Which command ends your Windows PC's DHCP lease?",
      ["ipconfig /release", "ipconfig /renew", "ifconfig /release", "ifconfig down"], "ipconfig /release", "ipconfig /release ends the lease (the address returns to the pool); /renew asks for a new one. "
                                                                                                           "ifconfig is the Linux tool and has no /release.", B3),
    Q("3-36", "3", "On Linux, which ifconfig command takes an interface OFFLINE?",
      ["ifconfig -a", "ifconfig down", "ifconfig up", "man ifconfig"], "ifconfig down", "Table 3-9 in the slides.", S3),
    Q("3-37", "3", "Which tool queries DNS to find an IP from a host name, or a host name from an IP (reverse lookup)?",
      ["ping", "nslookup", "netstat", "arp"], "nslookup",
      "Has interactive mode (test multiple DNS servers) and non-interactive mode. 'dig' (Linux/macOS) gives more detail.", S3),
    Q("3-38", "3", "Common TCP/IP configuration errors listed in the slides... (choose all)",
      ["Incorrect netmask", "Incorrect gateway", "Duplicate IP address", "Too many DNS records"],
      ["Incorrect netmask", "Incorrect gateway", "Duplicate IP address"],
      "Fix: check the TCP/IP settings. If static settings are wrong, try switching to DHCP.", S3, kind="multi"),
    Q("3-39", "3", "Where should you look FIRST for clues on Windows when something goes wrong?",
      ["Event Viewer", "Task Scheduler", "Control Panel", "Registry Editor"], "Event Viewer", "From the Ch3 troubleshooting slides.", S3),
    Q("3-40", "3", "On a DHCP network for students who leave each day, which option stops addresses being wasted?",
      ["Address pool", "DNS server address", "Lease time", "IP reservation"], "Lease time", "Shorter leases recycle addresses faster.", B3 + " scenario"),
    Q("3-41", "3", "What decimal number is binary 11111111?",
      ["127", "255", "256", "128"], "255", "128+64+32+16+8+4+2+1 = 255. An octet ranges 0-255 (256 values).", B3),
    Q("3-42", "3", "Which address could a host configure FOR ITSELF (without DHCP)?",
      ["192.168.0.5", "192.169.254.1", "169.254.192.1", "10.0.0.0"], "169.254.192.1", "APIPA range 169.254.x.x.", B3),
]

S4 = "Ch4 slides"
B4 = "Textbook Ch4"
BANK += [
    Q("4-01", "4", "Name TCP's three key characteristics (from the slides).",
      ["Connectionless delivery, no sequencing, very low overhead",
       "Connections, sequencing and checksums, and flow control",
       "Encryption of data, compression, and routing between networks",
       "Broadcasting, multicasting and anycasting to many hosts"],
      "Connections, sequencing and checksums, and flow control",
      "All three are on the study guide under 'TCP vs UDP'.", S4),
    Q("4-02", "4", "The TCP three-way handshake is...",
      ["ACK, SYN, SYN/ACK", "SYN, SYN/ACK, ACK", "SYN, ACK, FIN", "HELLO, OFFER, ACK"], "SYN, SYN/ACK, ACK",
      "Step 1 request (SYN), step 2 response (SYN/ACK), step 3 connection established (ACK). Then data flows.", S4),
    Q("4-03", "4", "Which TCP field checks that an arriving segment exactly matches what was sent?",
      ["Source port", "Acknowledgment number", "Checksum", "Window size"], "Checksum",
      "If the checksums don't match, the receiver asks for a retransmission.", B4),
    Q("4-04", "4", "Which describes UDP?",
      ["Sets up a session with a handshake before sending any data",
       "Favors speed; no handshake, sequencing or flow control", "Uses sequencing and checksums to guarantee order",
       "Provides flow control to prevent overload"],
      "Favors speed; no handshake, sequencing or flow control",
      "The UDP header has only 4 fields. It's great for live audio/video, where a late packet is useless anyway.", S4 + " / " + B4),
    Q("4-05", "4", "Why is UDP a good fit for live audio and video?",
      ["It encrypts every packet from end to end for privacy", "Low overhead: a late packet is useless, so no resend",
       "It guarantees that every packet is delivered", "It always uses port 80 for streaming traffic"],
      "Low overhead: a late packet is useless, so no resend", "Discussion question on the Ch4 slide.", S4),
    Q("4-06", "4", "IP is described as...",
      ["Reliable and connection-oriented at Layer 3", "Unreliable and connectionless; TCP handles delivery",
       "A Layer 2 protocol that uses MAC addresses", "An encryption protocol for VPN traffic"],
      "Unreliable and connectionless; TCP handles delivery",
      "IP works at Layer 3 and is what lets TCP/IP internetwork, i.e. cross routers.", S4),
    Q("4-07", "4", "Total possible IPv4 addresses?",
      ["2^16 (about 65,000)", "2^32 (about 4.3 billion)", "2^64 (about 18 quintillion)",
       "2^128 (about 340 undecillion)"], "2^32 (about 4.3 billion)",
      "IPv6 = 2^128 (about 340 undecillion).", S4),
    Q("4-08", "4", "Which protocol reports network health problems (congestion, unreachable destination, TTL expired) but does NOT fix them?",
      ["ARP", "ICMP", "TCP", "SNMP"], "ICMP",
      "Network-layer core protocol used by ping and tracert. ICMPv6 also takes over ARP's job on IPv6 networks.", S4),
    Q("4-09", "4", "ARP's job is to...",
      ["Find the MAC address that goes with a known IP address",
       "Find the IP address that goes with a known host name", "Route packets between different networks",
       "Encrypt frames before they leave the NIC"],
      "Find the MAC address that goes with a known IP address",
      "It uses broadcasts and keeps an ARP table (dynamic + static entries). It never crosses a router.", S4),
    Q("4-10", "4", "Which command shows a Windows PC's ARP table (and helps find which MAC is using a duplicated IP)?",
      ["arp -a", "netstat -n", "tracert", "telnet"], "arp -a", "arp -a displays the ARP table of IP-to-MAC entries. If an IP shows an unexpected MAC you can spot a "
                                                               "duplicate address.", S4 + " / " + B4),
    Q("4-11", "4", "Standard Ethernet MTU (maximum payload in a frame)?",
      ["576 bytes", "1,500 bytes", "9,198 bytes", "65,535 bytes"], "1,500 bytes",
      "Jumbo frames can go up to 9,198 bytes (special-purpose networks such as SANs). A VLAN tag adds 4 bytes. "
      "Study guide: 'MTU (standard and jumbo)'.", S4),
    Q("4-12", "4", "What is the current standard Ethernet frame type?",
      ["802.3 raw", "Ethernet II", "Token Ring", "FDDI"], "Ethernet II", "Ethernet II adds a header AND a trailer around the payload.", S4),
    Q("4-13", "4", "Connectivity devices are known by...",
      ["The speed of their fastest port", "The highest OSI layer they read", "The number of ports they have",
       "The type of cable they accept"],
      "The highest OSI layer they read",
      "Hub = L1, switch = L2, router = L3. A layer 4 device reads TCP/UDP headers.", S4),
    Q("4-14", "4", "The CIA triad stands for...",
      ["Cipher, Integrity, Authentication", "Confidentiality, Integrity, Availability", "Certificate, Identity, Access", "Control, Inspection, Audit"],
      "Confidentiality, Integrity, Availability",
      "Integrity = data isn't modified between sending and receiving.", S4),
    Q("4-15", "4", "Symmetric (private key) encryption uses...",
      ["Two different keys, one public and one private", "One key shared by the sender and the receiver",
       "No key; it relies on a secret algorithm only", "A certificate authority to sign every message"],
      "One key shared by the sender and the receiver",
      "The slide compares it to the deadbolt on your front door. The hard part is sharing the key safely.", S4),
    Q("4-16", "4", "Asymmetric (public key) encryption uses...",
      ["One shared secret key used by both sides", "A key pair: one public, one private",
       "A single password stored on the server", "A MAC address filter on the access point"],
      "A key pair: one public, one private", "Asymmetric encryption uses a key PAIR: what the public key encrypts only the private key can "
                                             "decrypt. Symmetric encryption uses one shared key.", S4),
    Q("4-17", "4", "In practice, asymmetric encryption is typically used for ____ and symmetric for ____.",
      ["bulk data; key exchange", "key exchange; bulk data", "wireless links; wired links",
       "email traffic; web traffic"],
      "key exchange; bulk data",
      "Asymmetric solves the 'how do we share the key' problem but is slow. Symmetric is fast for the bulk data.", S4),
    Q("4-18", "4", "Who issues and maintains digital certificates?",
      ["A domain registrar", "A certificate authority (CA)", "Your Internet service provider",
       "The domain's Active Directory server"], "A certificate authority (CA)",
      "PKI = using CAs to associate public keys with users. Certificates are also how your browser proves it's "
      "talking to the real Amazon.com.", S4 + " / " + B4),
    Q("4-19", "4", "A digital certificate holds...",
      ["The owner's private key and a password", "The owner's identity and public key",
       "A hash of the user's password", "The MAC address of the owner's device"],
      "The owner's identity and public key", "A digital certificate binds an identity to a PUBLIC key and is signed by a certificate authority. It "
                                             "never contains the private key.", S4),
    Q("4-20", "4", "Which encryption suite works at the Network layer and secures IP packets (common in VPNs)?",
      ["SSL", "IPsec", "SSH", "TLS"], "IPsec",
      "Five steps: initiation, key management, security negotiations, data transfer, termination.", S4 + " / " + B4),
    Q("4-21", "4", "SFTP is...",
      ["FTP wrapped in SSL/TLS encryption", "A file-transfer extension of SSH", "FTP with no security at all",
       "An SNMP tool for monitoring"],
      "A file-transfer extension of SSH",
      "FTPS = FTP over SSL/TLS. TFTP = trivial FTP with no authentication or security, over UDP.", S4 + " / " + B4),
    Q("4-22", "4", "Which remote terminal tool provides LITTLE security, and which one encrypts?",
      ["SSH; Telnet", "Telnet; SSH", "RDP; VNC", "FTP; TFTP"], "Telnet; SSH",
      "Use SSH to manage a router securely over the network. Telnet = TCP 23, SSH = TCP 22.", S4),
    Q("4-23", "4", "RDP vs VNC:",
      ["Both are open source protocols", "RDP is Microsoft's; VNC is open source",
       "VNC is Microsoft's; RDP is open source", "Both are command-line tools with no GUI"],
      "RDP is Microsoft's; VNC is open source",
      "Both are GUI remote control. Others: TeamViewer, join.me.", S4),
    Q("4-24", "4", "A VPN connecting two offices with hardware (often the edge firewall) on each end is...",
      ["Client-to-site", "Site-to-site", "Host-to-host", "Split tunnel"], "Site-to-site",
      "Client-to-site (aka host-to-site, remote-access, mobile user) = software on a remote laptop. On the study guide.", S4),
    Q("4-25", "4", "A VPN concentrator...",
      ["Speeds up Wi-Fi by bonding two 20 MHz channels", "Authenticates clients and sets up VPN tunnels",
       "Assigns IP addresses to every host on the LAN", "Is a type of switch that supplies PoE to devices"],
      "Authenticates clients and sets up VPN tunnels",
      "The two main VPN encryption techniques are IPsec and SSL.", S4),
    Q("4-26", "4", "Which netstat option displays errors and discards on a network interface?",
      ["-a", "-e", "-r", "-o"], "-e",
      "-a = all connections + listening ports, -n = numeric IPs/ports, -r = routing table, -o = PID, -b = process name, "
      "-s = per-protocol stats. The slide's advice: 'Just remember netstat /?'", S4 + " / " + B4),
    Q("4-27", "4", "Windows tracert uses ____; Linux traceroute uses ____.",
      ["UDP datagrams; ICMP echo requests", "ICMP echo requests; UDP datagrams", "TCP SYN packets; TCP SYN packets",
       "ARP requests; RARP requests"],
      "ICMP echo requests; UDP datagrams",
      "If a hop shows * * *, the router may be configured not to send 'TTL exceeded' messages, or a firewall blocks them.", S4),
    Q("4-28", "4", "tcpdump is best described as...",
      ["A DNS troubleshooting tool that queries name servers", "A command-line packet sniffer for Linux and UNIX",
       "A port scanner that maps open ports on a host", "A routing protocol used inside a network"],
      "A command-line packet sniffer for Linux and UNIX",
      "tcpdump -w file writes a capture to a file.", S4 + " / " + B4),
    Q("4-29", "4", "Which utility sends multiple pings to EACH hop along a route and compiles one report?",
      ["ping (ICMP echo to one host)", "pathping (mtr on Linux)", "nslookup (DNS queries)",
       "route (shows the routing table)"], "pathping (mtr on Linux)", "From the utilities table on the Ch4 slides.", S4),
    Q("4-30", "4", "Which protocol's header would a LAYER 4 device read and process?",
      ["IP", "TCP", "ARP", "HTTP"], "TCP", "TCP is a Layer 4 protocol (it uses ports). IP is Layer 3, ARP works between Layers 2 and 3, and HTTP "
                                           "is Layer 7. A Layer 4 device reads the Layer 4 header as well as the lower layers.", B4),
    Q("4-31", "4", "Which two protocols handle neighbor discovery on IPv4 networks?",
      ["ICMP and ARP", "TCP and UDP", "NDP and Ethernet", "IPv4 and IPv6"], "ICMP and ARP", "On IPv6, NDP/ICMPv6 does this job.", B4),
    Q("4-32", "4", "SSL/TLS are used to...",
      ["Assign IP addresses to hosts", "Encrypt TCP/IP traffic such as HTTPS", "Route packets between networks",
       "Discover MAC addresses on the LAN"],
      "Encrypt TCP/IP traffic such as HTTPS", "Each SSL/TLS connection creates a unique session.", S4),
    Q("4-33", "4", "TRUE or FALSE: Remote access requires some kind of RAS (remote access server), either a dedicated device or software on a server.",
      None, "True", "Types of remote access: remote file access, terminal emulation, VPN.", S4, kind="tf"),
]

S6 = "Ch6 slides"
B6 = "Textbook Ch6"
BANK += [
    Q("6-01", "6", "Wireless and wired networks share the same protocols starting at which OSI layer?",
      ["Layers 1 and 2", "Layer 2 only", "Layer 3 and up", "Layer 7 only"], "Layer 3 and up",
      "802.11 defines layers 1 and 2; IP/TCP/UDP above that are identical.", S6 + " / " + B6),
    Q("6-02", "6", "The wireless spectrum (as defined by the FCC) spans...",
      ["1 Hz-1 kHz", "9 kHz-300 GHz", "2.4-5 GHz only", "300 GHz-1 THz"], "9 kHz-300 GHz",
      "Wi-Fi 6E adds the 6 GHz band.", S6),
    Q("6-03", "6", "Which low-power IoT protocol handles small amounts of data for building automation, HVAC, AMR (meter reading) and fleet management?",
      ["ZigBee", "802.11ac", "LTE", "Ethernet"], "ZigBee", "Why not Wi-Fi? Too power-hungry for battery devices.", S6),
    Q("6-04", "6", "Which smart-home protocol uses a hub/network controller that relays commands from your phone to devices?",
      ["Z-Wave", "RFID", "IR", "ANT+"], "Z-Wave", "Z-Wave functions: signaling (manage connections) and control (data/commands).", S6),
    Q("6-05", "6", "Bluetooth operates in which band, and how does it reduce interference?",
      ["5 GHz; channel bonding", "2.4 GHz; frequency hopping", "6 GHz; MIMO", "900 MHz; beamforming"], "2.4 GHz; frequency hopping",
      "Needs close proximity; range depends on device class.", S6),
    Q("6-06", "6", "An attacker SENDS unsolicited data to your Bluetooth device. That is...",
      ["Bluesnarfing", "Bluejacking", "War driving", "Evil twin"], "Bluejacking",
      "Bluesnarfing = DOWNLOADING data from the device without permission. Memory trick: SNARF = steal.", S6),
    Q("6-07", "6", "Which is TRUE about NFC?",
      ["A long-range replacement for Wi-Fi", "A very short-range form of RFID",
       "A technology that uses infrared light", "A technology that always requires a hub"],
      "A very short-range form of RFID",
      "Used for contactless payment.", S6),
    Q("6-08", "6", "RFID tags: an ARPT system is...",
      ["Active Reader Passive Tag", "Automatic Radio Proximity Tag", "Active Reader Powered Transmitter",
       "Access Router Passive Transmitter"],
      "Active Reader Passive Tag",
      "Combos: ARPT, PRAT (Passive Reader Active Tag), ARAT (Active Reader Active Tag). Active tag = has its own battery. "
      "Common use: inventory management. The study guide says 'RFID: tags, active vs passive'.", S6),
    Q("6-09", "6", "Which wireless technology sits just BELOW visible light and is used for sensors and remote controls?",
      ["RFID (radio tags)", "Infrared (IR)", "Z-Wave (smart home)", "ZigBee (IoT mesh)"], "Infrared (IR)", "Infrared sits just below visible light, needs line of sight and is used for remote controls and "
                                                                                                           "simple sensors. ZigBee and Z-Wave are radio technologies, and RFID uses radio tags.", S6),
    Q("6-10", "6", "An antenna that sends signal in a single direction (for point-to-point links) is...",
      ["Omnidirectional (all directions)", "Unidirectional (one direction)", "Isotropic (equal everywhere)",
       "MIMO (many antennas at once)"], "Unidirectional (one direction)",
      "Omnidirectional = roughly equal strength in all directions (good for many mobile clients). Two antennas must be "
      "tuned to the same FREQUENCY to communicate.", S6),
    Q("6-11", "6", "A signal weakens as it moves away from the antenna. This is ____ and can be fixed by ____.",
      ["Refraction; turning on MAC filtering", "Attenuation; more power or a repeater",
       "Multipath; turning off SSID broadcast", "Diffraction; switching to WPA2"],
      "Attenuation; more power or a repeater", "Attenuation is the signal weakening with distance. Fix it with more transmit power or a "
                                               "repeater/range extender. Refraction, multipath and diffraction are different effects, and MAC "
                                               "filtering, SSID broadcast and WPA2 do nothing for signal strength.", S6),
    Q("6-12", "6", "A wireless signal hits a sharp edge (a desk corner) and splits into secondary waves that seem to bend around it. That's...",
      ["Reflection", "Refraction", "Diffraction", "Scattering"], "Diffraction",
      "Reflection = bounces off LARGE smooth surfaces (walls, metal). Scattering = small or rough objects, rain. "
      "Refraction = passing INTO a different medium (glass, water) changes direction/speed. Diffraction is on the study guide.", B6),
    Q("6-13", "6", "Signals reaching the receiver over several different paths are called multipath. Pros and cons?",
      ["No advantages at all; the extra paths only cause problems",
       "Better odds of arrival, but delays can cause errors", "Only advantages, since more paths are always better",
       "It encrypts the signal across the paths"],
      "Better odds of arrival, but delays can cause errors", "Multipath means the signal reaches the receiver along several routes (reflections and so on). More "
                                                             "paths improve the odds that it arrives, but the different delays can corrupt the data.", S6),
    Q("6-14", "6", "SNR stands for ____ and a LOWER SNR means...",
      ["Signal-to-noise ratio; more noise relative to signal", "Single network route; faster speeds on the network",
       "Secure network relay; a more secure connection", "Signal node range; a longer range for each node"],
      "Signal-to-noise ratio; more noise relative to signal", "SNR = signal-to-noise ratio. A LOWER SNR means more noise compared with the signal, which is worse.", S6),
    Q("6-15", "6", "802.11ac is also called ____ and 802.11ax is ____.",
      ["Wi-Fi 4; Wi-Fi 5", "Wi-Fi 5; Wi-Fi 6", "Wi-Fi 6; Wi-Fi 7", "Wi-Fi 3; Wi-Fi 4"], "Wi-Fi 5; Wi-Fi 6",
      "802.11n = Wi-Fi 4. 802.11be = Wi-Fi 7.", S6),
    Q("6-16", "6", "Max theoretical throughput of 802.11n?",
      ["11 Mbps", "54 Mbps", "600 Mbps", "9.6 Gbps"], "600 Mbps",
      "Study guide: 'Approx. Throughput'. Book Table 6-3: b 11 Mbps (2.4 GHz), a 54 Mbps (5 GHz), g 54 Mbps (2.4), "
      "n 600 Mbps (2.4/5), ac 1.3/3.47/6.93 Gbps (5 GHz), ax 9.6 Gbps (2.4/5/6), be 46 Gbps.", B6),
    Q("6-17", "6", "Which 802.11 standard runs ONLY in the 5 GHz band?",
      ["802.11b", "802.11g", "802.11ac", "802.11n"], "802.11ac", "802.11a is also 5 GHz only. b and g = 2.4 GHz. n = both.", B6),
    Q("6-18", "6", "Which standard can use ALL three Wi-Fi bands (2.4, 5 and 6 GHz)?",
      ["802.11n (Wi-Fi 4)", "802.11ac (Wi-Fi 5)", "802.11g (2.4 GHz)", "802.11ax (Wi-Fi 6E)"], "802.11ax (Wi-Fi 6E)", "Only 802.11ax (Wi-Fi 6E) uses all three bands: 2.4, 5 and 6 GHz. 802.11n uses 2.4 and 5, 802.11ac is "
                                                                                                                      "5 GHz only and 802.11g is 2.4 GHz only.", B6),
    Q("6-19", "6", "2.4 GHz vs 5 GHz:",
      ["2.4 GHz has more throughput and a shorter range", "5 GHz has more throughput; 2.4 GHz reaches farther",
       "They are identical apart from the channel numbers", "5 GHz passes through walls better than 2.4 GHz"],
      "5 GHz has more throughput; 2.4 GHz reaches farther",
      "Band steering nudges capable clients to the better band.", B6),
    Q("6-20", "6", "In the U.S., which 2.4 GHz channels are used to avoid OVERLAP between neighboring networks?",
      ["1, 2, 3", "1, 6, 11", "1, 7, 13", "36, 40, 44"], "1, 6, 11", "Overlapping channels = interference (study guide item).", B6),
    Q("6-21", "6", "MU-MIMO (multiuser MIMO) improves on MIMO by...",
      ["Using a single antenna to cut interference", "Serving several clients at the same time",
       "Bonding two 20 MHz channels into one wider channel", "Removing encryption to reduce overhead"],
      "Serving several clients at the same time",
      "Introduced with 802.11ac Wave 2. MIMO = multiple AP and client antennas issuing signals to one or more receivers.", S6),
    Q("6-22", "6", "Combining two adjacent 20 MHz channels into one 40 MHz channel is...",
      ["Frame aggregation", "Channel bonding", "Band steering", "MIMO"], "Channel bonding",
      "It more than doubles bandwidth because no buffer is needed between them. Frame aggregation = combining frames to cut overhead.", S6),
    Q("6-23", "6", "Wi-Fi uses which access method, because radios can't detect collisions while transmitting?",
      ["CSMA/CD", "CSMA/CA", "Token passing", "Polling"], "CSMA/CA",
      "Collision AVOIDANCE: an ACK verifies every transmission. Wired Ethernet's CSMA/CD = collision DETECTION. "
      "Verifying every transmission is why Wi-Fi loses more throughput than wired.", S6 + " / " + B6),
    Q("6-24", "6", "Which optional 802.11 protocol further reduces collisions but DECREASES overall efficiency?",
      ["RTS/CTS (request to send, clear to send)", "WPA2 (a stronger security mode)",
       "SSID broadcast (the network name)", "Band steering (moving clients to 5 GHz)"],
      "RTS/CTS (request to send, clear to send)", "On the study guide.", S6),
    Q("6-25", "6", "In association, a client sending a special frame to look for APs is ____ scanning; listening for an AP's beacon is ____ scanning.",
      ["passive (beacon); active (probe)", "active (probe); passive (beacon)", "open (no key); closed (key needed)",
       "SSID (name); BSSID (MAC address)"], "active (probe); passive (beacon)", "Active scanning: the client sends probe requests to look for APs. Passive scanning: the client "
                                                                                "listens for the AP's beacon frames.", S6),
    Q("6-26", "6", "A group of stations sharing ONE access point is a...",
      ["ESS (extended service set)", "BSS (basic service set)", "VLAN (virtual LAN)", "PAN (personal area network)"], "BSS (basic service set)",
      "ESS = several APs on the same LAN sharing an ESSID, which allows roaming. In the field, ESSID = 'SSID'. "
      "Watch out for 'sticky clients' that won't roam.", S6),
    Q("6-27", "6", "Which wireless topology has nodes talking directly to each other with no AP?",
      ["Infrastructure", "Ad hoc", "Mesh", "Star"], "Ad hoc",
      "Infrastructure = clients go through an AP (which connects to a switch). Mesh = APs act as peers "
      "(e.g., city-wide Wi-Fi on streetlights with no Ethernet backhaul).", S6),
    Q("6-28", "6", "A wireless controller can provide... (choose all)",
      ["Centralized authentication of wireless clients", "Channel and power management",
       "Detection of rogue access points", "Preventing broadcast storms on wired switches"],
      ["Centralized authentication of wireless clients", "Channel and power management",
       "Detection of rogue access points"], "A wireless controller manages many APs: centralized authentication, channel and power management, "
                                            "and rogue AP detection. Broadcast storms on wired switches are prevented by STP, not by a "
                                            "controller.", S6, kind="multi"),
    Q("6-29", "6", "Before installing APs in a large building, you should do a...",
      ["A port scan of the network", "A site survey of the building", "A zone transfer between DNS servers",
       "A rollback of the wireless firmware"],
      "A site survey of the building",
      "Factors: distance, coverage, interference, density.", S6),
    Q("6-30", "6", "The most secure Wi-Fi setup in the slides combines WPA2 with a ____ server (often backed by Active Directory).",
      ["DNS", "RADIUS", "DHCP", "NTP"], "RADIUS",
      "That's WPA2-Enterprise: log on to Wi-Fi with your domain credentials. WPA-Personal/PSK = a shared passphrase.", S6 + " / " + B6),
    Q("6-31", "6", "WPA-Personal vs WPA-Enterprise: the main difference?",
      ["Enterprise uses a RADIUS authentication server", "Enterprise uses a shared passphrase for everyone",
       "Personal encrypts traffic and Enterprise does not", "There is no difference between the two modes"],
      "Enterprise uses a RADIUS authentication server", "WPA-Personal uses one shared passphrase (a pre-shared key). WPA-Enterprise authenticates each user "
                                                        "against a RADIUS server (802.1X). Both encrypt the traffic.", B6),
    Q("6-32", "6", "Which encryption is broken/obsolete and should never be used?",
      ["WPA3", "WPA2", "WEP", "AES"], "WEP",
      "WEP (Wired Equivalent Privacy) authentication options OSA and SKA are both insecure. WPA used TKIP, WPA2 uses "
      "CCMP/AES, WPA3 enforces at least 128-bit AES and protects the handshake.", B6),
    Q("6-33", "6", "The first page a new guest sees, requiring them to accept terms before getting access, is a...",
      ["Captive portal", "Evil twin", "RADIUS prompt", "Beacon"], "Captive portal",
      "Pair it with a separate GUEST network to keep visitors off your private data (book scenario: a music teacher's home).", S6),
    Q("6-34", "6", "A rogue AP posing as a legitimate one (e.g., 'Free Coffee WiFi' at the coffee shop) is a(n)...",
      ["War chalk", "Evil twin", "Bluejack", "Captive portal"], "Evil twin",
      "Prof. Norwood: war driving and war chalking are 'VERY old school', but evil twins are used all the time.", S6),
    Q("6-35", "6", "Cracking the PIN that gives access to an AP's settings is a...",
      ["WPA attack", "WPS attack", "Evil twin", "DDoS"], "WPS attack", "WPA attack = intercepting the network keys exchanged between stations and APs.", S6),
    Q("6-36", "6", "A tool that scans a frequency band for signals AND noise is a ____; a tool that evaluates Wi-Fi networks, channels and signal strength is a ____.",
      ["Wi-Fi analyzer; spectrum analyzer", "Spectrum analyzer; Wi-Fi analyzer", "protocol analyzer; port scanner",
       "cable tester; toner probe"],
      "Spectrum analyzer; Wi-Fi analyzer",
      "Slides' examples: the 'WiFi Analyzer' mobile app, a laptop with Wireshark, AirMagnet, Ekahau.", B6 + " / " + S6),
    Q("6-37", "6", "Removing a device's special permissions/apps remotely when an employee leaves is...",
      ["On-boarding with a remote install", "Off-boarding with a remote wipe", "MAC filtering of the old device",
       "Band steering to the guest network"], "Off-boarding with a remote wipe", "Off-boarding removes a departing employee's access, and a remote wipe erases company data and apps "
                                                                                 "from their device. On-boarding is the opposite: granting access.", S6),
    Q("6-38", "6", "MAC filtering on an AP...",
      ["Encrypts the traffic between the AP and every client", "Blocks devices whose MAC is not on the allowed list",
       "Hides the SSID so the network cannot be seen", "Boosts the signal strength for approved devices only"],
      "Blocks devices whose MAC is not on the allowed list",
      "802.11 has NO security by default; only the SSID is required.", S6),
    Q("6-39", "6", "In Prof. Norwood's WiFi war story, why did the client reverse its decision and pick TNS?",
      ["TNS offered the lowest price and a longer warranty on the APs",
       "TNS showed that client radios are weaker, so AP density matters",
       "The client decided that wired ports would cost less than APs",
       "TNS proposed a mesh network, which needs fewer wired drops"],
      "TNS showed that client radios are weaker, so AP density matters",
      "Lesson from the slides: 'Not understanding the tech puts you at a disadvantage!' Don't size Wi-Fi by AP radio strength alone.", "WS Lecture - WiFi"),
    Q("6-40", "6", "Which RSSI reading is the MINIMUM for reliable data delivery?",
      ["-30 dBm", "-50 dBm", "-70 dBm", "-90 dBm"], "-70 dBm",
      "-30 excellent, -50 good (VoIP/video), -70 acceptable, -80 basic connectivity only, -90 unusable. Closer to 0 = better.", B6),
]

S7 = "Ch7 slides"
B7 = "Textbook Ch7"
BANK += [
    Q("7-01", "7", "An unmanaged switch...",
      ["Has an IP address and a command-line interface", "Is plug-and-play with no IP address or configuration",
       "Supports VLANs and spanning tree configuration", "Routes traffic between different networks"],
      "Is plug-and-play with no IP address or configuration",
      "Managed switches have an IP and are configured via CLI or web GUI. VLANs require a MANAGED switch. "
      "On the study guide: managed vs unmanaged.", S7),
    Q("7-02", "7", "A switch that can interpret Layer 3 data and works like a router is a...",
      ["Layer 2 switch", "Layer 3 switch", "Hub (repeats to all ports)", "Repeater (boosts the signal)"], "Layer 3 switch", "Layer 4 switches also exist.", S7),
    Q("7-03", "7", "Redundant switch links can create traffic loops. Which protocol prevents them (choosing least-cost paths)?",
      ["OSPF (a routing protocol)", "STP (Spanning Tree Protocol)", "ARP (Address Resolution Protocol)",
       "LACP (link aggregation)"], "STP (Spanning Tree Protocol)",
      "Uncontrolled loops cause broadcast storms. On an STP network there can be only ONE root bridge.", S7 + " / " + B7),
    Q("7-04", "7", "Classic Cisco 3-tier design, from hosts up:",
      ["Core, distribution, access", "Access, distribution, core", "Spine, leaf, access", "Edge, core, cloud"],
      "Access, distribution, core",
      "Core = high-speed L3 backbone. Distribution = redundant mesh between access and core. On the study guide.", S7),
    Q("7-05", "7", "Traffic between peers WITHIN a network segment is ____; traffic leaving the segment is ____.",
      ["north-south; east-west", "east-west; north-south", "up-down; side", "inbound; outbound"], "east-west; north-south", "East-west traffic goes between peers inside a segment (server to server). North-south traffic leaves "
                                                                                                                            "the segment, for example to clients or the Internet.", S7),
    Q("7-06", "7", "Spine-and-leaf architecture...",
      ["Adds a fourth layer of switches above the core layer",
       "Collapses the core; every spine connects to every leaf", "Connects every spine to the other spines in a ring",
       "Is a design that is used only for wireless networks"],
      "Collapses the core; every spine connects to every leaf",
      "It was built for heavy east-west traffic (virtualization, SDN, cloud): lower latency, more redundancy and "
      "scalability, lower cost. Also called a collapsed core.", S7 + " / " + B7),
    Q("7-07", "7", "In SDN, which plane makes the decisions?",
      ["Infrastructure/data plane", "Control plane", "Application plane", "Management plane"], "Control plane",
      "Infrastructure (data) plane = devices that send/receive messages. Application plane = the SDN controller "
      "talking to apps via APIs. SDN is centralized and uses disaggregation/abstraction.", S7),
    Q("7-08", "7", "A SAN makes storage available to servers at the ____ level.",
      ["File", "Block", "Folder", "Byte"], "Block",
      "SAN technologies: FC (Fibre Channel, separate from Ethernet), FCoE, iSCSI (runs over TCP), InfiniBand (special hardware).", S7),
    Q("7-09", "7", "Which SAN protocol runs on top of TCP over ordinary LANs, WANs and the Internet?",
      ["Fibre Channel", "iSCSI", "InfiniBand", "SMB"], "iSCSI", "On the study guide (SAN, iSCSI).", S7),
    Q("7-10", "7", "A Type 1 hypervisor ____; a Type 2 hypervisor ____.",
      ["runs inside a host OS; installs before any OS (bare metal)",
       "installs before any OS (bare metal); runs inside a host OS",
       "is for Linux hosts only; is for Windows hosts only", "is free to use; requires a paid license for each VM"],
      "installs before any OS (bare metal); runs inside a host OS",
      "Examples: Type 1 = Hyper-V/ESXi. Type 2 = VirtualBox/VMware Workstation. Study guide: 'Type 1 vs. 2, Bare-metal'.", S7),
    Q("7-11", "7", "Physical computer = ____; each VM = ____; software that creates/manages VMs = ____.",
      ["guest; host; hypervisor", "host; guest; hypervisor", "hypervisor; host; guest", "server; client; NOS"],
      "host; guest; hypervisor", "The physical computer is the HOST, each virtual machine is a GUEST, and the hypervisor is the "
                                 "software that creates and manages the VMs.", S7),
    Q("7-12", "7", "Which VM networking mode gets its IP from the PHYSICAL LAN's DHCP server and looks like any other node?",
      ["NAT", "Host-only", "Bridged", "Isolated"], "Bridged",
      "NAT mode = the host acts as NAT and the hypervisor is the DHCP server. Host-only = VMs talk only to each other "
      "and the host, never through the physical NIC.", S7 + " / " + B7),
    Q("7-13", "7", "The virtual switch that connects VMs' vNICs is called a...",
      ["vSwitch (a virtual switch run by the hypervisor)",
       "Patch panel (a virtual cable organizer in the hypervisor)",
       "Hub (a virtual repeater that copies frames to every VM)",
       "Router (a virtual router that forwards between VM networks)"],
      "vSwitch (a virtual switch run by the hypervisor)",
      "It works primarily at the data link layer. One host can run multiple vSwitches. Study guide: vSwitch, distributed switching.", S7),
    Q("7-14", "7", "Which are ADVANTAGES of virtualization? (choose all)",
      ["Efficient use of resources", "Cost and energy savings", "Fault and threat isolation", "Simple backups, recovery and replication", "Single point of failure"],
      ["Efficient use of resources", "Cost and energy savings", "Fault and threat isolation", "Simple backups, recovery and replication"],
      "Disadvantages: compromised performance, increased complexity, increased licensing costs, single point of failure.", S7, kind="multi"),
    Q("7-15", "7", "Prof. Norwood's NFV caution:",
      ["Virtual firewalls are best placed at the network edge",
       "Virtual devices need licenses; avoid a virtual firewall at the edge",
       "NFV has no real downsides compared with physical devices",
       "NFV only works for devices that run inside a public cloud"],
      "Virtual devices need licenses; avoid a virtual firewall at the edge", "The professor's NFV caution: you need a license for each virtual device, there is latency between "
                                                                             "the physical and virtual worlds, and a virtual firewall at the network edge is NOT best practice.", S7),
    Q("7-16", "7", "Which TWO technologies enabled cloud computing (slide answer)?",
      ["Wi-Fi and Bluetooth for mobile devices", "Cheap, fast Internet and server virtualization",
       "IPv6 addressing and global DNS services", "RAID arrays and tape backup libraries"],
      "Cheap, fast Internet and server virtualization", "Cloud computing took off because of cheap, fast Internet access and server virtualization, which "
                                                        "lets many customers share the same hardware (multi-tenant).", S7),
    Q("7-17", "7", "'Bring your own application and data' (the provider gives the hardware + OS + libraries) is...",
      ["IaaS", "PaaS", "SaaS", "On-prem"], "PaaS",
      "IaaS = bring your OS, app and data. PaaS = bring your app and data. SaaS = bring only your data. On the study guide.", S7),
    Q("7-18", "7", "Gmail / Office 365, where you only bring your data, is...",
      ["IaaS", "PaaS", "SaaS", "Private cloud"], "SaaS", "SaaS: the provider runs everything and you only bring your data (Gmail, Office 365). IaaS = bring "
                                                         "the OS, app and data; PaaS = bring the app and data.", S7),
    Q("7-19", "7", "A cloud shared between several organizations is a ____ cloud.",
      ["Public", "Private", "Community", "Hybrid"], "Community",
      "Hybrid = combination of models. Prof. Norwood: 'private cloud' is an abused term, since being virtualized "
      "alone doesn't make it a private cloud (it also needs automation, elasticity, etc.).", S7),
    Q("7-20", "7", "Automating many cloud tasks to work together in a complex workflow is...",
      ["Automation of one task", "Orchestration", "Infrastructure as code (IaC)", "Elasticity"], "Orchestration",
      "IaC = text-based config files that create/manage cloud resources. Automation = a programmed response to one specific event.", S7 + " / " + B7),
    Q("7-21", "7", "MTBF vs MTTR:",
      ["MTBF = average repair time; MTTR = average time between failures",
       "MTBF = average time until the next failure; MTTR = average repair time",
       "They are the same measure; MTBF is simply the older name for it",
       "Both measure how much bandwidth a device can carry before failing"],
      "MTBF = average time until the next failure; MTTR = average repair time", "On the study guide.", S7),
    Q("7-22", "7", "A duplicate component already INSTALLED that takes over automatically if the original fails is a...",
      ["Cold spare", "Hot spare", "Warm site", "Snapshot"], "Hot spare",
      "Cold spare = on the shelf, installed only after a failure. Hot-swappable = can be replaced while the machine runs.", S7),
    Q("7-23", "7", "Combining multiple NICs into one logical interface (e.g., NIC teaming) gives... (choose all)",
      ["Increased total throughput", "Automatic failover", "Load balancing", "Encryption"],
      ["Increased total throughput", "Automatic failover", "Load balancing"],
      "This is link (port) aggregation. LACP is the protocol most often used to bond switch-to-server links.", S7 + " / " + B7, kind="multi"),
    Q("7-24", "7", "Grouping multiple servers so they appear as one device, represented by a VIP, is...",
      ["Clustering", "Spanning tree", "VLAN tagging", "NAT"], "Clustering",
      "A load balancer distributes traffic among them, and the public VIP attaches to the load balancer.", S7 + " / " + B7),
    Q("7-25", "7", "The main disadvantage of redundancy is...",
      ["Lower availability", "Added cost", "Slower network speeds", "Weaker security"], "Added cost", "Redundancy (spares, duplicate links, clusters) improves availability, but it costs more hardware, "
                                                                                                      "licensing and complexity. Cost is the main disadvantage.", S7),
    Q("7-26", "7", "Availability vs fault vs failure:",
      ["A fault is one component malfunctioning that may cause a failure",
       "Fault and failure mean the same thing in networking, per the book",
       "A failure always causes a fault, and never the other way around",
       "Availability is the total cost of keeping the system running"],
      "A fault is one component malfunctioning that may cause a failure",
      "HA = functions reliably nearly all the time. Uptime: the 'uptime' command on Linux, Task Manager on Windows.", S7),
    Q("7-27", "7", "Why did Cisco push the 3-tier (edge-distribution-core) design in the late 1990s? (slide discussion)",
      ["Purely for technical performance reasons", "Partly technical, but it also sold more switches",
       "Because Wi-Fi was spreading in offices", "Because IPv6 was being rolled out then"],
      "Partly technical, but it also sold more switches",
      "This was a discussion prompt ('Technical? Other?'), so treat it as context more than a likely exam fact.", S7),
]

S8 = "Ch8 slides"
B8 = "Textbook Ch8"
BANK += [
    Q("8-01", "8", "Segmenting a network into smaller networks gives which benefits? (choose all)",
      ["Enhanced security", "Improved performance", "Simplified troubleshooting", "More broadcast traffic"],
      ["Enhanced security", "Improved performance", "Simplified troubleshooting"],
      "Each segment is its own broadcast domain. Segment by geography, department or device type.", S8, kind="multi"),
    Q("8-02", "8", "A subnet mask's 1 bits mark the ____ portion; 0 bits mark the ____ portion.",
      ["host; network", "network; host", "MAC; IP", "port; socket"], "network; host",
      "192.168.123.132 with mask 255.255.255.0 gives network ID 192.168.123.0 and host portion .132.", S8),
    Q("8-03", "8", "Default masks for Class A, B, C are...",
      ["/8, /16, /24", "/16, /24, /32", "/4, /8, /16", "/24, /16, /8"], "/8, /16, /24",
      "So a Class A uses 24 bits for hosts. The 'problem' with classful: you only get ~16M, 65K, or 254 hosts. Way too coarse.", S8),
    Q("8-04", "8", "In CIDR notation 192.168.89.127/24, what does 24 mean?",
      ["A maximum of 24 hosts can be on the network", "The mask has 24 one-bits (network bits)",
       "The network is split into 24 subnets", "The address uses port 24 on the host"],
      "The mask has 24 one-bits (network bits)", "Called a CIDR block.", S8),
    Q("8-05", "8", "Subnetting BORROWS host bits to use for the network. The effect is...",
      ["More hosts on each network, but fewer networks", "More networks, but fewer hosts on each",
       "Fewer networks and fewer hosts overall", "No change to the number of networks or hosts"],
      "More networks, but fewer hosts on each", "Subnetting = classless addressing.", S8),
    Q("8-06", "8", "How many USABLE host addresses in a /26?",
      ["64", "62", "30", "126"], "62", "Host bits = 32-26 = 6. 2^6 = 64 total minus network and broadcast = 62.", S8),
    Q("8-07", "8", "A server's mask is 255.255.255.224. How many bits identify the host?",
      ["27", "8", "5", "3"], "5", "224 = 11100000, so the mask is /27 and 32-27 = 5 host bits (30 usable hosts).", B8),
    Q("8-08", "8", "Two University of Utah ranges from the slides: 155.96.0.0/13 has how many addresses?",
      ["65,536", "262,144", "524,288", "1,048,576"], "524,288", "2^(32-13) = 2^19 = 524,288. And 128.110.0.0/16 = 65,536.", S8),
    Q("8-09", "8", "Midterm subnetting questions (from the Ch8 slides): 'Midterm will have one of each' of which types?",
      ["VLSM problems with unequal subnet sizes, and IPv6 problems",
       "Subnets from requirements, and network ID from a host IP", "Only binary-to-decimal conversion problems",
       "Only hexadecimal conversion problems"],
      "Subnets from requirements, and network ID from a host IP",
      "Plus simple ones like 'how many hosts with a /26'. The Subnetting lecture adds: unequal-size (VLSM) problems will NOT be tested.", S8 + " / Subnetting lecture"),
    Q("8-10", "8", "One DHCP server must serve several subnets. What lets DHCP requests cross the router?",
      ["NAT on the edge router facing the ISP", "A DHCP relay agent on the router",
       "STP running on the access layer switches", "A hub placed between the two subnets"],
      "A DHCP relay agent on the router",
      "The router forwards the broadcast to the DHCP server, which uses the relay agent's IP to pick the right subnet. "
      "On the study guide ('Relay agents').", S8),
    Q("8-11", "8", "VLSM vs CLSM:",
      ["They are the same method; CLSM is just the newer name",
       "VLSM uses subnets of different sizes; CLSM uses equal sizes",
       "CLSM is the version of subnetting designed only for IPv6",
       "VLSM can only be used on Class C networks with a /24 mask"],
      "VLSM uses subnets of different sizes; CLSM uses equal sizes",
      "Expect a longhand CLSM question on the midterm. VLSM won't be tested.", S8 + " / Subnetting lecture"),
    Q("8-12", "8", "IPv6 subnetting: which is TRUE?",
      ["Uses address classes A, B and C to size each subnet", "Uses dotted-decimal subnet masks like IPv4 does",
       "Classless; one subnet holds 2^64 addresses", "Allows a maximum of 254 hosts in each IPv6 subnet"],
      "Classless; one subnet holds 2^64 addresses",
      "First 4 blocks = network prefix, last 4 = interface. Study guide: 'IPv6 basics: classless, prefix, hop limits'.", S8),
    Q("8-13", "8", "A VLAN...",
      ["Is a special type of router for VLAN traffic", "Groups switch ports into separate broadcast domains",
       "Encrypts the traffic between two switches", "Requires a separate physical switch for each group"],
      "Groups switch ports into separate broadcast domains",
      "VLAN member ports don't have to be next to each other. VLANs need a MANAGED switch.", S8),
    Q("8-14", "8", "Reasons to use VLANs (choose all)",
      ["Isolate heavy-traffic connections", "Identify priority traffic (e.g., voice)", "Separate users needing special security",
       "Temporary/test networks", "Reduce the cost of networking equipment", "Make one huge broadcast domain for the whole building"],
      ["Isolate heavy-traffic connections", "Identify priority traffic (e.g., voice)", "Separate users needing special security",
       "Temporary/test networks", "Reduce the cost of networking equipment"],
      "Also: containing legacy protocols. All five are from the slide list.", S8, kind="multi"),
    Q("8-15", "8", "Which IEEE standard defines VLAN tagging in Ethernet frames?",
      ["802.11", "802.1Q", "802.3af", "802.1X"], "802.1Q", "802.1X = port-based authentication. 802.3af = PoE.", S8 + " / " + B8),
    Q("8-16", "8", "A switch port connecting a single end device (one VLAN) is ____; a port carrying MULTIPLE VLANs is ____.",
      ["trunk (tagged); access", "access; trunk (tagged)", "native; default", "uplink; downlink"], "access; trunk (tagged)",
      "Prof. Norwood dislikes the word 'trunk' because it also means link aggregation; he says 'tagged port'.", S8),
    Q("8-17", "8", "Subnetting operates at the ____ layer; VLANs at the ____ layer.",
      ["physical (1); data link (2)", "network (3); data link (2)", "data link (2); network (3)",
       "transport (4); network (3)"], "network (3); data link (2)",
      "Usually each VLAN gets its own subnet.", B8),
    Q("8-18", "8", "TRUE or FALSE: Traffic between two computers on the SAME VLAN must go through the router.",
      None, "False", "Same-VLAN traffic is switched normally. Traffic BETWEEN VLANs (inter-VLAN routing) goes through the router.", B8, kind="tf"),
    Q("8-19", "8", "An attacker double-tags a frame to reach a protected VLAN. This is...",
      ["Switch spoofing", "VLAN hopping", "MAC flooding", "Evil twin"], "VLAN hopping", "VLAN hopping: an attacker double-tags a frame (or tricks a trunk) to reach a VLAN they shouldn't. "
                                                                                        "Switch spoofing is a related attack, MAC flooding fills the switch's address table, and an evil twin "
                                                                                        "is a Wi-Fi attack.", B8),
    Q("8-20", "8", "On which device do you configure VLANs?",
      ["A router on the edge", "A managed switch", "An end-user PC", "A Wi-Fi client"], "A managed switch", "VLANs are configured on managed switches (assign ports to VLANs and tag the trunks). Routers route "
                                                                                                            "between VLANs; endpoints don't configure them.", B8),
    Q("8-21", "8", "Each network created by segmenting/subnetting is its own...",
      ["Collision domain only", "Broadcast domain", "DNS zone for the subnet", "VLAN tag on every frame"], "Broadcast domain",
      "Routers (and VLANs + routers) bound broadcast domains. 'Broadcast domains' is on the study guide.", S8),
    Q("8-22", "8", "How does a computer decide whether to send a packet directly or to the default gateway?",
      ["It asks the DNS server which path the packet should take",
       "It compares its own network ID with the destination's", "It always sends every packet to the default gateway",
       "It broadcasts a request and sends to whoever replies"],
      "It compares its own network ID with the destination's", "A host ANDs the destination with its own mask and compares the result with its own network ID. Same "
                                                               "network: deliver directly (ARP for the destination). Different network: send to the default gateway.", B8),
]

S12 = "Ch12 slides"
B12 = "Textbook Ch12"
BANK += [
    Q("12-01", "12", "A network MONITOR vs a PROTOCOL ANALYZER:",
      ["They are the same tool; analyzer is just the newer name",
       "A monitor tracks traffic flows; an analyzer captures frames",
       "An analyzer is only available as a hardware device", "A monitor encrypts the traffic it watches on the wire"],
      "A monitor tracks traffic flows; an analyzer captures frames", "A monitor shows traffic types, flows and volume. A protocol analyzer (Wireshark) captures every "
                                                                     "frame in detail. Analyzers are usually software.", S12),
    Q("12-02", "12", "Copying all traffic from switch ports to one port where a monitoring PC listens is...",
      ["Port mirroring (SPAN)", "Port security (MAC limits)", "Trunking (tagged VLAN links)",
       "NAT (address translation)"], "Port mirroring (SPAN)",
      "Alternative: an in-line network TAP. Study guide: 'Taps, Mirror/span, Wireshark'.", S12),
    Q("12-03", "12", "Which errors can monitoring tools identify? (choose all)",
      ["Runts", "Giants", "Jabber", "Packet loss / discards", "Interface resets", "Misspelled words in users' e-mail messages"],
      ["Runts", "Giants", "Jabber", "Packet loss / discards", "Interface resets"],
      "Runt = too-small frame, giant = too-large frame, jabber = a device continuously sending garbage.", S12, kind="multi"),
    Q("12-04", "12", "Syslog roles: the monitored computer issuing events is the ____; the one gathering messages is the ____.",
      ["collector; generator", "generator; collector", "agent; MIB", "client; server"], "generator; collector",
      "Windows uses the Event log viewed in Event Viewer. Syslog = UDP 514.", S12),
    Q("12-05", "12", "In SNMP, the NMS gathering data from managed devices is called ____, and the 'data dictionary' of device definitions is the ____.",
      ["trapping; the OID table", "polling; the MIB database", "pinging; the ARP table", "logging; the syslog file"],
      "polling; the MIB database", "An agent on each managed device collects and reports data. SNMP agents listen on UDP 161; traps go to 162.", S12 + " / " + B12),
    Q("12-06", "12", "Which SNMP version is the most secure?",
      ["v1", "v2", "v2c", "v3"], "v3", "v2 is still widely used. v1 is the original and rarely used.", S12),
    Q("12-07", "12", "A report of the network's NORMAL operating state is a...",
      ["Baseline", "SLA", "Audit log", "Snapshot"], "Baseline",
      "'If you don't know what is normal, it's extremely difficult to troubleshoot.' Metrics: utilization, error rate, "
      "packet drops, response time.", S12),
    Q("12-08", "12", "Prioritizing delay-sensitive VoIP/video during congestion is...",
      ["Flow control (receiver limits)", "QoS (quality of service)", "Congestion control (open-loop)",
       "Port mirroring (SPAN)"], "QoS (quality of service)",
      "Flow control = between TWO devices so the receiver isn't overwhelmed (also a TCP feature). Congestion control: "
      "open-loop prevents it, closed-loop fixes it after it starts.", S12),
    Q("12-09", "12", "Congestion control that PREVENTS congestion before it occurs is ____; that remedies it after it starts is ____.",
      ["closed-loop; open-loop", "open-loop; closed-loop", "QoS; flow control", "FIFO queues; LIFO queues"], "open-loop; closed-loop", "Open-loop congestion control PREVENTS congestion before it occurs (for example shaping or admission "
                                                                                                                                       "control). Closed-loop REMEDIES it after it starts, using feedback to slow senders down.", S12),
    Q("12-10", "12", "An event with adverse effects on network availability/resources is an ____; an extreme one with an outage affecting more than one system is a ____.",
      ["outage; incident", "incident; disaster", "fault; failure", "alert; alarm"], "incident; disaster", "An incident is any event with adverse effects on network availability or resources. A disaster is an "
                                                                                                          "extreme incident, such as an outage that affects more than one system.", S12),
    Q("12-11", "12", "Order the 6 incident-response stages:",
      ["Detection, preparation, containment, recovery, remediation, review",
       "Preparation, detection, containment, remediation, recovery, review",
       "Containment, preparation, review, recovery, detection, remediation",
       "Review, recovery, remediation, containment, detection, preparation"],
      "Preparation, detection, containment, remediation, recovery, review",
      "Incident response begins BEFORE the incident (preparation). The team should include a dispatcher, tech support "
      "specialist, manager, PR specialist... and a lawyer.", S12),
    Q("12-12", "12", "Which DR site has components that MATCH the network's current state, all configured, updated and connected?",
      ["Cold", "Warm", "Hot", "Cloud"], "Hot",
      "Cold = components exist but aren't configured/connected (can take weeks). Warm = some configured. Hot = ready "
      "(and most expensive). On the study guide twice.", S12),
    Q("12-13", "12", "A momentary DECREASE in voltage is a...",
      ["Surge (spike)", "Brownout (sag)", "Blackout (total loss)", "Noise (EMI)"], "Brownout (sag)",
      "Surge/spike = momentary INCREASE (lightning). Noise = fluctuation from EMI or other devices. Blackout = complete loss. "
      "Study guide: brownout, sags, spikes.", S12),
    Q("12-14", "12", "Which UPS continuously powers the device FROM ITS BATTERY (with AC constantly recharging it)?",
      ["Standby UPS", "Online UPS", "Generator", "PDU"], "Online UPS",
      "Standby UPS switches to battery only when it detects a power loss. Online = no switchover gap.", S12 + " / " + B12),
    Q("12-15", "12", "Generators: which statement is TRUE?",
      ["They make UPS units unnecessary because they start instantly",
       "They supply power in long blackouts and fuel must be checked",
       "They run only on batteries that recharge from AC power", "They clean noisy power without any other equipment"],
      "They supply power in long blackouts and fuel must be checked", "Generators supply power during extended blackouts (diesel, propane, natural gas, steam). A UPS "
                                                                      "covers short outages and the switchover, so the two are combined, and the fuel must be checked "
                                                                      "regularly.", S12),
    Q("12-16", "12", "The 3-2-1-1 backup rule means...",
      ["3 servers, 2 sites, 1 cloud copy, 1 tape copy", "3 copies, 2 media types, 1 offsite, 1 offline",
       "3 full, 2 incremental, 1 differential, 1 snapshot", "3 days kept, 2 weeks kept, 1 month, 1 year"],
      "3 copies, 2 media types, 1 offsite, 1 offline",
      "Why offline? Ransomware/attackers can't encrypt or delete what isn't connected. Prof. Norwood: what matters "
      "is the ability to RESTORE.", S12),
    Q("12-17", "12", "Which backup copies data changed since the LAST FULL backup (and grows each day until the next full)?",
      ["Full", "Incremental", "Differential", "Snapshot"], "Differential",
      "Incremental = changes since the last backup of ANY kind (smallest, but a restore needs the full + every "
      "incremental). Full = everything (slowest backup, fastest restore). On the study guide.", B12),
    Q("12-18", "12", "Which backup type, done daily, gives the lowest RTO (fastest restore)?",
      ["Incremental", "Full", "Archive", "Differential"], "Full", "A full backup restores fastest (one set of media), so done daily it gives the lowest RTO. "
                                                                  "Incremental needs the full plus every incremental; differential needs the full plus the latest "
                                                                  "differential.", B12),
    Q("12-19", "12", "RPO answers ____; RTO answers ____.",
      ["How fast must we be back up?; How much data can we lose?",
       "How much data can we lose?; How quickly must we be back up?",
       "How much does it cost?; How long does it take?", "How much bandwidth is used?; How much latency is added?"],
      "How much data can we lose?; How quickly must we be back up?", "Lower RPO/RTO = higher cost.", S12),
    Q("12-20", "12", "Replication vs snapshot:",
      ["They are the same feature; the vendors just name it differently",
       "Replication copies data live; a snapshot freezes it in time",
       "A snapshot copies the data to an offsite location", "Replication is an offline copy that is kept on tape"],
      "Replication copies data live; a snapshot freezes it in time", "Replication copies data live to another location. A snapshot freezes storage blocks so you can go "
                                                                     "back to an earlier point in time; it is not an offsite copy by itself.", S12),
    Q("12-21", "12", "Which RAID level MIRRORS data (100% overhead)?",
      ["RAID 0", "RAID 1", "RAID 5", "RAID 6"], "RAID 1",
      "RAID 0 = striping, no redundancy (0% overhead). RAID 5 = striping + parity, 3+ drives, survives 1 failure. "
      "RAID 10 = mirrored pairs then striped (4+ disks). RAID 6 = dual parity, survives 2 failures (popular with big drives).", S12),
    Q("12-22", "12", "Which RAID level offers NO fault tolerance?",
      ["RAID 0", "RAID 1", "RAID 5", "RAID 10"], "RAID 0", "Striping only: lose one disk and you lose everything.", S12),
    Q("12-23", "12", "Minimum drives for RAID 5? For RAID 10?",
      ["2; 3", "3; 4", "4; 6", "5; 10"], "3; 4", "RAID 5 needs at least 3 drives (striping with parity). RAID 10 needs at least 4 (mirrored pairs that "
                                                 "are then striped).", S12),
    Q("12-24", "12", "Why is RAID 6 becoming popular?",
      ["It gives the fastest write speed of any RAID level in use",
       "Big drives rebuild slowly; RAID 6 survives two failed drives",
       "It uses no parity, so it needs fewer drives than RAID 5", "It is built into every operating system for free"],
      "Big drives rebuild slowly; RAID 6 survives two failed drives",
      "Related to the slide discussion: 'RAID 5 has low overhead, why not always use RAID 5?'", S12),
    Q("12-25", "12", "NAS vs SAN (study guide item):",
      ["They are identical; NAS is just the older name for a SAN",
       "NAS gives file-level storage; SAN gives block-level storage",
       "SAN gives file-level storage; NAS gives block-level storage",
       "NAS uses Fibre Channel; SAN uses only Ethernet"],
      "NAS gives file-level storage; SAN gives block-level storage", "NAS = file-level storage on the LAN. SAN = a separate high-speed network (Fibre Channel, iSCSI) that "
                                                                     "gives servers BLOCK-level storage.", S12 + " / " + S7),
    Q("12-26", "12", "Which log type proves WHO did WHAT and WHEN?",
      ["Traffic log", "Audit log", "System log", "Syslog"], "Audit log", "An audit log records WHO did WHAT and WHEN. System logs and syslog record events from systems and "
                                                                         "devices; a traffic log records traffic.", B12),
    Q("12-27", "12", "Network slowdown this morning: which documentation helps you see what changed?",
      ["SLA", "DR plan", "Baseline", "Audit report"], "Baseline", "A baseline records what normal looks like (utilization, errors, drops, response time), so comparing "
                                                                  "it with today shows what changed. An SLA is a contract and a DR plan is for disasters.", B12),
    Q("12-28", "12", "To limit how much bandwidth your roommate's PC can use, configure...",
      ["Congestion control", "Flow control", "Traffic shaping", "Power management"], "Traffic shaping", "Traffic shaping limits how much bandwidth a device or application may use. Flow control protects a "
                                                                                                        "receiver, and congestion control manages overall overload.", B12),
    Q("12-29", "12", "Which tool examines the TCP messages exchanged between a server and a client?",
      ["Spiceworks", "Wireshark", "iPerf", "NetFlow"], "Wireshark", "Wireshark is a protocol analyzer that captures and decodes frames, including the TCP messages "
                                                                    "between a client and a server. NetFlow shows flows and iPerf measures throughput.", B12),
]

L = "L"
BANK += [
    Q("L-01", L, "A frame crosses a ROUTER (no NAT). Which addresses get REWRITTEN?",
      ["Source and destination IP addresses", "Source and destination MAC addresses",
       "Source and destination port numbers", "Nothing; the frame passes through unchanged"],
      "Source and destination MAC addresses",
      "MACs are only meaningful on the local network, so each hop builds a new frame. IPs (L3) and ports (L4) stay "
      "end-to-end unless NAT/PAT rewrites them. That's the point of the 'How a Frame Traverses' lecture.", "How a Frame Traverse lecture"),
    Q("L-02", L, "Order of headers in a frame on the wire, outermost first:",
      ["L4, L3, L2, then data", "L2, L3, L4, then the data", "L3, L2, L4, then the data", "The data, then L4, L3, L2"],
      "L2, L3, L4, then the data",
      "The lecture slide draws Data | L4 src/dst | L3 src/dst | L2 src/dst. Encapsulation wraps the data from the inside out.",
      "How a Frame Traverse lecture"),
    Q("L-03", L, "When PC-A sends to a server on ANOTHER network, the destination MAC in the first frame is...",
      ["The server's own MAC address", "The default gateway's MAC address",
       "FF:FF:FF:FF:FF:FF, the broadcast address", "The MAC address of the DNS server"],
      "The default gateway's MAC address",
      "The destination IP is the server's, but the destination MAC is the next hop's, found with ARP.", "How a Frame Traverse lecture"),
    Q("L-04", L, "In the Subnetting lecture, Table 2 is the 'high-order' bits table. Which sequence is it?",
      ["1, 2, 4, 8, 16, 32, 64, 128", "0, 128, 192, 224, 240, 248, 252, 254, 255", "255, 254, 252, 248", "8, 16, 24, 32"],
      "0, 128, 192, 224, 240, 248, 252, 254, 255",
      "Table 1 = powers of two (2^0 = 1 ... 2^12 = 4096). Table 2 = mask octet values. Build both on your scratch paper "
      "the moment the exam starts.", "Subnetting lecture", author="PROFESSOR"),
    Q("L-05", L, "CIDR, CLSM, VLSM stand for...",
      ["Classless Inter-Domain Routing; Constant Length Subnet Masking; Variable Length Subnet Masking",
       "Classful Internet Domain Routing; Common Length Subnet Masking; Very Large Subnet Masking",
       "Classless Internet Data Routing; Class Length Subnet Masking; VLAN Subnet Mapping",
       "Centralized Inter-Domain Routing; Constant Length Subnet Mapping; Variable Length Subnet Mapping"],
      "Classless Inter-Domain Routing; Constant Length Subnet Masking; Variable Length Subnet Masking",
      "Prof. Norwood says CIDR is pronounced 'cider'.", "Subnetting lecture", author="PROFESSOR"),
    Q("L-06", L, "In the subnetting war story, what happened during the all-night SAN maintenance job?",
      ["The SAN failed and the whole team spent the night restoring data",
       "The whole IT team took his subnetting exam while they waited",
       "They upgraded the Wi-Fi during the maintenance window", "They switched the whole network over to IPv6"],
      "The whole IT team took his subnetting exam while they waited",
      "His point: subnetting is the hard skill that marks a 'true' IT person.", "WS Lecture - Subnetting"),
]

# ===========================================================================
# Added questions (all written by Claude): more true/false (the real exam mixes MC and T/F), binary/hex,
# and extra Mod 7 / 8 / 12 coverage. Same sources as the rest of the bank.
# ===========================================================================
SX = "Slides + textbook"


def TF(qid, ch, statement, is_true, why, src=SX):
    return Q(qid, ch, "TRUE or FALSE: " + statement, ["True", "False"], "True" if is_true else "False", why, src, kind="tf")


BANK += [
    # ---- Module 1 ----
    TF("1-31", "1", "A router belongs to two or more networks, while a switch belongs only to its local network.", True,
       "That is the fundamental difference: the router is the gateway BETWEEN networks.", "Ch1 slides"),
    TF("1-32", "1", "A MAC address works at Layer 3 and is used to route packets across the Internet.", False,
       "MAC addresses are Layer 2 and only matter on the local network. Layer 3 IP addresses are what routers use.", "Ch1 slides"),
    TF("1-33", "1", "UDP is connectionless and does not guarantee delivery.", True,
       "UDP = 'send it and forget it': no handshake, no sequencing, no retransmission.", "Ch1 slides"),
    TF("1-34", "1", "In the troubleshooting process, you document your findings before you verify full system functionality.", False,
       "Verify full functionality FIRST, then document. Order: identify, theory, test, plan, implement/escalate, verify, document.", "Ch1 slides"),
    TF("1-35", "1", "A peer-to-peer network scales well to hundreds of computers because each PC manages its own resources.", False,
       "P2P is simple and cheap but NOT scalable: every PC keeps its own accounts and controls its own resources.", "Ch1 slides"),
    TF("1-36", "1", "The Layer 2 PDU is called a frame, and it has both a header and a trailer.", True,
       "Layer 2 is the only layer that adds a trailer as well as a header.", "Ch1 slides"),
    TF("1-37", "1", "A hub sends each incoming frame only out of the port that leads to the destination MAC address.", False,
       "A hub is a Layer 1 repeater: it sends the signal out of EVERY other port. Switches (Layer 2) use MAC addresses to pick one port.", "Ch1 slides"),
    # ---- Module 2 ----
    TF("2-31", "2", "A memorandum of understanding (MOU) is usually legally binding, while an SLA is usually not.", False,
       "It is the other way around: an MOU is usually NOT binding, and an SLA is a binding, measurable agreement.", "Ch2 slides"),
    TF("2-32", "2", "The maximum length of a horizontal twisted-pair Ethernet cable segment is 100 meters.", True,
       "100 m (328 ft). Use fiber for longer runs.", "Ch2 slides"),
    TF("2-33", "2", "A patch and an upgrade are the same type of software change.", False,
       "A patch is a correction or small improvement; an upgrade is a major change. Rollback and installation are the other two types.", "Ch2 slides"),
    TF("2-34", "2", "The demarc marks the point where the service provider's responsibility ends and yours begins.", True,
       "Whether the ISP or you pay for a failed device depends on which side of the demarc it sits.", "Ch2 slides"),
    TF("2-35", "2", "A standard equipment rack is 19 inches wide, and a full-height rack is typically 42U.", True,
       "1U = 1.75 inches, so 42U is about 6 feet.", "Ch2 slides / Textbook Ch2"),
    TF("2-36", "2", "Network documentation only needs to be written once, because networks rarely change.", False,
       "Documentation is outdated the minute it is saved, so it must be kept up to date.", "Ch2 slides"),
    # ---- Module 3 ----
    TF("3-43", "3", "A MAC address is 48 bits long, and its first 24 bits are the OUI.", True,
       "First 24 bits = OUI (manufacturer, assigned by the IEEE); last 24 bits = device ID.", "Ch3 slides"),
    TF("3-44", "3", "172.32.5.1 is a private (RFC 1918) IPv4 address.", False,
       "The private 172 range is 172.16.0.0 through 172.31.255.255. 172.32 is outside it.", "Ch3 slides"),
    TF("3-45", "3", "In an IPv6 address, the double colon (::) can be used only once.", True,
       "Using it twice would make it impossible to tell how many zero blocks each one replaced.", "Ch3 slides"),
    TF("3-46", "3", "IPv6 uses broadcast addresses in the same way IPv4 does.", False,
       "IPv6 has no broadcast. It uses unicast, multicast and anycast.", "Ch3 slides"),
    TF("3-47", "3", "Well-known port numbers are 0 through 1023.", True,
       "Registered ports are 1024-49151 and dynamic/private ports are 49152-65535.", "Ch3 slides"),
    TF("3-48", "3", "A computer that shows a 169.254.x.x address received that address from a DHCP server.", False,
       "169.254.x.x is APIPA: the PC assigned it to itself because it could NOT reach a DHCP server.", "Ch3 slides"),
    TF("3-49", "3", "A primary DNS server holds a read-only copy of a zone that it receives through zone transfers.", False,
       "That describes a SECONDARY server. The primary holds the read/write authoritative copy.", "Ch3 slides"),
    TF("3-50", "3", "Class C addresses have a first octet from 192 through 223.", True,
       "Class A 1-126, B 128-191, C 192-223, D 224-239 (multicast), E 240-254 (research).", "Ch3 slides"),
    # ---- Module 4 ----
    TF("4-34", "4", "The TCP three-way handshake is SYN, then SYN/ACK, then ACK.", True,
       "Request, response, then the connection is established.", "Ch4 slides"),
    TF("4-35", "4", "UDP provides sequencing and flow control, which is why it is used for downloads.", False,
       "UDP has neither. TCP provides sequencing, checksums and flow control.", "Ch4 slides"),
    TF("4-36", "4", "ICMP both detects network problems and fixes them automatically.", False,
       "ICMP only REPORTS problems (for example TTL expired or destination unreachable). It does not fix them.", "Ch4 slides"),
    TF("4-37", "4", "ARP finds the MAC address that goes with an IP address on the local network.", True,
       "It works by broadcast, never crosses a router, and keeps an ARP table.", "Ch4 slides"),
    TF("4-38", "4", "Telnet is more secure than SSH because it is simpler.", False,
       "Telnet sends everything, including passwords, in cleartext. SSH encrypts the session.", "Ch4 slides"),
    TF("4-39", "4", "IPsec works at the Network layer.", True,
       "SSL/TLS works higher up, at the Transport layer.", "Ch4 slides"),
    TF("4-40", "4", "Asymmetric encryption uses one shared key for both encrypting and decrypting.", False,
       "That is symmetric encryption. Asymmetric uses a public and private key pair.", "Ch4 slides"),
    TF("4-41", "4", "The standard Ethernet MTU is 1,500 bytes.", True,
       "Jumbo frames can be larger (about 9,000 to 9,198 bytes), and a VLAN tag adds 4 bytes.", "Ch4 slides"),
    # ---- Module 6 ----
    TF("6-41", "6", "Wi-Fi uses CSMA/CA because a wireless radio cannot detect collisions while it transmits.", True,
       "It avoids collisions and uses ACKs to confirm delivery. Wired Ethernet uses CSMA/CD (detection).", "Ch6 slides"),
    TF("6-42", "6", "802.11a operates in the 2.4 GHz band.", False,
       "802.11a is 5 GHz only. 802.11b and g are 2.4 GHz; n can use both.", "Ch6 slides / Textbook Ch6"),
    TF("6-43", "6", "WEP is still considered secure as long as you use a long password.", False,
       "WEP is broken and obsolete regardless of password length.", "Ch6 slides"),
    TF("6-44", "6", "NFC is a very short-range form of RFID.", True,
       "The tag can be powered by the phone through magnetic induction.", "Ch6 slides"),
    TF("6-45", "6", "In the 2.4 GHz band in the U.S., channels 1, 6 and 11 do not overlap with each other.", True,
       "Pick those three to avoid interference between neighboring access points.", "Ch6 slides"),
    TF("6-46", "6", "Bluesnarfing means sending unsolicited messages to a Bluetooth device.", False,
       "That is bluejacking. Bluesnarfing steals (downloads) data from the device.", "Ch6 slides"),
    TF("6-47", "6", "WPA2-Enterprise authenticates users with a RADIUS server instead of a shared passphrase.", True,
       "Personal mode uses a pre-shared key (PSK).", "Ch6 slides"),
    # ---- Module 7 ----
    TF("7-28", "7", "A Type 1 hypervisor installs directly on the hardware before any operating system.", True,
       "That is why it is called bare-metal. A Type 2 hypervisor runs as an application inside a host OS.", "Ch7 slides"),
    TF("7-29", "7", "With IaaS, the provider manages everything and the customer brings only the data.", False,
       "That describes SaaS. With IaaS the customer brings the OS, the application and the data.", "Ch7 slides"),
    TF("7-30", "7", "In a spine-and-leaf design, the spine switches connect to each other.", False,
       "Every spine connects to every leaf, but spines do not connect to other spines.", "Ch7 slides"),
    TF("7-31", "7", "Spanning Tree Protocol prevents switching loops and the broadcast storms they cause.", True,
       "An STP network has only one root bridge.", "Ch7 slides"),
    TF("7-32", "7", "A hot spare is already installed and takes over automatically, while a cold spare sits on a shelf.", True,
       "A cold spare is installed only after a failure.", "Ch7 slides"),
    TF("7-33", "7", "A higher MTTR is better than a lower MTTR.", False,
       "MTTR is the mean time to repair, so LOWER is better. For MTBF, higher is better.", "Ch7 slides"),
    # ---- Module 8 ----
    TF("8-23", "8", "A /24 network has 254 usable host addresses.", True,
       "2^8 = 256 addresses, minus the network and broadcast addresses.", "Ch8 slides"),
    TF("8-24", "8", "VLSM (subnets of different sizes) will be tested on the midterm.", False,
       "The professor said VLSM is not tested. A longhand CLSM (equal-size subnets) question is.", "Subnetting lecture"),
    TF("8-25", "8", "Subnetting borrows network bits so that each subnet can have more hosts.", False,
       "Subnetting borrows HOST bits to make more networks, and each network then has fewer hosts.", "Ch8 slides"),
    TF("8-26", "8", "Routers do not forward broadcasts by default, so each router interface bounds a broadcast domain.", True,
       "That is why segmenting with routers (or VLANs plus routers) shrinks broadcast domains.", "Ch8 slides"),
    TF("8-27", "8", "Only managed switches support VLANs.", True,
       "Unmanaged switches are plug-and-play and cannot be configured.", "Ch8 slides"),
    TF("8-28", "8", "The subnet mask 255.255.255.240 is written /28 in CIDR notation.", True,
       "240 = 11110000, so 24 + 4 = 28 one-bits.", "Ch8 slides"),
    # ---- Module 12 ----
    TF("12-30", "12", "A differential backup copies everything that changed since the last FULL backup.", True,
       "It grows each day until the next full backup. Incremental copies changes since the last backup of any kind.", "Ch12 slides"),
    TF("12-31", "12", "RAID 0 protects against drive failure by mirroring the data.", False,
       "RAID 0 is striping with no redundancy. RAID 1 mirrors.", "Ch12 slides"),
    TF("12-32", "12", "RPO describes how much data you can afford to lose, and RTO describes how quickly you must be back up.", True,
       "Lower RPO and RTO generally cost more.", "Ch12 slides"),
    TF("12-33", "12", "A brownout (sag) is a momentary increase in voltage.", False,
       "A brownout is a decrease. A surge or spike is a momentary increase.", "Ch12 slides"),
    TF("12-34", "12", "A cold site can take weeks to bring online.", True,
       "It has components but they are not configured or connected. A hot site is ready to go.", "Ch12 slides"),
    TF("12-35", "12", "SNMP agents send traps to the network management system on UDP port 162.", True,
       "Polling uses UDP 161.", "Ch12 slides"),
    TF("12-36", "12", "A protocol analyzer such as Wireshark shows only overall traffic volume, not individual frames.", False,
       "An analyzer captures detailed frame-by-frame data. A monitor shows flows and volume.", "Ch12 slides"),
    # ---- Lectures ----
    TF("L-07", "L", "When a packet crosses a router (with no NAT), its source and destination IP addresses are rewritten.", False,
       "Only the Layer 2 MAC addresses are rewritten at each hop. IP addresses and ports stay end to end.", "Frame traversal lecture"),
    TF("L-08", "L", "A router first picks the longest matching prefix, and uses the metric only to break a tie.", True,
       "Longest prefix match first, then the metric (fewest hops or fastest link).", "Routing tables lecture"),
    TF("L-09", "L", "On the midterm, assume CIDR is enabled, so the all-zeros and all-ones subnets are usable.", True,
       "The professor's convention: usable hosts = 2^h - 2, and no subnet is thrown away.", "Subnetting lecture / handoff notes"),
]

BANK += [
    # ---- Binary / hex / masks (Table 1 and Table 2 skills) ----
    Q("3-58", "3", "What is binary 11000000 in decimal?", ["128", "160", "192", "224"], "192",
      "128 + 64 = 192. Eight bits read left to right are 128, 64, 32, 16, 8, 4, 2, 1. It is also the third entry of Table 2.", "Subnetting lecture"),
    Q("3-59", "3", "What is decimal 172 in 8-bit binary?", ["10101100", "10101010", "11001100", "10011100"], "10101100",
      "172 = 128 + 32 + 8 + 4, so the bits are 1,0,1,0,1,1,0,0.", "Subnetting lecture"),
    Q("3-60", "3", "What is the hexadecimal value FF in decimal?", ["15", "225", "255", "256"], "255",
      "F = 15, so FF = 15 x 16 + 15 = 255. It is also 11111111 in binary.", "Ch3 slides"),
    Q("3-61", "3", "How many bits does one hexadecimal digit represent?", ["2 bits", "4 bits", "8 bits", "16 bits"], "4 bits",
      "One hex digit covers 16 values (0-F), which is 4 bits. That is why a MAC address (48 bits) is 12 hex digits.", "Ch3 slides"),
    Q("3-62", "3", "A subnet mask octet is 11111000. What is its decimal value?", ["240", "248", "252", "254"], "248",
      "128 + 64 + 32 + 16 + 8 = 248. This is the fifth entry of Table 2 (a /29 in the last octet).", "Subnetting lecture"),
    Q("3-63", "3", "Which of these is a valid value for a subnet mask octet?", ["250", "196", "224", "100"], "224",
      "Mask octets only come from Table 2: 0, 128, 192, 224, 240, 248, 252, 254, 255, because the 1-bits must be contiguous.", "Subnetting lecture"),
    Q("3-52", "3", "Which line of the ipconfig /all output shows the NIC's MAC address?",
      ["Default Gateway", "Physical Address", "DHCP Server", "DNS Servers"], "Physical Address",
      "Windows calls the MAC the Physical Address. The Big 4 settings (IP, mask, gateway, DNS) are in the same output.", "Ch3 slides"),
    Q("3-53", "3", "A host's default gateway is...",
      ["the router interface that it uses to reach other networks",
       "the DNS server that it asks to translate host names",
       "the switch port that its network cable is plugged into",
       "the DHCP server that handed it the current IP lease"],
      "the router interface that it uses to reach other networks",
      "If the destination's network ID differs from the host's own, the host sends the frame to the gateway's MAC.", "Ch3 slides"),
    Q("3-55", "3", "Which protocol uses UDP port 123?", ["NTP", "SNMP", "TFTP", "DHCP"], "NTP",
      "NTP = Network Time Protocol (123). SNMP 161/162, TFTP 69, DHCP 67/68.", "Ch4 slides"),
    Q("3-56", "3", "Which port does LDAP use by default?", ["389", "636", "443", "445"], "389",
      "LDAP is 389 and LDAPS (secure) is 636. 445 is SMB and 443 is HTTPS.", "Ch4 slides"),
    Q("3-57", "3", "A server is listening on TCP port 445. What is it most likely providing?",
      ["Windows file sharing", "Remote desktop access", "Encrypted web pages", "Network time updates"],
      "Windows file sharing", "SMB = 445. RDP is 3389, HTTPS is 443, NTP is 123. SMB is on the study guide as Windows file sharing.", "Ch3 slides"),
    Q("6-48", "6", "A client reports a signal strength of -50 dBm. How good is that signal?",
      ["Good, enough for VoIP and video", "Excellent, the best possible", "Only enough for basic connectivity", "Unusable"],
      "Good, enough for VoIP and video",
      "-30 excellent, -50 good, -70 acceptable (the minimum for reliable data), -80 basic, -90 unusable. Closer to 0 is stronger.", "Ch6 slides"),
    # ---- Mod 7 ----
    Q("7-34", "7", "In a data center that uses spine-and-leaf, the leaf switches are usually...",
      ["top-of-rack switches that the servers plug into", "core routers that connect the data center to the ISP",
       "root bridges that run Spanning Tree for the fabric", "wireless controllers that manage the access points"],
      "top-of-rack switches that the servers plug into",
      "Servers plug into leaf (ToR) switches; each leaf connects to every spine. Lots of east-west traffic is what this design is built for.", "Ch7 slides"),
    Q("7-35", "7", "Which NIST cloud characteristic means customers are billed only for what they actually use?",
      ["Measured service", "Resource pooling", "Rapid elasticity", "Broad network access"], "Measured service",
      "The five: on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service.", "Ch7 slides"),
    Q("7-36", "7", "A company keeps sensitive data in its own cloud but bursts to a provider's cloud for peaks. That is a...",
      ["hybrid cloud", "community cloud", "public cloud only", "private cloud only"], "hybrid cloud",
      "Hybrid = a combination of deployment models (here private + public).", "Ch7 slides"),
    Q("7-37", "7", "What is a vNIC?",
      ["a virtual network adapter that the hypervisor gives a VM", "a faster physical NIC that needs a special switch",
       "a physical NIC that only works on wireless networks", "a card that is installed inside the hypervisor's switch"],
      "a virtual network adapter that the hypervisor gives a VM",
      "vNICs connect to a vSwitch, which can connect to the physical NIC.", "Ch7 slides"),
    Q("7-38", "7", "Link aggregation (such as LACP) combines...",
      ["several physical links into one logical link", "several VLANs together into a single subnet",
       "several routing entries into one default route", "several DNS zones together into a single zone"],
      "several physical links into one logical link",
      "It gives more throughput, automatic failover and load balancing. NIC teaming is the server-side version.", "Ch7 slides"),
    Q("7-39", "7", "Most of the traffic in a virtualized data center moves between servers inside it. That traffic is called...",
      ["east-west traffic", "north-south traffic", "inbound traffic only", "management-plane traffic"], "east-west traffic",
      "North-south traffic leaves the segment (to the Internet or clients). East-west traffic stays inside.", "Ch7 slides"),
    # ---- Mod 8 ----
    Q("8-29", "8", "How many usable host addresses are in a /27?", ["30", "32", "14", "62"], "30",
      "2^5 = 32 addresses, minus the network and broadcast addresses = 30.", "Subnetting lecture"),
    Q("8-30", "8", "Which dotted-decimal subnet mask is /20?",
      ["255.255.240.0", "255.255.248.0", "255.255.224.0", "255.255.255.240"], "255.255.240.0",
      "/20 = 16 + 4 one-bits, so the third octet has 4 ones = 240 (Table 2).", "Subnetting lecture"),
    Q("8-31", "8", "What is the network ID of the host 192.168.10.77/26?",
      ["192.168.10.64", "192.168.10.0", "192.168.10.76", "192.168.10.128"], "192.168.10.64",
      "/26 gives a magic number of 64 in the last octet. Count 0, 64, 128... : 77 falls in the block that starts at 64 (broadcast .127).", "Subnetting lecture"),
    Q("8-32", "8", "What is the broadcast address of the host 192.168.10.77/26?",
      ["192.168.10.127", "192.168.10.255", "192.168.10.78", "192.168.10.63"], "192.168.10.127",
      "The block is .64 to .127, and the broadcast is the last address of the block.", "Subnetting lecture"),
    Q("8-33", "8", "You must split a /24 into 6 equal subnets. How many host bits do you borrow, and what is the new prefix?",
      ["3 bits, /27", "2 bits, /26", "4 bits, /28", "6 bits, /30"], "3 bits, /27",
      "2^2 = 4 is too few, 2^3 = 8 is enough (CLSM, with CIDR enabled). 24 + 3 = /27.", "Subnetting lecture"),
    Q("8-34", "8", "Each subnet must hold at least 500 hosts, and you want the smallest subnet that works. Which prefix?",
      ["/23", "/22", "/24", "/25"], "/23",
      "Smallest h with 2^h - 2 >= 500 is h = 9 (510), so the prefix is 32 - 9 = /23. A /24 only holds 254.", "Subnetting lecture"),
    Q("8-35", "8", "What is the magic number (block size) for the mask 255.255.255.192?",
      ["64", "32", "128", "192"], "64", "Magic number = 256 - 192 = 64, so the subnets start at .0, .64, .128 and .192.", "Subnetting lecture"),
    Q("8-36", "8", "Why does the professor say to 'assume CIDR is enabled' on the midterm?",
      ["So the all-zeros and all-ones subnets are usable", "So every subnet must be the same size as a Class C",
       "So only /24 networks can be subnetted", "So broadcast addresses can be assigned to hosts"],
      "So the all-zeros and all-ones subnets are usable",
      "That makes the host count 2^h - 2 and means no subnet is thrown away.", "Subnetting lecture / handoff notes"),
    Q("8-37", "8", "Which device interface bounds a broadcast domain by default?",
      ["A router interface", "A hub port", "A repeater port", "An unmanaged switch port"], "A router interface",
      "Hubs, repeaters and switches pass broadcasts along. Routers do not forward them.", "Ch8 slides"),
    # ---- Mod 12 ----
    Q("12-37", "12", "Which backup scheme needs the last full backup plus EVERY incremental since then to restore?",
      ["Incremental", "Differential", "Full", "Snapshot"], "Incremental",
      "Incremental backups are the smallest but slowest to restore. A differential restore needs only the full plus the latest differential.", "Ch12 slides"),
    Q("12-38", "12", "A company says it can lose at most 15 minutes of data. That requirement is its...",
      ["RPO", "RTO", "MTBF", "SLA uptime"], "RPO",
      "RPO = recovery point objective (how much data you can lose). RTO = how long you can be down.", "Ch12 slides"),
    Q("12-39", "12", "Which RAID level needs at least four drives and stripes data across mirrored pairs?",
      ["RAID 10", "RAID 5", "RAID 6", "RAID 1"], "RAID 10", "RAID 10 = mirrored pairs (RAID 1) that are then striped (RAID 0).", "Ch12 slides"),
    Q("12-40", "12", "Which disaster recovery site is the cheapest but slowest to bring online?",
      ["Cold site", "Warm site", "Hot site", "Mirror site"], "Cold site",
      "A cold site has only basic components, not configured. It can take weeks. A hot site is ready and the most expensive.", "Ch12 slides"),
    Q("12-41", "12", "You want to capture traffic in-line without configuring port mirroring. Which hardware do you use?",
      ["A network TAP", "A patch panel", "A KVM switch", "A rack PDU"], "A network TAP",
      "A TAP sits in the cable path and copies the traffic. Port mirroring (SPAN) is configured on a managed switch instead.", "Ch12 slides"),
    Q("12-42", "12", "In SNMP, an agent sends a trap to the NMS...",
      ["on its own when an event occurs", "only when the NMS asks it for data", "once a minute, like a ping would",
       "only after the MIB has been reset"],
      "on its own when an event occurs",
      "Polling is NMS-initiated (UDP 161). A trap is agent-initiated and goes to UDP 162.", "Ch12 slides"),
]

FLASHCARDS = [
    ("OSI layers 1-7", "Physical, Data Link, Network, Transport, Session, Presentation, Application ('Please Do Not Throw Sausage Pizza Away')"),
    ("PDUs by layer", "L1 bits, L2 frame, L3 packet, L4 segment (TCP) / datagram (UDP), L7 data/payload"),
    ("Addresses by layer", "L2 MAC (48-bit), L3 IP (32/128-bit), L4 port, L7 FQDN/host name"),
    ("Devices by layer", "Hub L1, NIC L1-2, switch L2 (L3 switch can route), router L3, firewall L3-7"),
    ("P2P vs client-server", "P2P: each PC controls its own resources, local accounts, cheap, not scalable. Client-server: domain, AD/AD DS, central control, scalable."),
    ("PAN/LAN/MAN(CAN)/WAN", "Personal (Bluetooth/NFC) < local (office) < metro/campus < wide (Internet = largest WAN)"),
    ("Troubleshooting steps", "Identify problem -> theory of probable cause -> test theory -> plan of action -> implement or escalate -> verify full functionality -> document"),
    ("ESD failures", "Catastrophic (destroyed now) vs upset (shortens life). ~10 V can damage parts; can't feel <1,500 V."),
    ("Fail-open vs fail-close", "Fail-open (fail-safe): doors unlock so no one is harmed. Fail-close (fail-secure): protects resources even if access is denied."),
    ("TIA/EIA-568", "Structured cabling standard: hierarchical, star topology"),
    ("Demarc", "Where the ISP's network ends and yours begins"),
    ("EF / MDF / IDF", "Entrance facility (service enters) / main distribution frame (central LAN+WAN interconnect) / intermediate distribution frame (floor/building closets)"),
    ("Horizontal vs backbone cabling", "Horizontal: workstation -> nearest data room (max 100 m). Backbone: EF<->MDF<->IDFs."),
    ("Rack size", "1U = 1.75 in; standard rack 42U (~6 ft); 19 in wide"),
    ("SMF vs MMF", "Single-mode: 8-10 micron core, laser, longest distance (backbone). Multimode: 50/62.5 micron, LED/laser, shorter, cheaper."),
    ("Software changes", "Patch (fix), upgrade (major), rollback (backleveling), installation. Always have a backout plan."),
    ("RFP / MOU / MSA / SOW / SLA", "Request vendor proposals / intent to agree (usually not binding) / terms for future contracts / detailed project work (binding) / measurable service levels (binding)"),
    ("MTBF / MTTR", "Mean time between failures (higher = better) / mean time to repair (lower = better)"),
    ("Nmap", "Network mapper: discovers devices. Zenmap = its GUI."),
    ("MAC address", "48 bits, 6 hex pairs; first 24 bits OUI (IEEE-assigned manufacturer ID), last 24 device ID"),
    ("Big 4 TCP/IP settings", "IP address, subnet mask, default gateway, DNS server"),
    ("IPv4 classes", "A 1-126 /8, B 128-191 /16, C 192-223 /24, D 224-239 multicast, E 240-254 research"),
    ("Private IPv4 (RFC 1918)", "10.0.0.0/8, 172.16.0.0-172.31.255.255, 192.168.0.0/16"),
    ("Special IPv4", "127.0.0.1 loopback, 169.254.x.x APIPA, 255.255.255.255 broadcast, 0.0.0.0 unassigned"),
    ("NAT / PAT", "NAT swaps private IPs for a public one (conserves IPv4); PAT tracks sessions by port so many hosts share one public IP"),
    ("IPv6 basics", "128 bits, 8 blocks of 16 bits in hex; drop leading zeros; '::' once; no broadcast; link-local FE80::/64; loopback ::1; neighbors; dual stack; tunneling"),
    ("IPv6 address types", "Unicast (global, link-local), multicast, anycast (closest of several)"),
    ("Port ranges", "Well-known 0-1023, registered 1024-49151, dynamic/private 49152-65535"),
    ("Socket", "IP:port, e.g. 10.43.3.87:23"),
    ("DNS parts", "Namespace, name servers, resolvers. Root (13 clusters) -> TLD -> authoritative. Zones."),
    ("DNS servers", "Primary (read/write, authoritative), secondary (read-only copy via zone transfer), caching, forwarding"),
    ("Recursive vs iterative", "Recursive demands a final answer (client->local server); iterative = server asks root/TLD/authoritative step by step"),
    ("DNS records", "A (IPv4), AAAA (IPv6), CNAME (alias), PTR (reverse), NS (name server), MX (mail)"),
    ("ipconfig / ifconfig / ip", "Windows / old Linux / new Linux TCP/IP config tools. ipconfig /all, /release, /renew, /flushdns"),
    ("nslookup / dig", "Query DNS (forward and reverse). dig = more detailed (Linux/macOS)."),
    ("TCP", "Connection-oriented (3-way handshake SYN, SYN/ACK, ACK), sequencing & checksums, flow control"),
    ("UDP", "Connectionless, unreliable, no handshake/sequencing/flow control, 4-field header, fast (VoIP/video, DNS, DHCP, TFTP)"),
    ("ICMP", "L3 health reporting (ping, tracert); reports but doesn't fix errors"),
    ("ARP", "Finds MAC from IP on the local network via broadcast; ARP table; arp -a"),
    ("Ethernet MTU", "1,500 bytes standard; jumbo up to 9,198; VLAN tag adds 4 bytes"),
    ("CIA triad", "Confidentiality, integrity, availability"),
    ("Symmetric vs asymmetric", "One shared key (fast, bulk data) vs public/private key pair (key exchange, identity)"),
    ("PKI / CA / certificate", "Infrastructure that ties public keys to identities / authority that issues certificates / ID info + public key"),
    ("IPsec", "Network-layer encryption suite (VPNs): initiation, key management, negotiation, data transfer, termination"),
    ("FTP / FTPS / SFTP / TFTP", "20-21 cleartext / FTP over SSL-TLS / file transfer over SSH (22) / trivial, no security, UDP 69"),
    ("Telnet vs SSH", "Remote CLI: Telnet (23) insecure; SSH (22) encrypted"),
    ("RDP vs VNC", "GUI remote control: RDP (3389) Microsoft proprietary; VNC open source"),
    ("VPN types", "Site-to-site (hardware both ends), client-to-site (aka host-to-site / remote-access / mobile user), host-to-host. VPN concentrator."),
    ("netstat", "Connections and stats: -a all, -n numeric, -e interface errors, -r routes, -o PID, -b process, -s per protocol"),
    ("tracert vs traceroute", "Windows ICMP echo vs Linux UDP; * * * = no TTL-exceeded reply"),
    ("Key ports", "20/21 FTP, 22 SSH/SFTP, 23 Telnet, 25 SMTP, 53 DNS, 67/68 DHCP, 69 TFTP, 80 HTTP, 110 POP3, 123 NTP, 143 IMAP, 161/162 SNMP, 389 LDAP, 443 HTTPS, 445 SMB, 514 syslog, 3389 RDP"),
    ("Wireless IoT radios", "ZigBee (low-power IoT), Z-Wave (smart home hub), Bluetooth (2.4 GHz hopping), ANT+ (fitness sensors), RFID, NFC (short-range RFID), IR"),
    ("Bluejacking vs bluesnarfing", "Sending unsolicited data vs stealing (downloading) data"),
    ("Propagation effects", "Fading, attenuation (fix: power or repeater), interference/SNR, multipath, reflection, refraction, scattering, diffraction"),
    ("802.11 standards", "b 2.4 GHz 11 Mbps; a 5 GHz 54; g 2.4 54; n (Wi-Fi 4) 2.4/5 600 Mbps; ac (Wi-Fi 5) 5 GHz 1.3-6.93 Gbps; ax (Wi-Fi 6/6E) 2.4/5/6 9.6 Gbps"),
    ("MIMO / MU-MIMO", "Multiple antennas / multiple antennas serving multiple clients at once (ac Wave 2)"),
    ("CSMA/CA vs CSMA/CD", "Wi-Fi collision AVOIDANCE with ACKs (+ optional RTS/CTS) vs wired Ethernet collision DETECTION"),
    ("SSID / BSS / ESS", "Network name / stations on one AP / several APs sharing an ESSID (roaming)"),
    ("Wi-Fi topologies", "Ad hoc (direct), infrastructure (AP), mesh (APs as peers)"),
    ("Wi-Fi security", "WEP (broken), WPA (TKIP), WPA2 (CCMP/AES), WPA3; Personal = PSK; Enterprise = RADIUS/802.1X"),
    ("Wi-Fi threats", "War driving, war chalking, evil twin, WPA attack, WPS PIN attack"),
    ("Captive portal / guest network", "Terms-of-use page before access / separate network for visitors"),
    ("STP", "Spanning Tree Protocol prevents switching loops/broadcast storms; one root bridge"),
    ("3-tier vs spine-leaf", "Access-distribution-core (north-south) vs spine+leaf collapsed core (east-west optimized)"),
    ("SDN planes", "Infrastructure/data (forwarding), control (decisions), application (APIs); SDN controller"),
    ("SAN protocols", "Fibre Channel, FCoE, iSCSI (over TCP), InfiniBand; block-level"),
    ("Hypervisors", "Type 1 bare-metal (before any OS) vs Type 2 hosted (app in host OS)"),
    ("VM network modes", "Bridged (IP from LAN), NAT (host is NAT, hypervisor DHCP), host-only (VMs + host only)"),
    ("Cloud service models", "IaaS (bring OS+app+data), PaaS (bring app+data), SaaS (bring data)"),
    ("Cloud deployment", "Public, private, community, hybrid (+ multicloud)"),
    ("IaC / automation / orchestration", "Config files define infra / response to one event / chained automated workflow"),
    ("Hot vs cold spare", "Installed and auto-failover vs on the shelf"),
    ("Link aggregation", "NIC teaming/LACP: throughput + failover + load balancing"),
    ("Clustering / VIP", "Many servers appear as one, addressed by a virtual IP"),
    ("Subnet mask table", "128, 192, 224, 240, 248, 252, 254, 255 (1-8 ones)"),
    ("Hosts in /n", "2^(32-n) - 2 usable"),
    ("DHCP relay", "Router forwards DHCP broadcasts to a server on another subnet ('IP helper address')"),
    ("VLAN / 802.1Q", "Logical broadcast domains on managed switches; tag added to frames; access vs trunk (tagged) ports"),
    ("VLSM vs CLSM", "Different-size subnets (largest first, NOT on midterm) vs same-size subnets (ON midterm)"),
    ("Monitor vs analyzer", "Traffic flow/volume vs frame-by-frame capture (Wireshark)"),
    ("Mirror/SPAN vs TAP", "Switch copies traffic to a port vs in-line device"),
    ("Runt / giant / jabber", "Too-small frame / too-big frame / device sending garbage continuously"),
    ("SNMP", "NMS polls agents on managed devices; MIB; v3 most secure; UDP 161 (traps 162)"),
    ("Baseline", "Record of normal operation, used to spot abnormal"),
    ("QoS / flow / congestion control", "Prioritize traffic / don't overwhelm the receiver / open-loop prevents, closed-loop remedies"),
    ("Incident response stages", "Preparation, detection & identification, containment, remediation, recovery, review"),
    ("Hot / warm / cold site", "Fully ready / partly configured / components only"),
    ("Power problems", "Surge/spike (up), brownout/sag (down), noise (fluctuation), blackout (none)"),
    ("UPS types", "Standby (switches to battery on loss) vs online (always on battery)"),
    ("Backup types", "Full (everything), incremental (since last backup), differential (since last FULL)"),
    ("3-2-1-1", "3 copies, 2 media, 1 offsite, 1 offline"),
    ("RPO / RTO", "Max data loss / max downtime"),
    ("RAID", "0 stripe (no redundancy), 1 mirror, 5 stripe+parity (3+ disks), 10 mirror+stripe (4+), 6 double parity"),
]


FLASHCARDS += [
    ("Binary place values", "One octet, left to right: 128, 64, 32, 16, 8, 4, 2, 1. Add the values of the 1-bits. 11000000 = 192."),
    ("Hexadecimal", "Base 16: 0-9 then A=10 ... F=15. One hex digit = 4 bits, two digits = one octet. FF = 255. A MAC is 12 hex digits."),
    ("Subnetting Table 1", "Powers of 2: 2^0=1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 2^12=4096. Build it first on scratch paper."),
    ("Subnetting Table 2", "High-order bits: 0, 128, 192, 224, 240, 248, 252, 254, 255 (zero through eight 1-bits in an octet). Mask octets only use these values."),
    ("Magic number", "256 minus the mask octet where the mask stops being 255. It is the block size: count up by it to find the network."),
    ("CIDR problem steps", "1) find the octet where the mask stops being 255, 2) magic number = 256 - that mask octet, 3) count up by it to the block holding the address = network, 4) broadcast = next block - 1."),
    ("CLSM problem steps", "1) smallest h with 2^h - 2 >= hosts, 2) new prefix = 32 - h, 3) list the blocks (count up by the block size). Assume CIDR is enabled (all-zeros and all-ones subnets usable)."),
    ("Usable hosts", "2^h - 2, where h = host bits = 32 - prefix. Subtract the network and broadcast addresses."),
    ("Slash to mask", "/n = n one-bits. /8 255.0.0.0, /16 255.255.0.0, /24 255.255.255.0, /25 .128, /26 .192, /27 .224, /28 .240, /29 .248, /30 .252."),
    ("Broadcast domain", "Devices that hear each other's broadcasts. A router interface (or a VLAN) bounds it. Hubs and switches don't."),
    ("Collision domain", "Devices that can collide on a shared medium. A hub is one big collision domain; every switch port is its own."),
    ("Default gateway", "The router interface a host sends to when the destination's network ID differs from its own."),
    ("Hub vs switch vs router", "Hub: Layer 1, repeats to all ports. Switch: Layer 2, forwards by MAC. Router: Layer 3, forwards by IP between networks."),
    ("APIPA", "169.254.x.x: a Windows PC's self-assigned address when it can't reach a DHCP server."),
    ("DHCP steps (DORA)", "Discover (broadcast), Offer, Request, Acknowledge. UDP 67 (server) / 68 (client). Lease, scope (pool), reservation."),
    ("DHCP lease / scope / reservation", "Lease = how long an address is loaned (shorter recycles faster). Scope = the pool. Reservation = the same IP always goes to one MAC."),
    ("SLAAC / link-local", "SLAAC: an IPv6 host builds its own address. Link-local FE80::/64 is self-configured and only valid on the local link."),
    ("IPv6 shortening", "Drop leading zeros in each block, then replace ONE run of all-zero blocks with ::. The interface ID is the last 64 bits."),
    ("Routing table lookup", "Longest prefix match first (most specific route), then the metric (fewest hops or fastest link) breaks ties. 0.0.0.0/0 is the default route."),
    ("Frame traversal rule", "At every router hop the Layer 2 MAC addresses are rewritten. Layer 3 IPs and Layer 4 ports stay end to end, unless NAT/PAT changes them."),
    ("ARP table", "Cache of IP-to-MAC mappings on the local network (dynamic and static entries). arp -a shows it."),
    ("TTL", "Time to live: decremented at each router; when it reaches 0 the router drops the packet and ICMP reports 'TTL exceeded'. tracert uses this."),
    ("TCP handshake / teardown", "Open: SYN, SYN/ACK, ACK. Close: FIN and ACK in each direction. Sequence numbers and checksums let TCP resend lost data."),
    ("VLAN tagging (802.1Q)", "A 4-byte tag marks the VLAN on a trunk (tagged) port. An access port belongs to one VLAN and strips the tag."),
    ("Inter-VLAN routing", "Different VLANs are different subnets, so traffic between them must go through a router (router-on-a-stick) or a Layer 3 switch."),
    ("Wi-Fi bands", "2.4 GHz: longer range, slower, crowded, channels 1/6/11. 5 GHz: faster, shorter range. 6 GHz: Wi-Fi 6E only."),
    ("RSSI scale", "-30 dBm excellent, -50 good (VoIP/video), -70 acceptable (minimum for reliable data), -80 basic, -90 unusable."),
    ("Wi-Fi association", "Scan (active = probe request, passive = listen for beacons), authenticate, associate. Roaming = moving between APs of one ESS."),
    ("Wi-Fi security summary", "WEP broken; WPA TKIP; WPA2 AES/CCMP; WPA3 newest. Personal = shared passphrase (PSK); Enterprise = RADIUS and 802.1X."),
    ("HTTPS handshake idea", "The server sends a certificate; the client checks it with a CA; asymmetric keys protect the exchange of a symmetric session key, which then encrypts the data."),
    ("Wireshark vs monitor", "Monitor: traffic types, flows and volume. Analyzer (Wireshark, tcpdump): every frame in detail."),
    ("SNMP pieces", "NMS (the manager), agents on managed devices, MIB (the data dictionary). Poll UDP 161, traps UDP 162. v3 most secure."),
    ("Syslog vs Event Viewer", "Syslog: UDP 514, devices (generators) send to a collector. Event Viewer: the Windows event log."),
    ("DR plan vs BCP", "DR plan restores IT after a disaster. BCP (business continuity plan) keeps the whole business operating."),
    ("Backup comparison", "Full: everything (slowest backup, fastest restore). Incremental: since the last backup (smallest, slowest restore). Differential: since the last full."),
    ("Snapshot vs replication", "Snapshot: storage freezes blocks to go back in time. Replication: live copy to another location."),
    ("NAS vs SAN", "NAS: file-level storage device on the LAN. SAN: separate high-speed network giving servers block-level storage (Fibre Channel, iSCSI)."),
    ("NIST cloud characteristics", "On-demand self-service, broad network access, resource pooling, rapid elasticity, measured service."),
    ("Spine-leaf vs 3-tier", "3-tier: access, distribution, core (north-south). Spine-leaf: every leaf to every spine, spines not linked to each other (east-west)."),
    ("Virtualization pros and cons", "Pros: efficient resource use, cost/energy savings, isolation, easy backups. Cons: performance, complexity, licensing, single point of failure."),
    ("Contract types in one line each", "RFP asks for proposals; MOU states intent (not binding); MSA sets terms for future deals; SOW defines one project's work (binding); SLA defines measurable service (binding)."),
    ("Structured cabling terms", "EF -> MDF -> IDFs (backbone), IDF -> workstation (horizontal, max 100 m), demarc where the ISP ends. TIA/EIA-568: hierarchical star."),
    ("OSI memory trick", "Layers 1-7: Please Do Not Throw Sausage Pizza Away. Layers 5 and 6 are mostly folded into 7; the exam focuses on 1-4 and 7."),
]

# ---------------------------------------------------------------------------
# FACTS: one-line facts about terms. When you pick a wrong option, the quiz looks up the terms in it and shows
# "what that term actually is", which usually shows why it doesn't fit the question. Order matters: the first
# matches win, so specific entries come before general ones.   (pattern, label, fact)
# ---------------------------------------------------------------------------
FACTS = [
    # --- devices, layers, topologies ---
    (r"KVM", "KVM switch", "Lets one keyboard, monitor and mouse control several computers."),
    (r"layer 3 switch|l3 switch", "Layer 3 switch", "A switch that can also route between networks using IP addresses (it works at Layers 2 and 3)."),
    (r"unmanaged switch", "Unmanaged switch", "Plug-and-play 'dumb' switch: no IP address, no CLI, no VLANs. Managed switches can be configured."),
    (r"managed switch", "Managed switch", "A switch with an IP address you configure through a CLI or web GUI. VLANs, port mirroring and STP need a managed switch."),
    (r"hub", "Hub", "Layer 1 repeater: copies every signal out of all other ports. One collision domain and one broadcast domain."),
    (r"switch", "Switch", "Layer 2 device that forwards frames by MAC address. Each port is a separate collision domain; it belongs to one network."),
    (r"router", "Router", "Layer 3 device that connects two or more networks and forwards packets by IP address. It does not forward broadcasts."),
    (r"repeater|range extender", "Repeater / range extender", "Layer 1 device that regenerates or boosts a signal to fix attenuation. It does not read addresses."),
    (r"firewall", "Firewall", "Filters traffic by rules (addresses, ports, sessions). Works at Layers 3-7 depending on type; often at the network edge."),
    (r"access point|\bAP\b|\bAPs\b", "Access point (AP)", "Connects Wi-Fi clients to the wired network. A group of clients sharing one AP is a BSS."),
    (r"\bNIC\b|network interface card", "NIC", "Network interface card: works at Layers 1 and 2 and holds the device's MAC address."),
    (r"patch panel", "Patch panel", "A panel of ports where many cables terminate in one place; short patch cables then connect it to switches."),
    (r"patch cable", "Patch cable", "A short cable with connectors on both ends, such as printer to wall jack or patch panel to switch."),
    (r"demarc|demarcation", "Demarc", "Demarcation point: where the service provider's network ends and the customer's network begins."),
    (r"\bMDF\b|main distribution", "MDF", "Main distribution frame: the central point where the LAN and WAN interconnect (often the main data room)."),
    (r"\bIDF\b|intermediate distribution", "IDF", "Intermediate distribution frame: a closet on a floor or building that connects workstations back to the MDF."),
    (r"entrance facility|\bEF\b", "Entrance facility (EF)", "Where the service provider's cabling enters the building and connects to the customer's network."),
    (r"horizontal cabling", "Horizontal cabling", "Runs from a workstation to the nearest data room (IDF). Twisted pair maximum is 100 m."),
    (r"backbone cabling", "Backbone cabling", "Connects the entrance facility, the MDF and the IDFs to each other."),
    (r"work area", "Work area", "Where users and their devices sit; patch cables run from the wall jack to the device."),
    (r"plenum", "Plenum cable", "Cable with a fire-resistant jacket for air-handling spaces (it gives off less toxic smoke)."),
    (r"extended star", "Extended star", "A star topology with more stars hanging off it, such as workstations to IDFs to the MDF."),
    (r"star-bus|hybrid topology|\(hybrid\)", "Star-bus / hybrid", "Daisy-chained switches (a bus) with a star of devices on each one. Combining topologies makes a hybrid."),
    (r"\bbus\b", "Bus topology", "All devices share one backbone cable. Daisy-chained switches form a bus."),
    (r"\bstar\b", "Star topology", "Every device connects to one central device, usually a switch."),
    (r"\bring\b", "Ring topology", "Each device connects to exactly two neighbors, forming a loop."),
    (r"mesh", "Mesh", "Devices connect to several others. In Wi-Fi, mesh APs act as peers and relay traffic for each other."),
    (r"point-to-point", "Point-to-point", "A dedicated link between exactly two endpoints."),
    (r"peer-to-peer|\bP2P\b", "Peer-to-peer", "Each computer controls its own resources and local accounts. Simple and cheap but not scalable."),
    (r"client-server", "Client-server", "Servers provide resources and a central directory (such as Active Directory) controls access. Scalable."),
    (r"active directory|\bAD DS\b", "Active Directory", "A Windows directory database of users and resources, managed by AD DS, that gives central sign-in and access control."),
    (r"\bNOS\b|network operating system", "NOS", "Network operating system (Windows Server, Red Hat Enterprise Linux): manages resources, file access and user authorization."),
    (r"\bPAN\b", "PAN", "Personal area network: a few personal devices over Bluetooth or NFC. The smallest network type."),
    (r"\bLAN\b", "LAN", "Local area network: devices in one building or office."),
    (r"\bMAN\b|\bCAN\b", "MAN / CAN", "Metropolitan or campus area network: several LANs in the same city or campus."),
    (r"\bWAN\b", "WAN", "Wide area network covering a large area. The Internet is the largest and most varied WAN."),
    (r"physical topology", "Physical topology", "How devices and cables are actually laid out. Logical topology is how access to the network is controlled."),
    (r"logical topology", "Logical topology", "How access to the network is controlled (software). Physical topology is the layout of devices and cables."),
    (r"\bESD\b|electrostatic", "ESD", "Electrostatic discharge. Catastrophic failure destroys a part now; an upset failure shortens its life."),
    (r"fail-open|fail open", "Fail-open", "Also fail-safe: in an emergency the doors unlock so nobody is trapped."),
    (r"fail-close|fail close|fail-secure", "Fail-close", "Also fail-secure: protects resources even if that means access is denied during the emergency."),
    # --- OSI, PDUs, encapsulation ---
    (r"encapsulation", "Encapsulation", "Each layer adds its own header to the data from the layer above. The receiver de-encapsulates in reverse order."),
    (r"segment", "Segment", "The Layer 4 PDU when TCP is used. (With UDP it is called a datagram.)"),
    (r"datagram", "Datagram", "The Layer 4 PDU when UDP is used."),
    (r"packet", "Packet", "The Layer 3 PDU: an IP header plus the data from above."),
    (r"frame", "Frame", "The Layer 2 PDU: a header and a trailer around the packet. MAC addresses live in the frame header."),
    (r"physical layer|layer 1", "Layer 1 (Physical)", "Bits as voltage, light or radio. Hubs, cables and fiber live here."),
    (r"data link|layer 2", "Layer 2 (Data Link)", "Frames and MAC addresses on the local network. Switches and NICs work here; Ethernet and Wi-Fi are Layer 2 protocols."),
    (r"network layer|layer 3", "Layer 3 (Network)", "Packets and IP addresses across networks. Routers work here; IP, ICMP, RIP and OSPF."),
    (r"transport layer|layer 4", "Layer 4 (Transport)", "Segments or datagrams and port numbers. TCP and UDP work here."),
    (r"layer 7|application layer", "Layer 7 (Application)", "Where applications and their protocols live: HTTP, SMTP, DNS, RDP, FTP, SNMP. Layers 5 and 6 are mostly folded into 7."),
    # --- TCP/IP protocols ---
    (r"\bTCP\b", "TCP", "Layer 4, connection-oriented: three-way handshake, sequencing, checksums and flow control. Reliable but slower."),
    (r"\bUDP\b", "UDP", "Layer 4, connectionless and unreliable: no handshake, sequencing or flow control. Fast, so used for live audio/video, DNS, DHCP, TFTP."),
    (r"\bICMP\b|ICMPv6", "ICMP", "Layer 3: reports network problems (unreachable, TTL expired) but does not fix them. Used by ping and tracert."),
    (r"\bARP\b", "ARP", "Finds the MAC address for a known IP address on the local network, by broadcast. It never crosses a router."),
    (r"\bNDP\b|neighbor discovery", "NDP", "Neighbor Discovery Protocol: does ARP's job on IPv6 networks, using ICMPv6."),
    (r"\bIPv4\b", "IPv4", "32-bit addresses in four decimal octets: about 4.29 billion (2^32) addresses."),
    (r"\bIPv6\b", "IPv6", "128-bit addresses, eight 16-bit hex blocks, no broadcast. About 340 undecillion (2^128) addresses."),
    (r"\bIP\b", "IP", "Layer 3, connectionless and unreliable. Gets packets across networks; TCP handles ordering and delivery."),
    (r"\bDHCP\b", "DHCP", "Hands out IP settings automatically from a scope (pool) with a lease. UDP 67 (server) and 68 (client)."),
    (r"relay agent|ip helper", "DHCP relay agent", "A router feature ('IP helper address') that forwards DHCP broadcasts to a server on another subnet."),
    (r"\bAPIPA\b|169\.254", "APIPA", "169.254.x.x: a Windows PC gave itself this address because it could not reach a DHCP server."),
    (r"\bDNS\b", "DNS", "Translates names to IP addresses. Port 53. Namespace + name servers + resolvers."),
    (r"\bHTTPS\b", "HTTPS", "HTTP over SSL/TLS encryption, port 443."),
    (r"\bHTTP\b", "HTTP", "Web protocol at Layer 7, port 80, no encryption."),
    (r"\bSFTP\b", "SFTP", "File transfer over SSH (port 22): encrypted and authenticated."),
    (r"\bFTPS\b", "FTPS", "FTP over SSL/TLS: FTP with encryption."),
    (r"\bTFTP\b", "TFTP", "Trivial FTP: no authentication or security, runs over UDP port 69."),
    (r"\bFTP\b", "FTP", "File transfer on ports 20 (data) and 21 (control). Sends everything in cleartext."),
    (r"\bSSH\b", "SSH", "Encrypted remote command line (and file transfer), TCP port 22."),
    (r"telnet", "Telnet", "Remote command line in cleartext, TCP port 23. Insecure; use SSH instead."),
    (r"\bRDP\b", "RDP", "Remote Desktop Protocol: Microsoft's GUI remote control, TCP port 3389."),
    (r"\bVNC\b", "VNC", "Open-source GUI remote control (many vendors build on it)."),
    (r"\bSMTP\b|SMTPS", "SMTP", "Sends email (port 25; 587 for SMTPS). Clients receive with POP3 or IMAP."),
    (r"\bPOP3\b", "POP3", "Receives email by downloading it from the server (port 110, 995 with TLS)."),
    (r"\bIMAP4?\b", "IMAP4", "Receives email while keeping it on the server (port 143, 993 with TLS)."),
    (r"\bSNMP\b", "SNMP", "A network management system polls agents on devices (UDP 161); agents send traps to UDP 162. Info lives in the MIB. v3 is most secure."),
    (r"syslog", "Syslog", "Devices (generators) send log messages to a collector, UDP port 514."),
    (r"\bNTP\b", "NTP", "Network Time Protocol, UDP port 123."),
    (r"\bLDAPS?\b", "LDAP", "Directory access protocol used by Active Directory: port 389 (636 for LDAPS)."),
    (r"\bSMB\b|file sharing", "SMB", "Windows file sharing, TCP port 445."),
    (r"\bSIP\b", "SIP", "Session Initiation Protocol for voice/video calls, ports 5060/5061."),
    (r"\bRIP\b", "RIP", "A routing protocol IP uses at Layer 3 to find routes (hop count based)."),
    (r"\bOSPF\b", "OSPF", "A link-state routing protocol IP uses at Layer 3 to find the best route."),
    (r"\bSTP\b|spanning tree", "STP", "Spanning Tree Protocol: blocks redundant switch links so loops and broadcast storms can't form. One root bridge."),
    (r"\bLACP\b|link aggregation|nic teaming", "Link aggregation", "Bonds several physical links into one logical link: more throughput, automatic failover and load balancing."),
    (r"\bIPsec\b", "IPsec", "Network-layer (Layer 3) encryption suite used for VPNs. Five steps: initiation, key management, negotiation, data transfer, termination."),
    (r"\bSSL\b|\bTLS\b", "SSL/TLS", "Encrypts TCP/IP sessions at the Transport layer, for example web pages (HTTPS)."),
    (r"\bPKI\b", "PKI", "Public key infrastructure: certificate authorities tie public keys to identities."),
    (r"certificate authority|\bCA\b", "CA", "Certificate authority: issues and maintains digital certificates."),
    (r"certificate", "Digital certificate", "Holds identity information and the owner's PUBLIC key, signed by a CA."),
    (r"asymmetric", "Asymmetric encryption", "A key pair: public key encrypts, private key decrypts. Slow, so used for key exchange and identity."),
    (r"symmetric", "Symmetric encryption", "One shared key encrypts and decrypts. Fast, so used for bulk data; the hard part is sharing the key safely."),
    (r"\bCIA\b", "CIA triad", "Confidentiality, integrity, availability."),
    (r"VPN concentrator", "VPN concentrator", "Authenticates VPN clients, sets up the tunnels and manages the VPN encryption (often built into a firewall)."),
    (r"site-to-site", "Site-to-site VPN", "Hardware (often firewalls) at each office end builds the tunnel; users don't run VPN software."),
    (r"client-to-site|host-to-site", "Client-to-site VPN", "Software on a remote laptop connects to the office VPN (also called remote access or mobile user)."),
    (r"host-to-host", "Host-to-host VPN", "A tunnel directly between two individual computers."),
    (r"split tunnel", "Split tunnel", "Only traffic for the office goes through the VPN; everything else goes straight to the Internet."),
    # --- addressing ---
    (r"\bMAC\b", "MAC address", "48-bit hardware address (six hex pairs). The first 24 bits are the OUI. Layer 2, only meaningful on the local network."),
    (r"\bOUI\b", "OUI", "Organizationally Unique Identifier: the first 24 bits of a MAC, assigned to the manufacturer by the IEEE."),
    (r"default gateway|\bgateway\b", "Default gateway", "The router interface a host sends to when the destination is on a different network."),
    (r"subnet mask|netmask", "Subnet mask", "The 1-bits mark the network portion and the 0-bits the host portion."),
    (r"loopback|127\.0\.0\.1|::1\b", "Loopback", "127.0.0.1 in IPv4 and ::1 in IPv6: your own computer."),
    (r"broadcast", "Broadcast", "Sent to every device in the local broadcast domain (255.255.255.255). Routers don't forward it. IPv6 has none."),
    (r"multicast", "Multicast", "Delivered to a group of subscribers. IPv4 Class D (224-239)."),
    (r"anycast", "Anycast", "Delivered to the nearest of several destinations sharing the same address (IPv6)."),
    (r"link-local|fe80", "Link-local IPv6", "FE80::/64: self-configured address valid only on the local link (neighbors)."),
    (r"unicast", "Unicast", "Delivered to a single destination."),
    (r"dual stack", "Dual stack", "Running IPv4 and IPv6 at the same time."),
    (r"tunneling", "Tunneling", "Carrying one protocol inside another, such as IPv6 packets through an IPv4 network."),
    (r"\bPAT\b", "PAT", "Port Address Translation: tracks sessions by port number so many hosts can share one public IP."),
    (r"\bSNAT\b|static nat", "Static NAT", "A fixed public-to-private mapping, such as for an inbound web server."),
    (r"\bDNAT\b|dynamic nat", "Dynamic NAT", "The gateway picks from a pool of public addresses."),
    (r"\bNAT\b", "NAT", "Swaps private IP addresses for a public one. Conserves IPv4 addresses and hides the private network."),
    (r"\bCIDR\b", "CIDR", "Classless Inter-Domain Routing (pronounced 'cider'): slash notation, networks of any size, no classes."),
    (r"\bVLSM\b", "VLSM", "Variable Length Subnet Masking: subnets of different sizes (largest first). Not tested on the midterm."),
    (r"\bCLSM\b", "CLSM", "Constant Length Subnet Masking: all subnets the same size. Tested on the midterm."),
    (r"class a\b", "Class A", "First octet 1-126, default /8, about 16 million hosts."),
    (r"class b\b", "Class B", "First octet 128-191, default /16, about 65,000 hosts."),
    (r"class c\b", "Class C", "First octet 192-223, default /24, 254 hosts."),
    (r"class d\b", "Class D", "First octet 224-239: multicast."),
    (r"class e\b", "Class E", "First octet 240-254: research/experimental."),
    (r"\bsocket\b", "Socket", "An IP address plus a port number, such as 10.43.3.87:23."),
    (r"well-known port", "Well-known ports", "0-1023. Registered ports are 1024-49151 and dynamic/private ports are 49152-65535."),
    (r"\bFQDN\b|host name|hostname", "FQDN / host name", "A Layer 7 name such as www.example.com that DNS turns into an IP address."),
    (r"zone transfer", "Zone transfer", "A secondary DNS server copies the zone from the primary."),
    (r"secondary", "Secondary DNS server", "Read-only copy of the zone, updated by zone transfers from the primary."),
    (r"primary", "Primary DNS server", "Holds the read/write authoritative database for a zone."),
    (r"caching", "Caching DNS server", "Stores answers it has looked up; holds no zone files of its own."),
    (r"forwarding", "Forwarding DNS server", "Passes queries it cannot answer on to another DNS server."),
    (r"recursive", "Recursive query", "Demands a final answer (or 'not found'), like a PC asking its local DNS server."),
    (r"iterative", "Iterative query", "The local server asks root, then TLD, then authoritative servers step by step."),
    (r"\bAAAA\b", "AAAA record", "Maps a name to an IPv6 address."),
    (r"\bCNAME\b", "CNAME record", "An alias: points one name at another name."),
    (r"\bPTR\b", "PTR record", "Reverse lookup: maps an IP address back to a name (in .arpa)."),
    (r"\bMX\b", "MX record", "Identifies the mail server for a domain."),
    (r"\bNS\b record|name server record", "NS record", "Identifies the authoritative name servers for a zone."),
    (r"\bA record\b", "A record", "Maps a name to an IPv4 address."),
    (r"\bBIND\b", "BIND", "The most popular open-source DNS server software."),
    (r"\.arpa", ".arpa", "The top-level domain used for reverse lookups."),
    (r"root server|root dns", "Root servers", "13 clusters at the top of DNS; they point to the TLD servers."),
    (r"\bTLD\b", "TLD", "Top-level domain servers (.com, .edu...). They point to the authoritative servers."),
    (r"\bSLAAC\b", "SLAAC", "Stateless address autoconfiguration: an IPv6 host builds its own address without DHCPv6."),
    # --- tools ---
    (r"ipconfig", "ipconfig", "Windows TCP/IP tool. /all shows everything, /release ends the DHCP lease, /renew gets a new one, /flushdns clears the DNS cache."),
    (r"ifconfig", "ifconfig", "Older Linux TCP/IP tool (the 'ip' command replaces it). 'ifconfig down' takes an interface offline."),
    (r"pathping", "pathping", "Sends many pings to each hop along a route and compiles one report (mtr on Linux)."),
    (r"\bping\b", "ping", "Uses ICMP echo request/reply to test that a host is reachable."),
    (r"tracert", "tracert", "Windows tool that lists each router hop using ICMP echo requests. * * * means no 'TTL exceeded' reply."),
    (r"traceroute", "traceroute", "Linux version of tracert; it sends UDP messages to a random port."),
    (r"netstat", "netstat", "Shows connections and statistics: -a all, -n numeric, -e interface errors, -r routes, -o process ID, -b process name, -s per protocol."),
    (r"nslookup", "nslookup", "Queries DNS for an IP from a name, or a name from an IP (reverse lookup)."),
    (r"\bdig\b", "dig", "Linux/macOS DNS lookup tool with more detail than nslookup."),
    (r"nmap|zenmap", "Nmap", "Network mapper: discovers devices and open ports. Zenmap is its GUI."),
    (r"wireshark", "Wireshark", "Protocol analyzer: captures and shows traffic frame by frame."),
    (r"tcpdump", "tcpdump", "Free command-line packet sniffer for Linux/UNIX."),
    (r"netflow", "NetFlow", "Collects traffic flow data (who talks to whom, how much) for monitoring."),
    (r"iperf", "iPerf", "Measures network throughput between two hosts."),
    (r"event viewer", "Event Viewer", "Windows tool for the event log; the first place to look for clues."),
    (r"\barp -a\b", "arp -a", "Shows the ARP table (IP-to-MAC entries) on the local computer."),
    (r"route print|route add|route command|route -n", "route", "Shows or edits a computer's routing table."),
    (r"toner", "Toner and probe", "Tools for tracing a copper cable through walls to its other end."),
    # --- wireless ---
    (r"802\.11ax|wi-fi 6", "802.11ax (Wi-Fi 6/6E)", "2.4, 5 and (6E) 6 GHz bands, about 9.6 Gbps. The only one that can use all three bands."),
    (r"802\.11ac|wi-fi 5", "802.11ac (Wi-Fi 5)", "5 GHz only, 1.3 to 6.93 Gbps, introduced MU-MIMO (Wave 2)."),
    (r"802\.11n|wi-fi 4", "802.11n (Wi-Fi 4)", "2.4 and 5 GHz, up to 600 Mbps, introduced MIMO."),
    (r"802\.11g", "802.11g", "2.4 GHz, 54 Mbps."),
    (r"802\.11b", "802.11b", "2.4 GHz, 11 Mbps."),
    (r"802\.11a\b", "802.11a", "5 GHz only, 54 Mbps."),
    (r"802\.11be|wi-fi 7", "802.11be (Wi-Fi 7)", "Up to about 46 Gbps."),
    (r"802\.1q", "802.1Q", "The IEEE standard for VLAN tagging in Ethernet frames (adds a 4-byte tag)."),
    (r"802\.1x", "802.1X", "Port-based network authentication (used with RADIUS in WPA-Enterprise)."),
    (r"802\.3af|\bPoE\b", "PoE", "Power over Ethernet (802.3af): powers devices like APs and phones through the network cable."),
    (r"802\.11", "802.11", "The Wi-Fi standards (Layers 1 and 2). Above Layer 2 wired and wireless networks use the same protocols."),
    (r"2\.4 ?ghz", "2.4 GHz", "Longer range but slower and more crowded. Non-overlapping channels are 1, 6 and 11."),
    (r"\b5 ?ghz", "5 GHz", "Higher throughput but shorter range and weaker through walls."),
    (r"6 ?ghz", "6 GHz", "The band added by Wi-Fi 6E."),
    (r"\bMU-MIMO\b", "MU-MIMO", "Multiuser MIMO: several antennas serve several clients at once (802.11ac Wave 2)."),
    (r"\bMIMO\b", "MIMO", "Multiple antennas on the AP and client send several streams to raise throughput."),
    (r"channel bonding", "Channel bonding", "Combining two adjacent 20 MHz channels into one 40 MHz channel."),
    (r"frame aggregation", "Frame aggregation", "Combining several frames into one transmission to cut overhead."),
    (r"band steering", "Band steering", "The AP nudges capable clients onto the 5 GHz band."),
    (r"csma/cd", "CSMA/CD", "Collision DETECTION, used by wired Ethernet."),
    (r"csma/ca", "CSMA/CA", "Collision AVOIDANCE with ACKs, used by Wi-Fi because radios can't detect collisions while sending."),
    (r"rts/cts|rts|cts", "RTS/CTS", "Optional request-to-send / clear-to-send exchange that cuts collisions but lowers efficiency."),
    (r"\bSSID\b", "SSID", "The name of a Wi-Fi network."),
    (r"\bBSSID\b", "BSSID", "The MAC address of an access point's radio."),
    (r"\bBSS\b", "BSS", "Basic service set: stations sharing ONE access point."),
    (r"\bESS\b|ESSID", "ESS", "Extended service set: several APs sharing an ESSID so clients can roam."),
    (r"ad hoc", "Ad hoc", "Wi-Fi devices talk directly to each other with no access point."),
    (r"infrastructure", "Infrastructure mode", "Wi-Fi clients connect through an access point."),
    (r"\bWEP\b", "WEP", "Wired Equivalent Privacy: broken and obsolete; never use it."),
    (r"\bWPA3\b", "WPA3", "The newest Wi-Fi security; protects the handshake and enforces stronger encryption."),
    (r"\bWPA2\b", "WPA2", "Uses CCMP/AES. With RADIUS (Enterprise) it is the most secure setup in the slides."),
    (r"\bWPA\b", "WPA", "Used TKIP with a per-packet key; the replacement for WEP."),
    (r"\bPSK\b|wpa-personal|wpa2-personal|personal mode", "WPA-Personal", "Uses a pre-shared key: one shared passphrase."),
    (r"enterprise|radius", "WPA-Enterprise / RADIUS", "Each user authenticates against a RADIUS server (often backed by Active Directory) using 802.1X."),
    (r"mac filtering", "MAC filtering", "The AP only authenticates devices on an allowed MAC list. It does not encrypt or hide anything."),
    (r"captive portal", "Captive portal", "The page a guest must accept (terms of use) before getting access."),
    (r"guest network", "Guest network", "A separate network that keeps visitors away from private resources."),
    (r"evil twin", "Evil twin", "A rogue AP that imitates a legitimate one to capture users' traffic."),
    (r"\bWPS\b", "WPS attack", "Cracking the WPS PIN to get into an AP's settings."),
    (r"war driving|wardriving", "War driving", "Driving around looking for open Wi-Fi networks (very old school)."),
    (r"war chalking", "War chalking", "Marking where open Wi-Fi networks are found (very old school)."),
    (r"bluejack", "Bluejacking", "SENDING unsolicited messages to a Bluetooth device."),
    (r"bluesnarf", "Bluesnarfing", "STEALING data from a Bluetooth device."),
    (r"bluetooth", "Bluetooth", "2.4 GHz, short range, frequency hopping to reduce interference."),
    (r"zigbee", "ZigBee", "Low-power IoT radio for building automation, HVAC and meter reading."),
    (r"z-wave", "Z-Wave", "Smart-home radio that uses a hub/controller to relay commands."),
    (r"\bNFC\b", "NFC", "A very short-range form of RFID; the tag can be powered by the phone through induction."),
    (r"\bRFID\b", "RFID", "Radio tags for inventory. Active tags have their own battery; passive tags are powered by the reader."),
    (r"\bANT\+", "ANT+", "Low-power radio for fitness and health sensors."),
    (r"infrared|\bIR\b", "Infrared (IR)", "Just below visible light; used for remote controls and sensors. Needs line of sight."),
    (r"omnidirectional", "Omnidirectional antenna", "Radiates roughly equally in all directions."),
    (r"unidirectional|directional", "Directional antenna", "Sends the signal mainly in one direction (point-to-point links)."),
    (r"attenuation", "Attenuation", "The signal weakens with distance; fix it with more power or a repeater/range extender."),
    (r"diffraction", "Diffraction", "Waves bend around a sharp edge, such as a desk corner."),
    (r"refraction", "Refraction", "Waves bend when passing into a different medium."),
    (r"reflection", "Reflection", "Waves bounce off large smooth surfaces such as walls and metal."),
    (r"scattering", "Scattering", "Waves hit small or rough objects (or rain) and scatter."),
    (r"multipath", "Multipath", "A signal arrives over several paths: better odds of arriving, but delays can cause errors."),
    (r"fading", "Fading", "Signal strength varies with time or location."),
    (r"\bSNR\b|signal-to-noise", "SNR", "Signal-to-noise ratio: a lower SNR means more noise compared with the signal (worse)."),
    (r"\bRSSI\b|dbm", "RSSI", "Received signal strength: -30 excellent, -50 good, -70 acceptable (minimum for reliable data), -80 basic, -90 unusable."),
    (r"site survey", "Site survey", "Measuring coverage, interference and density before installing APs."),
    (r"spectrum analyzer", "Spectrum analyzer", "Scans a frequency band for signals AND noise."),
    (r"wi-fi analyzer|wifi analyzer", "Wi-Fi analyzer", "Evaluates Wi-Fi networks, channels and signal strength."),
    (r"roaming|sticky client", "Roaming", "A client moves between APs of the same ESS. 'Sticky clients' hold on to the old AP too long."),
    (r"wireless controller", "Wireless controller", "Centralizes authentication, channel management and rogue-AP detection for many APs."),
    (r"beacon", "Beacon", "A frame an AP broadcasts to announce itself; passive scanning listens for beacons."),
    (r"probe request|probe frame|\(probe\)|active scan", "Probe request", "A frame a client sends to look for APs (active scanning)."),
    # --- architecture / virtualization / cloud ---
    (r"spine", "Spine-and-leaf", "Every spine connects to every leaf, but spines don't connect to each other. Built for east-west traffic."),
    (r"3-tier|three-tier|access.{0,12}distribution.{0,12}core", "3-tier design", "Access (edge), distribution (aggregation), core. Good for north-south traffic."),
    (r"east-west", "East-west traffic", "Traffic between peers inside a segment or data center."),
    (r"north-south", "North-south traffic", "Traffic that leaves the segment (to clients or the Internet)."),
    (r"\bSDN\b", "SDN", "Software-defined networking: a central controller makes the decisions (control plane) while devices forward (data plane)."),
    (r"control plane", "Control plane", "The SDN layer that makes forwarding decisions."),
    (r"data plane|infrastructure plane", "Data / infrastructure plane", "The devices that actually send and receive messages."),
    (r"application plane", "Application plane", "SDN applications talking to the controller through APIs."),
    (r"\bSAN\b", "SAN", "A separate high-speed network that gives servers block-level storage (Fibre Channel, iSCSI)."),
    (r"\bNAS\b", "NAS", "A file-level storage device on the LAN."),
    (r"iscsi", "iSCSI", "SAN protocol that runs over ordinary TCP/IP networks."),
    (r"fibre channel|\bFCoE\b", "Fibre Channel", "Dedicated SAN technology (FCoE runs it over Ethernet)."),
    (r"infiniband", "InfiniBand", "SAN technology that needs special hardware."),
    (r"type 1|bare-metal|bare metal", "Type 1 hypervisor", "Installs on the hardware before any OS (bare metal), for example Hyper-V or ESXi."),
    (r"type 2|hosted", "Type 2 hypervisor", "Runs as an application inside a host OS, for example VirtualBox or VMware Workstation."),
    (r"hypervisor", "Hypervisor", "Software that creates and manages virtual machines."),
    (r"vswitch|virtual switch", "vSwitch", "The virtual switch, run by the hypervisor, that connects VMs' vNICs. It works mainly at Layer 2."),
    (r"vnic", "vNIC", "A virtual network adapter that a hypervisor gives to a VM."),
    (r"bridged", "Bridged mode", "The VM gets an IP from the physical LAN's DHCP server and looks like any other node."),
    (r"host-only", "Host-only mode", "VMs talk only to each other and to the host, never through the physical network."),
    (r"\bNFV\b", "NFV", "Network functions virtualization. Caution: licenses per device, latency, and no virtual firewall at the edge."),
    (r"iaas", "IaaS", "Infrastructure as a service: you bring the OS, application and data."),
    (r"paas", "PaaS", "Platform as a service: you bring your application and data."),
    (r"saas", "SaaS", "Software as a service (Gmail, Office 365): you bring only your data."),
    (r"public cloud", "Public cloud", "Shared infrastructure owned by a provider and used by many customers."),
    (r"private cloud", "Private cloud", "Cloud infrastructure used by one organization."),
    (r"community cloud", "Community cloud", "A cloud shared by several organizations with common needs."),
    (r"hybrid cloud", "Hybrid cloud", "A combination of two or more deployment models."),
    (r"orchestration", "Orchestration", "Automated tasks chained into a complex workflow."),
    (r"\bIaC\b|infrastructure as code", "IaC", "Text-based configuration files that create and manage cloud resources."),
    (r"automation", "Automation", "A programmed response to one specific event."),
    (r"elasticity", "Rapid elasticity", "Resources scale up and down quickly with demand (a NIST cloud characteristic)."),
    (r"measured service", "Measured service", "Usage is metered, so customers pay for what they use (NIST cloud characteristic)."),
    (r"\bMTBF\b", "MTBF", "Mean time between failures: average time until the next failure. Higher is better."),
    (r"\bMTTR\b", "MTTR", "Mean time to repair: average time to fix a failure. Lower is better."),
    (r"hot spare", "Hot spare", "Already installed; takes over automatically when the original fails."),
    (r"cold spare", "Cold spare", "Sits on the shelf and is installed only after a failure."),
    (r"hot-swap", "Hot-swappable", "A part that can be replaced while the machine keeps running."),
    (r"cluster", "Clustering", "Several servers appear as one device and share a virtual IP (VIP)."),
    (r"\bVIP\b|virtual ip", "VIP", "Virtual IP address that represents a cluster; it attaches to the load balancer."),
    (r"load balancer", "Load balancer", "Spreads traffic across several servers."),
    (r"high availability|\bHA\b", "High availability", "A system that works reliably nearly all the time (redundancy, spares, clustering)."),
    (r"fault tolerance|fault-tolerant", "Fault tolerance", "Stops a component fault from becoming a failure."),
    # --- segmentation ---
    (r"broadcast domain", "Broadcast domain", "The set of devices that receive each other's broadcasts. Routers (and VLANs) bound them."),
    (r"collision domain", "Collision domain", "Devices that can collide with each other; each switch port is its own."),
    (r"vlan hopping|double.tag", "VLAN hopping", "An attack that double-tags frames to reach another VLAN."),
    (r"native vlan", "Native VLAN", "The VLAN whose frames cross a trunk untagged."),
    (r"trunk|tagged port", "Trunk (tagged) port", "A switch port that carries MANY VLANs, with an 802.1Q tag on each frame."),
    (r"access port", "Access port", "A switch port that belongs to ONE VLAN and connects an end device."),
    (r"\bVLANs?\b", "VLAN", "A logical broadcast domain on a managed switch. Traffic between VLANs needs a router."),
    (r"inter-vlan", "Inter-VLAN routing", "A router (or L3 switch) forwards traffic between VLANs."),
    # --- performance / recovery ---
    (r"port mirroring|\bSPAN\b", "Port mirroring (SPAN)", "A switch copies traffic from some ports to one port where a monitor listens."),
    (r"\bTAP\b", "Network TAP", "An in-line device that copies the traffic passing through a cable."),
    (r"protocol analyzer", "Protocol analyzer", "Captures detailed frame-by-frame data (Wireshark)."),
    (r"network monitor", "Network monitor", "Shows traffic types, flows and volume."),
    (r"\brunts?\b", "Runt", "A frame that is too small."),
    (r"\bgiants?\b", "Giant", "A frame that is too large."),
    (r"jabber", "Jabber", "A device that continuously sends garbage onto the network."),
    (r"baseline", "Baseline", "A record of normal operation (utilization, errors, drops, response time) used to spot abnormal behavior."),
    (r"\bQoS\b|quality of service", "QoS", "Prioritizes traffic such as VoIP and video during congestion."),
    (r"flow control", "Flow control", "Keeps a sender from overwhelming a receiver (between two devices)."),
    (r"congestion control", "Congestion control", "Open-loop prevents congestion before it happens; closed-loop fixes it after it starts."),
    (r"traffic shaping", "Traffic shaping", "Limits how much bandwidth a device or application may use."),
    (r"incident response", "Incident response", "Six stages: preparation, detection, containment, remediation, recovery, review."),
    (r"\bDR plan|disaster recovery", "Disaster recovery", "The plan for restoring IT after a disaster. A BCP covers keeping the whole business running."),
    (r"hot site", "Hot site", "Fully configured and ready to take over; the most expensive."),
    (r"warm site", "Warm site", "Partly configured; takes less time than cold, more than hot."),
    (r"cold site", "Cold site", "Has components but nothing configured or connected; can take weeks."),
    (r"\bRPO\b", "RPO", "Recovery point objective: how much data you can afford to lose."),
    (r"\bRTO\b", "RTO", "Recovery time objective: how quickly you must be back up."),
    (r"surge|spike", "Surge / spike", "A momentary INCREASE in voltage (for example lightning)."),
    (r"brownout|sag", "Brownout (sag)", "A momentary DECREASE in voltage."),
    (r"blackout", "Blackout", "A complete loss of power."),
    (r"\bnoise\b", "Power noise", "Fluctuations caused by EMI or other devices."),
    (r"standby ups", "Standby UPS", "Switches to battery only when it detects a power loss."),
    (r"online ups", "Online UPS", "Always runs the device from its battery while AC recharges it, so there is no switchover gap."),
    (r"\bUPS\b", "UPS", "Uninterruptible power supply: battery backup for short outages."),
    (r"generator", "Generator", "Provides power in long blackouts; often combined with a UPS; fuel must be checked regularly."),
    (r"\bPDU\b", "PDU", "Power distribution unit: distributes power to the equipment in a rack."),
    (r"3-2-1-1", "3-2-1-1 rule", "3 copies, 2 media types, 1 offsite, 1 offline."),
    (r"differential", "Differential backup", "Copies everything changed since the last FULL backup (grows each day)."),
    (r"incremental", "Incremental backup", "Copies what changed since the last backup of any kind. Smallest, but a restore needs the full plus every incremental."),
    (r"full backup|^\s*full\s*$", "Full backup", "Copies everything. Slowest to make, fastest to restore."),
    (r"snapshot", "Snapshot", "Storage 'freezes' the blocks so you can go back in time."),
    (r"replication", "Replication", "Live copying of data to another location."),
    (r"raid 0", "RAID 0", "Striping: faster, but NO redundancy. Lose one disk and everything is gone."),
    (r"raid 10|raid 1\+0", "RAID 10", "Mirrored pairs that are then striped; needs at least 4 drives."),
    (r"raid 1\b", "RAID 1", "Mirroring: 100% overhead, survives one failed disk."),
    (r"raid 5", "RAID 5", "Striping with parity, 3+ drives, survives one failure; has a write penalty and risky rebuilds on big drives."),
    (r"raid 6", "RAID 6", "Double parity: survives two failed drives, so it is popular with large drives."),
    (r"audit log", "Audit log", "Records WHO did WHAT and WHEN."),
    # --- documents, change management ---
    (r"\bRFP\b", "RFP", "Request for proposal: asks vendors to submit proposals."),
    (r"\bMOU\b", "MOU", "Memorandum of understanding: intent to agree; usually NOT legally binding."),
    (r"\bMSA\b", "MSA", "Master service agreement: sets the terms of future contracts (payment terms, arbitration)."),
    (r"\bSOW\b", "SOW", "Statement of work: tasks, deliverables and timeline for a project; legally binding, often an addendum to an MSA."),
    (r"\bSLA\b", "SLA", "Service level agreement: a binding contract with measurable service levels such as uptime."),
    (r"system life cycle|\bSLC\b", "System life cycle", "Designing, implementing and maintaining a network, including disposing of outdated assets."),
    (r"rollback|backlevel", "Rollback", "Reverting to a previous software version (backleveling). Always have a backout plan."),
    (r"\bpatch\b", "Patch", "A correction, improvement or enhancement to existing software."),
    (r"upgrade", "Upgrade", "A major software change."),
    (r"rack diagram", "Rack diagram", "Shows the devices stacked in a rack system."),
    (r"wiring schematic", "Wiring schematic", "A detailed drawing of the wired infrastructure."),
    (r"1u|rack unit", "Rack unit", "1U = 1.75 inches. A full rack is 42U (about 6 ft) and 19 inches wide."),
    (r"\bSMF\b|single-mode", "Single-mode fiber", "Narrow 8-10 micron core and laser light: the longest distances (backbone)."),
    (r"\bMMF\b|multimode", "Multimode fiber", "50 or 62.5 micron core: shorter distances and cheaper."),
    (r"bend radius", "Bend radius", "The tightest a cable may be bent without damaging it."),
    (r"\bEMI\b", "EMI", "Electromagnetic interference: keep data cables away from power cables and motors."),
    (r"TIA/EIA-568|568", "TIA/EIA-568", "The structured cabling standard: hierarchical design and star topology."),
    (r"metric", "Routing metric", "The tie-breaker between equal-length matching routes (fewest hops or fastest link)."),
    (r"longest prefix", "Longest prefix match", "The most specific matching route (largest prefix length) always wins first."),
    (r"default route|0\.0\.0\.0/0", "Default route", "0.0.0.0/0: used when no more specific route matches."),
    (r"next hop", "Next hop", "The next router (by IP) the packet is handed to."),
]


# More facts for short options (single words and terms that the first list doesn't catch). These go FIRST so the
# anchored one-word entries win over the generic ones.
FACTS[0:0] = [
    (r"^\s*physical\s*$", "Physical layer", "Layer 1: bits as voltage, light or radio. Cables, hubs and link lights."),
    (r"^\s*network\s*$", "Network layer", "Layer 3: packets and IP addresses across networks. Routers work here."),
    (r"^\s*transport\s*$", "Transport layer", "Layer 4: segments/datagrams and port numbers. TCP and UDP."),
    (r"^\s*application\s*$", "Application layer", "Layer 7: the applications' protocols (HTTP, SMTP, DNS, RDP)."),
    (r"^\s*session\s*$", "Session layer", "Layer 5: mostly folded into Layer 7 in data networking."),
    (r"^\s*presentation\s*$", "Presentation layer", "Layer 6: mostly folded into Layer 7 in data networking."),
    (r"decapsulation", "Decapsulation", "Removing the headers as data moves UP the stack at the receiver (the reverse of encapsulation)."),
    (r"fragmentation", "Fragmentation", "Splitting a packet into smaller pieces so it fits a smaller MTU."),
    (r"^\s*segmentation\s*$", "Segmentation", "Dividing a network into smaller networks (or splitting data into TCP segments). It is not adding a header."),
    (r"campus network|citywide", "MAN / CAN", "Several LANs in the same city or campus."),
    (r"home network", "Home network", "A small LAN, usually one router doing NAT. It is not a group of connected LANs."),
    (r"catastrophic", "Catastrophic ESD failure", "The part is destroyed immediately."),
    (r"upset failure", "Upset ESD failure", "The part still works but its life is shortened."),
    (r"rfc 1918", "RFC 1918", "The private IPv4 ranges: 10.0.0.0/8, 172.16.0.0-172.31.255.255 and 192.168.0.0/16."),
    (r"cable tray", "Cable tray", "A tray or channel that holds and routes cables overhead. It is not a rack system."),
    (r"\bIDFs?\b|intermediate distribution", "IDF", "Intermediate distribution frame: a closet on a floor or building that connects workstations back to the MDF."),
    (r"visio|lucidchart", "Visio / Lucidchart", "Diagramming tools for DRAWING network maps. They don't discover devices; Nmap does."),
    (r"floor plan", "Floor plan", "A drawing of the building's layout (rooms and jacks). It does not show the devices stacked in a rack."),
    (r"^\s*installation\s*$", "Installation", "Putting new software onto the system. A patch fixes existing software and a rollback goes back a version."),
    (r"\bEOL\b|end of life", "EOL", "End of life: the vendor stops selling the product. It is not a failure-rate measure."),
    (r"\bEOS\b|end of support", "EOS", "End of support: no more patches or help from the vendor. It is not a failure-rate measure."),
    (r"backbone cabl", "Backbone cabling", "Connects the entrance facility, the MDF and the IDFs to each other."),
    (r"fiber-optic cable|fiber optic", "Fiber-optic cable", "Light through glass: the longest distances. For a nearby wall jack you just need a patch cable."),
    (r"source port", "Source port", "The TCP/UDP field that identifies the SENDING application's port."),
    (r"acknowledgment number", "Acknowledgment number", "Tells the sender which byte the receiver expects next. It doesn't verify the data itself; the checksum does."),
    (r"window size", "Window size", "How much data the receiver will accept before an ACK (flow control)."),
    (r"checksum", "Checksum", "Lets the receiver verify that a segment arrived exactly as sent; if it doesn't match, the data is resent."),
    (r"registrar", "Domain registrar", "Sells and registers domain names. It does not issue digital certificates (a CA does)."),
    (r"802\.3 raw", "802.3 raw", "An old Ethernet frame format with no type field. Ethernet II is the current standard."),
    (r"\bFDDI\b", "FDDI", "An old fiber ring network technology, not Ethernet."),
    (r"token ring|token passing", "Token Ring", "An older LAN technology that passes a token. Wi-Fi doesn't use it; it uses CSMA/CA."),
    (r"\bLTE\b", "LTE", "A cellular data network for phones, with a carrier plan. It is not a low-power IoT building-automation radio."),
    (r"^\s*ethernet\s*$", "Ethernet", "The wired LAN standard (802.3). It is not a low-power IoT radio."),
    (r"\bDDoS\b", "DDoS", "Flooding a target with traffic from many machines. It is not an attack on an AP's settings."),
    (r"^\s*AES\s*$", "AES", "The strong cipher WPA2 uses (with CCMP). It is not obsolete."),
    (r"management plane", "Management plane", "Configuring and monitoring the devices. The CONTROL plane makes the forwarding decisions."),
    (r"^\s*(file|folder)\s*$", "File-level storage", "NAS shares files and folders. A SAN gives servers raw BLOCKS."),
    (r"^\s*byte\s*$", "Byte level", "Storage is shared as files or as blocks; 'byte' is not one of the levels."),
    (r"^\s*isolated\s*$", "Isolated VM network", "A VM network with no connection outside the hypervisor."),
    (r"single point of failure", "Single point of failure", "A DISADVANTAGE of virtualization: many VMs depend on one host."),
    (r"on-prem", "On-premises", "You own and run the hardware yourself. It is not a cloud service model."),
    (r"^\s*public\s*$", "Public cloud", "Shared infrastructure owned by a provider and used by many customers."),
    (r"^\s*private\s*$", "Private cloud", "Cloud infrastructure used by a single organization."),
    (r"^\s*hybrid\s*$", "Hybrid cloud", "A combination of two or more deployment models."),
    (r"^\s*community\s*$", "Community cloud", "A cloud shared by several organizations with common needs."),
    (r"^\s*v1\s*$", "SNMPv1", "The original SNMP: rarely used, with no real security."),
    (r"^\s*v2c?\s*$", "SNMPv2", "Widely used, but its community strings travel in cleartext. v3 adds authentication and encryption."),
    (r"^\s*v3\s*$", "SNMPv3", "The most secure SNMP version: authentication and encryption."),
    (r"^\s*cold\s*$", "Cold site", "Components exist but nothing is configured or connected; can take weeks."),
    (r"^\s*warm\s*$", "Warm site", "Partly configured and connected."),
    (r"^\s*hot\s*$", "Hot site", "Fully configured and ready; the most expensive."),
    (r"^\s*cloud\s*$", "Cloud DR", "A cloud provider hosts the recovery environment. The classic DR sites are cold, warm and hot."),
    (r"^\s*archive\s*$", "Archive", "Long-term storage of old data. It is not one of the full / incremental / differential backup types."),
    (r"traffic log", "Traffic log", "Records traffic passing through a device. It doesn't prove who did what."),
    (r"system log", "System log", "Records events on a system. An audit log is the one that shows who did what and when."),
    (r"audit report", "Audit report", "A review of controls or compliance. It isn't a record of what normal network behavior looks like."),
    (r"spiceworks", "Spiceworks", "Free IT inventory and monitoring software. It doesn't capture and decode TCP messages like Wireshark."),
    (r"task scheduler", "Task Scheduler", "Windows tool for scheduling programs; not where error clues are logged."),
    (r"control panel", "Control Panel", "Windows settings. The first place to look for clues is Event Viewer."),
    (r"registry editor|regedit", "Registry Editor", "Edits the Windows registry. It is risky and is not where events are logged."),
    (r"\bIIS\b", "IIS", "Microsoft's web server. It is not DNS software."),
    (r"apache|nginx", "Apache / nginx", "Open-source WEB servers, not DNS software."),
    (r"address pool|\bscope\b", "Address pool (scope)", "The range of addresses a DHCP server may hand out. A short LEASE time is what recycles them faster."),
    (r"^\s*reverse\s*$", "Reverse lookup", "IP address to name (PTR record, under .arpa)."),
    (r"^\s*forwarded\s*$", "Forwarded query", "A forwarding server passing a query on to another DNS server."),
    (r"^\s*NS\s*$", "NS record", "Identifies the authoritative name servers for a zone."),
    (r"^\s*A\s*$", "A record", "Maps a name to an IPv4 address."),
    (r"^\s*\.com\s*$", ".com", "A commercial top-level domain."),
    (r"^\s*\.int\s*$", ".int", "A restricted TLD for international organizations."),
    (r"^\s*\.net\s*$", ".net", "A top-level domain originally for network providers."),
    (r"peers", "Peers", "Equal participants. In IPv6 the word for nodes on the same link is NEIGHBORS."),
    (r"anycasts", "Anycast", "One address shared by several destinations; packets go to the nearest."),
    (r"classful", "Classful", "The old A/B/C class system with fixed mask sizes."),
    (r"tunneled", "Tunneled", "IPv6 carried inside IPv4 packets. Running both at once is dual stack."),
    (r"2000::/3", "2000::/3", "Global unicast addresses (routable on the Internet)."),
    (r"ff00::/8", "FF00::/8", "IPv6 multicast addresses."),
    (r"::1/128", "::1", "The IPv6 loopback address."),
    (r"\bEMI\b|electromagnetic", "EMI", "Electromagnetic interference: keep data cables away from power cables and motors."),
    (r"war chalk", "War chalking", "Marking where open Wi-Fi networks are found (very old school)."),
    (r"on-boarding", "On-boarding", "Granting a new person or device access; off-boarding removes it."),
    (r"beamforming", "Beamforming", "Focusing the signal toward a client. It is not how Bluetooth avoids interference (frequency hopping)."),
    (r"900 mhz", "900 MHz", "A sub-GHz band used by some IoT radios; Bluetooth is 2.4 GHz."),
    (r"^\s*polling\s*$", "Polling", "The NMS asking agents for data."),
    (r"fifo|lifo", "FIFO / LIFO", "Queue orderings (first-in-first-out, last-in-first-out); not congestion-control types."),
]

PROF_CIDR = [("201.25.145.52", 19), ("163.82.142.36", 20), ("121.34.183.36", 21), ("135.34.115.36", 22),
             ("135.34.115.121", 27), ("122.35.98.88", 28), ("121.153.235.117", 19), ("121.153.235.117", 20),
             ("132.16.221.40", 20)]
PROF_CLSM = [("129.1.56.0", 24, 8, 16), ("211.182.135.0", 24, 4, 50), ("221.180.0.0", 16, 4, 4000),
             ("221.180.0.0", 16, 5, 1000), ("23.59.0.0", 16, 5, 2000), ("221.180.121.0", 24, 4, 35),
             ("215.17.236.0", 24, 8, 25)]

LOGAN = [  # destination, prefix, interface, next hop, hops, speed(Mbps)
    ("10.1.1.0", 24, 14, "10.50.1.10", 1, 100), ("10.1.1.0", 24, 34, "10.50.1.5", 3, 500),
    ("10.1.2.0", 24, 14, "10.50.1.10", 1, 100), ("10.1.2.0", 24, 14, "10.50.1.5", 3, 500),
    ("10.200.1.0", 24, 34, "10.50.1.5", 1, 1000), ("10.200.1.0", 24, 14, "10.50.1.10", 3, 100),
    ("192.168.0.0", 16, 34, "10.50.1.5", 1, 1000), ("192.168.0.0", 16, 14, "10.50.1.10", 3, 100),
    ("172.17.3.0", 24, 34, "10.50.1.5", 2, 1000), ("172.17.3.0", 24, 44, "10.50.1.10", 2, 100),
    ("172.20.1.0", 25, 24, "Local", 0, 1000),
    ("0.0.0.0", 0, 34, "10.50.1.5", 1, 1000), ("0.0.0.0", 0, 14, "10.50.1.5", 3, 100),
]

PORTS = {"FTP (data)": "20", "FTP (control)": "21", "SSH / SFTP": "22", "Telnet": "23", "SMTP": "25", "DNS": "53",
         "DHCP (client->server)": "67", "DHCP (server->client)": "68", "TFTP": "69", "HTTP": "80", "POP3": "110",
         "NTP": "123", "IMAP4": "143", "SNMP (agent)": "161", "SNMP (trap)": "162", "LDAP": "389", "HTTPS": "443",
         "SMB (Windows file sharing)": "445", "Syslog": "514", "LDAPS": "636", "RDP": "3389"}
OSI = {"Hub": "1", "Switch": "2", "Router": "3", "NIC (MAC address)": "2", "Frame": "2", "Packet": "3", "Segment": "4",
       "Datagram (UDP)": "4", "Bits / voltage / light": "1", "MAC address": "2", "IP address": "3", "Port number": "4",
       "TCP": "4", "UDP": "4", "IP": "3", "ICMP": "3", "HTTP": "7", "SMTP": "7", "DNS": "7", "RDP": "7", "SNMP": "7",
       "Ethernet": "2", "Wi-Fi 802.11": "2", "IPsec": "3", "RIP / OSPF": "3", "FQDN / host name": "7",
       "Cable / fiber / radio": "1", "Layer 3 switch": "3", "ARP (book: touches 2 & 3; slides call it L2)": "2"}

STUDY_GUIDE = [
    ("OSI key layers 1-4 & 7; which layer each device works at", "1"), ("Headers, encapsulation, PDU names, address types per layer", "1"),
    ("Key protocols TCP/IP, UDP, SNMP, SMTP, HTTP, RDP", "1/4"), ("PAN, LAN, MAN, WAN", "1"), ("NIC, hub, switch, router", "1/7"),
    ("Topologies", "1"), ("Basic troubleshooting steps", "1"), ("Active Directory vs workgroup/peer-to-peer", "1"),
    ("Server vs client/workstation", "1"), ("Change management, documentation, patches", "2"),
    ("Contract types (MSA, SLA, ...)", "2"), ("Racks: height (U) and width", "2"), ("Basics of cables, fiber types, 100 m max", "2"),
    ("Entrance facility, backbone, demarc, MDF, IDF", "2"), ("Nmap", "2"), ("Binary vs decimal vs hexadecimal", "3/8"),
    ("Ports", "3"), ("DNS architecture, zones, root/TLD, records A AAAA MX PTR CNAME", "3"), ("DHCP", "3"),
    ("MAC addresses: OUI, length", "3"), ("Broadcast domains", "3/8"), ("ipconfig, ifconfig, ping", "3"),
    ("Windows file sharing (SMB 445)", "3"), ("IPv4 format, mask, loopback, private vs public, NAT, classes", "3"),
    ("IPv6 neighbors, dual stack", "3"), ("Ethernet MTU standard & jumbo, collisions, ARP", "4"),
    ("TCP vs UDP: flow control, connection, sequencing/checksum, handshake", "4"), ("Port number ranges", "3"),
    ("Telnet & SSH; VNC & RDP", "4"), ("VPN site-to-site vs client-to-site; IPsec basics", "4"),
    ("Encryption: PKI, CA, certificates, symmetric vs asymmetric, key pairs, CIA, HTTPS", "4"),
    ("tracert, ping (ICMP), netstat", "4"), ("Wi-Fi interference, overlapping channels, diffraction", "6"),
    ("Bluetooth, NFC, Z-Wave, infrared", "6"), ("802.11 standards & approx. throughput", "6"),
    ("MIMO, MU-MIMO, RTS/CTS, BSS, SSID, frequencies", "6"), ("Ad hoc, infrastructure, mesh", "6"),
    ("WEP, WPA, Enterprise & RADIUS, guest & captive portals, evil twin", "6"), ("Wi-Fi/spectrum analyzers", "6"),
    ("RFID tags, active vs passive", "6"), ("Virtualization pros/cons, hypervisor type 1 vs 2, vSwitch", "7"),
    ("Core-distribution-access", "7"), ("SAN, iSCSI", "7"), ("SDN basics", "7"), ("IaaS, PaaS, SaaS; cloud types", "7"),
    ("HA & fault tolerance: spares, clustering, MTBF/MTTR, hot/warm/cold sites", "7/12"),
    ("VLANs, relay agents, tag/trunk ports, segmentation", "8"), ("Slash/decimal/classes/binary conversions, hosts/networks", "8"),
    ("SUBNETTING: host+CIDR -> network/mask/broadcast; CLSM longhand", "8"), ("Managed vs unmanaged switches", "7/8"),
    ("IPv6 classless, prefix, hop limits", "8"), ("Power: brownout, sag, spike, UPS, generators", "12"),
    ("Backups: full, incremental, differential", "12"), ("Monitoring: taps, mirror/SPAN, Wireshark, baselines, SNMP, logs", "12"),
    ("NAS vs SAN; RAID levels", "12"), ("Tie it together: how a frame traverses a network", "L"),
]


# ---------------------------------------------------------------------------
# Step-by-step walk-throughs (the "dev mode" for networking). Each is a sequence diagram:
# actors across the top, one message per step. step = (from, to, label, explanation); from == to is a note.
# ---------------------------------------------------------------------------
WALKS = {
    "tcp": {
        "title": "TCP connection: three-way handshake and teardown",
        "tab_hint": "TCP / handshake",
        "actors": ["Client", "Server (port 443)"],
        "intro": "TCP is connection-oriented: the two ends agree on a connection before any data moves, and later close it politely.",
        "steps": [
            (0, 0, "Client wants a web page", "The client picks a random dynamic port (49152-65535) as its source port. The destination port is 443 (HTTPS)."),
            (0, 1, "1. SYN  (seq = 100)", "Step 1 of the three-way handshake: 'I want to open a connection. My sequence numbers start at 100.'"),
            (1, 0, "2. SYN/ACK  (seq = 300, ack = 101)", "Step 2: the server agrees ('ack 101' means 'I got your 100, send 101 next') and gives its own starting number."),
            (0, 1, "3. ACK  (ack = 301)", "Step 3: the client confirms. The connection is now ESTABLISHED, so data can flow."),
            (0, 1, "Data segment  (seq = 101, checksum)", "Each segment carries a sequence number and a checksum so the receiver can put data in order and detect damage."),
            (1, 0, "ACK  (ack = 600)", "The receiver acknowledges what arrived. If an ACK doesn't come, the sender retransmits: that is TCP's reliability."),
            (1, 1, "Flow control", "The ACK also carries a window size: 'send no more than this much before the next ACK', so a fast sender can't overwhelm a slow receiver."),
            (0, 1, "FIN", "Closing: the client says it has no more data to send."),
            (1, 0, "ACK, then FIN", "The server acknowledges and sends its own FIN."),
            (0, 1, "ACK", "The connection is closed. (UDP has none of this: no handshake, sequencing or flow control.)"),
        ],
        "summary": "Handshake: SYN, SYN/ACK, ACK.  TCP adds sequencing, checksums and flow control; UDP adds none of them.",
    },
    "dhcp": {
        "title": "DHCP: getting an IP address (DORA)",
        "tab_hint": "DHCP",
        "actors": ["New client", "DHCP server"],
        "intro": "A new device has no IP address yet, so every early message is a broadcast. DHCP uses UDP: port 67 on the server, 68 on the client.",
        "steps": [
            (0, 0, "Client boots, has no IP", "It uses 0.0.0.0 as its source and has no idea where a DHCP server is."),
            (0, 1, "1. DISCOVER (broadcast)", "Sent to 255.255.255.255: 'Is there a DHCP server out there?' Routers don't forward broadcasts, so a relay agent is needed if the server is on another subnet."),
            (1, 0, "2. OFFER", "The server offers an unused address from its scope (pool) with a mask, gateway, DNS server and lease time."),
            (0, 1, "3. REQUEST (broadcast)", "The client accepts the offer. It is broadcast so any other DHCP server knows its offer was not chosen."),
            (1, 0, "4. ACKNOWLEDGE", "The server confirms the lease. Now the client has the 'Big 4': IP address, mask, default gateway, DNS server."),
            (0, 0, "Lease renewal", "At about half the lease time the client asks to renew. If it can never reach a server it gives itself a 169.254.x.x (APIPA) address."),
        ],
        "summary": "DORA: Discover, Offer, Request, Acknowledge.  Shorter lease times recycle addresses faster; a reservation always gives one MAC the same IP.",
    },
    "dns": {
        "title": "DNS: looking up www.example.com",
        "tab_hint": "DNS",
        "actors": ["Your PC (resolver)", "Local DNS server", "Root server", ".com TLD server", "Authoritative server"],
        "intro": "The PC sends one RECURSIVE query. The local server does the ITERATIVE work: root, then TLD, then authoritative.",
        "steps": [
            (0, 0, "Check my own cache first", "The PC's resolver cache (ipconfig /displaydns) may already have the answer. ipconfig /flushdns clears it."),
            (0, 1, "Recursive query: www.example.com?", "'Give me a final answer, or tell me it can't be found.' A recursive query demands the whole answer."),
            (1, 1, "Check cache", "A caching server stores answers it looked up before."),
            (1, 2, "Iterative query", "The local server asks a root server (13 clusters). It doesn't know the name but knows who handles .com."),
            (2, 1, "Referral to .com", "The root server answers with the address of the .com TLD servers."),
            (1, 3, "Iterative query", "Next the local server asks the .com TLD server."),
            (3, 1, "Referral to example.com's servers", "The TLD server knows which authoritative servers hold example.com's zone (the NS records)."),
            (1, 4, "Iterative query", "The local server finally asks the authoritative server."),
            (4, 1, "Answer: A record 93.184.216.34", "The primary or secondary authoritative server holds the zone (A = IPv4, AAAA = IPv6, MX = mail, CNAME = alias, PTR = reverse)."),
            (1, 0, "Answer (and cache it)", "The local server returns the answer, caches it, and the PC can now open a TCP connection to the IP address."),
        ],
        "summary": "Root (13 clusters) -> TLD -> authoritative.  Client-to-local-server = recursive; local-server-to-others = iterative.  Secondary servers copy the primary by zone transfer.",
    },
    "arp": {
        "title": "ARP: finding a MAC address on the local network",
        "tab_hint": "ARP",
        "actors": ["PC-A  192.168.1.10", "Everyone on the LAN", "Router  192.168.1.1"],
        "intro": "To send a frame, PC-A needs the destination's MAC. For an outside destination the 'destination' is the default gateway.",
        "steps": [
            (0, 0, "Destination 8.8.8.8 is not on my network", "PC-A compares 8.8.8.8 with its own network ID using its mask. They differ, so the next hop is the default gateway 192.168.1.1."),
            (0, 0, "Check the ARP table", "arp -a shows the table of IP-to-MAC entries (dynamic and static). No entry for 192.168.1.1 yet."),
            (0, 1, "ARP request (broadcast)", "'Who has 192.168.1.1? Tell 192.168.1.10.' Sent to MAC FF:FF:FF:FF:FF:FF, so every device hears it."),
            (2, 0, "ARP reply (unicast)", "Only the router answers: '192.168.1.1 is at MAC 00:1A:2B:3C:4D:5E.'"),
            (0, 0, "Save it in the ARP table", "PC-A caches the entry and builds the frame: destination MAC = the router's, destination IP = 8.8.8.8."),
            (0, 2, "Frame sent", "ARP never crosses a router. On IPv6 the Neighbor Discovery Protocol (ICMPv6) does this job."),
        ],
        "summary": "ARP finds a MAC from an IP on the LOCAL network, by broadcast.  It never crosses a router.",
    },
    "wifi": {
        "title": "Wi-Fi: joining a network and sending data",
        "tab_hint": "Wi-Fi association and CSMA/CA",
        "actors": ["Client", "Access point"],
        "intro": "Wi-Fi radios can't detect collisions while sending, so they avoid them (CSMA/CA) and confirm every frame with an ACK.",
        "steps": [
            (1, 0, "Beacon (passive scanning)", "The AP regularly broadcasts a beacon with its SSID. A client that just listens is doing PASSIVE scanning."),
            (0, 1, "Probe request (active scanning)", "A client can instead send a probe request: ACTIVE scanning."),
            (1, 0, "Probe response", "The AP answers with its SSID and capabilities."),
            (0, 1, "Authentication", "Open authentication, or a WPA2/WPA3 handshake (PSK, or RADIUS with 802.1X for Enterprise)."),
            (0, 1, "Association request", "The client joins the BSS (the stations sharing this AP). With several APs sharing an ESSID the client can later roam."),
            (1, 0, "Association response", "The AP accepts and assigns an association ID. The client is now on the WLAN and can use DHCP."),
            (0, 0, "Listen before sending", "CSMA/CA: the client waits until the channel is idle (plus a random back-off) before transmitting."),
            (0, 1, "RTS (optional)", "Request to Send: 'I want the channel for this long.' It reduces collisions but lowers overall efficiency."),
            (1, 0, "CTS (optional)", "Clear to Send: the AP tells everyone else in range to stay quiet."),
            (0, 1, "Data frame", "An 802.11 frame has four address fields (an Ethernet frame has two)."),
            (1, 0, "ACK", "Every frame is acknowledged. No ACK means a possible collision, so the client retries. Verifying every frame is why Wi-Fi loses some throughput."),
        ],
        "summary": "CSMA/CA = avoid collisions with ACKs (wired Ethernet uses CSMA/CD = detect).  RTS/CTS is optional and costs efficiency.",
    },
    "tls": {
        "title": "HTTPS: asymmetric keys first, symmetric keys after",
        "tab_hint": "HTTPS / encryption",
        "actors": ["Browser", "Web server"],
        "intro": "HTTPS is HTTP inside SSL/TLS. It uses slow asymmetric encryption just to exchange a key, then fast symmetric encryption for the data.",
        "steps": [
            (0, 1, "Client hello", "The browser connects to port 443 and lists the encryption methods it supports."),
            (1, 0, "Server hello + certificate", "The server picks a method and sends its digital certificate: its identity plus its PUBLIC key, signed by a certificate authority (CA)."),
            (0, 0, "Verify the certificate", "The browser checks the CA's signature (PKI) and that the name matches. This is how it knows it is talking to the real site."),
            (0, 1, "Session key, encrypted with the server's public key", "Asymmetric encryption: only the server's PRIVATE key can decrypt it. Slow, so it is used only to share a key."),
            (1, 1, "Decrypt with the private key", "Now both sides hold the same secret session key."),
            (0, 1, "Encrypted data (symmetric)", "Both sides switch to symmetric encryption: one shared key, fast, used for the bulk data."),
            (1, 0, "Encrypted data (symmetric)", "Confidentiality (encryption) and integrity (tamper detection) from the CIA triad are both protected."),
        ],
        "summary": "Asymmetric = key pair, used for key exchange and identity.  Symmetric = one shared key, used for bulk data.  CA/PKI proves identity.",
    },
    "ipsec": {
        "title": "IPsec VPN: the five steps",
        "tab_hint": "IPsec / VPN",
        "actors": ["Site A gateway", "Site B gateway"],
        "intro": "IPsec works at the Network layer (AH and ESP) and is common in site-to-site VPNs, where hardware at each end builds the tunnel.",
        "steps": [
            (0, 0, "1. Initiation", "Traffic that matches the VPN policy ('interesting traffic') starts the process."),
            (0, 1, "2. Key management", "The gateways authenticate each other and set up a secure channel for exchanging keys (IKE)."),
            (1, 0, "3. Security negotiations", "They agree on the algorithms and settings (a security association): AH for integrity, ESP for encryption plus integrity."),
            (0, 1, "4. Data transfer", "User packets are encrypted and sent through the tunnel across the Internet. Users on each LAN notice nothing."),
            (1, 0, "4. Data transfer", "Replies come back the same way. (Client-to-site VPNs do this with software on a laptop instead.)"),
            (0, 1, "5. Termination", "The tunnel is torn down when the session ends or times out."),
        ],
        "summary": "IPsec steps: initiation, key management, negotiation, data transfer, termination.  IPsec = Layer 3; SSL/TLS = Transport layer.",
    },
    "vlan": {
        "title": "VLAN tagging (802.1Q) across a trunk",
        "tab_hint": "VLANs / 802.1Q",
        "actors": ["PC-A (VLAN 10)", "Switch 1", "Switch 2", "PC-B (VLAN 10)"],
        "intro": "VLANs split a switch into separate broadcast domains. Frames carry a 4-byte 802.1Q tag only on trunk (tagged) ports.",
        "steps": [
            (0, 1, "Untagged frame", "PC-A sends a normal Ethernet frame. It has no idea VLANs exist."),
            (1, 1, "Access port: assign VLAN 10", "The port is an ACCESS port that belongs to VLAN 10 only. The switch now knows which VLAN the frame belongs to."),
            (1, 2, "Trunk: frame + 802.1Q tag (VLAN 10)", "Over the trunk (tagged) port the switch inserts a 4-byte tag so the next switch knows the VLAN."),
            (2, 2, "Read the tag, pick the ports", "Switch 2 only forwards the frame out of ports in VLAN 10."),
            (2, 3, "Tag removed at the access port", "The access port strips the tag, so PC-B receives an ordinary frame."),
            (3, 3, "Different VLAN? Needs a router", "VLAN 20 is a different subnet. Traffic between VLANs must go through a router (router-on-a-stick) or a Layer 3 switch."),
        ],
        "summary": "Access port = one VLAN.  Trunk/tagged port = many VLANs, 802.1Q tag (+4 bytes).  Only managed switches support VLANs.  VLANs are Layer 2; subnets are Layer 3.",
    },
    "nat": {
        "title": "NAT / PAT: many private hosts share one public IP",
        "tab_hint": "NAT / PAT",
        "actors": ["PC  10.0.0.5", "NAT router", "Web server  203.0.113.9"],
        "intro": "NAT swaps private (RFC 1918) addresses for a public one, which is how IPv4 lasted so long. PAT keeps track of each session by port number.",
        "steps": [
            (0, 1, "src 10.0.0.5:50123  ->  dst 203.0.113.9:443", "The PC sends from its private address to the server's public address."),
            (1, 1, "Translation table entry", "The router records: 10.0.0.5:50123 <-> 198.51.100.7:61001 (its own public IP and a unique port: that is the PAT part)."),
            (1, 2, "src 198.51.100.7:61001  ->  dst 203.0.113.9:443", "The packet leaves with the PUBLIC source address. The server never sees 10.0.0.5."),
            (2, 1, "dst 198.51.100.7:61001", "The reply goes to the router's public IP and the port from the table."),
            (1, 0, "dst 10.0.0.5:50123", "The router looks up the port in its table and forwards to the right private host. Another PC would get a different port."),
        ],
        "summary": "NAT conserves public IPv4 addresses and hides the inside.  PAT shares ONE public IP by tracking ports.  Static NAT (SNAT, professor's definition) = a fixed public IP for an inbound server.",
    },
    "troubleshoot": {
        "title": "Troubleshooting: the 7 steps on a real problem",
        "tab_hint": "Troubleshooting method",
        "actors": ["You", "User / network"],
        "intro": "Worked example: 'I can't get to the Internet.' OSI troubleshooting goes bottom-up: rule out hardware before software.",
        "steps": [
            (0, 1, "1. Identify the problem", "Gather information, question the user (they may not mention what changed), and duplicate the problem if you can."),
            (0, 0, "2. Establish a theory of probable cause", "Start simple and at the bottom: Layer 1. Are the link lights on? Is the cable plugged in?"),
            (0, 1, "3. Test the theory", "Link light is off. Swap the patch cable. If the theory is wrong, make a new one (Layer 2, then 3...) or escalate."),
            (0, 0, "4. Establish a plan of action", "The light is on now but ipconfig shows 169.254.x.x (APIPA): DHCP failed. Plan: renew the lease, then check the DHCP server."),
            (0, 1, "5. Implement the solution (or escalate)", "ipconfig /release then /renew. If it were beyond your authority you would escalate."),
            (0, 1, "6. Verify full system functionality", "Ping the gateway, ping 8.8.8.8, ping a name, open a web page. Add preventive measures if appropriate."),
            (0, 0, "7. Document findings, actions and outcomes", "Document LAST, after you verify. Good records speed up the next problem."),
        ],
        "summary": "Identify, theory, test, plan, implement or escalate, verify, document.  OSI troubleshooting goes bottom-up.",
    },
}
WALK_ORDER = ["tcp", "dhcp", "dns", "arp", "wifi", "tls", "ipsec", "vlan", "nat", "troubleshoot"]

# Encapsulation (drawn as a growing stack, not as arrows)
ENCAP_STEPS = [
    ("Layer 7  Application", "data", "The application hands data to the stack (an HTTP request, an email...). The Layer 7 address is a host name / FQDN."),
    ("Layer 4  Transport", "segment", "Adds a Layer 4 header with the source and destination PORTS. PDU = segment (TCP) or datagram (UDP)."),
    ("Layer 3  Network", "packet", "Adds a Layer 3 header with the source and destination IP addresses. PDU = packet."),
    ("Layer 2  Data Link", "frame", "Adds a Layer 2 header (source and destination MAC) AND a trailer. PDU = frame. Only Layer 2 adds a trailer."),
    ("Layer 1  Physical", "bits", "The frame is sent as bits (voltage, light or radio). The receiver de-encapsulates in the reverse order."),
]

# ---------------------------------------------------------------------------
# Which lab / walk-through / cheat-sheet fits a question (keyword rules, checked in order)
# ---------------------------------------------------------------------------
LAB_RULES = [
    (r"frame.{0,30}(cross|travers)|router.{0,40}(rewrit|destination mac)|destination mac|source and destination mac", ("frame", None)),
    (r"routing table|longest prefix|next hop|metric|default route", ("route", None)),
    (r"clsm|equal.{0,12}subnet|how many (host|subnet)|\d+ subnets|borrow", ("clsm", None)),
    (r"subnet|cidr|mask|broadcast address|network id|/\d{1,2}\b|magic number|usable host", ("subnet", None)),
    (r"ipv6|::|fe80|dual stack|anycast", ("ipv6", None)),
    (r"binary|hexadecimal|\bhex\b|octet|decimal", ("binary", None)),
    (r"handshake|syn\b|tcp|udp|segment|flow control", ("walk", "tcp")),
    (r"dhcp|apipa|lease|relay agent", ("walk", "dhcp")),
    (r"dns|nslookup|recursive|iterative|zone|resolver", ("walk", "dns")),
    (r"\barp\b|neighbor", ("walk", "arp")),
    (r"csma|rts|cts|association|beacon|roaming|probe|wi-fi.{0,20}collision", ("walk", "wifi")),
    (r"https|certificate|asymmetric|symmetric|\bpki\b|ssl|tls|public key", ("walk", "tls")),
    (r"ipsec|vpn|tunnel", ("walk", "ipsec")),
    (r"vlan|802\.1q|trunk|tagged", ("walk", "vlan")),
    (r"\bnat\b|\bpat\b|port address", ("walk", "nat")),
    (r"troubleshoot|theory of probable|bottom-up|link light", ("walk", "troubleshoot")),
    (r"encapsulat|pdu|header|osi layer|which layer", ("encap", None)),
]


# ===========================================================================
#                          ENGINE (no GUI code in this part)
# ===========================================================================
LETTERS = "ABCDEFGH"

# ---------------------------------------------------------------------------
# Progress (the one file this trainer writes). Same format as the earlier terminal version:
# {"q": {id: {right, tries, last}}, "checklist": {index: bool}, "cards": [known flashcard terms]}
# ---------------------------------------------------------------------------
PROGRESS_FILE = os.path.join(os.path.expanduser("~"), ".is4440_trainer_progress.json")


def load_progress():
    try:
        with open(PROGRESS_FILE) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_progress(p=None):
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(PROGRESS if p is None else p, f)
        return True
    except Exception:
        return False


PROGRESS = load_progress()


def record(key, correct):
    r = PROGRESS.setdefault("q", {}).setdefault(key, {"right": 0, "tries": 0, "last": None})
    r["tries"] += 1
    r["right"] += int(bool(correct))
    r["last"] = bool(correct)
    save_progress()


def progress_of(key):
    r = PROGRESS.get("q", {}).get(key)
    return r if isinstance(r, dict) and r.get("tries") else None


def known_cards():
    c = PROGRESS.get("cards", [])
    return set(c) if isinstance(c, list) else set()


def set_card_known(term, known):
    cards = known_cards()
    (cards.add if known else cards.discard)(term)
    PROGRESS["cards"] = sorted(cards)
    save_progress()


def checklist_marks():
    m = PROGRESS.setdefault("checklist", {})
    return m if isinstance(m, dict) else {}


def set_check(index, value):
    PROGRESS.setdefault("checklist", {})[str(index)] = bool(value)
    save_progress()


# ---------------------------------------------------------------------------
# Subnetting math (the professor's two-table + magic-number method)
# ---------------------------------------------------------------------------
TABLE2 = [0, 128, 192, 224, 240, 248, 252, 254, 255]


def ip2int(s):
    return int(ipaddress.IPv4Address(s))


def int2ip(n):
    return str(ipaddress.IPv4Address(n))


def mask_of(prefix):
    return int2ip((0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF) if prefix else "0.0.0.0"


def usable(prefix):
    return max(0, 2 ** (32 - prefix) - 2)


def bits32(s):
    """'192.168.1.5' -> '11000000.10101000.00000001.00000101'"""
    return ".".join(f"{int(o):08b}" for o in s.split("."))


def norm_ip(s):
    s = (s or "").strip().split("/")[0]
    try:
        return str(ipaddress.IPv4Address(s))
    except Exception:
        return None


def solve_cidr(ip, prefix):
    n = ip2int(ip)
    m = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    net = n & m
    bc = net | (~m & 0xFFFFFFFF)
    return {"network": int2ip(net), "mask": int2ip(m), "broadcast": int2ip(bc),
            "first": int2ip(net + 1) if prefix < 31 else int2ip(net),
            "last": int2ip(bc - 1) if prefix < 31 else int2ip(bc), "usable": usable(prefix)}


def cidr_steps(ip, prefix):
    """Worked solution as a list of steps. -> (solution dict, steps). step = {"title", "lines": [...], "key": ...}"""
    sol = solve_cidr(ip, prefix)
    octs = [int(x) for x in ip.split(".")]
    steps = []
    if prefix >= 32:
        steps.append({"key": "mask", "title": "A /32 is a single host",
                      "lines": [f"/32 means all 32 bits are network bits, so the 'network' is just {ip} itself.",
                                "There are no host bits, so there is no separate broadcast address or host range."]})
        return sol, steps
    idx = prefix // 8                     # index of the first octet where the mask is not 255
    ones = prefix % 8
    mask_oct = TABLE2[ones]
    magic = 256 - mask_oct
    full = ["255"] * idx
    lines = [f"/{prefix} means {prefix} one-bits, then {32 - prefix} zero-bits.",
             f"Full octets of 1s: {idx}  ->  the first {idx} mask octet(s) are 255."]
    if idx < 4:
        lines.append(f"Octet #{idx + 1} is where the mask stops being 255. It holds {ones} one-bit(s): "
                     f"Table 2 with {ones} ones = {mask_oct}.")
    lines.append(f"Octets after that are 0.   Mask = {sol['mask']}")
    steps.append({"key": "mask", "title": "1. Turn the prefix into a mask", "lines": lines, "octet": idx})
    steps.append({"key": "binary", "title": "2. (Check) the same thing in binary",
                  "lines": [f"IP       {bits32(ip)}", f"Mask     {bits32(sol['mask'])}",
                            f"AND      {bits32(sol['network'])}   <- the network ID",
                            "The mask's 1-bits keep the network part; its 0-bits are the host part, which becomes 0 in the network ID."],
                  "bits": (bits32(ip), bits32(sol["mask"]), bits32(sol["network"])), "prefix": prefix})
    steps.append({"key": "magic", "title": "3. Magic number",
                  "lines": [f"Magic number = 256 - {mask_oct} = {magic}.",
                            f"That is the block size in octet #{idx + 1}: the networks there start at multiples of {magic}."], "octet": idx})
    mult = list(range(0, 256, magic))
    net_oct = (octs[idx] // magic) * magic
    shown = [m for m in mult if m <= octs[idx]]
    nxt = net_oct + magic
    seq = ", ".join(str(m) for m in shown[-8:]) + (f", {nxt}" if nxt <= 255 else "")
    steps.append({"key": "count", "title": f"4. Count up by {magic} to the block holding {octs[idx]}",
                  "lines": [("...  " if len(shown) > 8 else "") + seq,
                            f"{octs[idx]} falls between {net_oct} and {nxt if nxt <= 255 else 256}, so octet #{idx + 1} of the network is {net_oct}.",
                            f"The broadcast octet is the next block minus 1:  {nxt if nxt <= 255 else 256} - 1 = {net_oct + magic - 1}."],
                  "octet": idx})
    steps.append({"key": "answer", "title": "5. Network ID and broadcast",
                  "lines": [f"Network ID:  {sol['network']}   (copy the first {idx} octet(s), then {net_oct}, then zeros)",
                            f"Mask:        {sol['mask']}",
                            f"Broadcast:   {sol['broadcast']}   (copy the first {idx} octet(s), then {net_oct + magic - 1}, then 255s)"],
                  "answer": True, "net_oct": net_oct, "bc_oct": net_oct + magic - 1, "magic": magic, "octet": idx})
    h = 32 - prefix
    steps.append({"key": "hosts", "title": "6. Host range",
                  "lines": [f"Host bits = 32 - {prefix} = {h}.   Usable hosts = 2^{h} - 2 = {sol['usable']:,}.",
                            f"First usable: {sol['first']}     Last usable: {sol['last']}"]})
    return sol, steps


def clsm_solution(base, base_prefix, n_subnets, hosts):
    h = 1
    while 2 ** h - 2 < hosts:
        h += 1
    new_prefix = 32 - h
    possible = 2 ** (new_prefix - base_prefix) if new_prefix >= base_prefix else 0
    nets, start, size = [], ip2int(base), 2 ** h
    for i in range(min(n_subnets, possible)):
        net = start + i * size
        nets.append((int2ip(net), int2ip(net + size - 1)))
    return new_prefix, possible, nets, h


def clsm_steps(base, base_prefix, n_subnets, hosts):
    """Worked CLSM solution. -> (new_prefix, subnets [(net, first, last, bc)], steps)"""
    new_prefix, possible, nets, h = clsm_solution(base, base_prefix, n_subnets, hosts)
    steps = []
    small = (f"2^{h - 1} - 2 = {2 ** (h - 1) - 2:,} is too small" if h > 1 else "")
    steps.append({"key": "hostbits", "title": "1. How many host bits?",
                  "lines": [f"Each subnet needs at least {hosts:,} usable hosts.",
                            "Find the smallest h with 2^h - 2 >= hosts (Table 1):",
                            f"  2^{h} - 2 = {2 ** h - 2:,}  >= {hosts:,}  OK" + (f"      ({small})" if small else ""),
                            f"So h = {h} host bits."]})
    ok = possible >= n_subnets
    lines = [f"New prefix = 32 - {h} = /{new_prefix}   (mask {mask_of(new_prefix)}).",
             f"You borrowed {new_prefix - base_prefix} bit(s) from the /{base_prefix}, which gives 2^{new_prefix - base_prefix} = {possible} possible subnets."]
    lines.append(f"You need {n_subnets}: " + ("enough." if ok else "NOT enough, so this requirement can't be met inside that network."))
    lines.append("Assume CIDR is enabled: the all-zeros and all-ones subnets are usable, and hosts = 2^h - 2.")
    steps.append({"key": "prefix", "title": "2. New prefix", "lines": lines})
    block = 2 ** h
    idx_oct = max(0, (new_prefix - 1) // 8) if new_prefix else 0
    magic = max(1, block // (256 ** (3 - idx_oct)))
    steps.append({"key": "magic", "title": "3. Block size (magic number)",
                  "lines": [f"Each subnet covers 2^{h} = {block:,} addresses.",
                            f"In octet #{idx_oct + 1} that means counting up by {magic}."]})
    rows = []
    for net, bc in nets:
        n_int = ip2int(net)
        rows.append((net, int2ip(n_int + 1) if h > 1 else net, int2ip(ip2int(bc) - 1) if h > 1 else bc, bc))
    steps.append({"key": "list", "title": f"4. List the {len(rows)} subnet(s)",
                  "lines": [f"#{i}:  {r[0]}/{new_prefix}   hosts {r[1]} - {r[2]}   broadcast {r[3]}" for i, r in enumerate(rows, 1)],
                  "answer": True})
    return new_prefix, rows, steps


def random_cidr_problem(rng=random):
    prefix = rng.choice([17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 12, 13, 14, 26, 27, 28, 20, 21, 22])
    while True:
        ip = ".".join(str(rng.randint(1, 223) if i == 0 else rng.randint(0, 255)) for i in range(4))
        if not (ip.startswith("127.") or ip.startswith("0.")):
            return ip, prefix


def random_clsm_problem(rng=random):
    while True:
        base_prefix = rng.choice([24, 24, 24, 16, 16, 20, 22])
        first = rng.choice([rng.randint(1, 126), rng.randint(128, 191), rng.randint(192, 223)])
        octs = [first] + [rng.randint(0, 255) for _ in range(3)]
        base = int2ip(ip2int(".".join(map(str, octs))) & ((0xFFFFFFFF << (32 - base_prefix)) & 0xFFFFFFFF))
        h = rng.randint(3, (32 - base_prefix) - 2)
        hosts = rng.randint(2 ** (h - 1) - 1, 2 ** h - 2)
        new_prefix = 32 - h
        maxn = 2 ** (new_prefix - base_prefix)
        if maxn >= 2:
            return base, base_prefix, rng.randint(2, min(8, maxn)), hosts


# The professor's CIDR Practice Problems sheet (his answers are in section 5 of the handoff notes)
PROF_ANSWERS = {  # verified against the sheet: address -> (network, mask, broadcast)
    ("201.25.145.52", 19): ("201.25.128.0", "255.255.224.0", "201.25.159.255"),
    ("163.82.142.36", 20): ("163.82.128.0", "255.255.240.0", "163.82.143.255"),
    ("121.34.183.36", 21): ("121.34.176.0", "255.255.248.0", "121.34.183.255"),
    ("135.34.115.36", 22): ("135.34.112.0", "255.255.252.0", "135.34.115.255"),
    ("135.34.115.121", 27): ("135.34.115.96", "255.255.255.224", "135.34.115.127"),
    ("122.35.98.88", 28): ("122.35.98.80", "255.255.255.240", "122.35.98.95"),
    ("121.153.235.117", 19): ("121.153.224.0", "255.255.224.0", "121.153.255.255"),
    ("121.153.235.117", 20): ("121.153.224.0", "255.255.240.0", "121.153.239.255"),
    ("132.16.221.40", 20): ("132.16.208.0", "255.255.240.0", "132.16.223.255"),
}


# ---------------------------------------------------------------------------
# Routing table lab (Logan router A)
# ---------------------------------------------------------------------------
def _mask_int(p):
    return (0xFFFFFFFF << (32 - p)) & 0xFFFFFFFF if p else 0


def route_lookup(dest, metric):
    d = ip2int(dest)
    matches = [r for r in LOGAN if (d & _mask_int(r[1])) == ip2int(r[0])]
    best_len = max(r[1] for r in matches)
    cands = [r for r in matches if r[1] == best_len]
    if metric == "hops":
        best = min(cands, key=lambda r: r[4])
        tie = sum(1 for r in cands if r[4] == best[4]) > 1
    else:
        best = max(cands, key=lambda r: r[5])
        tie = sum(1 for r in cands if r[5] == best[5]) > 1
    return best, best_len, tie


def speed_text(mbps):
    return f"{mbps // 1000} Gb" if mbps >= 1000 else f"{mbps} Mb"


def route_steps(dest, metric="hops"):
    """-> dict(rows matched flags, final index, steps). Row indexes refer to LOGAN."""
    d = ip2int(dest)
    flags = [(d & _mask_int(r[1])) == ip2int(r[0]) for r in LOGAN]
    match_ix = [i for i, f in enumerate(flags) if f]
    best_len = max(LOGAN[i][1] for i in match_ix)
    cand_ix = [i for i in match_ix if LOGAN[i][1] == best_len]
    if metric == "hops":
        key = lambda i: LOGAN[i][4]                 # noqa: E731
        pick = min(cand_ix, key=key)
        tie_ix = [i for i in cand_ix if key(i) == key(pick)]
    else:
        key = lambda i: -LOGAN[i][5]                # noqa: E731
        pick = min(cand_ix, key=key)
        tie_ix = [i for i in cand_ix if key(i) == key(pick)]
    chosen = LOGAN[pick]
    steps = []
    lines = []
    for i in match_ix:
        r = LOGAN[i]
        lines.append(f"Row {i + 1}: {dest} AND {mask_of(r[1])} (/{r[1]}) = {int2ip(d & _mask_int(r[1]))}  =  {r[0]}  MATCH")
    others = len(LOGAN) - len(match_ix)
    lines.append(f"The other {others} rows don't match (their network ID differs from {dest} AND their mask).")
    steps.append({"key": "match", "title": "1. Which routes match the destination?", "lines": lines, "rows": match_ix})
    ll = [f"Prefix lengths of the matching rows: " + ", ".join(f"/{LOGAN[i][1]}" for i in match_ix)]
    ll.append(f"The LONGEST prefix (most specific route) wins: /{best_len}." + ("  That is the default route 0.0.0.0/0: nothing more specific matched." if best_len == 0 else ""))
    ll.append(f"{len(cand_ix)} route(s) left.")
    steps.append({"key": "longest", "title": "2. Longest prefix wins", "lines": ll, "rows": cand_ix})
    if len(cand_ix) == 1:
        steps.append({"key": "metric", "title": "3. Metric (tie-breaker)",
                      "lines": ["Only one route is left, so the metric isn't needed."], "rows": cand_ix})
    else:
        label = "HOP COUNT (fewest hops wins)" if metric == "hops" else "LINK SPEED (fastest wins)"
        ml = [f"The router's metric is {label}."]
        for i in cand_ix:
            r = LOGAN[i]
            ml.append(f"Row {i + 1}: {r[4]} hop(s), {speed_text(r[5])}")
        if len(tie_ix) > 1:
            ml.append("These routes tie on this metric. Try the other metric to see which one wins.")
        else:
            ml.append(f"Row {pick + 1} wins.")
        steps.append({"key": "metric", "title": "3. Metric breaks the tie", "lines": ml, "rows": [pick]})
    where = ("directly connected: deliver on the local network (no next-hop router)" if chosen[3] == "Local"
             else f"forward to next hop {chosen[3]}")
    steps.append({"key": "result", "title": "4. Forward the packet",
                  "lines": [f"Route used: {chosen[0]}/{chosen[1]}", f"Out interface {chosen[2]}, {where}."],
                  "rows": [pick], "answer": True})
    return {"flags": flags, "final": pick, "tie": len(tie_ix) > 1, "steps": steps, "chosen": chosen, "best_len": best_len}


# ---------------------------------------------------------------------------
# Frame traversal model
# ---------------------------------------------------------------------------
def rand_mac(rng=random):
    return ":".join(f"{rng.randint(0, 255):02X}" for _ in range(6))


def frame_model(nat=False, routers=1, rng=random):
    """A PC sends to a web server through 1 or 2 routers. -> dict with devices, hops and teaching steps."""
    pc = {"name": "PC-A", "ip": f"192.168.10.{rng.randint(10, 99)}", "mac": rand_mac(rng)}
    r1 = {"name": "Router R1", "in_ip": "192.168.10.1", "in_mac": rand_mac(rng)}
    srv = {"name": "Server S", "ip": f"203.0.113.{rng.randint(20, 200)}", "mac": rand_mac(rng)}
    port = 49152 + rng.randint(0, 9000)
    dst_port = 443
    pub_ip, pat_port = "198.51.100.7", 61000 + rng.randint(0, 900)
    devices = [pc, r1]
    if routers == 1:
        r1["out_ip"], r1["out_mac"] = "203.0.113.1", rand_mac(rng)
        edge = r1
    else:
        r1["out_ip"], r1["out_mac"] = "10.0.0.1", rand_mac(rng)
        r2 = {"name": "Router R2", "in_ip": "10.0.0.2", "in_mac": rand_mac(rng), "out_ip": "203.0.113.1", "out_mac": rand_mac(rng)}
        devices.append(r2)
        edge = r2
    devices.append(srv)
    hops = []
    hops.append({"name": f"Hop 1: PC-A -> {r1['name']}", "src_mac": pc["mac"], "dst_mac": r1["in_mac"], "src_ip": pc["ip"],
                 "dst_ip": srv["ip"], "src_port": str(port), "dst_port": str(dst_port),
                 "where": "on LAN 1 (192.168.10.0/24)"})
    if routers == 2:
        src_ip, src_port = (pub_ip, str(pat_port)) if (nat and False) else (pc["ip"], str(port))
        hops.append({"name": "Hop 2: R1 -> R2", "src_mac": r1["out_mac"], "dst_mac": devices[2]["in_mac"], "src_ip": src_ip,
                     "dst_ip": srv["ip"], "src_port": src_port, "dst_port": str(dst_port), "where": "on the link 10.0.0.0/30"})
    last_src_mac = (devices[2]["out_mac"] if routers == 2 else r1["out_mac"])
    src_ip = pub_ip if nat else pc["ip"]
    src_port = str(pat_port) if nat else str(port)
    hops.append({"name": f"Hop {len(hops) + 1}: {edge['name']} -> Server S", "src_mac": last_src_mac, "dst_mac": srv["mac"],
                 "src_ip": src_ip, "dst_ip": srv["ip"], "src_port": src_port, "dst_port": str(dst_port),
                 "where": "on the server's network (203.0.113.0/24)"})
    for i, h in enumerate(hops):
        prev = hops[i - 1] if i else None
        h["changed"] = {k for k in ("src_mac", "dst_mac", "src_ip", "dst_ip", "src_port", "dst_port")
                        if prev is not None and prev[k] != h[k]}
    steps = [{"key": "setup", "hop": None, "title": "The situation",
              "lines": [f"PC-A ({pc['ip']}) wants to open a web page on Server S ({srv['ip']}), port 443.",
                        f"They are on different networks, joined by {routers} router(s)." + ("  NAT/PAT is on the edge router." if nat else "  No NAT in this example.")]},
             {"key": "local", "hop": None, "title": "PC-A: local or remote?",
              "lines": [f"PC-A compares the server's network ID with its own, using its mask (/24).",
                        f"{srv['ip']} is NOT on 192.168.10.0/24, so the frame must go to the DEFAULT GATEWAY ({r1['in_ip']}).",
                        "The destination IP stays the server's, but the destination MAC will be the gateway's."]},
             {"key": "arp", "hop": None, "title": "ARP finds the gateway's MAC",
              "lines": [f"PC-A broadcasts: 'Who has {r1['in_ip']}?'  The router replies with MAC {r1['in_mac']}.",
                        "ARP only works on the local network; it never crosses a router."]}]
    for i, h in enumerate(hops):
        if i == 0:
            lines = ["PC-A builds the frame and sends it:", "  Layer 4: ports (source is a random dynamic port, destination 443)",
                     "  Layer 3: PC-A's IP -> the server's IP", "  Layer 2: PC-A's MAC -> the gateway's MAC"]
        else:
            lines = [f"The router strips the old Layer 2 header (de-encapsulates), looks up the route, and ARPs for the next hop's MAC.",
                     "It builds a NEW frame:", "  Layer 2 addresses are REWRITTEN (new source MAC = the router's outgoing interface, new destination MAC = the next hop)."]
            ch = h["changed"] - {"src_mac", "dst_mac"}
            if ch:
                lines.append("  NAT/PAT also rewrote: " + ", ".join(sorted(c.replace("_", " ") for c in ch)) + " (the edge router, not a normal hop).")
            else:
                lines.append("  Layer 3 IP addresses and Layer 4 ports are unchanged.")
        steps.append({"key": f"hop{i + 1}", "hop": i, "title": h["name"], "lines": lines})
    steps.append({"key": "summary", "hop": None, "title": "Key idea",
                  "lines": ["Layer 2 (MAC) addresses are rewritten at EVERY router hop.",
                            "Layer 3 (IP) and Layer 4 (port) stay end to end, unless NAT/PAT rewrites the source IP (and port) at the edge."]})
    return {"devices": devices, "hops": hops, "steps": steps, "nat": nat, "routers": routers, "pc": pc, "srv": srv}


# ---------------------------------------------------------------------------
# Generated multiple-choice subnetting questions (used in the exam simulation)
# ---------------------------------------------------------------------------
def gen_cidr_mc(rng=random):
    p = rng.choice([19, 20, 21, 22, 26, 27, 28, 29])
    ip = f"{rng.randint(1, 223)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    if ip.startswith("127."):
        ip = "129" + ip[ip.index("."):]
    s = solve_cidr(ip, p)
    right = f"Network {s['network']}, mask {s['mask']}, broadcast {s['broadcast']}"
    wrongs = set()
    for dp in (-1, 1, 2):
        t = solve_cidr(ip, max(8, min(30, p + dp)))
        wrongs.add(f"Network {t['network']}, mask {t['mask']}, broadcast {t['broadcast']}")
    wrongs.add(f"Network {s['network']}, mask {s['mask']}, broadcast {int2ip(ip2int(s['broadcast']) + 1)}")
    wrongs.discard(right)
    ch = [right] + rng.sample(sorted(wrongs), min(3, len(wrongs)))
    rng.shuffle(ch)
    return Q("GEN-cidr", "8", f"Given the host address {ip} /{p}, what are the network ID, subnet mask and broadcast address?",
             ch, right, f"Magic-number method: mask {s['mask']}, block size {256 - int(s['mask'].split('.')[p // 8]) if p % 8 else 256} in octet {p // 8 + 1}. "
             "Practice the longhand version in the Subnetting Gym.", "Generated: midterm subnetting type 1", author="GENERATED")


def gen_hosts_mc(rng=random):
    p = rng.randint(20, 30)
    right = str(usable(p))
    ch = [right, str(2 ** (32 - p)), str(usable(p + 1)), str(usable(p - 1))]
    rng.shuffle(ch)
    return Q("GEN-hosts", "8", f"How many usable host addresses are in a /{p} network?", ch, right,
             f"2^(32-{p}) - 2 = {right}. Subtract 2 for the network and broadcast addresses.", "Generated: simple subnetting",
             author="GENERATED")


def gen_clsm_mc(rng=random):
    base_prefix = rng.choice([24, 24, 16])
    o = rng.randint(192, 223) if base_prefix == 24 else rng.randint(128, 191)
    base = f"{o}.{rng.randint(0, 255)}.{'0' if base_prefix == 16 else rng.randint(0, 255)}.0"
    h = rng.randint(3, 6) if base_prefix == 24 else rng.randint(9, 13)
    hosts = rng.randint(2 ** (h - 1) - 1, 2 ** h - 2)
    newp = 32 - h
    n = min(4, 2 ** (newp - base_prefix))
    right = f"/{newp}"
    ch = [right, f"/{newp - 1}", f"/{newp + 1}", f"/{newp + 2}"]
    rng.shuffle(ch)
    return Q("GEN-clsm", "8", f"You own {base}/{base_prefix} and need {n} equal subnets with at least {hosts:,} hosts each. "
             f"Which mask should each subnet use (most efficient)?", ch, right,
             f"Smallest h with 2^h - 2 >= {hosts:,} is h = {h} (2^{h} - 2 = {2 ** h - 2:,}), so the mask is 32 - {h} = /{newp}.",
             "Generated: CLSM", author="GENERATED")


# ---------------------------------------------------------------------------
# Who wrote each question (shown as a tag on every question)
# ---------------------------------------------------------------------------
PROF_IDS = ("L-04", "L-05")


def origin_of(item):
    """'prof' = built from Prof. Norwood's own material, 'gen' = generated by the program, 'claude' = written by Claude."""
    qid = str(item.get("id", ""))
    if item.get("author") == "PROFESSOR" or qid in PROF_IDS or qid.startswith("PROF-"):
        return "prof"
    if item.get("author") == "GENERATED" or qid.startswith("GEN-"):
        return "gen"
    return "claude"


def origin_chip(item):
    return {"prof": "PROFESSOR'S MATERIAL", "gen": "GENERATED PRACTICE", "claude": "PRACTICE QUESTION (by Claude)"}[origin_of(item)]


def origin_note(item):
    o = origin_of(item)
    if o == "prof":
        return ("Built from Prof. Norwood's own subnetting lecture material. The question and the correct answer follow his slides; "
                "any wrong options were written by Claude.")
    if o == "gen":
        return ("Made up by the program from random numbers, like the subnetting questions on the exam. It is not one of the "
                "professor's problems.")
    return ("Written by Claude from the slides and textbook (source below), in the style of your professor's focus list. "
            "It is not one of the professor's questions, and none of the bank is copied from a real exam.")


# ---------------------------------------------------------------------------
# Skills (for weak-spot drills)
# ---------------------------------------------------------------------------
SKILLS = {
    "subnet": "Subnetting, binary & masks",
    "layers": "OSI layers, PDUs & devices",
    "protocols": "TCP/IP protocols & ports",
    "addressing": "MAC, IPv4/IPv6, NAT, DNS & DHCP",
    "wireless": "Wireless networking",
    "security": "Encryption, VPN & remote access",
    "arch": "Switching, VLANs, virtualization & cloud",
    "avail": "Availability, backup & power",
    "monitor": "Monitoring, tools & troubleshooting",
    "docs": "Cabling, documentation & contracts",
}
SKILL_SHORT = {"subnet": "Subnetting", "layers": "Layers & devices", "protocols": "Protocols & ports", "addressing": "Addressing",
               "wireless": "Wireless", "security": "Security", "arch": "Architecture", "avail": "Availability",
               "monitor": "Monitoring", "docs": "Cabling & docs"}
_SKILL_PATTERNS = [
    ("subnet", r"subnet|cidr|clsm|vlsm|mask|/\d{1,2}\b|binary|hexadecimal|\bhex\b|octet|usable host|magic|broadcast address|network id"),
    ("layers", r"\bosi\b|layer [1-7]|\bpdu\b|segment|datagram|\bframe|\bpacket|encapsulat|\bhub\b|\bswitch\b|\brouter\b|\bnic\b"),
    ("protocols", r"\btcp\b|\budp\b|\bicmp\b|\barp\b|\bport\b|\bhttp|\bsmtp|\bsnmp|\bftp|\bssh\b|telnet|\brdp\b|handshake|\bmtu\b|ethernet|\bsmb\b|\bntp\b|ldap"),
    ("addressing", r"\bmac\b|\boui\b|ipv4|ipv6|\bnat\b|\bpat\b|\bdns\b|\bdhcp\b|apipa|loopback|private|gateway|class [a-e]\b|\brecord|zone|socket"),
    ("wireless", r"wi-fi|wifi|wireless|802\.11|ghz|bluetooth|\bnfc\b|zigbee|z-wave|rfid|antenna|ssid|\bwpa|\bwep\b|signal|rssi|\bchannel|mimo"),
    ("security", r"encrypt|\bpki\b|certificate|asymmetric|symmetric|\bvpn\b|ipsec|\bcia\b|\bssl\b|\btls\b|radius|captive|evil twin|firewall"),
    ("arch", r"3-tier|spine|\bsdn\b|\bsan\b|\bnas\b|iscsi|hypervisor|virtual|vswitch|cloud|iaas|paas|saas|\bstp\b|managed|vlan|trunk|tagged|segmentation"),
    ("avail", r"backup|incremental|differential|\braid\b|\bups\b|generator|brownout|blackout|surge|spike|\bmtbf\b|\bmttr\b|\brpo\b|\brto\b|hot site|cold site|warm site|cluster|\bspare|redundan|disaster|replication|snapshot"),
    ("monitor", r"troubleshoot|\bping\b|tracert|netstat|nslookup|ipconfig|wireshark|baseline|\bsnmp\b|syslog|\blog\b|\bmonitor|analyzer|\btap\b|mirror|\bqos\b|congestion|flow control|nmap"),
    ("docs", r"cabling|demarc|\bmdf\b|\bidf\b|\brack|patch panel|documentation|\brfp\b|\bmou\b|\bmsa\b|\bsow\b|\bsla\b|change management|\bpatch\b|rollback|upgrade|\btia\b|fiber|\besd\b|fail-open|fail-close"),
]
_CHAPTER_SKILL = {"1": "layers", "2": "docs", "3": "addressing", "4": "protocols", "6": "wireless", "7": "arch", "8": "subnet",
                  "12": "monitor", "L": "layers"}
SKILL_TAB = {"subnet": "subnet", "layers": "layers", "protocols": "protocols", "addressing": "addressing", "wireless": "wifi",
             "security": "protocols", "arch": "arch", "avail": "avail", "monitor": "monitor", "docs": "docs"}


def skills_of(q):
    text = " ".join([q["prompt"], " ".join(q["choices"]), q["why"]]).lower()
    found = [k for k, pat in _SKILL_PATTERNS if re.search(pat, text)]
    base = _CHAPTER_SKILL.get(q["ch"])
    if base and base not in found:
        found.insert(0, base)
    return found[:3] or ["layers"]


for _q in BANK:
    _q["skills"] = skills_of(_q)
    if _q["kind"] in ("mc", "multi"):      # fixed pseudo-random option order (the same every run)
        random.Random("order-" + _q["id"]).shuffle(_q["choices"])

# ---------------------------------------------------------------------------
# "Why isn't my answer right?" notes: facts about the terms in each option
# ---------------------------------------------------------------------------
def _split_alternatives(pat):
    """Split a regex on its top-level '|' (ignoring '|' inside groups and escaped characters)."""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(pat):
        c = pat[i]
        if c == "\\" and i + 1 < len(pat):
            cur += pat[i:i + 2]
            i += 2
            continue
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        if c == "|" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
        i += 1
    parts.append(cur)
    return parts


def _compile_fact(pat):
    """Alternatives written with capital letters (acronyms such as MAN, CAN, AP, IP) are case-sensitive, so ordinary lowercase
    words like 'man' and 'can' don't match them. Alternatives written in lowercase ignore case."""
    alts = []
    for part in _split_alternatives(pat):
        has_upper = re.search(r"[A-Z]", re.sub(r"\\.", "", part)) is not None
        alts.append(part if has_upper else "(?i:" + part + ")")
    return re.compile(r"(?<!\w)(?:" + "|".join(alts) + ")")


_FACT_RES = [(_compile_fact(pat), label, fact) for pat, label, fact in FACTS]
TRAPS = {}   # hand-written notes for the trickiest questions: {question id: {option text: note}}


def option_facts(text, limit=2):
    """Facts about the terms an option is ABOUT: every match for a short option, only a leading term for a long one.
    The term that appears first (and the more specific one on a tie) comes first; terms inside an already-used term are skipped."""
    t = text.strip()
    short = len(t) <= 40
    hits = []
    for order, (rx, label, fact) in enumerate(_FACT_RES):
        m = rx.search(t)
        if m and (short or m.start() <= 3):
            hits.append((m.start(), -(m.end() - m.start()), order, m.start(), m.end(), label, fact))
    hits.sort()
    found, seen, spans = [], set(), []
    for _, _, _, s, e, label, fact in hits:
        if label in seen or any(s >= a and e <= b for a, b in spans):
            continue
        seen.add(label)
        spans.append((s, e))
        found.append((label, fact))
        if len(found) >= limit:
            break
    return found


_CLASS_RANGES = {"1-126": "Class A", "128-191": "Class B", "192-223": "Class C", "224-239": "Class D (multicast)",
                 "240-254": "Class E (research)"}
_NETSTAT = {"-a": "all connections and listening ports", "-e": "Ethernet (interface) statistics: errors and discards",
            "-r": "the routing table", "-o": "the owning process ID", "-n": "numeric addresses and ports",
            "-b": "the process (program) name", "-s": "statistics for each protocol"}
_MTU_NOTE = {576: "576 bytes is an old minimum IP size, not the Ethernet MTU.",
             9198: "About 9,000-9,198 bytes is the JUMBO frame size, not the standard MTU.",
             65535: "65,535 bytes is the largest possible IP packet, not an Ethernet MTU.",
             1500: "1,500 bytes is the standard Ethernet MTU."}


_CIDR_PROMPT = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})\s*/\s*(\d{1,2})")


def cidr_relation_note(q, ip):
    """For 'network ID / broadcast of host/prefix' questions: where does this option sit relative to the real subnet?"""
    m = _CIDR_PROMPT.search(q["prompt"])
    if not m or not re.search(r"network id|broadcast|first usable|last usable|network address", q["prompt"], re.I):
        return ""
    host, prefix = m.group(1), int(m.group(2))
    sol = solve_cidr(host, prefix)
    if ip == sol["network"]:
        return f"{ip} is the network ID of {host}/{prefix}."
    if ip == sol["broadcast"]:
        return f"{ip} is the broadcast address of {host}/{prefix}, the last address of the block."
    own = solve_cidr(ip, prefix)
    if own["network"] == sol["network"]:
        return f"{ip} is just a host address inside the block {sol['network']} - {sol['broadcast']} (the block that holds {host})."
    return (f"{ip} belongs to a different /{prefix} block (it starts at {own['network']}). "
            f"The block that holds {host} runs {sol['network']} - {sol['broadcast']}.")


def describe_ip(ip):
    o = [int(x) for x in ip.split(".")]
    if ip == "255.255.255.255":
        return "255.255.255.255 is the broadcast address (every device on the local network)."
    if ip == "0.0.0.0":
        return "0.0.0.0 means 'unassigned' (or 'any'); it is not a usable host address."
    if all(x in TABLE2 for x in o) and o == sorted(o, reverse=True):
        bits = sum(bin(x).count("1") for x in o)
        return f"{ip} is a subnet MASK: /{bits}."
    a = ipaddress.IPv4Address(ip)
    if o[0] == 127:
        return f"{ip} is in the loopback range 127.x.x.x (your own computer)."
    if ip.startswith("169.254."):
        return f"{ip} is an APIPA address: a Windows PC gave it to itself because DHCP failed."
    if 224 <= o[0] <= 239:
        return f"{ip} is Class D (multicast)."
    if a.is_private:
        return f"{ip} is a PRIVATE (RFC 1918) address."
    cls = "A" if o[0] <= 126 else "B" if o[0] <= 191 else "C" if o[0] <= 223 else "E"
    extra = ""
    if o[0] == 172:
        extra = " The private 172 range is only 172.16.0.0-172.31.255.255."
    elif o[0] == 192 and o[1] != 168:
        extra = " The private 192 range is only 192.168.x.x."
    return f"{ip} is a PUBLIC Class {cls} address.{extra}"


def computed_note(q, text):
    """Notes worked out from the option itself: numbers, masks, ports, addresses, binary, units."""
    t = text.strip()
    pr = q["prompt"].lower()
    if t in _CLASS_RANGES:
        return f"{t} is the {_CLASS_RANGES[t]} range."
    m = re.fullmatch(r"/(\d{1,2})", t)
    if m and 0 < int(m.group(1)) <= 32:
        p = int(m.group(1))
        return f"/{p} = {mask_of(p)}, with {usable(p):,} usable hosts."
    m = re.match(r"(\d{1,3}(?:\.\d{1,3}){3})\b", t)
    if m and all(int(x) < 256 for x in m.group(1).split(".")):
        rel = cidr_relation_note(q, m.group(1))
        if rel:
            return rel
        if re.search(r"network id|broadcast address|first usable|last usable|network address", pr):
            return ""
        return describe_ip(m.group(1))
    if re.fullmatch(r"[01]{8}", t):
        return f"{t} is {int(t, 2)} in decimal."
    if "netstat" in pr and t in _NETSTAT:
        return f"netstat {t} shows {_NETSTAT[t]}."
    if "mtu" in pr or "frame" in pr:
        n = re.sub(r"[^0-9]", "", t.split()[0]) if t and t[0].isdigit() else ""
        if n and int(n) in _MTU_NOTE:
            return _MTU_NOTE[int(n)]
    if "rack" in pr and "inch" in t:
        return "A standard rack is 19 inches wide (23-inch racks also exist); one rack unit (1U) is 1.75 inches tall."
    if re.fullmatch(r"\d+ m \(\d[\d,]* ft\)", t) and ("length" in pr or "cable" in pr):
        return "Twisted-pair Ethernet segments top out at 100 m (328 ft); longer runs need fiber or a repeater/switch."
    m = re.fullmatch(r"(\d[\d,]*)", t)
    if m:
        n = int(m.group(1).replace(",", ""))
        if "host" in pr and n + 2 > 2 and (n + 2) & (n + 1) == 0:
            h = (n + 2).bit_length() - 1
            return f"{n:,} usable hosts = 2^{h} - 2, which is a /{32 - h}."
        if "bits" in pr or "bit " in pr:
            return f"{n} bits."
        if ("port" in pr or "protocol" in pr) and str(n) in {v for v in PORTS.values()}:
            names = [k for k, v in PORTS.items() if v == str(n)]
            return f"Port {n} is {names[0]}."
        if n <= 255 and ("binary" in pr or "octet" in pr or "decimal" in pr or "mask" in pr):
            return f"{n} is {n:08b} in binary."
        if n > 255 and ("binary" in pr or "octet" in pr or "decimal" in pr):
            return f"{n} is too big for one octet (an octet is 0-255)."
        if str(n) in {v for v in PORTS.values()}:
            return f"Port {n} is {[k for k, v in PORTS.items() if v == str(n)][0]}."
        if n <= 255:
            return f"{n} is {n:08b} in binary."
    if re.fullmatch(r"[0-9A-Fa-f]{2}", t) and "hex" in pr:
        return f"{t.upper()} in hex is {int(t, 16)} in decimal."
    return ""


def note_for(q, choice):
    hand = TRAPS.get(q["id"], {}).get(choice)
    if hand:
        return hand
    comp = computed_note(q, choice)
    facts = option_facts(choice, limit=1 if comp else 2)
    return "  ".join(([comp] if comp else []) + [f"{label}: {fact}" for label, fact in facts])


def diagnose(q, picks):
    """picks = chosen option texts. -> [(option, note)] for each WRONG pick (note may be '')."""
    return [(ch, note_for(q, ch)) for ch in picks if ch not in q["answer"]]


def multi_feedback(q, picks):
    missed = [a for a in q["answer"] if a not in picks]
    extra = [p for p in picks if p not in q["answer"]]
    return missed, extra


# --- related flashcards ---------------------------------------------------------------------------------
_CARD_STOP = {"and", "the", "vs", "basics", "steps", "summary", "table", "rule", "models", "model", "types", "type", "key", "list",
              "layers", "layer", "data", "network", "networks", "address", "addresses", "one", "line", "each", "pieces"}
_FLASH_EXTRA = {
    "OSI layers 1-7": ["osi", "layers 1", "layer 5", "layer 6"], "PDUs by layer": ["pdu", "segment", "datagram", "frame", "packet"],
    "Addresses by layer": ["address type", "which address"], "Devices by layer": ["hub", "switch", "router", "nic"],
    "Hub vs switch vs router": ["hub", "switch", "router"], "Key ports": ["port", "443", "445", "3389"],
    "Big 4 TCP/IP settings": ["big 4", "default gateway", "dns server"], "IPv4 classes": ["class a", "class b", "class c", "class d"],
    "Private IPv4 (RFC 1918)": ["private", "rfc 1918"], "Special IPv4": ["loopback", "apipa", "255.255.255.255"],
    "Slash to mask": ["/24", "/26", "/27", "mask"], "Usable hosts": ["usable host", "2^h"], "Hosts in /n": ["usable host", "hosts in"],
    "CIDR problem steps": ["network id", "broadcast address", "magic number", "host address"],
    "CLSM problem steps": ["clsm", "equal subnets", "equal-size"], "Magic number": ["magic number", "block size"],
    "Subnetting Table 1": ["table 1", "powers of 2", "powers of two"], "Subnetting Table 2": ["table 2", "high-order", "mask octet"],
    "Binary place values": ["binary", "octet"], "Hexadecimal": ["hexadecimal", "hex"], "Subnet mask table": ["mask octet", "table 2"],
    "TCP handshake / teardown": ["handshake", "syn"], "TCP": ["tcp"], "UDP": ["udp"],
    "Frame traversal rule": ["frame", "rewritten", "router hop"], "Routing table lookup": ["routing table", "longest prefix", "metric", "next hop"],
    "DHCP steps (DORA)": ["dora", "discover", "offer"], "APIPA": ["apipa", "169.254"],
    "VLSM vs CLSM": ["vlsm", "clsm"], "Backup comparison": ["incremental", "differential", "backup"], "RAID": ["raid"],
    "Wi-Fi bands": ["2.4 ghz", "5 ghz"], "RSSI scale": ["rssi", "dbm"], "Wi-Fi security summary": ["wpa", "wep", "radius"],
    "NIST cloud characteristics": ["measured service", "elasticity", "nist"], "Virtualization pros and cons": ["virtualization"],
    "Contract types in one line each": ["rfp", "mou", "msa", "sow", "sla"], "Troubleshooting steps": ["troubleshoot", "theory of probable"],
}


def _card_keys(term):
    keys = set(k.lower() for k in _FLASH_EXTRA.get(term, []))
    for piece in re.split(r"[/,()]| vs | & ", term):
        piece = piece.strip().lower()
        if len(piece) >= 3 and piece not in _CARD_STOP and not re.fullmatch(r"[\d\s.\-]+", piece):
            keys.add(piece)
    return keys


_CARD_KEYS = [(t, d, [re.compile(r"(?<!\w)" + re.escape(k) + r"(?!\w)") for k in _card_keys(t)]) for t, d in FLASHCARDS]


def related_flashcards(q, limit=3):
    text = " ".join([q["prompt"], " ".join(q["answer"]), q["why"]]).lower()
    scored = []
    for term, defn, rxs in _CARD_KEYS:
        hits = sum(1 for rx in rxs if rx.search(text))
        if hits:
            scored.append((-hits, term, defn))
    scored.sort()
    return [(t, d) for _, t, d in scored[:limit]]


# ---------------------------------------------------------------------------
# Which lab / walk-through / cheat sheet fits a question
# ---------------------------------------------------------------------------
_IP_PREFIX = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})\s*/\s*(\d{1,2})")
_CLSM_Q = re.compile(r"you own (\S+?)/(\d+) and need (\d+) equal subnets with at least ([\d,]+) hosts", re.I)


def lab_for(q):
    """-> {"lab": 'subnet'|'clsm'|'route'|'frame'|'binary'|'ipv6'|'walk'|'encap', "arg": walk key or None, "args": {...}} or None"""
    prompt = q["prompt"]
    m = _CLSM_Q.search(prompt)
    if m:
        return {"lab": "clsm", "arg": None, "args": {"base": m.group(1), "bp": int(m.group(2)), "n": int(m.group(3)),
                                                      "hosts": int(m.group(4).replace(",", ""))}}
    m = _IP_PREFIX.search(prompt)
    if m:
        return {"lab": "subnet", "arg": None, "args": {"ip": m.group(1), "prefix": int(m.group(2))}}
    text = (prompt + " " + " ".join(q["answer"])).lower()
    for pat, (lab, arg) in LAB_RULES:
        if re.search(pat, text):
            args = {}
            pm = re.search(r"/(\d{1,2})\b", prompt)
            if pm and lab in ("subnet", "clsm"):
                args["prefix"] = int(pm.group(1))
            return {"lab": lab, "arg": arg, "args": args}
    return None


# ---------------------------------------------------------------------------
# Exam simulation
# ---------------------------------------------------------------------------
EXAM_WEIGHTS = {"1": 9, "2": 8, "3": 12, "4": 10, "6": 9, "7": 9, "8": 7, "12": 8, "L": 2}


def exam_minutes(n):
    """Professor's rule: fewer than 70 questions = 80 minutes, more than 70 = 90. Exactly 70 isn't stated: use the longer one."""
    return 80 if n < 70 else 90


def build_exam(n=70, rng=random):
    """n questions: 4 generated subnetting questions + the rest sampled from the bank, weighted by module."""
    n = max(8, n)
    k = n - 4
    total = sum(EXAM_WEIGHTS.values())
    quota = {ch: w * k / total for ch, w in EXAM_WEIGHTS.items()}
    take = {ch: int(v) for ch, v in quota.items()}
    for ch, _ in sorted(quota.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True):
        if sum(take.values()) >= k:
            break
        take[ch] += 1
    pool = []
    for ch, cnt in take.items():
        qs = [q for q in BANK if q["ch"] == ch]
        pool += rng.sample(qs, min(len(qs), cnt))
    rng.shuffle(pool)
    pool = pool[:k] + [gen_cidr_mc(rng), gen_cidr_mc(rng), gen_clsm_mc(rng), gen_hosts_mc(rng)]
    rng.shuffle(pool)
    return pool


# ---------------------------------------------------------------------------
# Speed drills
# ---------------------------------------------------------------------------
DRILL_SETS = {
    "Ports and protocols": ["port2name", "name2port"],
    "OSI layers": ["osi"],
    "Subnet quick math": ["hosts", "mask", "slash", "magic", "table2"],
    "Binary, decimal and hex": ["bin", "dec", "hex", "dec2hex"],
    "Classes and private ranges": ["class", "private"],
}


def _port_names(name):
    head = name.split("(")[0].lower()
    toks = {t for t in re.split(r"[\s/]+", head) if t}
    if "imap4" in toks:
        toks.add("imap")
    return toks


def make_drill(kind, rng=random):
    """-> {"kind", "prompt", "answer", "accept": set of normalized answers}"""
    if kind == "port2name":
        name, port = rng.choice(list(PORTS.items()))
        return {"kind": kind, "prompt": f"Which protocol uses port {port}?", "answer": name, "accept": _port_names(name)}
    if kind == "name2port":
        name, port = rng.choice(list(PORTS.items()))
        return {"kind": kind, "prompt": f"What port does {name} use?", "answer": port, "accept": {port}}
    if kind == "osi":
        thing, layer = rng.choice(list(OSI.items()))
        return {"kind": kind, "prompt": f"{thing}: which OSI layer (1-7)?", "answer": f"Layer {layer}", "accept": {layer}}
    if kind == "hosts":
        p = rng.randint(16, 30)
        return {"kind": kind, "prompt": f"How many usable hosts are in a /{p}?", "answer": f"{usable(p):,}", "accept": {str(usable(p))}}
    if kind == "mask":
        p = rng.randint(8, 30)
        return {"kind": kind, "prompt": f"Write /{p} as a dotted-decimal mask:", "answer": mask_of(p), "accept": {mask_of(p)}}
    if kind == "slash":
        p = rng.randint(8, 30)
        return {"kind": kind, "prompt": f"What slash prefix is {mask_of(p)}?", "answer": f"/{p}", "accept": {str(p)}}
    if kind == "magic":
        o = rng.choice(TABLE2[1:8])
        return {"kind": kind, "prompt": f"The mask octet is {o}. What is the magic number (block size)?", "answer": str(256 - o),
                "accept": {str(256 - o)}}
    if kind == "table2":
        n = rng.randint(1, 8)
        return {"kind": kind, "prompt": f"Table 2: what value does an octet with {n} one-bit(s) (from the left) have?",
                "answer": str(TABLE2[n]), "accept": {str(TABLE2[n])}}
    if kind == "bin":
        v = rng.choice(TABLE2[1:] + [rng.randint(0, 255)])
        return {"kind": kind, "prompt": f"Write {v} in 8-bit binary:", "answer": f"{v:08b}", "accept": {f"{v:08b}"}}
    if kind == "dec":
        v = rng.randint(0, 255)
        return {"kind": kind, "prompt": f"Convert binary {v:08b} to decimal:", "answer": str(v), "accept": {str(v)}}
    if kind == "hex":
        v = rng.randint(0, 255)
        return {"kind": kind, "prompt": f"Convert hex {v:02X} to decimal:", "answer": str(v), "accept": {str(v)}}
    if kind == "dec2hex":
        v = rng.randint(0, 255)
        return {"kind": kind, "prompt": f"Convert decimal {v} to two hex digits:", "answer": f"{v:02X}", "accept": {f"{v:02x}"}}
    if kind == "class":
        o = rng.choice([rng.randint(1, 126), rng.randint(128, 191), rng.randint(192, 223), rng.randint(224, 239)])
        ip = f"{o}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
        ans = "A" if o <= 126 else "B" if o <= 191 else "C" if o <= 223 else "D"
        return {"kind": kind, "prompt": f"What class is {ip}? (A, B, C or D)", "answer": ans, "accept": {ans.lower()}}
    ip = rng.choice(["10.4.5.6", "172.16.9.1", "172.31.200.2", "172.32.0.1", "192.168.44.3", "192.169.1.1", "169.254.3.3", "11.1.1.1",
                     "172.15.255.1", "8.8.8.8"])
    ans = "yes" if ipaddress.IPv4Address(ip).is_private and not ip.startswith("169.254") else "no"
    return {"kind": "private", "prompt": f"Is {ip} an RFC 1918 private address? (yes/no)", "answer": ans, "accept": {ans, ans[0]}}


def check_drill(d, text):
    t = (text or "").strip().lower().replace(" ", "").replace(",", "").lstrip("/")
    if d["kind"] in ("port2name",):
        raw = (text or "").strip().lower()
        return any(tok in raw for tok in d["accept"])
    if d["kind"] == "bin":
        return t == d["answer"]
    return t in {a.lower().replace(" ", "").lstrip("/") for a in d["accept"]}


# ---------------------------------------------------------------------------
# Professor's study-guide checklist: each item also knows which questions practice it
# ---------------------------------------------------------------------------
STUDY_KEYS = [
    r"layer|osi|pdu|\bhub\b|switch|router|\bnic\b", r"encapsul|pdu|header|frame|packet|segment|datagram|address type",
    r"\btcp\b|\budp\b|snmp|smtp|http|rdp", r"\bpan\b|\blan\b|\bman\b|\bwan\b|campus", r"\bnic\b|\bhub\b|switch|router",
    r"topolog|\bbus\b|\bstar\b|\bring\b|mesh", r"troubleshoot|theory|bottom", r"active directory|peer-to-peer|\bp2p\b|client-server",
    r"\bnos\b|server|client", r"change|document|patch|rollback|upgrade", r"\brfp\b|\bmou\b|\bmsa\b|\bsow\b|\bsla\b",
    r"rack|\b1u\b|\bu\b", r"fiber|smf|mmf|cable|100 m|utp", r"entrance|backbone|demarc|\bmdf\b|\bidf\b", r"nmap",
    r"binary|hexadecimal|\bhex\b|decimal", r"port", r"dns|root|tld|zone|\bmx\b|\bptr\b|cname|aaaa", r"dhcp|lease|apipa|scope",
    r"\bmac\b|\boui\b", r"broadcast", r"ipconfig|ifconfig|\bping\b", r"\bsmb\b|445|file sharing",
    r"ipv4|loopback|private|\bnat\b|class [a-e]|rfc 1918|apipa", r"ipv6|neighbor|dual stack", r"mtu|jumbo|collision|\barp\b|ethernet",
    r"\btcp\b|\budp\b|handshake|flow control|sequenc", r"well-known|registered|dynamic|port number", r"telnet|\bssh\b|\bvnc\b|\brdp\b",
    r"vpn|ipsec|site-to-site|client-to-site", r"pki|certificate|symmetric|asymmetric|\bcia\b|https|encrypt",
    r"tracert|traceroute|\bping\b|icmp|netstat", r"interference|overlap|diffraction|channel|multipath|attenuation|reflection",
    r"bluetooth|\bnfc\b|z-wave|infrared|zigbee", r"802\.11|wi-fi [4-7]|mbps|gbps", r"mimo|rts|cts|\bbss\b|ssid|ghz",
    r"ad hoc|infrastructure|mesh", r"wep|wpa|radius|captive|evil twin|guest", r"analyzer|spectrum|site survey", r"rfid|active|passive",
    r"virtual|hypervisor|vswitch|vnic|nfv", r"core|distribution|access|3-tier|spine", r"\bsan\b|iscsi|fibre channel|infiniband",
    r"\bsdn\b|control plane|data plane|controller", r"iaas|paas|saas|cloud", r"availability|fault|mtbf|mttr|spare|cluster|hot site|warm|cold",
    r"vlan|relay|trunk|tagged|segment|802\.1q", r"/\d|slash|usable|hosts|class [a-e]|mask", r"subnet|cidr|clsm|network id|broadcast address|magic",
    r"managed|unmanaged", r"ipv6|prefix|hop limit|classless", r"brownout|sag|spike|surge|\bups\b|generator|blackout|power",
    r"backup|incremental|differential|\bfull\b|3-2-1|rpo|rto|snapshot|replication", r"\btap\b|mirror|span|wireshark|baseline|snmp|\blog\b|monitor|analyzer",
    r"\bnas\b|\bsan\b|raid", r"frame|hop|router|\bmac\b|traverse",
]


def study_questions(index):
    """Questions that practice one study-guide item (by keyword, inside the modules the item names)."""
    item, chs = STUDY_GUIDE[index]
    chapters = set(c for c in re.split(r"[/ ,]+", chs) if c)
    pat = re.compile(STUDY_KEYS[index], re.I) if index < len(STUDY_KEYS) else None
    pool = [q for q in BANK if q["ch"] in chapters] or list(BANK)
    if pat:
        hit = [q for q in pool if pat.search(q["prompt"] + " " + " ".join(q["answer"]))]
        if len(hit) >= 3:
            return hit
        hit2 = [q for q in pool if pat.search(q["prompt"] + " " + " ".join(q["choices"]) + " " + q["why"])]
        if len(hit2) >= 3:
            return hit2
    return pool


def accuracy_by(key_of, names):
    """Saved accuracy grouped by key_of(question) -> {key: [right, tries]} for keys in names."""
    stats = {}
    for q in BANK:
        r = progress_of(q["id"])
        if r:
            for k in key_of(q):
                s = stats.setdefault(k, [0, 0])
                s[0] += r["right"]
                s[1] += r["tries"]
    return {k: v for k, v in stats.items() if k in names}


# ===========================================================================
# CHEAT SHEETS (data). Section = {"h": heading, "cols": [...], "rows": [[...]], "note": text} or {"h", "lines": [...]}.
# The subnetting tables are computed, not typed, so they can't contain typos.
# ===========================================================================
def table1_rows():
    return [[f"2^{i}", f"{2 ** i:,}"] for i in range(13)]


def table2_rows():
    out = []
    for i in range(9):
        bits = ("1" * i).ljust(8, "0")
        out.append([str(i), f"{bits[:4]} {bits[4:]}", str(TABLE2[i]), str(256 - TABLE2[i]) if i < 8 else "1"])
    return out


def mask_rows(lo=8, hi=30):
    rows = []
    for p in range(lo, hi + 1):
        idx, ones = p // 8, p % 8
        magic = 256 - TABLE2[ones]
        rows.append([f"/{p}", mask_of(p), str(32 - p), f"octet {idx + 1}: {magic}" if idx < 4 else "-", f"{usable(p):,}"])
    return rows


def subnet_cheat_text():
    """A one-page, plain-text summary of the subnetting tables and steps (for copying or saving)."""
    out = ["IS 4440 - SUBNETTING CHEAT SHEET  (Prof. Norwood's two-table + magic-number method)", "=" * 74, "",
           "TABLE 1 (powers of 2)                 TABLE 2 (high-order bits in a mask octet)"]
    for i in range(13):
        left = f"  2^{i:<2} = {2 ** i:<6,}"
        right = ""
        if i <= 8:
            bits = ("1" * i).ljust(8, "0")
            right = f"  {i} ones: {bits[:4]} {bits[4:]} = {TABLE2[i]:<3}  (magic number {256 - TABLE2[i] if i < 8 else 1})"
        out.append(left.ljust(38) + right)
    out += ["", "BINARY PLACE VALUES (one octet):  128  64  32  16   8   4   2   1", "",
            "CIDR PROBLEM  (given host + /prefix -> network ID, mask, broadcast)",
            "  1) Find the octet where the mask stops being 255.   (/19 -> third octet: 3 ones = 224)",
            "  2) Magic number = 256 - that mask octet.             (256 - 224 = 32)",
            "  3) Count up by the magic number to the block that holds the address. That is the network.",
            "  4) Broadcast = the next block minus 1.  Octets after it: 0 for the network, 255 for the broadcast.",
            "  Usable hosts = 2^h - 2  (h = 32 - prefix).", "",
            "CLSM PROBLEM  (N equal subnets, at least H hosts each)",
            "  1) Smallest h with 2^h - 2 >= H.     2) New prefix = 32 - h.     3) List the blocks, counting up by the block size.",
            "  Assume CIDR is enabled: all-zeros and all-ones subnets are usable. VLSM is not tested.", "",
            "PREFIX   MASK              HOST BITS   MAGIC           USABLE HOSTS"]
    for r in mask_rows(8, 30):
        out.append(f"{r[0]:<8} {r[1]:<17} {r[2]:<11} {r[3]:<15} {r[4]}")
    return "\n".join(out)


CHEAT_ORDER = ["layers", "ports", "addressing", "subnet", "protocols", "wifi", "arch", "avail", "monitor", "docs", "calc"]
CHEAT = {
    "layers": {"title": "OSI, devices & topologies", "sections": [
        {"h": "OSI layers, PDUs, addresses and devices", "cols": ["Layer", "Name", "PDU", "Address", "Devices / examples"], "rows": [
            ["7", "Application", "data", "FQDN / host name", "HTTP, SMTP, DNS, RDP, SNMP, FTP, SSH"],
            ["6", "Presentation", "data", "-", "(mostly folded into 7)"],
            ["5", "Session", "data", "-", "(mostly folded into 7)"],
            ["4", "Transport", "segment (TCP) / datagram (UDP)", "port number", "TCP, UDP; Layer 4 switch / firewall"],
            ["3", "Network", "packet", "IP address", "router, Layer 3 switch; IP, ICMP, RIP, OSPF, IPsec"],
            ["2", "Data Link", "frame (header + trailer)", "MAC address", "switch, NIC; Ethernet, Wi-Fi, STP"],
            ["1", "Physical", "bits", "-", "hub, repeater, cables, NIC; voltage / light / radio"]],
         "note": "Bottom-up: Please Do Not Throw Sausage Pizza Away. The exam focuses on layers 1-4 and 7. Only Layer 2 adds a TRAILER."},
        {"h": "Connectivity devices", "cols": ["Device", "Layer", "What it does"], "rows": [
            ["Hub", "1", "Repeats every signal out of all other ports (one collision and one broadcast domain)"],
            ["Switch", "2", "Forwards frames by MAC address; each port is its own collision domain; belongs to one network"],
            ["Layer 3 switch", "2-3", "A switch that can also route between networks by IP"],
            ["Router", "3", "Connects 2+ networks, forwards by IP, does not forward broadcasts"],
            ["NIC", "1-2", "Holds the MAC address; Ethernet/Wi-Fi protocols are in its firmware"],
            ["Firewall", "3-7", "Filters traffic by rules"]],
         "note": "Devices are known by the HIGHEST OSI layer they read and process."},
        {"h": "Network types", "cols": ["Type", "Size", "Notes"], "rows": [
            ["PAN", "personal devices", "Bluetooth / NFC; the smallest"],
            ["LAN", "one building or office", "You own the cables"],
            ["MAN / CAN", "city or campus", "Group of connected LANs"],
            ["WAN", "wide area", "The Internet is the largest and most varied WAN; you usually don't own the links"]]},
        {"h": "Topologies", "cols": ["Topology", "Shape"], "rows": [
            ["Bus", "all devices on one backbone (daisy-chained switches)"], ["Star", "every device to one central switch"],
            ["Ring", "each device to two neighbors"], ["Mesh", "devices connect to several others"],
            ["Star-bus (hybrid)", "stars hanging off a bus"], ["Extended star", "workstations -> IDFs -> MDF"]],
         "note": "Physical topology = how devices and cables fit together. Logical topology = how access to the network is controlled."},
        {"h": "Network models", "cols": ["Model", "Who controls resources", "Notes"], "rows": [
            ["Peer-to-peer", "each computer's own OS", "Simple and cheap, NOT scalable"],
            ["Client-server", "central server / domain (Active Directory, AD DS)", "Central credentials and control, scalable, NOS"]]},
        {"h": "Troubleshooting (7 steps)", "lines": [
            "1 Identify the problem   2 Establish a theory of probable cause   3 Test the theory",
            "4 Establish a plan of action   5 Implement the solution or escalate   6 Verify full system functionality   7 Document",
            "OSI troubleshooting goes bottom-up: link lights (Layer 1) first. Users may not tell you what changed."]},
    ]},
    "ports": {"title": "Ports", "sections": [
        {"h": "Ports to know", "cols": ["Port", "Service", "Transport", "Notes"], "rows": [
            ["20 / 21", "FTP", "TCP", "data / control; cleartext"], ["22", "SSH / SFTP", "TCP", "encrypted remote CLI and file transfer"],
            ["23", "Telnet", "TCP", "cleartext remote CLI"], ["25", "SMTP", "TCP", "sends email"],
            ["53", "DNS", "UDP / TCP", "names to IPs"], ["67 / 68", "DHCP", "UDP", "server / client"],
            ["69", "TFTP", "UDP", "no authentication"], ["80", "HTTP", "TCP", "web, cleartext"], ["110", "POP3", "TCP", "receives email (downloads)"],
            ["123", "NTP", "UDP", "time"], ["143", "IMAP4", "TCP", "receives email (stays on server)"],
            ["161 / 162", "SNMP", "UDP", "162 = traps"], ["389", "LDAP", "TCP / UDP", "directory (Active Directory)"],
            ["443", "HTTPS", "TCP", "HTTP over SSL/TLS"], ["445", "SMB", "TCP", "Windows file sharing"], ["514", "syslog", "UDP", "log collection"],
            ["587", "SMTPS", "TCP", "secure SMTP submission"], ["636", "LDAPS", "TCP", "LDAP over SSL/TLS"], ["993", "IMAPS", "TCP", "IMAP over SSL/TLS"],
            ["995", "POP3S", "TCP", "POP3 over SSL/TLS"], ["1433", "SQL Server", "TCP", "Microsoft SQL Server"], ["3389", "RDP", "TCP", "Windows Remote Desktop"],
            ["5060 / 5061", "SIP", "UDP / TCP", "VoIP call setup (5061 = TLS)"]]},
        {"h": "Port ranges", "cols": ["Range", "Name"], "rows": [["0 - 1023", "well-known"], ["1024 - 49151", "registered"], ["49152 - 65535", "dynamic / private"]],
         "note": "A socket is an IP address plus a port, such as 10.43.3.87:23."},
    ]},
    "addressing": {"title": "Addressing: MAC, IP, DNS, DHCP", "sections": [
        {"h": "The four address types", "cols": ["Layer", "Address", "Size / form"], "rows": [
            ["2", "MAC (physical)", "48 bits, six hex pairs; first 24 bits OUI (IEEE), last 24 device ID"],
            ["3", "IP", "IPv4 32 bits (4 octets) / IPv6 128 bits (8 blocks)"], ["4", "Port", "16 bits (0-65535)"], ["7", "FQDN / host name", "www.example.com"]]},
        {"h": "IPv4 classes", "cols": ["Class", "First octet", "Default mask", "Hosts", "Notes"], "rows": [
            ["A", "1-126", "/8", "~16 million", "127.x is loopback"], ["B", "128-191", "/16", "~65,000", ""], ["C", "192-223", "/24", "254", ""],
            ["D", "224-239", "-", "-", "multicast"], ["E", "240-254", "-", "-", "research / experimental"]]},
        {"h": "Private and special IPv4 addresses", "cols": ["Address", "Meaning"], "rows": [
            ["10.0.0.0/8", "private (RFC 1918)"], ["172.16.0.0 - 172.31.255.255", "private (RFC 1918)"], ["192.168.0.0/16", "private (RFC 1918)"],
            ["127.0.0.1 (127.x)", "loopback: your own computer"], ["169.254.x.x", "APIPA: DHCP failed, the PC gave itself an address"],
            ["255.255.255.255", "broadcast to the local network"], ["0.0.0.0", "unassigned / any"]]},
        {"h": "The Big 4 settings", "lines": ["IP address, subnet mask, default gateway, DNS server.   Static vs DHCP.   ipconfig /all shows them."]},
        {"h": "NAT and PAT", "cols": ["Term", "Meaning"], "rows": [
            ["NAT", "swaps private IPs for a public one; conserves IPv4 and hides the inside"],
            ["PAT", "tracks sessions by port so MANY hosts share ONE public IP"],
            ["Static NAT (SNAT)", "professor's definition: a public IP permanently mapped to an inside host for INBOUND connections (a web server)"],
            ["Dynamic NAT (DNAT)", "the gateway picks from a pool of public addresses"]]},
        {"h": "IPv6", "cols": ["Topic", "Fact"], "rows": [
            ["Format", "128 bits, eight 16-bit hex blocks, no broadcast"],
            ["Shortening", "drop leading zeros in each block; replace ONE run of all-zero blocks with ::"],
            ["Prefix / interface ID", "first 64 bits network prefix, last 64 bits interface ID; one subnet = 2^64 addresses; no classes"],
            ["Types", "unicast (global 2000::/3, link-local FE80::/64), multicast (FF00::/8), anycast (nearest)"],
            ["Loopback", "::1"], ["Neighbors", "nodes on the same link; NDP (ICMPv6) replaces ARP; SLAAC self-configures"],
            ["Transition", "dual stack = IPv4 and IPv6 at once; tunneling = IPv6 inside IPv4"]]},
        {"h": "DNS", "cols": ["Item", "Fact"], "rows": [
            ["Parts", "namespace, name servers, resolvers"], ["Hierarchy", "13 root clusters -> TLD (.com, .edu) -> authoritative servers; ICANN"],
            ["Servers", "primary (read/write), secondary (read-only, zone transfer), caching, forwarding"],
            ["Queries", "recursive = demands a final answer (PC to local server); iterative = server asks root, TLD, authoritative"],
            ["Records", "A IPv4, AAAA IPv6, CNAME alias, PTR reverse (.arpa), NS name server, MX mail"], ["Software", "BIND (open source), Microsoft DNS"]]},
        {"h": "DHCP", "cols": ["Item", "Fact"], "rows": [
            ["DORA", "Discover (broadcast), Offer, Request, Acknowledge; UDP 67/68"], ["Scope / pool", "the range of addresses it can lease"],
            ["Lease time", "how long an address is loaned; shorter recycles addresses faster"], ["Reservation", "one MAC always gets the same IP"],
            ["Relay agent", "router 'IP helper' forwards DHCP broadcasts to a server on another subnet"]]},
        {"h": "Address and TCP/IP tools", "cols": ["Tool", "Use"], "rows": [
            ["ipconfig /all", "full config incl. MAC (Physical Address), DHCP, DNS"], ["ipconfig /release  /renew", "end the lease / get a new one"],
            ["ipconfig /flushdns", "clear the DNS cache"], ["ifconfig / ip", "Linux equivalents"], ["ping (ping -6 / ping6)", "ICMP echo"],
            ["nslookup / dig", "DNS lookups incl. reverse"], ["arp -a", "ARP table"]]},
    ]},
    "subnet": {"title": "Subnetting tables & method", "sections": [
        {"h": "Table 1: powers of 2", "cols": ["Power", "Value"], "rows": table1_rows(), "note": "Build this first on your scratch paper."},
        {"h": "Table 2: high-order bits in a mask octet", "cols": ["Ones", "Binary", "Value", "Magic number"], "rows": table2_rows(),
         "note": "Magic number = 256 - mask octet. Mask octets only ever use these values."},
        {"h": "CIDR problem: host + prefix -> network ID, mask, broadcast", "lines": [
            "1) Find the octet where the mask stops being 255.   2) Magic number = 256 - that mask octet.",
            "3) Count up by the magic number to the block that holds the address: that is the network ID.",
            "4) Broadcast = the next block minus 1. Octets after the interesting one: 0 for the network, 255 for the broadcast.",
            "Usable hosts = 2^h - 2, where h = 32 - prefix (the professor's convention)."]},
        {"h": "CLSM problem: N equal subnets with at least H hosts", "lines": [
            "1) Smallest h with 2^h - 2 >= H (Table 1).   2) New prefix = 32 - h.   3) List the N blocks by counting up by the block size.",
            "Assume CIDR is enabled: the all-zeros and all-ones subnets are usable. VLSM is NOT tested."]},
        {"h": "Prefix chart", "cols": ["Prefix", "Mask", "Host bits", "Magic number", "Usable hosts"], "rows": mask_rows(8, 30)},
        {"h": "Binary place values", "lines": ["One octet: 128  64  32  16  8  4  2  1.   11000000 = 192.   Hex: 0-9, A=10 ... F=15; one hex digit = 4 bits; FF = 255."]},
    ]},
    "protocols": {"title": "Protocols, encryption & tools", "sections": [
        {"h": "TCP vs UDP", "cols": ["", "TCP", "UDP"], "rows": [
            ["Connection", "connection-oriented (3-way handshake SYN, SYN/ACK, ACK)", "connectionless, no handshake"],
            ["Reliability", "sequencing, checksums, retransmission", "unreliable, no sequencing"], ["Flow control", "yes", "no"],
            ["Header", "larger", "4 fields"], ["Used for", "web, email, file transfer", "live audio/video, DNS, DHCP, TFTP"]]},
        {"h": "Network-layer helpers", "cols": ["Protocol", "Job"], "rows": [
            ["IP", "Layer 3, connectionless, unreliable; IPv4 2^32 addresses, IPv6 2^128"], ["ICMP", "reports problems, doesn't fix them; ping and tracert"],
            ["ARP", "IP -> MAC on the local network by broadcast; never crosses a router; ARP table"], ["NDP / ICMPv6", "does ARP's job for IPv6"],
            ["RIP / OSPF", "routing protocols"]]},
        {"h": "Ethernet", "lines": ["Ethernet II frame: header + payload + trailer.  Standard MTU 1,500 bytes; jumbo frames up to about 9,000-9,198; a VLAN tag adds 4 bytes.",
                                    "Wired Ethernet uses CSMA/CD (collision detection)."]},
        {"h": "Encryption", "cols": ["Topic", "Fact"], "rows": [
            ["CIA triad", "Confidentiality, Integrity, Availability"], ["Symmetric", "ONE shared key: fast, bulk data; hard part is sharing the key"],
            ["Asymmetric", "key PAIR (public + private): key exchange and identity; slower"], ["PKI / CA / certificate", "a CA issues certificates (identity + public key)"],
            ["IPsec", "Network layer VPN suite (AH, ESP): initiation, key management, negotiation, data transfer, termination"],
            ["SSL/TLS", "Transport layer; encrypts web traffic (HTTPS, port 443)"]]},
        {"h": "Remote access", "cols": ["Tool", "Notes"], "rows": [
            ["Telnet", "port 23, cleartext CLI"], ["SSH", "port 22, encrypted CLI (and SFTP)"], ["RDP", "port 3389, Microsoft GUI remote desktop"],
            ["VNC", "open-source GUI remote control"], ["FTP / FTPS / SFTP / TFTP", "cleartext / over SSL-TLS / over SSH / UDP 69, no security"]]},
        {"h": "VPN types", "cols": ["Type", "Notes"], "rows": [
            ["Site-to-site", "hardware (often firewalls) at each office; users run nothing"],
            ["Client-to-site", "software on a remote laptop (host-to-site, remote access, mobile user)"], ["Host-to-host", "tunnel between two computers"],
            ["Full vs split tunnel", "all traffic through the VPN vs only office traffic"], ["VPN concentrator", "authenticates clients and builds tunnels"]]},
        {"h": "Command-line tools", "cols": ["Tool", "Notes"], "rows": [
            ["netstat", "-a all, -n numeric, -e interface errors, -r routes, -o PID, -b process, -s per-protocol"],
            ["tracert / traceroute", "Windows ICMP / Linux UDP; * * * = no 'TTL exceeded' reply"], ["pathping (mtr)", "pings every hop and reports"],
            ["tcpdump", "Linux packet sniffer"], ["route", "show/edit the routing table"], ["nmap / Zenmap", "discover devices and ports"]]},
    ]},
    "wifi": {"title": "Wireless", "sections": [
        {"h": "802.11 standards", "cols": ["Standard", "Name", "Band", "Max speed"], "rows": [
            ["b", "", "2.4 GHz", "11 Mbps"], ["a", "", "5 GHz", "54 Mbps"], ["g", "", "2.4 GHz", "54 Mbps"], ["n", "Wi-Fi 4", "2.4 / 5 GHz", "600 Mbps"],
            ["ac", "Wi-Fi 5", "5 GHz", "1.3 / 3.47 / 6.93 Gbps"], ["ax", "Wi-Fi 6 / 6E", "2.4 / 5 / 6 GHz", "9.6 Gbps"], ["be", "Wi-Fi 7", "", "~46 Gbps"]]},
        {"h": "Bands, channels, throughput", "cols": ["Topic", "Fact"], "rows": [
            ["2.4 GHz", "longer range, slower; non-overlapping channels 1, 6, 11 (U.S.)"], ["5 GHz", "more throughput, shorter range"], ["6 GHz", "Wi-Fi 6E only"],
            ["MIMO", "multiple antennas"], ["MU-MIMO", "serves several clients at once (802.11ac Wave 2)"], ["Channel bonding", "2 x 20 MHz = 40 MHz"],
            ["Frame aggregation", "combines frames to cut overhead"], ["Band steering", "nudges clients to 5 GHz"]]},
        {"h": "Collisions and association", "cols": ["Topic", "Fact"], "rows": [
            ["CSMA/CA", "Wi-Fi avoids collisions with ACKs (CSMA/CD = wired, detection)"], ["RTS/CTS", "optional; fewer collisions, lower efficiency"],
            ["Scanning", "active = probe request; passive = listen for beacons"], ["SSID / BSS / ESS", "name / stations on one AP / several APs sharing an ESSID (roaming)"],
            ["Modes", "ad hoc (direct), infrastructure (AP), mesh (APs as peers)"], ["Frames", "802.11 has 4 address fields; Ethernet has 2"]]},
        {"h": "Other radios", "cols": ["Technology", "Notes"], "rows": [
            ["ZigBee", "low-power IoT: building automation, HVAC, meter reading"], ["Z-Wave", "smart home, uses a hub / controller"],
            ["Bluetooth", "2.4 GHz, frequency hopping; bluejacking SENDS, bluesnarfing STEALS"], ["NFC", "very short range RFID, powered by induction"],
            ["RFID", "active tags have a battery, passive tags are powered by the reader"], ["ANT+", "fitness sensors"], ["IR", "just below visible light, line of sight"]]},
        {"h": "Wi-Fi security", "cols": ["Item", "Fact"], "rows": [
            ["WEP", "broken; never use"], ["WPA", "TKIP, per-packet key"], ["WPA2", "CCMP / AES"], ["WPA3", "newest; protects the handshake"],
            ["Personal", "pre-shared key (one passphrase)"], ["Enterprise", "RADIUS + 802.1X, each user authenticates"], ["MAC filtering", "allow-list of MACs; not encryption"],
            ["Guest network / captive portal", "separate network / terms page first"]]},
        {"h": "Threats", "cols": ["Threat", "What it is"], "rows": [
            ["War driving / war chalking", "hunting for / marking open Wi-Fi (very old school)"], ["Evil twin", "rogue AP imitating a real one"],
            ["WPS attack", "cracking the AP's PIN"], ["WPA attack", "capturing the key exchange"]]},
        {"h": "Signal strength (RSSI)", "cols": ["dBm", "Quality"], "rows": [
            ["-30", "excellent"], ["-50", "good (VoIP / video)"], ["-70", "acceptable: minimum for reliable data"], ["-80", "basic connectivity"], ["-90", "unusable"]]},
        {"h": "Signal problems", "cols": ["Effect", "Meaning"], "rows": [
            ["Attenuation", "weakens with distance: more power or a repeater"], ["Reflection", "bounces off large smooth surfaces"],
            ["Refraction", "bends passing into another medium"], ["Scattering", "small objects, rain"], ["Diffraction", "bends around sharp edges"],
            ["Multipath", "several routes: may arrive, but delays cause errors"], ["Interference / SNR", "lower SNR = more noise vs signal"]]},
        {"h": "Tools", "lines": ["Wi-Fi analyzer (networks, channels, signal) vs spectrum analyzer (signals AND noise in a band). Site survey before installing APs.",
                                 "Wireless controller: centralized authentication, channel management, rogue AP detection."]},
    ]},
    "arch": {"title": "Architecture, VLANs, virtualization & cloud", "sections": [
        {"h": "Switches", "cols": ["Type", "Notes"], "rows": [
            ["Unmanaged", "plug-and-play, no IP, no VLANs"], ["Managed", "IP address, CLI/GUI: VLANs, mirroring, STP"], ["Layer 3 / Layer 4", "route / read TCP-UDP ports"],
            ["Features", "VLANs, PoE, L3, faster uplink ports than line ports"], ["STP", "prevents loops and broadcast storms; one root bridge"], ["LACP / NIC teaming", "link aggregation"]]},
        {"h": "Designs", "cols": ["Design", "Notes"], "rows": [
            ["3-tier", "access (edge) -> distribution (aggregation) -> core; north-south traffic"],
            ["Spine-and-leaf", "every leaf to every spine, spines NOT linked; ToR leaf switches; east-west traffic"],
            ["East-west / north-south", "inside the segment / leaving it"], ["SDN", "controller; infrastructure (data), control, application, management planes"],
            ["SAN", "separate network, BLOCK-level storage: Fibre Channel, FCoE, iSCSI (over TCP), InfiniBand"], ["NAS", "FILE-level storage on the LAN"]]},
        {"h": "VLANs", "cols": ["Topic", "Fact"], "rows": [
            ["What", "logical broadcast domains on a MANAGED switch (Layer 2); each VLAN gets its own subnet"], ["Between VLANs", "needs a router (router-on-a-stick) or L3 switch"],
            ["802.1Q", "4-byte tag on trunk (tagged) ports; access port = one VLAN"], ["Types", "default, native, data, management, voice"],
            ["Attack", "VLAN hopping (double tagging)"], ["Reasons", "isolate heavy traffic, priority (voice), security, legacy protocols, test networks, cost"]]},
        {"h": "Virtualization", "cols": ["Topic", "Fact"], "rows": [
            ["Host / guest / hypervisor", "physical computer / each VM / software that manages VMs"], ["Type 1", "bare-metal, installs before any OS (Hyper-V, ESXi)"],
            ["Type 2", "hosted, an app inside an OS (VirtualBox, VMware Workstation)"], ["vSwitch / vNIC", "virtual switch run by the hypervisor / VM's virtual adapter"],
            ["VM network modes", "bridged (IP from the LAN), NAT (hypervisor is DHCP/NAT), host-only"], ["Pros", "efficiency, cost and energy, isolation, easy backups"],
            ["Cons", "performance, complexity, licensing, single point of failure"], ["NFV", "license per virtual device, latency, no virtual firewall at the edge"]]},
        {"h": "Cloud: what the customer brings", "cols": ["Model", "Customer brings", "Example"], "rows": [
            ["IaaS", "OS + app + data", "virtual servers"], ["PaaS", "app + data", "a runtime platform"], ["SaaS", "data only", "Gmail, Office 365"]]},
        {"h": "Cloud: deployment and features", "cols": ["Topic", "Fact"], "rows": [
            ["Deployment", "public, private, community (shared by several organizations), hybrid; multicloud"],
            ["NIST features", "on-demand self-service, broad network access, resource pooling, rapid elasticity, measured service"],
            ["IaC / automation / orchestration", "config files / one event response / chained workflow"]]},
    ]},
    "avail": {"title": "Availability, power, backups & RAID", "sections": [
        {"h": "Availability", "cols": ["Term", "Fact"], "rows": [
            ["High availability", "works reliably nearly all the time"], ["Fault tolerance", "a fault doesn't become a failure"], ["MTBF", "mean time between failures: higher is better"],
            ["MTTR", "mean time to repair: lower is better"], ["Hot spare", "installed, takes over automatically"], ["Cold spare", "on the shelf"],
            ["Hot-swappable", "replace while running"], ["Clustering / VIP", "many servers appear as one; load balancer in front"]]},
        {"h": "Recovery", "cols": ["Term", "Fact"], "rows": [
            ["RPO", "how much data you can lose"], ["RTO", "how quickly you must be back"], ["DR plan vs BCP", "restore IT vs keep the business running"],
            ["Hot site", "ready, most expensive"], ["Warm site", "partly configured"], ["Cold site", "components only; can take weeks"],
            ["Incident response", "preparation, detection, containment, remediation, recovery, review"]]},
        {"h": "Power", "cols": ["Problem", "Meaning"], "rows": [
            ["Surge / spike", "momentary INCREASE"], ["Brownout / sag", "momentary DECREASE"], ["Blackout", "complete loss"], ["Noise", "fluctuation (EMI)"]],
         "note": "Standby UPS switches to battery on loss; online UPS always runs from the battery. Generators cover long outages. PDU distributes power in a rack."},
        {"h": "Backups", "cols": ["Type", "Copies", "Restore"], "rows": [
            ["Full", "everything", "fastest (one set)"], ["Incremental", "changes since the last backup of any kind", "full + EVERY incremental"],
            ["Differential", "changes since the last FULL", "full + latest differential"]],
         "note": "3-2-1-1: 3 copies, 2 media types, 1 offsite, 1 offline. Replication = live copy to another place; snapshot = freeze blocks to go back in time."},
        {"h": "RAID", "cols": ["Level", "How", "Notes"], "rows": [
            ["0", "striping", "NO redundancy"], ["1", "mirroring", "100% overhead"], ["5", "striping + parity", "3+ disks, survives 1 failure, write penalty"],
            ["6", "double parity", "survives 2 failures"], ["10", "mirrored pairs, striped", "4+ disks"]]},
    ]},
    "monitor": {"title": "Monitoring & management", "sections": [
        {"h": "Tools", "cols": ["Tool / idea", "What it does"], "rows": [
            ["Network monitor", "traffic types, flows and volume"], ["Protocol analyzer (Wireshark, tcpdump)", "frame-by-frame capture"],
            ["Port mirroring (SPAN)", "switch copies traffic to a monitoring port"], ["TAP", "in-line device that copies traffic"], ["NetFlow", "flow data"],
            ["iPerf", "throughput test"], ["Baseline", "record of normal: utilization, errors, drops, response time"]]},
        {"h": "SNMP and logs", "cols": ["Item", "Fact"], "rows": [
            ["SNMP", "NMS polls agents (UDP 161); agents send traps (UDP 162); MIB = data dictionary; v1 rare, v2 common, v3 most secure"],
            ["Syslog", "UDP 514; generator sends, collector gathers"], ["Event Viewer", "the Windows event log: look here first"], ["Audit log", "who did what and when"]]},
        {"h": "Errors and traffic control", "cols": ["Item", "Fact"], "rows": [
            ["Runt / giant / jabber", "too small / too big / continuous garbage"], ["Discards, resets", "interface errors to watch"],
            ["QoS", "prioritize VoIP/video"], ["Flow control", "don't overwhelm the receiver"], ["Congestion control", "open-loop prevents, closed-loop remedies"],
            ["Traffic shaping", "limit a device's bandwidth"]]},
    ]},
    "docs": {"title": "Cabling, documentation & contracts", "sections": [
        {"h": "Structured cabling (TIA/EIA-568: hierarchical star)", "cols": ["Term", "Meaning"], "rows": [
            ["Entrance facility (EF)", "service provider cabling enters"], ["Demarc", "where the ISP ends and you begin"], ["MDF", "main distribution frame: LAN/WAN interconnect"],
            ["IDF", "intermediate distribution frame: floor closets"], ["Backbone cabling", "EF - MDF - IDFs"], ["Horizontal cabling", "workstation to nearest data room, 100 m max"],
            ["Work area", "where users sit"], ["Patch panel / patch cable", "termination point / short cable"]]},
        {"h": "Racks and cable", "cols": ["Topic", "Fact"], "rows": [
            ["Rack height", "1U = 1.75 in; full rack 42U (about 6 ft); half racks 18-22U"], ["Rack width", "19 in (23 in also exists)"],
            ["Racks", "open 2-post vs enclosed 4-post"], ["UTP", "RJ-45, 100 m, mind the bend radius and EMI"], ["Single-mode fiber", "8-10 micron core, laser, longest distance"],
            ["Multimode fiber", "50 / 62.5 micron, shorter, cheaper"]]},
        {"h": "Documents and agreements", "cols": ["Term", "Meaning", "Binding?"], "rows": [
            ["RFP", "request for proposal", "no"], ["MOU", "memorandum of understanding", "usually NOT"], ["MSA", "master service agreement: terms of future contracts", "yes"],
            ["SOW", "statement of work: tasks, deliverables, timeline (addendum to an MSA)", "yes"], ["SLA", "service level agreement: measurable service", "yes"]]},
        {"h": "Documentation and change management", "cols": ["Item", "Fact"], "rows": [
            ["Documentation", "network diagram, wiring schematic, rack diagram, floor plan; outdated the minute you save it"],
            ["Software changes", "patch (fix), upgrade (major), rollback (revert), installation; always have a backout plan"],
            ["Schedule changes", "in a maintenance window"], ["System life cycle", "design, implement, maintain, dispose"]]},
        {"h": "Safety", "lines": ["ESD: catastrophic (destroyed now) vs upset (shortened life); about 10 V can damage parts, you can't feel less than 1,500 V.",
                                 "Fail-open (fail-safe): doors unlock.  Fail-close (fail-secure): protects resources.  SDS and OSHA are the safety references."]},
    ]},
    "calc": {"title": "Calculators", "sections": []},
}
CHEAT_TITLES = {k: v["title"] for k, v in CHEAT.items()}



# ===========================================================================
# GUI (tkinter ships with Python)
# ===========================================================================
try:
    import tkinter as tk
    from tkinter import filedialog, font as tkfont, messagebox, ttk
    HAVE_TK = True
except Exception:  # ImportError, or a broken Tcl install
    HAVE_TK = False

if HAVE_TK:
    # palette
    # Every value inside one palette must be unique: switching themes remaps old colors to new ones.
    LIGHT = dict(
        BG="#f4f5f7", CARD="#ffffff", LINE="#d0d5dd", TEXT="#101828", MUTED="#667085", HEAD="#1e3a8a",
        ACCENT="#2563eb", ACCENT_DK="#1d4ed8", GOOD="#15803d", GOOD_BG="#dcfce7", BAD="#b91c1c",
        BAD_BG="#fee2e2", SEL_BG="#dbeafe", CUR_BG="#fff3b0", CHG_BG="#e6f4ea",
        NET="#2563eb", HOST="#c2410c", FLAG="#f59e0b",
        B1="#2f6fed", B2="#0d9488", B3="#ea7a12", B4="#7c3aed", B5="#16a34a", B6="#db2777",
    )
    DARK = dict(
        BG="#0d1117", CARD="#161b22", LINE="#30363d", TEXT="#e6edf3", MUTED="#8b949e", HEAD="#79b8ff",
        ACCENT="#388bfd", ACCENT_DK="#1f6feb", GOOD="#3fb950", GOOD_BG="#14301f", BAD="#f85149",
        BAD_BG="#3d1418", SEL_BG="#1c3358", CUR_BG="#4a4210", CHG_BG="#173824",
        NET="#58a6ff", HOST="#ffa657", FLAG="#d29922",
        B1="#2d6cdf", B2="#14a39a", B3="#d9730d", B4="#8957e5", B5="#2ea043", B6="#d12f7d",
    )
    PALETTES = {"light": LIGHT, "dark": DARK}
    CURRENT = {"name": "light"}
    THEME_LISTENERS = []      # called after every theme switch (canvases redraw themselves)
    TREE_TAGS = ("chg", "match", "pick", "dim", "final")


    def apply_palette(name):
        CURRENT["name"] = name
        globals().update(PALETTES[name])  # BG, CARD, TEXT, ... become module-level names


    def system_theme():
        """'dark' if Windows is set to dark app mode, else 'light'."""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as k:
                return "light" if winreg.QueryValueEx(k, "AppsUseLightTheme")[0] else "dark"
        except Exception:
            return "light"


    apply_palette("light")
    F = {}  # shared fonts (resizing them resizes the whole app)
    APP = {"root": None, "listeners": []}


    def make_fonts(root):
        fam, mono = "Segoe UI", "Consolas"
        F["ui"] = tkfont.Font(root=root, family=fam, size=11)
        F["bold"] = tkfont.Font(root=root, family=fam, size=11, weight="bold")
        F["h1"] = tkfont.Font(root=root, family=fam, size=20, weight="bold")
        F["h2"] = tkfont.Font(root=root, family=fam, size=13, weight="bold")
        F["code"] = tkfont.Font(root=root, family=mono, size=12)
        F["codeb"] = tkfont.Font(root=root, family=mono, size=12, weight="bold")
        F["small"] = tkfont.Font(root=root, family=fam, size=10)


    def shade(color, factor):
        h = color.lstrip("#")
        rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
        return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * factor))) for c in rgb)


    def row_height():
        return F["ui"].metrics("linespace") + 10


    def scale_trees(widget, ratio):
        """Keep table columns proportional when the text size changes."""
        if isinstance(widget, ttk.Treeview):
            for col in widget["columns"]:
                c = widget.column(col)
                widget.column(col, width=int(c["width"] * ratio), minwidth=int(c["minwidth"] * ratio))
        for child in widget.winfo_children():
            scale_trees(child, ratio)


    def resize_fonts(delta):
        old = abs(F["ui"].cget("size"))
        for f in F.values():
            f.configure(size=max(8, min(26, abs(f.cget("size")) + delta)))
        new = abs(F["ui"].cget("size"))
        root = APP["root"]
        if root is not None and new != old:
            ttk.Style(root).configure("Treeview", rowheight=row_height())  # taller rows for bigger text
            scale_trees(root, new / old)
        for fn in list(APP["listeners"]):
            try:
                fn()
            except tk.TclError:
                pass


    def make_tile(parent, title, subtitle, color_key, command):
        """A big colored button whose text WRAPS instead of being cut off at large text sizes."""
        col = globals()[color_key]
        tile = tk.Frame(parent, bg=col, cursor="hand2", padx=16, pady=12)
        top = tk.Label(tile, text=title, font=F["h2"], bg=col, fg="#fefefe", anchor="w", justify="left")
        sub = tk.Label(tile, text=subtitle, font=F["bold"], bg=col, fg="#fefefe", anchor="w", justify="left")
        top.pack(fill="x")
        sub.pack(fill="x")
        parts = (tile, top, sub)

        def paint(factor):
            c = globals()[color_key]
            c = c if factor == 1 else shade(c, factor)
            for w in parts:
                w.configure(bg=c)
        hover = lambda: 0.88 if CURRENT["name"] == "light" else 1.2  # noqa: E731
        for w in parts:
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", lambda e: paint(hover()))
            w.bind("<Leave>", lambda e: paint(1))
        tile.bind("<Configure>", lambda e: (top.configure(wraplength=max(120, e.width - 40)),
                                            sub.configure(wraplength=max(120, e.width - 40))))
        return tile


    def make_chip(parent, item):
        """Small colored tag: purple = the professor's material, teal = generated, grey = practice question written by Claude."""
        o = origin_of(item)
        bg = {"prof": B4, "gen": B2, "claude": LINE}[o]
        return tk.Label(parent, text=origin_chip(item), font=F["bold"], bg=bg, fg="#fefefe" if o != "claude" else TEXT,
                        padx=8, pady=2)


    def style_app(root):
        st = ttk.Style(root)
        st.theme_use("clam")
        root.configure(bg=BG)
        root.option_add("*TCombobox*Listbox.background", CARD)
        root.option_add("*TCombobox*Listbox.foreground", TEXT)
        root.option_add("*TCombobox*Listbox.font", F["ui"])
        st.configure(".", background=BG, foreground=TEXT, font=F["ui"], bordercolor=LINE,
                     lightcolor=BG, darkcolor=BG, troughcolor=LINE, focuscolor=BG)
        st.configure("TFrame", background=BG)
        st.configure("Card.TFrame", background=CARD)
        st.configure("TLabel", background=BG, foreground=TEXT, font=F["ui"])
        st.configure("TButton", background=CARD, foreground=TEXT, font=F["ui"], padding=(12, 6),
                     bordercolor=LINE, lightcolor=CARD, darkcolor=CARD)
        st.map("TButton", background=[("active", SEL_BG), ("disabled", BG)], foreground=[("disabled", MUTED)])
        st.configure("Accent.TButton", background=ACCENT, foreground="#ffffff", font=F["bold"],
                     padding=(14, 8), bordercolor=ACCENT_DK, lightcolor=ACCENT, darkcolor=ACCENT)
        st.map("Accent.TButton", background=[("active", ACCENT_DK), ("disabled", MUTED)],
               foreground=[("disabled", "#ffffff")])
        st.configure("Treeview", font=F["ui"], rowheight=row_height(), background=CARD, fieldbackground=CARD,
                     foreground=TEXT, bordercolor=LINE)
        st.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])
        st.configure("Treeview.Heading", font=F["bold"], background=LINE, foreground=TEXT, relief="flat")
        st.map("Treeview.Heading", background=[("active", SEL_BG)])
        st.configure("TLabelframe", background=BG, bordercolor=LINE)
        st.configure("TLabelframe.Label", background=BG, font=F["bold"], foreground=MUTED)
        for name in ("TEntry", "TSpinbox", "TCombobox"):
            st.configure(name, fieldbackground=CARD, foreground=TEXT, insertcolor=TEXT, bordercolor=LINE,
                         arrowcolor=TEXT, background=CARD)
        st.map("TCombobox", fieldbackground=[("readonly", CARD)], foreground=[("readonly", TEXT)])
        st.configure("TCheckbutton", background=BG, foreground=TEXT, indicatorbackground=CARD, indicatorforeground=TEXT,
                     bordercolor=MUTED, indicatormargin=(0, 0, 8, 0), indicatorsize=18)
        st.map("TCheckbutton", background=[("active", BG)],
               indicatorbackground=[("selected", ACCENT), ("!selected", CARD)])
        st.configure("TRadiobutton", background=BG, foreground=TEXT, indicatorbackground=CARD, indicatorforeground=TEXT,
                     bordercolor=MUTED, indicatormargin=(0, 0, 8, 0), indicatorsize=18)
        st.map("TRadiobutton", background=[("active", BG)], indicatorbackground=[("selected", ACCENT), ("!selected", CARD)])
        st.configure("TScrollbar", background=LINE, troughcolor=BG, bordercolor=BG, arrowcolor=TEXT)
        st.map("TScrollbar", background=[("active", MUTED)])
        st.configure("TSeparator", background=LINE)
        st.configure("TNotebook", background=BG, bordercolor=LINE)
        st.configure("TNotebook.Tab", background=BG, foreground=MUTED, padding=(14, 6), font=F["bold"])
        st.map("TNotebook.Tab", background=[("selected", CARD)], foreground=[("selected", TEXT)])


    # --- switching theme ---------------------------------------------------------------------------
    COLOR_OPTIONS = ("bg", "fg", "background", "foreground", "highlightbackground", "highlightcolor",
                     "insertbackground", "selectbackground", "selectforeground", "activebackground",
                     "activeforeground", "troughcolor", "disabledforeground")


    def recolor(widget, mapping):
        try:
            keys = widget.keys()
        except Exception:
            keys = []
        for opt in COLOR_OPTIONS:
            if opt in keys:
                try:
                    cur = str(widget.cget(opt)).lower()
                    if cur in mapping:
                        widget.configure(**{opt: mapping[cur]})
                except tk.TclError:
                    pass
        if isinstance(widget, tk.Text):
            for tag in widget.tag_names():
                for opt in ("background", "foreground"):
                    try:
                        cur = str(widget.tag_cget(tag, opt)).lower()
                        if cur in mapping:
                            widget.tag_configure(tag, **{opt: mapping[cur]})
                    except tk.TclError:
                        pass
        if isinstance(widget, ttk.Treeview):
            for tag in TREE_TAGS:
                for opt in ("background", "foreground"):
                    try:
                        cur = str(widget.tag_configure(tag, opt)).lower()
                        if cur in mapping:
                            widget.tag_configure(tag, **{opt: mapping[cur]})
                    except tk.TclError:
                        pass
        if getattr(widget, "_theme_btn", False):
            widget.configure(text=theme_button_text())
        for child in widget.winfo_children():
            recolor(child, mapping)


    def theme_button_text():
        return "Light mode" if CURRENT["name"] == "dark" else "Dark mode"


    def set_theme(root, name):
        old, new = PALETTES[CURRENT["name"]], PALETTES[name]
        mapping = {old[k].lower(): new[k] for k in old}
        apply_palette(name)
        style_app(root)
        recolor(root, mapping)
        for fn in list(THEME_LISTENERS):
            try:
                fn()
            except tk.TclError:
                pass


    # --- small widget helpers ----------------------------------------------------------------------
    def ro_text(parent, height, font=None, bg=None, **kw):
        """Read-only Text widget with a scrollbar."""
        box = ttk.Frame(parent)
        kw.setdefault("wrap", "word")
        txt = tk.Text(box, height=height, font=font or F["ui"], bg=bg or CARD, fg=TEXT, insertbackground=TEXT,
                      relief="solid", bd=1, highlightthickness=0, padx=8, pady=6, **kw)
        sb = ttk.Scrollbar(box, command=txt.yview)
        txt.configure(yscrollcommand=sb.set, state="disabled")
        sb.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        return box, txt


    def set_text(txt, content, tag=None):
        txt.configure(state="normal")
        txt.delete("1.0", "end")
        txt.insert("end", content, tag or ())
        txt.configure(state="disabled")


    def make_grid(parent, height=8, hscroll=True):
        """A table: Treeview with scrollbars. -> (frame, tree)."""
        box = ttk.Frame(parent)
        tree = ttk.Treeview(box, show="headings", height=height)
        vs = ttk.Scrollbar(box, command=tree.yview)
        tree.configure(yscrollcommand=vs.set)
        if hscroll:
            hs = ttk.Scrollbar(box, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=hs.set)
            hs.pack(side="bottom", fill="x")
        vs.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        paint_tree_tags(tree)
        return box, tree


    def paint_tree_tags(tree):
        tree.tag_configure("chg", background=CHG_BG)
        tree.tag_configure("match", background=CUR_BG)
        tree.tag_configure("pick", background=GOOD_BG)
        tree.tag_configure("dim", foreground=MUTED)
        tree.tag_configure("final", background=GOOD_BG)


    def fill_plain_grid(tree, cols, rows, max_chars=60, stretch_last=True):
        tree.delete(*tree.get_children())
        ids = [f"c{i}" for i in range(len(cols))]
        tree.configure(columns=ids)
        cw = F["bold"].measure("0")
        for i, name in enumerate(cols):
            width = max([len(str(name)) + 2] + [min(max_chars, len(str(r[i]))) for r in rows[:60]])
            tree.heading(ids[i], text=name, anchor="w")
            tree.column(ids[i], width=max(cw * 5, cw * width + 16), minwidth=cw * 4, anchor="w",
                        stretch=(stretch_last and i == len(cols) - 1))
        for r in rows:
            tree.insert("", "end", values=list(r))


    class ScrollFrame(ttk.Frame):
        """A vertically scrollable area. Put content in .body"""

        def __init__(self, parent):
            super().__init__(parent)
            self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
            self.sb = ttk.Scrollbar(self, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.sb.set)
            self.sb.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)
            self.body = ttk.Frame(self.canvas, padding=(24, 12))
            self.win = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
            self.body.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width))

        def scroll(self, units):
            if self.body.winfo_reqheight() > self.canvas.winfo_height():
                self.canvas.yview_scroll(units, "units")


    def wrap_label(parent, text, font=None, fg=None, bg=None, **kw):
        """A label that wraps to the width of its parent (re-wrapped whenever the parent is resized)."""
        lbl = tk.Label(parent, text=text, font=font or F["ui"], fg=fg or TEXT, bg=bg or BG, justify="left", anchor="w", **kw)
        parent.bind("<Configure>", lambda e: lbl.configure(wraplength=max(200, e.width - 24)), add="+")
        return lbl



    # ===========================================================================
    # STEP PANEL + DIAGRAM WIDGETS (shared by the labs and the quiz screens)
    # ===========================================================================
    class StepPanel(ttk.Frame):
        """Shows a worked solution one step at a time. accumulate=True keeps earlier steps visible (hand-solve style);
        accumulate=False shows only the current step (walk-throughs)."""

        def __init__(self, parent, on_change=None, accumulate=True, height=12):
            super().__init__(parent)
            self.steps, self.shown, self.on_change, self.accumulate = [], 0, on_change, accumulate
            bar = ttk.Frame(self)
            bar.pack(fill="x", pady=(0, 4))
            self.btn_prev = ttk.Button(bar, text="< Back", command=self.back)
            self.btn_next = ttk.Button(bar, text="Next step  >", style="Accent.TButton", command=self.forward)
            self.btn_all = ttk.Button(bar, text="Show all", command=self.show_all)
            self.btn_reset = ttk.Button(bar, text="Start over", command=self.reset)
            for b in (self.btn_prev, self.btn_next, self.btn_all, self.btn_reset):
                b.pack(side="left", padx=(0, 6))
            self.lbl = tk.Label(bar, text="", bg=BG, fg=MUTED, font=F["bold"])
            self.lbl.pack(side="left", padx=8)
            box, self.txt = ro_text(self, height, font=F["ui"])
            box.pack(fill="both", expand=True)
            self._tags()
            APP["listeners"].append(self._tags)

        def _tags(self):
            try:
                self.txt.tag_configure("title", font=F["bold"], foreground=HEAD, spacing1=6)
                self.txt.tag_configure("now", background=CUR_BG)
                self.txt.tag_configure("ans", font=F["codeb"], foreground=GOOD)
                self.txt.tag_configure("mono", font=F["code"])
                self.txt.tag_configure("hint", foreground=MUTED, font=F["ui"])
            except tk.TclError:
                pass

        def set_steps(self, steps, shown=0):
            self.steps, self.shown = list(steps), shown
            self._render()

        def forward(self):
            if self.shown < len(self.steps):
                self.shown += 1
                self._render()

        def back(self):
            if self.shown > 0:
                self.shown -= 1
                self._render()

        def show_all(self):
            self.shown = len(self.steps)
            self._render()

        def reset(self):
            self.shown = 0
            self._render()

        def _render(self):
            t = self.txt
            t.configure(state="normal")
            t.delete("1.0", "end")
            if not self.steps:
                t.insert("end", "Nothing to show yet.", "hint")
            elif self.shown == 0:
                t.insert("end", "Try it yourself first on scratch paper.\nPress 'Next step' to reveal the first step, or 'Show all'.", "hint")
            else:
                lo = 0 if self.accumulate else self.shown - 1
                for i in range(lo, self.shown):
                    st = self.steps[i]
                    cur = i == self.shown - 1 and self.accumulate
                    t.insert("end", st["title"] + "\n", ("title", "now") if cur else ("title",))
                    for ln in st["lines"]:
                        mono = any(ln.lstrip().startswith(p) for p in ("IP ", "Mask", "AND", "#", "...", "Row ", "  2^", "Network ID", "Broadcast", "Mask:"))
                        tags = ("ans",) if st.get("answer") and ln.strip() else (("mono",) if mono else ())
                        t.insert("end", ln + "\n", tags)
                t.see("end")
            t.configure(state="disabled")
            n = len(self.steps)
            self.lbl.configure(text=(f"step {self.shown} of {n}" if n else ""))
            self.btn_prev.configure(state="normal" if self.shown > 0 else "disabled")
            self.btn_next.configure(state="normal" if self.shown < n else "disabled")
            self.btn_all.configure(state="normal" if self.shown < n else "disabled")
            if self.on_change:
                self.on_change(self.shown)


    class BitBar(tk.Canvas):
        """32 bits in four octets, drawn as boxes: network bits (blue) and host bits (orange). Rows: IP, mask, network."""
        ROW_LABELS = ("IP address", "Subnet mask", "AND = network ID")

        def __init__(self, parent):
            super().__init__(parent, bg=BG, highlightthickness=0, height=140)
            self.rows, self.prefix, self.octet = [], 0, None
            self.bind("<Configure>", lambda e: self.redraw())
            THEME_LISTENERS.append(self.redraw)
            APP["listeners"].append(self.redraw)

        def set_rows(self, rows, prefix, octet=None):
            self.rows, self.prefix, self.octet = rows, prefix, octet
            self.redraw()

        def redraw(self):
            try:
                self.delete("all")
                w = max(self.winfo_width(), 300)
                lh = F["code"].metrics("linespace")
                cell = max(14, F["code"].measure("0") + 6)
                labels = self.ROW_LABELS
                lab_w = F["bold"].measure("AND = network ID") + 14
                if lab_w + 32 * cell + 40 > w:                 # tight: shorter labels and smaller boxes
                    labels = ("IP", "Mask", "AND")
                    lab_w = F["bold"].measure("Mask") + 20
                    cell = max(9, int((w - lab_w - 40) / 32))
                bitfont = F["codeb"] if cell >= F["codeb"].measure("0") + 4 else F["small"]
                row_h = lh + 10
                self.configure(height=len(self.rows) * row_h + lh + 14 if self.rows else 10)
                if not self.rows:
                    return
                for r, (label, bits) in enumerate(zip(labels, self.rows)):
                    y = 8 + r * row_h
                    self.create_text(4, y + row_h // 2 - 3, text=label, anchor="w", fill=MUTED, font=F["bold"])
                    flat = bits.replace(".", "")
                    x = lab_w
                    for i, ch in enumerate(flat):
                        if i and i % 8 == 0:
                            x += 10
                        net = i < self.prefix
                        self.create_rectangle(x, y, x + cell, y + row_h - 4, outline=LINE, fill=CARD)
                        self.create_text(x + cell // 2, y + (row_h - 4) // 2, text=ch, font=bitfont, fill=NET if net else HOST)
                        x += cell
                    if self.octet is not None and 0 <= self.octet < 4:
                        ox = lab_w + self.octet * (8 * cell + 10)
                        self.create_rectangle(ox - 2, y - 2, ox + 8 * cell + 2, y + row_h - 2, outline=FLAG, width=2)
                y = 8 + len(self.rows) * row_h
                self.create_text(4, y, text="blue = network bits (the mask's 1s)", anchor="nw", fill=NET, font=F["small"])
                self.create_text(4 + F["small"].measure("blue = network bits (the mask's 1s)") + 24, y,
                                 text="orange = host bits (the mask's 0s)", anchor="nw", fill=HOST, font=F["small"])
            except tk.TclError:
                pass


    class SeqDiagram(tk.Canvas):
        """Sequence diagram: actors across the top, one arrow (or note) per step. Draws steps[:count]; the last one is highlighted."""

        def __init__(self, parent):
            super().__init__(parent, bg=BG, highlightthickness=0, height=300)
            self.actors, self.steps, self.count = [], [], 0
            self.bind("<MouseWheel>", lambda e: self.yview_scroll(int(-e.delta / 120), "units"))
            self.bind("<Configure>", lambda e: self.redraw())
            THEME_LISTENERS.append(self.redraw)
            APP["listeners"].append(self.redraw)

        def load(self, actors, steps, count=0):
            self.actors, self.steps, self.count = actors, steps, count
            self.redraw()

        def show(self, count):
            self.count = count
            self.redraw()

        def redraw(self):
            try:
                self.delete("all")
                w = max(self.winfo_width(), 400)
                n = len(self.actors)
                if not n:
                    return
                fh = F["ui"].metrics("linespace")
                col_w = w / n
                xs = [col_w * (i + 0.5) for i in range(n)]
                top = 8
                head_h = fh * 2 + 10
                step_h = fh * 2 + 18
                total = top + head_h + step_h * (len(self.steps) + 1)
                for x in xs:
                    self.create_line(x, 0, x, total, fill=LINE, dash=(4, 4))
                shown = self.steps[:self.count]
                for k, (a, b, label, _) in enumerate(shown):
                    y = top + head_h + step_h * (k + 0.8)
                    cur = k == len(shown) - 1
                    col = ACCENT if cur else MUTED
                    if a == b:
                        bw = min(col_w * 1.8, w - 20)
                        x0 = min(max(10, xs[a] - bw / 2), w - bw - 10)
                        self.create_rectangle(x0, y - fh - 4, x0 + bw, y + 4, fill=CUR_BG if cur else CARD, outline=col)
                        self.create_text(x0 + bw / 2, y - fh / 2, text=label, fill=TEXT, font=F["bold"] if cur else F["ui"], width=bw - 12, justify="center")
                    else:
                        self.create_line(xs[a], y, xs[b], y, fill=col, width=3 if cur else 2, arrow=tk.LAST, arrowshape=(12, 14, 5))
                        mid = (xs[a] + xs[b]) / 2
                        self.create_text(mid, y - 6, text=label, fill=col if cur else TEXT, font=F["bold"] if cur else F["ui"],
                                         anchor="s", width=max(120, abs(xs[b] - xs[a]) - 24), justify="center")
                self.configure(scrollregion=(0, 0, w, total))
                y_off = 0
                if shown:
                    height = max(1, self.winfo_height())
                    need = top + head_h + step_h * (len(shown) + 0.5) - height
                    y_off = min(max(0, need), max(0, total - height))
                    self.yview_moveto(y_off / max(1, total))
                # the actor names stay pinned to the top of what you can see
                self.create_rectangle(0, y_off, w, y_off + top + head_h + 4, fill=BG, outline=BG)
                for i, a in enumerate(self.actors):
                    self.create_rectangle(xs[i] - col_w / 2 + 6, y_off + top, xs[i] + col_w / 2 - 6, y_off + top + head_h, fill=ACCENT, outline=ACCENT_DK)
                    self.create_text(xs[i], y_off + top + head_h / 2, text=a, fill="#ffffff", font=F["bold"], width=col_w - 20, justify="center")
            except tk.TclError:
                pass


    class StackView(tk.Canvas):
        """Encapsulation: a growing stack of headers around the data."""
        LAYER_COLORS = ("B1", "B2", "B3", "B4", "B5")

        def __init__(self, parent):
            super().__init__(parent, bg=BG, highlightthickness=0, height=240)
            self.count = 0
            self.bind("<Configure>", lambda e: self.redraw())
            THEME_LISTENERS.append(self.redraw)
            APP["listeners"].append(self.redraw)

        def show(self, count):
            self.count = count
            self.redraw()

        def redraw(self):
            try:
                self.delete("all")
                fh = F["bold"].metrics("linespace")
                w = max(self.winfo_width(), 400)
                colmap = {"L2 header": B3, "L3 header": B2, "L4 header": B1, "DATA": B5, "L2 trailer": B3}
                rows = [("Layer 7", "data", ["DATA"]), ("Layer 4", "segment / datagram", ["L4 header", "DATA"]),
                        ("Layer 3", "packet", ["L3 header", "L4 header", "DATA"]),
                        ("Layer 2", "frame", ["L2 header", "L3 header", "L4 header", "DATA", "L2 trailer"]), ("Layer 1", "bits", None)]
                rh = fh * 2 + 12
                need = len(rows) * (rh + 10) + 20
                if int(self.cget("height")) != need:
                    self.configure(height=need)
                lab_w = max(F["bold"].measure("Layer 7"), F["ui"].measure("segment / datagram")) + 28
                bw = max(70, (w - lab_w - 20) / 6.6)
                for k, (layer, pdu, parts) in enumerate(rows[:self.count]):
                    y = 10 + k * (rh + 10)
                    cur = k == self.count - 1
                    self.create_text(10, y + rh / 2, text=layer + "\n" + pdu, anchor="w", fill=HEAD if cur else MUTED,
                                     font=F["bold"] if cur else F["ui"])
                    x = lab_w
                    if parts is None:
                        self.create_text(x, y + rh / 2, text="1 0 1 1 0 0 1 0 1 1 1 0 0 1 0 ...  (voltage, light or radio)", anchor="w",
                                         fill=TEXT, font=F["codeb"] if cur else F["code"])
                        continue
                    for part in parts:
                        tw = bw * (1.5 if part == "DATA" else 1)
                        self.create_rectangle(x, y, x + tw, y + rh, fill=colmap[part], outline=FLAG if cur else CARD, width=3 if cur else 1)
                        self.create_text(x + tw / 2, y + rh / 2, text=part, fill="#ffffff", font=F["bold"])
                        x += tw
            except tk.TclError:
                pass


    class FrameView(tk.Canvas):
        """PC - router(s) - server diagram for the frame-traversal lab, with the current hop highlighted."""

        def __init__(self, parent):
            super().__init__(parent, bg=BG, highlightthickness=0, height=170)
            self.model, self.hop = None, None
            self.bind("<Configure>", lambda e: self.redraw())
            THEME_LISTENERS.append(self.redraw)
            APP["listeners"].append(self.redraw)

        def set_model(self, model, hop=None):
            self.model, self.hop = model, hop
            self.redraw()

        def redraw(self):
            try:
                self.delete("all")
                if not self.model:
                    return
                fh = F["ui"].metrics("linespace")
                w = max(self.winfo_width(), 500)
                devs = self.model["devices"]
                n = len(devs)
                bw = min(190, (w - 20) / n - 20)
                xs = [10 + bw / 2 + i * ((w - 20 - bw) / max(1, n - 1)) for i in range(n)]
                h = fh * 4 + 16
                y0 = 10
                need = h + fh * 2 + 24
                if int(self.cget("height")) != need:
                    self.configure(height=need)
                for i, d in enumerate(devs):
                    is_rt = "in_ip" in d
                    fill = B3 if is_rt else (B2 if d["name"].startswith("Server") else B1)
                    self.create_rectangle(xs[i] - bw / 2, y0, xs[i] + bw / 2, y0 + h, fill=fill, outline=CARD)
                    self.create_text(xs[i], y0 + 4, text=d["name"], fill="#ffffff", font=F["bold"], anchor="n", width=bw - 6)
                    if is_rt:
                        txt = f"in {d['in_ip']}\nout {d['out_ip']}"
                    else:
                        txt = f"{d['ip']}\n{d['mac'][:8]}..."
                    self.create_text(xs[i], y0 + fh + 10, text=txt, fill="#ffffff", font=F["small"], anchor="n", width=bw - 6, justify="center")
                for i in range(n - 1):
                    active = self.hop == i
                    col = ACCENT if active else LINE
                    self.create_line(xs[i] + bw / 2, y0 + h / 2, xs[i + 1] - bw / 2, y0 + h / 2, fill=col, width=5 if active else 2,
                                     arrow=tk.LAST if active else None, arrowshape=(14, 16, 6))
                    if self.model["hops"][i:i + 1]:
                        self.create_text((xs[i] + xs[i + 1]) / 2, y0 + h / 2 - 8, text=f"hop {i + 1}", fill=ACCENT if active else MUTED,
                                         font=F["bold"] if active else F["small"], anchor="s")
                if self.model.get("nat"):
                    self.create_text(xs[-2], y0 + h + 6, text="NAT / PAT here", fill=HOST, font=F["bold"], anchor="n")
            except tk.TclError:
                pass


    # ===========================================================================
    # LAB WINDOW (the "dev mode" for networking): each tab solves or follows something one step at a time
    # ===========================================================================
    SUBNET_EXAMPLES = [f"{ip}/{p}" for ip, p in PROF_CIDR]
    CLSM_EXAMPLES = [f"{b}/{bp}  {n} subnets, {h:,} hosts" for b, bp, n, h in PROF_CLSM]
    ROUTE_EXAMPLES = ["10.1.1.77", "10.1.2.200", "10.200.1.9", "192.168.45.3", "192.168.200.10", "172.17.3.50", "172.20.1.15",
                      "172.20.1.100", "172.20.1.200", "8.8.8.8", "10.1.3.4"]


    def entry_row(parent, label, width=20, text=""):
        ttk.Label(parent, text=label).pack(side="left", padx=(0, 4))
        var = tk.StringVar(value=text)
        ent = ttk.Entry(parent, textvariable=var, width=width, font=F["ui"])
        ent.pack(side="left", padx=(0, 12))
        return var, ent


    class SubnetTab(ttk.Frame):
        def __init__(self, lab, parent):
            super().__init__(parent, padding=10)
            self.lab = lab
            top = ttk.Frame(self)
            top.pack(fill="x")
            self.ip, ent = entry_row(top, "Host IP:", 16, "201.25.145.52")
            ttk.Label(top, text="/").pack(side="left")
            self.prefix = tk.IntVar(value=19)
            ttk.Spinbox(top, from_=1, to=32, width=3, textvariable=self.prefix, font=F["ui"]).pack(side="left", padx=(2, 12))
            ttk.Label(top, text="Professor's sheet:").pack(side="left", padx=(8, 4))
            self.ex = ttk.Combobox(top, state="readonly", width=20, values=SUBNET_EXAMPLES, font=F["ui"])
            self.ex.pack(side="left")
            self.ex.bind("<<ComboboxSelected>>", self.pick_example)
            row2 = ttk.Frame(self)
            row2.pack(fill="x", pady=(8, 4))
            ttk.Button(row2, text="Solve step by step", style="Accent.TButton", command=self.solve).pack(side="left", padx=(0, 6))
            ttk.Button(row2, text="Random problem", command=self.random).pack(side="left", padx=4)
            self.hand = tk.BooleanVar(value=False)
            ttk.Checkbutton(row2, text="Hand-solve first", variable=self.hand).pack(side="left", padx=10)
            ent.bind("<Return>", lambda e: self.solve())
            self.msg = tk.Label(self, text="", bg=BG, fg=BAD, font=F["ui"], anchor="w")
            self.msg.pack(fill="x")
            self.bits = BitBar(self)
            self.bits.pack(fill="x", pady=(4, 4))
            self.panel = StepPanel(self, on_change=self._changed)
            self.panel.pack(fill="both", expand=True)
            self.sol, self.steps = None, []
            self.solve()

        def pick_example(self, _=None):
            ip, p = self.ex.get().split("/")
            self.ip.set(ip)
            self.prefix.set(int(p))
            self.solve()

        def random(self):
            ip, p = random_cidr_problem()
            self.ip.set(ip)
            self.prefix.set(p)
            self.solve()

        def load(self, ip=None, prefix=None):
            if ip:
                self.ip.set(ip)
            if prefix:
                self.prefix.set(int(prefix))
            self.solve()

        def solve(self):
            ip = norm_ip(self.ip.get())
            try:
                p = int(self.prefix.get())
            except (tk.TclError, ValueError):
                p = -1
            if ip is None or not 1 <= p <= 32:
                self.msg.configure(text="Enter a valid IPv4 address (like 201.25.145.52) and a prefix from 1 to 32.")
                return
            self.msg.configure(text="")
            self.ip.set(ip)
            self.sol, self.steps = cidr_steps(ip, p)
            self.panel.set_steps(self.steps, shown=0 if self.hand.get() else 1)

        def _changed(self, shown):
            if not self.steps:
                return
            bits_step = next((s for s in self.steps if s["key"] == "binary"), None)
            idx = self.steps.index(bits_step) if bits_step else None
            if bits_step and shown > idx:
                self.bits.set_rows(list(bits_step["bits"]), bits_step["prefix"], octet=self.steps[0].get("octet"))
            else:
                self.bits.set_rows([], 0)


    class ClsmTab(ttk.Frame):
        def __init__(self, lab, parent):
            super().__init__(parent, padding=10)
            top = ttk.Frame(self)
            top.pack(fill="x")
            self.base, _ = entry_row(top, "Network:", 14, "211.182.135.0")
            ttk.Label(top, text="/").pack(side="left")
            self.bp = tk.IntVar(value=24)
            ttk.Spinbox(top, from_=8, to=30, width=3, textvariable=self.bp, font=F["ui"]).pack(side="left", padx=(2, 12))
            ttk.Label(top, text="Subnets:").pack(side="left", padx=(0, 4))
            self.n = tk.IntVar(value=4)
            ttk.Spinbox(top, from_=2, to=64, width=3, textvariable=self.n, font=F["ui"]).pack(side="left", padx=(0, 12))
            ttk.Label(top, text="Hosts each:").pack(side="left", padx=(0, 4))
            self.hosts = tk.IntVar(value=50)
            ttk.Spinbox(top, from_=1, to=1000000, width=7, textvariable=self.hosts, font=F["ui"]).pack(side="left", padx=(0, 12))
            row1b = ttk.Frame(self)
            row1b.pack(fill="x", pady=(6, 0))
            ttk.Label(row1b, text="Professor's sheet:").pack(side="left", padx=(0, 4))
            self.ex = ttk.Combobox(row1b, state="readonly", width=30, values=CLSM_EXAMPLES, font=F["ui"])
            self.ex.pack(side="left", padx=(0, 12))
            self.ex.bind("<<ComboboxSelected>>", self.pick_example)
            row2 = ttk.Frame(self)
            row2.pack(fill="x", pady=(8, 4))
            ttk.Button(row2, text="Solve step by step", style="Accent.TButton", command=self.solve).pack(side="left", padx=(0, 6))
            ttk.Button(row2, text="Random problem", command=self.random).pack(side="left", padx=4)
            self.hand = tk.BooleanVar(value=False)
            ttk.Checkbutton(row2, text="Hand-solve first", variable=self.hand).pack(side="left", padx=10)
            self.msg = tk.Label(self, text="", bg=BG, fg=BAD, font=F["ui"], anchor="w")
            self.msg.pack(fill="x")
            self.panel = StepPanel(self, on_change=self._changed, height=9)
            self.panel.pack(fill="both", expand=True)
            box, self.tree = make_grid(self, height=6)
            box.pack(fill="x", pady=(6, 0))
            fill_plain_grid(self.tree, ["#", "Network", "First host", "Last host", "Broadcast"], [])
            self.rows, self.steps = [], []
            self.solve()

        def pick_example(self, _=None):
            i = CLSM_EXAMPLES.index(self.ex.get())
            b, bp, n, h = PROF_CLSM[i]
            self.load(b, bp, n, h)

        def random(self):
            b, bp, n, h = random_clsm_problem()
            self.load(b, bp, n, h)

        def load(self, base=None, bp=None, n=None, hosts=None):
            if base:
                self.base.set(base)
            if bp:
                self.bp.set(int(bp))
            if n:
                self.n.set(int(n))
            if hosts:
                self.hosts.set(int(hosts))
            self.solve()

        def solve(self):
            base = norm_ip(self.base.get())
            try:
                bp, n, hosts = int(self.bp.get()), int(self.n.get()), int(self.hosts.get())
            except (tk.TclError, ValueError):
                base = None
            if base is None or not (8 <= bp <= 30 and n >= 2 and hosts >= 1):
                self.msg.configure(text="Enter a network like 211.182.135.0, a prefix 8-30, at least 2 subnets and at least 1 host.")
                return
            self.msg.configure(text="")
            self.base.set(base)
            np_, rows, self.steps = clsm_steps(base, bp, n, hosts)
            self.rows, self.np = rows, np_
            self.panel.set_steps(self.steps, shown=0 if self.hand.get() else 1)

        def _changed(self, shown):
            done = bool(self.steps) and shown >= len(self.steps)
            fill_plain_grid(self.tree, ["#", "Network", "First host", "Last host", "Broadcast"],
                            [(i, f"{r[0]}/{self.np}", r[1], r[2], r[3]) for i, r in enumerate(self.rows, 1)] if done else [])


    class RouteTab(ttk.Frame):
        def __init__(self, lab, parent):
            super().__init__(parent, padding=10)
            top = ttk.Frame(self)
            top.pack(fill="x")
            self.dest, ent = entry_row(top, "Packet for:", 14, "10.1.1.77")
            ttk.Label(top, text="Examples:").pack(side="left", padx=(8, 4))
            self.ex = ttk.Combobox(top, state="readonly", width=15, values=ROUTE_EXAMPLES, font=F["ui"])
            self.ex.pack(side="left")
            self.ex.bind("<<ComboboxSelected>>", lambda e: (self.dest.set(self.ex.get()), self.go()))
            row2 = ttk.Frame(self)
            row2.pack(fill="x", pady=(8, 4))
            self.metric = tk.StringVar(value="hops")
            ttk.Radiobutton(row2, text="metric = hop count", variable=self.metric, value="hops").pack(side="left", padx=(0, 8))
            ttk.Radiobutton(row2, text="metric = link speed", variable=self.metric, value="speed").pack(side="left", padx=4)
            row3 = ttk.Frame(self)
            row3.pack(fill="x", pady=(0, 4))
            ttk.Button(row3, text="Look it up step by step", style="Accent.TButton", command=self.go).pack(side="left", padx=(0, 6))
            self.hand = tk.BooleanVar(value=False)
            ttk.Checkbutton(row3, text="Hand-solve first", variable=self.hand).pack(side="left", padx=10)
            ent.bind("<Return>", lambda e: self.go())
            ttk.Label(self, text="Logan router A (from the Routing Tables lecture). Rule 1: the LONGEST matching prefix wins. "
                                 "Rule 2: the metric breaks ties.", foreground=MUTED).pack(anchor="w", pady=(4, 2))
            box, self.tree = make_grid(self, height=7, hscroll=False)
            box.pack(fill="x")
            fill_plain_grid(self.tree, ["#", "Destination", "Mask", "Interface", "Next hop", "Hops", "Speed"],
                            [(i + 1, r[0], f"/{r[1]}", r[2], r[3], r[4], speed_text(r[5])) for i, r in enumerate(LOGAN)], stretch_last=False)
            self.msg = tk.Label(self, text="", bg=BG, fg=BAD, font=F["ui"], anchor="w")
            self.msg.pack(fill="x")
            self.panel = StepPanel(self, on_change=self._changed, height=9)
            self.panel.pack(fill="both", expand=True, pady=(6, 0))
            self.res = None
            self.go()

        def load(self, dest=None):
            if dest:
                self.dest.set(dest)
            self.go()

        def go(self):
            d = norm_ip(self.dest.get())
            if d is None:
                self.msg.configure(text="Enter a destination IP address like 10.1.1.77.")
                return
            self.msg.configure(text="")
            self.dest.set(d)
            self.res = route_steps(d, self.metric.get())
            self.panel.set_steps(self.res["steps"], shown=0 if self.hand.get() else 1)

        def _changed(self, shown):
            for iid in self.tree.get_children():
                self.tree.item(iid, tags=())
            if not self.res or shown == 0:
                return
            st = self.res["steps"][shown - 1]
            kids = self.tree.get_children()
            tag = "pick" if st["key"] in ("metric", "result") else "match"
            rows = st.get("rows", [])
            for i in rows:
                self.tree.item(kids[i], tags=(tag,))
            if rows:
                self.tree.see(kids[rows[-1]])
                self.tree.see(kids[rows[0]])


    class FrameTab(ttk.Frame):
        def __init__(self, lab, parent):
            super().__init__(parent, padding=10)
            top = ttk.Frame(self)
            top.pack(fill="x")
            self.nat = tk.BooleanVar(value=False)
            self.routers = tk.IntVar(value=1)
            ttk.Checkbutton(top, text="NAT / PAT on the edge", variable=self.nat, command=self.new).pack(side="left", padx=(0, 12))
            ttk.Radiobutton(top, text="1 router", variable=self.routers, value=1, command=self.new).pack(side="left", padx=4)
            ttk.Radiobutton(top, text="2 routers", variable=self.routers, value=2, command=self.new).pack(side="left", padx=4)
            row2 = ttk.Frame(self)
            row2.pack(fill="x", pady=(6, 0))
            ttk.Button(row2, text="New addresses", command=self.new).pack(side="left")
            self.view = FrameView(self)
            self.view.pack(fill="x", pady=(8, 4))
            self.panel = StepPanel(self, on_change=self._changed, accumulate=False, height=4)
            self.panel.pack(fill="x")
            ttk.Label(self, text="Each column is one hop's frame. Highlighted rows changed since the previous hop.", foreground=MUTED).pack(anchor="w", pady=(8, 2))
            box, self.tree = make_grid(self, height=6, hscroll=True)
            box.pack(fill="both", expand=True)
            self.model = None
            self.new()

        def new(self):
            self.model = frame_model(self.nat.get(), self.routers.get())
            self.panel.set_steps(self.model["steps"], shown=1)

        def _changed(self, shown):
            if not self.model:
                return
            st = self.model["steps"][shown - 1]
            hop = st["hop"]
            self.view.set_model(self.model, hop)
            hops = self.model["hops"]
            upto = (hop + 1) if hop is not None else (len(hops) if st["key"] == "summary" else 0)
            cols = ["Layer", "Field"] + [f"Hop {i + 1}" for i in range(upto)]
            rows = []
            fields = [("2", "source MAC", "src_mac"), ("2", "destination MAC", "dst_mac"), ("3", "source IP", "src_ip"),
                      ("3", "destination IP", "dst_ip"), ("4", "source port", "src_port"), ("4", "destination port", "dst_port")]
            fill_plain_grid(self.tree, cols, [], stretch_last=False)
            for layer, label, key in fields:
                vals = [hops[i][key] for i in range(upto)]
                iid = self.tree.insert("", "end", values=[f"L{layer}", label] + vals)
                for i in range(upto):
                    if key in hops[i]["changed"] and i > 0:
                        self.tree.item(iid, tags=("chg",))
                        break
            cw = F["ui"].measure("0")
            self.tree.column("c1", width=cw * 18)
            for i in range(upto):
                self.tree.column(f"c{i + 2}", width=cw * 20)


    class WalkTab(ttk.Frame):
        def __init__(self, lab, parent):
            super().__init__(parent, padding=10)
            top = ttk.Frame(self)
            top.pack(fill="x")
            ttk.Label(top, text="Walk-through:").pack(side="left", padx=(0, 6))
            self.keys = WALK_ORDER + ["encap"]
            self.titles = [WALKS[k]["title"] if k in WALKS else "Encapsulation: how data is wrapped on the way down" for k in self.keys]
            self.combo = ttk.Combobox(top, state="readonly", width=58, values=self.titles, font=F["ui"])
            self.combo.pack(side="left", padx=(0, 8))
            self.combo.bind("<<ComboboxSelected>>", lambda e: self.load(self.keys[self.titles.index(self.combo.get())]))
            self.play_btn = ttk.Button(top, text="Play", command=self.play)
            self.play_btn.pack(side="left", padx=4)
            self.intro = wrap_label(self, "", fg=MUTED)
            self.intro.pack(fill="x", pady=(6, 4))
            self.seq = SeqDiagram(self)
            self.stack = StackView(self)
            self.panel = StepPanel(self, on_change=self._changed, accumulate=False, height=5)
            self.panel.pack(side="bottom", fill="x", pady=(6, 0))
            self.seq.pack(fill="both", expand=True)
            self.key = None
            self._job = None
            self.load("tcp")

        def load(self, key):
            self.stop()
            self.key = key
            self.combo.set(self.titles[self.keys.index(key)])
            if key == "encap":
                self.seq.pack_forget()
                self.stack.pack(fill="both", expand=True)
                self.intro.configure(text="Sending data down the stack: every layer adds its own header (Layer 2 also adds a trailer). "
                                          "The receiver de-encapsulates in the reverse order.")
                steps = [{"title": t, "lines": [f"PDU: {pdu}", txt]} for t, pdu, txt in ENCAP_STEPS]
                self.panel.set_steps(steps, shown=1)
            else:
                self.stack.pack_forget()
                self.seq.pack(fill="both", expand=True)
                w = WALKS[key]
                self.intro.configure(text=w["intro"])
                self.seq.load(w["actors"], w["steps"], 0)
                steps = [{"title": lab, "lines": [txt]} for _, _, lab, txt in w["steps"]]
                steps.append({"title": "Summary", "lines": [w["summary"]], "answer": False})
                self.panel.set_steps(steps, shown=1)

        def _changed(self, shown):
            if self.key == "encap":
                self.stack.show(shown)
            elif self.key:
                self.seq.show(min(shown, len(WALKS[self.key]["steps"])))

        def play(self):
            if self._job:
                self.stop()
                return
            self.panel.reset()
            self.play_btn.configure(text="Stop")
            self._tick()

        def _tick(self):
            if self.panel.shown >= len(self.panel.steps):
                self.stop()
                return
            self.panel.forward()
            self._job = self.after(2200, self._tick)

        def stop(self):
            if self._job:
                try:
                    self.after_cancel(self._job)
                except tk.TclError:
                    pass
            self._job = None
            try:
                self.play_btn.configure(text="Play")
            except tk.TclError:
                pass


    class BinaryTab(ttk.Frame):
        def __init__(self, lab, parent):
            super().__init__(parent, padding=10)
            ttk.Label(self, text="Click a bit to flip it, or type a number. One octet = 8 bits.", foreground=MUTED).pack(anchor="w")
            self.bits = [0] * 8
            self.cells = []
            row = tk.Frame(self, bg=BG)
            row.pack(anchor="w", pady=10)
            for i in range(8):
                col = tk.Frame(row, bg=BG)
                col.pack(side="left", padx=4)
                tk.Label(col, text=str(128 >> i), font=F["bold"], bg=BG, fg=MUTED).pack()
                b = tk.Label(col, text="0", font=F["h1"], width=3, bg=CARD, fg=TEXT, bd=1, relief="solid", cursor="hand2")
                b.pack()
                b.bind("<Button-1>", lambda e, i=i: self.flip(i))
                self.cells.append(b)
            r2 = ttk.Frame(self)
            r2.pack(fill="x", pady=4)
            self.dec, de = entry_row(r2, "Decimal:", 6, "0")
            self.hexv, he = entry_row(r2, "Hex:", 5, "00")
            de.bind("<KeyRelease>", lambda e: self.from_dec())
            he.bind("<KeyRelease>", lambda e: self.from_hex())
            self.info = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["ui"], anchor="w", justify="left")
            self.info.pack(fill="x", pady=6)
            ttk.Separator(self).pack(fill="x", pady=8)
            ttk.Label(self, text="A whole IPv4 address in binary:").pack(anchor="w")
            r3 = ttk.Frame(self)
            r3.pack(fill="x", pady=4)
            self.ipv, ie = entry_row(r3, "IP address:", 18, "192.168.10.77")
            ie.bind("<KeyRelease>", lambda e: self.ip_bin())
            self.ipout = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["code"], anchor="w", justify="left")
            self.ipout.pack(fill="x")
            self.refresh()
            self.ip_bin()

        def value(self):
            return sum(b << (7 - i) for i, b in enumerate(self.bits))

        def flip(self, i):
            self.bits[i] ^= 1
            self.refresh()

        def from_dec(self):
            try:
                v = int(self.dec.get())
            except ValueError:
                return
            if 0 <= v <= 255:
                self.bits = [int(c) for c in f"{v:08b}"]
                self.refresh(skip="dec")

        def from_hex(self):
            try:
                v = int(self.hexv.get(), 16)
            except ValueError:
                return
            if 0 <= v <= 255:
                self.bits = [int(c) for c in f"{v:08b}"]
                self.refresh(skip="hex")

        def refresh(self, skip=None):
            for b, c in zip(self.bits, self.cells):
                c.configure(text=str(b), bg=ACCENT if b else CARD, fg="#ffffff" if b else TEXT)
            v = self.value()
            if skip != "dec":
                self.dec.set(str(v))
            if skip != "hex":
                self.hexv.set(f"{v:02X}")
            ones = f"{v:08b}".count("1")
            valid = v in TABLE2 and f"{v:08b}" == "1" * ones + "0" * (8 - ones)
            parts = [f"{v:08b}  =  {v} decimal  =  0x{v:02X}"]
            parts.append(f"Valid mask octet: yes. Table 2 with {ones} one-bit(s) = {v}; magic number = 256 - {v} = {256 - v}." if valid
                         else "Valid mask octet: no. A mask octet's 1-bits must be contiguous from the left (Table 2: 0, 128, 192, 224, 240, 248, 252, 254, 255).")
            self.info.configure(text="\n".join(parts))

        def ip_bin(self):
            ip = norm_ip(self.ipv.get())
            if ip is None:
                self.ipout.configure(text="(type an IPv4 address)")
                return
            o = ip.split(".")
            self.ipout.configure(text="decimal  " + "   ".join(f"{x:>8}" for x in o) + "\nbinary   " + " ".join(f"{int(x):08b}" for x in o)
                                 + "\nhex      " + "   ".join(f"{int(x):>8X}" for x in o))


    class IPv6Tab(ttk.Frame):
        def __init__(self, lab, parent):
            super().__init__(parent, padding=10)
            top = ttk.Frame(self)
            top.pack(fill="x")
            self.addr, ent = entry_row(top, "IPv6 address:", 36, "2001:0000:0B80:0000:0000:00D3:9C5A:00CC")
            ent.bind("<Return>", lambda e: self.explain())
            row0 = ttk.Frame(self)
            row0.pack(fill="x", pady=(6, 0))
            ttk.Button(row0, text="Explain step by step", style="Accent.TButton", command=self.explain).pack(side="left", padx=(0, 6))
            ttk.Button(row0, text="Random", command=self.random).pack(side="left", padx=4)
            row = ttk.Frame(self)
            row.pack(fill="x", pady=(10, 4))
            self.mine, me = entry_row(row, "Your shortened form:", 28, "")
            ttk.Button(row, text="Check", command=self.check).pack(side="left", padx=4)
            self.verdict = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["bold"], anchor="w")
            self.verdict.pack(fill="x")
            me.bind("<Return>", lambda e: self.check())
            self.msg = tk.Label(self, text="", bg=BG, fg=BAD, font=F["ui"], anchor="w")
            self.msg.pack(fill="x")
            self.panel = StepPanel(self, height=14)
            self.panel.pack(fill="both", expand=True)
            self.explain()

        def random(self):
            r = random.Random()
            blocks = [f"{r.randint(0, 0xFFFF):04X}" for _ in range(8)]
            for _ in range(r.randint(1, 3)):
                blocks[r.randint(1, 6)] = "0000"
            i = r.randint(1, 5)
            for j in range(i, i + r.randint(1, 3)):
                blocks[min(j, 7)] = "0000"
            self.addr.set(":".join(blocks))
            self.mine.set("")
            self.verdict.configure(text="")
            self.explain()

        def explain(self):
            try:
                a = ipaddress.IPv6Address(self.addr.get().strip())
            except ValueError:
                self.msg.configure(text="That isn't a valid IPv6 address (eight blocks of up to four hex digits, with at most one ::).")
                return
            self.msg.configure(text="")
            exp = a.exploded.split(":")
            nolead = [b.lstrip("0") or "0" for b in exp]
            comp = a.compressed
            runs, cur = [], []
            for i, b in enumerate(nolead + ["x"]):
                if b == "0":
                    cur.append(i)
                else:
                    if cur:
                        runs.append(cur)
                    cur = []
            steps = [{"key": "expand", "title": "1. Write all eight blocks, four hex digits each",
                      "lines": [":".join(exp), "8 blocks x 16 bits = 128 bits."]},
                     {"key": "lead", "title": "2. Drop the leading zeros in each block",
                      "lines": [":".join(nolead), "A block of 0000 becomes a single 0."]}]
            if runs:
                best = max(runs, key=len)
                steps.append({"key": "run", "title": "3. Replace ONE run of all-zero blocks with ::",
                              "lines": [f"Zero blocks found: " + "; ".join(f"blocks {r[0] + 1}-{r[-1] + 1}" for r in runs),
                                        f"Use the LONGEST run (blocks {best[0] + 1}-{best[-1] + 1}), and only once: using :: twice would hide how many zeros each one stands for."
                                        if len(runs) > 1 else "Only one run, so that is the one to replace. (:: may be used only once.)",
                                        "A run of just one zero block is not worth shortening unless it is the only run."]})
            else:
                steps.append({"key": "run", "title": "3. Look for a run of zero blocks", "lines": ["There is no run of all-zero blocks, so nothing becomes ::."]})
            kind = ("loopback (::1)" if a.is_loopback else "link-local (FE80::/10, valid only on this link)" if a.is_link_local else
                    "multicast (FF00::/8)" if a.is_multicast else "unique local (FC00::/7)" if a.is_private and exp[0].startswith(("fc", "fd"))
                    else "global unicast (2000::/3, routable on the Internet)" if exp[0][0] in "23" else "other / reserved")
            steps.append({"key": "answer", "title": "4. Shortest form and type",
                          "lines": [f"Shortest:  {comp}", f"Type: {kind}", f"Network prefix = first 64 bits: {':'.join(exp[:4])}",
                                    f"Interface ID = last 64 bits: {':'.join(exp[4:])}"], "answer": True})
            self.comp = comp
            self.panel.set_steps(steps, shown=1)

        def check(self):
            try:
                mine = ipaddress.IPv6Address(self.mine.get().strip())
                same = mine == ipaddress.IPv6Address(self.addr.get().strip())
            except ValueError:
                self.verdict.configure(text="not a valid IPv6 address", fg=BAD)
                return
            txt = self.mine.get().strip().lower()
            if same and txt == self.comp:
                self.verdict.configure(text="Correct: shortest form", fg=GOOD)
            elif same:
                self.verdict.configure(text=f"Same address, but not the shortest. Shortest: {self.comp}", fg=HOST)
            else:
                self.verdict.configure(text="That is a different address", fg=BAD)


    class TabHost(ttk.Frame):
        """Tab buttons that WRAP onto extra rows (a Notebook clips its tabs when the text gets large). Pages live in .body."""

        def __init__(self, parent, on_select=None):
            super().__init__(parent)
            self.bar = tk.Frame(self, bg=BG)
            self.bar.pack(fill="x")
            self.body = ttk.Frame(self)
            self.body.pack(fill="both", expand=True, pady=(6, 0))
            self.buttons, self.pages, self.cur, self.on_select = {}, {}, None, on_select
            self.bar.bind("<Configure>", lambda e: self._layout())
            APP["listeners"].append(self._layout)

        def add(self, key, title, page):
            btn = ttk.Button(self.bar, text=title, command=lambda: self.select(key))
            self.buttons[key] = btn
            self.pages[key] = page
            self._layout()

        def _layout(self):
            try:
                w = max(self.bar.winfo_width(), 300)
                x = row = col = 0
                for b in self.buttons.values():
                    bw = b.winfo_reqwidth() + 8
                    if x + bw > w and col:
                        row, col, x = row + 1, 0, 0
                    b.grid(row=row, column=col, padx=3, pady=2, sticky="w")
                    x += bw
                    col += 1
            except tk.TclError:
                pass

        def select(self, key):
            if key not in self.pages:
                return
            if self.cur is not None:
                self.pages[self.cur].pack_forget()
            self.cur = key
            self.pages[key].pack(fill="both", expand=True)
            for k, b in self.buttons.items():
                b.configure(style="Accent.TButton" if k == key else "TButton")
            if self.on_select:
                self.on_select(key)


    class Lab(tk.Toplevel):
        """The walk-through labs. open_tab('subnet', ip=..., prefix=...) pre-fills a problem."""
        TABS = [("subnet", "Subnet (CIDR)", SubnetTab), ("clsm", "CLSM", ClsmTab), ("route", "Routing table", RouteTab),
                ("frame", "Frame traversal", FrameTab), ("walk", "Walk-throughs", WalkTab), ("encap", None, None),
                ("binary", "Binary / hex", BinaryTab), ("ipv6", "IPv6", IPv6Tab)]

        def __init__(self, app):
            super().__init__(app.root)
            self.app = app
            self.title("IS 4440 Labs - step by step")
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{min(1120, sw - 60)}x{min(860, sh - 120)}")
            self.minsize(720, 520)
            self.configure(bg=BG)
            self.nb = TabHost(self)
            self.nb.pack(fill="both", expand=True, padx=8, pady=8)
            self.tabs = {}
            for key, title, cls in self.TABS:
                if cls is None:
                    continue
                tab = cls(self, self.nb.body)
                self.nb.add(key, title, tab)
                self.tabs[key] = tab
            self.nb.select("subnet")
            self.bind("<F2>", lambda e: self.destroy())
            self.bind("<Escape>", lambda e: self.destroy())
            self.protocol("WM_DELETE_WINDOW", self.destroy)

        def open_tab(self, key, arg=None, **kw):
            if key == "encap":
                key, arg = "walk", "encap"
            tab = self.tabs.get(key)
            if tab is None:
                return
            self.nb.select(key)
            if key == "subnet" and kw:
                tab.load(kw.get("ip"), kw.get("prefix"))
            elif key == "clsm" and kw:
                tab.load(kw.get("base"), kw.get("bp"), kw.get("n"), kw.get("hosts"))
            elif key == "route" and kw.get("dest"):
                tab.load(kw["dest"])
            elif key == "walk" and arg:
                tab.load(arg)
            self.lift()
            self.focus_force()



    # ===========================================================================
    # CHEAT SHEETS (F3) + calculators
    # ===========================================================================
    class WrapTable(tk.Frame):
        """A table whose cells WRAP, so nothing is cut off at large text sizes."""

        def __init__(self, parent, cols, rows):
            super().__init__(parent, bg=LINE)
            self.cols, self.rows = cols, rows
            n = len(cols)
            self.cells = []
            weights = []
            for i in range(n):
                lens = [len(str(cols[i]))] + [len(str(r[i])) for r in rows]
                weights.append(min(max(sum(lens) / len(lens), 6), 46))
            tot = sum(weights)
            self.share = [w / tot for w in weights]
            for c in range(n):
                self.columnconfigure(c, weight=int(self.share[c] * 100), uniform="wt")
            for c, name in enumerate(cols):
                if name == "" and all(not str(r[c]) for r in rows):
                    continue
                lab = tk.Label(self, text=name, font=F["bold"], bg=LINE, fg=TEXT, anchor="w", justify="left", padx=8, pady=4)
                lab.grid(row=0, column=c, sticky="nsew", padx=(0, 1), pady=(0, 1))
                self.cells.append((lab, c))
            for r, row in enumerate(rows, 1):
                for c, val in enumerate(row):
                    lab = tk.Label(self, text=str(val), font=F["bold"] if c == 0 else F["ui"], bg=CARD, fg=TEXT, anchor="nw",
                                   justify="left", padx=8, pady=3)
                    lab.grid(row=r, column=c, sticky="nsew", padx=(0, 1), pady=(0, 1))
                    self.cells.append((lab, c))
            self.bind("<Configure>", self._wrap)

        def _wrap(self, e):
            for lab, c in self.cells:
                lab.configure(wraplength=max(60, int(e.width * self.share[c]) - 22))


    CHEAT_TAB_NAMES = {"layers": "OSI & devices", "ports": "Ports", "addressing": "Addressing", "subnet": "Subnetting", "protocols": "Protocols",
                       "wifi": "Wireless", "arch": "Architecture", "avail": "Recovery & power", "monitor": "Monitoring", "docs": "Cabling & docs",
                       "calc": "Calculators"}


    class CheatSheet(tk.Toplevel):
        def __init__(self, app, tab=None):
            super().__init__(app.root)
            self.app = app
            self.title("IS 4440 - Cheat sheets")
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{min(1060, sw - 60)}x{min(820, sh - 120)}")
            self.minsize(760, 560)
            self.configure(bg=BG)
            top = ttk.Frame(self)
            top.pack(fill="x", padx=10, pady=(8, 0))
            ttk.Label(top, text="Cheat sheets", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Close  (Esc)", command=self.destroy).pack(side="right")
            self.nb = TabHost(self, on_select=lambda k: self._build(k))
            self.nb.pack(fill="both", expand=True, padx=8, pady=8)
            self.frames, self.keys = {}, []
            for key in CHEAT_ORDER:
                holder = ttk.Frame(self.nb.body)
                self.nb.add(key, CHEAT_TAB_NAMES[key], holder)
                self.keys.append(key)
                self.frames[key] = holder
            self.built = set()
            self.bind("<Escape>", lambda e: self.destroy())
            self.bind("<F3>", lambda e: self.destroy())
            self.bind("<MouseWheel>", self._wheel)
            self.sf = {}
            self.nb.select(tab if tab in self.frames else self.keys[0])

        def _wheel(self, e):
            sf = self.sf.get(self.nb.cur)
            if sf is not None:
                sf.scroll(int(-e.delta / 120))

        def select_tab(self, key):
            if key in self.frames:
                self.nb.select(key)
            self.lift()
            self.focus_force()

        def _build(self, key):
            if key in self.built:
                return
            self.built.add(key)
            holder = self.frames[key]
            sf = ScrollFrame(holder)
            sf.pack(fill="both", expand=True)
            self.sf[key] = sf
            body = sf.body
            if key == "calc":
                CalcPanel(self.app, body).pack(fill="both", expand=True)
                return
            info = CHEAT[key]
            ttk.Label(body, text=info["title"], font=F["h1"], foreground=HEAD).pack(anchor="w")
            if key == "subnet":
                row = ttk.Frame(body)
                row.pack(fill="x", pady=(4, 2))
                ttk.Button(row, text="Copy this page as text", command=self.copy_subnet).pack(side="left")
                ttk.Button(row, text="Save as a text file...", command=self.save_subnet).pack(side="left", padx=8)
                ttk.Button(row, text="Open the Subnet lab", style="Accent.TButton",
                           command=lambda: self.app.open_lab({"lab": "subnet", "args": {}})).pack(side="left")
            for sec in info["sections"]:
                tk.Label(body, text=sec["h"], font=F["h2"], bg=BG, fg=TEXT, anchor="w").pack(fill="x", pady=(14, 4))
                if sec.get("cols"):
                    WrapTable(body, sec["cols"], sec["rows"]).pack(fill="x")
                for ln in sec.get("lines", []):
                    wrap_label(body, ln).pack(fill="x", pady=1)
                if sec.get("note"):
                    wrap_label(body, sec["note"], fg=MUTED).pack(fill="x", pady=(4, 0))

        def copy_subnet(self):
            self.clipboard_clear()
            self.clipboard_append(subnet_cheat_text())
            messagebox.showinfo("Copied", "The subnetting cheat sheet is on your clipboard as plain text.", parent=self)

        def save_subnet(self):
            path = filedialog.asksaveasfilename(parent=self, defaultextension=".txt", initialfile="subnetting_cheat_sheet.txt",
                                                filetypes=[("Text file", "*.txt")])
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(subnet_cheat_text() + "\n")
                    messagebox.showinfo("Saved", f"Saved to {path}", parent=self)
                except OSError as e:
                    messagebox.showerror("Could not save", str(e), parent=self)


    class CalcPanel(ttk.Frame):
        """Subnet calculator, host-count helpers, binary/hex converter and an IPv6 shortener, all live."""

        def __init__(self, app, parent):
            super().__init__(parent)
            self.app = app
            self._section("Subnet calculator")
            r = ttk.Frame(self)
            r.pack(fill="x")
            self.ip = tk.StringVar(value="192.168.10.77")
            self.pre = tk.StringVar(value="26")
            ttk.Label(r, text="Host IP:").pack(side="left", padx=(0, 4))
            ttk.Entry(r, textvariable=self.ip, width=18, font=F["ui"]).pack(side="left", padx=(0, 8))
            ttk.Label(r, text="/").pack(side="left")
            ttk.Entry(r, textvariable=self.pre, width=4, font=F["ui"]).pack(side="left", padx=(2, 8))
            ttk.Button(r, text="Step by step in the Lab", command=self.to_lab).pack(side="left")
            self.out = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["code"], anchor="w", justify="left")
            self.out.pack(fill="x", pady=4)
            self.ip.trace_add("write", lambda *a: self.calc())
            self.pre.trace_add("write", lambda *a: self.calc())
            self._section("How many hosts / subnets?")
            r = ttk.Frame(self)
            r.pack(fill="x")
            self.need = tk.StringVar(value="500")
            ttk.Label(r, text="Hosts needed per subnet:").pack(side="left", padx=(0, 4))
            ttk.Entry(r, textvariable=self.need, width=9, font=F["ui"]).pack(side="left", padx=(0, 12))
            self.subs = tk.StringVar(value="6")
            self.bpre = tk.StringVar(value="24")
            ttk.Label(r, text="Subnets needed:").pack(side="left", padx=(0, 4))
            ttk.Entry(r, textvariable=self.subs, width=5, font=F["ui"]).pack(side="left", padx=(0, 12))
            ttk.Label(r, text="from a /").pack(side="left")
            ttk.Entry(r, textvariable=self.bpre, width=4, font=F["ui"]).pack(side="left", padx=2)
            self.out2 = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["code"], anchor="w", justify="left")
            self.out2.pack(fill="x", pady=4)
            for v in (self.need, self.subs, self.bpre):
                v.trace_add("write", lambda *a: self.calc2())
            self._section("Binary / decimal / hex (one octet)")
            r = ttk.Frame(self)
            r.pack(fill="x")
            self.dec, self.binv, self.hexv = tk.StringVar(value="192"), tk.StringVar(value="11000000"), tk.StringVar(value="C0")
            self._lock = False
            for label, var, w, src in (("Decimal", self.dec, 6, "dec"), ("Binary", self.binv, 11, "bin"), ("Hex", self.hexv, 5, "hex")):
                ttk.Label(r, text=label + ":").pack(side="left", padx=(0, 4))
                e = ttk.Entry(r, textvariable=var, width=w, font=F["ui"])
                e.pack(side="left", padx=(0, 12))
                e.bind("<KeyRelease>", lambda ev, s=src: self.convert(s))
            self._section("IPv6 shortener")
            r = ttk.Frame(self)
            r.pack(fill="x")
            self.v6 = tk.StringVar(value="2001:0db8:0000:0000:0000:ff00:0042:8329")
            ttk.Entry(r, textvariable=self.v6, width=46, font=F["ui"]).pack(side="left", padx=(0, 8))
            self.out3 = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["code"], anchor="w", justify="left")
            self.out3.pack(fill="x", pady=4)
            self.v6.trace_add("write", lambda *a: self.calc3())
            self.calc()
            self.calc2()
            self.calc3()

        def _section(self, text):
            tk.Label(self, text=text, font=F["h2"], bg=BG, fg=TEXT, anchor="w").pack(fill="x", pady=(14, 4))

        def to_lab(self):
            ip = norm_ip(self.ip.get())
            try:
                p = int(self.pre.get())
            except ValueError:
                p = None
            self.app.open_lab({"lab": "subnet", "args": {"ip": ip, "prefix": p}})

        def calc(self):
            ip = norm_ip(self.ip.get())
            try:
                p = int(self.pre.get())
            except ValueError:
                p = -1
            if ip is None or not 1 <= p <= 32:
                self.out.configure(text="(enter an IPv4 address and a prefix 1-32)")
                return
            s = solve_cidr(ip, p)
            o = int(ip.split(".")[0])
            cls = "A" if o <= 126 else "B" if o <= 191 else "C" if o <= 223 else "D" if o <= 239 else "E"
            self.out.configure(text=(f"Network ID : {s['network']}\nMask       : {s['mask']}   (/{p})\nBroadcast  : {s['broadcast']}\n"
                                     f"Hosts      : {s['first']} - {s['last']}   ({s['usable']:,} usable)\n"
                                     f"Class {cls}; {'private (RFC 1918)' if ipaddress.IPv4Address(ip).is_private else 'public'}"))

        def calc2(self):
            lines = []
            try:
                n = int(self.need.get())
                if n >= 1:
                    h = 1
                    while 2 ** h - 2 < n:
                        h += 1
                    lines.append(f"{n:,} hosts -> h = {h} (2^{h} - 2 = {2 ** h - 2:,}) -> /{32 - h}  ({mask_of(32 - h)})")
            except ValueError:
                pass
            try:
                s, b = int(self.subs.get()), int(self.bpre.get())
                if s >= 1 and 1 <= b <= 30:
                    k = 0
                    while 2 ** k < s:
                        k += 1
                    lines.append(f"{s} subnets from a /{b} -> borrow {k} bit(s) (2^{k} = {2 ** k}) -> /{b + k}  ({mask_of(min(32, b + k))})")
            except ValueError:
                pass
            self.out2.configure(text="\n".join(lines) or "(enter numbers)")

        def convert(self, src):
            try:
                if src == "dec":
                    v = int(self.dec.get())
                elif src == "bin":
                    v = int(self.binv.get(), 2)
                else:
                    v = int(self.hexv.get(), 16)
            except ValueError:
                return
            if not 0 <= v <= 255:
                return
            if src != "dec":
                self.dec.set(str(v))
            if src != "bin":
                self.binv.set(f"{v:08b}")
            if src != "hex":
                self.hexv.set(f"{v:02X}")

        def calc3(self):
            try:
                a = ipaddress.IPv6Address(self.v6.get().strip())
            except ValueError:
                self.out3.configure(text="(not a valid IPv6 address)")
                return
            self.out3.configure(text=f"Shortest : {a.compressed}\nFull     : {a.exploded}")



    # ===========================================================================
    # SUBNETTING GYM: one practice problem at a time, typed answers, hints that reveal the method step by step
    # ===========================================================================
    class ProblemPage(ttk.Frame):
        """mode: 'cidr' (random host + prefix), 'clsm' (random equal-subnet problem) or 'prof' (the professor's sheet, in order)."""

        def __init__(self, app, parent, mode):
            super().__init__(parent, padding=10)
            self.app, self.mode, self.k = app, mode, 0
            self.fields, self.entries, self.marks = [], {}, {}
            self.head = ttk.Frame(self)
            self.head.pack(fill="x")
            self.chip_holder = ttk.Frame(self.head)
            self.chip_holder.pack(side="left")
            self.counter = tk.Label(self.head, text="", bg=BG, fg=MUTED, font=F["bold"])
            self.counter.pack(side="right")
            if mode == "prof":
                self.pick = ttk.Combobox(self.head, state="readonly", width=44, font=F["ui"],
                                         values=[f"CIDR {i + 1}: {ip}/{p}" for i, (ip, p) in enumerate(PROF_CIDR)] +
                                                [f"CLSM {i + 1}: {b}/{bp}, {n} subnets, {h:,} hosts" for i, (b, bp, n, h) in enumerate(PROF_CLSM)])
                self.pick.pack(side="right", padx=8)
                self.pick.bind("<<ComboboxSelected>>", lambda e: self.goto(self.pick.current()))
            self.stmt = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["h2"], anchor="w", justify="left")
            self.stmt.pack(fill="x", pady=(8, 6))
            self.bind("<Configure>", lambda e: self.stmt.configure(wraplength=max(300, e.width - 40)))
            self.form = ttk.Frame(self)
            self.form.pack(fill="x")
            bar = ttk.Frame(self)
            bar.pack(fill="x", pady=(8, 2))
            ttk.Button(bar, text="Check my answers", style="Accent.TButton", command=self.check).pack(side="left")
            ttk.Button(bar, text="Hint (next step)", command=self.hint).pack(side="left", padx=6)
            ttk.Button(bar, text="Show the whole solution", command=self.solution).pack(side="left")
            ttk.Button(bar, text="Next problem  >", command=self.next).pack(side="left", padx=6)
            bar2 = ttk.Frame(self)
            bar2.pack(fill="x", pady=(0, 6))
            ttk.Button(bar2, text="Open in the Lab", command=self.in_lab).pack(side="left")
            ttk.Button(bar2, text="Tables (F3)", command=lambda: app.open_cheat("subnet")).pack(side="left", padx=6)
            self.result = tk.Label(self, text="", bg=BG, fg=TEXT, font=F["bold"], anchor="w", justify="left")
            self.result.pack(fill="x")
            self.panel = StepPanel(self, height=11)
            self.panel.pack(fill="both", expand=True, pady=(6, 0))
            self.next()

        # -- problems --------------------------------------------------------------
        def goto(self, k):
            self.k = k % (len(PROF_CIDR) + len(PROF_CLSM))
            self.load_prof()

        def next(self):
            if self.mode == "prof":
                self.k = (self.k + 1) % (len(PROF_CIDR) + len(PROF_CLSM)) if getattr(self, "problem", None) else 0
                self.load_prof()
            elif self.mode == "cidr":
                ip, p = random_cidr_problem()
                self.set_problem({"kind": "cidr", "ip": ip, "prefix": p, "key": "SUB-cidr", "prof": False})
            else:
                base, bp, n, hosts = random_clsm_problem()
                self.set_problem({"kind": "clsm", "base": base, "bp": bp, "n": n, "hosts": hosts, "key": "SUB-clsm", "prof": False})

        def load_prof(self):
            k = self.k
            self.pick.current(k)
            if k < len(PROF_CIDR):
                ip, p = PROF_CIDR[k]
                self.set_problem({"kind": "cidr", "ip": ip, "prefix": p, "key": f"PROF-cidr-{k + 1}", "prof": True})
            else:
                b, bp, n, h = PROF_CLSM[k - len(PROF_CIDR)]
                self.set_problem({"kind": "clsm", "base": b, "bp": bp, "n": n, "hosts": h, "key": f"PROF-clsm-{k - len(PROF_CIDR) + 1}", "prof": True})

        def set_problem(self, pr):
            self.problem = pr
            for w in self.chip_holder.winfo_children():
                w.destroy()
            make_chip(self.chip_holder, {"id": "PROF-x" if pr["prof"] else "GEN-x"}).pack(side="left")
            for w in self.form.winfo_children():
                w.destroy()
            self.entries, self.marks = {}, {}
            if pr["kind"] == "cidr":
                sol, steps = cidr_steps(pr["ip"], pr["prefix"])
                pr["sol"] = sol
                self.stmt.configure(text=f"Given the IP address {pr['ip']} /{pr['prefix']}, give the network address, the subnet mask (decimal) "
                                         f"and the broadcast address.")
                pr["fields"] = [("Network address", "network"), ("Subnet mask", "mask"), ("Broadcast address", "broadcast")]
                pr["expect"] = {"network": sol["network"], "mask": sol["mask"], "broadcast": sol["broadcast"]}
            else:
                np_, rows, steps = clsm_steps(pr["base"], pr["bp"], pr["n"], pr["hosts"])
                pr["np"], pr["rows"] = np_, rows
                n = pr["n"]
                a, b = (2, n) if n > 2 else (1, 2)
                self.stmt.configure(text=f"You own {pr['base']}/{pr['bp']} (mask {mask_of(pr['bp'])}). Subnet it into {n} equal subnetworks with at "
                                         f"least {pr['hosts']:,} hosts on each. Give the new mask in slash notation, and the network and broadcast "
                                         f"of subnet #{a} and of subnet #{b}. Assume CIDR is enabled (the all-zeros and all-ones subnets are usable).")
                pr["fields"] = [("New mask (like /26)", "mask"), (f"Subnet #{a} network", f"n{a}"), (f"Subnet #{a} broadcast", f"b{a}"),
                                (f"Subnet #{b} network", f"n{b}"), (f"Subnet #{b} broadcast", f"b{b}")]
                pr["expect"] = {"mask": f"/{np_}", f"n{a}": rows[a - 1][0], f"b{a}": rows[a - 1][3], f"n{b}": rows[b - 1][0], f"b{b}": rows[b - 1][3]}
            for i, (label, key) in enumerate(pr["fields"]):
                ttk.Label(self.form, text=label + ":", width=24).grid(row=i, column=0, sticky="w", pady=2)
                var = tk.StringVar()
                ent = ttk.Entry(self.form, textvariable=var, width=22, font=F["ui"])
                ent.grid(row=i, column=1, sticky="w", pady=2, padx=(0, 10))
                ent.bind("<Return>", lambda e: self.check())
                mark = tk.Label(self.form, text="", bg=BG, font=F["bold"], anchor="w")
                mark.grid(row=i, column=2, sticky="w")
                self.entries[key], self.marks[key] = var, mark
            self.form.grid_columnconfigure(2, weight=1)
            self.steps = steps
            self.panel.set_steps(steps, shown=0)
            self.result.configure(text="")
            self.counter.configure(text="")
            first = next(iter(self.entries.values()), None)
            if first is not None:
                list(self.form.winfo_children())[1].focus_set()

        # -- actions ---------------------------------------------------------------
        def check(self):
            pr = self.problem
            good = 0
            for label, key in pr["fields"]:
                raw = self.entries[key].get().strip()
                exp = pr["expect"][key]
                if key == "mask" and pr["kind"] == "clsm":
                    ok = raw.lstrip("/").isdigit() and f"/{int(raw.lstrip('/'))}" == exp
                else:
                    ok = norm_ip(raw) == exp
                good += ok
                self.marks[key].configure(text="correct" if ok else ("blank" if not raw else f"no (it's {exp})"), fg=GOOD if ok else BAD)
            total = len(pr["fields"])
            record(pr["key"], good == total)
            self.result.configure(text=("All right!  Press 'Next problem'." if good == total else f"{good} of {total} right. Use 'Hint' for the next step of the method."),
                                  fg=GOOD if good == total else HOST)
            if good == total:
                self.panel.show_all()

        def hint(self):
            self.panel.forward()

        def solution(self):
            self.panel.show_all()
            for label, key in self.problem["fields"]:
                if not self.entries[key].get().strip():
                    self.marks[key].configure(text=f"it's {self.problem['expect'][key]}", fg=MUTED)

        def in_lab(self):
            pr = self.problem
            if pr["kind"] == "cidr":
                self.app.open_lab({"lab": "subnet", "arg": None, "args": {"ip": pr["ip"], "prefix": pr["prefix"]}})
            else:
                self.app.open_lab({"lab": "clsm", "arg": None, "args": {"base": pr["base"], "bp": pr["bp"], "n": pr["n"], "hosts": pr["hosts"]}})



    # ===========================================================================
    # MAIN APP: shell, home, chapter quizzes, learning panel, results
    # ===========================================================================
    SHORT_MOD = {"1": "Module 1", "2": "Module 2", "3": "Module 3", "4": "Module 4", "6": "Module 6", "7": "Module 7",
                 "8": "Module 8", "12": "Module 12", "L": "Lectures"}
    KIND_LABEL = {"mc": "multiple choice", "tf": "true / false", "multi": "select all that apply"}


    class App:
        def __init__(self):
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
            self.root = tk.Tk()
            self.root.title("IS 4440 - Networking & Servers Midterm Trainer")
            self.root.geometry("1180x900")
            self.root.minsize(900, 680)
            self.root.report_callback_exception = self._report
            APP["root"] = self.root
            apply_palette(system_theme())
            make_fonts(self.root)
            style_app(self.root)
            self.mode, self.frame, self.scroller = "home", None, None
            self.wrap_labels, self.card_labels = [], []
            self.cheat, self.lab = None, None
            self.shuffle_q = tk.BooleanVar(value=True)
            self.shuffle_c = tk.BooleanVar(value=True)
            self.exam_n = tk.IntVar(value=70)
            self.exam_back = tk.BooleanVar(value=True)
            self.clock_lbl, self._clock_job, self.exam_end = None, None, None
            self.items, self.i, self.answered = [], 0, False
            self.source_stats = {}
            self.root.bind("<Key>", self._on_key)
            self.root.bind("<F2>", lambda e: self.open_lab())
            self.root.bind("<F3>", lambda e: self.open_cheat(self.cheat_tab_for(self.current_q())))
            self.root.bind("<Control-equal>", lambda e: resize_fonts(1))
            self.root.bind("<Control-plus>", lambda e: resize_fonts(1))
            self.root.bind("<Control-minus>", lambda e: resize_fonts(-1))
            self.root.bind("<Configure>", self._on_resize)
            self.root.bind_all("<MouseWheel>", self._wheel)
            self.root.bind_all("<Button-4>", lambda e: self._wheel(e, 1))
            self.root.bind_all("<Button-5>", lambda e: self._wheel(e, -1))
            self.show_home()

        # --- shell helpers -------------------------------------------------------
        def _report(self, exc, val, tb):
            import traceback
            detail = "".join(traceback.format_exception(exc, val, tb))
            try:
                messagebox.showerror("Something went wrong", "The app hit an unexpected error but is still running.\n\n" + detail[-1500:])
            except Exception:
                pass

        def _wheel(self, e, direction=None):
            sc = self.scroller
            if sc is None or not sc.winfo_exists():
                return
            w = self.root.winfo_containing(e.x_root, e.y_root)
            if w is None or isinstance(w, (tk.Text, ttk.Treeview, tk.Listbox, ttk.Combobox)) or not str(w).startswith(str(sc)):
                return
            sc.scroll(direction * -1 if direction else int(-e.delta / 120))

        def theme_button(self, parent):
            btn = ttk.Button(parent, text=theme_button_text(), command=self.toggle_theme)
            btn._theme_btn = True
            return btn

        def toggle_theme(self):
            set_theme(self.root, "light" if CURRENT["name"] == "dark" else "dark")

        def clear(self, scroll=False):
            if self.frame is not None:
                self.frame.destroy()
            self.frame = ttk.Frame(self.root, padding=(24, 16))
            self.frame.pack(fill="both", expand=True)
            self.wrap_labels, self.card_labels, self.scroller = [], [], None
            self.clock_lbl = None
            if scroll:
                self.frame.configure(padding=0)
                sf = ScrollFrame(self.frame)
                sf.pack(fill="both", expand=True)
                self.scroller = sf
                return sf.body
            return self.frame

        def wlabel(self, parent, text, font=None, fg=None, bg=None, **kw):
            lbl = tk.Label(parent, text=text, font=font or F["ui"], fg=fg or TEXT, bg=bg or BG, justify="left", anchor="w", **kw)
            self.wrap_labels.append(lbl)
            lbl.configure(wraplength=max(300, self.root.winfo_width() - 110))
            return lbl

        def _on_resize(self, e):
            if e.widget is self.root:
                for lbl in self.wrap_labels:
                    try:
                        lbl.configure(wraplength=max(300, e.width - 110))
                    except tk.TclError:
                        pass
                for lbl in self.card_labels:
                    try:
                        lbl.configure(wraplength=max(300, e.width - 190))
                    except tk.TclError:
                        pass

        def _typing(self):
            return isinstance(self.root.focus_get(), (tk.Text, tk.Entry, ttk.Entry, tk.Spinbox, ttk.Spinbox, ttk.Combobox))

        def _on_key(self, e):
            if self.mode == "flash" and not self._typing():
                if e.keysym == "space":
                    self.fc_flip()
                elif e.char.lower() == "y":
                    self.fc_grade(True)
                elif e.char.lower() == "n":
                    self.fc_grade(False)
                return
            if self.mode not in ("quiz", "exam") or self._typing():
                return
            q = self.current_q()
            if q is None:
                return
            ch = e.char.upper()
            if self.mode == "exam":
                if ch and ch in LETTERS[:len(self.cur_choices)]:
                    self.exam_select(LETTERS.index(ch))
                elif q["kind"] == "tf" and ch in ("T", "F"):
                    self.exam_select(0 if ch == "T" else 1)
                elif e.keysym == "Right":
                    self.exam_go(1)
                elif e.keysym == "Left":
                    self.exam_go(-1)
                return
            if not self.answered and q["kind"] == "tf" and ch in ("T", "F"):
                self.select(0 if ch == "T" else 1)
            elif not self.answered and ch and ch in LETTERS[:len(self.cur_choices)]:
                self.select(LETTERS.index(ch))
            elif e.keysym in ("Return", "KP_Enter"):
                (self.next_q if self.answered else self.submit)()

        def current_q(self):
            if self.mode == "exam" and getattr(self, "ex_items", None):
                return self.ex_items[self.ex_i]
            if self.items and 0 <= self.i < len(self.items):
                return self.items[self.i]
            return None

        def cheat_tab_for(self, q):
            for sk in (q or {}).get("skills", []):
                if sk in SKILL_TAB:
                    return SKILL_TAB[sk]
            return None

        def open_cheat(self, tab=None):
            if self.cheat is not None and self.cheat.winfo_exists():
                self.cheat.lift()
                self.cheat.focus_force()
                if tab:
                    self.cheat.select_tab(tab)
                return
            self.cheat = CheatSheet(self, tab)

        def open_lab(self, spec=None):
            """Open the labs. spec = {"lab": ..., "arg": ..., "args": {...}} (what lab_for returns); default = the current question's lab."""
            if spec is None:
                q = self.current_q() if self.mode in ("quiz", "exam") else None
                spec = lab_for(q) if q else None
            if self.lab is None or not self.lab.winfo_exists():
                self.lab = Lab(self)
            spec = spec or {"lab": "subnet", "arg": None, "args": {}}
            self.lab.open_tab(spec["lab"], spec.get("arg"), **(spec.get("args") or {}))

        # --- home --------------------------------------------------------------
        def show_home(self):
            self.mode = "home"
            self._stop_clock()
            f = self.clear(scroll=True)
            head = ttk.Frame(f)
            head.pack(fill="x")
            ttk.Label(head, text="IS 4440  -  Networking & Servers Midterm Trainer", font=F["h1"], foreground=HEAD).pack(side="left")
            self.theme_button(head).pack(side="right")
            self.wlabel(f, "Prof. Norwood's midterm: Network+ Modules 1, 2, 3, 4, 6, 7, 8 and 12 plus the frame, routing and subnetting lectures. "
                           "Press F2 for step-by-step labs and F3 for cheat sheets.", fg=MUTED).pack(fill="x", pady=(2, 8))
            opts = ttk.LabelFrame(f, text="Options", padding=10)
            opts.pack(fill="x")
            ttk.Checkbutton(opts, text="Shuffle question order", variable=self.shuffle_q).grid(row=0, column=0, sticky="w", padx=6)
            ttk.Checkbutton(opts, text="Shuffle answer letters", variable=self.shuffle_c).grid(row=0, column=1, sticky="w", padx=6)
            grid = ttk.Frame(f)
            grid.pack(fill="x", pady=(14, 4))
            for c in range(3):
                grid.columnconfigure(c, weight=1, uniform="a")
            n_tf = sum(1 for q in BANK if q["kind"] == "tf")
            items = [
                (f"Chapter Quizzes\n{len(BANK)} questions: pick modules and types", self.show_chapters),
                ("EXAM SIMULATION\n70 questions, Scantron-style sheet, 90-minute clock", self.show_exam_setup),
                ("Subnetting Gym\nfind network / mask / broadcast, CLSM, with hints", lambda: self.show_gym(0)),
                ("Professor's CIDR Sheet\nhis 9 CIDR + 7 CLSM problems, his order", lambda: self.show_gym(2)),
                ("Walk-through Labs\nsubnet, routing, frames, TCP, DHCP, DNS...  (F2)", self.open_lab),
                ("Routing Table Lab\nthe Logan router, longest prefix + metric", lambda: self.open_lab({"lab": "route", "arg": None, "args": {}})),
                ("Frame Traversal Lab\nwhat changes at every hop", lambda: self.open_lab({"lab": "frame", "arg": None, "args": {}})),
                ("Speed Drills\nports, OSI layers, masks, binary, hex", self.show_drills),
                (f"Flashcards\n{len(FLASHCARDS)} key terms", self.show_flashcards),
                (f"Study-Guide Checklist\nthe professor's {len(STUDY_GUIDE)} focus items, with practice", self.show_checklist),
                ("Weak Spots\nyour saved accuracy by module and skill", self.show_weak_spots),
                ("Cheat Sheets\nports, OSI, subnet tables, Wi-Fi, calculators  (F3)", self.open_cheat),
            ]
            for i, (txt, cmd) in enumerate(items):
                title, _, sub = txt.partition("\n")
                make_tile(grid, title, sub, f"B{i % 6 + 1}", cmd).grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            ttk.Label(f, text="PRACTICE BY SKILL  (drill what you mix up)", foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(10, 0))
            sgrid = ttk.Frame(f)
            sgrid.pack(fill="x", pady=(2, 8))
            for c in range(3):
                sgrid.columnconfigure(c, weight=1, uniform="s")
            for i, key in enumerate(SKILLS):
                cnt = sum(1 for q in BANK if key in q["skills"])
                make_tile(sgrid, SKILL_SHORT[key], f"{cnt} questions", f"B{(i + 3) % 6 + 1}",
                          lambda k=key: self.start_skill(k)).grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            ttk.Label(f, text="Tips:  F2 = labs   |   F3 = cheat sheets   |   A-D (or T / F) = pick an answer   |   Enter = submit / next   |   Ctrl +/- = text size",
                      foreground=MUTED).pack(anchor="w")
            self.wlabel(f, f"Who wrote what: only the professor's own material carries the purple PROFESSOR'S MATERIAL tag (his CIDR sheet, the Logan "
                           f"routing table and questions L-04 and L-05). The other {len(BANK)} bank questions carry a grey PRACTICE QUESTION tag: Claude wrote "
                           "them from the slides and textbook, in the style of his focus list, and none is copied from a real exam. Teal GENERATED PRACTICE "
                           "questions are made from random numbers, like the subnetting questions on the exam. VLSM is not tested, so it is not drilled.",
                        fg=MUTED).pack(fill="x", pady=(6, 0))
            self.wlabel(f, "Your accuracy is saved in one small file in your home folder so Weak Spots can track it. Nothing else is written "
                           "unless you click Save on a cheat sheet.", fg=MUTED).pack(fill="x", pady=(4, 0))

        # --- building quizzes ----------------------------------------------------
        def maybe_shuffle(self, pool):
            return random.sample(pool, len(pool)) if self.shuffle_q.get() else list(pool)

        def start_pool(self, pool, title):
            self.start_quiz(self.maybe_shuffle(pool), title)

        def start_skill(self, key):
            self.start_pool([q for q in BANK if key in q["skills"]], SKILLS[key])

        def show_chapters(self):
            self.mode = "chapters"
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Chapter Quizzes", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            self.wlabel(f, "Tick the modules to include. The real exam mixes multiple choice and true/false.", fg=MUTED).pack(fill="x", pady=(2, 8))
            self.ch_vars = {}
            for k in CHAPTERS:
                n = sum(1 for q in BANK if q["ch"] == k)
                v = tk.BooleanVar(value=True)
                self.ch_vars[k] = v
                ttk.Checkbutton(f, text=f"{CHAPTERS[k]}   ({n} questions)", variable=v).pack(anchor="w", pady=3)
            ttk.Label(f, text="Question types", foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(12, 2))
            self.kind_vars = {}
            for k, label in KIND_LABEL.items():
                v = tk.BooleanVar(value=True)
                self.kind_vars[k] = v
                ttk.Checkbutton(f, text=f"{label}   ({sum(1 for q in BANK if q['kind'] == k)})", variable=v).pack(anchor="w", pady=2)
            self.only_wrong = tk.BooleanVar(value=False)
            ttk.Checkbutton(f, text="Only questions I got wrong last time (from my saved history)", variable=self.only_wrong).pack(anchor="w", pady=(10, 2))
            ttk.Button(f, text="Start the quiz", style="Accent.TButton", command=self.start_chapters).pack(anchor="w", pady=14)

        def start_chapters(self):
            chosen = [k for k, v in self.ch_vars.items() if v.get()] or list(self.ch_vars)
            kinds = [k for k, v in self.kind_vars.items() if v.get()] or list(KIND_LABEL)
            pool = [q for q in BANK if q["ch"] in chosen and q["kind"] in kinds]
            if self.only_wrong.get():
                pool = [q for q in pool if (progress_of(q["id"]) or {}).get("last") is False]
            self.start_pool(pool, "Chapter quiz")

        def _stop_clock(self):
            if self._clock_job is not None:
                try:
                    self.root.after_cancel(self._clock_job)
                except Exception:
                    pass
            self._clock_job = None

        # --- the quiz ------------------------------------------------------------
        def start_quiz(self, items, title):
            if not items:
                messagebox.showinfo("Nothing to practice", "There are no questions for that selection.")
                return
            for it in items:
                it.setdefault("skills", skills_of(it))
            self.title_text = title
            self.items = list(items)
            self.i, self.score, self.answered_count = 0, 0, 0
            self.missed = []
            self.topic_stats, self.skill_stats, self.source_stats = {}, {}, {}
            self.review_picks, self.result_note = {}, ""
            self.started = time.time()
            self.show_question()

        def show_question(self):
            self.mode = "quiz"
            q = self.current_q()
            f = self.clear(scroll=True)
            self.answered, self.picks = False, set()
            choices = q["choices"][:]
            if self.shuffle_c.get() and q["kind"] != "tf":
                random.shuffle(choices)
            self.cur_choices = choices
            self.correct_idx = {i for i, c in enumerate(choices) if c in q["answer"]}
            info = ttk.Frame(f)
            info.pack(fill="x")
            ttk.Label(info, text=f"Question {self.i + 1} of {len(self.items)}   |   {q['id']}   |   {SHORT_MOD.get(q['ch'], q['ch'])}",
                      font=F["bold"], foreground=HEAD).pack(side="left")
            self.score_lbl = ttk.Label(info, text=self._score_text(), foreground=MUTED, font=F["bold"])
            self.score_lbl.pack(side="right")
            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=(6, 0))
            ttk.Button(bar, text="Walk-through  (F2)", style="Accent.TButton", command=self.open_lab).pack(side="right")
            ttk.Button(bar, text="Cheat sheets  (F3)", command=lambda: self.open_cheat(self.cheat_tab_for(q))).pack(side="right", padx=8)
            ttk.Button(bar, text="Home", command=self.confirm_home).pack(side="right")
            self.theme_button(bar).pack(side="right", padx=8)
            make_chip(f, q).pack(anchor="w", pady=(8, 0))
            self.wlabel(f, origin_note(q), fg=MUTED).pack(fill="x", pady=(6, 0))
            self.wlabel(f, f"Source: {q['src']}   |   {CHAPTERS.get(q['ch'], '')}   |   Skills: " + ", ".join(SKILL_SHORT[s] for s in q["skills"]),
                        fg=MUTED).pack(fill="x", pady=(2, 0))
            ttk.Separator(f).pack(fill="x", pady=8)
            self.wlabel(f, q["prompt"], font=F["h2"]).pack(fill="x", pady=(0, 8))
            if q["kind"] == "multi":
                self.wlabel(f, "Select ALL that apply, then press Submit.", fg=ACCENT, font=F["bold"]).pack(fill="x")
            elif q["kind"] == "tf":
                self.wlabel(f, "True or false?  (press T or F)", fg=ACCENT, font=F["bold"]).pack(fill="x")
            self.cards = []
            cf = ttk.Frame(f)
            cf.pack(fill="x", pady=10)
            for i, ch in enumerate(choices):
                card = tk.Frame(cf, bg=CARD, bd=1, relief="solid", cursor="hand2")
                card.pack(fill="x", pady=3)
                letter = tk.Label(card, text=LETTERS[i], font=F["h2"], bg=CARD, width=3, fg=ACCENT)
                letter.pack(side="left")
                body = tk.Label(card, text=ch, font=F["ui"], bg=CARD, fg=TEXT, justify="left", anchor="w",
                                wraplength=max(300, self.root.winfo_width() - 190))
                body.pack(side="left", fill="x", expand=True, pady=6)
                self.card_labels.append(body)
                for w in (card, letter, body):
                    w.bind("<Button-1>", lambda e, i=i: self.select(i))
                self.cards.append((card, letter, body))
            self.btn_row = ttk.Frame(f)
            self.btn_row.pack(fill="x", pady=4)
            self.submit_btn = ttk.Button(self.btn_row, text="Submit answer", style="Accent.TButton", command=self.submit, state="disabled")
            self.submit_btn.pack(side="left")
            ttk.Button(self.btn_row, text="Skip", command=self.skip).pack(side="left", padx=8)
            self.result_holder = ttk.Frame(f)
            self.result_holder.pack(fill="both", expand=True)

        def _score_text(self):
            return f"Score {self.score} / {self.answered_count}"

        def select(self, i):
            if self.answered:
                return
            q = self.current_q()
            if q["kind"] == "multi":
                self.picks ^= {i}
            else:
                self.picks = {i}
            for j, (card, letter, body) in enumerate(self.cards):
                col = SEL_BG if j in self.picks else CARD
                for w in (card, letter, body):
                    w.configure(bg=col)
            self.submit_btn.configure(state="normal" if self.picks else "disabled")

        def _color_cards(self):
            for j, (card, letter, body) in enumerate(self.cards):
                col = GOOD_BG if j in self.correct_idx else (BAD_BG if j in self.picks else CARD)
                for w in (card, letter, body):
                    w.configure(bg=col, cursor="arrow")

        def submit(self):
            if not self.answered and self.picks:
                self._finish_question(skipped=False)

        def skip(self):
            if not self.answered:
                self.picks = set()
                self._finish_question(skipped=True)

        def _section(self, parent, title):
            ttk.Label(parent, text=title, foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(12, 0))

        def _finish_question(self, skipped):
            q = self.current_q()
            self.answered = True
            for w in self.btn_row.winfo_children():
                w.destroy()
            correct = (not skipped) and self.picks == self.correct_idx
            letters = ", ".join(LETTERS[i] for i in sorted(self.correct_idx))
            self.review_picks[id(q)] = {"choices": self.cur_choices[:], "picks": set(self.picks)}
            if skipped:
                self.missed.append(q)
                msg, col = f"Skipped. The answer is {letters}.", MUTED
            else:
                self.answered_count += 1
                if correct:
                    self.score += 1
                    msg, col = "Correct!", GOOD
                else:
                    self.missed.append(q)
                    right_picked = len(self.picks & self.correct_idx)
                    msg = (f"Not quite. The answer is {letters}." if q["kind"] != "multi" else
                           f"Not quite: you found {right_picked} of {len(self.correct_idx)}. The answers are {letters}.")
                    col = BAD
                record(q["id"], correct)
            for key, table in (((q["ch"], self.topic_stats), (origin_of(q), self.source_stats)) + tuple((s, self.skill_stats) for s in q["skills"])):
                st = table.setdefault(key, [0, 0])
                st[1] += 1
                st[0] += 1 if correct else 0
            self.score_lbl.configure(text=self._score_text())
            self._color_cards()
            last = self.i == len(self.items) - 1
            tk.Label(self.btn_row, text=msg, font=F["h2"], fg=col, bg=BG, wraplength=700, justify="left").pack(side="left", padx=(0, 16))
            ttk.Button(self.btn_row, text="See results" if last else "Next  >", style="Accent.TButton", command=self.next_q).pack(side="left")
            if lab_for(q):
                ttk.Button(self.btn_row, text="Walk through it  (F2)", command=self.open_lab).pack(side="left", padx=8)
            tab = self.cheat_tab_for(q)
            if tab:
                ttk.Button(self.btn_row, text="Open the cheat sheet", command=lambda: self.open_cheat(tab)).pack(side="left")
            self.learning_panel(self.result_holder, q, self.picks, self.cur_choices, correct, skipped)

        def learning_panel(self, rf, q, picks, choices, correct, skipped, show_solution=True):
            """Why the right answer is right, what the picked option actually is, other options, key terms."""
            correct_idx = {i for i, c in enumerate(choices) if c in q["answer"]}
            self._section(rf, "WHY THE RIGHT ANSWER IS RIGHT")
            self.wlabel(rf, "Answer: " + "  |  ".join(q["answer"]), font=F["bold"], fg=GOOD).pack(fill="x", pady=(2, 0))
            self.wlabel(rf, q["why"]).pack(fill="x")
            if show_solution:
                self._solution_panel(rf, q)
            if not correct and not skipped:
                picked = [choices[i] for i in sorted(picks)]
                if q["kind"] == "multi":
                    missed, extra = multi_feedback(q, picked)
                    self._section(rf, "WHAT YOU GOT WRONG")
                    if missed:
                        self.wlabel(rf, "You missed:  " + "  |  ".join(missed), fg=BAD).pack(fill="x")
                    for ch, note in diagnose(q, picked):
                        self.wlabel(rf, "You also chose:  " + ch, fg=BAD, font=F["bold"]).pack(fill="x", pady=(4, 0))
                        self.wlabel(rf, note or "That option isn't one of the correct answers (see the explanation above).", fg=MUTED).pack(fill="x")
                elif picked:
                    self._section(rf, f"WHY YOUR ANSWER ({LETTERS[min(picks)]}) ISN'T RIGHT")
                    self.wlabel(rf, "You picked:  " + picked[0], font=F["bold"], fg=BAD).pack(fill="x")
                    d = diagnose(q, picked)
                    note = d[0][1] if d else ""
                    self.wlabel(rf, ("What that is: " + note) if note else "Compare it with the correct answer and the explanation above.").pack(fill="x", pady=(2, 0))
            others = [(i, ch) for i, ch in enumerate(choices) if i not in correct_idx and i not in picks and q["kind"] != "tf"]
            reasons = [(i, ch, note_for(q, ch)) for i, ch in others]
            reasons = [r for r in reasons if r[2]]
            if reasons:
                holder = ttk.Frame(rf)
                state = {"open": False}
                btn = ttk.Button(rf, text="Show what the other options are")

                def toggle():
                    if state["open"]:
                        holder.pack_forget()
                        btn.configure(text="Show what the other options are")
                    else:
                        if not holder.winfo_children():
                            for i, ch, why in reasons:
                                self.wlabel(holder, f"{LETTERS[i]})  " + ch, font=F["bold"]).pack(fill="x", pady=(6, 0))
                                self.wlabel(holder, why, fg=MUTED).pack(fill="x")
                        holder.pack(fill="x", pady=4)
                        btn.configure(text="Hide the other options")
                    state["open"] = not state["open"]
                btn.configure(command=toggle)
                btn.pack(anchor="w", pady=(12, 0))
            cards = related_flashcards(q)
            if cards:
                self._section(rf, "KEY TERMS TO REVIEW")
                for term, defn in cards:
                    self.wlabel(rf, term, font=F["bold"], fg=HEAD).pack(fill="x", pady=(4, 0))
                    self.wlabel(rf, defn, fg=MUTED).pack(fill="x")

        def _solution_panel(self, rf, q):
            """Generated subnetting questions show their worked solution right under the answer."""
            spec = lab_for(q)
            if not spec or not q["id"].startswith("GEN-"):
                return
            a = spec["args"]
            if spec["lab"] == "subnet" and a.get("ip"):
                _, steps = cidr_steps(a["ip"], a["prefix"])
            elif spec["lab"] == "clsm" and a.get("base"):
                _, _, steps = clsm_steps(a["base"], a["bp"], a["n"], a["hosts"])
            else:
                return
            self._section(rf, "STEP-BY-STEP SOLUTION  (the professor's method)")
            panel = StepPanel(rf, height=min(14, 3 + sum(len(s["lines"]) + 1 for s in steps)))
            panel.pack(fill="x", pady=(2, 0))
            panel.set_steps(steps, shown=len(steps))

        def next_q(self):
            if not self.answered:
                return
            if self.i >= len(self.items) - 1:
                self.show_results()
            else:
                self.i += 1
                self.show_question()

        def confirm_home(self):
            if messagebox.askyesno("Leave?", "Go back to the home screen? Your progress in this session will be lost."):
                self.show_home()

        # --- results -------------------------------------------------------------
        def show_results(self):
            self._stop_clock()
            self.mode = "results"
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Results", font=F["h1"], foreground=HEAD).pack(side="left")
            self.theme_button(top).pack(side="right")
            if self.answered_count:
                pct = round(100 * self.score / self.answered_count)
                ttk.Label(f, text=f"{self.score} / {self.answered_count} answered correctly  ({pct}%)", font=F["h2"]).pack(anchor="w", pady=6)
            ttk.Label(f, text=f"Time: {(time.time() - self.started) / 60:.1f} minutes", foreground=MUTED).pack(anchor="w")
            if getattr(self, "result_note", ""):
                self.wlabel(f, self.result_note, fg=MUTED).pack(fill="x", pady=(2, 0))
            weak = []
            sources = {"prof": "Professor's material", "gen": "Generated practice", "claude": "Practice questions (written by Claude)"}
            for title, stats, names, bad_keys in (("BY SOURCE", self.source_stats, sources, None),
                                                  ("BY MODULE", self.topic_stats, CHAPTERS, None),
                                                  ("BY SKILL  (red = your weak spots)", self.skill_stats, SKILLS, weak)):
                if not stats:
                    continue
                ttk.Label(f, text=title, foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(10, 2))
                for key in names:
                    if key not in stats:
                        continue
                    good, total = stats[key]
                    low = good / total < 0.75
                    if low and bad_keys is not None:
                        bad_keys.append(key)
                    tk.Label(f, text=f"{good}/{total}   {names[key].split(' (')[0]}", font=F["ui"], bg=BG, anchor="w",
                             fg=GOOD if good == total else (BAD if low else TEXT)).pack(fill="x")
            ttk.Label(f, text="MISSED OR SKIPPED  (double-click one to review it)", foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(12, 2))
            tree = ttk.Treeview(f, columns=("t", "p"), show="headings", height=8)
            tree.heading("t", text="Question")
            tree.heading("p", text="Prompt")
            tree.column("t", width=110, stretch=False)
            tree.column("p", width=700)
            for idx, q in enumerate(self.missed):
                tree.insert("", "end", iid=str(idx), values=(q["id"], q["prompt"].split("\n")[0][:120]))
            tree.pack(fill="x")

            def review(_=None):
                sel = tree.selection()
                if sel:
                    self.show_review(self.missed, int(sel[0]))
            tree.bind("<Double-1>", review)
            row = ttk.Frame(f)
            row.pack(fill="x", pady=12)
            if self.missed:
                ttk.Button(row, text="Review the selected one", style="Accent.TButton", command=review).pack(side="left")
                ttk.Button(row, text="Retry missed questions",
                           command=lambda: self.start_quiz(self.maybe_shuffle(self.missed[:]), "Retry")).pack(side="left", padx=8)
            if weak:
                ttk.Button(row, text="Practice my weak skills",
                           command=lambda: self.start_pool([q for q in BANK if any(k in q["skills"] for k in weak)], "Weak skills")).pack(side="left")
            ttk.Button(row, text="Home", command=self.show_home).pack(side="right")

        def show_review(self, qs, idx, back=None):
            """Read-only review of one question: your last answer vs the right one, with the full learning panel."""
            self.mode = "review"
            q = qs[idx]
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text=f"Review {idx + 1} of {len(qs)}   |   {q['id']}   |   {SHORT_MOD.get(q['ch'], q['ch'])}", font=F["bold"],
                      foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Back to results", command=back or self.show_results).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            row = ttk.Frame(f)
            row.pack(fill="x", pady=(6, 0))
            make_chip(row, q).pack(side="left")
            ttk.Button(row, text="Walk through it  (F2)", style="Accent.TButton", command=lambda: self.open_lab(lab_for(q))).pack(side="right")
            ttk.Button(row, text="Cheat sheet", command=lambda: self.open_cheat(self.cheat_tab_for(q))).pack(side="right", padx=8)
            self.wlabel(f, origin_note(q), fg=MUTED).pack(fill="x", pady=(6, 0))
            ttk.Separator(f).pack(fill="x", pady=8)
            self.wlabel(f, q["prompt"], font=F["h2"]).pack(fill="x", pady=(0, 8))
            mine = getattr(self, "review_picks", {}).get(id(q))
            choices = (mine or {}).get("choices", q["choices"])
            picks = (mine or {}).get("picks", set())
            for i, ch in enumerate(choices):
                good = ch in q["answer"]
                card = tk.Frame(f, bg=GOOD_BG if good else (BAD_BG if i in picks else CARD), bd=1, relief="solid")
                card.pack(fill="x", pady=3)
                tk.Label(card, text=LETTERS[i], font=F["h2"], bg=card.cget("bg"), width=3, fg=ACCENT).pack(side="left")
                lab = tk.Label(card, text=ch + ("      <- your answer" if i in picks else ""), font=F["ui"], bg=card.cget("bg"), fg=TEXT,
                               justify="left", anchor="w", wraplength=max(300, self.root.winfo_width() - 190))
                lab.pack(side="left", fill="x", expand=True, pady=6)
                self.card_labels.append(lab)
            correct = bool(picks) and {choices[i] for i in picks} == set(q["answer"])
            self.learning_panel(f, q, picks, choices, correct, not picks)
            nav = ttk.Frame(f)
            nav.pack(fill="x", pady=14)
            if idx > 0:
                ttk.Button(nav, text="< Previous", command=lambda: self.show_review(qs, idx - 1, back)).pack(side="left")
            if idx < len(qs) - 1:
                ttk.Button(nav, text="Next  >", style="Accent.TButton", command=lambda: self.show_review(qs, idx + 1, back)).pack(side="left", padx=8)



        # ===========================================================================
        # EXAM SIMULATION: answer sheet like a Scantron, flag for review, clock, no feedback until you hand it in
        # ===========================================================================
        def show_exam_setup(self):
            self.mode = "examsetup"
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Exam Simulation", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            self.wlabel(f, "The real midterm (from the professor's study-guide slides): 65-75 multiple-choice and true/false questions on a paper "
                           "Scantron, in class, closed book, with blank scratch paper allowed. Subnetting appears as one problem giving a host "
                           "address and CIDR prefix (network ID, mask, broadcast) plus one longhand CLSM problem. VLSM is not tested.",
                        fg=MUTED).pack(fill="x", pady=(4, 6))
            self.wlabel(f, "Here: questions are weighted by module, 4 of them are generated subnetting problems, and nothing is graded or "
                           "explained until you hand the exam in. Use scratch paper for the subnetting, as you will on the day.").pack(fill="x", pady=(0, 10))
            row = ttk.Frame(f)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text="Number of questions:").pack(side="left", padx=(0, 6))
            ttk.Spinbox(row, from_=20, to=75, width=5, textvariable=self.exam_n, font=F["ui"], command=self._exam_time_label).pack(side="left")
            self.exam_n.trace_add("write", lambda *a: self._exam_time_label())
            self.time_lbl = tk.Label(f, text="", bg=BG, fg=TEXT, font=F["bold"], anchor="w", justify="left")
            self.time_lbl.pack(fill="x", pady=(6, 0))
            self.wlabel(f, "Time rule: fewer than 70 questions = 80 minutes, more than 70 = 90 minutes. Exactly 70 isn't stated, so this "
                           "simulation gives the longer 90.", fg=MUTED).pack(fill="x")
            ttk.Checkbutton(f, text="Let me go back and change answers (a paper Scantron lets you)", variable=self.exam_back).pack(anchor="w", pady=10)
            ttk.Button(f, text="Start the exam", style="Accent.TButton", command=self.start_exam).pack(anchor="w", pady=6)
            self._exam_time_label()

        def _exam_time_label(self):
            try:
                n = max(20, min(75, int(self.exam_n.get())))
            except (tk.TclError, ValueError):
                n = 70
            if getattr(self, "time_lbl", None) is not None and self.time_lbl.winfo_exists():
                self.time_lbl.configure(text=f"{n} questions  ->  time limit {exam_minutes(n)} minutes")

        def start_exam(self):
            try:
                n = max(20, min(75, int(self.exam_n.get())))
            except (tk.TclError, ValueError):
                n = 70
            items = build_exam(n)
            for it in items:
                it.setdefault("skills", skills_of(it))
            self.ex_items = items
            self.ex_choices = []
            for q in items:
                ch = q["choices"][:]
                if self.shuffle_c.get() and q["kind"] != "tf":
                    random.shuffle(ch)
                self.ex_choices.append(ch)
            self.ex_picks = [set() for _ in items]
            self.ex_flags, self.ex_i, self.ex_minutes = set(), 0, exam_minutes(n)
            self.ex_start = time.time()
            self.exam_end = self.ex_start + self.ex_minutes * 60
            self._time_up_shown = False
            self.show_exam_question()

        def _add_clock(self, parent):
            self.clock_lbl = tk.Label(parent, text="", font=F["h2"], bg=BG, fg=TEXT)
            self.clock_lbl.pack(side="right", padx=14)
            self._stop_clock()
            self._tick_clock()

        def _tick_clock(self):
            self._clock_job = None
            if self.exam_end is None or self.mode != "exam":
                return
            left = self.exam_end - time.time()
            if self.clock_lbl is not None and self.clock_lbl.winfo_exists():
                if left > 0:
                    m, s = divmod(int(left), 60)
                    self.clock_lbl.configure(text=f"Time left {m:02d}:{s:02d}", fg=BAD if left < 600 else TEXT)
                else:
                    self.clock_lbl.configure(text="TIME'S UP", fg=BAD)
            if left <= 0 and not self._time_up_shown:
                self._time_up_shown = True
                messagebox.showinfo("Time's up", f"The {self.ex_minutes} minutes are over. On the real exam you would hand it in now; "
                                                 "you can keep going to finish the practice.")
            self._clock_job = self.root.after(1000, self._tick_clock)

        def show_exam_question(self):
            self.mode = "exam"
            i = self.ex_i
            q = self.ex_items[i]
            self.cur_choices = self.ex_choices[i]
            f = self.clear(scroll=True)
            info = ttk.Frame(f)
            info.pack(fill="x")
            ttk.Label(info, text=f"Question {i + 1} of {len(self.ex_items)}", font=F["h2"], foreground=HEAD).pack(side="left")
            self._add_clock(info)
            bar = ttk.Frame(f)
            bar.pack(fill="x", pady=(6, 0))
            ttk.Button(bar, text="Finish exam", style="Accent.TButton", command=self.finish_exam).pack(side="right")
            ttk.Button(bar, text="Walk-through  (F2)", command=lambda: self.open_lab(lab_for(q))).pack(side="right", padx=8)
            ttk.Button(bar, text="Cheat sheets  (F3)", command=lambda: self.open_cheat(self.cheat_tab_for(q))).pack(side="right")
            self.theme_button(bar).pack(side="right", padx=8)
            make_chip(f, q).pack(anchor="w", pady=(8, 0))
            self.wlabel(f, "Exam mode: nothing is graded or explained until you finish. (F2 and F3 are for use after you hand it in, or to peek and give up the points.)",
                        fg=MUTED).pack(fill="x", pady=(6, 0))
            # answer sheet
            self.wlabel(f, "ANSWER SHEET  (blue = answered, orange = flagged, outlined = this one)", fg=MUTED, font=F["bold"]).pack(fill="x", pady=(8, 2))
            sheet = tk.Frame(f, bg=BG)
            sheet.pack(fill="x")
            self.sheet_cells = []
            cols = 15
            for k in range(len(self.ex_items)):
                lab = tk.Label(sheet, text=str(k + 1), font=F["bold"], width=3, bd=2, relief="solid", cursor="hand2")
                lab.grid(row=k // cols, column=k % cols, padx=2, pady=2, sticky="nsew")
                lab.bind("<Button-1>", lambda e, k=k: self.exam_jump(k))
                self.sheet_cells.append(lab)
            self._paint_sheet()
            ttk.Separator(f).pack(fill="x", pady=8)
            self.wlabel(f, q["prompt"], font=F["h2"]).pack(fill="x", pady=(0, 8))
            if q["kind"] == "multi":
                self.wlabel(f, "Select ALL that apply.", fg=ACCENT, font=F["bold"]).pack(fill="x")
            self.cards = []
            cf = ttk.Frame(f)
            cf.pack(fill="x", pady=8)
            for k, ch in enumerate(self.cur_choices):
                card = tk.Frame(cf, bg=CARD, bd=1, relief="solid", cursor="hand2")
                card.pack(fill="x", pady=3)
                letter = tk.Label(card, text=LETTERS[k], font=F["h2"], bg=CARD, width=3, fg=ACCENT)
                letter.pack(side="left")
                body = tk.Label(card, text=ch, font=F["ui"], bg=CARD, fg=TEXT, justify="left", anchor="w", wraplength=max(300, self.root.winfo_width() - 190))
                body.pack(side="left", fill="x", expand=True, pady=6)
                self.card_labels.append(body)
                for w in (card, letter, body):
                    w.bind("<Button-1>", lambda e, k=k: self.exam_select(k))
                self.cards.append((card, letter, body))
            self._paint_cards()
            nav = ttk.Frame(f)
            nav.pack(fill="x", pady=8)
            back_ok = self.exam_back.get()
            ttk.Button(nav, text="< Previous", command=lambda: self.exam_go(-1), state="normal" if (back_ok and i > 0) else "disabled").pack(side="left")
            ttk.Button(nav, text="Next  >", style="Accent.TButton", command=lambda: self.exam_go(1),
                       state="normal" if i < len(self.ex_items) - 1 else "disabled").pack(side="left", padx=8)
            self.flag_var = tk.BooleanVar(value=i in self.ex_flags)
            ttk.Checkbutton(nav, text="Flag this question for review", variable=self.flag_var, command=self.exam_flag).pack(side="left", padx=16)

        def _paint_sheet(self):
            for k, lab in enumerate(self.sheet_cells):
                answered = bool(self.ex_picks[k])
                flagged = k in self.ex_flags
                bg = FLAG if flagged else (ACCENT if answered else CARD)
                lab.configure(bg=bg, fg="#ffffff" if (answered or flagged) else TEXT, relief="solid", bd=3 if k == self.ex_i else 1)

        def _paint_cards(self):
            picks = self.ex_picks[self.ex_i]
            for k, (card, letter, body) in enumerate(self.cards):
                col = SEL_BG if k in picks else CARD
                for w in (card, letter, body):
                    w.configure(bg=col)

        def exam_select(self, k):
            if self.mode != "exam" or k >= len(self.cur_choices):
                return
            q = self.ex_items[self.ex_i]
            if q["kind"] == "multi":
                self.ex_picks[self.ex_i] ^= {k}
            else:
                self.ex_picks[self.ex_i] = {k}
            self._paint_cards()
            self._paint_sheet()

        def exam_flag(self):
            (self.ex_flags.add if self.flag_var.get() else self.ex_flags.discard)(self.ex_i)
            self._paint_sheet()

        def exam_go(self, delta):
            if self.mode != "exam":
                return
            if delta < 0 and not self.exam_back.get():
                return
            j = self.ex_i + delta
            if 0 <= j < len(self.ex_items):
                self.ex_i = j
                self.show_exam_question()

        def exam_jump(self, k):
            if self.mode == "exam" and (self.exam_back.get() or k > self.ex_i):
                self.ex_i = k
                self.show_exam_question()

        def finish_exam(self):
            if self.mode != "exam":
                return
            blank = sum(1 for p in self.ex_picks if not p)
            msg = f"{blank} question(s) unanswered and {len(self.ex_flags)} flagged.\n\nHand in the exam and see your results?"
            if not messagebox.askyesno("Hand it in?", msg):
                return
            self._stop_clock()
            used = (time.time() - self.ex_start) / 60
            n = len(self.ex_items)
            self.items = self.ex_items
            self.missed, self.score, self.review_picks = [], 0, {}
            self.topic_stats, self.skill_stats, self.source_stats = {}, {}, {}
            for q, ch, picks in zip(self.ex_items, self.ex_choices, self.ex_picks):
                correct_idx = {k for k, c in enumerate(ch) if c in q["answer"]}
                correct = bool(picks) and picks == correct_idx
                self.review_picks[id(q)] = {"choices": ch, "picks": set(picks)}
                if picks:
                    record(q["id"], correct)
                if correct:
                    self.score += 1
                else:
                    self.missed.append(q)
                for key, table in (((q["ch"], self.topic_stats), (origin_of(q), self.source_stats)) + tuple((s, self.skill_stats) for s in q["skills"])):
                    st = table.setdefault(key, [0, 0])
                    st[1] += 1
                    st[0] += 1 if correct else 0
            self.answered_count = n
            over = used - self.ex_minutes
            self.started = self.ex_start
            self.result_note = (f"Exam: {n} questions, limit {self.ex_minutes} minutes" + (f" (you went {over:.0f} minute(s) over)" if over > 0 else "") +
                                f".  {blank} left blank count as wrong.")
            self.mode = "results"
            self.show_results()

        # ===========================================================================
        # SUBNETTING GYM
        # ===========================================================================
        def show_gym(self, tab=0):
            self.mode = "gym"
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Subnetting Gym", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            self.wlabel(f, "Solve each problem on scratch paper first (build Table 1 and Table 2 the way you will on the exam), type your answers, "
                           "and use Hint to reveal the method one step at a time. CIDR is enabled; usable hosts = 2^h - 2; VLSM isn't tested.",
                        fg=MUTED).pack(fill="x", pady=(2, 6))
            host = TabHost(f)
            host.pack(fill="both", expand=True)
            for title, mode in (("Network / mask / broadcast", "cidr"), ("CLSM (equal subnets)", "clsm"), ("Professor's sheet", "prof")):
                host.add(mode, title, ProblemPage(self, host.body, mode))
            host.select(("cidr", "clsm", "prof")[tab])

        # ===========================================================================
        # SPEED DRILLS
        # ===========================================================================
        def show_drills(self):
            self.mode = "drills"
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Speed Drills", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            self.wlabel(f, "Rapid-fire typed answers. Type and press Enter; press Enter again for the next one.", fg=MUTED).pack(fill="x", pady=(2, 8))
            self.drill_set = tk.StringVar(value=list(DRILL_SETS)[0])
            self.drill_n = tk.IntVar(value=15)
            row = ttk.Frame(f)
            row.pack(fill="x", pady=4)
            ttk.Label(row, text="Drill:").pack(side="left", padx=(0, 6))
            ttk.Combobox(row, state="readonly", width=30, textvariable=self.drill_set, values=list(DRILL_SETS) + ["Everything (mixed)"], font=F["ui"]).pack(side="left")
            ttk.Label(row, text="  How many:").pack(side="left")
            ttk.Spinbox(row, from_=5, to=60, width=4, textvariable=self.drill_n, font=F["ui"]).pack(side="left", padx=6)
            ttk.Button(row, text="Start", style="Accent.TButton", command=self.start_drill).pack(side="left", padx=8)
            self.drill_body = ttk.Frame(f)
            self.drill_body.pack(fill="both", expand=True, pady=10)

        def start_drill(self):
            name = self.drill_set.get()
            kinds = [k for ks in DRILL_SETS.values() for k in ks] if name.startswith("Everything") else DRILL_SETS.get(name, ["hosts"])
            try:
                n = max(5, min(60, int(self.drill_n.get())))
            except (tk.TclError, ValueError):
                n = 15
            self.dr = {"kinds": kinds, "n": n, "k": 0, "right": 0, "streak": 0, "best": 0, "wrong": [], "state": "ask"}
            self.mode = "drills"
            self._drill_next()

        def _drill_next(self):
            d = self.dr
            for w in self.drill_body.winfo_children():
                w.destroy()
            if d["k"] >= d["n"]:
                ttk.Label(self.drill_body, text=f"Done: {d['right']} / {d['n']} right   (best streak {d['best']})", font=F["h2"]).pack(anchor="w", pady=8)
                if d["wrong"]:
                    ttk.Label(self.drill_body, text="Ones to review:", foreground=MUTED, font=F["bold"]).pack(anchor="w")
                    for p, a in d["wrong"][:25]:
                        self.wlabel(self.drill_body, f"{p}   ->   {a}", fg=BAD).pack(fill="x")
                ttk.Button(self.drill_body, text="Go again", style="Accent.TButton", command=self.start_drill).pack(anchor="w", pady=10)
                return
            d["cur"] = make_drill(random.choice(d["kinds"]))
            d["state"] = "ask"
            ttk.Label(self.drill_body, text=f"{d['k'] + 1} of {d['n']}      right {d['right']}      streak {d['streak']}", foreground=MUTED, font=F["bold"]).pack(anchor="w")
            self.wlabel(self.drill_body, d["cur"]["prompt"], font=F["h2"]).pack(fill="x", pady=(8, 6))
            self.drill_var = tk.StringVar()
            ent = ttk.Entry(self.drill_body, textvariable=self.drill_var, width=30, font=F["h2"])
            ent.pack(anchor="w")
            ent.focus_set()
            ent.bind("<Return>", self._drill_enter)
            self.drill_fb = tk.Label(self.drill_body, text="", bg=BG, font=F["h2"], anchor="w")
            self.drill_fb.pack(fill="x", pady=8)

        def _drill_enter(self, _=None):
            d = self.dr
            if d["state"] == "ask":
                cur = d["cur"]
                ok = check_drill(cur, self.drill_var.get())
                record("DRILL-" + cur["kind"], ok)
                d["state"] = "shown"
                d["k"] += 1
                if ok:
                    d["right"] += 1
                    d["streak"] += 1
                    d["best"] = max(d["best"], d["streak"])
                    self.drill_fb.configure(text="Correct", fg=GOOD)
                else:
                    d["streak"] = 0
                    d["wrong"].append((cur["prompt"], cur["answer"]))
                    self.drill_fb.configure(text=f"Not quite: {cur['answer']}", fg=BAD)
            else:
                self._drill_next()



        # ===========================================================================
        # FLASHCARDS
        # ===========================================================================
        def show_flashcards(self, only_new=None):
            self.mode = "flash"
            known = known_cards()
            if only_new is None:
                only_new = self.fc_only_new.get() if hasattr(self, "fc_only_new") else False
            deck = [(t, d) for t, d in FLASHCARDS if not (only_new and t in known)]
            random.shuffle(deck)
            self.fc_deck, self.fc_i, self.fc_shown, self.fc_missed = deck, 0, False, []
            self.fc_only_new_flag = only_new
            self._draw_flash()

        def _draw_flash(self):
            f = self.clear()
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Flashcards", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            known = known_cards()
            ttk.Label(f, text=f"{len(known)} of {len(FLASHCARDS)} cards marked as known (saved).   Keys: Space = reveal,  Y = I knew it,  N = not yet",
                      foreground=MUTED).pack(anchor="w", pady=(2, 8))
            var = tk.BooleanVar(value=self.fc_only_new_flag)
            self.fc_only_new = var
            ttk.Checkbutton(f, text="Only cards I haven't mastered", variable=var, command=lambda: self.show_flashcards(only_new=var.get())).pack(anchor="w")
            if self.fc_i >= len(self.fc_deck):
                self.wlabel(f, f"Deck finished!  {len(self.fc_deck) - len(self.fc_missed)} known, {len(self.fc_missed)} to review.", font=F["h2"]).pack(fill="x", pady=20)
                if self.fc_missed:
                    ttk.Button(f, text="Go through the ones I missed", style="Accent.TButton", command=self._flash_retry).pack(anchor="w")
                ttk.Button(f, text="Shuffle and start again", command=lambda: self.show_flashcards(only_new=var.get())).pack(anchor="w", pady=8)
                return
            term, defn = self.fc_deck[self.fc_i]
            self.wlabel(f, f"Card {self.fc_i + 1} of {len(self.fc_deck)}", fg=MUTED).pack(fill="x", pady=(14, 0))
            card = tk.Frame(f, bg=CARD, bd=1, relief="solid", padx=24, pady=26)
            card.pack(fill="x", pady=10)
            t = tk.Label(card, text=term, font=F["h1"], bg=CARD, fg=HEAD, justify="left", anchor="w", wraplength=900)
            t.pack(fill="x")
            self.card_labels.append(t)
            self.fc_def = tk.Label(card, text="(try to say the definition out loud first)", font=F["ui"], bg=CARD, fg=MUTED, justify="left",
                                   anchor="w", wraplength=900)
            self.fc_def.pack(fill="x", pady=(14, 0))
            self.card_labels.append(self.fc_def)
            self.fc_card_defn = defn
            row = ttk.Frame(f)
            row.pack(fill="x", pady=8)
            self.fc_flip_btn = ttk.Button(row, text="Show the definition  (Space)", style="Accent.TButton", command=self.fc_flip)
            self.fc_flip_btn.pack(side="left")
            self.fc_yes = ttk.Button(row, text="I knew it  (Y)", command=lambda: self.fc_grade(True), state="disabled")
            self.fc_no = ttk.Button(row, text="Not yet  (N)", command=lambda: self.fc_grade(False), state="disabled")
            self.fc_yes.pack(side="left", padx=8)
            self.fc_no.pack(side="left")
            self.fc_shown = False

        def fc_flip(self):
            if self.mode != "flash" or self.fc_i >= len(self.fc_deck) or self.fc_shown:
                return
            self.fc_shown = True
            self.fc_def.configure(text=self.fc_card_defn, fg=TEXT)
            self.fc_yes.configure(state="normal")
            self.fc_no.configure(state="normal")
            self.fc_flip_btn.configure(state="disabled")

        def fc_grade(self, knew):
            if self.mode != "flash" or self.fc_i >= len(self.fc_deck) or not self.fc_shown:
                return
            term = self.fc_deck[self.fc_i][0]
            set_card_known(term, knew)
            if not knew:
                self.fc_missed.append(self.fc_deck[self.fc_i])
            self.fc_i += 1
            self._draw_flash()

        def _flash_retry(self):
            self.fc_deck, self.fc_i, self.fc_missed = self.fc_missed[:], 0, []
            self._draw_flash()

        # ===========================================================================
        # STUDY-GUIDE CHECKLIST (the professor's focus list), each item with practice
        # ===========================================================================
        def show_checklist(self):
            self.mode = "checklist"
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="The professor's study-guide checklist", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            marks = checklist_marks()
            self.wlabel(f, "From his 'Midterm Preparations' slides. Tick what you know; press Practice for questions on that item. "
                           "Your ticks are saved.", fg=MUTED).pack(fill="x", pady=(2, 6))
            self.check_count = tk.Label(f, text="", bg=BG, fg=TEXT, font=F["bold"], anchor="w")
            self.check_count.pack(fill="x", pady=(0, 6))
            self.check_vars = []
            for i, (item, chs) in enumerate(STUDY_GUIDE):
                row = ttk.Frame(f)
                row.pack(fill="x", pady=1)
                v = tk.BooleanVar(value=bool(marks.get(str(i))))
                self.check_vars.append(v)
                ttk.Checkbutton(row, text=item, variable=v, command=lambda i=i: self._tick(i)).pack(side="left")
                ttk.Button(row, text="Practice", command=lambda i=i: self.practice_item(i)).pack(side="right", padx=4)
                ttk.Label(row, text="Mod " + chs, foreground=MUTED).pack(side="right", padx=8)
            ttk.Button(f, text="Practice everything I haven't ticked", style="Accent.TButton", command=self.practice_unticked).pack(anchor="w", pady=12)
            self._update_check_count()

        def _tick(self, i):
            set_check(i, self.check_vars[i].get())
            self._update_check_count()

        def _update_check_count(self):
            done = sum(1 for v in self.check_vars if v.get())
            self.check_count.configure(text=f"{done} of {len(STUDY_GUIDE)} checked off")

        def practice_item(self, i):
            self.start_pool(study_questions(i), STUDY_GUIDE[i][0])

        def practice_unticked(self):
            pool, seen = [], set()
            for i, v in enumerate(self.check_vars):
                if not v.get():
                    for q in study_questions(i):
                        if q["id"] not in seen:
                            seen.add(q["id"])
                            pool.append(q)
            if not pool:
                messagebox.showinfo("All ticked", "Every item is ticked. Nice. Try the exam simulation.")
                return
            self.start_pool(pool, "Study-guide items I haven't ticked")

        # ===========================================================================
        # WEAK SPOTS (saved progress)
        # ===========================================================================
        def show_weak_spots(self):
            self.mode = "weak"
            f = self.clear(scroll=True)
            top = ttk.Frame(f)
            top.pack(fill="x")
            ttk.Label(top, text="Weak Spots", font=F["h1"], foreground=HEAD).pack(side="left")
            ttk.Button(top, text="Home", command=self.show_home).pack(side="right")
            self.theme_button(top).pack(side="right", padx=8)
            qprog = PROGRESS.get("q", {}) if isinstance(PROGRESS.get("q"), dict) else {}
            tried_q = [q for q in BANK if progress_of(q["id"])]
            extra = {k: v for k, v in qprog.items() if isinstance(v, dict) and v.get("tries") and not k[0].isdigit() and k[:2] != "L-"}
            if not tried_q and not extra:
                self.wlabel(f, "No history yet. Take a quiz or a drill first, then come back here to see your accuracy.", fg=MUTED).pack(fill="x", pady=10)
                return
            total = sum(progress_of(q["id"])["tries"] for q in tried_q) + sum(v["tries"] for v in extra.values())
            self.wlabel(f, f"Your accuracy across all sessions ({total} answers saved in {PROGRESS_FILE}).", fg=MUTED).pack(fill="x", pady=(2, 6))
            sections = [("BY MODULE", lambda q: [q["ch"]], CHAPTERS), ("BY SKILL", lambda q: q["skills"], SKILLS)]
            for title, key_of, names in sections:
                stats = accuracy_by(key_of, names)
                if not stats:
                    continue
                ttk.Label(f, text=title + "   (lowest first)", foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(10, 2))
                for k, (right, n) in sorted(stats.items(), key=lambda kv: kv[1][0] / kv[1][1]):
                    pct = 100 * right / n
                    bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
                    tk.Label(f, text=f"{pct:5.1f}%   {bar}   {names[k].split('(')[0].strip()[:42]}   ({n} tries)", font=F["code"], bg=BG, anchor="w",
                             fg=GOOD if pct >= 80 else (TEXT if pct >= 60 else BAD)).pack(fill="x")
            labels = {"SUB-cidr": "Subnet gym: network/mask/broadcast", "SUB-clsm": "Subnet gym: CLSM"}
            rows = []
            for k, v in extra.items():
                if k in labels or k.startswith(("PROF-", "DRILL-")):
                    name = labels.get(k) or ("Professor's sheet " + k[5:] if k.startswith("PROF-") else "Drill: " + k[6:])
                    rows.append((v["right"] / v["tries"] * 100, name, v["tries"]))
            if rows:
                ttk.Label(f, text="GYM AND DRILLS   (lowest first)", foreground=MUTED, font=F["bold"]).pack(anchor="w", pady=(10, 2))
                for pct, name, n in sorted(rows):
                    bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
                    tk.Label(f, text=f"{pct:5.1f}%   {bar}   {name[:42]}   ({n} tries)", font=F["code"], bg=BG, anchor="w",
                             fg=GOOD if pct >= 80 else (TEXT if pct >= 60 else BAD)).pack(fill="x")
            wrong = [q for q in tried_q if progress_of(q["id"]).get("last") is False]
            row = ttk.Frame(f)
            row.pack(fill="x", pady=14)
            self.wlabel(f, f"{len(wrong)} question(s) you got wrong the last time you saw them.", fg=MUTED).pack(fill="x")
            if wrong:
                ttk.Button(row, text="Drill those now", style="Accent.TButton", command=lambda: self.start_pool(wrong, "Weak Spots")).pack(side="left")
            ttk.Button(row, text="Reset my saved progress", command=self.reset_progress).pack(side="left", padx=8)

        def reset_progress(self):
            if messagebox.askyesno("Reset progress", "Erase all saved accuracy, flashcard and checklist progress?"):
                PROGRESS.clear()
                save_progress()
                self.show_weak_spots()

        def run(self):
            self.root.mainloop()



# ===========================================================================
# Entry point
# ===========================================================================
def entry():
    if sys.version_info < (3, 8):
        print("This trainer needs Python 3.8 or newer. You have " + sys.version.split()[0] + ".")
        return
    if not HAVE_TK:
        print("tkinter isn't available in this Python, so the window can't open. "
              "Reinstall Python from python.org and keep 'tcl/tk and IDLE' ticked.")
        return
    try:
        App().run()
    except tk.TclError as e:
        print(f"The window could not open ({e}).")


if __name__ == "__main__":
    entry()
