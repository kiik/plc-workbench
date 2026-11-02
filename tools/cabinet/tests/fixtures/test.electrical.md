# Test station: electrical

Status: test fixture

Test fixture for `tools/cabinet`: fictional devices and parts, not a real machine. It has a known
part, unknown parts (`?`), a rail overflow (row 4), a duct with unknown height and an enclosure
with a known plate and Max power loss (`+CAB1`), and one with an unknown enclosure (`+CAB2`).

## 1. Locations

| Location | Name | Notes |
|---|---|---|
| `+CAB1` | Test cabinet | |
| `+CAB2` | Test box, enclosure unknown | |
| `+ST1` | Test station plate | |

## 2. Devices

| Designation | Label | Tag | Name | Part |
|---|---|---|---|---|
| `+CAB1-FC1` | ? | | Supply protection | [Testco TC-CB-1](parts/testco-tc-cb-1.md) |
| `+CAB1-TC1` | ? | | 24 V DC power supply | [Testco TC-PSU-24](parts/testco-tc-psu-24.md) |
| `+CAB1-KE1` | ? | | PLC | ? |
| `+CAB1-XD1` | X1 | | Terminal: 24 V | [Testco TC-TERM-5](parts/testco-tc-term-5.md) |
| `+CAB1-XD2` | X2 | | Terminal: 0 V | [Testco TC-TERM-5](parts/testco-tc-term-5.md) |
| `=MAG+CAB1-KF1` | ? | | Relay module 1 | [Testco TC-RELAY-110](parts/testco-tc-relay-110.md) |
| `=MAG+CAB1-KF2` | ? | | Relay module 2 | [Testco TC-RELAY-110](parts/testco-tc-relay-110.md) |
| `=MAG+CAB1-KF3` | ? | | Relay module 3 | [Testco TC-RELAY-110](parts/testco-tc-relay-110.md) |
| `+CAB2-KE2` | RIO | | Remote I/O | ? |
| `=MAG+ST1-BG1` | ? | 1S1 | Cylinder extended | ? |

## 7. Layout

### Enclosures

| Location | Part | Notes |
|---|---|---|
| `+CAB1` | [Testco TC-BOX-300](parts/testco-tc-box-300.md) | |
| `+CAB2` | ? | ?1 |

### Rows

| Location | Row | Kind | Height | Contents |
|---|---|---|---|---|
| `+CAB1` | 1 | duct | 40 | |
| `+CAB1` | 2 | rail | | `+CAB1-FC1`, `+CAB1-TC1`, `+CAB1-KE1`, `+CAB1-XD1`, `+CAB1-XD2` |
| `+CAB1` | 3 | duct | ? | |
| `+CAB1` | 4 | rail | | `=MAG+CAB1-KF1`, `=MAG+CAB1-KF2`, `=MAG+CAB1-KF3` |
| `+CAB1` | 5 | duct | 40 | |
| `+CAB2` | 1 | rail | | `+CAB2-KE2` |

## 8. Open questions

- [ ] **?1** Which enclosure is `+CAB2`? Layout, Part `?`. Test fixture.
