using System;
using System.Text;

public class CPHInline
{
    private const string Prefix = "smwTrackerPrediction.";

    public bool Execute()
    {
        CPH.SetArgument("smwCommand", "none");

        string line;
        if (!CPH.TryGetArg("line", out line) || String.IsNullOrWhiteSpace(line))
            return true;

        string[] fields = line.Split('|');
        if (fields.Length < 9 || fields[0] != "SMWTRACKER" || fields[1] != "1")
            return true;

        string eventId = fields[2];
        string eventName = fields[3].ToLowerInvariant();
        string sessionId = fields[4];
        string hackTitle = Decode(fields[5]);
        int levelId = ParseInt(fields[6], -1);
        int levelDeaths = Math.Max(0, ParseInt(fields[7], 0));
        string language = fields.Length > 9 ? fields[9] : "en";

        string previousEventId = CPH.GetGlobalVar<string>(Prefix + "lastEventId", false);
        if (eventId == previousEventId)
            return true;
        CPH.SetGlobalVar(Prefix + "lastEventId", eventId, false);

        string activeSession = CPH.GetGlobalVar<string>(Prefix + "sessionId", false);
        bool predictionOpen = CPH.GetGlobalVar<bool>(Prefix + "open", false);
        int startingDeaths = CPH.GetGlobalVar<int>(Prefix + "startingDeaths", false);
        int lifeTarget = CPH.GetGlobalVar<int>(Prefix + "lifeTarget", false);

        if (eventName == "start")
        {
            int completedLevels = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "completedLevels", false)
            );
            int totalLivesUsed = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "totalLivesUsed", false)
            );

            lifeTarget = completedLevels == 0
                ? 100
                : Math.Max(
                    1,
                    (int)Math.Round(
                        totalLivesUsed / (double)completedLevels,
                        MidpointRounding.AwayFromZero
                    )
                );

            CPH.SetGlobalVar(Prefix + "sessionId", sessionId, false);
            CPH.SetGlobalVar(Prefix + "open", true, false);
            CPH.SetGlobalVar(Prefix + "startingDeaths", levelDeaths, false);
            CPH.SetGlobalVar(Prefix + "lifeTarget", lifeTarget, false);

            CPH.SetArgument("smwCommand", "start");
            CPH.SetArgument("smwPredictionTitle", PredictionTitle(language, lifeTarget));
            CPH.SetArgument("smwYesOutcome", YesOutcome(language));
            CPH.SetArgument("smwNoOutcome", NoOutcome(language));
            CPH.SetArgument("smwLifeTarget", lifeTarget);
            CPH.SetArgument("smwHackTitle", hackTitle);
            CPH.SetArgument("smwLevelId", levelId);
            return true;
        }

        if (sessionId != activeSession)
            return true;

        int deathsThisAttempt = Math.Max(0, levelDeaths - startingDeaths);
        CPH.SetArgument("smwLifeTarget", lifeTarget);
        CPH.SetArgument("smwLivesUsed", deathsThisAttempt + 1);
        CPH.SetArgument("smwHackTitle", hackTitle);
        CPH.SetArgument("smwLevelId", levelId);

        if (eventName == "death")
        {
            // Losing the Nth life without clearing makes "within N lives" No.
            if (predictionOpen && deathsThisAttempt >= lifeTarget)
            {
                CPH.SetArgument("smwCommand", "resolve");
                CPH.SetArgument("smwWinningIndex", 1);
                CPH.SetGlobalVar(Prefix + "open", false, false);
            }
            return true;
        }

        if (eventName == "clear")
        {
            int completedLevels = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "completedLevels", false)
            );
            int totalLivesUsed = Math.Max(
                0,
                CPH.GetGlobalVar<int>(Prefix + "totalLivesUsed", false)
            );

            // Clearing with zero deaths used one life, five deaths used six.
            completedLevels += 1;
            totalLivesUsed += deathsThisAttempt + 1;
            CPH.SetGlobalVar(Prefix + "completedLevels", completedLevels, false);
            CPH.SetGlobalVar(Prefix + "totalLivesUsed", totalLivesUsed, false);

            if (predictionOpen)
            {
                CPH.SetArgument("smwCommand", "resolve");
                CPH.SetArgument(
                    "smwWinningIndex",
                    deathsThisAttempt < lifeTarget ? 0 : 1
                );
            }

            CPH.SetGlobalVar(Prefix + "open", false, false);
            CPH.SetGlobalVar(Prefix + "sessionId", "", false);
            return true;
        }

        if (eventName == "cancel")
        {
            if (predictionOpen)
                CPH.SetArgument("smwCommand", "cancel");
            CPH.SetGlobalVar(Prefix + "open", false, false);
            CPH.SetGlobalVar(Prefix + "sessionId", "", false);
        }

        return true;
    }

    private static int ParseInt(string value, int fallback)
    {
        int parsed;
        return Int32.TryParse(value, out parsed) ? parsed : fallback;
    }

    private static string Decode(string value)
    {
        try
        {
            return Encoding.UTF8.GetString(Convert.FromBase64String(value));
        }
        catch
        {
            return "";
        }
    }

    private static string PredictionTitle(string language, int target)
    {
        switch ((language ?? "en").ToLowerInvariant())
        {
            case "es":
                return "¿Superaré este nivel en " + target + " vidas?";
            case "fr":
                return "Vais-je finir ce niveau en " + target + " vies maximum ?";
            case "de":
                return "Schaffe ich dieses Level in " + target + " Leben?";
            case "pt-br":
                return "Vou vencer esta fase em até " + target + " vidas?";
            case "au":
                return "Reckon I'll beat this level within " + target + " lives, mate?";
            default:
                return "Will I beat this level within " + target + " lives?";
        }
    }

    private static string YesOutcome(string language)
    {
        switch ((language ?? "en").ToLowerInvariant())
        {
            case "es": return "Sí";
            case "fr": return "Oui";
            case "de": return "Ja";
            case "pt-br": return "Sim";
            case "au": return "Yeah, mate";
            default: return "Yes";
        }
    }

    private static string NoOutcome(string language)
    {
        switch ((language ?? "en").ToLowerInvariant())
        {
            case "es": return "No";
            case "fr": return "Non";
            case "de": return "Nein";
            case "pt-br": return "Não";
            case "au": return "No chance";
            default: return "No";
        }
    }
}
