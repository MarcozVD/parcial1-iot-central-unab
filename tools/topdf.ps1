param([string]$Docx, [string]$Pdf)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open($Docx, $false, $false)
  foreach ($t in $d.TablesOfContents) { $t.Update() }
  $d.Fields.Update() | Out-Null
  $d.Save()
  $d.ExportAsFixedFormat($Pdf, 17)
  "PAGES=" + $d.ComputeStatistics(2)
  $d.Close()
} finally { $w.Quit() }
