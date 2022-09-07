# Externe Klassen werden importiert
from ij import IJ, WindowManager, ImagePlus
from ij.measure import ResultsTable
from ij.plugin.filter import AVI_Writer
import os

# Ordnernamen durch Nutzer holen
ordnerName = IJ.getDirectory("Select a directory")
listeDateinamen = os.listdir(ordnerName)

# Parameterliste
parameterListRadius = [1,2]
parameterListLineWidth = [10,9,8,7,6]
parameterListLineExtend = ["","extend_line"]

# Listen erstellen (ohne Inhalt)
listeKombination = []
listeSchlechteDateien = []
listeGuteDateien = []

# Inhalt der Kombinationsliste mit Parameter
for lineWidth in parameterListLineWidth:
    for radius in parameterListRadius:
        for extend in parameterListLineExtend:
            # Kombination an Liste anfügen
            listeKombination.append([lineWidth, radius, extend])

# Finde passende Kombination = True, falls nicht = False
def Auswertung(kombination, dateiName):
    lineWidth = kombination[0]
    radius = kombination[1]
    extend = kombination[2]
    zeilenAnzahl = 0

    try:
        IJ.open(ordnerName + dateiName)
        IJ.selectWindow(dateiName)
        # Nimmt das geöffnete Bild
        imp = IJ.getImage()
        anzahlFrames = imp.getImageStackSize()
        IJ.runMacro("""run("8-bit");run("Subtract Background...", "rolling=150 light stack");""")
        command = 'run("Variance...", "radius={} stack");'.format(radius)
        IJ.runMacro(command)
        IJ.runMacro("""run("Invert", "stack")""")
        command = 'run("Enhance Contrast...", "saturated=0.35 normalize process_all");'
        IJ.runMacro(command)
        # Avi zwischenspeichern "ridged_cell"
        impRidged = imp.duplicate()

        IJ.runMacro(command)
        command = 'run("Ridge Detection", "line_width={} high_contrast=230 low_contrast=87 darkline {} displayresults method_for_overlap_resolution=NONE minimum_line_length=350 maximum=500 stack");'.format(
            lineWidth, extend)
        IJ.runMacro(command)
        # avi zwischenspeichern "red_ridged_cell"
        impridgedRed = imp.duplicate()

        # Entfernt die letzten 4 Buchstaben (.avi)
        fileNameNoExtension = dateiName[:len(dateiName) - 4]
        rt = ResultsTable().getResultsTable("Results")
        su = ResultsTable().getResultsTable("Summary")

        # Schließt das Originalvideo
        imp.changes = False
        imp.close()

        noJunctions = True
        # Result-Datei auf class= closed prüfen
        for zeilenNummer in range(0,rt.size()-1):
            zeile = rt.getRowAsString(zeilenNummer)
            zeileGesplittet = zeile.split("	")
            if zeileGesplittet[7] != "closed":
                noJunctions = False
                # Wenn eine Zeile fehlerhaft ist, wird die Kombination übersprungen
                break

        # Bedingung
        zeilenAnzahl = su.size()
        if (zeilenAnzahl == anzahlFrames) and noJunctions:
            # Nur speichern, wenn Bedingung erfüllt wurden
            aviRidgedPfad = ordnerName + "ridged_" + dateiName
            AVI_Writer().writeImage(impRidged, aviRidgedPfad, 0, 99)
            aviRedRidgedPfad = ordnerName + "red_ridged_" + dateiName
            AVI_Writer().writeImage(impridgedRed, aviRedRidgedPfad, 0, 99)
            su.save(ordnerName +"ridge_" + fileNameNoExtension + "_Summary.csv")
            rt.save(ordnerName +"ridge_" + fileNameNoExtension + "_Results.csv")
            rt.reset()
            return True
        else:
            rt.reset()
            return False

    except Exception as errorMessage:
        print(errorMessage)
        return False

# Definition von kombinationenDurchgehen
def kombinationenDurchgehen(dateiName):
    # Kombination für Datei durchgehen
    for kombination in listeKombination:
        auswertungErfolgreich = Auswertung(kombination, dateiName)
        if auswertungErfolgreich:
            print(" Auswertung fuer ", dateiName, " mit Kombination:", kombination, " erfolgreich ")
            return True
    return False

# Verwendung und Ergebnis von kombinationenDurchgehen
for dateiName in listeDateinamen:
    if dateiName.endswith(".avi"):
            print(" Auswertung fuer ", dateiName, " gestartet ")
            ergebnisAuswertung = kombinationenDurchgehen(dateiName)
            if ergebnisAuswertung:
                listeGuteDateien.append(dateiName)
            else:
                listeSchlechteDateien.append(dateiName)
                print(" Keine Kombination fuer diese Datei zu finden ")

# Ergebnisse ausgeben
print(" Schlechte Dateien:", listeSchlechteDateien)
print(" Gute Dateien:", listeGuteDateien)

# Fenster werden geschlossen
IJ.selectWindow("Junctions")
IJ.run("Close")
IJ.selectWindow("Summary")
IJ.run("Close")
IJ.selectWindow("Results")
IJ.run("Close")
