# Knowledge Crystal - Comprehensive Testing Guide

## 🧪 Complete Test Suite for Knowledge Crystal

This document provides comprehensive testing scenarios for all Knowledge Crystal functionality.

---

## Prerequisites

### 1. Start Required Services

```powershell
# Start Ollama
ollama serve

# Verify Ollama is running
curl http://localhost:11434/api/tags

# Pull the model if not already done
ollama pull llama3.2:3b

# Start MongoDB (verify it's running)
# Default: mongodb://localhost:27017

# Start Backend Server
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### 2. Base URL
All tests use: `http://localhost:8000/kb`

---

## Test Suite Overview

| Category | Tests | Status |
|----------|-------|--------|
| Health & Setup | 1 | ⬜ |
| Document Creation (Admin) | 5 | ⬜ |
| NLP Chat Interface | 8 | ⬜ |
| Semantic Search | 6 | ⬜ |
| Document Listing | 5 | ⬜ |
| Document Management | 4 | ⬜ |
| Access Control | 5 | ⬜ |
| Statistics & Analytics | 3 | ⬜ |
| Edge Cases | 6 | ⬜ |
| Performance Tests | 4 | ⬜ |

---

## 1. Health & Setup Tests

### Test 1.1: Health Check ✅

**Purpose**: Verify service is running with correct configuration

```bash
GET http://localhost:8000/kb/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "knowledge-crystal",
  "version": "2.0",
  "features": [
    "document_upload",
    "role_based_access_control",
    "nlp_chat_interface",
    "mission_document_library",
    "technical_documentation_center",
    "vector_embeddings",
    "semantic_search",
    "rag_qa_engine"
  ],
  "supported_roles": ["agent", "technician"],
  "document_categories": ["agent", "technician"]
}
```

**Validation**:
- ✅ Status is "healthy"
- ✅ Version is "2.0"
- ✅ All 8 features listed
- ✅ Both roles supported

---

## 2. Document Creation Tests (Admin Only)

### Test 2.1: Create Agent Mission Document ✅

**Purpose**: Create a mission document for agents

```bash
POST http://localhost:8000/kb/create
Content-Type: application/json

{
  "title": "Mission Report: Operation Phoenix - Germany",
  "content": "Operation Phoenix was conducted in Berlin, Germany from January 15-30, 2025. The mission objective was to secure the diplomatic facility during an international summit and protect the high-value target.\n\nTeam Composition:\n- 5 field agents deployed\n- 2 technical specialists\n- 1 communications officer\n\nEquipment Used:\n- Advanced surveillance systems\n- Secure encrypted communication devices\n- Biometric access control systems\n- Night vision equipment\n- Tactical gear\n\nKey Mission Phases:\n1. Reconnaissance (Jan 15-17): Mapped facility layout, identified entry/exit points, established safe houses\n2. Setup (Jan 18-20): Installed surveillance equipment, coordinated with local authorities\n3. Active Protection (Jan 21-28): 24/7 monitoring, threat assessment, perimeter security\n4. Extraction (Jan 29-30): Secure extraction of VIP, equipment recovery\n\nMission Outcomes:\n- Primary objective achieved: VIP protection successful\n- Zero security incidents reported\n- Diplomatic summit concluded safely\n- All team members returned safely\n\nLessons Learned:\n1. Local language skills proved invaluable for coordination\n2. Weather conditions (winter storms) required equipment adjustments\n3. Coordination with German federal police was excellent\n4. Safe house network in Berlin districts worked perfectly\n5. Secure communication protocols maintained throughout\n\nResources & Locations:\n- Safe House Alpha: Charlottenburg district (coordinates: 52.5200° N, 13.2905° E)\n- Safe House Bravo: Mitte district (coordinates: 52.5200° N, 13.4050° E)\n- Embassy coordination center\n- Local transport: BMW sedan fleet, public transit passes\n- Medical facility: Charité Hospital (emergency protocol established)\n\nRecommendations for Future Germany Operations:\n- Maintain existing safe house network\n- Continue partnership with German federal authorities\n- Stock cold-weather gear year-round\n- Establish backup communication channels\n- Brief team on German operational law and customs",
  "category": "agent",
  "mission_id": "MS-2025-001",
  "country": "Germany",
  "tags": ["mission", "completed", "2025", "europe", "diplomatic", "vip-protection"],
  "visibility": "public",
  "author": "admin",
  "metadata": {
    "department": "field-operations",
    "classification": "confidential",
    "team_lead": "Agent Red Ranger"
  }
}
```

**Expected Response**:
```json
{
  "message": "Knowledge page created successfully",
  "data": {
    "success": true,
    "page_id": "507f1f77bcf86cd799439011",
    "chunks_created": 8,
    "title": "Mission Report: Operation Phoenix - Germany",
    "created_at": "2025-12-08T10:30:00Z"
  }
}
```

**Validation**:
- ✅ Success status
- ✅ Valid page_id returned
- ✅ Chunks created (should be 6-10)
- ✅ Created timestamp present

### Test 2.2: Create Agent Mission Document - Japan ✅

```bash
POST http://localhost:8000/kb/create
Content-Type: application/json

{
  "title": "Mission Report: Operation Dragon Eye - Japan",
  "content": "Operation Dragon Eye was executed in Tokyo, Japan from March 5-20, 2025. Mission focused on corporate espionage prevention and intellectual property protection for a major tech company.\n\nMission Context:\n- Client: Major semiconductor manufacturer\n- Threat: Industrial espionage attempts\n- Duration: 15 days\n- Team: 4 agents, 3 cyber specialists\n\nKey Activities:\n1. Facility Security Assessment\n   - Identified 12 potential vulnerability points\n   - Implemented additional access controls\n   - Upgraded surveillance systems\n\n2. Counter-Surveillance Operations\n   - Detected 3 suspicious individuals\n   - Confirmed corporate espionage attempts\n   - Coordinated with Japanese National Police\n\n3. Cyber Defense\n   - Blocked 47 intrusion attempts\n   - Traced attacks to competing firms\n   - Implemented enhanced firewall protocols\n\nChallenges Faced:\n- Language barrier in technical discussions\n- Japanese business protocol compliance\n- Coordination with local law enforcement\n- Time zone differences for HQ communication\n\nSuccesses:\n- Zero data breaches during operation\n- 3 espionage attempts neutralized\n- Client relationship strengthened\n- Future contract secured\n\nLocal Resources:\n- Hotel: Park Hyatt Tokyo (team accommodation)\n- Transport: JR Pass, Tokyo Metro cards\n- Emergency Contact: Japanese Embassy liaison\n- Medical: St. Luke's International Hospital\n\nCultural Notes:\n- Always remove shoes in certain facilities\n- Business cards exchanged with both hands\n- Punctuality critical in Japanese business culture\n- Bow appropriately (15-degree for business)\n\nRecommendations:\n- Hire Japanese language specialist for future ops\n- Establish permanent Tokyo liaison\n- Study Japanese corporate security protocols\n- Build relationship with Tokyo Metropolitan Police",
  "category": "agent",
  "mission_id": "MS-2025-003",
  "country": "Japan",
  "tags": ["mission", "completed", "2025", "asia", "corporate-security", "cyber"],
  "visibility": "public",
  "author": "admin"
}
```

**Validation**:
- ✅ Different country (Japan)
- ✅ Different mission type (corporate security)
- ✅ Proper categorization

### Test 2.3: Create Technician Document - CCTV System ✅

```bash
POST http://localhost:8000/kb/create
Content-Type: application/json

{
  "title": "CCTV Camera System - Complete Setup and Troubleshooting Guide",
  "content": "HQ CCTV System Documentation - Hikvision DS-2CD2185FWD-I 8MP Network Cameras\n\n=== SYSTEM OVERVIEW ===\n\nEquipment:\n- Model: Hikvision DS-2CD2185FWD-I\n- Resolution: 8MP (4K)\n- Type: IP Network Camera with PoE\n- Quantity: 24 cameras (HQ building coverage)\n- Recording: Hikvision NVR DS-7608NI-K2/8P\n\nDeployment Locations:\n- Floor 1 (Lobby): 6 cameras\n- Floor 2 (Operations): 4 cameras\n- Floor 3 (Laboratories): 6 cameras\n- Floor 4 (Admin): 3 cameras\n- Perimeter (Outside): 5 cameras\n\n=== INSTALLATION PROCEDURE ===\n\n1. Physical Installation:\n   a) Mount cameras at 2.5 meters height\n   b) Ensure 30-degree downward angle for optimal coverage\n   c) Use weatherproof mounting brackets for outdoor units\n   d) Cable management through conduits\n\n2. Network Connection:\n   a) Connect to PoE network switch (Cisco Catalyst 2960-X)\n   b) Each camera requires PoE+ (30W minimum)\n   c) Use Cat6 ethernet cables (max 100m distance)\n   d) Label each cable with camera location\n\n3. IP Configuration:\n   a) Static IP range: 192.168.10.100-192.168.10.123\n   b) Subnet mask: 255.255.255.0\n   c) Gateway: 192.168.10.1\n   d) DNS: 192.168.10.2\n   e) VLAN: 10 (Security Systems)\n\n4. Camera Settings:\n   a) Recording quality: 4K at 15fps\n   b) Compression: H.265+\n   c) Storage: 30 days retention\n   d) Motion detection: Enabled on all zones\n   e) Night mode: Automatic IR activation\n\n=== NETWORK CONFIGURATION ===\n\nVLAN Setup:\n- VLAN ID: 10\n- Name: Security_Systems\n- Ports: 1-24 (dedicated to cameras)\n- Trunk port: Port 25 (to NVR)\n\nNVR Configuration:\n- IP Address: 192.168.10.50\n- Web Interface: http://192.168.10.50\n- RTSP Port: 554\n- HTTP Port: 80\n- HTTPS Port: 443\n- NTP Server: pool.ntp.org\n\nAccess Credentials:\n- Admin Username: admin\n- Password: [Set during initial setup - stored in password vault]\n- Tech Username: technician\n- Password: [Set during initial setup - stored in password vault]\n\n=== COMMON ISSUES & TROUBLESHOOTING ===\n\nProblem 1: Camera Connection Timeout\nSymptoms:\n- Camera not accessible via web interface\n- No video feed in NVR\n- Ping test fails\n\nSolutions:\na) Check physical connections:\n   - Verify ethernet cable is properly seated\n   - Test cable with cable tester\n   - Check for cable damage\n\nb) Verify PoE power supply:\n   - Check PoE switch LED indicators\n   - Verify power budget not exceeded\n   - Test with PoE injector if needed\n\nc) Camera restart:\n   - Disconnect power for 30 seconds\n   - Reconnect and wait 2 minutes for boot\n   - Check for steady LED on camera\n\nd) Network settings:\n   - Verify VLAN configuration\n   - Check IP address conflicts\n   - Verify gateway and DNS settings\n\nProblem 2: Poor Image Quality\nSymptoms:\n- Blurry or out-of-focus images\n- Dark or overexposed video\n- Color issues\n\nSolutions:\na) Focus adjustment:\n   - Access camera web interface\n   - Use remote focus control\n   - Adjust during daytime for best results\n\nb) Lighting conditions:\n   - Check IR illuminator function (night)\n   - Adjust exposure settings\n   - Enable WDR (Wide Dynamic Range) if needed\n\nc) Lens cleaning:\n   - Power off camera\n   - Clean lens with microfiber cloth\n   - Check for condensation inside dome\n\nd) Settings optimization:\n   - Adjust brightness/contrast\n   - Set appropriate frame rate\n   - Enable image enhancement features\n\nProblem 3: Recording Failures\nSymptoms:\n- No recordings in NVR\n- Gaps in timeline\n- Storage full errors\n\nSolutions:\na) Storage check:\n   - Verify hard drive status in NVR\n   - Check available storage space\n   - Run disk health diagnostics\n\nb) Recording schedule:\n   - Verify recording is enabled\n   - Check schedule settings (24/7 recommended)\n   - Verify motion detection settings\n\nc) Network bandwidth:\n   - Test bandwidth between camera and NVR\n   - Reduce resolution if bandwidth limited\n   - Check for network congestion\n\nd) NVR maintenance:\n   - Reboot NVR monthly\n   - Update firmware quarterly\n   - Clear system logs regularly\n\nProblem 4: Motion Detection False Alarms\nSymptoms:\n- Excessive motion detection alerts\n- Recording storage filling quickly\n- Notification spam\n\nSolutions:\na) Sensitivity adjustment:\n   - Lower motion detection sensitivity\n   - Adjust detection zones\n   - Exclude problem areas (trees, flags)\n\nb) Time scheduling:\n   - Set detection active periods\n   - Disable during high-traffic times\n   - Use different settings day/night\n\nc) Advanced features:\n   - Enable smart detection (human/vehicle)\n   - Use line crossing detection\n   - Set minimum target size\n\n=== MAINTENANCE SCHEDULE ===\n\nWeekly Tasks:\n- Monitor camera feeds for issues\n- Check NVR recording status\n- Review storage capacity\n- Test random camera functionality\n\nMonthly Tasks:\n- Clean outdoor camera lenses\n- Verify all cameras operational\n- Check network connectivity\n- Review and backup critical footage\n- Restart NVR for optimization\n\nQuarterly Tasks:\n- Firmware updates (cameras and NVR)\n- Full system health check\n- Cable and connection inspection\n- Update access credentials\n- Test backup and restore procedures\n\nAnnually Tasks:\n- Complete system inspection\n- Replace aging cables/connectors\n- Hard drive health assessment\n- Comprehensive security audit\n- Training refresh for operators\n\n=== ADVANCED CONFIGURATION ===\n\nRemote Access Setup:\n1. Port forwarding on router\n   - Forward port 443 to NVR IP\n   - Use non-standard port for security\n2. DDNS configuration\n   - Register with Hikvision DDNS service\n   - Set auto-update interval\n3. Mobile app setup\n   - Install Hik-Connect app\n   - Add device using QR code or serial number\n\nIntegration with Access Control:\n- Link cameras to door events\n- Trigger recording on access attempts\n- Synchronize video with access logs\n\nAlert Configuration:\n- Email alerts for critical events\n- Push notifications to mobile\n- SMS alerts for system failures\n\n=== SECURITY BEST PRACTICES ===\n\n1. Change default passwords immediately\n2. Enable HTTPS for web access\n3. Disable unused protocols (Telnet, FTP)\n4. Regular firmware updates\n5. Use strong password policy\n6. Enable IP whitelist for remote access\n7. Disable UPnP on cameras\n8. Regular security audits\n9. Monitor access logs\n10. Backup configuration regularly\n\n=== TECHNICAL SPECIFICATIONS ===\n\nCamera Specs:\n- Sensor: 1/2.5\" Progressive Scan CMOS\n- Resolution: 3840 × 2160\n- Lens: 2.8mm fixed lens (106° horizontal)\n- IR Range: 30 meters\n- WDR: 120 dB\n- Power: PoE (802.3at)\n- Operating Temp: -30°C to +60°C\n- IP Rating: IP67 (outdoor models)\n\nNVR Specs:\n- Channels: 8 (expandable)\n- Recording: H.265+/H.265/H.264+/H.264\n- Bandwidth: 80 Mbps incoming\n- Storage: 2x 6TB HDD (RAID 1)\n- Backup: USB 3.0, eSATA\n- Output: HDMI 4K, VGA\n\n=== SUPPORT & CONTACTS ===\n\nHikvision Technical Support:\n- Phone: 1-800-HIKVISION\n- Email: support@hikvision.com\n- Portal: https://www.hikvision.com/support\n\nInternal Contacts:\n- IT Department: ext. 2100\n- Security Team: ext. 2200\n- Facilities: ext. 2300\n\nSpare Parts Inventory:\n- Location: Storage Room B3\n- Spare cameras: 2 units\n- Spare cables: 100m Cat6\n- Spare power supplies: 3 units\n- Spare hard drives: 2x 6TB",
  "category": "technician",
  "tags": ["cctv", "cameras", "surveillance", "network", "hikvision", "setup", "troubleshooting", "security-systems"],
  "visibility": "public",
  "author": "admin",
  "metadata": {
    "equipment_type": "cctv",
    "manufacturer": "Hikvision",
    "model": "DS-2CD2185FWD-I",
    "last_updated": "2025-12-01"
  }
}
```

**Validation**:
- ✅ Technician category
- ✅ Comprehensive technical content
- ✅ No mission_id or country (tech docs)

### Test 2.4: Create Technician Document - Fingerprint System ✅

```bash
POST http://localhost:8000/kb/create
Content-Type: application/json

{
  "title": "Biometric Fingerprint Access Control System - Setup & Maintenance",
  "content": "ZKTeco F18 Fingerprint Access Control Terminal - Complete Documentation\n\n=== SYSTEM OVERVIEW ===\n\nEquipment Information:\n- Model: ZKTeco F18\n- Type: Fingerprint & RFID Card Reader\n- Capacity: 3,000 fingerprints, 10,000 cards\n- Locations: 8 terminals (all entry points)\n- Controller: C3-400 4-door controller\n\nInstallation Points:\n1. Main Entrance (Terminal-01)\n2. Lab Wing Entrance (Terminal-02)\n3. Server Room (Terminal-03)\n4. Armory (Terminal-04)\n5. Operations Center (Terminal-05)\n6. Admin Floor Access (Terminal-06)\n7. Garage Entry (Terminal-07)\n8. Emergency Exit (Terminal-08)\n\n=== INSTALLATION GUIDE ===\n\nPhysical Installation:\n1. Mount at 1.4 meters height\n2. Ensure 15cm clearance on sides\n3. Avoid direct sunlight exposure\n4. Weatherproof housing for outdoor units\n5. Wired connection required (no WiFi)\n\nWiring:\n- Power: 12V DC, 3A (included adapter)\n- Communication: RS-485 bus to controller\n- Door Strike: Relay output (NO/NC/COM)\n- Exit Button: Dry contact input\n- Door Sensor: Magnetic contact input\n- Alarm Output: Relay for siren/buzzer\n\nNetwork Configuration:\n- IP Address: Static (192.168.20.x range)\n- Subnet: 255.255.255.0\n- Gateway: 192.168.20.1\n- Port: 4370 (default)\n- Protocol: TCP/IP\n\n=== USER ENROLLMENT ===\n\nFingerprint Registration:\n1. Access admin menu (password required)\n2. Select \"Add User\"\n3. Enter user ID (1-99999)\n4. Scan fingerprint 3 times for verification\n5. Assign access level (1-10)\n6. Set time zone permissions\n7. Enable/disable RFID card if needed\n\nBest Practices:\n- Use clean, dry fingers\n- Center finger on sensor\n- Apply moderate pressure\n- Scan index and middle finger (backup)\n- Avoid damaged or cut fingers\n\nRFID Card Assignment:\n1. Hold card near reader\n2. Enter user ID to link\n3. Test card recognition\n4. Print card number on card\n5. Store backup in system\n\n=== ACCESS LEVELS & TIME ZONES ===\n\nAccess Level Configuration:\n- Level 1: Public areas (24/7)\n- Level 2: Office areas (6 AM - 10 PM)\n- Level 3: Lab areas (24/7, logged)\n- Level 4: Server room (business hours only)\n- Level 5: Armory (authorized personnel only)\n- Level 10: Admin/Master access (all areas, all times)\n\nTime Zone Setup:\n1. Access controller web interface\n2. Configure time zones (TZ1-TZ10)\n3. Set weekday/weekend schedules\n4. Define holidays\n5. Test access during restricted times\n\n=== TROUBLESHOOTING ===\n\nProblem 1: Fingerprint Not Recognized\nCauses:\n- Dirty sensor\n- Wet/damaged finger\n- Poor quality enrollment\n- Sensor malfunction\n\nSolutions:\n1. Clean sensor with alcohol wipe\n2. Dry hands thoroughly\n3. Re-enroll fingerprint\n4. Try alternative finger\n5. Use RFID card backup\n6. Check sensor connection\n\nProblem 2: Door Not Unlocking\nCauses:\n- Relay failure\n- Door strike power issue\n- Lock mechanism jammed\n- Controller offline\n\nSolutions:\n1. Check relay LED on terminal\n2. Test manual unlock button\n3. Verify strike power (12V/24V)\n4. Check door alignment\n5. Test lock mechanism manually\n6. Reboot controller\n\nProblem 3: System Not Recording Logs\nCauses:\n- Memory full\n- Network connection lost\n- Controller software crash\n- Database error\n\nSolutions:\n1. Clear old logs (keep 90 days)\n2. Check network cable\n3. Restart controller\n4. Verify database connectivity\n5. Update controller firmware\n\nProblem 4: False Rejections\nCauses:\n- Sensor sensitivity too high\n- Environmental factors\n- Fingerprint quality degraded\n- System misconfiguration\n\nSolutions:\n1. Adjust sensor sensitivity (1-5)\n2. Clean sensor regularly\n3. Re-enroll problematic users\n4. Check lighting conditions\n5. Verify system time sync\n\n=== MAINTENANCE SCHEDULE ===\n\nDaily:\n- Monitor system status\n- Review access logs\n- Check for alerts/errors\n\nWeekly:\n- Clean fingerprint sensors\n- Test backup power\n- Verify door locks function\n- Check network connectivity\n\nMonthly:\n- Review user access rights\n- Remove inactive users\n- Test emergency override\n- Backup user database\n- Check door sensor alignment\n\nQuarterly:\n- Firmware updates\n- System health diagnostics\n- Replace worn components\n- Security audit\n- User training refresh\n\nAnnually:\n- Complete system overhaul\n- Replace backup batteries\n- Recalibrate sensors\n- Update access policies\n- Physical security inspection\n\n=== EMERGENCY PROCEDURES ===\n\nPower Failure:\n1. UPS provides 2 hours backup\n2. Doors automatically unlock (fail-safe)\n3. System retains all data in memory\n4. Manual override keys available\n\nSystem Failure:\n1. Use mechanical override keys\n2. Contact IT department immediately\n3. Activate backup authentication (RFID cards)\n4. Document incident\n5. Review access logs after restoration\n\nLockout Situation:\n1. Verify user credentials\n2. Check access level assignment\n3. Use master card for override\n4. Escort authorized personnel\n5. Update access rights if needed\n\n=== INTEGRATION WITH OTHER SYSTEMS ===\n\nCCTV Integration:\n- Link access events to camera recording\n- Capture photo on denied access\n- Store images with access logs\n\nAlarm System:\n- Trigger alarm on forced entry\n- Silent alarm for duress code\n- Integration with security console\n\nTime & Attendance:\n- Export logs for payroll\n- Track employee hours\n- Generate attendance reports\n\n=== SECURITY BEST PRACTICES ===\n\n1. Regular access right reviews\n2. Immediate removal of terminated users\n3. Unique user IDs (no sharing)\n4. Strong admin passwords\n5. Encrypted communication\n6. Regular log monitoring\n7. Backup database daily\n8. Physical security of controller\n9. Firmware updates applied promptly\n10. Incident response plan in place\n\n=== TECHNICAL SPECIFICATIONS ===\n\nF18 Terminal:\n- Sensor: Optical fingerprint sensor\n- Capacity: 3,000 templates\n- Cards: 10,000 RFID (125KHz/13.56MHz)\n- Logs: 100,000 transactions\n- Verification: < 1 second\n- FAR: < 0.0001%\n- FRR: < 1%\n- Display: 2.8\" TFT color\n- Communication: TCP/IP, RS-485\n- Power: DC 12V, 3A\n- Operating Temp: 0°C to 45°C\n\nC3-400 Controller:\n- Doors: 4 (expandable to 16)\n- Users: 20,000\n- Cards: 50,000\n- Communication: TCP/IP\n- Backup: Battery for 4 hours\n- Dimensions: 280×235×60mm\n\n=== SUPPORT INFORMATION ===\n\nManufacturer Support:\n- ZKTeco: www.zkteco.com\n- Phone: 1-888-ZKT-ECO1\n- Email: support@zkteco.com\n\nInternal Contacts:\n- Security: ext. 2200\n- IT Support: ext. 2100\n- Facilities: ext. 2300\n\nSpare Parts:\n- Location: Storage B3\n- Spare terminals: 2 units\n- Spare controllers: 1 unit\n- RFID cards: 500 blank cards\n- Backup batteries: 4 units",
  "category": "technician",
  "tags": ["biometric", "fingerprint", "access-control", "zkteco", "security", "setup", "troubleshooting"],
  "visibility": "public",
  "author": "admin"
}
```

### Test 2.5: Create Technician Document - Door Lock System ✅

```bash
POST http://localhost:8000/kb/create
Content-Type: application/json

{
  "title": "Electronic Door Lock System - Installation and Configuration Guide",
  "content": "Electromagnetic Lock System - Complete Technical Documentation\n\n=== SYSTEM OVERVIEW ===\n\nEquipment:\n- Mag Locks: Securitron M62 (1,200 lbs holding force)\n- Electric Strikes: HES 5000 Series\n- Door Controllers: Mercury Security MR52\n- Exit Buttons: Illuminated push-to-exit buttons\n- Door Sensors: Magnetic contact switches\n\nInstallation Locations:\n- 15 Mag locks (high-security areas)\n- 20 Electric strikes (office areas)\n- All doors monitored by sensors\n\n=== INSTALLATION PROCEDURES ===\n\nMagnetic Lock Installation:\n1. Mount lock on door frame top\n2. Align armature plate on door\n3. Ensure 1/8\" maximum gap\n4. Wire to controller (2-wire, 12/24V)\n5. Install door position sensor\n6. Test holding force\n\nElectric Strike Installation:\n1. Cut mortise in door frame\n2. Mount strike in opening\n3. Adjust keeper alignment\n4. Wire to controller\n5. Set fail-safe/fail-secure mode\n6. Test operation\n\nWiring Standards:\n- Power: 12V DC or 24V DC\n- Wire gauge: 18 AWG minimum\n- Max run: 100 feet (voltage drop consideration)\n- Color code: Red (+), Black (-)\n- Shielded cable for long runs\n\n=== TROUBLESHOOTING ===\n\nDoor Won't Lock:\n- Check power supply voltage\n- Test relay output on controller\n- Verify wiring connections\n- Check for obstruction\n- Test lock with direct power\n\nDoor Won't Unlock:\n- Verify unlock signal sent\n- Check relay function\n- Test manual override\n- Inspect strike keeper alignment\n- Replace faulty strike if needed\n\nBuzzing Sound:\n- Check alignment (mag lock)\n- Verify voltage (should be 12V or 24V)\n- Look for AC instead of DC power\n- Check for loose connections\n\n=== MAINTENANCE ===\n\nWeekly:\n- Visual inspection of all locks\n- Test emergency release buttons\n- Check door sensors\n\nMonthly:\n- Clean lock surfaces\n- Test fail-safe/fail-secure modes\n- Verify backup power\n- Check for physical damage\n\nQuarterly:\n- Tighten all mounting screws\n- Test holding force (mag locks)\n- Lubricate strike mechanisms\n- Update access schedules\n\nAnnually:\n- Replace worn components\n- Full system test\n- Update documentation\n- Security audit",
  "category": "technician",
  "tags": ["door-locks", "magnetic-locks", "electric-strikes", "security", "access-control", "installation"],
  "visibility": "public",
  "author": "admin"
}
```

**Wait 5 seconds after document creation for indexing**

---

## 3. NLP Chat Interface Tests

### Test 3.1: Agent Chat - Query About Germany Missions ✅

**Purpose**: Test agent querying mission documents

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "What missions have been conducted in Germany and what resources are available there?",
  "user_role": "agent",
  "limit": 5
}
```

**Expected Response Structure**:
```json
{
  "message": "Chat query processed successfully",
  "data": {
    "answer": "Based on the available documents, Operation Phoenix was conducted in Berlin, Germany from January 15-30, 2025...",
    "matched_documents": [
      {
        "document_id": "...",
        "title": "Mission Report: Operation Phoenix - Germany",
        "mission_id": "MS-2025-001",
        "country": "Germany",
        "long_summary": "Comprehensive summary of the mission...",
        "matched_points": [
          "Mission conducted in Berlin from January 15-30, 2025",
          "Safe houses located in Charlottenburg and Mitte districts",
          "Coordination with German federal police was excellent"
        ],
        "category": "agent",
        "tags": ["mission", "completed", "2025", "europe", "diplomatic"],
        "similarity_score": 0.85,
        "author": "admin"
      }
    ],
    "confidence": 0.85,
    "model_used": "llama3.2:3b"
  }
}
```

**Validation**:
- ✅ Answer mentions Operation Phoenix
- ✅ Matched documents include Germany mission
- ✅ Mission ID present
- ✅ Country is "Germany"
- ✅ Long summary provided
- ✅ 3-5 matched points extracted
- ✅ Category is "agent"
- ✅ Confidence score > 0.5
- ✅ Model is "llama3.2:3b"

### Test 3.2: Agent Chat - Query About Japan Missions ✅

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "Tell me about missions in Japan and what challenges were faced",
  "user_role": "agent",
  "limit": 5
}
```

**Validation**:
- ✅ Returns Operation Dragon Eye
- ✅ Country is "Japan"
- ✅ Mentions corporate security context
- ✅ Includes challenges (language barrier, business protocol)

### Test 3.3: Agent Chat - General Mission Query ✅

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "What types of equipment are typically used in field operations?",
  "user_role": "agent",
  "limit": 5
}
```

**Validation**:
- ✅ Returns relevant mission documents
- ✅ Only agent category documents
- ✅ Answer synthesizes equipment info from multiple missions

### Test 3.4: Technician Chat - CCTV Troubleshooting ✅

**Purpose**: Test technician querying equipment documentation

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "How do I fix a CCTV camera that has connection timeout issues?",
  "user_role": "technician",
  "limit": 5
}
```

**Expected Response**:
- ✅ Returns CCTV documentation
- ✅ Category is "technician"
- ✅ Answer includes troubleshooting steps
- ✅ Matched points include specific solutions
- ✅ No mission_id or country (tech docs don't have these)

### Test 3.5: Technician Chat - Fingerprint System ✅

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "What should I do if the fingerprint reader is not recognizing fingerprints?",
  "user_role": "technician",
  "limit": 5
}
```

**Validation**:
- ✅ Returns fingerprint system documentation
- ✅ Troubleshooting steps provided
- ✅ Multiple solutions suggested

### Test 3.6: Technician Chat - Door Lock Issues ✅

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "How do I troubleshoot a door that won't unlock?",
  "user_role": "technician",
  "limit": 3
}
```

**Validation**:
- ✅ Returns door lock documentation
- ✅ Specific troubleshooting steps
- ✅ Technical details included

### Test 3.7: Technician Chat - General Equipment Query ✅

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "What security equipment maintenance should be performed monthly?",
  "user_role": "technician",
  "limit": 5
}
```

**Validation**:
- ✅ Returns multiple equipment documents
- ✅ Synthesizes maintenance schedules
- ✅ Covers different equipment types

### Test 3.8: Chat - Empty Results ✅

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "Information about submarine operations in Antarctica",
  "user_role": "agent",
  "limit": 5
}
```

**Expected Response**:
```json
{
  "message": "Chat query processed successfully",
  "data": {
    "answer": "No relevant documents found in the Knowledge Crystal for agents...",
    "matched_documents": [],
    "confidence": 0.0,
    "model_used": "llama3.2:3b"
  }
}
```

**Validation**:
- ✅ Graceful handling of no results
- ✅ Helpful message to user
- ✅ Confidence is 0.0

---

## 4. Access Control Tests (Critical)

### Test 4.1: Agent Trying to Access Technician Documents ❌ Should Fail

**Purpose**: Verify agents cannot see technical documentation

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "How do I configure the CCTV system?",
  "user_role": "agent",
  "limit": 5
}
```

**Expected Behavior**:
- ✅ matched_documents should be empty or not contain tech docs
- ✅ Answer should indicate no relevant documents for agents
- ✅ Should NOT return CCTV documentation

**Validation**:
- ✅ No technician documents in results
- ✅ Category filter working correctly

### Test 4.2: Technician Trying to Access Agent Documents ❌ Should Fail

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "What missions were conducted in Germany?",
  "user_role": "technician",
  "limit": 5
}
```

**Expected Behavior**:
- ✅ matched_documents should be empty
- ✅ Should NOT return mission documents
- ✅ Answer indicates no documents for technicians

### Test 4.3: Agent Search with Category Filter ✅

```bash
GET http://localhost:8000/kb/search?q=security&category=agent&limit=5
```

**Validation**:
- ✅ Only agent documents returned
- ✅ No technician documents in results

### Test 4.4: Technician Search with Category Filter ✅

```bash
GET http://localhost:8000/kb/search?q=system&category=technician&limit=5
```

**Validation**:
- ✅ Only technician documents returned
- ✅ No agent/mission documents in results

### Test 4.5: Invalid Role Handling ❌

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "Test query",
  "user_role": "invalid_role",
  "limit": 5
}
```

**Expected Response**:
```json
{
  "message": "Chat query processed successfully",
  "data": {
    "answer": "Invalid user role. Must be 'agent' or 'technician'.",
    "matched_documents": [],
    "confidence": 0.0,
    "model_used": "llama3.2:3b"
  }
}
```

---

## 5. Semantic Search Tests

### Test 5.1: Search with Agent Category ✅

```bash
GET http://localhost:8000/kb/search?q=diplomatic%20operations&category=agent&limit=5
```

**Validation**:
- ✅ Returns agent documents only
- ✅ Ranked by relevance
- ✅ Includes similarity scores

### Test 5.2: Search by Country ✅

```bash
GET http://localhost:8000/kb/search?q=operations&category=agent&country=Germany&limit=5
```

**Validation**:
- ✅ Only Germany missions returned
- ✅ Japan missions NOT included
- ✅ Country filter working

### Test 5.3: Search with Tags ✅

```bash
GET http://localhost:8000/kb/search?q=security&category=agent&tags=diplomatic&tags=vip-protection&limit=5
```

**Validation**:
- ✅ Documents with specified tags prioritized
- ✅ Tag filtering applied

### Test 5.4: Technician Equipment Search ✅

```bash
GET http://localhost:8000/kb/search?q=troubleshooting&category=technician&limit=5
```

**Validation**:
- ✅ Returns equipment documentation
- ✅ Multiple equipment types included
- ✅ Relevance ranking applied

### Test 5.5: Search with Visibility Filter ✅

```bash
GET http://localhost:8000/kb/search?q=mission&category=agent&visibility=public&limit=5
```

**Validation**:
- ✅ Only public documents returned
- ✅ Visibility filter respected

### Test 5.6: Multi-Filter Search ✅

```bash
GET http://localhost:8000/kb/search?q=security&category=agent&country=Japan&tags=cyber&visibility=public&limit=3
```

**Validation**:
- ✅ All filters applied simultaneously
- ✅ Correct documents returned
- ✅ Result count respects limit

---

## 6. Document Listing Tests

### Test 6.1: List All Agent Documents ✅

```bash
GET http://localhost:8000/kb/pages?category=agent&limit=10&skip=0
```

**Expected Response Structure**:
```json
{
  "pages": [...],
  "total": 2,
  "limit": 10,
  "skip": 0,
  "filters": {
    "category": "agent",
    "country": null,
    "mission_id": null,
    "visibility": null,
    "tags": null
  }
}
```

**Validation**:
- ✅ Pages array contains agent documents
- ✅ Total count accurate
- ✅ Pagination working

### Test 6.2: List All Technician Documents ✅

```bash
GET http://localhost:8000/kb/pages?category=technician&limit=10&skip=0
```

**Validation**:
- ✅ Only technician documents listed
- ✅ Equipment types represented
- ✅ Total count matches

### Test 6.3: List by Country ✅

```bash
GET http://localhost:8000/kb/pages?category=agent&country=Germany&limit=10
```

**Validation**:
- ✅ Only Germany missions listed
- ✅ Country filter effective

### Test 6.4: List by Mission ID ✅

```bash
GET http://localhost:8000/kb/pages?category=agent&mission_id=MS-2025-001&limit=10
```

**Validation**:
- ✅ Specific mission document returned
- ✅ Mission ID match exact

### Test 6.5: List with Pagination ✅

```bash
GET http://localhost:8000/kb/pages?category=technician&limit=2&skip=0
GET http://localhost:8000/kb/pages?category=technician&limit=2&skip=2
```

**Validation**:
- ✅ Different documents in each page
- ✅ No overlap between pages
- ✅ Skip/limit working correctly

---

## 7. Document Management Tests

### Test 7.1: Get Single Document ✅

```bash
GET http://localhost:8000/kb/page/{page_id}
```

*Replace {page_id} with actual ID from creation response*

**Validation**:
- ✅ Document retrieved successfully
- ✅ All fields present
- ✅ Content intact

### Test 7.2: Update Document ✅

```bash
PUT http://localhost:8000/kb/page/{page_id}
Content-Type: application/json

{
  "tags": ["mission", "completed", "2025", "europe", "diplomatic", "vip-protection", "updated"]
}
```

**Validation**:
- ✅ Document updated
- ✅ New tags applied
- ✅ updated_at timestamp changed

### Test 7.3: Update Document Content (Re-indexing) ✅

```bash
PUT http://localhost:8000/kb/page/{page_id}
Content-Type: application/json

{
  "content": "Updated content with additional information about the mission outcomes and recommendations for future operations in the region."
}
```

**Validation**:
- ✅ Content updated
- ✅ Re-indexing triggered
- ✅ New embeddings created
- ✅ Searchable with new content

### Test 7.4: Delete Document ✅

```bash
DELETE http://localhost:8000/kb/page/{page_id}
```

**Validation**:
- ✅ Document deleted from MongoDB
- ✅ Chunks removed from vector store
- ✅ No longer appears in searches

---

## 8. Statistics & Analytics Tests

### Test 8.1: Get Overall Statistics ✅

```bash
GET http://localhost:8000/kb/stats
```

**Expected Response Structure**:
```json
{
  "total_pages": 5,
  "agent_documents": 2,
  "technician_documents": 3,
  "public_pages": 5,
  "private_pages": 0,
  "top_tags": [
    {"_id": "mission", "count": 2},
    {"_id": "setup", "count": 3},
    ...
  ],
  "countries": [
    {"_id": "Germany", "count": 1},
    {"_id": "Japan", "count": 1}
  ]
}
```

**Validation**:
- ✅ Correct document counts
- ✅ Category breakdown accurate
- ✅ Top tags listed
- ✅ Countries for agent docs listed

### Test 8.2: Verify Category Distribution ✅

**Validation from stats**:
- ✅ agent_documents count matches agent docs created
- ✅ technician_documents count matches tech docs created
- ✅ Sum equals total_pages

### Test 8.3: Verify Country Statistics ✅

**Validation from stats**:
- ✅ Germany appears in countries
- ✅ Japan appears in countries
- ✅ Count per country accurate

---

## 9. Edge Cases & Error Handling

### Test 9.1: Empty Query ❌

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "",
  "user_role": "agent",
  "limit": 5
}
```

**Expected**: 422 Validation Error

### Test 9.2: Query Too Short ❌

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "hi",
  "user_role": "agent",
  "limit": 5
}
```

**Expected**: 422 Validation Error (min_length=5)

### Test 9.3: Invalid Category in Search ❌

```bash
GET http://localhost:8000/kb/search?q=test&category=invalid&limit=5
```

**Expected**: Should handle gracefully or return validation error

### Test 9.4: Limit Out of Bounds ❌

```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "test query",
  "user_role": "agent",
  "limit": 100
}
```

**Expected**: 422 Validation Error (max limit is 20)

### Test 9.5: Non-existent Document ID ❌

```bash
GET http://localhost:8000/kb/page/000000000000000000000000
```

**Expected**: 404 Not Found

### Test 9.6: Invalid Document ID Format ❌

```bash
GET http://localhost:8000/kb/page/invalid-id-format
```

**Expected**: 400 Bad Request or 422 Validation Error

---

## 10. Performance Tests

### Test 10.1: Response Time - Chat Query ⏱️

**Execute multiple times and measure**:
```bash
POST http://localhost:8000/kb/chat
Content-Type: application/json

{
  "query": "What are the key security considerations?",
  "user_role": "agent",
  "limit": 5
}
```

**Acceptable Performance**:
- ✅ First query: < 10 seconds (model loading)
- ✅ Subsequent queries: 2-5 seconds
- ✅ Consistent response times

### Test 10.2: Response Time - Search ⏱️

```bash
GET http://localhost:8000/kb/search?q=security&category=agent&limit=5
```

**Acceptable Performance**:
- ✅ Response time: < 3 seconds
- ✅ Embedding generation: < 1 second

### Test 10.3: Large Document Handling ⏱️

Create a document with 5000+ words and test:
- ✅ Indexing completes successfully
- ✅ Chunking works correctly
- ✅ Search retrieves relevant chunks
- ✅ No timeout errors

### Test 10.4: Concurrent Requests 🔀

Execute 5 chat requests simultaneously:

**Validation**:
- ✅ All requests complete successfully
- ✅ No race conditions
- ✅ Responses are correct
- ✅ No database conflicts

---

## 11. Integration Tests

### Test 11.1: End-to-End Agent Workflow ✅

**Scenario**: Agent needs mission intel

1. Agent queries: "What do I need to know about operations in Germany?"
2. System retrieves Operation Phoenix
3. Agent gets safe house locations
4. Agent queries: "What equipment was used?"
5. System extracts equipment list
6. Agent satisfied with information

**Validation**:
- ✅ All queries successful
- ✅ Relevant information retrieved
- ✅ Context maintained across queries

### Test 11.2: End-to-End Technician Workflow ✅

**Scenario**: Technician troubleshooting CCTV

1. Technician queries: "CCTV camera offline"
2. System retrieves troubleshooting docs
3. Technician follows step 1 (check cables)
4. Technician queries: "Camera still offline after cable check"
5. System provides advanced troubleshooting
6. Issue resolved

**Validation**:
- ✅ Progressive troubleshooting flow
- ✅ Relevant info at each step

---

## 12. Data Integrity Tests

### Test 12.1: Document Count Consistency ✅

```bash
# Get stats
GET http://localhost:8000/kb/stats

# List all agent docs
GET http://localhost:8000/kb/pages?category=agent&limit=100

# List all tech docs
GET http://localhost:8000/kb/pages?category=technician&limit=100
```

**Validation**:
- ✅ Stats total matches actual count
- ✅ Category counts match listings
- ✅ No duplicate documents

### Test 12.2: Vector Store Consistency ✅

**After creating/updating/deleting documents**:
- ✅ MongoDB and ChromaDB stay in sync
- ✅ Orphaned chunks are cleaned up
- ✅ No stale embeddings

### Test 12.3: Metadata Consistency ✅

**Validation**:
- ✅ All agent docs have mission_id or country
- ✅ Technician docs don't have mission_id
- ✅ Categories correctly assigned
- ✅ Tags properly stored and searchable

---

## Test Results Summary Template

| Test ID | Test Name | Status | Response Time | Notes |
|---------|-----------|--------|---------------|-------|
| 1.1 | Health Check | ⬜ | - | |
| 2.1 | Create Agent Doc (Germany) | ⬜ | - | |
| 2.2 | Create Agent Doc (Japan) | ⬜ | - | |
| 2.3 | Create Tech Doc (CCTV) | ⬜ | - | |
| 2.4 | Create Tech Doc (Fingerprint) | ⬜ | - | |
| 2.5 | Create Tech Doc (Door Locks) | ⬜ | - | |
| 3.1 | Agent Chat - Germany | ⬜ | - | |
| 3.2 | Agent Chat - Japan | ⬜ | - | |
| 3.3 | Agent Chat - General | ⬜ | - | |
| 3.4 | Tech Chat - CCTV | ⬜ | - | |
| 3.5 | Tech Chat - Fingerprint | ⬜ | - | |
| 3.6 | Tech Chat - Door Locks | ⬜ | - | |
| 3.7 | Tech Chat - Maintenance | ⬜ | - | |
| 3.8 | Chat - No Results | ⬜ | - | |
| 4.1 | Agent → Tech Docs (Block) | ⬜ | - | |
| 4.2 | Tech → Agent Docs (Block) | ⬜ | - | |
| 4.3 | Agent Search Filter | ⬜ | - | |
| 4.4 | Tech Search Filter | ⬜ | - | |
| 4.5 | Invalid Role | ⬜ | - | |
| 5.1 | Search Agent Category | ⬜ | - | |
| 5.2 | Search by Country | ⬜ | - | |
| 5.3 | Search with Tags | ⬜ | - | |
| 5.4 | Search Tech Docs | ⬜ | - | |
| 5.5 | Search Visibility | ⬜ | - | |
| 5.6 | Multi-Filter Search | ⬜ | - | |
| 6.1 | List Agent Docs | ⬜ | - | |
| 6.2 | List Tech Docs | ⬜ | - | |
| 6.3 | List by Country | ⬜ | - | |
| 6.4 | List by Mission ID | ⬜ | - | |
| 6.5 | List Pagination | ⬜ | - | |
| 7.1 | Get Single Doc | ⬜ | - | |
| 7.2 | Update Doc Tags | ⬜ | - | |
| 7.3 | Update Doc Content | ⬜ | - | |
| 7.4 | Delete Doc | ⬜ | - | |
| 8.1 | Get Statistics | ⬜ | - | |
| 8.2 | Category Distribution | ⬜ | - | |
| 8.3 | Country Statistics | ⬜ | - | |
| 9.1-9.6 | Edge Cases | ⬜ | - | |
| 10.1-10.4 | Performance Tests | ⬜ | - | |

---

## Test Execution Checklist

### Before Testing
- [ ] Ollama is running (`ollama serve`)
- [ ] Model is pulled (`ollama pull llama3.2:3b`)
- [ ] MongoDB is running
- [ ] Backend server is running
- [ ] Database is empty or clean state
- [ ] All required dependencies installed

### During Testing
- [ ] Record response times
- [ ] Check Ollama logs for errors
- [ ] Monitor MongoDB connections
- [ ] Verify no memory leaks
- [ ] Check for error messages

### After Testing
- [ ] All tests passed
- [ ] Performance acceptable
- [ ] Access control verified
- [ ] Document integrity confirmed
- [ ] Generate test report

---

## Known Issues & Limitations

1. **First Query Slow**: Initial Ollama model loading takes 5-10 seconds
2. **Embedding Time**: Large documents take longer to index
3. **Context Window**: Very long documents may be truncated
4. **Concurrent Limits**: High concurrent load may slow responses

---

## Test Coverage Summary

- ✅ **Health & Setup**: 1 test
- ✅ **Document Creation**: 5 tests
- ✅ **NLP Chat**: 8 tests
- ✅ **Access Control**: 5 tests (CRITICAL)
- ✅ **Search**: 6 tests
- ✅ **Listing**: 5 tests
- ✅ **Management**: 4 tests
- ✅ **Statistics**: 3 tests
- ✅ **Edge Cases**: 6 tests
- ✅ **Performance**: 4 tests
- ✅ **Integration**: 2 tests
- ✅ **Data Integrity**: 3 tests

**Total: 47+ Comprehensive Tests**

---

## Success Criteria

### Must Pass (Critical)
- ✅ All access control tests (4.1-4.5)
- ✅ All chat interface tests (3.1-3.8)
- ✅ Document creation and indexing (2.1-2.5)
- ✅ Search functionality (5.1-5.6)

### Should Pass (Important)
- ✅ All listing tests (6.1-6.5)
- ✅ Document management (7.1-7.4)
- ✅ Statistics accuracy (8.1-8.3)

### Nice to Have
- ✅ Performance within acceptable ranges
- ✅ Graceful error handling
- ✅ Integration workflows smooth

---

## Final Validation

After completing all tests:

1. **Functional Requirements**:
   - [ ] Role-based access control working
   - [ ] NLP chat provides relevant answers
   - [ ] Document upload and indexing successful
   - [ ] Search returns accurate results
   - [ ] All CRUD operations functional

2. **Performance Requirements**:
   - [ ] Chat queries: < 5 seconds (after initial load)
   - [ ] Search queries: < 3 seconds
   - [ ] Document indexing: < 15 seconds
   - [ ] Concurrent requests handled

3. **Security Requirements**:
   - [ ] Agents cannot access tech docs
   - [ ] Technicians cannot access mission docs
   - [ ] Category enforcement strict
   - [ ] No data leakage across roles

4. **Quality Requirements**:
   - [ ] Answers are relevant and accurate
   - [ ] Summaries capture key information
   - [ ] Matched points are specific
   - [ ] Confidence scores reasonable

---

**Test Report Date**: _________________
**Tester**: _________________
**Environment**: _________________
**Overall Status**: ⬜ PASS / ⬜ FAIL
**Notes**: _________________

---

## Automated Testing Script

Save as `run_tests.py`:

```python
import requests
import time
import json

BASE_URL = "http://localhost:8000/kb"

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_chat_agent():
    print("Testing agent chat...")
    data = {
        "query": "What missions were conducted in Germany?",
        "user_role": "agent",
        "limit": 5
    }
    response = requests.post(f"{BASE_URL}/chat", json=data)
    assert response.status_code == 200
    result = response.json()
    assert len(result["data"]["matched_documents"]) > 0
    print("✅ Agent chat test passed")

def test_access_control():
    print("Testing access control...")
    data = {
        "query": "CCTV setup instructions",
        "user_role": "agent",
        "limit": 5
    }
    response = requests.post(f"{BASE_URL}/chat", json=data)
    result = response.json()
    # Should have no technician documents
    for doc in result["data"]["matched_documents"]:
        assert doc["category"] == "agent"
    print("✅ Access control test passed")

if __name__ == "__main__":
    test_health()
    time.sleep(1)
    test_chat_agent()
    time.sleep(2)
    test_access_control()
    print("\n✅ All automated tests passed!")
```

---

**End of Comprehensive Testing Guide**
