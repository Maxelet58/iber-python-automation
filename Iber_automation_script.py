"""
Iber 2D Flood Risk Automation Script
Author: Marcel Manresa Masgoret
Description: 
This script automates the batch execution of Iber 2D hydraulic simulations. 
It programmatically modifies the base calculation files (Iber2D.dat and Iber_Breach.dat) 
for various stress-test scenarios, executes the Iber solver in the background, 
and isolates the raster output folders for subsequent GIS spatial analysis.
"""

import os
import shutil
import subprocess
import time
from datetime import datetime

def log_event(message, log_file_path):
    """Generates a timestamped log entry in the console and saves it to a text file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(log_file_path, 'a', encoding='utf-8') as file:
        file.write(log_line + "\n")

def run_automated_iber_batch():
    # =========================================================================
    # 1. PATH CONFIGURATION (Update these variables to match local directories)
    # =========================================================================
    # Define the root directory where the Iber project (.gid) is located
    WORKSPACE_DIR = r"C:\Path\To\Your\Workspace" 
    PROJECT_FOLDER_NAME = "Project.gid"
    PROJECT_BASE_NAME = "Project" # Base name used in Iber command-line execution
    
    # Path to the Iber solver executable
    IBER_EXECUTABLE_PATH = r"C:\Path\To\Iber\Iber 3.4\problemtypes\IBER.gid\bin\windows\Iber"
    
    # Internal project file paths
    PROJECT_DIR = os.path.join(WORKSPACE_DIR, PROJECT_FOLDER_NAME)
    FILE_2D_DAT = os.path.join(PROJECT_DIR, "Iber2D.dat")
    FILE_BREACH_DAT = os.path.join(PROJECT_DIR, "Iber_Breach.dat")
    IBER_CMD_ARGUMENT = os.path.join(PROJECT_DIR, PROJECT_BASE_NAME)
    
    LOG_FILE = os.path.join(WORKSPACE_DIR, "simulation_log.txt")
    
    # =========================================================================
    # 2. SCENARIO MATRIX & BASELINE PARAMETERS
    # =========================================================================
    scenarios = [
        {"name": "00_Baseline", "manning": "0.05", "breach_time": "60", "inflow_vimbodi": "351", "inflow_riba": "478"},
        {"name": "01_Forest_Risk", "manning": "0.08", "breach_time": "60", "inflow_vimbodi": "351", "inflow_riba": "478"},
        {"name": "02_Gradual_Collapse", "manning": "0.05", "breach_time": "900", "inflow_vimbodi": "351", "inflow_riba": "478"},
        {"name": "03_Hydraulic_Limit", "manning": "0.05", "breach_time": "60", "inflow_vimbodi": "702", "inflow_riba": "956"},
        {"name": "04_Total_Disaster", "manning": "0.10", "breach_time": "60", "inflow_vimbodi": "775", "inflow_riba": "1000"}
    ]

    baseline = {
        "manning": "0.05",
        "breach_time": "60",
        "inflow_vimbodi": "351",
        "inflow_riba": "478"
    }

    # Clean previous log file
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    log_event("=== STARTING IBER SIMULATION AUTOMATION ===", LOG_FILE)
    
    # =========================================================================
    # 3. MEMORY BACKUP OF ORIGINAL FILES
    # =========================================================================
    log_event("Reading and storing baseline .dat files in memory...", LOG_FILE)
    with open(FILE_2D_DAT, 'r', encoding='utf-8') as f:
        backup_2d = f.readlines()
    with open(FILE_BREACH_DAT, 'r', encoding='utf-8') as f:
        backup_breach = f.readlines()

    total_start_time = time.time()

    # =========================================================================
    # 4. EXECUTION LOOP
    # =========================================================================
    try:
        for scenario in scenarios:
            scenario_start_time = time.time()
            log_event(f"\n--- PREPARING SCENARIO: {scenario['name']} ---", LOG_FILE)
            
            # 4.1 Modify Iber2D.dat (Manning and Inflow parameters)
            new_lines_2d = []
            for line in backup_2d:
                # Replace Manning coefficient
                if f" {baseline['manning']} " in line and len(line.split()) > 4:
                    line = line.replace(f" {baseline['manning']} ", f" {scenario['manning']} ")
                # Replace inflow discharges
                if f"-{baseline['inflow_vimbodi']} " in line:
                    line = line.replace(f"-{baseline['inflow_vimbodi']} ", f"-{scenario['inflow_vimbodi']} ")
                if f"-{baseline['inflow_riba']} " in line:
                    line = line.replace(f"-{baseline['inflow_riba']} ", f"-{scenario['inflow_riba']} ")
                new_lines_2d.append(line)
                
            with open(FILE_2D_DAT, 'w', encoding='utf-8') as f:
                f.writelines(new_lines_2d)
            log_event("Iber2D.dat successfully configured.", LOG_FILE)

            # 4.2 Modify Iber_Breach.dat (Breach time parameter)
            new_lines_breach = []
            for line in backup_breach:
                if f" {baseline['breach_time']} " in line:
                    line = line.replace(f" {baseline['breach_time']} ", f" {scenario['breach_time']} ")
                new_lines_breach.append(line)
                
            with open(FILE_BREACH_DAT, 'w', encoding='utf-8') as f:
                f.writelines(new_lines_breach)
            log_event("Iber_Breach.dat successfully configured.", LOG_FILE)

            # 4.3 Trigger Iber Solver
            log_event(f"Launching Iber calculation engine for {scenario['name']}...", LOG_FILE)
            
            # Purge previous results to prevent false positive outputs
            iber_results_folder = os.path.join(PROJECT_DIR, "RasterResults")
            if os.path.exists(iber_results_folder):
                shutil.rmtree(iber_results_folder)

            # Execute the solver process
            subprocess.run([IBER_EXECUTABLE_PATH, IBER_CMD_ARGUMENT], cwd=PROJECT_DIR)
            
            # 4.4 Verify Output and Isolate Folder
            scenario_output_folder = os.path.join(PROJECT_DIR, f"RasterResults_{scenario['name']}")
            
            if os.path.exists(iber_results_folder):
                if os.path.exists(scenario_output_folder):
                    shutil.rmtree(scenario_output_folder)
                os.rename(iber_results_folder, scenario_output_folder)
                log_event(f"[SUCCESS] Calculation complete. Results isolated at: RasterResults_{scenario['name']}", LOG_FILE)
            else:
                log_event(f"[CRITICAL ERROR] Iber failed to generate RasterResults for {scenario['name']}. Possible divergence.", LOG_FILE)

            # Individual scenario time tracking
            scenario_end_time = time.time()
            scenario_duration_min = (scenario_end_time - scenario_start_time) / 60
            log_event(f"Scenario computation time: {scenario_duration_min:.2f} minutes", LOG_FILE)

    except Exception as e:
        log_event(f"[FATAL ERROR] Script interrupted unexpectedly: {str(e)}", LOG_FILE)
        
    finally:
        # =========================================================================
        # 5. MANDATORY RESTORATION PROTOCOL
        # =========================================================================
        log_event("\n--- INITIATING RESTORATION PROTOCOL ---", LOG_FILE)
        with open(FILE_2D_DAT, 'w', encoding='utf-8') as f:
            f.writelines(backup_2d)
        with open(FILE_BREACH_DAT, 'w', encoding='utf-8') as f:
            f.writelines(backup_breach)
        log_event("[OK] Baseline .dat files successfully restored to original values.", LOG_FILE)

        total_end_time = time.time()
        total_duration_hours = (total_end_time - total_start_time) / 3600
        log_event(f"\n=== BATCH PROCESS COMPLETED IN {total_duration_hours:.2f} HOURS ===", LOG_FILE)

if __name__ == "__main__":
    run_automated_iber_batch()