# Water Level Data Integration Script
# PowerShell version for processing CSV files

Write-Host "Starting Water Level Data Integration..." -ForegroundColor Green
Write-Host "=" * 60

# Set paths
$inputDir = "..\Data\Niveles"
$outputFile = "calamar.csv"
$logFile = "integration.log"

# Function to log messages
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp | $($Level.PadRight(8)) | $Message"
    Write-Host $logMessage
    Add-Content -Path $logFile -Value $logMessage
}

# Initialize log
if (Test-Path $logFile) { Remove-Item $logFile }
Write-Log "Water Level Data Integration Started"
Write-Log "Input directory: $inputDir"
Write-Log "Output file: $outputFile"

# Find CSV files
if (!(Test-Path $inputDir)) {
    Write-Log "Input directory does not exist: $inputDir" "ERROR"
    exit 1
}

$csvFiles = Get-ChildItem -Path $inputDir -Filter "Calamar*.csv"
if ($csvFiles.Count -eq 0) {
    Write-Log "No Calamar*.csv files found in input directory" "ERROR"
    exit 1
}

Write-Log "Found $($csvFiles.Count) CSV files:"
foreach ($file in $csvFiles) {
    Write-Log "  - $($file.Name)"
}

# Process each CSV file
$dataFrames = @()
foreach ($file in $csvFiles) {
    Write-Log "Processing $($file.Name)..."
    
    try {
        # Read CSV
        $df = Import-Csv $file.FullName
        Write-Log "  Read $($df.Count) rows and $($df[0].PSObject.Properties.Name.Count) columns"
        
        # Clean and format data
        $cleanedData = @()
        foreach ($row in $df) {
            $cleanedRow = @{}
            
            # Process each column
            foreach ($prop in $row.PSObject.Properties) {
                $value = $prop.Value.Trim()
                
                # Handle date formatting
                if ($prop.Name -eq 'Fecha') {
                    # Extract date part (remove time)
                    if ($value -match '(\d{4})-(\d{1,2})-(\d{1,2})') {
                        $year = $matches[1]
                        $month = $matches[2].PadLeft(2, '0')
                        $day = $matches[3].PadLeft(2, '0')
                        $cleanedRow['Fecha'] = "$year-$month-$day"
                    } else {
                        $cleanedRow['Fecha'] = $value
                    }
                } else {
                    $cleanedRow[$prop.Name] = $value
                }
            }
            
            # Only add rows with valid data
            if ($cleanedRow['Fecha'] -and $cleanedRow['Valor']) {
                $cleanedData += [PSCustomObject]$cleanedRow
            }
        }
        
        Write-Log "  Cleaned data: $($cleanedData.Count) valid rows"
        $dataFrames += ,$cleanedData
        
    } catch {
        Write-Log "  Error processing $($file.Name): $($_.Exception.Message)" "ERROR"
    }
}

if ($dataFrames.Count -eq 0) {
    Write-Log "No valid data found to process" "ERROR"
    exit 1
}

# Merge all data
Write-Log "Merging CSV files..."
$mergedData = @()
foreach ($df in $dataFrames) {
    $mergedData += $df
}

# Remove duplicates
$uniqueData = $mergedData | Sort-Object -Property Fecha -Unique
$duplicatesRemoved = $mergedData.Count - $uniqueData.Count
if ($duplicatesRemoved -gt 0) {
    Write-Log "Removed $duplicatesRemoved duplicate rows"
}

# Sort by date
$sortedData = $uniqueData | Sort-Object -Property Fecha

Write-Log "Final dataset: $($sortedData.Count) records"

# Data validation
Write-Log "Performing data validation..."
$validationResults = @{
    total_rows = $sortedData.Count
    missing_dates = 0
    missing_values = 0
    invalid_dates = 0
}

foreach ($row in $sortedData) {
    if ([string]::IsNullOrEmpty($row.Fecha)) { $validationResults.missing_dates++ }
    if ([string]::IsNullOrEmpty($row.Valor)) { $validationResults.missing_values++ }
    
    # Validate date format
    if ($row.Fecha -and $row.Fecha -notmatch '^\d{4}-\d{2}-\d{2}$') {
        $validationResults.invalid_dates++
    }
}

Write-Log "=== Data Validation Results ==="
Write-Log "Total rows: $($validationResults.total_rows)"
Write-Log "Missing dates: $($validationResults.missing_dates)"
Write-Log "Missing values: $($validationResults.missing_values)"
Write-Log "Invalid dates: $($validationResults.invalid_dates)"

# Generate summary
if ($sortedData.Count -gt 0) {
    $firstDate = $sortedData[0].Fecha
    $lastDate = $sortedData[-1].Fecha
    $uniqueDates = ($sortedData | Select-Object -Property Fecha -Unique).Count
    $uniqueStations = ($sortedData | Select-Object -Property CodigoEstacion -Unique).Count
    
    Write-Log "=== Integration Summary ==="
    Write-Log "Date range: $firstDate to $lastDate"
    Write-Log "Unique dates: $uniqueDates"
    Write-Log "Unique stations: $uniqueStations"
    
    # Water level statistics
    $values = $sortedData | ForEach-Object { [double]$_.Valor } | Where-Object { $_ -ne $null }
    if ($values.Count -gt 0) {
        $minValue = ($values | Measure-Object -Minimum).Minimum
        $maxValue = ($values | Measure-Object -Maximum).Maximum
        $avgValue = ($values | Measure-Object -Average).Average
        
        Write-Log "Water level statistics:"
        Write-Log "  Min: $([math]::Round($minValue, 2)) cm"
        Write-Log "  Max: $([math]::Round($maxValue, 2)) cm"
        Write-Log "  Mean: $([math]::Round($avgValue, 2)) cm"
    }
}

# Save to CSV
Write-Log "Saving integrated data to $outputFile..."
try {
    # Convert to CSV format
    $csvContent = @()
    
    # Add header
    if ($sortedData.Count -gt 0) {
        $headers = $sortedData[0].PSObject.Properties.Name -join ","
        $csvContent += $headers
        
        # Add data rows
        foreach ($row in $sortedData) {
            $values = @()
            foreach ($prop in $row.PSObject.Properties) {
                $values += '"' + $prop.Value + '"'
            }
            $csvContent += $values -join ","
        }
    }
    
    # Save file
    $csvContent | Out-File -FilePath $outputFile -Encoding UTF8
    
    Write-Log "Successfully saved $($sortedData.Count) rows to $outputFile"
    
} catch {
    Write-Log "Failed to save output file: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Log "=" * 60
Write-Log "Water Level Data Integration Completed Successfully!" -ForegroundColor Green
Write-Log "=" * 60

# Display final file info
$fileInfo = Get-Item $outputFile
Write-Log "Output file: $($fileInfo.FullName)"
Write-Log "File size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB"
Write-Log "Records: $($sortedData.Count)"