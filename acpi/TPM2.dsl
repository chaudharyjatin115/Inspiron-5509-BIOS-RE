/*
 * Intel ACPI Component Architecture
 * AML/ASL+ Disassembler version 20251212 (64-bit version)
 * Copyright (c) 2000 - 2025 Intel Corporation
 * 
 * Disassembly of tpm2.dat
 *
 * ACPI Data Table [TPM2]
 *
 * Format: [HexOffset DecimalOffset ByteLength]  FieldName : FieldValue (in hex)
 */

[000h 0000 004h]                   Signature : "TPM2"    [Trusted Platform Module hardware interface Table]
[004h 0004 004h]                Table Length : 0000004C
[008h 0008 001h]                    Revision : 04
[009h 0009 001h]                    Checksum : 91
[00Ah 0010 006h]                      Oem ID : "DELL  "
[010h 0016 008h]                Oem Table ID : "Dell Inc"
[018h 0024 004h]                Oem Revision : 00000002
[01Ch 0028 004h]             Asl Compiler ID : "    "
[020h 0032 004h]       Asl Compiler Revision : 01000013

[024h 0036 002h]              Platform Class : 0000
[026h 0038 002h]                    Reserved : 0000
[028h 0040 008h]             Control Address : 00000000FED40040
[030h 0048 004h]                Start Method : 07 [Command Response Buffer]

[034h 0052 00Ch]           Method Parameters : 00 00 00 00 00 00 00 00 00 00 00 00
[040h 0064 004h]          Minimum Log Length : 00010000
[044h 0068 008h]                 Log Address : 0000000061CF0000

Raw Table Data: Length 76 (0x4C)

    0000: 54 50 4D 32 4C 00 00 00 04 91 44 45 4C 4C 20 20  // TPM2L.....DELL  
    0010: 44 65 6C 6C 20 49 6E 63 02 00 00 00 20 20 20 20  // Dell Inc....    
    0020: 13 00 00 01 00 00 00 00 40 00 D4 FE 00 00 00 00  // ........@.......
    0030: 07 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  // ................
    0040: 00 00 01 00 00 00 CF 61 00 00 00 00              // .......a....
