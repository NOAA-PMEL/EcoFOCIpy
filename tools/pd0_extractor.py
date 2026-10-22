#!/bin/env python3

#Program for converting RDI pd0 files to text from the factory binary file
#written with gemini during FA2605 cruise. 






import argparse
import struct
import sys
import os
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Extract data from Teledyne RDI PD0 binary files.")
    parser.add_argument("-i", "--input", required=True, help="Input PD0 binary file path")
    parser.add_argument("-s", "--serial", default="auto", 
                        help="Instrument serial number for file naming. Defaults to 'auto' to extract from file.")
    # Remove required=True from type
    parser.add_argument("-t", "--type", 
                        choices=['report', 'intensity', 'correlation', 'pgood', 'velocity', 'scalars', 'all'], 
                        help="Type of data to extract")
    # NEW: Add the serialno flag
    parser.add_argument("-sn", "--serialno", action="store_true", 
                        help="Print the instrument serial number from the file and exit")
    
    args = parser.parse_args()
    
    # Manually check that --type is provided UNLESS they just want the serial number
    if not args.serialno and not args.type:
        parser.error("The following arguments are required: -t/--type (unless using -sn/--serialno)")
        
    return args

def parse_fixed_leader(data):
    """Parses Fixed Leader structure using absolute byte indexing."""
    if len(data) < 59:
        return {}
    
    fw_ver, fw_rev = data[2], data[3]
    sys_cfg = struct.unpack("<H", data[4:6])[0]
    
    # Decode System Configuration
    freq_code = sys_cfg & 0b111
    freq_map = {0: "75", 1: "150", 2: "300", 3: "600", 4: "1200", 5: "2400"}
    freq = freq_map.get(freq_code, "300")
    
    pattern = "Convex" if (sys_cfg & 0b1000) else "Concave"
    head_attached = "attached" if (sys_cfg & 0b1000000) else "not attached"
    orientation = "Up-looking" if (sys_cfg & 0b10000000) else "Down-looking"
    
    beam_angle_code = (sys_cfg >> 8) & 0b11
    angle_map = {0: "15", 1: "20", 2: "30"}
    beam_angle = angle_map.get(beam_angle_code, "20")
    
    num_beams = data[8]
    num_bins = data[9]
    pings_per_ens = struct.unpack("<H", data[10:12])[0]
    bin_length_cm = struct.unpack("<H", data[12:14])[0]
    blank_cm = struct.unpack("<H", data[14:16])[0]
    prof_mode = data[16]
    
    tpp_min, tpp_sec, tpp_hundredths = data[22], data[23], data[24]
    time_per_ping_sec = tpp_min * 60 + tpp_sec + (tpp_hundredths / 100.0)
    
    bin1_dist_cm = struct.unpack("<H", data[32:34])[0]
    xmit_pulse_cm = struct.unpack("<H", data[34:36])[0]
    serial_number = struct.unpack("<I", data[54:58])[0]
    
    return {
        'firmware': f"{fw_ver}.{fw_rev:02d}",
        'frequency': freq,
        'beam_pattern': pattern,
        'head_attached': head_attached,
        'orientation': orientation,
        'beam_angle': beam_angle,
        'beams': num_beams,
        'bins': num_bins,
        'pings': pings_per_ens,
        'bin_len': bin_length_cm,
        'blank': blank_cm,
        'prof_mode': prof_mode,
        'time_ping': f"{time_per_ping_sec:.2f}",
        'dist1': bin1_dist_cm,
        'xmit_len': xmit_pulse_cm,
        'serial_no': serial_number
    }

def parse_variable_leader(data):
    """Parses Variable Leader date and time values handling Y2K standards."""
    if len(data) < 64:
        return None
    
    ens_num = struct.unpack("<H", data[2:4])[0]
    
    # Check Y2K compliant RTC starting at byte 59 (index 58)
    year = data[58]
    month = data[59]
    day = data[60]
    hour = data[61]
    minute = data[62]
    second = data[63]
    
    # Fallback to standard RTC at byte 5 (index 4) if Y2K is completely zeroed
    if year == 0 and month == 0 and day == 0:
        year = data[4]
        month = data[5]
        day = data[6]
        hour = data[7]
        minute = data[8]
        second = data[9]
        
    century = 2000 if year < 70 else 1900
    if len(data) >= 65 and data[57] > 0:
        century = data[57] * 100
        
    full_year = century + year
    
    try:
        dt = datetime(full_year, month, day, hour, minute, second)
    except ValueError:
        dt = datetime(2000, 1, 1, 0, 0, 0)
        
    return ens_num, dt

def extract_pd0(input_file):
    """Reads PD0 file using strict checksum validation and returns decoded ensembles."""
    ensembles = []
    
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'.")
        sys.exit(1)
        
    i = 0
    valid_ensembles = 0
    
    while i < len(data) - 1:
        if data[i] == 0x7F and data[i+1] == 0x7F:
            if i + 4 > len(data):
                break
                
            ensemble_len = struct.unpack('<H', data[i+2:i+4])[0]
            
            if i + ensemble_len + 2 > len(data):
                break
                
            ensemble = data[i:i+ensemble_len]
            
            # Verify Checksum
            expected_checksum = struct.unpack('<H', data[i+ensemble_len:i+ensemble_len+2])[0]
            calculated_checksum = sum(ensemble) & 0xFFFF
            
            if expected_checksum == calculated_checksum:
                ens_data = process_ensemble_chunks(ensemble)
                if ens_data:
                    ensembles.append(ens_data)
                    valid_ensembles += 1
                i += ensemble_len + 2
                continue
            else:
                i += 1
        else:
            i += 1
            
    print(f"Extraction complete. Successfully decoded {valid_ensembles} valid ensembles.")
    return ensembles

def process_ensemble_chunks(ensemble):
    num_data_types = ensemble[5]
    offsets = []
    
    for j in range(num_data_types):
        offset_idx = 6 + j * 2
        if offset_idx + 2 <= len(ensemble):
            offsets.append(struct.unpack('<H', ensemble[offset_idx:offset_idx+2])[0])
            
    ens_data = {}
    
    for offset in offsets:
        if offset + 2 > len(ensemble):
            continue
            
        data_id = struct.unpack('<H', ensemble[offset:offset+2])[0]
        
        # Match Little-Endian Hex IDs exactly
        if data_id == 0x0000:
            ens_data['fixed'] = parse_fixed_leader(ensemble[offset:])
        elif data_id == 0x0080:
            ens_data['var_leader'] = ensemble[offset:]
            v_data = parse_variable_leader(ensemble[offset:])
            if v_data:
                ens_data['ens_num'], ens_data['datetime'] = v_data
        elif data_id == 0x0100:
            ens_data['velocity'] = ensemble[offset:]
        elif data_id == 0x0200:
            ens_data['correlation'] = ensemble[offset:]
        elif data_id == 0x0300:
            ens_data['intensity'] = ensemble[offset:]
        elif data_id == 0x0400:
            ens_data['pgood'] = ensemble[offset:]

    if 'fixed' in ens_data and 'datetime' in ens_data:
        return ens_data
    return None

def generate_report(output_file, config):
    """Generates ASCII report text matching DOS style."""
    report_content = f"""REPORT FOR ASCII DATA CONVERSION
--------------------------------

1. ADCP INFORMATION:
   Frequency {config.get('frequency', '300')} kHz
   Beam angle {config.get('beam_angle', '20')} deg
   {config.get('beams', '4')} beam system
   {config.get('orientation', 'Up-looking')} orientation
   {config.get('beam_pattern', 'Convex')} beam pattern
   Transducer head {config.get('head_attached', 'attached')}
   CPU firmware {config.get('firmware', '50.41')}
   Serial Number {config.get('serial_no', 'xxx')}

2. ADCP SETUP:
   Number of bins {config.get('bins', '19')}
   Bin length {config.get('bin_len', '400')} cm
   Blank after transmit {config.get('blank', '176')} cm
   Distance to first bin {config.get('dist1', '621')} cm
   Transmit length {config.get('xmit_len', '441')} cm
   Pings per ensemble {config.get('pings', '50')}
   Time per ping {config.get('time_ping', '72.00')} s
   Profiling mode {config.get('prof_mode', '1')}

3. ASCII FILE DATA FORMAT:
   Line 1-{config.get('bins', '19')}: Recording date string, Recording time string, Bin number, Beam 1, 2, 3, 4

4. PROCESSING PARAMETERS:
   Velocity units: ADCP
   Velocity reference: ADCP
   Depth units: ADCP
   Bins: From 1 to {config.get('bins', '19')} skip 0 bin
   Magnetic variation 0.00 deg
   Do not mark data below bottom

END OF REPORT
-------------
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f" -> Created {output_file}")

def export_data(output_file, ensembles, data_type):
    """Generates formatted time series ASCII text files mimicking BBATCH."""
    if not ensembles:
        return

    with open(output_file, 'w', encoding='utf-8') as f:
        for ens in ensembles:
            dt = ens['datetime']
            year_val = dt.year % 100
            
            # --- Handle Scalar Environmental Data (.SCA) ---
            if data_type == 'scalars':
                var_buf = ens.get('var_leader')
                if var_buf and len(var_buf) >= 34:
                    # Bytes 27,28 (Index 26) = Temperature
                    temp = struct.unpack('<h', var_buf[26:28])[0] / 100.0
                    # Bytes 19,20 (Index 18) = Heading
                    heading = struct.unpack('<H', var_buf[18:20])[0] / 100.0
                    # Bytes 21,22 (Index 20) = Pitch
                    pitch = struct.unpack('<h', var_buf[20:22])[0] / 100.0
                    # Bytes 23,24 (Index 22) = Roll
                    roll = struct.unpack('<h', var_buf[22:24])[0] / 100.0
                    
                    # Byte 32 (Index 31) = Heading Std Dev
                    h_std = var_buf[31]
                    # Byte 33 (Index 32) = Pitch Std Dev
                    p_std = var_buf[32]
                    # Byte 34 (Index 33) = Roll Std Dev
                    r_std = var_buf[33]
                    
                    # Formatted to perfectly mimic: "25/04/23 00:00:00 1  8.35 144.72 -26.29 -31.42    20    19    10"
                    out_str = f"{year_val:02d}/{dt.month:02d}/{dt.day:02d} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} 1 {temp:5.2f} {heading:6.2f} {pitch:6.2f} {roll:6.2f}{h_std:6d}{r_std:6d}{p_std:6d}\n"
                    f.write(out_str)
                continue

            # --- Handle Bin-based Array Data ---
            raw_buf = ens.get(data_type)
            if not raw_buf:
                continue

            num_bins = ens['fixed']['bins']
            for bin_idx in range(num_bins):
                bin_num = bin_idx + 1

                if data_type in ['intensity', 'correlation', 'pgood']:
                    start = 2 + (bin_idx * 4)
                    if start + 4 <= len(raw_buf):
                        b1, b2, b3, b4 = raw_buf[start:start+4]
                        out_str = f"{year_val:02d}/{dt.month:02d}/{dt.day:02d} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}{bin_num:>4}{b1:>7}{b2:>7}{b3:>7}{b4:>7}\n"
                        f.write(out_str)

                elif data_type == 'velocity':
                    start = 2 + (bin_idx * 8)
                    if start + 8 <= len(raw_buf):
                        v1, v2, v3, v4 = struct.unpack('<hhhh', raw_buf[start:start+8])
                        # Apply BBATCH 99999 mask for bad data
                        v1 = 99999 if v1 == -32768 else v1
                        v2 = 99999 if v2 == -32768 else v2
                        v3 = 99999 if v3 == -32768 else v3
                        v4 = 99999 if v4 == -32768 else v4
                        
                        out_str = f"{year_val:02d}/{dt.month:02d}/{dt.day:02d} {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}{bin_num:>4}{v1:>7}{v2:>7}{v3:>7}{v4:>7}\n"
                        f.write(out_str)

    print(f" -> Created {output_file}")

def main():
    args = parse_args()
    
    ext_map = {
        'report': 'RPT',
        'intensity': 'EIN',
        'correlation': 'COR',
        'pgood': 'PG',
        'velocity': 'VEL',
        'scalars': 'SCA'
    }
    
    if args.type == 'all':
        types_to_process = ['report', 'intensity', 'pgood', 'velocity', 'scalars']
    else:
        types_to_process = [args.type]
        
    print(f"Reading {args.input}...")
    ensembles = extract_pd0(args.input)
    
    if not ensembles:
        print("Error: Could not extract any valid ensembles. File may be corrupted.")
        sys.exit(1)
    
    # --- NEW: Just print the serial number and exit if -sn is used ---
    if args.serialno:
        extracted_serial = ensembles[0]['fixed'].get('serial_no', 0)
        print("\n========================================")
        if not extracted_serial or extracted_serial == 0 or extracted_serial > 999999:
            print(f"INSTRUMENT SERIAL NUMBER: INVALID/MISSING ({extracted_serial})")
        else:
            print(f"INSTRUMENT SERIAL NUMBER: {extracted_serial}")
        print("========================================\n")
        sys.exit(0)  # Stop the script here!
    
    # --- NEW: Auto-detect serial number logic ---
    if args.serial.lower() == 'auto':
        # Grab the serial number we successfully parsed on line 42
        extracted_serial = ensembles[0]['fixed'].get('serial_no', 0)
        
        # Halt if missing, exactly 0, or unrealistically large (e.g., > 999999)
        if not extracted_serial or extracted_serial == 0 or extracted_serial > 999999:
            print(f"Error: Invalid or corrupted serial number detected in file ({extracted_serial}).")
            print("Please run the script again and manually assign one using: -s YOUR_SERIAL")
            sys.exit(1)
            
        file_prefix = str(extracted_serial)
        print(f"Auto-detected Serial Number: {file_prefix}")
    else:
        file_prefix = args.serial

    for current_type in types_to_process:
        output_filename = f"{file_prefix}.{ext_map[current_type]}"
        
        if current_type == 'report':
            config = ensembles[0]['fixed']
            generate_report(output_filename, config)
        else:
            export_data(output_filename, ensembles, current_type)

if __name__ == "__main__":
    main()